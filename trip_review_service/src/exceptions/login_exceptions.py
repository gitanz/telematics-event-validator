class LoginException(Exception):
    def __init__(self, message: str = "User/location not found") -> None:
        super().__init__(message)