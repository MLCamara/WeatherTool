import unittest
from unittest.mock import patch, MagicMock
import json
from Weather import get_coord, get_forecast, get_current_weather, degrees_to_compass

class TestWeatherFunctions(unittest.TestCase):
    '''These tests will ensure that the functions return JSON data in the correct format,
     even though the actual values will vary depending on the API response.'''
    @patch('Weather.urlopen')
    def test_get_coord_valid(self, mock_urlopen):
        # Mock API response for a location
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps([{"lat": 38.8951, "lon": -77.0364}]).encode('utf-8')
        mock_urlopen.return_value = mock_response

        lat, lon = get_coord("Washington")
        self.assertIsInstance(lat, float)
        self.assertIsInstance(lon, float)

    @patch('Weather.urlopen')
    def test_get_forecast_valid(self, mock_urlopen):
        # Mock API response for forecast
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "list": [
                {
                    "dt_txt": "2024-12-11 00:00:00",
                    "main": {
                        "temp": 280.32,
                        "temp_min": 279.15,
                        "temp_max": 281.48,
                        "humidity": 81,
                        "feels_like": 278.66
                    }
                },
                {
                    "dt_txt": "2024-12-12 00:00:00",
                    "main": {
                        "temp": 290.32,
                        "temp_min": 289.15,
                        "temp_max": 291.48,
                        "humidity": 75,
                        "feels_like": 289.66
                    }
                }
            ]
        }).encode('utf-8')
        mock_urlopen.return_value = mock_response

        forecast = get_forecast(38.8951, -77.0364, 0)
        self.assertIsInstance(forecast, dict)
        self.assertGreater(len(forecast), 0)  # Ensure it's not empty

    @patch('Weather.urlopen')
    def test_get_current_weather_valid(self, mock_urlopen):
        # Mock API response for current weather
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "weather": [{"description": "clear sky"}],
            "main": {"temp": 283.55, "feels_like": 281.86, "humidity": 72},
            "wind": {"speed": 4.1, "deg": 80},
            "clouds": {"all": 0},
            "timezone": -18000
        }).encode('utf-8')
        mock_urlopen.return_value = mock_response

        current_weather = get_current_weather(38.8951, -77.0364, 0)
        self.assertIsInstance(current_weather, dict)
        self.assertGreater(len(current_weather), 0)

    def test_degrees_to_compass(self):
        # Testing various degrees and their expected compass directions

        # Test for North direction (0° to 44°)
        self.assertEqual(degrees_to_compass(0), 'N')
        self.assertEqual(degrees_to_compass(22), 'N')
        self.assertEqual(degrees_to_compass(44), 'N')

        # Test for Northeast direction (45° to 89°)
        self.assertEqual(degrees_to_compass(45), 'NE')
        self.assertEqual(degrees_to_compass(67), 'NE')
        self.assertEqual(degrees_to_compass(89), 'NE')

        # Test for East direction (90° to 134°)
        self.assertEqual(degrees_to_compass(90), 'E')
        self.assertEqual(degrees_to_compass(112), 'E')
        self.assertEqual(degrees_to_compass(134), 'E')

        # Test for Southeast direction (135° to 179°)
        self.assertEqual(degrees_to_compass(135), 'SE')
        self.assertEqual(degrees_to_compass(157), 'SE')
        self.assertEqual(degrees_to_compass(179), 'SE')

        # Test for South direction (180° to 224°)
        self.assertEqual(degrees_to_compass(180), 'S')
        self.assertEqual(degrees_to_compass(202), 'S')
        self.assertEqual(degrees_to_compass(224), 'S')

        # Test for Southwest direction (225° to 269°)
        self.assertEqual(degrees_to_compass(225), 'SW')
        self.assertEqual(degrees_to_compass(247), 'SW')
        self.assertEqual(degrees_to_compass(269), 'SW')

        # Test for West direction (270° to 314°)
        self.assertEqual(degrees_to_compass(270), 'W')
        self.assertEqual(degrees_to_compass(292), 'W')
        self.assertEqual(degrees_to_compass(314), 'W')

        # Test for Northwest direction (315° to 359°)
        self.assertEqual(degrees_to_compass(315), 'NW')
        self.assertEqual(degrees_to_compass(337), 'NW')
        self.assertEqual(degrees_to_compass(359), 'NW')

if __name__ == '__main__':
    unittest.main()
