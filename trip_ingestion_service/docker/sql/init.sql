CREATE DATABASE IF NOT EXISTS trips;
USE trips;

CREATE TABLE IF NOT EXISTS trips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unique_id VARCHAR(255) NOT NULL,
    location ENUM('North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania') NULL,
    country VARCHAR(255) NULL,
    start_location VARCHAR(255) NULL,
    start_datetime DATETIME NULL,
    end_location VARCHAR(255) NULL,
    end_datetime DATETIME NULL
);

CREATE INDEX idx_location_country ON trips(location, country);
CREATE INDEX idx_unique_id ON trips(unique_id);

CREATE TABLE IF NOT EXISTS trip_stops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    unique_id VARCHAR(255) NOT NULL,
    stop_location VARCHAR(255) NOT NULL,
    stop_datetime DATETIME NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);

CREATE INDEX idx_trip_id ON trip_stops(trip_id);

CREATE TABLE IF NOT EXISTS moderators (
    moderator_id INT AUTO_INCREMENT PRIMARY KEY,
    location ENUM('North America', 'Europe', 'Asia', 'South America', 'Africa', 'Oceania') NOT NULL
) AUTO_INCREMENT=10001;

-- seed 5 moderators for each of the 6 locations, total 30 moderators
INSERT INTO moderators (location) VALUES
    ('North America'), ('North America'), ('North America'), ('North America'), ('North America'),
    ('Europe'), ('Europe'), ('Europe'), ('Europe'), ('Europe'),
    ('Asia'), ('Asia'), ('Asia'), ('Asia'), ('Asia'),
    ('South America'), ('South America'), ('South America'), ('South America'), ('South America'),
    ('Africa'), ('Africa'), ('Africa'), ('Africa'), ('Africa'),
    ('Oceania'), ('Oceania'), ('Oceania'), ('Oceania'), ('Oceania');
