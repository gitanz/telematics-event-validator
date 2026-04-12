import requests

class TripIngestionService:
    service_url: str
    def __init__(self, service_url: str):
        self.service_url = service_url

    def queue_trip(self, trip_data: dict):
        requests.post(self.service_url + "/v1/webhook/trip", json=trip_data)
