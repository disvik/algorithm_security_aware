import hashlib
import time
import pickle
import multiprocessing

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from cls_node import Node
from cls_network import Network
from cls_synchronize import Sync


# Глобальная переменная для хранения ссылки на текущий процесс визуализации
current_vis_process = None


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        """
        Создает новый блок.
        
        :param index: Индекс блока в цепочке.
        :param transactions: Список транзакций в блоке.
        :param timestamp: Временная метка блока.
        :param previous_hash: Хэш предыдущего блока.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Вычисляет хэш блока.
        
        :return: Хэш блока.
        """
        sha = hashlib.sha256()
        transactions_str = ''.join(self.transactions)
        data = str(self.index) + transactions_str + str(self.timestamp) + str(self.previous_hash) + str(self.nonce)
        sha.update(data.encode('utf-8'))
        return sha.hexdigest()
    

    def mine_block(self, difficulty):
        """
        Майнит блок с учетом уровня сложности.
        
        :param difficulty: Уровень сложности.
        """
        start_time = time.time()  # Запоминаем текущее время начала майнинга
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        end_time = time.time()  # Запоминаем текущее время окончания майнинга
        mining_time = end_time - start_time  # Вычисляем время майнинга
        print(f"Block {self.index} mined in {round(mining_time, 3)} seconds: {self.hash}")

    def __str__(self):
        """
        Возвращает строковое представление блока.
        
        :return: Строковое представление блока.
        """
        return f"Block {self.index} [Timestamp: {self.timestamp}, Hash: {self.hash}, Previous Hash: {self.previous_hash}]"



