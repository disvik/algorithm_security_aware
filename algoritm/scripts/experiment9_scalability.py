import csv
import copy
import math
import random
import statistics
import time
from pathlib import Path

import matplotlib.pyplot as plt

from cls_network import Network
from crypto_state import CryptoPolicy


# ============================================================
# EXPERIMENT 9
# Scalability + paired statistical validation
# Baseline vs Normalized Security-Aware Clustering
# ============================================================

NETWORK_SIZES = [50, 100, 250, 500, 1000]
RUNS_PER_SIZE = 30

VALID_RATIO = 0.70
TRANSITIONAL_RATIO = 0.20
NON_COMPLIANT_RATIO = 0.10

# Weights selected after sensitivity analysis
W_NC = 2.0
W_TR = 1.0
RESOURCE_WEIGHT = 1.0

RANDOM_SEED_BASE = 90000

RESULTS_DIR = Path("results_experiment9")
RESULTS_DIR.mkdir(exist_ok=True)

try:
    from scipy.stats import wilcoxon, ttest_rel
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def disable_link_generation(network):
    """
    Experiment 9 isolates the clustering procedure itself.

    The current Network class generates intra- and inter-cluster
    links after clustering. For large N this can dominate runtime
    and memory, while it is not part of the cluster-selection rule.

    Therefore link generation is disabled for BOTH methods.
    """
    network.add_intra_cluster_links = lambda clusters: None
    network.add_inter_cluster_links = lambda clusters: None


def count_states(cluster):
    counts = {
        "VALID": 0,
        "TRANSITIONAL": 0,
        "NON_COMPLIANT": 0,
        "UNKNOWN": 0,
    }

    for node in cluster:
        state = getattr(node, "crypto_state", "UNKNOWN")
        counts[state] = counts.get(state, 0) + 1

    return counts


def calculate_cluster_metrics(clusters):
    concentrations = []
    cluster_sizes = []

    for cluster in clusters:
        cluster_size = len(cluster)
        cluster_sizes.append(cluster_size)

        counts = count_states(cluster)

        nc_ratio = (
            counts["NON_COMPLIANT"] / cluster_size
            if cluster_size > 0
            else 0.0
        )

        concentrations.append(nc_ratio)

    return {
        "clusters": len(clusters),
        "max_non_compliant_concentration":
            max(concentrations) if concentrations else 0.0,
        "mean_non_compliant_concentration":
            statistics.mean(concentrations)
            if concentrations else 0.0,
        "cluster_size_std":
            statistics.stdev(cluster_sizes)
            if len(cluster_sizes) > 1 else 0.0,
        "cluster_size_range":
            max(cluster_sizes) - min(cluster_sizes)
            if cluster_sizes else 0,
    }


def mean_ci95(values):
    n = len(values)

    if n == 0:
        return 0.0, 0.0, 0.0

    mean_value = statistics.mean(values)

    if n == 1:
        return mean_value, mean_value, mean_value

    sd = statistics.stdev(values)
    margin = 1.96 * sd / math.sqrt(n)

    return (
        mean_value,
        mean_value - margin,
        mean_value + margin
    )


def paired_statistical_test(baseline_values, security_values):
    """
    Baseline and Security-Aware are evaluated on identical
    generated networks, therefore the observations are paired.
    """

    result = {
        "paired_t_statistic": "",
        "paired_t_pvalue": "",
        "wilcoxon_statistic": "",
        "wilcoxon_pvalue": "",
    }

    if not SCIPY_AVAILABLE:
        return result

    t_result = ttest_rel(
        baseline_values,
        security_values
    )

    result["paired_t_statistic"] = float(
        t_result.statistic
    )
    result["paired_t_pvalue"] = float(
        t_result.pvalue
    )

    differences = [
        b - s
        for b, s in zip(
            baseline_values,
            security_values
        )
    ]

    if any(abs(d) > 1e-15 for d in differences):
        w_result = wilcoxon(
            baseline_values,
            security_values,
            alternative="greater"
        )

        result["wilcoxon_statistic"] = float(
            w_result.statistic
        )
        result["wilcoxon_pvalue"] = float(
            w_result.pvalue
        )

    return result


