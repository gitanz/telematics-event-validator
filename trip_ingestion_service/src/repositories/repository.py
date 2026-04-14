from abc import ABC, abstractmethod
from sqlalchemy import create_engine, text

from config import DatabaseConfig
from models.Trip import Trip


class TripRepository(ABC):

    @abstractmethod
    def insert(self, data: Trip) -> None:
        pass

    def prune(self):
        pass


class MySQLTripRepository(TripRepository):
    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self.connection_string = f"mysql+pymysql://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"
        self.engine = create_engine(self.connection_string)

    def insert(self, trip: Trip) -> None:
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                trips_insert_sql = text(
                    """
                    INSERT INTO trips (
                        unique_id, location, country, start_location, start_datetime, end_location, end_datetime
                    ) VALUES (:unique_id, :location, :country, :start_location, :start_datetime, :end_location, :end_datetime)
                    """
                )
                trip_dict = {
                    'unique_id': trip.trip_id,
                    'location': trip.location,
                    'country': trip.country,
                    'start_location': trip.start.location,
                    'start_datetime': trip.start.timestamp,
                    'end_location': trip.end.location,
                    'end_datetime': trip.end.timestamp,
                }

                result = conn.execute(trips_insert_sql, trip_dict)
                trip_id = result.lastrowid
                stops_insert_sql = text(
                    """
                    INSERT INTO trip_stops (
                        trip_id, unique_id, stop_location, stop_datetime
                    ) VALUES (:trip_id, :unique_id, :stop_location, :stop_datetime)
                    """
                )
                for stop in trip.stops:
                    stop_dict = {
                        'trip_id': trip_id,
                        'unique_id': trip.trip_id,
                        'stop_location': stop.location,
                        'stop_datetime': stop.timestamp,
                    }
                    conn.execute(stops_insert_sql, stop_dict)
                trans.commit()
            except Exception as e:
                trans.rollback()
                raise

    def prune(self):

        with self.engine.connect() as conn:
            prune_sql = text(
                """
                DELETE FROM trips
                WHERE created_at < NOW() - INTERVAL 2 DAY
                """
            )
            conn.execute(prune_sql)