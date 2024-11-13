import json
import urllib
from urllib.request import urlopen
import re

"""
weather.py

This module retrieves and displays a 5-day weather forecast for a specified city or zip code using the OpenWeather API.
The forecast includes temperature, weather conditions, and other relevant details for each day, and the information
is printed in a readable format on the console.

Requirements:
    - json module
    - requests module
    - An API key from OpenWeather: https://openweathermap.org/appid

Functions:
    get_coord(location: str) -> dict:
        Retrieves the 5-day weather forecast data from OpenWeather API for the given location (city name or zip code).

    parse_forecast_data(data: dict) -> list:
        Processes the raw data received from OpenWeather API and organizes it into a structured list of daily forecasts.

    display_forecast(forecast: list) -> None:
        Prints the 5-day forecast in a user-friendly format on the console.

Usage:
    1. Set your OpenWeather API key as an environment variable or directly within the code.
    2. Run the script and enter the city name or zip code when prompted to view the 5-day forecast.

Example:
    $ python weather.py
    Enter city or zip code: London
    Forecast for London:
    Day 1: [Weather details...]
    Day 2: [Weather details...]
    ...
"""
secret = 'API KEY GOES HERE'

def get_coord(location):
    """
    Retrieves latitude and longitude coordinates for a given location.

    Args:
        location (str): The name of the city or location for which to retrieve coordinates.

    Returns:
        tuple: A tuple containing the latitude (float) and longitude (float) of the specified location.
    """
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={location}&limit={1}&appid={secret}'
    response = urlopen(url)
    data = response.read()
    weather_data = json.loads(data)
    lat = weather_data[0]['lat']
    lon = weather_data[0]['lon']
    return lat, lon


def get_forecast(lat, lon):
    """
    Retrieves a 5-day weather forecast for a specified latitude and longitude, averaging the weather data for each day.

    Args:
        lat (float): Latitude coordinate of the location.
        lon (float): Longitude coordinate of the location.

    Returns:
        list: A list of dictionaries, each containing the average daily temperature, minimum temperature,
              maximum temperature, humidity, and 'feels like' temperature over 5 days.
    """
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={secret}'
    response = urlopen(url)
    data = response.read()
    forecast_data = json.loads(data)
    three_hour_forecast = []
    count = 0
    daily_avg = [0, 0, 0, 0, 0]
    same_day = ''
    same_day_count = 0
    forecast_list = []
    for day in forecast_data['list']:
        temp_info = day['main']
        dt = day['dt_txt']
        match = re.search(r"\d{4}-(\d{1,2})-(\d{1,2})", dt)
        date = match.group()
        temp = temp_info['temp']
        mininum = temp_info['temp_min']
        maximum = temp_info['temp_max']
        humidity = temp_info['humidity']
        feels_like = temp_info['feels_like']

        if date == same_day:
            count += 1
            daily_avg[0] += temp
            daily_avg[1] += mininum
            daily_avg[2] += maximum
            daily_avg[3] += humidity
            daily_avg[4] += feels_like
        elif count != 0:
            daily_avg[0] /= count
            daily_avg[1] /= count
            daily_avg[2] /= count
            daily_avg[3] /= count
            daily_avg[4] /= count
            forecast_list.append(daily_avg)
            daily_avg = [0, 0, 0, 0, 0]  # Reset averages
            count = 0

            same_day = date
    return forecast_list


if __name__ == '__main__':
   lat, lon = get_coord('boston')
   print(get_forecast(lat, lon))
