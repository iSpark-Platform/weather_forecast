# tests/test_api.py - Flask API Endpoints Integration Tests using Flask Test Client
import unittest
import json
from app import app

class TestFlaskEndpoints(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_forecast_page(self):
        response = self.client.get('/forecast?city=Mumbai')
        self.assertEqual(response.status_code, 200)

    def test_coastal_page(self):
        response = self.client.get('/coastal')
        self.assertEqual(response.status_code, 200)

    def test_map_page(self):
        response = self.client.get('/map')
        self.assertEqual(response.status_code, 200)

    def test_hourly_page(self):
        response = self.client.get('/hourly')
        self.assertEqual(response.status_code, 200)

    def test_analytics_page(self):
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 200)

    def test_decoder_page(self):
        response = self.client.get('/decoder')
        self.assertEqual(response.status_code, 200)

    def test_tutor_page(self):
        response = self.client.get('/tutor')
        self.assertEqual(response.status_code, 200)

    def test_api_weather_endpoint(self):
        response = self.client.get('/api/weather?city=Mumbai')
        self.assertIn(response.status_code, [200, 500, 404])
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertIn("location", data)
            self.assertIn("current", data)
            self.assertIn("daily", data)

    def test_api_coastal_endpoint(self):
        response = self.client.get('/api/coastal?city=Mumbai')
        self.assertIn(response.status_code, [200, 500, 404])

    def test_api_tutor_ask_endpoint(self):
        payload = {"question": "What causes cyclones?", "lang": "en"}
        response = self.client.post(
            '/api/tutor',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("answer", data)

    def test_api_tutor_greeting_endpoint(self):
        response = self.client.get('/api/tutor/greeting?lang=en')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("greeting", data)

    def test_api_cities_coastal(self):
        response = self.client.get('/api/cities/coastal')
        self.assertEqual(response.status_code, 200)

    def test_api_languages(self):
        response = self.client.get('/api/languages')
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
