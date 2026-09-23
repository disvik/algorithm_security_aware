import csv
import copy
import random
from pathlib import Path

import matplotlib.pyplot as plt

from cls_network import Network
from crypto_state import CryptoPolicy


# ============================================================
# EXPERIMENT 5
# Baseline Dynamic Clustering vs Security-Aware Clustering
# ============================================================

NUM_NODES = 100
VALID_RATIO = 0.70
TRANSITIONAL_RATIO = 0.20
NON_COMPLIANT_RATIO = 0.10

RANDOM_SEED = 42

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def count_crypto_states(cluster):
    """Count cryptographic states in one cluster."""
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


def calculate_metrics(clusters, method_name):
    """Calculate security-oriented clustering metrics."""

    total_nodes = sum(len(cluster) for cluster in clusters)

    cluster_rows = []

    non_compliant_total = 0
    clusters_with_non_compliant = 0
    max_non_compliant_concentration = 0.0

    for index, cluster in enumerate(clusters, start=1):
        counts = count_crypto_states(cluster)
        cluster_size = len(cluster)

        non_compliant = counts["NON_COMPLIANT"]

        concentration = (
            non_compliant / cluster_size
            if cluster_size > 0
            else 0.0
        )

        non_compliant_total += non_compliant

        if non_compliant > 0:
            clusters_with_non_compliant += 1

        max_non_compliant_concentration = max(
            max_non_compliant_concentration,
            concentration
        )

        cluster_rows.append({
            "method": method_name,
            "cluster": index,
            "nodes": cluster_size,
            "valid": counts["VALID"],
            "transitional": counts["TRANSITIONAL"],
            "non_compliant": non_compliant,
            "unknown": counts["UNKNOWN"],
            "non_compliant_concentration": concentration,
        })

    average_non_compliant_per_cluster = (
        non_compliant_total / len(clusters)
        if clusters
        else 0.0
    )

    summary = {
        "method": method_name,
        "nodes": total_nodes,
        "clusters": len(clusters),
        "non_compliant_total": non_compliant_total,
        "clusters_with_non_compliant": clusters_with_non_compliant,
        "max_non_compliant_concentration":
            max_non_compliant_concentration,
        "average_non_compliant_per_cluster":
            average_non_compliant_per_cluster,
    }

    return summary, cluster_rows


def save_csv(summary_rows, cluster_rows):
    """Save experiment results to CSV files."""

    summary_path = RESULTS_DIR / "experiment5_summary.csv"
    clusters_path = RESULTS_DIR / "experiment5_clusters.csv"

    summary_fields = [
        "method",
        "nodes",
        "clusters",
        "non_compliant_total",
        "clusters_with_non_compliant",
        "max_non_compliant_concentration",
        "average_non_compliant_per_cluster",
    ]

    with summary_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summary_rows)

    cluster_fields = [
        "method",
        "cluster",
        "nodes",
        "valid",
        "transitional",
        "non_compliant",
        "unknown",
        "non_compliant_concentration",
    ]

    with clusters_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=cluster_fields)
        writer.writeheader()
        writer.writerows(cluster_rows)

    print(f"\nCSV summary saved to: {summary_path}")
    print(f"CSV cluster data saved to: {clusters_path}")


def make_plots(summary_rows, cluster_rows):
    """Create first comparison graphs."""

    methods = [row["method"] for row in summary_rows]

    max_concentration = [
        row["max_non_compliant_concentration"]
        for row in summary_rows
    ]

    clusters_with_non_compliant = [
        row["clusters_with_non_compliant"]
        for row in summary_rows
    ]

    average_non_compliant = [
        row["average_non_compliant_per_cluster"]
        for row in summary_rows
    ]

    # --------------------------------------------------------
    # Graph 1: maximum concentration
    # --------------------------------------------------------

    plt.figure(figsize=(8, 5))
    plt.bar(methods, max_concentration)
    plt.ylabel("Maximum NON_COMPLIANT concentration")
    plt.title("Maximum concentration of non-compliant nodes")
    plt.ylim(0, max(max_concentration) * 1.25 if max(max_concentration) > 0 else 1)
    plt.tight_layout()

    path = RESULTS_DIR / "max_non_compliant_concentration.png"
    plt.savefig(path, dpi=200)
    plt.show()

    # --------------------------------------------------------
    # Graph 2: number of affected clusters
    # --------------------------------------------------------

    plt.figure(figsize=(8, 5))
    plt.bar(methods, clusters_with_non_compliant)
    plt.ylabel("Number of clusters")
    plt.title("Clusters containing NON_COMPLIANT nodes")
    plt.tight_layout()

    path = RESULTS_DIR / "affected_clusters.png"
    plt.savefig(path, dpi=200)
    plt.show()

    # --------------------------------------------------------
    # Graph 3: average number per cluster
    # --------------------------------------------------------

    plt.figure(figsize=(8, 5))
    plt.bar(methods, average_non_compliant)
    plt.ylabel("Average NON_COMPLIANT nodes per cluster")
    plt.title("Average non-compliant nodes per cluster")
    plt.tight_layout()

    path = RESULTS_DIR / "average_non_compliant.png"
    plt.savefig(path, dpi=200)
    plt.show()

    # --------------------------------------------------------
    # Graph 4: concentration by cluster
    # --------------------------------------------------------

    baseline_rows = [
        row for row in cluster_rows
        if row["method"] == "Baseline"
    ]

    security_rows = [
        row for row in cluster_rows
        if row["method"] == "Security-Aware"
    ]

    plt.figure(figsize=(10, 5))

    baseline_x = [
        row["cluster"] for row in baseline_rows
    ]
    baseline_y = [
        row["non_compliant_concentration"]
        for row in baseline_rows
    ]

    security_x = [
        row["cluster"] for row in security_rows
    ]
    security_y = [
        row["non_compliant_concentration"]
        for row in security_rows
    ]

    plt.plot(
        baseline_x,
        baseline_y,
        marker="o",
        label="Baseline"
    )

    plt.plot(
        security_x,
        security_y,
        marker="o",
        label="Security-Aware"
    )

    plt.xlabel("Cluster")
    plt.ylabel("NON_COMPLIANT concentration")
    plt.title("NON_COMPLIANT concentration by cluster")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    path = RESULTS_DIR / "concentration_by_cluster.png"
    plt.savefig(path, dpi=200)
    plt.show()


