# tests/test_coastal_alerts.py - Tests for coastal alerts module
import unittest
from modules.coastal_alerts import (
    get_cyclone_risk, assess_tsunami_risk, assess_flood_risk_by_precipitation,
    TSUNAMI_ZONES, FLOOD_ZONES
)

class TestCoastalAlerts(unittest.TestCase):

    def test_get_cyclone_risk_levels(self):
        # Super Cyclonic Storm
        res = get_cyclone_risk(230, month=5)
        self.assertEqual(res["category"], "SuCS")
        self.assertEqual(res["risk"], "EXTREME")

        # Cyclonic Storm
        res = get_cyclone_risk(70, month=5)
        self.assertEqual(res["category"], "CS")
        self.assertEqual(res["risk"], "MODERATE")

        # Low wind, off season
        res = get_cyclone_risk(20, month=1)
        self.assertEqual(res["category"], "NONE")
        self.assertEqual(res["risk"], "LOW")

    def test_assess_tsunami_risk(self):
        city = {"name": "Chennai", "coast": "Tamil Nadu"}
        risk = assess_tsunami_risk({}, city)
        self.assertIn("score", risk)
        self.assertIn("label", risk)

    def test_assess_flood_risk_by_precipitation(self):
        daily_forecast = [
            {"date": "2026-08-01", "precipitation": 150, "precip_prob": 90, "temp_max": 28},
            {"date": "2026-08-02", "precipitation": 10, "precip_prob": 20, "temp_max": 30}
        ]
        result = assess_flood_risk_by_precipitation(daily_forecast)
        self.assertIn("risk", result)
        self.assertIn("total_rain", result)
        self.assertGreaterEqual(result["total_rain"], 160)

    def test_zones_definition(self):
        self.assertTrue(len(TSUNAMI_ZONES) > 0)
        self.assertTrue(len(FLOOD_ZONES) > 0)

if __name__ == "__main__":
    unittest.main()
