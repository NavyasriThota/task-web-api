import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def resolve_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL") or os.getenv("DATABASEDATABASE_URL")
    if not raw_url:
        return "sqlite:///./student_management.db"

    lowered = raw_url.lower()
    placeholder_tokens = ("username", "password", "host", "database_name")
    if any(token in lowered for token in placeholder_tokens):
        return "sqlite:///./student_management.db"

    if raw_url.startswith("postgresql://") and "+" not in raw_url.split("://", 1)[1][:10]:
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return raw_url


DATABASE_URL = resolve_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
