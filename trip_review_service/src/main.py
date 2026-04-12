import logging
import traceback

from fastapi import FastAPI, Request, HTTPException, Depends, Header

from config import DatabaseConfig
from connections.database_connection import DatabaseConnection
from exceptions.login_exceptions import LoginException
from exceptions.trip_exceptions import TripNotFoundException, UnauthorizedTripException
from models.moderator import Moderator
from repositories.moderator_repository import MySQLModeratorRepository
from repositories.trip_repository import MySQLTripRepository
from use_cases.acknowledge_trip import AcknowledgeTripUseCase
from use_cases.claim_trip import ClaimTripUseCase
from use_cases.list_trips import ListTripsUseCase
from use_cases.login import LoginUseCase
from use_cases.review_trip import ReviewTripUseCase
from utils.jwt_utils import decode_jwt_token


def authorize_request(authorization: str = Header(...)) -> Moderator:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.split(" ", 1)[1]

    try:
        jwt_payload = decode_jwt_token(token)
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")

    connection = DatabaseConnection(DatabaseConfig()).connection
    moderator_repository = MySQLModeratorRepository(connection=connection)

    try:
        moderator = moderator_repository.get_moderator(jwt_payload['moderator_id'], jwt_payload['location'])
    finally:
        connection.close()

    if moderator is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return moderator

app = FastAPI()

@app.post("/v1/login")
async def login(request: Request):
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

    return { "token": jwt }

@app.get("/v1/trips")
async def trips(moderator: Moderator=Depends(authorize_request)):
    connection = DatabaseConnection(DatabaseConfig()).connection
    trip_repository = MySQLTripRepository(connection=connection)
    list_trip_use_case = ListTripsUseCase(trip_repository)
    try:
        trips = list_trip_use_case.execute(moderator.location.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return { "trips": [trip.model_dump() for trip in trips ] }

@app.get("/v1/trips/{trip_id}")
async def trip(trip_id: str, moderator: Moderator=Depends(authorize_request)):
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
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        connection.close()

    return { "trip": trip.model_dump() }

@app.patch("/v1/trips/{trip_id}/claim")
async def claim(trip_id: str, moderator: Moderator=Depends(authorize_request)):
    connection = DatabaseConnection(DatabaseConfig()).connection
    trip_repository = MySQLTripRepository(connection=connection)
    claim_trip_use_case = ClaimTripUseCase(trip_repository)
    try:
        claim_success = claim_trip_use_case.execute(trip_id, moderator)
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

@app.patch("/v1/trips/{trip_id}/acknowledge")
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
