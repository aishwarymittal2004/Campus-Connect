"""
Centralized application configuration.

All configuration is sourced from environment variables (see .env.example).
Never hardcode secrets here - this file only defines *how* config is loaded
and what the safe defaults are for local development.
"""
from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "Campus Connect API"
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # --- Security / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://campus:campus@localhost:5432/campus_connect"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://campus:campus@localhost:5432/campus_connect"
    DB_ECHO: bool = False

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- External APIs (all optional; features degrade gracefully if unset) ---
    GOOGLE_MAPS_API_KEY: str = ""
    FOURSQUARE_API_KEY: str = ""
    RAPIDAPI_KEY_TRAIN: str = ""
    RAPIDAPI_KEY_FLIGHT: str = ""
    RAPIDAPI_KEY_AMAZON: str = ""
    RAPIDAPI_KEY_FLIPKART: str = ""


    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = 60

    # --- Admin bootstrap (first-run convenience only) ---
    FIRST_ADMIN_EMAIL: str = "admin@campusconnect.app"
    FIRST_ADMIN_PASSWORD: str = "ChangeMe123!"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so environment parsing only happens once per process."""
    return Settings()


settings = get_settings()
