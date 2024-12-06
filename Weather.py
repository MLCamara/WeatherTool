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


def get_forecast(lat, lon, unit):
    """
    Retrieves a 5-day weather forecast for a specified latitude and longitude, averaging the weather data for each day.

    Args:
        lat (float): Latitude coordinate of the location.
        lon (float): Longitude coordinate of the location.

    Returns:
        list: A list of dictionaries, each containing the average daily temperature, minimum temperature,
              maximum temperature, humidity, and 'feels like' temperature over 5 days.
    """
    if int(unit):
        unit = 'imperial'
    else:
        unit = 'metric'
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={secret}&units={unit}'
    response = urlopen(url)
    data = response.read()
    forecast = json.loads(data)

    count = 0  # keeps track of same_day forecast count
    daily_avg = [0, 0, 0, 0, 0]
    same_day = ''  # empty string (placeholder)
    forecast_dict = {}

    for day in forecast['list']:
        temp_info = day['main']
        dt = day['dt_txt']  # dateTime of forecast
        match = re.search(r"\d{4}-(\d{1,2})-(\d{1,2})", dt)  # parses the YY-MM-DD
        date = match.group()
        temp = temp_info['temp']
        mininum = temp_info['temp_min']
        maximum = temp_info['temp_max']
        humidity = temp_info['humidity']
        feels_like = temp_info['feels_like']

        if date == same_day:  # adds the forecasted temperature to daily avg if forecasted on same day as previous forecast
            count += 1
            daily_avg[0] += temp

            if mininum < daily_avg[1]:
                daily_avg[1] = mininum

            if maximum > daily_avg[2]:
                daily_avg[2] = maximum

            daily_avg[3] += humidity
            daily_avg[4] += feels_like
        elif count != 0:  # finds the average of a 1-day forcast temperature, appends to forecast_dict and changes daily_avg and same_day with new forecast data
            daily_avg[0] /= count
            daily_avg[3] /= count
            daily_avg[4] /= count

            daily_avg = [int(degree) for degree in daily_avg]
            forecast_dict[same_day] = daily_avg
            daily_avg = [temp, mininum, maximum, humidity, feels_like]  # Reset averages
            count = 1
            same_day = date
        else:
            daily_avg = [temp, mininum, maximum, humidity, feels_like]
            same_day = date
            count = 1
    return forecast_dict


def get_current_weather(lat: float, lon: float, unit: int, weather_data=None):
    if int(unit):
        unit = 'imperial'
        speed = 'mph/hr'
        temp_unit = 'F'
    else:
        unit = 'metric'
        speed = 'm/s'
        temp_unit = 'C'

    if not weather_data:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units={unit}&appid={secret}'
        response = urlopen(url)
        data = response.read()
        weather_data = json.loads(data)

    weather_description = weather_data['weather'][0]['description']
    curr_temp = weather_data['main']['temp']
    curr_temp = int(curr_temp)
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    wind_degree = weather_data['wind']['deg']
    feels_like = weather_data['main']['feels_like']
    feels_like = int(feels_like)
    cloud_coverage = weather_data['clouds']['all']
    timezone_offset = weather_data['timezone']
    datetime = convert_timestamp(timezone_offset)
    print(
        f"{f'{datetime}':<36} {f'{curr_temp}°{temp_unit}':<6} {f'{humidity}% humidity':<15} {f'Feels like {feels_like}°{temp_unit}':<8}")
    print(weather_description)
    print(f"{f'Wind Speed: {wind_speed}{speed}':<10}    Direction: {wind_degree}°")
    print(f'Cloud Coverage: {cloud_coverage}%\n')
    return weather_data


def display_forecast(location: str, forecast: json, degree_unit: int):
    if int(degree_unit):
        temp_unit = 'F'
    else:
        temp_unit = 'C'
    location = location.replace('_', ' ')
    print(f"\n5-Day Weather Forecast for {location}\n")
    print(
        f"{'Date':<21} {f'Avg Temp (°{temp_unit})':<15} {f'Low (°{temp_unit})':<10} {f'High (°{temp_unit})':<10} {'Humidity (%)':<15} {f'Feels Like (°{temp_unit})':<15}")
    print("=" * 94)

    for date, forecast_data in forecast.items():
        # Convert string to datetime object
        date_object = datetime.strptime(date, '%Y-%m-%d')

        # Get day of the week (full name)
        day_of_week = date_object.strftime('%A')
        avg_temp, low_temp, high_temp, humidity, feels_like = forecast_data
        print(
            f"{date:<12} {day_of_week: <9} {avg_temp:<15} {low_temp:<10} {high_temp:<10} {humidity:<15} {feels_like:<15}")
        print("=" * 94)
    print()


def convert_timestamp(timezone_offset_seconds: int):
    # Get the current UTC time (with timezone info)
    now_utc = datetime.now(tz=timezone.utc)  # Get current UTC time

    # Create a timezone object using the provided timezone offset (in seconds)
    tz = timezone(timedelta(seconds=timezone_offset_seconds))

    # Convert the current UTC time to the specified timezone by applying the offset
    dt_with_timezone = now_utc.astimezone(tz)

    # Format the datetime to RFC 2822 format
    return dt_with_timezone.strftime('%a, %d %b %Y %H:%M:%S UTC%z')


def insert_to_database(forecast: json, curr_forecast: json, location: str, db_cursor: sqlite3.Cursor):
    forecast_json = json.dumps(forecast)
    curr_forecast_json = json.dumps(curr_forecast)
    db_cursor.execute('''INSERT OR IGNORE INTO weather (location, forecast, current_forecast) VALUES (?,?,?)''',
                      (location, forecast_json, curr_forecast_json))


def find_in_database(location: str, db_cursor: sqlite3.Cursor):
    db_cursor.execute('''SELECT forecast, current_forecast FROM weather WHERE location = ?''', (location,))
    result = db_cursor.fetchone()

    if result is None:
        return None
    else:
        forecast_json = result[0]  # JSON string from the database
        forecast_data = json.loads(forecast_json)  # Convert back to a dictionary
        current_forecast_json = result[1]
        current_forecast_data = json.loads(current_forecast_json)
        return forecast_data, current_forecast_data


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
            break  # Exit the loop if no error occurs
        except ValueError:
            print('Invalid input, try again.')

    while True:
        city = input('Select a City: ')
        city = city.replace(' ', '_')  # replaces spaces for underscores, so it can be used in a URL

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
                forecast_data = saved_weather[0]
                curr_forecast_data = saved_weather[1]
                display_forecast(city, forecast_data, unit)
                get_current_weather(lat, lon, unit, weather_data=curr_forecast_data)
                print("Data retrieved from database!")
        except Exception as e:
            print(f'Invalid location entered, try again. ({e})')
