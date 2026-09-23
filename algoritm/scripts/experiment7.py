import csv
import random
from pathlib import Path

import matplotlib.pyplot as plt

from cls_network import Network
from crypto_state import CryptoPolicy


# ============================================================
# EXPERIMENT 7
# Dynamic crypto-state changes and cluster reconfiguration
# ============================================================

NUM_NODES = 100
TIME_STEPS = 100

INITIAL_VALID_RATIO = 0.70
INITIAL_TRANSITIONAL_RATIO = 0.20
INITIAL_NON_COMPLIANT_RATIO = 0.10

# Доля узлов, которые на каждом временном шаге
# выбираются для возможного изменения crypto-state.
CHANGE_RATIO = 0.10

# Вероятность ухудшения состояния выбранного узла.
DETERIORATION_PROBABILITY = 0.75

# Экспериментальный порог, после превышения которого
# кластер требует реконфигурации.
MAX_NON_COMPLIANT_RATIO = 0.20

RANDOM_SEED = 42

RESULTS_DIR = Path("results_experiment7")
RESULTS_DIR.mkdir(exist_ok=True)


def count_network_crypto_states(nodes):
    """
    Подсчитывает текущее количество узлов
    каждого криптографического состояния.
    """
    counts = {
        "VALID": 0,
        "TRANSITIONAL": 0,
        "NON_COMPLIANT": 0,
        "UNKNOWN": 0,
    }

    for node in nodes:
        state = getattr(node, "crypto_state", "UNKNOWN")
        counts[state] = counts.get(state, 0) + 1

    return counts


