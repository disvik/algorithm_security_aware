import random
import time
import matplotlib.pyplot as plt
from cls_node import Node
from structure import Network

def visualize_network(network, alpha, fig, ax):
    """
    Визуализирует граф сети.

    :param network: Объект сети для визуализации.
    :param alpha: Список значений прозрачности для каждого узла.
    :param fig: Объект графического окна.
    :param ax: Объект осей для построения графика.
    """
    # Очищаем предыдущие данные на графике
    ax.clear()

    # Получаем координаты X и Y для каждого узла
    x = [node.topology[0] for node in network.nodes]
    y = [node.topology[1] for node in network.nodes]

    # Получаем размеры точек на основе их мощности
    sizes = [node.power * 100 for node in network.nodes]

    # Визуализируем узлы с обновленной прозрачностью на основе связности
    ax.scatter(x, y, s=sizes, alpha=alpha, cmap='viridis')

    # Визуализируем связи между узлами
    for node in network.nodes:
        for neighbor_id in node.graph.neighbors(node.id):
            neighbor = next((n for n in network.nodes if n.id == neighbor_id), None)
            if neighbor:
                ax.plot([node.topology[0], neighbor.topology[0]], [node.topology[1], neighbor.topology[1]], color='gray', alpha=0.5, zorder=0)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Network Visualization')
    ax.grid(True)

    # Обновляем график
    plt.pause(0.01)  # Создаем паузу для обновления графика

def update_dynamic_properties(nodes):
    """
    Обновляет динамические свойства узлов.

    :param nodes: Список узлов для обновления.
    :return: Список значений прозрачности для каждого узла.
    """
    alpha = []
    for node in nodes:
        # Изменяем связность узла
        node.update_connectivity()
        # Добавляем значение прозрачности в список
        alpha.append(node.connectivity)
    return alpha

if __name__ == "__main__":
    # Создаем графическое окно перед началом цикла
    fig, ax = plt.subplots(figsize=(14, 8))

    network = Network()
    network.create_network(100)
    network.print_nodes_info(network.nodes)
    alpha = [node.connectivity for node in network.nodes]

    try:
        while True:
            # Обновляем связи в сети
            network.update_edges()
            # Обновляем динамические свойства узлов каждую секунду
            alpha = update_dynamic_properties(network.nodes)
            # Перерисовываем сеть с обновленными свойствами и прозрачностью
            visualize_network(network, alpha, fig, ax)
            # Ждем 1 секунду перед следующим обновлением
            time.sleep(1)

    except KeyboardInterrupt:
        print("Программа завершена.")
