from sqlalchemy import create_engine

from config import DatabaseConfig


class DatabaseConnection:
    def __init__(self, database_config: DatabaseConfig) -> None:
        self.database_config = database_config
        self.connection_string = f"mysql+pymysql://{database_config.user}:{database_config.password}@{database_config.host}:{database_config.port}/{database_config.name}"
        self.engine = create_engine(self.connection_string)
        self.connection = self.engine.connect()

connection = DatabaseConnection(DatabaseConfig()).connection
