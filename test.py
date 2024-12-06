import unittest
import json
from unittest.mock import patch, MagicMock
from Weather import get_coord, get_forecast, get_current_weather, convert_timestamp

class TestWeatherModule(unittest.TestCase):

    @patch('Weather.urlopen')
    def test_get_coord(self, mock_urlopen):
        # Mock API response for get_coord
        mock_response = MagicMock()
        mock_response.read.return_value = b'[{"lat": 38.8951, "lon": -77.0364}]'
        mock_urlopen.return_value = mock_response

        # Call the function with a test city
        lat, lon = get_coord("Washington")
        self.assertEqual(lat, 38.8951)
        self.assertEqual(lon, -77.0364)

    def test_convert_timestamp(self):
        # Test convert_timestamp with a positive offset
        offset = 3600  # 1 hour
        dt = convert_timestamp(offset)
        self.assertIn("UTC+0100", dt)

        # Test convert_timestamp with a negative offset
        offset = -18000  # -5 hours
        dt = convert_timestamp(offset)
        self.assertIn("UTC-0500", dt)

        # Test convert_timestamp with zero offset
        offset = 0
        dt = convert_timestamp(offset)
        self.assertIn("UTC+0000", dt)


if __name__ == '__main__':
    unittest.main()
