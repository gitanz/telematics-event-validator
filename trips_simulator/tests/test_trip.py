import os
from datetime import datetime

from src.trip import Stop, Trip


def test_stop_creation():
    stop = Stop.from_values(name="TestStop", timestamp=datetime(2026, 4, 11, 12, 0, 0))
    assert stop.name == "TestStop"
    assert stop.timestamp.startswith("2026-04-11 12:00:00")


def test_trip_creation():
    print(os.getenv('APP_ENV'))
    trip = Trip(location="Europe")
    assert trip.id is not None
    assert isinstance(trip.id, str)
    assert trip.location == "Europe"
    assert trip.country is None
    assert trip.start is None
    assert isinstance(trip.stops, list)
    assert trip.stops == []
    assert trip.end is None

def test_trip_setters():
    trip = Trip(location="Europe")
    trip.set_country("Germany")
    assert trip.country == "Germany"

    start_stop = Stop.from_values(name="StartStop", timestamp=datetime(2026, 4, 11, 8, 0, 0))
    trip.set_start(start_stop)
    assert trip.start == start_stop

    stop1 = Stop.from_values(name="Stop1", timestamp=datetime(2026, 4, 11, 10, 0, 0))
    stop2 = Stop.from_values(name="Stop2", timestamp=datetime(2026, 4, 11, 11, 0, 0))
    trip.add_stop(stop1)
    trip.add_stop(stop2)
    assert trip.stops == [stop1, stop2]

    end_stop = Stop.from_values(name="EndStop", timestamp=datetime(2026, 4, 11, 18, 0, 0))
    trip.set_end(end_stop)
    assert trip.end == end_stop