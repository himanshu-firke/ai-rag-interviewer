"""
Database setup using SQLAlchemy with SQLite.
Provides engine, session factory, and dependency injection for FastAPI.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import settings

# Create engine — using check_same_thread=False for SQLite + FastAPI async
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency — yields a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on application startup."""
    from backend import models  # noqa: F401 — import to register models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
