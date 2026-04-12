from enum import Enum
from pydantic import BaseModel

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

class Location(str, Enum):
    north_america = "North America"
    europe = "Europe"
    asia = "Asia"
    south_america = "South America"
    africa = "Africa"
    oceania = "Oceania"

class Moderator(BaseModel):
    moderator_id: int
    location: Location
