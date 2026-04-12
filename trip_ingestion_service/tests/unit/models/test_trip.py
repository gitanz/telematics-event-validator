import pytest
from pydantic import ValidationError
from src.models.Trip import Trip, Stop
from datetime import datetime


def test_trip_full_fields():
    stop1 = Stop(location="Europe", timestamp="2024-04-12 10:00:00 UTC")
    stop2 = Stop(location="Europe", timestamp="2024-04-12 12:00:00 UTC")
    trip = Trip(
        trip_id="T123",
        location="Europe",
        country="IE",
        start=stop1,
        stops=[stop1, stop2],
        end=stop2
    )
    assert trip.trip_id == "T123"
    assert trip.location == "Europe"
    assert trip.country == "IE"
    assert trip.start == stop1
    assert trip.stops == [stop1, stop2]
    assert trip.end == stop2

def test_trip_required_fields():
    trip = Trip(trip_id="T456", location="Europe")
    assert trip.trip_id == "T456"
    assert trip.location == "Europe"
    assert trip.country is None
    assert trip.start is None
    assert trip.stops == []
    assert trip.end is None

def test_trip_missing_required_fields():
    with pytest.raises(ValidationError):
        Trip(location="Europe")  # missing trip_id
    with pytest.raises(ValidationError):
        Trip(trip_id="T789")  # missing location

def test_trip_serialization():
    trip = Trip(trip_id="T999", location="Europe")
    data = trip.model_dump()
    assert data["trip_id"] == "T999"
    assert data["location"] == "Europe"
    # Test JSON serialization
    json_str = trip.model_dump_json()
    assert "T999" in json_str
    assert "Europe" in json_str

def test_stop_from_values():
    dt = datetime(2024, 4, 12, 15, 30)
    stop = Stop.from_values("Kilkenny", dt)
    assert stop.location == "Kilkenny"
    assert stop.timestamp.startswith("2024-04-12 15:30:00")
