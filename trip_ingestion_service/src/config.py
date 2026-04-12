import os
from typing import Optional
from dotenv import load_dotenv

def load_env() -> None:
    if os.getenv('APP_ENV') is None:
        raise Exception("APP_ENV environment variable is not set. Please set it to 'development', or 'test'.")

    if os.getenv('APP_ENV') == 'test':
        load_dotenv(dotenv_path='.env.test')
        return

    load_dotenv()

load_env()


class QueueConfig:
    driver: Optional[str] = os.getenv("QUEUE_DRIVER")
    host: Optional[str] = os.getenv("QUEUE_HOST", "localhost")
    port: Optional[int] = int(os.getenv("QUEUE_PORT", "5672"))
    user: Optional[str] = os.getenv("QUEUE_USER", "guest")
    password: Optional[str] = os.getenv("QUEUE_PASSWORD", "guest")
    batch_size: Optional[int] = int(os.getenv("QUEUE_BATCH_SIZE", "10"))

queue_config  = QueueConfig()


class DatabaseConfig:
    driver: Optional[str] = os.getenv("DB_DRIVER")
    host: Optional[str] = os.getenv("DB_HOST", "localhost")
    port: Optional[int] = int(os.getenv("DB_PORT", "3306"))
    user: Optional[str] = os.getenv("DB_USER", "root")
    password: Optional[str] = os.getenv("DB_PASSWORD", "root")
    name: Optional[str] = os.getenv("DB_NAME", "trips")

database_config = DatabaseConfig()


class Config:
    env: str = os.getenv("APP_ENV", "development")
    queue_config: QueueConfig = queue_config
    db_config: DatabaseConfig = database_config

config: Config = Config()
