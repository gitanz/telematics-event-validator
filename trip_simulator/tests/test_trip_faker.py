from trip import Trip, Stop
from trip_faker import TripFaker


def test_trip_faker_yields_valid_trip():

    trip_faker = TripFaker()
    trip_generator = trip_faker.execute()

    # Get the first generated trip
    trip = next(trip_generator)

    assert isinstance(trip, Trip)
    assert trip.trip_id is not None
    assert trip.location is not None
    assert isinstance(trip.start, Stop)
    assert trip.stops
    assert isinstance(trip.stops[0], Stop)
    assert isinstance(trip.end, Stop)
    assert trip.country is not None
