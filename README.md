
## Version 3 - PostgreSQL Database Integration

Upgraded the FastAPI backend from JSON file storage to PostgreSQL.

### Features
- Store transactions in PostgreSQL
- Create, retrieve, update, and delete transactions
- Automatically generate unique transaction IDs
- Calculate account balances from database records
- Validate transaction amounts and prevent insufficient funds
- Handle invalid transaction IDs with HTTP errors

### Technologies
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Psycopg

### Database Setup

1. Install and start PostgreSQL.
2. Create a database named `finance_tracker`.
3. Create a `transactions` table with the following columns:
   - id: SERIAL PRIMARY KEY
   - type: VARCHAR(20)
   - amount: NUMERIC(12,2)
   - category: VARCHAR(100)

### Run the API

Install dependencies:

    python -m pip install "fastapi[standard]" sqlalchemy "psycopg[binary]"

Start the server:

    python -m fastapi dev api.py

Open http://127.0.0.1:8000/docs to test the endpoints.
