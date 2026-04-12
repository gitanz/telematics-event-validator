from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


class Continent(str, Enum):
    north_america = "North America"
    europe = "Europe"
    asia = "Asia"
    south_america = "South America"
    africa = "Africa"
    oceania = "Oceania"


class Stop(BaseModel):
    location: str
    timestamp: str

    @staticmethod
    def from_values(location: str, timestamp: datetime) -> "Stop":
        return Stop(location=location, timestamp=timestamp.strftime(_DATETIME_FORMAT))


class Trip(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    trip_id: str = Field()
    location: Continent = Field()
    country: Optional[str] = None
    start: Optional[Stop] = None
    stops: List[Stop] = Field(default_factory=list)
    end: Optional[Stop] = None
