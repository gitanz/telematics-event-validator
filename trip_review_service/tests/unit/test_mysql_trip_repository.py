import datetime
import uuid

import pytest
from sqlalchemy import text, Connection

from config import DatabaseConfig
from connections.database_connection import DatabaseConnection
from exceptions.trip_exceptions import UnauthorizedTripException
from models.moderator import Moderator, Location
from models.trip import Trip
from repositories.trip_repository import MySQLTripRepository


def moderator_factory(connection: Connection, moderator_id: int, location: str) -> Moderator:
    moderator = Moderator(
        moderator_id=moderator_id,
        location=Location(location)
    )
    sql = text("""
            INSERT INTO moderators (moderator_id, location) VALUES
            (:moderator_id, :location);
        """)
    connection.execute(sql, {
        'moderator_id': moderator.moderator_id,
        'location': moderator.location.value,
    })

    return moderator

def trip_factory(connection: Connection, location: str) -> Trip:
    trip = Trip(
        trip_id= uuid.uuid4().hex,
        location=Location(location)
    )

    sql = text("""
            INSERT INTO trips (unique_id, location) VALUES
                (:trip_id, :location);
        """)

    connection.execute(sql, {
        'trip_id': trip.trip_id,
        'location': location,
    })

    return trip


def claim_trip_factory(connection: Connection, trip: Trip, moderator: Moderator, claimed_at = datetime.datetime.now(datetime.timezone.utc)) -> None:
    # get trip
    sql = text("""
            SELECT * FROM trips WHERE unique_id = :trip_id;
        """)
    result = connection.execute(sql, {'trip_id': trip.trip_id})
    trip_row = result.mappings().fetchone()
    trip_id = trip_row['id']

    sql = text("""
            INSERT INTO trips_claims (trip_id, claimed_by, claimed_at) VALUES
                (:trip_id, :claimed_by, :claimed_at);
        """)

    connection.execute(sql, {
        'trip_id': trip_id,
        'claimed_by': moderator.moderator_id,
        'claimed_at': claimed_at.strftime('%Y-%m-%d %H:%M:%S'),
    })


def acknowledge_trip_factory(connection: Connection, trip: Trip, moderator: Moderator, acknowledged_at = datetime.datetime.now(datetime.timezone.utc)) -> None:
    # get trip
    sql = text("""
            SELECT * FROM trips WHERE unique_id = :trip_id;
        """)
    result = connection.execute(sql, {'trip_id': trip.trip_id})
    trip_row = result.mappings().fetchone()
    trip_id = trip_row['id']

    sql = text("""
            INSERT INTO trips_acknowledgements (trip_id, acknowledged_by, acknowledged_at) VALUES
                (:trip_id, :acknowledged_by, :acknowledged_at);
        """)

    connection.execute(sql, {
        'trip_id': trip_id,
        'acknowledged_by': moderator.moderator_id,
        'acknowledged_at': acknowledged_at.strftime('%Y-%m-%d %H:%M:%S'),
    })

def test_list_trip_does_not_return_trips_claimed_by_other_moderators_within_15_minutes():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_retriever = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        trips = mysql_trip_repository.list_trips(moderator_retriever)
        assert len(trips) == 0

    finally:
        transaction.rollback()
        connection.close()

def test_list_trip_returns_trips_claimed_by_same_moderator_within_15_minutes():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        trips = mysql_trip_repository.list_trips(moderator_claimer)
        assert len(trips) == 1

    finally:
        transaction.rollback()
        connection.close()

def test_list_trip_returns_trips_claimed_by_other_moderators_if_claimed_more_than_15_minutes_before():
    config = DatabaseConfig()
    connection = DatabaseConnection(config).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_retriever = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
        claim_trip_factory(connection, trip, moderator_claimer, claimed_at=expired_time)

        mysql_trip_repository = MySQLTripRepository(connection)
        trips = mysql_trip_repository.list_trips(moderator_retriever)
        assert len(trips) == 1

    finally:
        transaction.rollback()
        connection.close()

def test_list_trip_does_not_return_acknowledged_trips_even_if_claimed_by_same_moderator():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)
        acknowledge_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        trips = mysql_trip_repository.list_trips(moderator_claimer)
        assert len(trips) == 0

    finally:
        transaction.rollback()
        connection.close()


def test_get_trip_returns_trip_claimed_by_same_moderator_within_15_minutes():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        retrieved_trip = mysql_trip_repository.get_trip(trip.trip_id, moderator_claimer)
        assert retrieved_trip is not None
        assert retrieved_trip.trip_id == trip.trip_id
    finally:
        transaction.rollback()
        connection.close()

