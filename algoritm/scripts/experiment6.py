import csv
import copy
import random
import statistics
import time
from pathlib import Path

import matplotlib.pyplot as plt

from cls_network import Network
from crypto_state import CryptoPolicy

NUM_NODES = 100
RUNS_PER_SCENARIO = 50

SCENARIOS = [
    {"name": "S1_90_0_10", "valid": 0.90, "transitional": 0.00, "non_compliant": 0.10},
    {"name": "S2_80_10_10", "valid": 0.80, "transitional": 0.10, "non_compliant": 0.10},
    {"name": "S3_70_20_10", "valid": 0.70, "transitional": 0.20, "non_compliant": 0.10},
    {"name": "S4_60_20_20", "valid": 0.60, "transitional": 0.20, "non_compliant": 0.20},
]

RESULTS_DIR = Path("results_experiment6")
RESULTS_DIR.mkdir(exist_ok=True)


def count_crypto_states(cluster):
    counts = {"VALID": 0, "TRANSITIONAL": 0, "NON_COMPLIANT": 0, "UNKNOWN": 0}
    for node in cluster:
        state = getattr(node, "crypto_state", "UNKNOWN")
        counts[state] = counts.get(state, 0) + 1
    return counts


def cluster_metrics(clusters):
    concentrations = []
    cluster_sizes = []
    non_compliant_total = 0
    clusters_with_non_compliant = 0

    for cluster in clusters:
        size = len(cluster)
        cluster_sizes.append(size)
        counts = count_crypto_states(cluster)
        non_compliant = counts["NON_COMPLIANT"]
        non_compliant_total += non_compliant
        if non_compliant > 0:
            clusters_with_non_compliant += 1
        concentrations.append(non_compliant / size if size else 0.0)

    return {
        "clusters": len(clusters),
        "non_compliant_total": non_compliant_total,
        "clusters_with_non_compliant": clusters_with_non_compliant,
        "max_non_compliant_concentration": max(concentrations) if concentrations else 0.0,
        "mean_non_compliant_concentration": statistics.mean(concentrations) if concentrations else 0.0,
        "average_non_compliant_per_cluster": non_compliant_total / len(clusters) if clusters else 0.0,
        "cluster_size_std": statistics.stdev(cluster_sizes) if len(cluster_sizes) > 1 else 0.0,
        "cluster_size_range": (max(cluster_sizes) - min(cluster_sizes)) if cluster_sizes else 0,
    }


def run_one_experiment(seed, scenario, policy):
    random.seed(seed)
    base_network = Network()
    base_network.create_network(NUM_NODES)
    base_network.assign_crypto_states(
        valid_ratio=scenario["valid"],
        transitional_ratio=scenario["transitional"],
        non_compliant_ratio=scenario["non_compliant"],
    )
    base_network.evaluate_crypto_states(policy)

    baseline_network = copy.deepcopy(base_network)
    security_network = copy.deepcopy(base_network)

    start = time.perf_counter()
    baseline_clusters = baseline_network.split_into_clusters()
    baseline_time = time.perf_counter() - start
    baseline_metrics = cluster_metrics(baseline_clusters)
    baseline_metrics["clustering_time_sec"] = baseline_time

    start = time.perf_counter()
    security_clusters = security_network.split_into_security_aware_clusters(policy)
    security_time = time.perf_counter() - start
    security_metrics = cluster_metrics(security_clusters)
    security_metrics["clustering_time_sec"] = security_time

    return baseline_metrics, security_metrics


METRICS = [
    "max_non_compliant_concentration",
    "mean_non_compliant_concentration",
    "clusters_with_non_compliant",
    "average_non_compliant_per_cluster",
    "cluster_size_std",
    "cluster_size_range",
    "clustering_time_sec",
]


def aggregate(rows):
    result = {}
    for metric in METRICS:
        values = [row[metric] for row in rows]
        result[f"{metric}_mean"] = statistics.mean(values)
        result[f"{metric}_median"] = statistics.median(values)
        result[f"{metric}_std"] = statistics.stdev(values) if len(values) > 1 else 0.0
        result[f"{metric}_min"] = min(values)
        result[f"{metric}_max"] = max(values)
    return result


def save_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_metric(summary_rows, metric, ylabel, filename):
    scenario_names = [s["name"] for s in SCENARIOS]
    baseline_means, security_means = [], []
    baseline_std, security_std = [], []

    for scenario_name in scenario_names:
        b = next(r for r in summary_rows if r["scenario"] == scenario_name and r["method"] == "Baseline")
        s = next(r for r in summary_rows if r["scenario"] == scenario_name and r["method"] == "Security-Aware")
        baseline_means.append(b[f"{metric}_mean"])
        security_means.append(s[f"{metric}_mean"])
        baseline_std.append(b[f"{metric}_std"])
        security_std.append(s[f"{metric}_std"])

    x = list(range(len(scenario_names)))
    width = 0.36
    plt.figure(figsize=(10, 6))
    plt.bar([i - width / 2 for i in x], baseline_means, width=width, yerr=baseline_std, capsize=4, label="Baseline")
    plt.bar([i + width / 2 for i in x], security_means, width=width, yerr=security_std, capsize=4, label="Security-Aware")
    plt.xticks(x, scenario_names)
    plt.ylabel(ylabel)
    plt.title(ylabel + " by security scenario")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / filename, dpi=200)
    plt.close()


