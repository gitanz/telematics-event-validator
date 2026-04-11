import random
import time
from typing import Generator
from faker import Faker
from trip import Trip, Stop


class TripFaker:
    def execute(self) -> Generator[Trip, None, None]:
        while True:
            faker = Faker(random.choice(["en_US", "de_DE", "fr_FR", "es_ES"]))

            trip: Trip = Trip(
                location=random.choice(["North America", "Europe", "Asia", "South America", "Africa", "Oceania"]))
            trip.set_country(faker.country())
            trip.set_start(Stop.from_values(name=faker.city(), timestamp=faker.date_time_this_year()))
            for _ in range(random.randint(3, 5)):
                trip.add_stop(Stop.from_values(name=faker.city(), timestamp=faker.date_time_this_year()))

            trip.set_end(Stop.from_values(name=faker.city(), timestamp=faker.date_time_this_year()))

            yield trip
            time.sleep(1)
