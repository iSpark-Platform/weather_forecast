# tests/test_weather_service.py - Tests for weather service helper functions
import unittest
from modules.weather_service import get_wmo, WMO_CODES

class TestWeatherService(unittest.TestCase):

    def test_get_wmo_valid(self):
        label, icon, severity = get_wmo(0)
        self.assertEqual(label, "Clear Sky")
        self.assertEqual(severity, 0)

        label_95, icon_95, severity_95 = get_wmo(95)
        self.assertEqual(label_95, "Thunderstorm")
        self.assertEqual(severity_95, 5)

    def test_get_wmo_invalid(self):
        label, icon, severity = get_wmo(9999)
        self.assertEqual(label, "Unknown")
        self.assertEqual(severity, 0)

    def test_wmo_codes_dict(self):
        self.assertIn(0, WMO_CODES)
        self.assertIn(95, WMO_CODES)

if __name__ == "__main__":
    unittest.main()
