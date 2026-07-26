"""
LegalEase AI - Application Configuration
=========================================
Reads all settings from environment variables.
Uses pydantic-settings for type-safe config management.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration class.
    All values are loaded from the .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "LegalEase AI"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False

    # ---- API ----
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    # ---- Database ----
    database_url: str
    database_echo: bool = False

    # ---- JWT Authentication ----
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ---- Google Gemini API ----
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    gemini_temperature: float = 0.1

    # ---- ChromaDB ----
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "legalease_knowledge"

    # ---- Embeddings ----
    embedding_model: str = "all-MiniLM-L6-v2"

    # ---- CORS ----
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # ---- Logging ----
    log_level: str = "INFO"
    log_file: str = "logs/legalease.log"

    # ---- Legal Data ----
    legal_data_path: str = "./legal_data"
    chunk_size: int = 500
    chunk_overlap: int = 50

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins string into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return v

    @field_validator("gemini_api_key")
    @classmethod
    def gemini_key_must_not_be_placeholder(cls, v: str) -> str:
        if v == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY must be set to a real API key.")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached Settings instance.
    Uses lru_cache so the .env file is only parsed once per process.
    """
    return Settings()


# Module-level alias for convenience
settings = get_settings()
