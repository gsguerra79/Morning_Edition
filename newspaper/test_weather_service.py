import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import weather_service


class WeatherServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_cache = weather_service.CACHE_FILE
        weather_service.CACHE_FILE = str(Path(self.tmp.name) / "weather.json")
        weather_service._memory = None
        weather_service._memory_at = 0

    def tearDown(self):
        weather_service.CACHE_FILE = self.old_cache
        weather_service._memory = None
        weather_service._memory_at = 0
        self.tmp.cleanup()

    def test_weekly_combines_day_and_night_into_seven_cards(self):
        periods = []
        for day in range(1, 9):
            date = f"2026-09-{day:02d}"
            periods.extend([
                {
                    "startTime": f"{date}T06:00:00-05:00", "isDaytime": True,
                    "temperature": 90 + day, "shortForecast": "Sunny",
                    "probabilityOfPrecipitation": {"value": day},
                },
                {
                    "startTime": f"{date}T18:00:00-05:00", "isDaytime": False,
                    "temperature": 70 + day, "shortForecast": "Clear",
                    "probabilityOfPrecipitation": {"value": day + 4},
                },
            ])

        days = weather_service._weekly(periods)

        self.assertEqual(7, len(days))
        self.assertEqual(91, days[0]["high"])
        self.assertEqual(71, days[0]["low"])
        self.assertEqual(5, days[0]["precipitation"])

    def test_build_returns_houston_rio_and_weather_articles(self):
        hourly_period = {
            "startTime": "2026-09-03T12:00:00-05:00", "temperature": 88,
            "temperatureUnit": "F", "shortForecast": "Thunderstorms",
            "probabilityOfPrecipitation": {"value": 60},
            "windSpeed": "10 mph", "windDirection": "SE",
        }
        forecast_periods = [
            {**hourly_period, "isDaytime": True},
            {**hourly_period, "startTime": "2026-09-03T20:00:00-05:00",
             "temperature": 75, "isDaytime": False},
        ]

        def fake_json(url):
            if "/points/" in url:
                return {"properties": {"forecast": "forecast-url", "forecastHourly": "hourly-url"}}
            if url == "forecast-url":
                return {"properties": {"periods": forecast_periods}}
            if url == "hourly-url":
                return {"properties": {"periods": [hourly_period] * 30}}
            if "/alerts/active" in url:
                return {"features": [{"id": "https://weather.gov/alert/1", "properties": {
                    "headline": "Flood Warning", "description": "High water.",
                    "sent": "2026-09-03T12:00:00Z", "severity": "Severe",
                }}]}
            raise AssertionError(url)

        rio = {"temperature": 79, "condition": "Clear"}
        story = {"title": "Gulf storm update", "summary": "Latest outlook",
                 "url": "https://example.com/storm", "source": "NHC",
                 "published_at": "now", "kind": "article"}
        with patch.object(weather_service, "_json", side_effect=fake_json), \
             patch.object(weather_service, "_rio", return_value=rio), \
             patch.object(weather_service, "_rss", return_value=[story]):
            payload = weather_service._build()

        self.assertEqual(24, len(payload["houston"]["hourly"]))
        self.assertEqual("Flood Warning", payload["houston"]["alerts"][0]["title"])
        self.assertEqual(rio, payload["rio"])
        self.assertTrue(any(a["title"] == "Gulf storm update" for a in payload["articles"]))
        self.assertEqual("KHGX — Houston/Galveston", payload["houston"]["radar"]["station"])

    def test_failed_refresh_serves_stale_cache(self):
        cached = {"updated_at": "2026-09-03T00:00:00+00:00", "errors": []}
        Path(weather_service.CACHE_FILE).write_text(json.dumps(cached), encoding="utf-8")
        with patch.object(weather_service, "_build", side_effect=OSError("offline")):
            payload = weather_service.get_weather(force=True)

        self.assertTrue(payload["stale"])
        self.assertIn("offline", payload["errors"][-1])


if __name__ == "__main__":
    unittest.main()
