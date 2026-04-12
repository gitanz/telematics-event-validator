from fastapi import FastAPI, Request, HTTPException

from connections.database_connection import connection
from exceptions.login_exceptions import LoginException
from repositories.moderator_repository import MySQLModeratorRepository
from use_cases.login import LoginUseCase

app = FastAPI()

@app.get("/v1/login")
async def login(request: Request):
    body = await request.json()
    moderator_id = body.get("moderator_id")
    location = body.get("location")

    moderator_repository = MySQLModeratorRepository(connection=connection)
    login_use_case = LoginUseCase(moderator_repository)
    try:
        jwt = login_use_case.execute(moderator_id, location)
    except LoginException as e:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    return { "token": jwt }
