from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class AppSettings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    DATABASE_URL: str = "postgresql+asyncpg://user:mypassword@127.0.0.1:5434/task-manager-db"
    DEBUG: bool = True
    SCHEMA_REGISTRY_URL: str = "http://localhost:8081"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    SMTP_HOSTNAME: str = "127.0.0.1"
    SMTP_PORT: str = "587"

    class Config:
        env_file: str = "settings/.env"


@lru_cache(maxsize=None)
def get_settings() -> AppSettings:
    return AppSettings()  # type: ignore[call-arg]