import csv
import copy
import random
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

from cls_network import Network
from crypto_state import CryptoPolicy


# ============================================================
# EXPERIMENT 8
# Sensitivity analysis for w_nc and w_tr
# ============================================================

NUM_NODES = 100
RUNS_PER_COMBINATION = 30
RANDOM_SEED_BASE = 5000

VALID_RATIO = 0.70
TRANSITIONAL_RATIO = 0.20
NON_COMPLIANT_RATIO = 0.10

W_NC_VALUES = [0.5, 1.0, 2.0, 3.0, 4.0]
W_TR_VALUES = [0.0, 0.25, 0.5, 1.0, 2.0]

RESOURCE_WEIGHT = 1.0

RESULTS_DIR = Path("results_experiment8")
RESULTS_DIR.mkdir(exist_ok=True)


def count_states(cluster):
    counts = {
        "VALID": 0,
        "TRANSITIONAL": 0,
        "NON_COMPLIANT": 0,
    }

    for node in cluster:
        if node.crypto_state in counts:
            counts[node.crypto_state] += 1

    return counts


def calculate_metrics(clusters):
    concentrations = []
    cluster_sizes = []

    for cluster in clusters:
        cluster_sizes.append(len(cluster))

        counts = count_states(cluster)

        concentration = (
            counts["NON_COMPLIANT"] / len(cluster)
            if cluster
            else 0.0
        )

        concentrations.append(concentration)

    return {
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


def run_one(seed, w_nc, w_tr, policy):
    random.seed(seed)

    network = Network()
    network.create_network(NUM_NODES)

    network.assign_crypto_states(
        valid_ratio=VALID_RATIO,
        transitional_ratio=TRANSITIONAL_RATIO,
        non_compliant_ratio=NON_COMPLIANT_RATIO,
    )

    network.evaluate_crypto_states(policy)

    clusters = network.split_into_security_aware_clusters(
        policy,
        w_nc=w_nc,
        w_tr=w_tr,
        resource_weight=RESOURCE_WEIGHT,
    )

    return calculate_metrics(clusters)


def main():
    policy = CryptoPolicy(
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2,
    )

    raw_rows = []

    print("=" * 72)
    print("EXPERIMENT 8")
    print("Sensitivity analysis for w_nc and w_tr")
    print("=" * 72)

    combo_index = 0

    for w_nc in W_NC_VALUES:
        for w_tr in W_TR_VALUES:
            combo_index += 1

            print(
                f"Combination {combo_index:02d}: "
                f"w_nc={w_nc}, w_tr={w_tr}"
            )

            for run in range(RUNS_PER_COMBINATION):
                seed = (
                    RANDOM_SEED_BASE
                    + combo_index * 1000
                    + run
                )

                metrics = run_one(
                    seed,
                    w_nc,
                    w_tr,
                    policy,
                )

                raw_rows.append({
                    "w_nc": w_nc,
                    "w_tr": w_tr,
                    "run": run + 1,
                    "seed": seed,
                    **metrics,
                })

    # --------------------------------------------------------
    # Aggregate
    # --------------------------------------------------------

    summary_rows = []

    for w_nc in W_NC_VALUES:
        for w_tr in W_TR_VALUES:
            selected = [
                row for row in raw_rows
                if row["w_nc"] == w_nc
                and row["w_tr"] == w_tr
            ]

            max_values = [
                row["max_non_compliant_concentration"]
                for row in selected
            ]

            mean_values = [
                row["mean_non_compliant_concentration"]
                for row in selected
            ]

            balance_values = [
                row["cluster_size_std"]
                for row in selected
            ]

            range_values = [
                row["cluster_size_range"]
                for row in selected
            ]

            summary_rows.append({
                "w_nc": w_nc,
                "w_tr": w_tr,
                "runs": RUNS_PER_COMBINATION,

                "max_concentration_mean":
                    statistics.mean(max_values),

                "max_concentration_std":
                    statistics.stdev(max_values)
                    if len(max_values) > 1 else 0.0,

                "mean_concentration_mean":
                    statistics.mean(mean_values),

                "cluster_size_std_mean":
                    statistics.mean(balance_values),

                "cluster_size_range_mean":
                    statistics.mean(range_values),
            })

    # --------------------------------------------------------
    # Save raw CSV
    # --------------------------------------------------------

    raw_path = RESULTS_DIR / "experiment8_raw.csv"

    with raw_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(raw_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(raw_rows)

    # --------------------------------------------------------
    # Save summary CSV
    # --------------------------------------------------------

    summary_path = RESULTS_DIR / "experiment8_summary.csv"

    with summary_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(summary_rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    # --------------------------------------------------------
    # Print best combinations
    # --------------------------------------------------------

    ranked = sorted(
        summary_rows,
        key=lambda row: (
            row["max_concentration_mean"],
            row["cluster_size_std_mean"]
        )
    )

    print("\nTop 10 combinations:")
    print(
        "w_nc | w_tr | max conc mean | "
        "cluster-size SD mean"
    )

    for row in ranked[:10]:
        print(
            f"{row['w_nc']:4.2f} | "
            f"{row['w_tr']:4.2f} | "
            f"{row['max_concentration_mean']:.4f} | "
            f"{row['cluster_size_std_mean']:.4f}"
        )

    # --------------------------------------------------------
    # Plot 1: one line for each w_tr
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    for w_tr in W_TR_VALUES:
        rows = sorted(
            [
                row for row in summary_rows
                if row["w_tr"] == w_tr
            ],
            key=lambda row: row["w_nc"]
        )

        plt.plot(
            [row["w_nc"] for row in rows],
            [
                row["max_concentration_mean"]
                for row in rows
            ],
            marker="o",
            label=f"w_tr={w_tr}"
        )

    plt.xlabel("w_nc")
    plt.ylabel(
        "Mean maximum NON_COMPLIANT concentration"
    )
    plt.title(
        "Sensitivity of maximum concentration to security weights"
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "sensitivity_max_concentration.png",
        dpi=200
    )
    plt.close()

    # --------------------------------------------------------
    # Plot 2: cluster balance
    # --------------------------------------------------------

    plt.figure(figsize=(10, 6))

    for w_tr in W_TR_VALUES:
        rows = sorted(
            [
                row for row in summary_rows
                if row["w_tr"] == w_tr
            ],
            key=lambda row: row["w_nc"]
        )

        plt.plot(
            [row["w_nc"] for row in rows],
            [
                row["cluster_size_std_mean"]
                for row in rows
            ],
            marker="o",
            label=f"w_tr={w_tr}"
        )

    plt.xlabel("w_nc")
    plt.ylabel("Mean cluster-size standard deviation")
    plt.title(
        "Sensitivity of cluster balance to security weights"
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        RESULTS_DIR / "sensitivity_cluster_balance.png",
        dpi=200
    )
    plt.close()

    print("\nSaved:")
    print(raw_path)
    print(summary_path)
    print(
        RESULTS_DIR
        / "sensitivity_max_concentration.png"
    )
    print(
        RESULTS_DIR
        / "sensitivity_cluster_balance.png"
    )


if __name__ == "__main__":
    main()
