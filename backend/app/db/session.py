import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger

db_url = settings.get_database_url()

def create_configured_engine(url: str):
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    
    try:
        engine = create_engine(
            url,
            echo=False,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        logger.info(f"Database connection verified successfully using: {url.split('@')[-1] if '@' in url else url}")
        return engine
    except Exception as e:
        if settings.ALLOW_SQLITE_FALLBACK and not url.startswith("sqlite"):
            logger.warning(
                f"Failed to connect to primary database ({url.split('@')[-1] if '@' in url else url}): {e}. "
                "Falling back to local SQLite engine (datapulse.db)."
            )
            fallback_url = "sqlite:///./datapulse.db"
            fallback_engine = create_engine(
                fallback_url,
                echo=False,
                connect_args={"check_same_thread": False},
            )
            return fallback_engine
        raise e

engine = create_configured_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for obtaining a clean database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
