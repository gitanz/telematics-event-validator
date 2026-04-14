import logging
from abc import ABC, abstractmethod
from typing import Union, List
from sqlalchemy import text, Connection

from exceptions.trip_exceptions import TripNotFoundException, UnauthorizedTripException
from models.moderator import Location, Moderator
from models.trip import Trip, Stop


class TripRepositoryInterface(ABC):
    @abstractmethod
    def get_trip(self, trip_id: str, moderator: Moderator) -> Union[Trip, None]:
        pass

    @abstractmethod
    def list_trips(self, moderator: Moderator) -> List[Trip]:
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

    def get_trip(self, trip_id: str, moderator: Moderator) -> Union[Trip, None]:
        fetch_trip_sql = text("""
            SELECT 
                trips.*, 
                trip_stops.stop_location, 
                trip_stops.stop_datetime,
                IF(
                    latest_claims.claimed_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE),
                    NULL,
                    latest_claims.claimed_by
                ) as claimed_by,
                IF(
                    latest_claims.claimed_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE),
                    NULL,
                    latest_claims.claimed_at
                ) as claimed_at,
                 
                trips_acknowledgements.*
            FROM trips
            LEFT JOIN trip_stops ON trips.id = trip_stops.trip_id
             
            LEFT JOIN (
                SELECT trips_claims.* FROM trips_claims
                INNER JOIN (
                    SELECT trip_id, MAX(claimed_at) as claimed_at 
                    FROM trips_claims
                    GROUP BY trip_id
                ) as latest_trip_id_claim_tuple 
                ON 
                trips_claims.trip_id = latest_trip_id_claim_tuple.trip_id AND 
                trips_claims.claimed_at = latest_trip_id_claim_tuple.claimed_at
            ) as latest_claims ON trips.id = latest_claims.trip_id
            
            LEFT JOIN trips_acknowledgements ON trips.id = trips_acknowledgements.trip_id
            WHERE 
                trips.unique_id = :unique_id AND 
                trips.location = :location AND
                (
                    (latest_claims.trip_id IS NULL) OR
                    (   
                        latest_claims.trip_id IS NOT NULL AND -- latest claim 
                        latest_claims.claimed_by = :moderator  AND -- by current moderator
                        latest_claims.claimed_at >= DATE_SUB(NOW(), INTERVAL 15 MINUTE) -- within last 15 minutes
                    ) OR
                    (
                        latest_claims.trip_id IS NOT NULL AND -- latest claim 
                        latest_claims.claimed_by IS NOT NULL AND  -- by any moderator
                        latest_claims.claimed_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE) --  more than 15 minutes ago
                    )
                ) AND
                (
                    trips_acknowledgements.trip_id IS NULL  -- unacknowledged trips only
                ) AND
                trips.created_at > DATE_SUB(CURDATE(), INTERVAL 1 DAY) -- created more than 1 day ago
                
        """)

        result = self.connection.execute(fetch_trip_sql, {
            'unique_id': trip_id,
            'location': moderator.location.value,
            'moderator': moderator.moderator_id,
        })

        trip_with_stops = result.mappings().fetchall()

        if not len(trip_with_stops):
            return None

        print(trip_with_stops[0])

        trip = trip_with_stops[0]

        if trip["unique_id"] is None:
            raise TripNotFoundException("Trip unique_id is missing in the database result.")

        return Trip(
            trip_id=trip["unique_id"],
            location=Location(trip["location"]),
            country=trip["country"],
            start= Stop.from_values(trip["start_location"], trip["start_datetime"]) if trip["start_location"] and trip["start_datetime"] else None,
            stops= [
                Stop.from_values(stop["stop_location"], stop["stop_datetime"]) for stop in trip_with_stops if stop["stop_location"] and stop["stop_datetime"]
            ],
            end= Stop.from_values(trip["end_location"], trip["end_datetime"]) if trip["end_location"] and trip["end_datetime"] else None,
            claimed_by=trip["claimed_by"],
            claimed_at=trip["claimed_at"],
            acknowledged_by=trip["acknowledged_by"],
            acknowledged_at=trip["acknowledged_at"],
        )

    def list_trips(self, moderator: Moderator) -> List[Trip]:
        fetch_trips_sql = text("""
            SELECT * FROM trips
            LEFT JOIN (
                SELECT trips_claims.* FROM trips_claims
                INNER JOIN (
                    SELECT trip_id, MAX(claimed_at) as claimed_at 
                    FROM trips_claims
                    GROUP BY trip_id
                ) as latest_trip_id_claim_tuple 
                ON 
                trips_claims.trip_id = latest_trip_id_claim_tuple.trip_id AND 
                trips_claims.claimed_at = latest_trip_id_claim_tuple.claimed_at
            ) latest_claims ON trips.id = latest_claims.trip_id
            LEFT JOIN trips_acknowledgements ON trips.id = trips_acknowledgements.trip_id
            WHERE 
                trips.location = :location and
                (
                    (latest_claims.trip_id IS NULL) OR
                    (   
                        latest_claims.trip_id IS NOT NULL AND -- latest claim 
                        latest_claims.claimed_by = :moderator  AND -- by current moderator
                        latest_claims.claimed_at >= DATE_SUB(NOW(), INTERVAL 15 MINUTE) -- within last 15 minutes
                    ) OR
                    (
                        latest_claims.trip_id IS NOT NULL AND -- latest claim 
                        latest_claims.claimed_by IS NOT NULL AND  -- by any moderator
                        latest_claims.claimed_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE) --  more than 15 minutes ago
                    )
                ) AND
                (
                    trips_acknowledgements.trip_id IS NULL  -- unacknowledged trips only
                ) AND
                trips.created_at > DATE_SUB(CURDATE(), INTERVAL 1 DAY) -- created more than 1 day ago
        """)

        result = self.connection.execute(fetch_trips_sql, {
            'location': moderator.location.value,
            'moderator': moderator.moderator_id,
            'acknowledged_by': moderator.moderator_id,
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
        if self.connection.in_transaction():
            transaction = self.connection.begin_nested()
        else:
            transaction = self.connection.begin()
        try:
            trip_sql = text("""
                SELECT trips.* FROM trips
                
                LEFT JOIN (
                    SELECT trips_claims.* FROM trips_claims 
                    INNER JOIN (
                        SELECT trip_id, MAX(claimed_at) as claimed_at 
                        FROM trips_claims
                        GROUP BY trip_id
                    ) as latest_trip_id_claim_tuple 
                    ON 
                    trips_claims.trip_id = latest_trip_id_claim_tuple.trip_id AND 
                    trips_claims.claimed_at = latest_trip_id_claim_tuple.claimed_at
                ) latest_claims ON
                    trips.id = latest_claims.trip_id
                    
                LEFT JOIN trips_acknowledgements ON 
                    trips.id =trips_acknowledgements.trip_id
                WHERE
                    trips.unique_id = :unique_id AND
                    trips.location = :location AND
                    (
                        (latest_claims.trip_id IS NULL) OR -- no claims
                        (
                            latest_claims.trip_id IS NOT NULL AND -- has latest claims
                            latest_claims.claimed_by IS NOT NULL  AND -- by any moderator
                            latest_claims.claimed_at < DATE_SUB(NOW(), INTERVAL 15 MINUTE) --  15 minutes ago
                        )
                    ) AND
                    (
                        trips_acknowledgements.trip_id IS NULL  -- unacknowledged trips only
                    ) AND
                    trips.created_at > DATE_SUB(CURDATE(), INTERVAL 1 DAY) -- created more than 1 day ago
                    
                FOR UPDATE
            """)

            results = self.connection.execute(trip_sql, {
                'unique_id': trip_id,
                'location': moderator.location.value,
                'moderator': moderator.moderator_id,
            })

            trip = results.mappings().fetchone()

            if not trip:
                raise UnauthorizedTripException()

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
        if self.connection.in_transaction():
            transaction = self.connection.begin_nested()
        else:
            transaction = self.connection.begin()
        try:
            trip_sql = text("""
                SELECT trips.* FROM trips
                LEFT JOIN (
                    SELECT trips_claims.* FROM trips_claims
                    INNER JOIN (
                        SELECT trip_id, MAX(claimed_at) as claimed_at 
                        FROM trips_claims
                        GROUP BY trip_id
                    ) as latest_trip_id_claimed_at_tuple
                    ON
                    trips_claims.trip_id = latest_trip_id_claimed_at_tuple.trip_id AND
                    trips_claims.claimed_at = latest_trip_id_claimed_at_tuple.claimed_at
                ) latest_claims ON trips.id = latest_claims.trip_id
                LEFT JOIN trips_acknowledgements ON trips.id = trips_acknowledgements.trip_id
                WHERE
                    trips.unique_id = :unique_id AND
                    trips.location = :location AND
                    (   
                        latest_claims.trip_id IS NOT NULL AND -- has latest claim 
                        latest_claims.claimed_by = :moderator  AND -- by current moderator
                        latest_claims.claimed_at >= DATE_SUB(NOW(), INTERVAL 15 MINUTE) -- within last 15 minutes
                    ) AND
                    trips_acknowledgements.trip_id IS NULL AND
                    trips.created_at > DATE_SUB(CURDATE(), INTERVAL 1 DAY) -- created more than 1 day ago
                FOR UPDATE
            """)

            results = self.connection.execute(trip_sql, {
                'unique_id': trip_id,
                'location': moderator.location.value,
                'moderator': moderator.moderator_id,
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
