from abc import ABC, abstractmethod
from typing import Union, List
from sqlalchemy import text, Connection

from models.moderator import Location
from models.trip import Trip, Stop


class TripRepositoryInterface(ABC):
    @abstractmethod
    def get_trip(self, trip_id: str, location: str) -> Union[Trip, None]:
        pass

    @abstractmethod
    def list_trips(self, location: str) -> List[Trip]:
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
