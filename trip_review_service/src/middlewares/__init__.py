from fastapi import Request, HTTPException

from config import DatabaseConfig
from connections.database_connection import DatabaseConnection
from models.moderator import Moderator
from repositories.moderator_repository import MySQLModeratorRepository
from utils.jwt_utils import decode_jwt_token

def get_token(request: Request) -> str:
    token = request.cookies.get("authToken")
    if token:
        return token

    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return authorization.split(" ", 1)[1]

def authorize_request(request: Request) -> Moderator:
    token = get_token(request)

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
