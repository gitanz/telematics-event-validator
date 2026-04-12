from abc import ABC, abstractmethod
from typing import Union
from sqlalchemy import create_engine, text, Connection
from models.moderator import Location, Moderator


class ModeratorRepositoryInterface(ABC):
    @abstractmethod
    def get_moderator(self, moderator_id: int, location: Location) -> Moderator:
        pass


class MySQLModeratorRepository(ModeratorRepositoryInterface):
    def __init__(self, connection: Connection):
        self.connection = connection


    def get_moderator(self, moderator_id: int, location: Location) -> Union[Moderator, None]:
        fetch_moderator_sql = text("""
            SELECT * FROM moderators 
            WHERE moderator_id = :moderator_id and location = :location
        """)

        result = self.connection.execute(fetch_moderator_sql, {
            'moderator_id': moderator_id,
            'location': location.value,
        })

        moderator = result.mappings().fetchone()

        if moderator is None:
            return None

        return Moderator(
            moderator_id=int(moderator["moderator_id"]),
            location=Location(moderator['location'])
        )
