from django.test import TestCase

class ApiTest(TestCase):

    def test_score(self):
        response = self.client.get("/api/score?symbol=BTCUSDT")
        self.assertEqual(response.status_code, 200)

    def test_rsi(self):
        response = self.client.get("/api/rsi?symbol=ETHUSDT")
        self.assertEqual(response.status_code, 200)