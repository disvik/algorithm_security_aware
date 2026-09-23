import random
import matplotlib.pyplot as plt
import networkx as nx

class Node:
    next_id = 1
    
    def __init__(self, power, topology, connectivity):
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
        self.graph = nx.Graph()

    def connect(self, other_node):
        self.graph.add_edge(self.id, other_node.id)

    def disconnect(self, other_node):
        self.graph.remove_edge(self.id, other_node.id)

    def update_connectivity(self):
        """
        Обновляет связность узла.
        """
        # Вычисляем вероятность уменьшения связности на основе мощности узла
        # Чем выше мощность, тем меньше вероятность уменьшения связности
        probability_of_decrease = 0.8 - 0.6 * self.power
        if random.random() < probability_of_decrease:
            # Уменьшаем связность с вероятностью probability_of_decrease
            # Но ограничиваем уменьшение связности в пределах от 0.1 до 1 - (0.25 * (1 - self.power))
            decrease_factor = random.uniform(0.5, 1.0)
            min_decrease = max(0.1, 1 - (0.25 * (1 - self.power)))
            self.connectivity *= max(min_decrease, decrease_factor)
        else:
            # Увеличиваем связность с вероятностью (1 - probability_of_decrease)
            self.connectivity *= random.uniform(1.0, 1.5)
        # Ограничиваем связность в пределах от 0.1 до 1
        self.connectivity = max(0.1, min(self.connectivity, 1))

    def initialize_connections(self, nodes):
        """
        Инициализирует связи узла с другими узлами.

        :param nodes: Список всех узлов в сети.
        """
        for other_node in nodes:
            if other_node != self:
                self.connect(other_node)

    def visualize(self):
        # Создаем граф
        graph = nx.Graph()
        
        # Добавляем узел в граф
        graph.add_node(self.id)

        # Добавляем связи в граф
        for edge in self.graph.edges:
            graph.add_edge(edge[0], edge[1])

        # Рисуем граф
        nx.draw(graph, with_labels=True, node_size=500, node_color='skyblue', font_size=12, font_weight='bold')
        plt.show()


    def __str__(self):
        return f"Node with id {self.id}, power {self.power}, connectivity {self.connectivity}, and topology {self.topology}"
