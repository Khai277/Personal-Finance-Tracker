import json
import math

def save_transactions(transactions):
    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=4)

def load_transactions():
    try:
        with open("transactions.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []     

def main():
    balance = 0
    transactions = load_transactions()

    for transaction in transactions:
        if transaction["type"] == "Income":
            balance += transaction["amount"]
        else:
            balance -= transaction["amount"]

    while True:
        print("\n===== Personal Finance Tracker =====")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. View Balance")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            try:
                amount = float(input("Enter income amount: "))

                if not math.isfinite(amount) or amount <= 0:
                    print("Amount must be a positive number.")
                    continue

                category = input("Enter income category: ")

                balance += amount

                transaction = {
                    "type": "Income",
                    "amount": amount,
                    "category": category
                }

                transactions.append(transaction)
                save_transactions(transactions)
                print("Income added!")

            except ValueError:
                print("Invalid amount. Please enter a valid number.")

        elif choice == "2":
            try:
                amount = float(input("Enter expense amount: "))

                if not math.isfinite(amount) or amount <= 0:
                    print("Amount must be a positive number.")
                    continue

                if amount > balance:
                    print("Insufficient funds.")
                    continue

                category = input("Enter expense category: ")

                balance -= amount

                transaction = {
                    "type": "Expense",
                    "amount": amount,
                    "category": category
                }

                transactions.append(transaction)
                save_transactions(transactions)
                print("Expense added!")

            except ValueError:
                print("Please enter a valid number.")

        elif choice == "3":
            print("\n===== Transaction History =====")

            if len(transactions) == 0:
                print("No transactions found.")
            else:
                for transaction in transactions:
                    print(f"{transaction['type']} | ${transaction['amount']:.2f} | {transaction['category']}")

        elif choice == "4":
            print(f"Current Balance: ${balance:.2f}")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")


main()
