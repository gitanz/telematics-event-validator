from models.moderator import Moderator
from repositories.trip_repository import TripRepositoryInterface
from utils.queue_utils import QueueUtilInterface


class ClaimTripUseCase:
    def __init__(self, trip_repository: TripRepositoryInterface, queue_util: QueueUtilInterface):
        self.trip_repository = trip_repository
        self.queue_util = queue_util

    async def execute(self, trip_id: str, moderator: Moderator):
        try:
            self.trip_repository.claim_trip(trip_id, moderator)
            trip = self.trip_repository.get_trip(trip_id, moderator)
            await self.queue_util.push_claim(trip)

        except Exception as e:
            raise e
