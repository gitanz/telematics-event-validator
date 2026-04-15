import os
from typing import Optional

from dotenv import load_dotenv

def load_env() -> None:
    if os.getenv('APP_ENV') is None:
        raise Exception("APP_ENV environment variable is not set. Please set it to 'development', or 'test'.")

    if os.getenv('APP_ENV') == 'test':
        load_dotenv('.env.test')
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

class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    TRIP_INGESTION_SERVICE_URL = os.getenv("TRIP_INGESTION_SERVICE_URL")

    def to_dict(self) -> dict[str, str]:
        return {
            "APP_ENV": self.APP_ENV,
            "TRIP_INGESTION_SERVICE_URL": self.TRIP_INGESTION_SERVICE_URL
        }
