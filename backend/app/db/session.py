
import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger("uvicorn.error")


def get_engine_and_url():
    target_url = settings.DATABASE_URL
    is_sqlite = target_url.startswith("sqlite")

    connect_args = {}
    if is_sqlite:
        connect_args["check_same_thread"] = False

    try:
        engine = create_engine(
            target_url,
            pool_pre_ping=True,
            connect_args=connect_args,
        )

        # Test the configured database connection.
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        safe_url = (
            target_url.split("@")[-1]
            if "@" in target_url
            else target_url
        )
        logger.info("Successfully connected to database: %s", safe_url)

        return engine, target_url

    except Exception as exc:
        if settings.ENABLE_SQLITE_FALLBACK and not is_sqlite:
            logger.warning(
                "Could not connect to the configured database. "
                "Using SQLite fallback: %s. Error: %s",
                settings.SQLITE_FALLBACK_URL,
                exc,
            )

            fallback_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True,
            )

            # Verify that the fallback database is accessible.
            with fallback_engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            return fallback_engine, settings.SQLITE_FALLBACK_URL

        raise


engine, active_db_url = get_engine_and_url()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models so SQLAlchemy registers all tables before creation.
    from app.models.user import User
    from app.models.knowledge import KnowledgeItem
    from app.models.query import StudentQuery

    Base.metadata.create_all(bind=engine)

    logger.info("Database tables verified/created successfully.")

    db_type = "MySQL" if "mysql" in active_db_url.lower() else "SQLite"
    logger.info("Active database type: %s", db_type)


def check_db_connection() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        db_type = "MySQL" if "mysql" in active_db_url.lower() else "SQLite"

        return {
            "status": "connected",
            "type": db_type,
        }

    except Exception:
        logger.exception("Database connection check failed.")

        return {
            "status": "disconnected",
            "error": "Database connection failed. Check backend logs.",
        }
