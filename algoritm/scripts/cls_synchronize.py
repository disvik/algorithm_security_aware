import time
import random
import networkx as nx
from cls_node import Node
from cls_network import Network

class Sync:
    def __init__(self, network):
        self.network = network

    def get_node_by_id(self, node_id):
        for node in self.network.nodes:
            if node.id == node_id:
                return node
        return None

    def synchronize(self, start_node, clusters=None):
        if self.network.clustered:
            return self.cluster_sync(start_node, clusters)
        else:
            return self.cascade_sync(start_node)


    def reset_sync_states(self):
        for node in self.network.nodes:
            node.sync_state = 0

    def cascade_sync(self, start_node):
        """
        Базовый каскадный алгоритм, имитация типичных каскадных методов синхронизации
        """
        start_time = time.time()  # Запоминаем время начала выполнения метода
        
        sync_queue = [start_node] # Очередь для узлов, ожидающих синхронизации

        synced_nodes_count = 1 # Переменная для подсчета числа синхронизированных узлов

        total_nodes = len(self.network.nodes)  # Общее число узлов в сети

        while sync_queue:
            # Извлечение узла из очереди
            current_node = sync_queue.pop(0)

            # Вывод информации о текущем узле и его связях
            print(f"Идентификатор узла: {current_node.id}, Состояние синхронизации: {'Синхронизирован' if current_node.sync_state == 1 else 'Не синхронизирован'}")
            print("Исходящие ребра:")
            for neighbor_id in current_node.graph.neighbors(current_node.id):
                neighbor_node = self.get_node_by_id(neighbor_id)
                if neighbor_node:
                    print(f"   Идентификатор соседнего узла: {neighbor_node.id}, Состояние синхронизации: {'Синхронизирован' if neighbor_node.sync_state == 1 else 'Не синхронизирован'}")
                else:
                    print(f"   Узел с идентификатором {neighbor_id} не найден в сети.")
            print()

            # Определение исходящих ребер текущего узла
            neighbors_list = list(current_node.graph.neighbors(current_node.id))

            # Синхронизация соседних узлов
            total_time_delay = 0  # Инициализация общего времени задержки
            for neighbor_id in neighbors_list:
                neighbor_node = self.get_node_by_id(neighbor_id)
                if neighbor_node and neighbor_node.sync_state == 0:
                    # Выполнение синхронизации с несинхронизированным соседним узлом
                    neighbor_node.sync_state = 1
                    # Добавление соседнего узла в очередь на синхронизацию
                    sync_queue.append(neighbor_node)
                    synced_nodes_count += 1  # Увеличиваем счетчик синхронизированных узлов
                    # Увеличение общего времени задержки на 0.3, если соседний узел не синхронизирован
                    total_time_delay += 0.05
                elif neighbor_node and neighbor_node.sync_state == 1:
                    # Увеличение общего времени задержки на 0.15, если соседний узел уже синхронизирован
                    total_time_delay += 0.025
            
            # Пауза после синхронизации с каждым соседним узлом, пропорционально общему времени задержки
            time.sleep(total_time_delay)
            print(f"Общее время задержки для всех: {total_time_delay:.3f} секунд")

        # Рассчитываем процент синхронизации
        sync_percentage = round(synced_nodes_count / total_nodes * 100, 1)
        print(f"***********************************************************************")
        print(f"Процент синхронизации: {sync_percentage}%")

        # Проверяем, что все узлы стали синхронизированными
        all_synced = all(node.sync_state == 1 for node in self.network.nodes)
        if not all_synced:
            print("Не все узлы синхронизированы!")
        else:
            print("Полная синхронизация узлов!")
        print(f"***********************************************************************")

        # После завершения синхронизации сбрасываем состояния синхронизации всех узлов
        self.reset_sync_states()

        end_time = time.time()  # Запоминаем время завершения выполнения метода
        elapsed_time = end_time - start_time  # Вычисляем общее время выполнения

        return elapsed_time  # Возвращаем общее время выполнения метода




    def cluster_sync(self, start_node, clusters):
        """
        Синхронизация кластеризированной сети.

        Скорость синхронизации расчитывается исходя из формы связи между узлами
        Все внутрикластерные связи - сокращенное время, а внекластерные - полное
        Если попытка синхронизации уже синхронизированных узлов(проверка) - время сокращается вдвое
        """
        start_time = time.time()  # Запоминаем время начала выполнения метода

        sync_queue = [start_node] # Очередь для узлов, ожидающих синхронизации

        synced_nodes_count = 1 # Переменная для подсчета числа синхронизированных узлов

        total_nodes = len(self.network.nodes)  # Общее число узлов в сети

        intra_cluster_edges = self.network.intra_cluster_edges # Доступ к двумерному списку объектов новых связей**

        print(f"***********************************************************************")
        print("Синхронизация кластеризированной сети")
        print(f"***********************************************************************")

        while sync_queue:
            # Извлечение узла из очереди
            current_node = sync_queue.pop(0)

            # Вывод информации о текущем узле и его связях
            print(f"Идентификатор узла: {current_node.id}, Состояние синхронизации: {'Синхронизирован' if current_node.sync_state == 1 else 'Не синхронизирован'}")
            print("Исходящие ребра:")
            for neighbor_id in current_node.graph.neighbors(current_node.id):
                neighbor_node = self.get_node_by_id(neighbor_id)
                if neighbor_node:
                    print(f"   Идентификатор соседнего узла: {neighbor_node.id}, Состояние синхронизации: {'Синхронизирован' if neighbor_node.sync_state == 1 else 'Не синхронизирован'}")
                else:
                    print(f"   Узел с идентификатором {neighbor_id} не найден в сети.")
            print()

            # Определение исходящих ребер текущего узла
            neighbors_list = list(current_node.graph.neighbors(current_node.id))

            # Синхронизация соседних узлов
            total_time_delay = 0  # Инициализация общего времени задержки
            for neighbor_id in neighbors_list:
                neighbor_node = self.get_node_by_id(neighbor_id)

                # Условие, является ли текущее ребро внутрикластерным
                is_intra_cluster_edge = any(current_node in cluster and neighbor_node in cluster for cluster in clusters)

                # Вычисление времени задержки для текущей связи
                if is_intra_cluster_edge:
                    delay_coefficient = 0.005 if neighbor_node.sync_state == 0 else 0.0025
                else:
                    delay_coefficient = 0.05 if neighbor_node.sync_state == 0 else 0.025

                print(f"Исходящее ребро является врунтрикластерным? {is_intra_cluster_edge}")
                # Учитываем время взаимодействия с соседним узлом
                total_time_delay += delay_coefficient

                if neighbor_node and neighbor_node.sync_state == 0:
                    # Выполнение синхронизации с соседним узлом
                    neighbor_node.sync_state = 1
                    sync_queue.append(neighbor_node)
                    synced_nodes_count += 1  # Увеличиваем счетчик синхронизированных узлов

            # Пауза перед следующим этапом синхронизации
            time.sleep(total_time_delay)
            print(f"Общее время задержки для всех: {total_time_delay:.3f} секунд")

        # Рассчитываем процент синхронизации
        sync_percentage = round(synced_nodes_count / total_nodes * 100, 1)
        print(f"***********************************************************************")
        print(f"Процент синхронизации: {sync_percentage}%")

        # Проверяем, что все узлы стали синхронизированными
        all_synced = all(node.sync_state == 1 for node in self.network.nodes)
        if not all_synced:
            print("Не все узлы синхронизированы!")
        else:
            print("Полная синхронизация узлов!")
        print(f"***********************************************************************")

        # После завершения синхронизации сбрасываем состояния синхронизации всех узлов
        self.reset_sync_states()

        # Печать после паузы
        print(f"***********************************************************************")
        print(f"Синхронизация кластеризированной сети завершена")
        print(f"***********************************************************************")

        end_time = time.time()  # Запоминаем время завершения выполнения метода
        elapsed_time = end_time - start_time  # Вычисляем общее время выполнения

        return elapsed_time  # Возвращаем общее время выполнения метода






