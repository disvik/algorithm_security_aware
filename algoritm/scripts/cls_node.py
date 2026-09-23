import random
import matplotlib.pyplot as plt
import networkx as nx


class Node:
    next_id = 1

    def __init__(
        self,
        power,
        topology,
        connectivity,
        crypto_algorithm="AES-256",
        crypto_security_level=3,
        crypto_policy_version=2,
        key_valid=True
    ):
        if power < 0.1 or power > 1:
            raise ValueError("Мощность должна быть между 0.1 и 1.")
        if not (0 <= topology[0] <= 1) or not (0 <= topology[1] <= 1):
            raise ValueError("Топология варьируется от 0 до 1.")
        if not (0.1 <= connectivity <= 1):
            raise ValueError("Связность определяется между 0.1 и 1.")

        self.id = Node.next_id
        Node.next_id += 1

        self.power = power
        self.topology = topology
        self.connectivity = connectivity
        self.sync_state = 0
        self.graph = nx.Graph()

        # Cryptographic configuration/state
        self.crypto_algorithm = crypto_algorithm
        self.crypto_security_level = crypto_security_level
        self.crypto_policy_version = crypto_policy_version
        self.key_valid = key_valid
        self.crypto_state = "UNKNOWN"

    def evaluate_crypto_state(
        self,
        required_algorithm="AES-256",
        minimum_security_level=3,
        required_policy_version=2
    ):
        """Оценивает криптографическое состояние узла относительно политики сети."""
        if not self.key_valid:
            self.crypto_state = "NON_COMPLIANT"
            return self.crypto_state

        if (
            self.crypto_algorithm == required_algorithm
            and self.crypto_security_level >= minimum_security_level
            and self.crypto_policy_version == required_policy_version
        ):
            self.crypto_state = "VALID"

        elif (
            self.crypto_algorithm == required_algorithm
            and self.crypto_security_level >= minimum_security_level
            and self.crypto_policy_version < required_policy_version
        ):
            self.crypto_state = "TRANSITIONAL"

        else:
            self.crypto_state = "NON_COMPLIANT"

        return self.crypto_state

    def update_crypto_state(
        self,
        required_algorithm="AES-256",
        minimum_security_level=3,
        required_policy_version=2
    ):
        """Повторно вычисляет криптографическое состояние узла."""
        return self.evaluate_crypto_state(
            required_algorithm=required_algorithm,
            minimum_security_level=minimum_security_level,
            required_policy_version=required_policy_version
        )

    def connect(self, other_node):
        self.graph.add_edge(self.id, other_node.id)

    def disconnect(self, other_node):
        self.graph.remove_edge(self.id, other_node.id)

    def update_connectivity(self):
        """Обновляет связность узла."""
        probability_of_decrease = 0.8 - 0.6 * self.power

        if random.random() < probability_of_decrease:
            decrease_factor = random.uniform(0.5, 1.0)
            min_decrease = max(0.1, 1 - (0.25 * (1 - self.power)))
            self.connectivity *= max(min_decrease, decrease_factor)
        else:
            self.connectivity *= random.uniform(1.0, 1.5)

        self.connectivity = max(0.1, min(self.connectivity, 1))

    def initialize_connections(self, nodes):
        for other_node in nodes:
            if other_node != self:
                self.connect(other_node)

    def visualize(self):
        graph = nx.Graph()
        graph.add_node(self.id)

        for edge in self.graph.edges:
            graph.add_edge(edge[0], edge[1])

        nx.draw(
            graph,
            with_labels=True,
            node_size=500,
            node_color='skyblue',
            font_size=12,
            font_weight='bold'
        )
        plt.show()

    def __str__(self):
        sync_state_str = (
            "Synchronized" if self.sync_state == 1 else "Not synchronized"
        )

        return (
            f"Node with id {self.id}, "
            f"power {self.power}, "
            f"connectivity {self.connectivity}, "
            f"topology {self.topology}, "
            f"sync state {sync_state_str}, "
            f"crypto algorithm {self.crypto_algorithm}, "
            f"crypto security level {self.crypto_security_level}, "
            f"crypto policy version {self.crypto_policy_version}, "
            f"key valid {self.key_valid}, "
            f"crypto state {self.crypto_state}"
        )
