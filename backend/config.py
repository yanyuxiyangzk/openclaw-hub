from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "OpenClawHub"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./openclawhub.db"

    SECRET_KEY: str = "change-this-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]

    REDIS_URL: str = "redis://localhost:6379"

    PROJECT_DATA_PATH: str = "./data/projects"
    HARNESS_PATH: str = "./harness"
    LOG_PATH: str = "./logs"


@lru_cache()
def get_settings():
    return Settings()
