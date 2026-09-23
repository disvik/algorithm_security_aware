import random

class Node:
    def __init__(self, power, topology, connectivity):
        """
        Создает новый узел с заданной мощностью, топологией и связностью.

        :param power: Мощность узла (в пределах от 0.1 до 1).
        :param topology: Кортеж, представляющий топологию узла (X, Y).
        :param connectivity: Характер связности узла (в пределах от 0.1 до 1).
        """
        if power < 0.1 or power > 1:
            raise ValueError("Мощность должна быть между 0.1 и 1.")
        if not (0 <= topology[0] <= 1) or not (0 <= topology[1] <= 1):
            raise ValueError("Топология варьируется от 0 до 1.")
        if not (0.1 <= connectivity <= 1):
            raise ValueError("Связность определяема между 0.1 и 1.")
        self.power = power
        self.topology = topology
        self.connectivity = connectivity
        self.connections = set()

    def connect(self, other_node):
        """
        Устанавливает связь между текущим узлом и другим узлом.

        :param other_node: Другой узел, с которым устанавливается связь.
        """
        self.connections.add(other_node)
        other_node.connections.add(self)

    def disconnect(self, other_node):
        """
        Разрывает связь между текущим узлом и другим узлом.

        :param other_node: Узел, с которым разрывается связь.
        """
        if other_node in self.connections:
            self.connections.remove(other_node)
        if self in other_node.connections:
            other_node.connections.remove(self)

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


    def __str__(self):
        """
        Возвращает строковое представление узла.

        :return: Строковое представление узла.
        """
        return f"Node with power {self.power}, connectivity {self.connectivity}, and topology {self.topology}"