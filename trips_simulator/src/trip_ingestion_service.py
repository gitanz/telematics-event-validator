import requests

class TripIngestionService:
    service_url: str
    def __init__(self, service_url: str):
        self.service_url = service_url

    def queue_trip(self, trip_data: dict):
        requests.post(self.service_url + "/webhook/trips", json=trip_data)