def plot_relative_improvement(summary_rows):
    names, reductions = [], []
    for scenario in SCENARIOS:
        name = scenario["name"]
        b = next(r for r in summary_rows if r["scenario"] == name and r["method"] == "Baseline")
        s = next(r for r in summary_rows if r["scenario"] == name and r["method"] == "Security-Aware")
        base = b["max_non_compliant_concentration_mean"]
        sec = s["max_non_compliant_concentration_mean"]
        reduction = ((base - sec) / base) * 100 if base > 0 else 0.0
        names.append(name)
        reductions.append(reduction)

    plt.figure(figsize=(9, 5))
    plt.bar(names, reductions)
    plt.ylabel("Reduction, %")
    plt.title("Reduction of maximum NON_COMPLIANT concentration")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "relative_reduction.png", dpi=200)
    plt.close()


def main():
    print("=" * 72)
    print("EXPERIMENT 6")
    print(f"{RUNS_PER_SCENARIO} runs per scenario, {NUM_NODES} nodes")
    print("=" * 72)

    policy = CryptoPolicy(required_algorithm="AES-256", minimum_security_level=3, policy_version=2)
    raw_rows = []

    for scenario_index, scenario in enumerate(SCENARIOS):
        print(f"\n{scenario['name']}: VALID={scenario['valid']:.0%}, TRANSITIONAL={scenario['transitional']:.0%}, NON_COMPLIANT={scenario['non_compliant']:.0%}")

        for run in range(RUNS_PER_SCENARIO):
            seed = 10000 * (scenario_index + 1) + run
            baseline, security = run_one_experiment(seed, scenario, policy)
            raw_rows.append({"scenario": scenario["name"], "run": run + 1, "seed": seed, "method": "Baseline", **baseline})
            raw_rows.append({"scenario": scenario["name"], "run": run + 1, "seed": seed, "method": "Security-Aware", **security})

        print("  completed")

    summary_rows = []
    for scenario in SCENARIOS:
        for method in ["Baseline", "Security-Aware"]:
            selected = [r for r in raw_rows if r["scenario"] == scenario["name"] and r["method"] == method]
            summary_rows.append({
                "scenario": scenario["name"],
                "method": method,
                "runs": RUNS_PER_SCENARIO,
                "nodes": NUM_NODES,
                "valid_ratio": scenario["valid"],
                "transitional_ratio": scenario["transitional"],
                "non_compliant_ratio": scenario["non_compliant"],
                **aggregate(selected),
            })

    print("\n" + "=" * 72)
    print("STATISTICAL SUMMARY")
    print("=" * 72)

    for scenario in SCENARIOS:
        name = scenario["name"]
        b = next(r for r in summary_rows if r["scenario"] == name and r["method"] == "Baseline")
        s = next(r for r in summary_rows if r["scenario"] == name and r["method"] == "Security-Aware")
        base_max = b["max_non_compliant_concentration_mean"]
        sec_max = s["max_non_compliant_concentration_mean"]
        reduction = ((base_max - sec_max) / base_max) * 100 if base_max > 0 else 0.0
        time_change = ((s["clustering_time_sec_mean"] - b["clustering_time_sec_mean"]) / b["clustering_time_sec_mean"] * 100) if b["clustering_time_sec_mean"] > 0 else 0.0

        print(f"\n{name}")
        print(f"  Baseline max concentration: {base_max:.4f} (SD={b['max_non_compliant_concentration_std']:.4f})")
        print(f"  Security-Aware max concentration: {sec_max:.4f} (SD={s['max_non_compliant_concentration_std']:.4f})")
        print(f"  Relative reduction: {reduction:.2f}%")
        print(f"  Baseline clustering time: {b['clustering_time_sec_mean']:.6f} s")
        print(f"  Security-Aware clustering time: {s['clustering_time_sec_mean']:.6f} s")
        print(f"  Clustering-time change: {time_change:.2f}%")

    save_csv(RESULTS_DIR / "experiment6_raw_results.csv", raw_rows)
    save_csv(RESULTS_DIR / "experiment6_summary.csv", summary_rows)

    plot_metric(summary_rows, "max_non_compliant_concentration", "Maximum NON_COMPLIANT concentration", "max_concentration_mean_sd.png")
    plot_metric(summary_rows, "clusters_with_non_compliant", "Clusters containing NON_COMPLIANT nodes", "affected_clusters_mean_sd.png")
    plot_metric(summary_rows, "cluster_size_std", "Cluster-size standard deviation", "cluster_balance_mean_sd.png")
    plot_metric(summary_rows, "clustering_time_sec", "Clustering execution time, seconds", "clustering_time_mean_sd.png")
    plot_relative_improvement(summary_rows)

    print("\nExperiment 6 completed.")
    print(f"Results directory: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
