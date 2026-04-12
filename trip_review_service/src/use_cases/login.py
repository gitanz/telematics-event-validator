from exceptions.login_exceptions import LoginException
from models.moderator import Location
from repositories.moderator_repository import ModeratorRepositoryInterface
from utils import jwt_utils


class LoginUseCase:
    def __init__(self, moderator_repository: ModeratorRepositoryInterface):
        self.moderator_repository = moderator_repository

    def execute(self, moderator_id: int, location: str) -> str:
        location = Location(location)
        moderator = self.moderator_repository.get_moderator(moderator_id, location)
        if moderator:
            return jwt_utils.create_jwt_token(moderator)
        else:
            raise LoginException()
