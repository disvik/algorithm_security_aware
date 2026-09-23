import random
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import time
import hashlib


# Класс для представления блока в блокчейне
class Block:
    def __init__(self, transactions, previous_hash):
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = None  # Используется для Proof of Work
        self.hash = None

    def calculate_hash(self):
        block_string = str(self.transactions) + str(self.previous_hash) + str(self.nonce)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        prefix = '0' * difficulty
        while True:
            self.nonce = random.randint(0, 1000000)
            self.hash = self.calculate_hash()
            if self.hash.startswith(prefix):
                break


# Класс для представления узла в сети блокчейна
class Node:
    def __init__(self, computational_power):
        self.computational_power = computational_power

    def mine_block(self, transactions, previous_hash, difficulty):
        block = Block(transactions, previous_hash)
        block.mine_block(difficulty)
        return block


# Создаем модель 10x10 сети узлов (графовая модель)
G = nx.grid_2d_graph(10, 10)


# Пример динамической кластеризации с использованием k-means и мощности узлов
def dynamic_clustering(G, n_clusters, computational_powers):
    # Создаем матрицу признаков узлов (координаты и мощность узлов в графе)
    nodes = list(G.nodes)
    features = [[node[0], node[1], computational_powers[node]] for node in nodes]

    # Выполняем кластеризацию с помощью k-means
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(features)

    # Возвращаем метки кластеров для каждого узла
    return kmeans.labels_


# Пример присоединения нового узла
def join_group(G, clusters, new_node):
    # Присоединяем новый узел к группе с наибольшим количеством узлов
    group_sizes = {cluster: 0 for cluster in set(clusters)}
    for node, cluster in clusters.items():
        group_sizes[cluster] += 1
    max_size = max(group_sizes.values())
    largest_groups = [cluster for cluster, size in group_sizes.items() if size == max_size]
    chosen_group = random.choice(largest_groups)
    clusters[new_node] = chosen_group


# Пример перехода узла в другую группу
def move_to_group(G, clusters, node, target_cluster_index, min_blocks_to_move):
    # Проверяем количество опубликованных блоков узла
    if node not in clusters:
        return False  # Узел не принадлежит ни одной группе
    blocks_published = random.randint(min_blocks_to_move, 2 * min_blocks_to_move)  # Пример: случайное количество опубликованных блоков
    if blocks_published >= min_blocks_to_move:
        clusters[node] = target_cluster_index
        return True
    else:
        return False


# Визуализация графа с кластеризацией
def plot_graph_with_clusters(G, clusters):
    pos = {(x, y): (y, -x) for x, y in G.nodes()}
    color_map = [-1] * len(G.nodes())  # Инициализация списка цветов
    for i in range(len(clusters)):
        if clusters[i] != -1:
            color_map[i] = clusters[i]  # Устанавливаем метку кластера для соответствующего узла
    nx.draw(G, pos, node_color=color_map, with_labels=True, cmap=plt.cm.tab10)
    plt.show()


# Симуляция работы системы блокчейна с дополнительными метриками
def blockchain_simulation(G, computational_powers, num_transactions, difficulty, mining_interval):
    # Инициализация
    clusters = dynamic_clustering(G, n_clusters, computational_powers)
    total_transactions_processed = 0
    total_time = 0
    total_energy_consumed = 0

    # Симуляция обработки транзакций
    start_time = time.time()
    for _ in range(num_transactions):
        sender = random.choice(list(G.nodes()))
        recipient = random.choice(list(G.nodes()))
        transactions = {"sender": sender, "recipient": recipient, "amount": random.randint(1, 100)}

        # Майнинг блока
        miner_node = random.choice(list(G.nodes()))
        miner = Node(computational_powers[miner_node])
        previous_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()  # Пример предыдущего хэша
        block = miner.mine_block(transactions, previous_hash, difficulty)

        # Обновление статистики
        total_transactions_processed += 1
        total_time += time.time() - start_time
        total_energy_consumed += computational_powers[miner_node]  # Предполагаем, что потребляемая энергия пропорциональна мощности узла

        # Проверяем, прошло ли время для майнинга нового блока
        if total_time >= mining_interval:
            break

    # Вычисляем дополнительные метрики
    transactions_per_second = total_transactions_processed / total_time
    average_transaction_time = total_time / total_transactions_processed
    throughput = total_transactions_processed / mining_interval
    transaction_latency = total_time / total_transactions_processed
    security_level = 1 / difficulty  # Простейшая оценка уровня безопасности, чем выше сложность, тем выше безопасность

    return {
        "total_transactions_processed": total_transactions_processed,
        "total_time": total_time,
        "transactions_per_second": transactions_per_second,
        "average_transaction_time": average_transaction_time,
        "throughput": throughput,
        "transaction_latency": transaction_latency,
        "total_energy_consumed": total_energy_consumed,
        "security_level": security_level
    }


