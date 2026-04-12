from typing import List
from models.trip import Trip
from repositories.trip_repository import TripRepositoryInterface

class ListTripsUseCase:
    def __init__(self, trip_repository: TripRepositoryInterface):
        self.trip_repository = trip_repository

    def execute(self, location: str) -> List[Trip]:
        return self.trip_repository.list_trips(location)
