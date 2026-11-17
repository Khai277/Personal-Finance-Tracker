from decimal import Decimal
from fastapi import Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import TransactionDB


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

class Transaction(BaseModel):
    type: str
    amount: float = Field(gt=0, allow_inf_nan=False)
    category: str

@app.get("/")
def home():
    return {"message": "Welcome to Personal Finance Tracker"}


@app.get("/balance")
def get_balance(db: Session = Depends(get_db)):
    transactions = db.query(TransactionDB).all()
    balance = Decimal("0.00")

    for transaction in transactions:
        if transaction.type == "Income":
            balance += transaction.amount
        else:
            balance -= transaction.amount

    return {"balance": float(balance)}


@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(TransactionDB).all()

    return transactions


@app.post("/transactions", status_code=201)
def add_transaction(transaction: Transaction, db: Session = Depends(get_db)):

    if transaction.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense"
        )

    transactions = db.query(TransactionDB).all()

    balance = Decimal("0.00")

    for item in transactions:
        if item.type == "Income":
            balance += item.amount
        else:
            balance -= item.amount

    if transaction.type == "Expense" and Decimal(str(transaction.amount)) > balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    new_transaction = TransactionDB(
        type=transaction.type,
        amount=Decimal(str(transaction.amount)),
        category=transaction.category
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        "message": "Transaction added successfully",
        "id": new_transaction.id
    }


@app.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, transaction: Transaction, db: Session = Depends(get_db)):
    existing_transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id
    ).first()

    if existing_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    if transaction.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense"
        )

    transactions = db.query(TransactionDB).order_by(TransactionDB.id).all()
    balance = Decimal("0.00")

    for item in transactions:
        if item.id == transaction_id:
            item_type = transaction.type
            item_amount = Decimal(str(transaction.amount))
        else:
            item_type = item.type
            item_amount = item.amount

        if item_type == "Income":
            balance += item_amount
        else:
            balance -= item_amount

        if balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

    existing_transaction.type = transaction.type
    existing_transaction.amount = Decimal(str(transaction.amount))
    existing_transaction.category = transaction.category

    db.commit()

    return {"message": "Transaction updated successfully"}


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    existing_transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id
    ).first()

    if existing_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transactions = db.query(TransactionDB).order_by(TransactionDB.id).all()
    balance = Decimal("0.00")

    for transaction in transactions:
        if transaction.id == transaction_id:
            continue

        if transaction.type == "Income":
            balance += transaction.amount
        else:
            balance -= transaction.amount

        if balance < 0:
            raise HTTPException(
                status_code=400,
                detail="Deleting this transaction would cause insufficient funds"
            )

    db.delete(existing_transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}

   


