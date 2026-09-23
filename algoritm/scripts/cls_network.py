import random
import math

from cls_node import Node
from crypto_state import CryptoPolicy


class Network:
    def __init__(self, total_power=0, clustered=False):
        self.nodes = []
        self.total_power = total_power
        self.clustered = clustered

        # Списки внутрикластерных и межкластерных связей.
        self.intra_cluster_edges = []
        self.inter_cluster_edges = []

    # ============================================================
    # NETWORK CREATION
    # ============================================================

    def create_network(self, size):
        self.create_nodes(size)
        self.create_edges()

    def create_nodes(self, size):
        """
        Создание узлов сети.
        """

        self.nodes = []
        self.total_power = 0

        for _ in range(size):
            power = random.uniform(0.1, 1)

            topology = (
                random.random(),
                random.random()
            )

            connectivity = random.uniform(
                0.1,
                1
            )

            node = Node(
                power,
                topology,
                connectivity
            )

            self.nodes.append(node)
            self.total_power += power

    # ============================================================
    # MINING
    # ============================================================

    def choose_node_for_mining(self):
        """
        Выбор узла для майнинга пропорционально его мощности.

        На втором этапе исследования crypto_state сюда
        намеренно не добавляется, чтобы влияние нового метода
        было связано именно с кластеризацией.
        """

        weights = [
            node.power / self.total_power
            for node in self.nodes
        ]

        chosen_node = random.choices(
            self.nodes,
            weights=weights,
            k=1
        )[0]

        return chosen_node

    # ============================================================
    # EDGES
    # ============================================================

    def create_edges(self):
        """
        Создание сетевых связей.
        """

        for node in self.nodes:
            num_connections = self.calculate_connections(node)

            for _ in range(num_connections):
                other_node = self.choose_node_to_connect(node)

                if other_node is not None:
                    node.connect(other_node)

    def update_edges(self):
        """
        Полная реконфигурация исходных сетевых связей.
        """

        for node in self.nodes:
            node.graph.clear()

        self.create_edges()

    def choose_node_to_connect(self, node):
        """
        Выбор узла для создания связи.
        """

        candidate_nodes = []

        for other_node in self.nodes:
            if (
                other_node != node
                and not node.graph.has_edge(
                    node.id,
                    other_node.id
                )
            ):
                candidate_nodes.append(other_node)

        if not candidate_nodes:
            return None

        probabilities = []

        for other_node in candidate_nodes:
            distance = self.calculate_distance(
                node.topology,
                other_node.topology
            )

            probability = 1 / distance
            probabilities.append(probability)

        chosen_node = random.choices(
            candidate_nodes,
            weights=probabilities,
            k=1
        )[0]

        return chosen_node

    def calculate_distance(self, topology1, topology2):
        """
        Евклидово расстояние между двумя топологическими
        координатами.
        """

        distance = (
            (topology1[0] - topology2[0]) ** 2
            + (topology1[1] - topology2[1]) ** 2
        ) ** 0.5

        return max(distance, 0.01)

    def calculate_connections(self, node):
        """
        Число связей определяется через параметр connectivity.
        """

        num_connections = round(
            node.connectivity * 5
        )

        return max(num_connections, 1)

    def print_nodes_connections(self):
        for node in self.nodes:
            print(
                f"Node {node.id} connections:"
            )
            print(node.graph.edges)
            print()

    # ============================================================
    # BASELINE CLUSTERING
    # ============================================================

    def split_into_clusters(self):
        """
        Базовый метод динамической кластеризации
        из первого научного результата.
        """

        num_clusters = math.ceil(
            math.sqrt(len(self.nodes))
        )

        sorted_nodes = sorted(
            self.nodes,
            key=lambda node: (
                node.power,
                node.connectivity,
                node.topology
            )
        )

        clusters = [
            []
            for _ in range(num_clusters)
        ]

        cluster_sums = [
            (0, 0)
            for _ in range(num_clusters)
        ]

        for node in sorted_nodes:
            min_cluster = min(
                range(num_clusters),
                key=lambda i: sum(
                    cluster_sums[i]
                )
            )

            clusters[min_cluster].append(node)

            cluster_sums[min_cluster] = (
                cluster_sums[min_cluster][0]
                + node.power,
                cluster_sums[min_cluster][1]
                + node.connectivity
            )

        self.clustered = True

        # Не накапливаем старые связи при повторном запуске.
        self.intra_cluster_edges = []
        self.inter_cluster_edges = []

        self.add_intra_cluster_links(clusters)
        self.add_inter_cluster_links(clusters)

        return clusters

    # ============================================================
    # CONTROLLED CRYPTO STATE DISTRIBUTION
    # ============================================================

    def assign_crypto_states(
        self,
        valid_ratio=0.7,
        transitional_ratio=0.2,
        non_compliant_ratio=0.1
    ):
        """
        Контролируемое распределение криптографических
        конфигураций узлов.

        Сумма долей должна равняться 1.
        """

        total_ratio = (
            valid_ratio
            + transitional_ratio
            + non_compliant_ratio
        )

        if abs(total_ratio - 1.0) > 1e-9:
            raise ValueError(
                "Сумма valid_ratio + transitional_ratio + "
                "non_compliant_ratio должна быть равна 1."
            )

        nodes = self.nodes.copy()
        random.shuffle(nodes)

        total_nodes = len(nodes)

        valid_count = int(
            total_nodes * valid_ratio
        )

        transitional_count = int(
            total_nodes * transitional_ratio
        )

        non_compliant_count = (
            total_nodes
            - valid_count
            - transitional_count
        )

        # VALID
        for node in nodes[:valid_count]:
            node.crypto_algorithm = "AES-256"
            node.crypto_security_level = 3
            node.crypto_policy_version = 2
            node.key_valid = True

        # TRANSITIONAL
        transitional_start = valid_count
        transitional_end = (
            valid_count + transitional_count
        )

        for node in nodes[
            transitional_start:transitional_end
        ]:
            node.crypto_algorithm = "AES-256"
            node.crypto_security_level = 3
            node.crypto_policy_version = 1
            node.key_valid = True

        # NON_COMPLIANT
        non_compliant_start = transitional_end
        non_compliant_end = (
            transitional_end
            + non_compliant_count
        )

        for node in nodes[
            non_compliant_start:non_compliant_end
        ]:
            node.crypto_algorithm = "AES-128"
            node.crypto_security_level = 2
            node.crypto_policy_version = 1
            node.key_valid = True

        return self.nodes

    def evaluate_crypto_states(self, crypto_policy):
        """
        Пересчитывает crypto_state всех узлов сети
        относительно текущей CryptoPolicy.
        """

        for node in self.nodes:
            crypto_policy.apply_to_node(node)

        return self.nodes

    # ============================================================
    # NORMALIZED SECURITY-AWARE CLUSTERING
    # ============================================================

    def split_into_security_aware_clusters(
        self,
        crypto_policy,
        w_nc=2.0,
        w_tr=1.0,
        resource_weight=1.0
    ):
        """
        Нормализованная Security-Aware Dynamic Clustering.

        В критерии учитываются:
            1. нормализованная ресурсная нагрузка;
            2. доля NON_COMPLIANT;
            3. доля TRANSITIONAL.

        Параметры:
            w_nc            - вес NON_COMPLIANT;
            w_tr            - вес TRANSITIONAL;
            resource_weight - вес ресурсной составляющей.

        Эти веса являются параметрами модели и могут
        исследоваться в sensitivity analysis.
        """

        if not self.nodes:
            return []

        if w_nc < 0 or w_tr < 0 or resource_weight < 0:
            raise ValueError(
                "Веса w_nc, w_tr и resource_weight "
                "не могут быть отрицательными."
            )

        num_clusters = math.ceil(
            math.sqrt(len(self.nodes))
        )

        self.evaluate_crypto_states(
            crypto_policy
        )

        crypto_priority = {
            "VALID": 0,
            "TRANSITIONAL": 1,
            "NON_COMPLIANT": 2
        }

        sorted_nodes = sorted(
            self.nodes,
            key=lambda node: (
                crypto_priority.get(
                    node.crypto_state,
                    3
                ),
                node.power,
                node.connectivity,
                node.topology
            )
        )

        clusters = [
            []
            for _ in range(num_clusters)
        ]

        cluster_sums = [
            {
                "power": 0.0,
                "connectivity": 0.0,
                "non_compliant": 0,
                "transitional": 0
            }
            for _ in range(num_clusters)
        ]

        total_power = sum(
            node.power
            for node in self.nodes
        )

        total_connectivity = sum(
            node.connectivity
            for node in self.nodes
        )

        for node in sorted_nodes:

            def cluster_score(cluster_index):
                cluster_data = cluster_sums[
                    cluster_index
                ]

                current_cluster = clusters[
                    cluster_index
                ]

                current_size = len(
                    current_cluster
                )

                # Прогнозируем состояние кластера
                # после добавления текущего узла.
                projected_power = (
                    cluster_data["power"]
                    + node.power
                )

                projected_connectivity = (
                    cluster_data["connectivity"]
                    + node.connectivity
                )

                projected_size = (
                    current_size + 1
                )

                projected_non_compliant = (
                    cluster_data["non_compliant"]
                    + (
                        1
                        if node.crypto_state
                        == "NON_COMPLIANT"
                        else 0
                    )
                )

                projected_transitional = (
                    cluster_data["transitional"]
                    + (
                        1
                        if node.crypto_state
                        == "TRANSITIONAL"
                        else 0
                    )
                )

                # Нормализованная ресурсная часть.
                normalized_power = (
                    projected_power
                    / total_power
                    if total_power > 0
                    else 0.0
                )

                normalized_connectivity = (
                    projected_connectivity
                    / total_connectivity
                    if total_connectivity > 0
                    else 0.0
                )

                resource_load = (
                    0.5
                    * (
                        normalized_power
                        + normalized_connectivity
                    )
                )

                # Нормализованные security-компоненты.
                non_compliant_ratio = (
                    projected_non_compliant
                    / projected_size
                )

                transitional_ratio = (
                    projected_transitional
                    / projected_size
                )

                score = (
                    resource_weight
                    * resource_load
                    + w_nc
                    * non_compliant_ratio
                    + w_tr
                    * transitional_ratio
                )

                return score

            min_cluster = min(
                range(num_clusters),
                key=cluster_score
            )

            clusters[min_cluster].append(
                node
            )

            cluster_sums[
                min_cluster
            ]["power"] += (
                node.power
            )

            cluster_sums[
                min_cluster
            ]["connectivity"] += (
                node.connectivity
            )

            if (
                node.crypto_state
                == "NON_COMPLIANT"
            ):
                cluster_sums[
                    min_cluster
                ]["non_compliant"] += 1

            elif (
                node.crypto_state
                == "TRANSITIONAL"
            ):
                cluster_sums[
                    min_cluster
                ]["transitional"] += 1

        self.clustered = True

        self.intra_cluster_edges = []
        self.inter_cluster_edges = []

        self.add_intra_cluster_links(
            clusters
        )
        self.add_inter_cluster_links(
            clusters
        )

        return clusters

    # ============================================================
    # DYNAMIC CRYPTO-STATE CHANGES
    # ============================================================

    def simulate_crypto_state_changes(
        self,
        crypto_policy,
        change_ratio=0.10,
        deterioration_probability=0.75
    ):
        """
        Имитирует изменение криптографической конфигурации
        части узлов во времени.
        """

        if not (0 <= change_ratio <= 1):
            raise ValueError(
                "change_ratio должен быть "
                "в диапазоне [0, 1]."
            )

        if not (
            0
            <= deterioration_probability
            <= 1
        ):
            raise ValueError(
                "deterioration_probability должна быть "
                "в диапазоне [0, 1]."
            )

        if not self.nodes:
            return []

        self.evaluate_crypto_states(
            crypto_policy
        )

        number_to_change = max(
            1,
            int(
                len(self.nodes)
                * change_ratio
            )
        )

        number_to_change = min(
            number_to_change,
            len(self.nodes)
        )

        selected_nodes = random.sample(
            self.nodes,
            number_to_change
        )

        changed_nodes = []

        for node in selected_nodes:
            old_state = node.crypto_state

            deteriorate = (
                random.random()
                < deterioration_probability
            )

            if old_state == "VALID":
                if deteriorate:
                    if random.random() < 0.5:
                        node.crypto_algorithm = (
                            crypto_policy
                            .required_algorithm
                        )

                        node.crypto_security_level = (
                            crypto_policy
                            .minimum_security_level
                        )

                        node.crypto_policy_version = max(
                            0,
                            crypto_policy
                            .policy_version
                            - 1
                        )

                        node.key_valid = True

                    else:
                        node.crypto_algorithm = (
                            "AES-128"
                        )

                        node.crypto_security_level = max(
                            1,
                            crypto_policy
                            .minimum_security_level
                            - 1
                        )

                        node.crypto_policy_version = max(
                            0,
                            crypto_policy
                            .policy_version
                            - 1
                        )

                        node.key_valid = True

            elif old_state == "TRANSITIONAL":
                if deteriorate:
                    node.crypto_algorithm = (
                        "AES-128"
                    )

                    node.crypto_security_level = max(
                        1,
                        crypto_policy
                        .minimum_security_level
                        - 1
                    )

                    node.crypto_policy_version = max(
                        0,
                        crypto_policy
                        .policy_version
                        - 1
                    )

                    node.key_valid = True

                else:
                    node.crypto_algorithm = (
                        crypto_policy
                        .required_algorithm
                    )

                    node.crypto_security_level = (
                        crypto_policy
                        .minimum_security_level
                    )

                    node.crypto_policy_version = (
                        crypto_policy
                        .policy_version
                    )

                    node.key_valid = True

            elif old_state == "NON_COMPLIANT":
                if not deteriorate:
                    if random.random() < 0.5:
                        node.crypto_algorithm = (
                            crypto_policy
                            .required_algorithm
                        )

                        node.crypto_security_level = (
                            crypto_policy
                            .minimum_security_level
                        )

                        node.crypto_policy_version = (
                            crypto_policy
                            .policy_version
                        )

                        node.key_valid = True

                    else:
                        node.crypto_algorithm = (
                            crypto_policy
                            .required_algorithm
                        )

                        node.crypto_security_level = (
                            crypto_policy
                            .minimum_security_level
                        )

                        node.crypto_policy_version = max(
                            0,
                            crypto_policy
                            .policy_version
                            - 1
                        )

                        node.key_valid = True

            new_state = (
                crypto_policy
                .apply_to_node(
                    node
                )
            )

            if new_state != old_state:
                changed_nodes.append(
                    {
                        "node_id":
                            node.id,
                        "old_state":
                            old_state,
                        "new_state":
                            new_state
                    }
                )

        return changed_nodes

    # ============================================================
    # CLUSTER SECURITY METRICS
    # ============================================================

    def get_cluster_crypto_statistics(
        self,
        cluster
    ):
        """
        Статистика криптографических состояний
        одного кластера.
        """

        total = len(cluster)

        valid = sum(
            1
            for node in cluster
            if node.crypto_state == "VALID"
        )

        transitional = sum(
            1
            for node in cluster
            if node.crypto_state
            == "TRANSITIONAL"
        )

        non_compliant = sum(
            1
            for node in cluster
            if node.crypto_state
            == "NON_COMPLIANT"
        )

        non_compliant_ratio = (
            non_compliant / total
            if total > 0
            else 0.0
        )

        transitional_ratio = (
            transitional / total
            if total > 0
            else 0.0
        )

        return {
            "total":
                total,
            "valid":
                valid,
            "transitional":
                transitional,
            "non_compliant":
                non_compliant,
            "non_compliant_ratio":
                non_compliant_ratio,
            "transitional_ratio":
                transitional_ratio
        }

    def cluster_requires_reconfiguration(
        self,
        cluster,
        max_non_compliant_ratio=0.20
    ):
        """
        Проверка условия реконфигурации.
        """

        stats = (
            self
            .get_cluster_crypto_statistics(
                cluster
            )
        )

        return (
            stats[
                "non_compliant_ratio"
            ]
            > max_non_compliant_ratio
        )

    def evaluate_cluster_security(
        self,
        clusters,
        max_non_compliant_ratio=0.20
    ):
        """
        Возвращает индексы кластеров,
        нарушающих установленный порог.
        """

        unsafe_clusters = []

        for index, cluster in enumerate(
            clusters
        ):
            if (
                self
                .cluster_requires_reconfiguration(
                    cluster,
                    max_non_compliant_ratio
                )
            ):
                unsafe_clusters.append(
                    index
                )

        return unsafe_clusters

    def maximum_non_compliant_concentration(
        self,
        clusters
    ):
        """
        Максимальная доля NON_COMPLIANT
        среди всех кластеров.
        """

        if not clusters:
            return 0.0

        concentrations = []

        for cluster in clusters:
            stats = (
                self
                .get_cluster_crypto_statistics(
                    cluster
                )
            )

            concentrations.append(
                stats[
                    "non_compliant_ratio"
                ]
            )

        return max(concentrations)

    # ============================================================
    # DYNAMIC SECURITY-AWARE RECONFIGURATION
    # ============================================================

    def reconfigure_security_aware_clusters(
        self,
        clusters,
        crypto_policy,
        max_non_compliant_ratio=0.20,
        w_nc=2.0,
        w_tr=1.0,
        resource_weight=1.0
    ):
        """
        Проверяет состояние кластеров.

        Если хотя бы один кластер превышает
        допустимую долю NON_COMPLIANT,
        выполняется повторная нормализованная
        security-aware кластеризация.

        При реконфигурации используются те же веса,
        что и при первичном формировании кластеров.
        """

        self.evaluate_crypto_states(
            crypto_policy
        )

        concentration_before = (
            self
            .maximum_non_compliant_concentration(
                clusters
            )
        )

        unsafe_clusters = (
            self
            .evaluate_cluster_security(
                clusters,
                max_non_compliant_ratio
            )
        )

        if not unsafe_clusters:
            return {
                "clusters":
                    clusters,
                "reconfigured":
                    False,
                "reconfiguration_count":
                    0,
                "unsafe_clusters":
                    unsafe_clusters,
                "unsafe_clusters_count":
                    0,
                "moved_nodes":
                    [],
                "moved_nodes_count":
                    0,
                "max_concentration_before":
                    concentration_before,
                "max_concentration_after":
                    concentration_before
            }

        old_assignments = {}

        for cluster_index, cluster in enumerate(
            clusters
        ):
            for node in cluster:
                old_assignments[
                    node.id
                ] = cluster_index

        new_clusters = (
            self
            .split_into_security_aware_clusters(
                crypto_policy,
                w_nc=w_nc,
                w_tr=w_tr,
                resource_weight=resource_weight
            )
        )

        moved_nodes = []

        for cluster_index, cluster in enumerate(
            new_clusters
        ):
            for node in cluster:
                old_cluster = (
                    old_assignments.get(
                        node.id
                    )
                )

                if old_cluster != cluster_index:
                    moved_nodes.append(
                        node.id
                    )

        concentration_after = (
            self
            .maximum_non_compliant_concentration(
                new_clusters
            )
        )

        return {
            "clusters":
                new_clusters,
            "reconfigured":
                True,
            "reconfiguration_count":
                1,
            "unsafe_clusters":
                unsafe_clusters,
            "unsafe_clusters_count":
                len(unsafe_clusters),
            "moved_nodes":
                moved_nodes,
            "moved_nodes_count":
                len(moved_nodes),
            "max_concentration_before":
                concentration_before,
            "max_concentration_after":
                concentration_after
        }

    # ============================================================
    # CLUSTER LINKS
    # ============================================================

    def add_intra_cluster_links(
        self,
        clusters
    ):
        """
        Создание внутрикластерных связей.
        """

        self.intra_cluster_edges = []

        for cluster in clusters:
            cluster_edges = []

            for j, node1 in enumerate(
                cluster
            ):
                for node2 in cluster[
                    j + 1:
                ]:
                    probability = min(
                        node1.power,
                        1.0
                    )

                    if (
                        random.random()
                        < probability
                    ):
                        node1.connect(
                            node2
                        )

                        cluster_edges.append(
                            (
                                node1.id,
                                node2.id
                            )
                        )

            self.intra_cluster_edges.append(
                cluster_edges
            )

    def add_inter_cluster_links(
        self,
        clusters
    ):
        """
        Создание межкластерных связей.
        """

        self.inter_cluster_edges = []

        for i in range(
            len(clusters)
        ):
            for j in range(
                i + 1,
                len(clusters)
            ):
                for node_i in clusters[i]:
                    for node_j in clusters[j]:
                        edge_info = (
                            node_i,
                            node_j,
                            clusters[i],
                            clusters[j]
                        )

                        self.inter_cluster_edges.append(
                            edge_info
                        )

    # ============================================================
    # OUTPUT
    # ============================================================

    def display_edges(self):
        """
        Вывод информации о связях.
        """

        print(
            "Внутрикластерные связи:"
        )

        for cluster_number, edges in enumerate(
            self.intra_cluster_edges,
            start=1
        ):
            print(
                f"Cluster {cluster_number}:"
            )

            for edge in edges:
                print(edge)

        print(
            "\nМежкластерные связи:"
        )

        for edge in self.inter_cluster_edges:
            node_1 = edge[0]
            node_2 = edge[1]

            print(
                f"{node_1.id} -> "
                f"{node_2.id}"
            )

    @staticmethod
    def print_nodes_info(nodes):
        """
        Информация об узлах.
        """

        for i, node in enumerate(
            nodes
        ):
            sync_state_str = (
                "Synchronized"
                if node.sync_state == 1
                else "Not synchronized"
            )

            print(
                f"Node {i + 1}:"
            )
            print(
                f"ID: {node.id}"
            )
            print(
                f"Power: {node.power}"
            )
            print(
                f"Topology: {node.topology}"
            )
            print(
                f"Connectivity: "
                f"{node.connectivity}"
            )
            print(
                f"Sync state: "
                f"{sync_state_str}"
            )
            print(
                f"Crypto algorithm: "
                f"{node.crypto_algorithm}"
            )
            print(
                f"Crypto security level: "
                f"{node.crypto_security_level}"
            )
            print(
                f"Crypto policy version: "
                f"{node.crypto_policy_version}"
            )
            print(
                f"Key valid: "
                f"{node.key_valid}"
            )
            print(
                f"Crypto state: "
                f"{node.crypto_state}"
            )
            print(
                f"Connections: "
                f"{list(node.graph.edges)}"
            )
            print()


