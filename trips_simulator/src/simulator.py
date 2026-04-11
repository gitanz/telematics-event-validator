from config import Config
from trip_faker import TripFaker
from trip_ingestion_service import TripIngestionService


class Simulator:

    def __init__(self, trip_faker: TripFaker, ingestion_service: TripIngestionService):
        self.trip_faker = trip_faker
        self.trip_ingestion_service = ingestion_service

    def execute(self):
        for trip in self.trip_faker.execute():
            self.trip_ingestion_service.queue_trip(trip.to_dict())


if __name__ == "__main__":
    config = Config()
    trip_faker = TripFaker()
    print(f"Starting simulator with the following configuration: {config.to_dict()}")
    trip_ingestion_service = TripIngestionService(config.TRIP_INGESTION_SERVICE_URL)
    simulator = Simulator(trip_faker, trip_ingestion_service)

    simulator.execute()
