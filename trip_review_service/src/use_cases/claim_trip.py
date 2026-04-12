from exceptions.trip_exceptions import TripNotFoundException
from models.moderator import Moderator
from repositories.trip_repository import TripRepositoryInterface


class ClaimTripUseCase:
    def __init__(self, trip_repository: TripRepositoryInterface):
        self.trip_repository = trip_repository

    def execute(self, trip_id: str, moderator: Moderator):
        try:
            return self.trip_repository.claim_trip(trip_id, moderator)
        except Exception as e:
            raise e
