from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - configured for MySQL/TiDB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.environ.get("TIDB_CONNECTION_STRING"),
)

# Create synchronous engine
engine = create_engine(DATABASE_URL, echo=True)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
