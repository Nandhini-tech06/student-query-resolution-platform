import logging
from typing import Generator
from sqlalchemy import create_engine, text
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
            connect_args=connect_args
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Successfully connected to database: {target_url.split('@')[-1] if '@' in target_url else target_url}")
        return engine, target_url
    except Exception as e:
        if settings.ENABLE_SQLITE_FALLBACK and not is_sqlite:
            logger.warning(
                f"Could not connect to configured MySQL database ({e}). "
                f"Falling back to local SQLite database for development: {settings.SQLITE_FALLBACK_URL}"
            )
            fallback_engine = create_engine(
                settings.SQLITE_FALLBACK_URL,
                connect_args={"check_same_thread": False}
            )
            return fallback_engine, settings.SQLITE_FALLBACK_URL
        raise e

engine, active_db_url = get_engine_and_url()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models.user import User
    from app.models.knowledge import KnowledgeItem
    from app.models.query import StudentQuery
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")

def check_db_connection() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_type = "MySQL" if "mysql" in active_db_url else "SQLite"
        return {"status": "connected", "type": db_type}
    except Exception as exc:
        return {"status": "disconnected", "error": str(exc)}
