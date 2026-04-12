from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from models.moderator import Location

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

class Stop(BaseModel):
    location: str
    timestamp: str

    @staticmethod
    def from_values(location: str, timestamp: datetime) -> "Stop":
        return Stop(location=location, timestamp=timestamp.strftime(_DATETIME_FORMAT))


class Trip(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    trip_id: str = Field()
    location: Location = Field()
    country: Optional[str] = None
    start: Optional[Stop] = None
    stops: List[Stop] = Field(default_factory=list)
    end: Optional[Stop] = None
