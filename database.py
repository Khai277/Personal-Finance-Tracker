import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://localhost:5432/finance_tracker"
)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


    