import json
from urllib.request import urlopen
import re
from datetime import datetime, timezone, timedelta
import sqlite3

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
    get_coord(location: str) -> tuple:
        Retrieves latitude and longitude coordinates for a specified location (city name or zip code).

    get_forecast(lat: float, lon: float, unit: int) -> dict:
        Fetches and processes a 5-day weather forecast from OpenWeather API.

    get_current_weather(lat: float, lon: float, unit: int, weather_data=None) -> dict:
        Fetches and displays current weather conditions for a location.

    display_forecast(location: str, forecast: dict, degree_unit: int) -> None:
        Displays the 5-day forecast in a formatted table.

    convert_timestamp(timezone_offset_seconds: int) -> str:
        Converts a UNIX timestamp with a timezone offset to a readable date and time string.

    insert_to_database(forecast: dict, curr_forecast: dict, location: str, db_cursor: sqlite3.Cursor) -> None:
        Inserts forecast and current weather data into the database.

    find_in_database(location: str, db_cursor: sqlite3.Cursor) -> tuple or None:
        Searches the database for weather data for a specific location.

    degrees_to_compass(degrees: int) -> str:
        Converts a wind direction in degrees to its compass direction.

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

# To get your OpenWeather API key:
# 1. Visit the OpenWeather website: https://openweathermap.org/api
# 2. Create an account or log in if you already have one.
# 3. Go to the "API keys" section and generate a new key.
# 4. Copy the generated API key and paste it in place of 'API KEY GOES HERE' below.
secret = '4f4afd2ca411bb21cb3758cf1b4a4720'
#2nd api key generated and provided for less hassle for the reviewer/grader/professor



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


def get_forecast(lat, lon, unit):
    """
    Retrieves a 5-day weather forecast for a specified latitude and longitude, averaging the weather data for each day.

    Args:
        lat (float): Latitude coordinate of the location.
        lon (float): Longitude coordinate of the location.
        unit (int): Unit system to use (0 for metric, any other number for imperial).

    Returns:
        dict: A dictionary containing the processed 5-day forecast data.
    """
    unit = 'imperial' if int(unit) else 'metric'
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={secret}&units={unit}'
    response = urlopen(url)
    data = response.read()
    forecast = json.loads(data)

    count = 0
    daily_avg = [0, 0, 0, 0, 0]  # Temp, Min, Max, Humidity, Feels Like
    same_day = ''
    forecast_dict = {}

    for day in forecast['list']:
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
            daily_avg[1] = min(daily_avg[1], mininum)
            daily_avg[2] = max(daily_avg[2], maximum)
            daily_avg[3] += humidity
            daily_avg[4] += feels_like
        elif count != 0:
            daily_avg[0] /= count
            daily_avg[3] /= count
            daily_avg[4] /= count
            daily_avg = [int(degree) for degree in daily_avg]
            forecast_dict[same_day] = daily_avg
            daily_avg = [temp, mininum, maximum, humidity, feels_like]
            count = 1
            same_day = date
        else:
            daily_avg = [temp, mininum, maximum, humidity, feels_like]
            same_day = date
            count = 1
    return forecast_dict


def get_current_weather(lat: float, lon: float, unit: int, weather_data=None):
    """
    Retrieves and displays the current weather conditions for a given latitude and longitude.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        unit (int): Unit system (0 for metric, any other number for imperial).
        weather_data (dict, optional): Cached weather data to avoid API calls.

    Returns:
        dict: Current weather data.
    """
    unit = 'imperial' if int(unit) else 'metric'
    speed = 'mph' if unit == 'imperial' else 'm/s'
    temp_unit = 'F' if unit == 'imperial' else 'C'

    if not weather_data:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={unit}&appid={secret}'
        response = urlopen(url)
        data = response.read()
        weather_data = json.loads(data)

    weather_description = weather_data['weather'][0]['description']
    curr_temp = int(weather_data['main']['temp'])
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    wind_degree = weather_data['wind']['deg']
    feels_like = int(weather_data['main']['feels_like'])
    cloud_coverage = weather_data['clouds']['all']
    timezone_offset = weather_data['timezone']
    datetime_str = convert_timestamp(timezone_offset)
    direction = degrees_to_compass(wind_degree)

    print(
        f"{f'{datetime_str}':<36} {f'{curr_temp}°{temp_unit}':<6} {f'{humidity}% humidity':<15} {f'Feels like {feels_like}°{temp_unit}':<8}")
    print(weather_description)
    print(f"{f'Wind Speed: {wind_speed}{speed}':<10}    Direction: {direction}")
    print(f'Cloud Coverage: {cloud_coverage}%\n')
    return weather_data

def display_forecast(location: str, forecast: dict, degree_unit: int):
    """
    Displays the 5-day weather forecast for a specified location in a formatted table.

    Args:
        location (str): The name of the city or location for the forecast.
        forecast (dict): A dictionary containing the processed 5-day forecast data.
        degree_unit (int): Unit system (0 for metric, any other number for imperial).

    Returns:
        None
    """
    temp_unit = 'F' if int(degree_unit) else 'C'
    location = location.replace('_', ' ')
    print(f"\n5-Day Weather Forecast for {location}\n")
    print(
        f"{'Date':<21} {f'Avg Temp (°{temp_unit})':<15} {f'Low (°{temp_unit})':<10} "
        f"{f'High (°{temp_unit})':<10} {'Humidity (%)':<15} {f'Feels Like (°{temp_unit})':<15}")
    print("=" * 94)

    for date, forecast_data in forecast.items():
        date_object = datetime.strptime(date, '%Y-%m-%d')
        day_of_week = date_object.strftime('%A')
        avg_temp, low_temp, high_temp, humidity, feels_like = forecast_data
        print(
            f"{date:<12} {day_of_week:<9} {avg_temp:<15} {low_temp:<10} {high_temp:<10} "
            f"{humidity:<15} {feels_like:<15}")
        print("=" * 94)
    print()