def run_one(seed, network_size, policy):
    """
    One paired experiment:
    one base set of nodes -> two exact copies -> two algorithms.
    """

    random.seed(seed)

    base_network = Network()

    # Only node generation is required because initial graph edges
    # are not used in the clustering criterion.
    base_network.create_nodes(
        network_size
    )

    base_network.assign_crypto_states(
        valid_ratio=VALID_RATIO,
        transitional_ratio=TRANSITIONAL_RATIO,
        non_compliant_ratio=NON_COMPLIANT_RATIO,
    )

    base_network.evaluate_crypto_states(
        policy
    )

    baseline_network = copy.deepcopy(
        base_network
    )

    security_network = copy.deepcopy(
        base_network
    )

    disable_link_generation(
        baseline_network
    )

    disable_link_generation(
        security_network
    )

    start = time.perf_counter()

    baseline_clusters = (
        baseline_network
        .split_into_clusters()
    )

    baseline_time = (
        time.perf_counter() - start
    )

    baseline_metrics = (
        calculate_cluster_metrics(
            baseline_clusters
        )
    )

    start = time.perf_counter()

    security_clusters = (
        security_network
        .split_into_security_aware_clusters(
            policy,
            w_nc=W_NC,
            w_tr=W_TR,
            resource_weight=RESOURCE_WEIGHT
        )
    )

    security_time = (
        time.perf_counter() - start
    )

    security_metrics = (
        calculate_cluster_metrics(
            security_clusters
        )
    )

    return {
        "baseline": baseline_metrics,
        "security": security_metrics,
        "baseline_time": baseline_time,
        "security_time": security_time,
    }


