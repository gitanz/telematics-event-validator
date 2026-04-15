import asyncio
import logging

from config import QueueConfig
from queue_utils import QueueUtilInterface, QueueUtilFactory
from trip_faker import TripFaker


class Simulator:

    def __init__(self, trip_faker: TripFaker, queue_util: QueueUtilInterface):
        self.trip_faker = trip_faker
        self.queue_util = queue_util

    async def execute(self):
        for trip in self.trip_faker.execute():
            await self.queue_util.push(trip)
            logging.info('queued')
            print('queued')



async def run_simulator(trip_faker: TripFaker, queue_config: QueueConfig):
    queue_util = await QueueUtilFactory(queue_config).getQueueUtil()
    simulator = Simulator(trip_faker, queue_util)
    logging.info("Starting simulation...")
    print("Starting simulation...")
    await simulator.execute()


if __name__ == "__main__":
    trip_faker = TripFaker()
    config = QueueConfig()
    asyncio.run(run_simulator(trip_faker, config))
