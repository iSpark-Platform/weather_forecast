# tests/test_risk_calculator.py - Tests for risk calculator module
import unittest
from modules.risk_calculator import (
    compute_risk_score, score_to_risk, assess_daily_risks,
    assess_coastal_risk, get_overall_region_risk,
    get_wind_direction_label, get_uv_label, get_humidity_label
)

class TestRiskCalculator(unittest.TestCase):

    def test_compute_risk_score_low(self):
        daily = {
            "severity": 0,
            "precipitation": 0,
            "precip_prob": 10,
            "wind_speed": 10,
            "uv_index": 2
        }
        score = compute_risk_score(daily)
        self.assertGreaterEqual(score, 0)
        self.assertLess(score, 30)

    def test_compute_risk_score_extreme(self):
        daily = {
            "severity": 7,
            "precipitation": 120,
            "precip_prob": 100,
            "wind_speed": 130,
            "uv_index": 12
        }
        score = compute_risk_score(daily)
        self.assertEqual(score, 100)

    def test_score_to_risk(self):
        self.assertEqual(score_to_risk(10)["level"], "GREEN")
        self.assertEqual(score_to_risk(40)["level"], "YELLOW")
        self.assertEqual(score_to_risk(65)["level"], "ORANGE")
        self.assertEqual(score_to_risk(85)["level"], "RED")

    def test_assess_daily_risks(self):
        daily_list = [
            {"severity": 0, "precipitation": 0, "precip_prob": 0, "wind_speed": 5, "uv_index": 1},
            {"severity": 6, "precipitation": 90, "precip_prob": 80, "wind_speed": 70, "uv_index": 9}
        ]
        result = assess_daily_risks(daily_list)
        self.assertEqual(len(result), 2)
        self.assertIn("risk_score", result[0])
        self.assertIn("risk", result[0])
        self.assertEqual(result[0]["risk"]["level"], "GREEN")

    def test_assess_coastal_risk(self):
        weather_data = {
            "daily": [
                {"severity": 5, "precipitation": 90, "precip_prob": 80, "wind_speed": 85, "uv_index": 5}
            ]
        }
        city_info = {"name": "Mumbai", "coast": "West Coast"}
        results = assess_coastal_risk(weather_data, city_info)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0]["coastal_bonus"], 0)
        self.assertTrue(len(results[0]["alerts"]) > 0)

    def test_get_overall_region_risk(self):
        daily_risks = [
            {"risk_score": 20},
            {"risk_score": 85},
            {"risk_score": 40}
        ]
        overall = get_overall_region_risk(daily_risks)
        self.assertEqual(overall["level"], "RED")

    def test_labels(self):
        self.assertEqual(get_wind_direction_label(0), "N")
        self.assertEqual(get_wind_direction_label(90), "E")
        self.assertEqual(get_wind_direction_label(180), "S")
        self.assertEqual(get_wind_direction_label(270), "W")
        
        uv_label, _ = get_uv_label(12)
        self.assertEqual(uv_label, "Extreme")

        self.assertEqual(get_humidity_label(85), "Very Humid")
        self.assertEqual(get_humidity_label(15), "Very Dry")

if __name__ == "__main__":
    unittest.main()
