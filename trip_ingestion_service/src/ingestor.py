import logging
from time import sleep
from typing import List, Union

from config import queue_config, database_config
from models import Trip
from repositories.repository import TripRepository, MySQLTripRepository
from utils.queue_utils import QueueUtilFactory, QueueUtilInterface
import asyncio

class Ingestor:
    def __init__(self, queue_util: QueueUtilInterface, trip_repository: TripRepository):
        self.queue_util = queue_util
        self.trip_repository = trip_repository

    async def ingest_trips(self):

        while True:
            trip: Union[Trip, None] = await self.queue_util.pop()
            if trip:
                self.trip_repository.insert(trip)
            logging.info('OK: Trip ingested successfully')
            await asyncio.sleep(1)

async def run_ingestor():
    queue_util: QueueUtilInterface = await QueueUtilFactory(queue_config).getQueueUtil()
    trip_repository: TripRepository = MySQLTripRepository(database_config)

    ingestor = Ingestor(queue_util, trip_repository)
    await ingestor.ingest_trips()

if __name__ == "__main__":
    asyncio.run(run_ingestor())
