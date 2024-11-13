import unittest
from Weather import get_coord, get_forecast  # Adjust if the filename is different


class WeatherTestCase(unittest.TestCase):

    def test_get_coord_valid_city(self):
        """Test get_coord with a valid city name."""
        lat, lon = get_coord("Boston")
        # Check that lat and lon are floats
        self.assertIsInstance(lat, float, "Latitude should be a float.")
        self.assertIsInstance(lon, float, "Longitude should be a float.")

    def test_get_coord_invalid_city(self):
        """Test get_coord with an invalid city name to see if it handles errors."""
        with self.assertRaises(IndexError):
            get_coord("InvalidCityName1234")

    def test_get_forecast_valid_coordinates(self):
        """Test get_forecast with valid coordinates."""
        lat, lon = 42.3601, -71.0589  # Coordinates for Boston
        forecast = get_forecast(lat, lon)
        # Check that forecast is a list
        self.assertIsInstance(forecast, list, "Forecast should be a list.")
        # Check that forecast contains daily averages (i.e., sub-lists or dicts)
        if forecast:
            self.assertIsInstance(forecast[0], list, "Each item in forecast should be a list of daily averages.")
            self.assertEqual(len(forecast[0]), 5, "Each forecast entry should contain 5 daily average values.")

    def test_get_forecast_empty_result(self):
        """Test get_forecast with invalid coordinates (e.g., ocean or uninhabited area)."""
        lat, lon = 0.0, 0.0  # Example of empty or unpopulated coordinates
        forecast = get_forecast(lat, lon)
        # Check that forecast may return empty data or handle gracefully
        self.assertIsInstance(forecast, list, "Forecast should be a list even if empty.")
        self.assertTrue(len(forecast) >= 0, "Forecast list length should be zero or more.")


if __name__ == '__main__':
    unittest.main()