class Blockchain:
    def __init__(self):
        """
        Создает новую цепочку блоков.
        """
        self.chain = self.load_blockchain()  # Загрузка цепочки блоков из файла
        self.difficulty = 5  # Уровень сложности PoW(количество нулей хэша для замедления добычи)
        self.transaction_pool = []  # Пул транзакций

    def create_genesis_block(self):
        """
        Создает генезис-блок, первый блок в цепочке.
        
        :return: Генезис-блок.
        """
        # Задаем фиксированное время для генезис-блока (например, 0)
        return Block(0, [], 0, "0")

    def save_blockchain(self):
        """
        Сохраняет текущую цепочку блоков в файл.
        """
        with open("blockchain/blockchain.pkl", "wb") as file:
            pickle.dump(self.chain, file)

    def load_blockchain(self):
        """
        Загружает цепочку блоков из файла, если он существует.
        Если файл не существует, возвращает новую цепочку блоков.
        """
        try:
            with open("blockchain/blockchain.pkl", "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return [self.create_genesis_block()]

    def get_latest_block(self):
        """
        Получает последний блок в цепочке.
        
        :return: Последний блок в цепочке.
        """
        return self.chain[-1]

    def add_transaction(self, transaction):
        """
        Добавляет транзакцию в пул транзакций.
        
        :param transaction: Транзакция для добавления.
        """
        self.transaction_pool.append(transaction)

    def read_transactions_from_file(self, file_path):
        """
        Читает транзакции из файла и добавляет их в пул транзакций.
        
        :param file_path: Путь к файлу с транзакциями.
        """
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    self.add_transaction(line.strip())
            #self.transaction_pool.sort()
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")

    def mine_blocks_from_transaction_pool(self, block_size=3, network=None, clusters=None):
        """
        Майнит блоки из пула транзакций.
        
        :param block_size: Размер блока.
        """
        while len(self.transaction_pool) >= block_size:

            # Динамический визуализатор
            if network is not None:
                if clusters is not None:
                    # Если есть сеть и кластеры, визуализируем сеть с кластеризацией
                    visualize_in_another_process(visualize_cluster_network, network, clusters)
                else:
                    # Если есть только сеть, визуализируем простую сеть
                    visualize_in_another_process(visualize_simple_network, network)

            total_time = 30  # Общее время между майнингом блоков
            start_time = time.time()  # Засекаем время начала майнинга
            index = len(self.chain)
            timestamp = self.chain[-1].timestamp if self.chain else 0
            transactions = self.transaction_pool[:block_size]
            new_block = Block(index, transactions, timestamp, self.get_latest_block().hash)
            new_block.mine_block(self.difficulty)
            if network:
                # Выбираем узел для майнинга из сети
                chosen_node = network.choose_node_for_mining()
                # Присваиваем результат майнинга узлу для синхронизации
                chosen_node.sync_state = 1
                # Выводим айди узла, который был выбран для майнинга и синх
                print(f"Mined by node with ID: {chosen_node.id} Status node: {'Sync' if chosen_node.sync_state == 1 else 'Not Sync'}")
                sync_instance = Sync(network)
                elapsed_time = sync_instance.synchronize(chosen_node, clusters)
                print(f"Synchronize of network was complete by:", elapsed_time, "sec")
                print(f"-----------------------------------------------------------------------")

            self.chain.append(new_block)
            self.transaction_pool = self.transaction_pool[block_size:]
            
            # Обновляем файл пула транзакций
            with open("data/transaction_pool.txt", 'w') as file:
                for transaction in self.transaction_pool:
                    file.write(transaction + '\n')

            # Обновляем файл архива транзакций после майнинга нового блока
            self.update_transactions_file("data/transaction_archive.txt")

            # Сохраняем цепочку блоков в файл после добавления нового блока
            self.save_blockchain()

            end_time = time.time()  # Засекаем время окончания майнинга и синхронизации
            mining_sync_time = end_time - start_time  # Вычисляем общее время майнинга и синхронизации
            print(f"Mining and synchronization time took only:", mining_sync_time, "sec")
            print(f"-----------------------------------------------------------------------")
            time.sleep(3)  # Пауза в 3с
            print(f"Переконфигурация сети..")
            network.update_edges()
            print(f"-----------------------------------------------------------------------")
            # Если время майнинга блока меньше 60 секунд, добавляем паузу на оставшееся время
            if mining_sync_time < total_time:
                time.sleep(total_time - mining_sync_time)
            rest_time = total_time - mining_sync_time  # Вычисляем время отдыха
            print(f"Rest of time: ", rest_time, "sec")
            print(f"-----------------------------------------------------------------------")
            print(f"-----------------------------------------------------------------------")


            # После майнинга блока обновляем внутрикластерные связи
            if clusters:
                network.add_intra_cluster_links(clusters)


    def update_transactions_file(self, file_path):
        """
        Обновляет файл транзакций после майнинга нового блока.

        :param file_path: Путь к файлу с архивом транзакций.
        """
        with open(file_path, 'a') as file:
            for block in self.chain[-1:]:
                for transaction in block.transactions:
                    file.write(transaction + '\n')

    def clear_and_update_transaction_pool(self, file_path, num_transactions):
        """
        Очищает пул транзакций и обновляет файл пула транзакций.
        
        :param file_path: Путь к файлу пула транзакций.
        :param num_transactions: Количество транзакций для удаления из пула.
        """
        # Удаляем первые num_transactions транзакций из пула
        transactions_to_remove = self.transaction_pool[:num_transactions]
        self.transaction_pool = self.transaction_pool[num_transactions:]
        # Обновляем файл пула транзакций
        with open(file_path, 'w') as file:
            for transaction in transactions_to_remove:
                file.write(transaction + '\n')  
          

    def is_chain_valid(self):
        """
        Проверяет валидность цепочки блоков.
        
        :return: True, если цепочка валидна, иначе False.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True


    def __str__(self):
        """
        Возвращает строковое представление цепочки блоков.
        
        :return: Строковое представление цепочки блоков.
        """
        chain_str = ""
        for block in self.chain:
            chain_str += str(block) + "\n"
        return chain_str

def visualize_simple_network(network):
    """
    Визуализирует простую сеть без кластеров.

    :param network: Объект класса Network, представляющий собой сеть без кластеров.
    """
    # Создаем граф
    graph = nx.Graph()

    # Добавляем узлы в граф с соответствующими размерами
    for node in network.nodes:
        graph.add_node(node.id, pos=node.topology, size=node.power*300, alpha=node.connectivity)

    # Добавляем ребра между узлами
    for node in network.nodes:
        for neighbor_id in node.graph.adj[node.id]:
            graph.add_edge(node.id, neighbor_id, color="grey", alpha=0.2)

    # Получаем размеры узлов
    sizes = [node[1]['size']  for node in graph.nodes(data=True)]

    # Получаем цвета ребер
    edge_colors = [graph[u][v]['color'] for u, v in graph.edges()]

    # Получаем прозрачность узлов на основе свойства связности (connectivity)
    node_alphas = [node.connectivity for node in network.nodes]

    # Рисуем граф с установленными размерами узлов
    pos = nx.get_node_attributes(graph, 'pos')  # Получаем координаты узлов
    nx.draw(graph, pos, with_labels=True, node_size=sizes, font_size=6, node_color='g', edge_color=edge_colors, alpha=0.8)
    plt.show()

def visualize_cluster_network(network, clusters):
    """
    Визуализирует внутрикластерные связи каждого кластера на одном полотне, учитывая топологию узлов.

    :param network: Объект класса Network, представляющий собой сеть с разбиением на кластеры и внутрикластерными связями.
    :param clusters: Список кластеров. Каждый кластер представляет собой список узлов.
    """
    # Получаем список внутрикластерных связей из сети
    intra_cluster_edges = network.intra_cluster_edges

    # Создаем граф для всех кластеров
    graph = nx.Graph()

    # Добавляем узлы всех кластеров в граф с соответствующими цветами, размерами и координатами
    for i, cluster in enumerate(clusters):
        # Присваиваем цвет текущему кластеру
        color = plt.cm.tab10(i % 20)  # Используем % 20, чтобы не выйти за пределы цветовой карты
        
        # Добавляем узлы кластера в граф с соответствующим цветом, размером и координатами
        for node in cluster:
            # Используем координаты топологии узла
            graph.add_node(node.id, color=color, pos=node.topology, size=node.power*300)

            # Добавляем все ребра из узла
            for neighbor_id in node.graph.adj[node.id]:
                graph.add_edge(node.id, neighbor_id, color="grey", width=0.2)  # Тонкие серые ребра

        # Добавляем внутрикластерные связи в граф с соответствующими цветами
        for edge in network.intra_cluster_edges[i]:
            # Добавляем ребро с цветом кластера
            graph.add_edge(edge[0], edge[1], color=color)

    # Получаем размеры узлов
    sizes = [node[1]['size']  for node in graph.nodes(data=True)]

    # Получаем цвета ребер
    edge_colors = [graph[u][v]['color'] for u, v in graph.edges()]

    # Рисуем граф с установленными размерами узлов
    pos = nx.get_node_attributes(graph, 'pos')  # Получаем координаты узлов
    nx.draw(graph, pos, with_labels=True, node_color=[node[1]['color'] for node in graph.nodes(data=True)], edge_color=edge_colors, node_size=sizes, font_size=6, font_weight='bold')
    plt.show()


def visualize_in_another_process(visualization_function, *args):
    global current_vis_process
    # Завершаем предыдущий процесс визуализации, если он был
    if current_vis_process is not None and current_vis_process.is_alive():
        current_vis_process.terminate()
    # Создаем параллельный процесс для выполнения визуализации
    vis_process = multiprocessing.Process(target=visualization_function, args=args)
    vis_process.start()
    # Обновляем текущий процесс визуализации
    current_vis_process = vis_process


# Пример использования
if __name__ == "__main__":
    # Создаем экземпляр блокчейна
    my_blockchain = Blockchain()

    # Читаем транзакции из файла
    my_blockchain.read_transactions_from_file("data/transaction_pool.txt")

    # Добываем блоки из пула транзакций
    my_blockchain.mine_blocks_from_transaction_pool()

    # Выводим содержимое блокчейна после добавления новых блоков
    print(my_blockchain)