def save_csv(rows):
    """
    Сохраняет временной ряд эксперимента.
    """
    path = RESULTS_DIR / "experiment7_dynamic_reconfiguration.csv"

    fieldnames = [
        "time_step",
        "changed_nodes",
        "valid_nodes",
        "transitional_nodes",
        "non_compliant_nodes",
        "unsafe_clusters",
        "reconfigured",
        "reconfiguration_count_step",
        "reconfiguration_count_cumulative",
        "moved_nodes",
        "moved_nodes_cumulative",
        "max_concentration_before",
        "max_concentration_after",
        "concentration_reduction_absolute",
        "concentration_reduction_percent",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return path


def save_summary(rows):
    """
    Сохраняет сводные показатели всего динамического эксперимента.
    """
    path = RESULTS_DIR / "experiment7_summary.csv"

    total_reconfigurations = sum(
        row["reconfiguration_count_step"] for row in rows
    )

    total_moved_nodes = sum(
        row["moved_nodes"] for row in rows
    )

    total_changed_nodes = sum(
        row["changed_nodes"] for row in rows
    )

    mean_before = sum(
        row["max_concentration_before"] for row in rows
    ) / len(rows)

    mean_after = sum(
        row["max_concentration_after"] for row in rows
    ) / len(rows)

    mean_moved_when_reconfigured = (
        total_moved_nodes / total_reconfigurations
        if total_reconfigurations > 0
        else 0.0
    )

    steps_with_unsafe_clusters = sum(
        1 for row in rows
        if row["unsafe_clusters"] > 0
    )

    steps_reconfigured = sum(
        1 for row in rows
        if row["reconfigured"] == 1
    )

    summary = {
        "nodes": NUM_NODES,
        "time_steps": TIME_STEPS,
        "change_ratio": CHANGE_RATIO,
        "deterioration_probability": DETERIORATION_PROBABILITY,
        "max_non_compliant_ratio_threshold": MAX_NON_COMPLIANT_RATIO,
        "total_changed_nodes": total_changed_nodes,
        "steps_with_unsafe_clusters": steps_with_unsafe_clusters,
        "steps_reconfigured": steps_reconfigured,
        "total_reconfigurations": total_reconfigurations,
        "total_moved_nodes": total_moved_nodes,
        "mean_moved_nodes_per_reconfiguration": mean_moved_when_reconfigured,
        "mean_max_concentration_before": mean_before,
        "mean_max_concentration_after": mean_after,
    }

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    return path, summary


def make_plots(rows):
    """
    Строит три отдельных графика:
    1. Максимальная концентрация до/после реконфигурации.
    2. Накопленное число реконфигураций.
    3. Число перемещенных узлов на каждом шаге.
    """

    time_steps = [row["time_step"] for row in rows]

    before = [
        row["max_concentration_before"]
        for row in rows
    ]

    after = [
        row["max_concentration_after"]
        for row in rows
    ]

    cumulative_reconfigurations = [
        row["reconfiguration_count_cumulative"]
        for row in rows
    ]

    moved_nodes = [
        row["moved_nodes"]
        for row in rows
    ]

    # --------------------------------------------------------
    # Graph 1
    # --------------------------------------------------------

    plt.figure(figsize=(11, 6))
    plt.plot(
        time_steps,
        before,
        label="Before reconfiguration"
    )
    plt.plot(
        time_steps,
        after,
        label="After reconfiguration"
    )
    plt.axhline(
        y=MAX_NON_COMPLIANT_RATIO,
        linestyle="--",
        label="Reconfiguration threshold"
    )
    plt.xlabel("Time step")
    plt.ylabel("Maximum NON_COMPLIANT concentration")
    plt.title(
        "Maximum NON_COMPLIANT concentration before and after reconfiguration"
    )
    plt.legend()
    plt.tight_layout()

    path = RESULTS_DIR / "concentration_before_after.png"
    plt.savefig(path, dpi=200)
    plt.close()

    # --------------------------------------------------------
    # Graph 2
    # --------------------------------------------------------

    plt.figure(figsize=(11, 6))
    plt.plot(
        time_steps,
        cumulative_reconfigurations
    )
    plt.xlabel("Time step")
    plt.ylabel("Cumulative reconfigurations")
    plt.title("Cumulative number of cluster reconfigurations")
    plt.tight_layout()

    path = RESULTS_DIR / "cumulative_reconfigurations.png"
    plt.savefig(path, dpi=200)
    plt.close()

    # --------------------------------------------------------
    # Graph 3
    # --------------------------------------------------------

    plt.figure(figsize=(11, 6))
    plt.bar(
        time_steps,
        moved_nodes
    )
    plt.xlabel("Time step")
    plt.ylabel("Moved nodes")
    plt.title("Number of nodes moved during reconfiguration")
    plt.tight_layout()

    path = RESULTS_DIR / "moved_nodes_per_step.png"
    plt.savefig(path, dpi=200)
    plt.close()


def main():
    random.seed(RANDOM_SEED)

    print("=" * 76)
    print("EXPERIMENT 7")
    print("Dynamic crypto-state changes and security-aware reconfiguration")
    print("=" * 76)

    # --------------------------------------------------------
    # 1. Create network
    # --------------------------------------------------------

    network = Network()
    network.create_network(NUM_NODES)

    policy = CryptoPolicy(
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2
    )

    # --------------------------------------------------------
    # 2. Controlled initial crypto-state distribution
    # --------------------------------------------------------

    network.assign_crypto_states(
        valid_ratio=INITIAL_VALID_RATIO,
        transitional_ratio=INITIAL_TRANSITIONAL_RATIO,
        non_compliant_ratio=INITIAL_NON_COMPLIANT_RATIO
    )

    network.evaluate_crypto_states(policy)

    # --------------------------------------------------------
    # 3. Initial security-aware clustering
    # --------------------------------------------------------

    clusters = network.split_into_security_aware_clusters(
        policy
    )

    initial_counts = count_network_crypto_states(network.nodes)

    print("\nInitial crypto-state distribution:")
    print("VALID:", initial_counts["VALID"])
    print("TRANSITIONAL:", initial_counts["TRANSITIONAL"])
    print("NON_COMPLIANT:", initial_counts["NON_COMPLIANT"])

    print(
        "Initial maximum NON_COMPLIANT concentration:",
        round(
            network.maximum_non_compliant_concentration(clusters),
            4
        )
    )

    rows = []

    cumulative_reconfigurations = 0
    cumulative_moved_nodes = 0

    # --------------------------------------------------------
    # 4. Dynamic simulation
    # --------------------------------------------------------

    for time_step in range(1, TIME_STEPS + 1):

        # A. Change crypto configuration of some nodes
        changes = network.simulate_crypto_state_changes(
            policy,
            change_ratio=CHANGE_RATIO,
            deterioration_probability=DETERIORATION_PROBABILITY
        )

        # B. Evaluate and, if necessary, reconfigure
        result = network.reconfigure_security_aware_clusters(
            clusters,
            policy,
            max_non_compliant_ratio=MAX_NON_COMPLIANT_RATIO
        )

        # C. Continue with the current cluster structure
        clusters = result["clusters"]

        cumulative_reconfigurations += (
            result["reconfiguration_count"]
        )

        cumulative_moved_nodes += (
            result["moved_nodes_count"]
        )

        counts = count_network_crypto_states(
            network.nodes
        )

        before = result["max_concentration_before"]
        after = result["max_concentration_after"]

        absolute_reduction = before - after

        percent_reduction = (
            (absolute_reduction / before) * 100
            if before > 0
            else 0.0
        )

        row = {
            "time_step": time_step,
            "changed_nodes": len(changes),
            "valid_nodes": counts["VALID"],
            "transitional_nodes": counts["TRANSITIONAL"],
            "non_compliant_nodes": counts["NON_COMPLIANT"],
            "unsafe_clusters": result["unsafe_clusters_count"],
            "reconfigured": 1 if result["reconfigured"] else 0,
            "reconfiguration_count_step":
                result["reconfiguration_count"],
            "reconfiguration_count_cumulative":
                cumulative_reconfigurations,
            "moved_nodes": result["moved_nodes_count"],
            "moved_nodes_cumulative": cumulative_moved_nodes,
            "max_concentration_before": before,
            "max_concentration_after": after,
            "concentration_reduction_absolute":
                absolute_reduction,
            "concentration_reduction_percent":
                percent_reduction,
        }

        rows.append(row)

        print(
            f"t={time_step:3d} | "
            f"changed={len(changes):2d} | "
            f"NC={counts['NON_COMPLIANT']:3d} | "
            f"unsafe={result['unsafe_clusters_count']:2d} | "
            f"reconf={result['reconfiguration_count']} | "
            f"moved={result['moved_nodes_count']:3d} | "
            f"max before={before:.3f} | "
            f"after={after:.3f}"
        )

    # --------------------------------------------------------
    # 5. Save results
    # --------------------------------------------------------

    raw_csv = save_csv(rows)
    summary_csv, summary = save_summary(rows)
    make_plots(rows)

    # --------------------------------------------------------
    # 6. Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 76)
    print("FINAL SUMMARY")
    print("=" * 76)

    print(
        "Time steps:",
        summary["time_steps"]
    )

    print(
        "Total changed nodes:",
        summary["total_changed_nodes"]
    )

    print(
        "Steps with unsafe clusters:",
        summary["steps_with_unsafe_clusters"]
    )

    print(
        "Total reconfigurations:",
        summary["total_reconfigurations"]
    )

    print(
        "Total moved nodes:",
        summary["total_moved_nodes"]
    )

    print(
        "Mean moved nodes per reconfiguration:",
        round(
            summary["mean_moved_nodes_per_reconfiguration"],
            3
        )
    )

    print(
        "Mean maximum concentration before:",
        round(
            summary["mean_max_concentration_before"],
            4
        )
    )

    print(
        "Mean maximum concentration after:",
        round(
            summary["mean_max_concentration_after"],
            4
        )
    )

    print("\nSaved:")
    print(raw_csv)
    print(summary_csv)
    print(RESULTS_DIR / "concentration_before_after.png")
    print(RESULTS_DIR / "cumulative_reconfigurations.png")
    print(RESULTS_DIR / "moved_nodes_per_step.png")


if __name__ == "__main__":
    main()