# ================================================================
# SIMPLE TEST
# ================================================================

if __name__ == "__main__":

    random.seed(42)

    network = Network()

    network.create_network(
        100
    )

    policy = CryptoPolicy(
        required_algorithm="AES-256",
        minimum_security_level=3,
        policy_version=2
    )

    network.assign_crypto_states(
        valid_ratio=0.70,
        transitional_ratio=0.20,
        non_compliant_ratio=0.10
    )

    network.evaluate_crypto_states(
        policy
    )

    clusters = (
        network
        .split_into_security_aware_clusters(
            policy,
            w_nc=2.0,
            w_tr=1.0,
            resource_weight=1.0
        )
    )

    print(
        "\nINITIAL SECURITY-AWARE CLUSTERS"
    )

    for i, cluster in enumerate(
        clusters,
        start=1
    ):
        stats = (
            network
            .get_cluster_crypto_statistics(
                cluster
            )
        )

        print(
            f"Cluster {i}: "
            f"nodes={stats['total']}, "
            f"VALID={stats['valid']}, "
            f"TRANSITIONAL="
            f"{stats['transitional']}, "
            f"NON_COMPLIANT="
            f"{stats['non_compliant']}, "
            f"NC ratio="
            f"{stats['non_compliant_ratio']:.3f}"
        )

    print(
        "\nSIMULATING CRYPTO-STATE CHANGES"
    )

    changes = (
        network
        .simulate_crypto_state_changes(
            policy,
            change_ratio=0.10,
            deterioration_probability=0.75
        )
    )

    print(
        "Actually changed nodes:",
        len(changes)
    )

    for change in changes:
        print(
            f"Node {change['node_id']}: "
            f"{change['old_state']} "
            f"-> "
            f"{change['new_state']}"
        )

    result = (
        network
        .reconfigure_security_aware_clusters(
            clusters,
            policy,
            max_non_compliant_ratio=0.20,
            w_nc=2.0,
            w_tr=1.0,
            resource_weight=1.0
        )
    )

    print(
        "\nRECONFIGURATION RESULT"
    )

    print(
        "Reconfigured:",
        result["reconfigured"]
    )

    print(
        "Unsafe clusters:",
        result["unsafe_clusters"]
    )

    print(
        "Moved nodes:",
        result["moved_nodes_count"]
    )

    print(
        "Maximum concentration before:",
        round(
            result[
                "max_concentration_before"
            ],
            4
        )
    )

    print(
        "Maximum concentration after:",
        round(
            result[
                "max_concentration_after"
            ],
            4
        )
    )

    final_clusters = (
        result["clusters"]
    )

    print(
        "\nFINAL CLUSTERS"
    )

    for i, cluster in enumerate(
        final_clusters,
        start=1
    ):
        stats = (
            network
            .get_cluster_crypto_statistics(
                cluster
            )
        )

        print(
            f"Cluster {i}: "
            f"nodes={stats['total']}, "
            f"VALID={stats['valid']}, "
            f"TRANSITIONAL="
            f"{stats['transitional']}, "
            f"NON_COMPLIANT="
            f"{stats['non_compliant']}, "
            f"NC ratio="
            f"{stats['non_compliant_ratio']:.3f}"
        )