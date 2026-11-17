import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

class Transaction(BaseModel):
    type: str
    amount: float = Field(gt=0, allow_inf_nan=False)
    category: str

@app.get("/")
def home():
    return {"message": "Welcome to Personal Finance Tracker"}


@app.get("/balance")
def get_balance():
    transactions = load_transactions()
    balance = 0

    for transaction in transactions:
        if transaction["type"] == "Income":
            balance += transaction["amount"]
        else:
            balance -= transaction["amount"]

    return {"balance": round(balance, 2)}


def load_transactions():
    try:
        with open("transactions.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_transactions(transactions):
    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=4)

@app.get("/transactions")
def get_transactions():
    transactions = load_transactions()
    return transactions


@app.post("/transactions", status_code=201)
def add_transaction(transaction: Transaction):
    transactions = load_transactions()

    if transaction.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense"
        )

    balance = 0

    for item in transactions:
        if item["type"] == "Income":
            balance += item["amount"]
        else:
            balance -= item["amount"]

    if transaction.type == "Expense" and transaction.amount > balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    transactions.append(transaction.model_dump())
    save_transactions(transactions)

    return {"message": "Transaction added successfully"}


@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction: Transaction):
    transactions = load_transactions()

    if transaction_id < 0 or transaction_id >= len(transactions):
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if transaction.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense"
        )

    updated_transactions = transactions.copy()
    updated_transactions[transaction_id] = transaction.model_dump()

    balance = 0

    for item in updated_transactions:
        if item["type"] == "Income":
            balance += item["amount"]
        else:
            balance -= item["amount"]

        if balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

    save_transactions(updated_transactions)

    return {"message": "Transaction updated successfully"}


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int):
    transactions = load_transactions()

    if transaction_id < 0 or transaction_id >= len(transactions):
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    updated_transactions = transactions.copy()
    deleted_transaction = updated_transactions.pop(transaction_id)

    balance = 0

    for transaction in updated_transactions:
        if transaction["type"] == "Income":
            balance += transaction["amount"]
        else:
            balance -= transaction["amount"]

        if balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Deleting this transaction would cause insufficient funds"
            )

    save_transactions(updated_transactions)

    return {
        "message": "Transaction deleted successfully",
        "deleted_transaction": deleted_transaction
    }

