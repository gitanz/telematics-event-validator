import os

from dotenv import load_dotenv

def load_config() -> None:
    if os.getenv('APP_ENV') is None:
        raise Exception("APP_ENV environment variable is not set. Please set it to 'development', or 'test'.")

    if os.getenv('APP_ENV') == 'test':
        load_dotenv('../.env.test')
        return

    load_dotenv()

load_config()

class Config:
    APP_ENV = os.getenv("APP_ENV", "development")
    TRIP_INGESTION_SERVICE_URL = os.getenv("TRIP_INGESTION_SERVICE_URL")

    def to_dict(self) -> dict[str, str]:
        return {
            "APP_ENV": self.APP_ENV,
            "TRIP_INGESTION_SERVICE_URL": self.TRIP_INGESTION_SERVICE_URL
        }