def main():
    print("=" * 65)
    print("EXPERIMENT 5")
    print("Baseline vs Security-Aware Dynamic Clustering")
    print("=" * 65)

    # --------------------------------------------------------
    # 1. Fixed random seed.
    #
    # This makes the experiment reproducible.
    # --------------------------------------------------------

    random.seed(RANDOM_SEED)

    # --------------------------------------------------------
    # 2. Create ONE base network.
    # --------------------------------------------------------

    base_network = Network()
    base_network.create_network(NUM_NODES)

    # --------------------------------------------------------
    # 3. Assign exactly the same crypto configuration
    #    to the base network.
    # --------------------------------------------------------

    base_network.assign_crypto_states(
        valid_ratio=VALID_RATIO,
        transitional_ratio=TRANSITIONAL_RATIO,
        non_compliant_ratio=NON_COMPLIANT_RATIO,
    )

    policy = CryptoPolicy(
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2,
    )

    # Evaluate the same states before copying the network.
    base_network.evaluate_crypto_states(policy)

    print("\nInitial cryptographic distribution:")

    state_counts = {
        "VALID": 0,
        "TRANSITIONAL": 0,
        "NON_COMPLIANT": 0,
        "UNKNOWN": 0,
    }

    for node in base_network.nodes:
        state_counts[node.crypto_state] += 1

    for state, count in state_counts.items():
        print(f"{state}: {count}")

    # --------------------------------------------------------
    # 4. Make two copies of the SAME network.
    #
    # This is essential:
    # both algorithms receive identical nodes and states.
    # --------------------------------------------------------

    baseline_network = copy.deepcopy(base_network)
    security_network = copy.deepcopy(base_network)

    # --------------------------------------------------------
    # 5. Baseline clustering.
    # --------------------------------------------------------

    baseline_clusters = (
        baseline_network.split_into_clusters()
    )

    # --------------------------------------------------------
    # 6. Proposed security-aware clustering.
    # --------------------------------------------------------

    security_clusters = (
        security_network.split_into_security_aware_clusters(
            policy
        )
    )

    # --------------------------------------------------------
    # 7. Calculate metrics.
    # --------------------------------------------------------

    baseline_summary, baseline_cluster_rows = calculate_metrics(
        baseline_clusters,
        "Baseline"
    )

    security_summary, security_cluster_rows = calculate_metrics(
        security_clusters,
        "Security-Aware"
    )

    summary_rows = [
        baseline_summary,
        security_summary,
    ]

    cluster_rows = (
        baseline_cluster_rows
        + security_cluster_rows
    )

    # --------------------------------------------------------
    # 8. Print results.
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)

    for row in summary_rows:
        print(f"\n{row['method']}")
        print(
            "  Clusters:",
            row["clusters"]
        )
        print(
            "  NON_COMPLIANT total:",
            row["non_compliant_total"]
        )
        print(
            "  Clusters with NON_COMPLIANT:",
            row["clusters_with_non_compliant"]
        )
        print(
            "  Maximum concentration:",
            f"{row['max_non_compliant_concentration']:.4f}"
        )
        print(
            "  Average NON_COMPLIANT/cluster:",
            f"{row['average_non_compliant_per_cluster']:.4f}"
        )

    print("\n" + "=" * 65)
    print("CLUSTER DETAILS")
    print("=" * 65)

    for row in cluster_rows:
        print(
            f"{row['method']:17s} "
            f"Cluster {row['cluster']:2d}: "
            f"nodes={row['nodes']:2d}, "
            f"VALID={row['valid']:2d}, "
            f"TRANSITIONAL={row['transitional']:2d}, "
            f"NON_COMPLIANT={row['non_compliant']:2d}, "
            f"concentration="
            f"{row['non_compliant_concentration']:.3f}"
        )

    # --------------------------------------------------------
    # 9. Save CSV.
    # --------------------------------------------------------

    save_csv(
        summary_rows,
        cluster_rows
    )

    # --------------------------------------------------------
    # 10. Create graphs.
    # --------------------------------------------------------

    make_plots(
        summary_rows,
        cluster_rows
    )

    print("\nExperiment 5 completed.")


if __name__ == "__main__":
    main()
