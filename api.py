from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import decode_access_token
from jwt.exceptions import InvalidTokenError

from auth import verify_password, create_access_token
from auth import hash_password
from models import UserDB
from sqlalchemy.exc import IntegrityError

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


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_access_token(credentials.credentials)
        username = payload.get("sub")

        if not isinstance(username, str) or not username:
            raise HTTPException(status_code=401, detail="Invalid token")

    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(UserDB).filter(UserDB.username == username).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user



class Transaction(BaseModel):
    type: str
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: str


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

@app.get("/")
def home():
    return {"message": "Welcome to Personal Finance Tracker"}




@app.get("/balance")
def get_balance(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).all()

    balance = Decimal("0.00")

    for transaction in transactions:
        if transaction.type == "Income":
            balance += transaction.amount
        else:
            balance -= transaction.amount

    return {"balance": float(balance)}



@app.get("/transactions")
def get_transactions(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).all()

    return transactions



@app.post("/transactions", status_code=201)
def add_transaction(
    transaction: Transaction,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if transaction.type not in ["Income", "Expense"]:
        raise HTTPException(
            status_code=400,
            detail="Type must be Income or Expense"
        )

    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).all()

    balance = Decimal("0.00")

    for item in transactions:
        if item.type == "Income":
            balance += item.amount
        else:
            balance -= item.amount

    amount = Decimal(str(transaction.amount))

    if transaction.type == "Expense" and amount > balance:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    new_transaction = TransactionDB(
        type=transaction.type,
        amount=amount,
        category=transaction.category,
        user_id=current_user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return {
        "message": "Transaction added successfully",
        "id": new_transaction.id
    }


@app.put("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: int,
    transaction: Transaction,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id,
        TransactionDB.user_id == current_user.id
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

    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).order_by(TransactionDB.id).all()

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
def delete_transaction(
    transaction_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id,
        TransactionDB.user_id == current_user.id
    ).first()

    if existing_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).order_by(TransactionDB.id).all()

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


@app.post("/register", status_code=201)
def register(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = UserDB(
        username=user.username,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "id": new_user.id
    }


@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user.username
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(existing_user.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/me")
def get_me(current_user: UserDB = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username
    }