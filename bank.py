"""Banking logic (no screen code). Uses csv, os, random, datetime only."""

import csv
import os
import random
from datetime import datetime

USERS_FILE = "users.csv"
TRANSACTIONS_FILE = "transactions.csv"
MAX_ATTEMPTS = 3


# ---------- File handling ----------
def load_users():
    users = {}
    if not os.path.exists(USERS_FILE):
        return users
    with open(USERS_FILE, "r", newline="") as f:
        for row in csv.DictReader(f):
            users[row["account_no"]] = {
                "name": row["name"],
                "pin": row["pin"],
                "balance": float(row["balance"]),
                "blocked": row["blocked"].strip().lower() == "true",
                "transactions": [],
            }
    if os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, "r", newline="") as f:
            for row in csv.DictReader(f):
                if row["account_no"] in users:
                    users[row["account_no"]]["transactions"].append({
                        "time": row["time"],
                        "type": row["type"],
                        "amount": float(row["amount"]),
                        "balance": float(row["balance"]),
                    })
    return users


def save_users(users):
    with open(USERS_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account_no", "name", "pin", "balance", "blocked"])
        for acc, u in users.items():
            w.writerow([acc, u["name"], u["pin"], u["balance"], u["blocked"]])
    with open(TRANSACTIONS_FILE, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["account_no", "time", "type", "amount", "balance"])
        for acc, u in users.items():
            for t in u["transactions"]:
                w.writerow([acc, t["time"], t["type"], t["amount"], t["balance"]])


# ---------- Helpers ----------
def add_transaction(users, user, kind, amount):
    user["transactions"].append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": kind,
        "amount": amount,
        "balance": user["balance"],
    })
    save_users(users)


def generate_account_number(users):
    while True:
        acc_no = str(random.randint(1000000000, 9999999999))
        if acc_no not in users:
            return acc_no


def valid_pin(pin):
    return pin.isdigit() and len(pin) == 4


# ---------- Operations (each returns (success, message)) ----------
def login(users, acc_no, pin, failed_attempts):
    """Returns (success, message, blocked_now)."""
    if acc_no not in users:
        return False, "Account not found.", False
    user = users[acc_no]
    if user["blocked"]:
        return False, "This account is blocked. Contact the bank.", False
    if pin == user["pin"]:
        return True, f"Welcome, {user['name']}!", False
    left = MAX_ATTEMPTS - failed_attempts - 1
    if left <= 0:
        user["blocked"] = True
        save_users(users)
        return False, "Too many wrong attempts. Account blocked.", True
    return False, f"Wrong PIN. Attempts left: {left}", False


def create_account(users, name, pin, opening):
    if not name.strip():
        return False, "Name cannot be empty."
    if not valid_pin(pin):
        return False, "PIN must be exactly 4 digits."
    if opening <= 0:
        return False, "Opening deposit must be greater than zero."
    acc_no = generate_account_number(users)
    users[acc_no] = {"name": name.strip(), "pin": pin, "balance": float(opening),
                     "blocked": False, "transactions": []}
    add_transaction(users, users[acc_no], "Deposit", float(opening))
    return True, acc_no


def deposit(users, user, amount):
    if amount <= 0:
        return False, "Amount must be greater than zero."
    user["balance"] += amount
    add_transaction(users, user, "Deposit", amount)
    return True, f"Rs. {amount:.2f} deposited. New balance: Rs. {user['balance']:.2f}"


def withdraw(users, user, amount):
    if amount <= 0:
        return False, "Amount must be greater than zero."
    if amount % 100 != 0:
        return False, "Please enter an amount in multiples of 100."
    if amount > user["balance"]:
        return False, "Insufficient balance."
    user["balance"] -= amount
    add_transaction(users, user, "Withdraw", amount)
    return True, f"Please collect Rs. {amount:.2f}. New balance: Rs. {user['balance']:.2f}"


def change_pin(users, user, current_pin, new_pin):
    if current_pin != user["pin"]:
        return False, "Current PIN is wrong."
    if not valid_pin(new_pin):
        return False, "New PIN must be exactly 4 digits."
    user["pin"] = new_pin
    save_users(users)
    return True, "PIN changed successfully."


def delete_account(users, acc_no, pin):
    if pin != users[acc_no]["pin"]:
        return False, "Wrong PIN. Account not deleted."
    del users[acc_no]
    save_users(users)
    return True, f"Account {acc_no} deleted."
