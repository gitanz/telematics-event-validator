from sqlalchemy import text

from connections.database_connection import connection
from models.moderator import Location, Moderator
from repositories.moderator_repository import MySQLModeratorRepository


def test_get_moderator_found():
    transaction = connection.begin()

    try:
        moderator = Moderator(
            moderator_id=1,
            location=Location("North America")
        )

        sql = text("""
                INSERT INTO moderators (moderator_id, location) VALUES
                    (:moderator_id, :location);
            """)
        connection.execute(sql, {
            'moderator_id': moderator.moderator_id,
            'location': moderator.location.value,
        })

        mysql_moderator_repository = MySQLModeratorRepository(connection)
        fetched_moderator = mysql_moderator_repository.get_moderator(moderator.moderator_id, moderator.location.value)

        assert fetched_moderator is not None
        assert fetched_moderator.moderator_id == moderator.moderator_id
        assert fetched_moderator.location == moderator.location

    finally:
        transaction.rollback()


def test_get_moderator_not_found():
    transaction = connection.begin()
    try:
        # Ensure the moderator does not exist
        moderator = Moderator(
            moderator_id=1,
            location=Location("North America")
        )
        # No insert, so the moderator is not present
        mysql_moderator_repository = MySQLModeratorRepository(connection)
        fetched_moderator = mysql_moderator_repository.get_moderator(moderator.moderator_id, moderator.location.value)
        assert fetched_moderator is None
    finally:
        transaction.rollback()
