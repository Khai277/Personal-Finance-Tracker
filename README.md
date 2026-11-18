# Personal Finance Tracker

A backend personal finance application built with Python, FastAPI, and PostgreSQL. The application allows users to securely manage income and expenses, track account balances, and access their own financial transactions through a REST API.

## Features

- User registration and login with hashed passwords
- JWT-based authentication
- Protected API endpoints
- User-specific transaction storage and access
- Create, retrieve, update, and delete transactions
- Automatically generated transaction IDs
- Account balance calculation
- Transaction amount validation using Decimal
- Insufficient-funds protection
- PostgreSQL database integration
- Automated API and security testing with pytest

## Technologies

- **Language:** Python
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Authentication:** JWT and pwdlib (Argon2)
- **Database Driver:** Psycopg
- **Testing:** pytest and FastAPI TestClient

## Project Development

### Version 1 — Command-Line Application
Built the initial personal finance tracker using Python with JSON file storage.

### Version 2 — REST API
Converted the application into a FastAPI backend with endpoints for managing transactions and calculating account balances.

### Version 3 — PostgreSQL Integration
Replaced JSON storage with PostgreSQL and SQLAlchemy for persistent relational database storage.

### Version 4 — Authentication and Testing
Implemented user registration, login, password hashing, JWT authentication, protected endpoints, transaction ownership, and automated tests.

## Database Setup

Install and start PostgreSQL.

Create a database named `finance_tracker`.

Create the following tables:

**users**
- `id`: SERIAL PRIMARY KEY
- `username`: VARCHAR(100) UNIQUE NOT NULL
- `hashed_password`: VARCHAR(255) NOT NULL

**transactions**
- `id`: SERIAL PRIMARY KEY
- `type`: VARCHAR(20)
- `amount`: NUMERIC(12,2)
- `category`: VARCHAR(100)
- `user_id`: INTEGER REFERENCES users(id)

Each transaction is associated with a user account.

## Installation

Clone the repository:

```bash
git clone https://github.com/Khai277/Personal-Finance-Tracker.git
cd Personal-Finance-Tracker
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install "fastapi[standard]" sqlalchemy "psycopg[binary]" pydantic pwdlib[argon2] PyJWT python-dotenv pytest httpx
```

Create a `.env` file containing:

```dotenv
JWT_SECRET_KEY=your_generated_secret_key
```

Generate a secure secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit your `.env` file to GitHub.

## Run the API

Start the FastAPI development server:

```bash
python -m fastapi dev api.py
```

Open:

http://127.0.0.1:8000/docs

The interactive Swagger interface allows you to register, log in, authorize requests using a JWT, and manage transactions.

If port 8000 is unavailable, specify another port when starting the server.

## Automated Testing

The project includes 9 automated tests covering:

- API availability
- User registration and login
- Incorrect password rejection
- Unauthorized endpoint access
- Transaction creation and retrieval
- Transaction updates
- Transaction deletion
- User isolation
- Invalid transaction amount rejection

Run the tests:

```bash
python -m pytest -v
```

Tests use a separate PostgreSQL database named `finance_tracker_test`.

**Current test results: 9 passed.**

## Future Improvements

- Docker containerization
- AWS cloud deployment
- Additional security and validation tests
- Improved configuration and deployment workflows