def blockchain_simulation_with_clusters(G, clusters, num_transactions, difficulty, mining_interval):
    # Инициализация
    total_transactions_processed = 0
    total_time = 0
    total_energy_consumed = 0

    # Симуляция обработки транзакций
    start_time = time.time()
    for _ in range(num_transactions):
        sender = random.choice(list(G.nodes()))
        recipient = random.choice(list(G.nodes()))
        transactions = {"sender": sender, "recipient": recipient, "amount": random.randint(1, 100)}

        # Майнинг блока
        miner_node = random.choice(list(G.nodes()))
        miner = Node(computational_powers[miner_node])
        previous_hash = hashlib.sha256(str(random.random()).encode()).hexdigest()  # Пример предыдущего хэша
        block = miner.mine_block(transactions, previous_hash, difficulty)

        # Обновление статистики
        total_transactions_processed += 1
        total_time += time.time() - start_time
        total_energy_consumed += computational_powers[miner_node]  # Предполагаем, что потребляемая энергия пропорциональна мощности узла

        # Проверяем, прошло ли время для майнинга нового блока
        if total_time >= mining_interval:
            break

    # Вычисляем дополнительные метрики
    transactions_per_second = total_transactions_processed / total_time
    average_transaction_time = total_time / total_transactions_processed
    throughput = total_transactions_processed / mining_interval
    transaction_latency = total_time / total_transactions_processed
    security_level = 1 / difficulty  # Простейшая оценка уровня безопасности, чем выше сложность, тем выше безопасность

    return {
        "total_transactions_processed": total_transactions_processed,
        "total_time": total_time,
        "transactions_per_second": transactions_per_second,
        "average_transaction_time": average_transaction_time,
        "throughput": throughput,
        "transaction_latency": transaction_latency,
        "total_energy_consumed": total_energy_consumed,
        "security_level": security_level
    }


# Пример проведения экспериментов
if __name__ == "__main__":
    # Задаем параметры для симуляции
    n_clusters = 5
    num_transactions = 1000
    difficulty = 4
    mining_interval = 60  # Время для майнинга в секундах

    # Задаем вычислительную мощность узлов
    computational_powers = {(x, y): random.randint(1, 10) for x, y in G.nodes()}

    # Запускаем симуляцию с обычной работой Proof of Work
    results_pow = blockchain_simulation(G, computational_powers, num_transactions, difficulty, mining_interval)
    print("Proof of Work:")
    for metric, value in results_pow.items():
        print(f"{metric}: {value}")

    # Запускаем симуляцию с динамической кластеризацией
    clusters = dynamic_clustering(G, n_clusters, computational_powers)
    results_clustering = blockchain_simulation_with_clusters(G, clusters, num_transactions, difficulty, mining_interval)
    print("\nDynamic Clustering:")
    for metric, value in results_clustering.items():
        print(f"{metric}: {value}")

    # Визуализация графа с кластеризацией
    clusters = dynamic_clustering(G, n_clusters, computational_powers)
    plot_graph_with_clusters(G, clusters)