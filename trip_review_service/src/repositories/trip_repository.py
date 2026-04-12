import logging
from abc import ABC, abstractmethod
from typing import Union, List
from sqlalchemy import text, Connection

from exceptions.trip_exceptions import TripNotFoundException, UnauthorizedTripException
from models.moderator import Location, Moderator
from models.trip import Trip, Stop


class TripRepositoryInterface(ABC):
    @abstractmethod
    def get_trip(self, trip_id: str, location: str) -> Union[Trip, None]:
        pass

    @abstractmethod
    def list_trips(self, location: str) -> List[Trip]:
        pass

    @abstractmethod
    def claim_trip(self, trip_id: str, moderator: Moderator) -> bool:
        pass

    @abstractmethod
    def acknowledge_trip(self, trip_id: str, moderator: Moderator) -> bool:
        pass


class MySQLTripRepository(TripRepositoryInterface):
    def __init__(self, connection: Connection):
        self.connection = connection

    def get_trip(self, trip_id: str, location: str) -> Union[Trip, None]:
        fetch_trip_sql = text("""
            SELECT * FROM trips
            LEFT JOIN trip_stops ON trips.id = trip_stops.trip_id 
            WHERE trips.unique_id = :unique_id and trips.location = :location
        """)

        result = self.connection.execute(fetch_trip_sql, {
            'unique_id': trip_id,
            'location': location,
        })
        trip_with_stops = result.mappings().fetchall()

        if not len(trip_with_stops):
            return None

        trip = trip_with_stops[0]

        return Trip(
            trip_id=trip["unique_id"],
            location=Location(trip["location"]),
            country=trip["country"],
            start= Stop.from_values(trip["start_location"], trip["start_datetime"]) if trip["start_location"] and trip["start_datetime"] else None,
            stops= [
                Stop.from_values(stop["stop_location"], stop["stop_datetime"]) for stop in trip_with_stops if stop["stop_location"] and stop["stop_datetime"]
            ],
            end= Stop.from_values(trip["end_location"], trip["end_datetime"]) if trip["end_location"] and trip["end_datetime"] else None,
        )

    def list_trips(self, location: str) -> List[Trip]:
        fetch_trips_sql = text("""
            SELECT * FROM trips
            WHERE location = :location
        """)

        result = self.connection.execute(fetch_trips_sql, {
            'location': location,
        })

        trips = result.mappings().fetchall()

        return [
            Trip(
                trip_id=trip["unique_id"],
                location=Location(trip["location"]),
                country=trip["country"],
                start= Stop.from_values(trip["start_location"], trip["start_datetime"]) if trip["start_location"] and trip["start_datetime"] else None,
                end= Stop.from_values(trip["end_location"], trip["end_datetime"]) if trip["end_location"] and trip["end_datetime"] else None,
            ) for trip in trips
        ]

    def claim_trip(self, trip_id: str, moderator: Moderator) -> bool:
        transaction = self.connection.begin()
        try:
            trip_sql = text("""
                SELECT trips.* FROM trips
                LEFT JOIN trips_claims ON
                    trips.id = trips_claims.trip_id
                WHERE
                    trips.unique_id = :unique_id AND
                    trips.location = :location AND
                    trips_claims.trip_id IS NULL
                FOR UPDATE
            """)

            results = self.connection.execute(trip_sql, {
                'unique_id': trip_id,
                'location': moderator.location.value,
            })

            trip = results.mappings().fetchone()

            if not trip:
                raise TripNotFoundException()

            claim_sql = text("""
                INSERT INTO trips_claims (trip_id, claimed_by, claimed_at)
                VALUES (
                    :trip_id,
                    :claimed_by,
                    NOW()
                )
            """)

            self.connection.execute(claim_sql, {
                'trip_id': trip['id'],
                'claimed_by': moderator.moderator_id
            })

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e
        return True

    def acknowledge_trip(self, trip_id: str, moderator: Moderator) -> bool:
        transaction = self.connection.begin()
        try:
            trip_sql = text("""
                SELECT trips.* FROM trips
                LEFT JOIN trips_claims ON trips.id = trips_claims.trip_id
                LEFT JOIN trips_acknowledgements ON trips.id =trips_acknowledgements.trip_id
                WHERE
                    trips.unique_id = :unique_id AND
                    trips.location = :location AND
                    trips_claims.claimed_by = :claimed_by AND
                    trips_acknowledgements.trip_id IS NULL
                FOR UPDATE
            """)

            results = self.connection.execute(trip_sql, {
                'unique_id': trip_id,
                'location': moderator.location.value,
                'claimed_by': moderator.moderator_id,
            })

            trip = results.mappings().fetchone()

            if not trip:
                raise UnauthorizedTripException()

            claim_sql = text("""
                INSERT INTO trips_acknowledgements (trip_id, acknowledged_by, acknowledged_at)
                VALUES (
                    :trip_id,
                    :acknowledged_by,
                    NOW()
                )
            """)

            self.connection.execute(claim_sql, {
                'trip_id': trip['id'],
                'acknowledged_by': moderator.moderator_id,
            })

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            raise e
        return True
