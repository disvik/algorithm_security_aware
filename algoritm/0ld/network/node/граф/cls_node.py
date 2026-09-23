import random
import networkx as nx
import matplotlib.pyplot as plt

class Node:
    next_id = 1  # Используем 1 в качестве начального значения для идентификаторов
    
    def __init__(self, A, B, C):
        self.id = Node.next_id  # Присваиваем уникальный идентификатор
        Node.next_id += 1
        self.A = A
        self.B = B
        self.C = C

    def __str__(self):
        """
        Возвращает строковое представление узла.

        :return: Строковое представление узла.
        """
        return f"Node {self.id}: A={self.A}, B={self.B}, C={self.C}"

# Создаем граф
G = nx.Graph()

# Создаем 100 узлов с произвольными свойствами A, B и C
for i in range(100):
    A = random.randint(1, 10)
    B = random.uniform(0.1, 1)
    C = random.choice(['X', 'Y', 'Z'])
    G.add_node(i, A=A, B=B, C=C)

# Выводим информацию о свойствах узлов
for node_id in G.nodes():
    print(G.nodes[node_id])

# Рисуем граф
nx.draw(G, with_labels=True)
plt.show()
