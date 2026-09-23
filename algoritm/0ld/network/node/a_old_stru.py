import random
import time
import matplotlib.pyplot as plt
from 0_old_node import Node

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
    Визуализирует узлы на плоскости.

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
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Node Visualization')
    ax.grid(True)


def main():
    # Создаем несколько узлов для тестирования
    nodes = [Node(random.uniform(0.1, 1), (random.random(), random.random()), random.uniform(0.1, 1)) for _ in range(100)]

    # Задаем интервал обновления свойств узлов в секундах
    update_interval = 1

    fig, ax = plt.subplots(figsize=(8, 6))

    try:
        while True:
            # Обновляем динамические свойства узлов
            update_dynamic_properties(nodes)

            # Визуализируем узлы
            visualize_nodes(nodes, ax)
            plt.pause(0.01)  # Небольшая пауза, чтобы график успел обновиться

            # Ждем указанный интервал времени перед следующим обновлением
            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("Программа завершена.")
        plt.close()

if __name__ == "__main__":
    main()
