import uuid
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"


@dataclass
class Stop:
    name: str
    timestamp: str

    @staticmethod
    def from_values(name: str, timestamp: datetime) -> "Stop":
        return Stop(name=name, timestamp=timestamp.strftime(_DATETIME_FORMAT))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "timestamp": self.timestamp
        }


@dataclass
class Trip:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    location: str = ''
    country: Optional[str] = None
    start: Optional[Stop] = None
    stops: List[Stop] = field(default_factory=list)
    end: Optional[Stop] = None

    def set_country(self, country: str) -> None:
        self.country = country

    def set_start(self, start: Stop) -> None:
        self.start = start

    def add_stop(self, stop: Stop) -> None:
        self.stops.append(stop)

    def set_end(self, end: Stop) -> None:
        self.end = end

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "location": self.location,
            "country": self.country,
            "start": self.start.to_dict() if self.start else None,
            "stops": [stop.to_dict() for stop in self.stops],
            "end": self.end.to_dict() if self.end else None
        }
