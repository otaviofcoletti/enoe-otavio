CREATE TABLE IF NOT EXISTS ultrassonic (
    epoch VARCHAR(30) PRIMARY KEY,
    distance_cm VARCHAR(30) NOT NULL
);

CREATE TABLE IF NOT EXISTS images (
    epoch VARCHAR(30) PRIMARY KEY,
    image_path VARCHAR(120) NOT NULL
);


CREATE TABLE IF NOT EXISTS raspberry_info (
    epoch VARCHAR(30) PRIMARY KEY,
    cpu_temperature FLOAT NOT NULL,
    cpu_usage FLOAT NOT NULL,
    ram_usage FLOAT NOT NULL,
    storage_usage FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS weather (
    epoch VARCHAR(30) PRIMARY KEY,
    current_temperature_2m FLOAT NOT NULL,
    current_relative_humidity_2m FLOAT NOT NULL,
    current_apparent_temperature FLOAT NOT NULL,
    current_is_day FLOAT NOT NULL,
    current_precipitation FLOAT NOT NULL,
    current_rain FLOAT NOT NULL,
    current_showers FLOAT NOT NULL,
    current_weather_code FLOAT NOT NULL,
    current_cloud_cover FLOAT NOT NULL,
    current_pressure_msl FLOAT NOT NULL,
    current_surface_pressure FLOAT NOT NULL,
    current_wind_speed_10m FLOAT NOT NULL,
    current_wind_direction_10m FLOAT NOT NULL,
    current_wind_gusts_10m FLOAT NOT NULL
);
