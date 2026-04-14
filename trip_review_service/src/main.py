import asyncio
import json
import logging
import traceback
from datetime import datetime, timezone, timedelta

from aio_pika import IncomingMessage
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, StreamingResponse

from config import DatabaseConfig, jwt_config, QueueConfig
from connections.database_connection import DatabaseConnection
from exceptions.login_exceptions import LoginException
from exceptions.trip_exceptions import TripNotFoundException, UnauthorizedTripException
from middlewares import authorize_request
from models.moderator import Moderator
from repositories.moderator_repository import MySQLModeratorRepository
from repositories.trip_repository import MySQLTripRepository
from use_cases.acknowledge_trip import AcknowledgeTripUseCase
from use_cases.claim_trip import ClaimTripUseCase
from use_cases.list_trips import ListTripsUseCase
from use_cases.login import LoginUseCase
from use_cases.review_trip import ReviewTripUseCase
from utils.queue_utils import QueueUtilFactory

app = FastAPI()

origins = [
    "http://localhost:4200",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/login")
async def login(request: Request, response: Response):
    body = await request.json()
    moderator_id = body.get("moderator_id")
    location = body.get("location")
    connection = DatabaseConnection(DatabaseConfig()).connection
    moderator_repository = MySQLModeratorRepository(connection=connection)
    login_use_case = LoginUseCase(moderator_repository)
    try:
        jwt = login_use_case.execute(moderator_id, location)
    except LoginException as e:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    response.set_cookie(
        key="authToken",
        httponly=True,
        value=jwt,
        path='/',
        max_age=jwt_config.jwt_expire_seconds,
        samesite="none",
        secure=True
    )

    return { "token": jwt }

@app.post("/api/v1/logout")
async def logout(response: Response):
    response.set_cookie(key="authToken", path='/', expires=datetime.now(timezone.utc) - timedelta(seconds=jwt_config.jwt_expire_seconds))
    return { "message": "Logged out successfully" }

@app.get("/api/v1/trips")
async def trips(moderator: Moderator=Depends(authorize_request)):
    print(moderator.moderator_id)
    connection = DatabaseConnection(DatabaseConfig()).connection
    trip_repository = MySQLTripRepository(connection=connection)
    list_trip_use_case = ListTripsUseCase(trip_repository)
    try:
        trips = list_trip_use_case.execute(moderator)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return {
        "trips": [
            {
                "tripId": trip.trip_id,
                "location": trip.location.value,
                "startLocation": trip.start.location,
                "startTimestamp": trip.start.timestamp,
                "endLocation": trip.end.location,
                "endTimestamp": trip.end.timestamp,
            }

            for trip in trips
        ]
    }

@app.get("/api/v1/trips/{trip_id}")
async def trip(trip_id: str, moderator: Moderator=Depends(authorize_request)):
    print(moderator.moderator_id)
    connection = DatabaseConnection(DatabaseConfig()).connection

    trip_repository = MySQLTripRepository(connection=connection)
    review_trip_use_case = ReviewTripUseCase(trip_repository)

    try:
        trip = review_trip_use_case.execute(trip_id, moderator)
    except TripNotFoundException as e:
        raise HTTPException(status_code=404, detail="Trip not found")
    except UnauthorizedTripException as e:
        raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return {
        "tripId": trip.trip_id,
        "location": trip.location.value,
        "startLocation": trip.start.location,
        "startTimestamp": trip.start.timestamp,
        "stops": trip.stops,
        "endLocation": trip.end.location,
        "endTimestamp": trip.end.timestamp,
        "claimedBy": trip.claimed_by,
        "claimedAt": trip.claimed_at,
        "acknowledgedBy": trip.acknowledged_by,
        "acknowledgedAt": trip.acknowledged_at,
    }


@app.patch("/api/v1/trips/{trip_id}/claim")
async def claim(trip_id: str, moderator: Moderator=Depends(authorize_request)):
    connection = DatabaseConnection(DatabaseConfig()).connection
    trip_repository = MySQLTripRepository(connection=connection)
    queue_util = await QueueUtilFactory(QueueConfig()).getQueueUtil()
    claim_trip_use_case = ClaimTripUseCase(trip_repository, queue_util)
    try:
        claim_success = await claim_trip_use_case.execute(trip_id, moderator)
    except TripNotFoundException as e:
        raise HTTPException(status_code=404, detail="Trip not found")
    except UnauthorizedTripException as e:
        logging.debug(str(e))
        raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return { "success": True if claim_success else False }

@app.patch("/api/v1/trips/{trip_id}/acknowledge")
async def acknowledge(trip_id: str, moderator=Depends(authorize_request)):
    connection = DatabaseConnection(DatabaseConfig()).connection
    trip_repository = MySQLTripRepository(connection=connection)
    acknowledge_trip_use_case = AcknowledgeTripUseCase(trip_repository)

    try:
        acknowledge_success = acknowledge_trip_use_case.execute(trip_id, moderator)
    except TripNotFoundException as e:
        raise HTTPException(status_code=404, detail="Trip not found")
    except UnauthorizedTripException as e:
        logging.debug(str(e))
        raise HTTPException(status_code=403, detail="Forbidden")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return { "success": True if acknowledge_success else False }

@app.get("/api/v1/events")
async def events(moderator=Depends(authorize_request)):
    queue_util = await QueueUtilFactory(QueueConfig()).getQueueUtil()
    async def event_generator():
        while True:
            message: IncomingMessage = await queue_util.pop()
            if message is None:
                continue

            event = json.loads(message.body)

            if  event["event"] == "claim" and event["trip"]["claimed_by"] == moderator.moderator_id:
                await message.nack(requeue=True)
                continue

            response = {
                "event": event["event"],
                "tripId": event["trip"]["trip_id"],
            }

            yield f"data: {json.dumps(response)}\n\n"
            await message.ack()
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