def convert_timestamp(timezone_offset_seconds: int):
    """
    Converts a UNIX timestamp with a timezone offset to a readable date and time string.

    Args:
        timezone_offset_seconds (int): The timezone offset in seconds.

    Returns:
        str: The converted date and time string in RFC 2822 format.
    """
    now_utc = datetime.now(tz=timezone.utc)
    tz = timezone(timedelta(seconds=timezone_offset_seconds))
    dt_with_timezone = now_utc.astimezone(tz)
    return dt_with_timezone.strftime('%a, %d %b %Y %H:%M:%S UTC%z')


def insert_to_database(forecast: dict, curr_forecast: dict, location: str, db_cursor: sqlite3.Cursor):
    """
    Inserts forecast and current weather data into the database.

    Args:
        forecast (dict): The 5-day forecast data.
        curr_forecast (dict): The current weather data.
        location (str): The name of the location.
        db_cursor (sqlite3.Cursor): The database cursor.

    Returns:
        None
    """
    forecast_json = json.dumps(forecast)
    curr_forecast_json = json.dumps(curr_forecast)
    db_cursor.execute('''INSERT OR IGNORE INTO weather (location, forecast, current_forecast) VALUES (?,?,?)''',
                      (location, forecast_json, curr_forecast_json))


def find_in_database(location: str, db_cursor: sqlite3.Cursor):
    """
    Searches the database for weather data for a specific location.

    Args:
        location (str): The name of the location to search for.
        db_cursor (sqlite3.Cursor): The database cursor.

    Returns:
        tuple or None: A tuple containing the forecast and current weather data, or None if not found.
    """
    db_cursor.execute('''SELECT forecast, current_forecast FROM weather WHERE location = ?''', (location,))
    result = db_cursor.fetchone()

    if result is None:
        return None
    else:
        forecast_json = result[0]
        forecast_data = json.loads(forecast_json)
        current_forecast_json = result[1]
        current_forecast_data = json.loads(current_forecast_json)
        return forecast_data, current_forecast_data


def degrees_to_compass(degrees: int):
    """
    Converts a wind direction in degrees to its corresponding compass direction.

    Args:
        degrees (int): The wind direction in degrees.

    Returns:
        str: The compass direction (e.g., 'N', 'NE', 'E').
    """
    degrees = degrees % 360

    if degrees >= 0 and degrees < 22.5:
        return "N"
    elif degrees >= 22.5 and degrees < 45:
        return "NE"
    elif degrees >= 45 and degrees < 67.5:
        return "ENE"
    elif degrees >= 67.5 and degrees < 90:
        return "E"
    elif degrees >= 90 and degrees < 112.5:
        return "ESE"
    elif degrees >= 112.5 and degrees < 135:
        return "SE"
    elif degrees >= 135 and degrees < 157.5:
        return "SSE"
    elif degrees >= 157.5 and degrees < 180:
        return "S"
    elif degrees >= 180 and degrees < 202.5:
        return "SSW"
    elif degrees >= 202.5 and degrees < 225:
        return "SW"
    elif degrees >= 225 and degrees < 247.5:
        return "WSW"
    elif degrees >= 247.5 and degrees < 270:
        return "W"
    elif degrees >= 270 and degrees < 292.5:
        return "WNW"
    elif degrees >= 292.5 and degrees < 315:
        return "NW"
    elif degrees >= 315 and degrees < 337.5:
        return "NNW"
    else:
        return "N"


if __name__ == '__main__':
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS weather (location TEXT PRIMARY KEY, forecast TEXT, current_forecast TEXT)''')
    conn.commit()

    while True:
        unit = input('Enter 0 for Metric or any other number for Imperial: ')
        if unit == 'quit':
            conn.close()
            exit()
        try:
            int(unit)
            break
        except ValueError:
            print('Invalid input, try again.')

    while True:
        city = input('Select a City: ')
        city = city.replace(' ', '_')

        if city == 'quit':
            conn.close()
            exit()

        try:
            saved_weather = find_in_database(city, cursor)
            if saved_weather is None:
                lat, lon = get_coord(city)
                forecast_data = get_forecast(lat, lon, unit)
                display_forecast(city, forecast_data, unit)
                curr_forecast_data = get_current_weather(lat, lon, unit)
                insert_to_database(forecast_data, curr_forecast_data, city, cursor)
                conn.commit()
            else:
                forecast_data, curr_forecast_data = saved_weather
                display_forecast(city, forecast_data, unit)
                get_current_weather(lat, lon, unit, weather_data=curr_forecast_data)
                print("Data retrieved from database!")
        except Exception as e:
            print(f'Invalid location entered, try again. ({e})')
