
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import app, get_db
from models import Base, TransactionDB, UserDB

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://localhost:5432/finance_tracker_test"
)

test_engine = create_engine(TEST_DATABASE_URL)

assert test_engine.url.database == "finance_tracker_test"
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_test_database():
    assert test_engine.url.database == "finance_tracker_test"

    db = TestingSessionLocal()
    try:
        db.query(TransactionDB).delete()
        db.query(UserDB).delete()
        db.commit()
    finally:
        db.close()

    yield

    db = TestingSessionLocal()
    try:
        db.query(TransactionDB).delete()
        db.query(UserDB).delete()
        db.commit()
    finally:
        db.close()


def create_user(username):
    response = client.post("/register", json={
        "username": username,
        "password": "TestPassword123!"
    })
    assert response.status_code == 201

    response = client.post("/login", json={
        "username": username,
        "password": "TestPassword123!"
    })
    assert response.status_code == 200

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_registration_and_login():
    headers = create_user("alice")

    response = client.get("/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_wrong_password():
    create_user("alice")

    response = client.post("/login", json={
        "username": "alice",
        "password": "WrongPassword123!"
    })

    assert response.status_code == 401


def test_unauthorized_transactions():
    assert client.get("/transactions").status_code == 401
    assert client.get("/balance").status_code == 401

    assert client.post("/transactions", json={
        "type": "Income",
        "amount": 100,
        "category": "Salary"
    }).status_code == 401

    assert client.put("/transactions/1", json={
        "type": "Income",
        "amount": 100,
        "category": "Salary"
    }).status_code == 401

    assert client.delete("/transactions/1").status_code == 401


def test_create_and_read_transaction():
    headers = create_user("alice")

    response = client.post("/transactions", headers=headers, json={
        "type": "Income",
        "amount": 500,
        "category": "Paycheck"
    })

    assert response.status_code == 201

    transactions = client.get(
        "/transactions", headers=headers
    ).json()

    assert len(transactions) == 1
    assert transactions[0]["amount"] == 500

    balance = client.get("/balance", headers=headers)
    assert balance.json()["balance"] == 500


def test_update_transaction():
    headers = create_user("alice")

    created = client.post("/transactions", headers=headers, json={
        "type": "Income",
        "amount": 500,
        "category": "Paycheck"
    })

    transaction_id = created.json()["id"]

    response = client.put(
        f"/transactions/{transaction_id}",
        headers=headers,
        json={
            "type": "Income",
            "amount": 750,
            "category": "Salary"
        }
    )

    assert response.status_code == 200

    balance = client.get("/balance", headers=headers)
    assert balance.json()["balance"] == 750


def test_delete_transaction():
    headers = create_user("alice")

    created = client.post("/transactions", headers=headers, json={
        "type": "Income",
        "amount": 500,
        "category": "Paycheck"
    })

    transaction_id = created.json()["id"]

    response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 200

    transactions = client.get(
        "/transactions", headers=headers
    ).json()

    assert transactions == []


def test_user_isolation():
    alice = create_user("alice")
    bob = create_user("bob")

    created = client.post("/transactions", headers=alice, json={
        "type": "Income",
        "amount": 500,
        "category": "Paycheck"
    })

    transaction_id = created.json()["id"]

    bob_transactions = client.get(
        "/transactions", headers=bob
    )
    assert bob_transactions.json() == []

    bob_balance = client.get("/balance", headers=bob)
    assert bob_balance.json()["balance"] == 0

    update_response = client.put(
        f"/transactions/{transaction_id}",
        headers=bob,
        json={
            "type": "Income",
            "amount": 1000,
            "category": "Salary"
        }
    )
    assert update_response.status_code == 404

    delete_response = client.delete(
        f"/transactions/{transaction_id}",
        headers=bob
    )
    assert delete_response.status_code == 404

    alice_transactions = client.get(
        "/transactions", headers=alice
    )
    assert len(alice_transactions.json()) == 1
    assert alice_transactions.json()[0]["amount"] == 500


def test_invalid_amounts():
    headers = create_user("alice")

    for amount in [0, -50, 10.999]:
        response = client.post(
            "/transactions",
            headers=headers,
            json={
                "type": "Income",
                "amount": amount,
                "category": "Salary"
            }
        )

        assert response.status_code == 422

    response = client.get("/transactions", headers=headers)
    assert response.json() == []
