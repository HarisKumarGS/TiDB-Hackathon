from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import os

# Database URL - configured for MySQL/TiDB
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://2AyjJP1eRHUCep3.root:YOUR_PASSWORD_HERE@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/test",
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
