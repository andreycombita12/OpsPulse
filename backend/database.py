import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_USER = os.getenv("POSTGRES_USER", "opspulseuser")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "opspulsepass")
DB_HOST = os.getenv("POSTGRES_HOST", "database")
DB_NAME = os.getenv("POSTGRES_DB", "opspulsedb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
