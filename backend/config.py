from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
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

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
