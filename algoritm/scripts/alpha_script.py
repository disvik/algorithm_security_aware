import hashlib
import time
import random
import pickle
import multiprocessing
import threading

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation

from cls_node import Node
from cls_network import Network
from mine_blockchain import Block
from mine_blockchain import Blockchain
from cls_synchronize import Sync
from crypto_state import CryptoPolicy


# Глобальная переменная для хранения ссылки на текущий процесс визуализации
current_vis_process = None


def print_crypto_distribution(network):
    """Выводит распределение криптографических состояний узлов."""
    counts = {
        "VALID": 0,
        "TRANSITIONAL": 0,
        "NON_COMPLIANT": 0,
        "UNKNOWN": 0
    }

    for node in network.nodes:
        counts[node.crypto_state] = counts.get(node.crypto_state, 0) + 1

    print("\nРаспределение криптографических состояний:")
    for state, count in counts.items():
        print(f"{state}: {count}")


def print_security_clusters(clusters):
    """Выводит состав кластеров и crypto state узлов."""
    print("\nSecurity-Aware Clusters:")

    for index, cluster in enumerate(clusters, start=1):
        state_counts = {
            "VALID": 0,
            "TRANSITIONAL": 0,
            "NON_COMPLIANT": 0
        }

        for node in cluster:
            state_counts[node.crypto_state] = (
                state_counts.get(node.crypto_state, 0) + 1
            )

        print(
            f"Cluster {index}: "
            f"nodes={len(cluster)}, "
            f"VALID={state_counts['VALID']}, "
            f"TRANSITIONAL={state_counts['TRANSITIONAL']}, "
            f"NON_COMPLIANT={state_counts['NON_COMPLIANT']}"
        )


if __name__ == "__main__":
    # Создаем экземпляр блокчейна
    my_blockchain = Blockchain()
    my_blockchain.read_transactions_from_file("data/transaction_pool.txt")

    # Создание сетей
    network_first = Network()
    network_second = Network()
    network_security = Network()

    print("***********************************************************************")
    print("Выберите тип сети, на основании которой происходит расчет")
    print("1 — Простая каскадная сеть")
    print("2 — Динамическая кластеризация")
    print("3 — Security-Aware Dynamic Clustering")
    print("***********************************************************************")

    choice = input("Ваш выбор (1/2/3): ")

    if choice == "1":
        print("Вы выбрали первую опцию (Каскад).")
        nodes = None
        while nodes is None or nodes < 3 or nodes > 300:
            try:
                nodes = int(input("Укажите размерность базовой сети (от 3 до 300): "))
            except ValueError:
                print("Некорректный ввод. Пожалуйста, введите целое число.")

        network_first.create_network(nodes)
        print("***********************************************************************")
        my_blockchain.mine_blocks_from_transaction_pool(network=network_first)

    elif choice == "2":
        print("Вы выбрали вторую опцию (Динамическая кластеризация).")
        nodes = None
        while nodes is None or nodes < 3 or nodes > 300:
            try:
                nodes = int(input("Укажите размерность сети (от 3 до 300): "))
            except ValueError:
                print("Некорректный ввод. Пожалуйста, введите целое число.")

        network_second.create_network(nodes)
        print("***********************************************************************")

        clusters = network_second.split_into_clusters()
        my_blockchain.mine_blocks_from_transaction_pool(
            network=network_second,
            clusters=clusters
        )

    elif choice == "3":
        print("Вы выбрали третью опцию (Security-Aware Dynamic Clustering).")

        nodes = None
        while nodes is None or nodes < 3 or nodes > 300:
            try:
                nodes = int(input("Укажите размерность сети (от 3 до 300): "))
            except ValueError:
                print("Некорректный ввод. Пожалуйста, введите целое число.")

        # ----------------------------------------------------------
        # 1. Создаем обычную сеть с теми же характеристиками,
        #    что и в первой/второй модели.
        # ----------------------------------------------------------
        network_security.create_network(nodes)

        # ----------------------------------------------------------
        # 2. Создаем криптографическую политику сети.
        # ----------------------------------------------------------
        crypto_policy = CryptoPolicy(
            required_algorithm="AES-256",
            minimum_security_level=3,
            policy_version=2
        )

        # ----------------------------------------------------------
        # 3. Задаем контролируемое распределение crypto states.
        #
        # 70% VALID
        # 20% TRANSITIONAL
        # 10% NON_COMPLIANT
        # ----------------------------------------------------------
        network_security.assign_crypto_states(
            valid_ratio=0.7,
            transitional_ratio=0.2,
            non_compliant_ratio=0.1
        )

        # ----------------------------------------------------------
        # 4. Оцениваем crypto state относительно политики.
        # ----------------------------------------------------------
        network_security.evaluate_crypto_states(crypto_policy)
        print_crypto_distribution(network_security)

        # ----------------------------------------------------------
        # 5. Выполняем Security-Aware Dynamic Clustering.
        # ----------------------------------------------------------
        clusters = network_security.split_into_security_aware_clusters(
            crypto_policy
        )

        print_security_clusters(clusters)

        # ----------------------------------------------------------
        # 6. Пока консенсус и выбор майнера НЕ изменяются.
        # Это принципиально: второй пункт исследует именно
        # влияние crypto state на кластеризацию.
        # ----------------------------------------------------------
        my_blockchain.mine_blocks_from_transaction_pool(
            network=network_security,
            clusters=clusters
        )

    else:
        print("Выбрано неверное значение. Пожалуйста, выберите 1, 2 или 3.")

    print("Пул данных по транзакциям опустошен")
