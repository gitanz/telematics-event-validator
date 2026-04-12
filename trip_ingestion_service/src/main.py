from fastapi import FastAPI

from exceptions.exceptions import PushTripToQueueError
from models.Trip import Trip
from use_cases.receive_trip_use_case import ReceiveTripUseCase
from utils.queue_utils import QueueUtilFactory, QueueUtilInterface
from config import queue_config

app = FastAPI()

@app.post("/v1/webhook/trips", status_code=201)
async def queue_trip(trip: Trip):
    queue_util: QueueUtilInterface = await QueueUtilFactory(queue_config=queue_config).getQueueUtil()
    accept_trip_use_case = ReceiveTripUseCase(queue_util)

    try:
        await accept_trip_use_case.execute(trip)
    except PushTripToQueueError as e:
        return { "error": str(e) }

    return { "message": "Trip received"}
