import json

import jwt
from datetime import datetime, timedelta, UTC
from typing import Dict
from config import jwt_config
from models.moderator import Moderator


def create_jwt_token(moderator: Moderator) -> str:
    expire = datetime.now(UTC) + timedelta(seconds=jwt_config.jwt_expire_seconds)
    payload: Dict = {
        "moderator_id": moderator.moderator_id,
        "location": moderator.location.value,
        "exp": expire.timestamp()
    }
    token = jwt.encode(payload, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    return token


def decode_jwt_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
