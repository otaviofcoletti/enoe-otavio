import openmeteo_requests
import json
import requests_cache
import pandas as pd
from retry_requests import retry
from DatabaseHandler import DatabaseHandler
from LoggingClass import Logger  # Import the Logger class
import time

def load_config():
    with open("config.json") as f:
        return json.load(f)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -22.0175, # Latitude of Sao Carlos
	"longitude": -47.8908, # Longitude of Sao Carlos
	"current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "rain", "showers", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
	"timezone": "America/Sao_Paulo"
}
def main():
    config = load_config()
    db_config = config["DATABASE"]

    username = config["CREDENTIALS"]["username"]
    password = config["CREDENTIALS"]["password"]

    db_handler = DatabaseHandler(db_config)
    db_handler.connect()

    # Configuração do logger para o DatabaseHandler usando a nova classe Logger
    main_logger = Logger('main', rotation='W0').get_logger()  # Weekly rotation

    while True:
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()

        db_handler.insert_data('weather', current.Time(), current) 

        time.sleep(600) # Sleep for 10 minutes

main()
