from src.trip_ingestion_service import TripIngestionService


def test_queue_trip_method_invokes_the_webhook_url(mocker):
    service_url = "http://example.com/"
    trip_ingestion_service = TripIngestionService(service_url)

    mock_post = mocker.patch("requests.post")

    trip_data = {"trip_id": 123, "driver_id": 456, "start_time": "2024-01-01T08:00:00Z"}
    trip_ingestion_service.queue_trip(trip_data)

    mock_post.assert_called_once_with(service_url + "/webhook/trips", json=trip_data)