def main():
    print("=" * 78)
    print("EXPERIMENT 9")
    print("Scalability and paired statistical validation")
    print("=" * 78)

    print(
        f"Network sizes: {NETWORK_SIZES}"
    )

    print(
        f"Runs per size: {RUNS_PER_SIZE}"
    )

    print(
        f"Weights: w_nc={W_NC}, "
        f"w_tr={W_TR}, "
        f"w_R={RESOURCE_WEIGHT}"
    )

    if not SCIPY_AVAILABLE:
        print("\nWARNING: SciPy is not installed.")
        print(
            "Install with: pip3 install scipy"
        )

    policy = CryptoPolicy(
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2
    )

    raw_rows = []
    summary_rows = []

    for size_index, network_size in enumerate(
        NETWORK_SIZES
    ):
        print(
            f"\nN = {network_size}"
        )

        baseline_max_values = []
        security_max_values = []

        baseline_balance_values = []
        security_balance_values = []

        baseline_times = []
        security_times = []

        reductions_percent = []

        for run in range(
            RUNS_PER_SIZE
        ):
            seed = (
                RANDOM_SEED_BASE
                + size_index * 10000
                + run
            )

            result = run_one(
                seed,
                network_size,
                policy
            )

            baseline = result["baseline"]
            security = result["security"]

            baseline_max = (
                baseline[
                    "max_non_compliant_concentration"
                ]
            )

            security_max = (
                security[
                    "max_non_compliant_concentration"
                ]
            )

            reduction_percent = (
                (
                    baseline_max
                    - security_max
                )
                / baseline_max
                * 100.0
                if baseline_max > 0
                else 0.0
            )

            baseline_max_values.append(
                baseline_max
            )

            security_max_values.append(
                security_max
            )

            baseline_balance_values.append(
                baseline["cluster_size_std"]
            )

            security_balance_values.append(
                security["cluster_size_std"]
            )

            baseline_times.append(
                result["baseline_time"]
            )

            security_times.append(
                result["security_time"]
            )

            reductions_percent.append(
                reduction_percent
            )

            raw_rows.append({
                "network_size":
                    network_size,
                "run":
                    run + 1,
                "seed":
                    seed,
                "clusters":
                    baseline["clusters"],
                "baseline_max_concentration":
                    baseline_max,
                "security_max_concentration":
                    security_max,
                "absolute_difference":
                    baseline_max - security_max,
                "relative_reduction_percent":
                    reduction_percent,
                "baseline_cluster_size_std":
                    baseline["cluster_size_std"],
                "security_cluster_size_std":
                    security["cluster_size_std"],
                "baseline_time_sec":
                    result["baseline_time"],
                "security_time_sec":
                    result["security_time"],
            })

        (
            baseline_mean,
            baseline_ci_low,
            baseline_ci_high
        ) = mean_ci95(
            baseline_max_values
        )

        (
            security_mean,
            security_ci_low,
            security_ci_high
        ) = mean_ci95(
            security_max_values
        )

        (
            reduction_mean,
            reduction_ci_low,
            reduction_ci_high
        ) = mean_ci95(
            reductions_percent
        )

        test_results = (
            paired_statistical_test(
                baseline_max_values,
                security_max_values
            )
        )

        summary = {
            "network_size":
                network_size,
            "runs":
                RUNS_PER_SIZE,
            "baseline_max_mean":
                baseline_mean,
            "baseline_max_sd":
                statistics.stdev(
                    baseline_max_values
                ),
            "baseline_max_ci95_low":
                baseline_ci_low,
            "baseline_max_ci95_high":
                baseline_ci_high,
            "security_max_mean":
                security_mean,
            "security_max_sd":
                statistics.stdev(
                    security_max_values
                ),
            "security_max_ci95_low":
                security_ci_low,
            "security_max_ci95_high":
                security_ci_high,
            "relative_reduction_mean_percent":
                reduction_mean,
            "relative_reduction_sd_percent":
                statistics.stdev(
                    reductions_percent
                ),
            "relative_reduction_ci95_low":
                reduction_ci_low,
            "relative_reduction_ci95_high":
                reduction_ci_high,
            "baseline_cluster_size_std_mean":
                statistics.mean(
                    baseline_balance_values
                ),
            "security_cluster_size_std_mean":
                statistics.mean(
                    security_balance_values
                ),
            "baseline_time_mean_sec":
                statistics.mean(
                    baseline_times
                ),
            "security_time_mean_sec":
                statistics.mean(
                    security_times
                ),
            **test_results
        }

        summary_rows.append(
            summary
        )

        print(
            "  Baseline max concentration: "
            f"{baseline_mean:.4f}"
        )

        print(
            "  Security-Aware max concentration: "
            f"{security_mean:.4f}"
        )

        print(
            "  Mean reduction: "
            f"{reduction_mean:.2f}%"
        )

        print(
            "  Baseline time: "
            f"{summary['baseline_time_mean_sec']:.6f} s"
        )

        print(
            "  Security-Aware time: "
            f"{summary['security_time_mean_sec']:.6f} s"
        )

        if SCIPY_AVAILABLE:
            print(
                "  Wilcoxon p-value: "
                f"{summary['wilcoxon_pvalue']:.6g}"
            )

    raw_path = (
        RESULTS_DIR
        / "experiment9_raw.csv"
    )

    with raw_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(
                raw_rows[0].keys()
            )
        )
        writer.writeheader()
        writer.writerows(
            raw_rows
        )

    summary_path = (
        RESULTS_DIR
        / "experiment9_summary.csv"
    )

    with summary_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(
                summary_rows[0].keys()
            )
        )
        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    # Figure 1: concentration vs network size
    x = list(
        range(
            len(NETWORK_SIZES)
        )
    )

    width = 0.36

    baseline_means = [
        row[
            "baseline_max_mean"
        ]
        for row in summary_rows
    ]

    security_means = [
        row[
            "security_max_mean"
        ]
        for row in summary_rows
    ]

    baseline_errors = [
        (
            row["baseline_max_mean"]
            - row["baseline_max_ci95_low"]
        )
        for row in summary_rows
    ]

    security_errors = [
        (
            row["security_max_mean"]
            - row["security_max_ci95_low"]
        )
        for row in summary_rows
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        [
            i - width / 2
            for i in x
        ],
        baseline_means,
        width=width,
        yerr=baseline_errors,
        capsize=4,
        label="Baseline"
    )

    plt.bar(
        [
            i + width / 2
            for i in x
        ],
        security_means,
        width=width,
        yerr=security_errors,
        capsize=4,
        label="Security-Aware"
    )

    plt.xticks(
        x,
        NETWORK_SIZES
    )

    plt.xlabel(
        "Number of nodes"
    )

    plt.ylabel(
        "Mean maximum NON_COMPLIANT concentration"
    )

    plt.title(
        "Scalability of clustering quality"
    )

    plt.legend()
    plt.tight_layout()

    figure1_path = (
        RESULTS_DIR
        / "scalability_concentration.png"
    )

    plt.savefig(
        figure1_path,
        dpi=200
    )

    plt.close()

    # Figure 2: relative reduction vs network size
    reduction_means = [
        row[
            "relative_reduction_mean_percent"
        ]
        for row in summary_rows
    ]

    reduction_errors = [
        (
            row[
                "relative_reduction_mean_percent"
            ]
            - row[
                "relative_reduction_ci95_low"
            ]
        )
        for row in summary_rows
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.errorbar(
        NETWORK_SIZES,
        reduction_means,
        yerr=reduction_errors,
        marker="o",
        capsize=4
    )

    plt.xlabel(
        "Number of nodes"
    )

    plt.ylabel(
        "Mean relative reduction, %"
    )

    plt.title(
        "Relative reduction of maximum "
        "NON_COMPLIANT concentration"
    )

    plt.tight_layout()

    figure2_path = (
        RESULTS_DIR
        / "scalability_relative_reduction.png"
    )

    plt.savefig(
        figure2_path,
        dpi=200
    )

    plt.close()

    # Figure 3: clustering execution time
    baseline_time_means = [
        row[
            "baseline_time_mean_sec"
        ]
        for row in summary_rows
    ]

    security_time_means = [
        row[
            "security_time_mean_sec"
        ]
        for row in summary_rows
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        NETWORK_SIZES,
        baseline_time_means,
        marker="o",
        label="Baseline"
    )

    plt.plot(
        NETWORK_SIZES,
        security_time_means,
        marker="o",
        label="Security-Aware"
    )

    plt.xlabel(
        "Number of nodes"
    )

    plt.ylabel(
        "Mean clustering time, s"
    )

    plt.title(
        "Clustering execution time vs network size"
    )

    plt.legend()
    plt.tight_layout()

    figure3_path = (
        RESULTS_DIR
        / "scalability_execution_time.png"
    )

    plt.savefig(
        figure3_path,
        dpi=200
    )

    plt.close()

    print("\n" + "=" * 78)
    print("FINAL SUMMARY")
    print("=" * 78)

    print(
        "\nN | Baseline | Security-Aware | "
        "Reduction % | Wilcoxon p"
    )

    for row in summary_rows:
        p_value = (
            row["wilcoxon_pvalue"]
            if row["wilcoxon_pvalue"] != ""
            else "n/a"
        )

        if isinstance(
            p_value,
            float
        ):
            p_text = (
                f"{p_value:.6g}"
            )
        else:
            p_text = str(
                p_value
            )

        print(
            f"{row['network_size']:4d} | "
            f"{row['baseline_max_mean']:.4f} | "
            f"{row['security_max_mean']:.4f} | "
            f"{row['relative_reduction_mean_percent']:.2f}% | "
            f"{p_text}"
        )

    print("\nSaved:")
    print(raw_path)
    print(summary_path)
    print(figure1_path)
    print(figure2_path)
    print(figure3_path)


if __name__ == "__main__":
    main()
