class TripNotFoundException(Exception):
    """Raised when a trip is not found in the database."""
    pass

class UnauthorizedTripException(Exception):
    """Raised when a moderator tries to access a trip they are not authorized to review."""
    pass