def test_get_trip_does_not_return_trip_claimed_by_other_moderator_within_15_minutes():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_retriever = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        retrieved_trip = mysql_trip_repository.get_trip(trip.trip_id, moderator_retriever)
        assert retrieved_trip is None
    finally:
        transaction.rollback()
        connection.close()

def test_get_trip_returns_trip_claimed_by_other_moderator_if_claimed_more_than_15_minutes_before():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_retriever = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
        claim_trip_factory(connection, trip, moderator_claimer, claimed_at=expired_time)

        mysql_trip_repository = MySQLTripRepository(connection)
        retrieved_trip = mysql_trip_repository.get_trip(trip.trip_id, moderator_retriever)
        assert retrieved_trip is not None
        assert retrieved_trip.trip_id == trip.trip_id
    finally:
        transaction.rollback()
        connection.close()

def test_get_trip_does_not_return_acknowledged_trip_even_if_claimed_by_same_moderator():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()

    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)
        acknowledge_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)
        retrieved_trip = mysql_trip_repository.get_trip(trip.trip_id, moderator_claimer)
        assert retrieved_trip is None
    finally:
        transaction.rollback()
        connection.close()

def test_claim_trip_claims_trip():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()
    try:
        moderator = moderator_factory(connection, 1, 'North America')
        trip = trip_factory(connection, 'North America')
        mysql_trip_repository = MySQLTripRepository(connection)
        # Should succeed
        result = mysql_trip_repository.claim_trip(trip.trip_id, moderator)
        assert result is True
        # Check that the claim exists in the database
        sql = text("""SELECT * FROM
            trips 
            INNER JOIN trips_claims on trips.id = trips_claims.trip_id
            WHERE trips.unique_id = :trip_id AND claimed_by = :moderator_id""")

        claim = connection.execute(sql, {
            'trip_id': trip.trip_id,
            'moderator_id': moderator.moderator_id
        }).mappings().fetchone()

        assert claim is not None
        assert claim['claimed_by'] == moderator.moderator_id
    finally:
        transaction.rollback()
        connection.close()


def test_claim_trip_does_not_claim_trip_already_claimed_by_other_moderator_within_15_minutes():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()
    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_other = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)

        with pytest.raises(UnauthorizedTripException):
            mysql_trip_repository.claim_trip(trip.trip_id, moderator_other)
    finally:
        transaction.rollback()
        connection.close()

def test_claim_trip_allows_claiming_trip_already_claimed_by_other_moderator_if_claimed_more_than_15_minutes_before():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()
    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_other = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        expired_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)
        claim_trip_factory(connection, trip, moderator_claimer, claimed_at=expired_time)

        mysql_trip_repository = MySQLTripRepository(connection)

        result = mysql_trip_repository.claim_trip(trip.trip_id, moderator_other)
        assert result is True
    finally:
        transaction.rollback()
        connection.close()

def test_acknowledge_trip_acknowledges_trip():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()
    try:
        moderator = moderator_factory(connection, 1, 'North America')
        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator)

        mysql_trip_repository = MySQLTripRepository(connection)
        result = mysql_trip_repository.acknowledge_trip(trip.trip_id, moderator)
        assert result is True

        sql = text("""SELECT * FROM
                    trips 
                    INNER JOIN trips_acknowledgements on trips.id = trips_acknowledgements.trip_id
                    WHERE trips.unique_id = :trip_id AND acknowledged_by = :moderator_id""")

        acknowledgement = connection.execute(sql, {
            'trip_id': trip.trip_id,
            'moderator_id': moderator.moderator_id
        }).mappings().fetchone()

        assert acknowledgement is not None
        assert acknowledgement['acknowledged_by'] == moderator.moderator_id
    finally:
        transaction.rollback()
        connection.close()

def test_acknowledge_trip_does_not_acknowledge_trip_not_claimed_by_moderator():
    connection = DatabaseConnection(DatabaseConfig()).connection
    transaction = connection.begin()
    try:
        moderator_claimer = moderator_factory(connection, 1, 'North America')
        moderator_other = moderator_factory(connection, 2, 'North America')

        trip = trip_factory(connection, 'North America')
        claim_trip_factory(connection, trip, moderator_claimer)

        mysql_trip_repository = MySQLTripRepository(connection)

        with pytest.raises(UnauthorizedTripException):
            mysql_trip_repository.acknowledge_trip(trip.trip_id, moderator_other)
    finally:
        transaction.rollback()
        connection.close()