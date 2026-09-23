import random
import string

def generate_random_name():
    return random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase)

def generate_random_transaction():
    sender = generate_random_name()  # Генерируем случайное имя отправителя
    recipient = generate_random_name()  # Генерируем случайное имя получателя
    amount = random.randint(1, 100)  # Генерируем случайную сумму перевода от 1 до 100
    return f"{sender} {recipient} {amount}"

def generate_transactions_random_count():
    transactions_count = random.randint(10, 20)  # Генерируем случайное количество транзакций от 10 до 20
    transactions = [generate_random_transaction() for _ in range(transactions_count)]
    return transactions

def generate_transaction_manual():
    while True:
        sender = input("Введите имя отправителя (две буквы английского алфавита нижней раскладки): ")
        if len(sender) != 2 or not sender.isalpha() or not sender.islower() or not all(char in 'abcdefghijklmnopqrstuvwxyz' for char in sender):
            print("Ошибка: имя отправителя должно состоять из двух малых букв английского алфавита")
        else:
            break
    while True:
        recipient = input("Введите имя получателя (две буквы английского алфавита нижней раскладки): ")
        if len(recipient) != 2 or not recipient.isalpha() or not recipient.islower() or not all(char in 'abcdefghijklmnopqrstuvwxyz' for char in recipient):
            print("Ошибка: имя получателя должно состоять из двух малых букв английского алфавита")
        else:
            break  
    amount = int(input("Введите сумму перевода (целое число от 1 до 100): "))
    if amount < 1 or amount > 100:
        print("Ошибка: сумма перевода должна быть целым числом от 1 до 100")
        return None    
    return f"{sender} {recipient} {amount}"




def clear_transaction_pool():
    with open("data/transaction_pool.txt", "w") as file:
        file.write("")  # Очищаем файл

def main():
    print("Выберите тип генерации транзакций:")
    print("1. Случайное количество транзакций от 10 до 20")
    print("2. Ввод количества транзакций")
    print("3. Ручной ввод транзакции")
    print("4. Очистить базу данных пула транзакций")

    choice = input("Введите номер выбранного пункта: ")

    if choice == "1":
        transactions = generate_transactions_random_count()
    elif choice == "2":
        count = int(input("Введите количество транзакций (от 1 до 100): "))
        if count < 1 or count > 100:
            print("Ошибка: количество транзакций должно быть целым числом от 1 до 100")
            return
        transactions = [generate_random_transaction() for _ in range(count)]
    elif choice == "3":
        transaction = generate_transaction_manual()
        if transaction is None:
            return
        transactions = [transaction]
    elif choice == "4":
        clear_transaction_pool()
        print("База данных пула транзакций очищена")
        return
    else:
        print("Ошибка: неверный выбор")
        return

    with open("data/transaction_pool.txt", "a") as file:
        for transaction in transactions:
            file.write(transaction + "\n")

    print("Транзакции успешно добавлены в базу данных пула транзакций")

if __name__ == "__main__":
    main()
