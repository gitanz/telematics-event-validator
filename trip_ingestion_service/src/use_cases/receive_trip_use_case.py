from exceptions.exceptions import PushTripToQueueError
from models.Trip import Trip
from utils.queue_utils import QueueUtilInterface


class ReceiveTripUseCase:
    def __init__(self, queue_util: QueueUtilInterface):
        self.queue_util = queue_util

    async def execute(self, trip: Trip) -> bool:
        try:
            await self.queue_util.push(trip)
        except Exception as e:
            raise PushTripToQueueError(str(e))

        return True
