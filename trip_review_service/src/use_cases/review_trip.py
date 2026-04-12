from exceptions.trip_exceptions import TripNotFoundException
from models.moderator import Moderator
from repositories.trip_repository import TripRepositoryInterface


class ReviewTripUseCase:
    def __init__(self, trip_repository: TripRepositoryInterface):
        self.trip_repository = trip_repository

    def execute(self, trip_id: str, moderator: Moderator):
        trip = self.trip_repository.get_trip(
            trip_id=trip_id,
            location=moderator.location.value
        )

        if not trip:
            raise TripNotFoundException("Trip not found")

        return trip
