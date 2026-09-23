# Этот файл описывает конечную структуру

import random
import time
import matplotlib.pyplot as plt
from cls_node import Node

def update_dynamic_properties(nodes):
    """
    Обновляет динамические свойства узлов.

    :param nodes: Список узлов для обновления.
    """
    for node in nodes:
        # Изменяем связность узла
        node.update_connectivity()

def visualize_nodes(nodes, ax):
    """
    Визуализирует узлы и связи между ними на плоскости.

    :param nodes: Список узлов для визуализации.
    :param ax: Объект осей для построения графика.
    """
    # Получаем координаты X и Y для каждого узла
    x = [node.topology[0] for node in nodes]
    y = [node.topology[1] for node in nodes]

    # Получаем размеры точек на основе их мощности
    sizes = [node.power * 100 for node in nodes]

    # Получаем прозрачность точек на основе их связности
    # Чем больше связность, тем менее прозрачная точка
    alpha = [node.connectivity for node in nodes]

    # Визуализируем узлы
    ax.clear()
    ax.scatter(x, y, s=sizes, alpha=alpha, cmap='viridis')

    # Отображаем связи между узлами в виде линий
    for node in nodes:
        for connected_node in node.graph.neighbors(node):
            ax.plot([node.topology[0], connected_node.topology[0]], [node.topology[1], connected_node.topology[1]], color='gray', alpha=0.5, zorder=0)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Node Visualization')
    ax.grid(True)


def main():
    # Создаем 100 узлов с двумя связями для каждого
    nodes = [Node(random.uniform(0.1, 1), (random.random(), random.random()), random.uniform(0.1, 1)) for _ in range(100)]
    for node in nodes:
        node.initialize_connections(nodes)

    # Задаем интервал обновления свойств узлов в секундах
    update_interval = 1

    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        while True:
            # Обновляем динамические свойства узлов
            update_dynamic_properties(nodes)

            # Визуализируем узлы и связи между ними
            visualize_nodes(nodes, ax)
            plt.pause(0.01)  # Небольшая пауза, чтобы график успел обновиться

            # Ждем указанный интервал времени перед следующим обновлением
            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("Программа завершена.")
        plt.close()

if __name__ == "__main__":
    main()
