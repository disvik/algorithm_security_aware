import random
import time
from cls_node import Node

class Network:
    def __init__(self):
        self.nodes = []

    def create_network(self, size):
        self.create_nodes(size)
        self.create_edges()

    def create_nodes(self, size):
        # Создаем узлы
        self.nodes = []
        for i in range(size):
            power = random.uniform(0.1, 1)
            topology = (random.random(), random.random())
            connectivity = random.uniform(0.1, 1)
            node = Node(power, topology, connectivity)
            self.nodes.append(node)

    def create_edges(self):
        # Создаем связи между узлами
        for node in self.nodes:
            # Определяем количество связей в зависимости от свойств узла
            num_connections = self.calculate_connections(node)
            # Создаем связи
            for _ in range(num_connections):
                # Выбираем узел, к которому будем создавать связь
                other_node = self.choose_node_to_connect(node)
                if other_node is not None:
                    node.connect(other_node)

    def update_edges(self):
        # Удаляем все текущие связи
        for node in self.nodes:
            node.graph.clear()
        # Создаем связи заново на основе обновленных свойств связности
        self.create_edges()


    def choose_node_to_connect(self, node):
        # Составляем список узлов для выбора
        candidate_nodes = []
        for other_node in self.nodes:
            if other_node != node and not node.graph.has_edge(node.id, other_node.id):
                candidate_nodes.append(other_node)
        if not candidate_nodes:
            return None  # Если нет кандидатов для связи, возвращаем None

        # Определяем вероятности выбора узлов на основе их топологии и связности
        probabilities = []
        for other_node in candidate_nodes:
            distance = self.calculate_distance(node.topology, other_node.topology)
            # Изменяем вычисление вероятности на обратно пропорциональную близости узлов по топологии
            probability = 1 / distance  # Чем ближе узлы, тем больше вероятность
            probabilities.append(probability)

        # Выбираем узел с учетом вероятностей
        chosen_node = random.choices(candidate_nodes, weights=probabilities, k=1)[0]
        return chosen_node


    def calculate_distance(self, topology1, topology2):
        # Вычисляем "расстояние" между топологиями (может быть как расстояние между точками, так и как мера близости)
        # Например, евклидово расстояние между точками в двумерном пространстве
        distance = ((topology1[0] - topology2[0]) ** 2 + (topology1[1] - topology2[1]) ** 2) ** 0.5
        return max(distance, 0.01)  # Убеждаемся, что расстояние не равно нулю, чтобы избежать деления на ноль


    def calculate_connections(self, node):
        # Вычисляем количество связей на основе свойства связности узла
        connectivity = node.connectivity
        num_connections = round(connectivity * 5)  # Умножаем на 10 и округляем до целого числа
        return max(num_connections, 1)  # Убеждаемся, что количество связей как минимум 1

    def print_nodes_connections(self):
        for node in self.nodes:
            print(f"Node {node.id} connections:")
            print(node.graph.edges)
            print()


    @staticmethod
    def print_nodes_info(nodes):
        for i, node in enumerate(nodes):
            print(f"Node {i+1}:")
            print(f"ID: {node.id}")
            print(f"Power: {node.power}")
            print(f"Topology: {node.topology}")
            print(f"Connectivity: {node.connectivity}")
            print(f"Connections: {list(node.graph.edges)}")
            print()

if __name__ == "__main__":
    network = Network()
    network.create_network(100)
    network.print_nodes_info(network.nodes)
    network.print_nodes_connections()
    
    # Визуализируем каждый узел
    for node in network.nodes:
        node.visualize()


