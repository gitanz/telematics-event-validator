import pytest
from unittest.mock import AsyncMock

from models.Trip import Trip, Stop
from use_cases.receive_trip_use_case import ReceiveTripUseCase


@pytest.mark.asyncio
async def test_trip_is_pushed_to_queue():
    mock_queue_util = AsyncMock()
    receive_trip_use_case = ReceiveTripUseCase(mock_queue_util)

    trip = Trip(
        trip_id="test_trip_123",
        location="Europe",
        country="Test Country",
        start=Stop(location="Start Location", timestamp="2024-01-01 10:00:00 UTC"),
        stops=[Stop(location="Stop 1", timestamp="2024-01-01 12:00:00 UTC")],
        end=Stop(location="End Location", timestamp="2024-01-01 14:00:00 UTC")
    )

    await receive_trip_use_case.execute(trip)
    mock_queue_util.push.assert_awaited_once_with(trip)
