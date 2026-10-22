
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================================
    # Application Settings
    # ============================================================

    PROJECT_NAME: str = "Student Query Resolution Platform"
    API_V1_STR: str = "/api/v1"

    # ============================================================
    # JWT / Security Settings
    # ============================================================

    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_SECRET_KEY_SUPER_SECURE_123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ============================================================
    # Database Settings
    # ============================================================

    DATABASE_URL: str = (
        "mysql+pymysql://root:password@localhost:3306/student_query_db"
    )

    ENABLE_SQLITE_FALLBACK: bool = True
    SQLITE_FALLBACK_URL: str = "sqlite:///./student_query_platform.db"

    # ============================================================
    # CORS Settings
    # ============================================================

    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # ============================================================
    # Initial Admin Account
    # ============================================================

    FIRST_ADMIN_EMAIL: str = "admin@nip.ac.in"
    FIRST_ADMIN_PASSWORD: str = "Tnorth"
    FIRST_ADMIN_NAME: str = "Platform Administrator"

    # ============================================================
    # Generative AI / RAG Settings
    # ============================================================

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.6-flash"
    RAG_MIN_CONFIDENCE: float = 0.50
    RAG_TOP_K: int = 4

    # ============================================================
    # Pydantic Settings Configuration
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# ================================================================
# Create Settings Object
# ================================================================

settings = Settings()
