import logging

from time import sleep

from repositories.repository import TripRepository


class Pruner:
    def __init__(self, trip_repository: TripRepository):
        self.trip_repository = trip_repository

    def execute(self):
        while True:
            self.trip_repository.prune()
            logging.info("Pruning completed. Next pruning in 1 hour.")
            sleep(3600)


if __name__ == "__main__":
    from config import database_config
    from repositories.repository import MySQLTripRepository

    trip_repository = MySQLTripRepository(database_config)
    pruner = Pruner(trip_repository)
    pruner.execute()
