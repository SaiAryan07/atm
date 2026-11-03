"""ATM Simulation System - core Python only (json, os, datetime)."""

import json
import os
from datetime import datetime

DATA_FILE = "atm_data.json"
MAX_ATTEMPTS = 3
MIN_BALANCE = 0


def load_data():
    """Load account data from file, or create a default account."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    data = {"name": "Sai Aryan", "pin": "1234", "balance": 5000.0, "transactions": []}
    save_data(data)
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_transaction(data, kind, amount):
    data["transactions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": amount,
        "balance": data["balance"],
    })
    save_data(data)


def login(data):
    for attempt in range(1, MAX_ATTEMPTS + 1):
        pin = input("Enter 4-digit PIN: ").strip()
        if pin == data["pin"]:
            print(f"\nWelcome, {data['name']}!")
            return True
        print(f"Wrong PIN. Attempts left: {MAX_ATTEMPTS - attempt}")
    print("Card blocked. Too many wrong attempts.")
    return False


def get_amount(prompt):
    try:
        amount = float(input(prompt))
    except ValueError:
        print("Invalid amount. Enter a number.")
        return None
    if amount <= 0:
        print("Amount must be greater than zero.")
        return None
    return amount


def check_balance(data):
    print(f"Current balance: Rs. {data['balance']:.2f}")


def deposit(data):
    amount = get_amount("Enter amount to deposit: ")
    if amount is None:
        return
    data["balance"] += amount
    add_transaction(data, "Deposit", amount)
    print(f"Rs. {amount:.2f} deposited. New balance: Rs. {data['balance']:.2f}")


def withdraw(data):
    amount = get_amount("Enter amount to withdraw: ")
    if amount is None:
        return
    if amount % 100 != 0:
        print("Please enter an amount in multiples of 100.")
    elif amount > data["balance"] - MIN_BALANCE:
        print("Insufficient balance.")
    else:
        data["balance"] -= amount
        add_transaction(data, "Withdraw", amount)
        print(f"Please collect Rs. {amount:.2f}. New balance: Rs. {data['balance']:.2f}")


def mini_statement(data):
    last = data["transactions"][-5:]
    if not last:
        print("No transactions yet.")
        return
    print("\n--- Mini Statement (last 5) ---")
    print(f"{'Date/Time':<20}{'Type':<10}{'Amount':>10}{'Balance':>12}")
    for t in reversed(last):
        print(f"{t['time']:<20}{t['type']:<10}{t['amount']:>10.2f}{t['balance']:>12.2f}")


def main():
    data = load_data()
    print("=== Welcome to Python ATM ===")
    if not login(data):
        return

    while True:
        print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. Mini Statement\n5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            check_balance(data)
        elif choice == "2":
            deposit(data)
        elif choice == "3":
            withdraw(data)
        elif choice == "4":
            mini_statement(data)
        elif choice == "5":
            print("Thank you for using the ATM. Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
