import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import f1_service


class F1ServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_cache = f1_service.CACHE_FILE
        f1_service.CACHE_FILE = str(Path(self.tmp.name) / "f1.json")
        f1_service._memory = None
        f1_service._memory_at = 0
        f1_service._openf1_access_token = None
        f1_service._openf1_token_until = 0

    def tearDown(self):
        f1_service.CACHE_FILE = self.old_cache
        f1_service._memory = None
        f1_service._memory_at = 0
        self.tmp.cleanup()

    def test_driver_standings_are_normalized(self):
        payload = {"MRData": {"StandingsTable": {"season": "2026", "round": "12",
            "StandingsLists": [{"DriverStandings": [{"position": "1", "points": "242",
                "wins": "6", "Driver": {"code": "ANT", "givenName": "Kimi",
                "familyName": "Antonelli"}, "Constructors": [{"name": "Mercedes"}]}]}]}}}
        result = f1_service._standings_rows(payload, "drivers")
        self.assertEqual("2026", result["season"])
        self.assertEqual("Kimi Antonelli", result["rows"][0]["name"])
        self.assertEqual(242.0, result["rows"][0]["points"])

    def test_race_weekend_uses_latest_finalized_session_and_next_session(self):
        index = {"Meetings": [{"Name": "Italian Grand Prix", "Country": {"Name": "Italy"},
            "Circuit": {"ShortName": "Monza"}, "Sessions": [
                {"Name": "Practice 1", "StartDate": "2026-09-04T12:30:00",
                 "EndDate": "2026-09-04T13:30:00", "GmtOffset": "02:00:00", "Path": "fp1/"},
                {"Name": "Practice 2", "StartDate": "2026-09-04T16:00:00",
                 "EndDate": "2026-09-04T17:00:00", "GmtOffset": "02:00:00"},
                {"Name": "Race", "StartDate": "2026-09-06T15:00:00",
                 "EndDate": "2026-09-06T17:00:00", "GmtOffset": "02:00:00"},
            ]}]}
        result = {"session": "Practice 1", "rows": [{"position": 1}]}
        now = datetime(2026, 9, 4, 14, 30, tzinfo=timezone.utc)
        with patch.object(f1_service, "_session_result", return_value=result):
            weekend = f1_service._race_weekend(index, now)
        self.assertEqual("Practice 1", weekend["latest_session"]["session"])
        self.assertEqual("Practice 2", weekend["current_session"]["name"])
        self.assertEqual("Race", weekend["next_session"]["name"])

    def test_failed_refresh_serves_stale_cache(self):
        cached = {"updated_at": "2026-09-04T00:00:00+00:00", "standings": {}}
        Path(f1_service.CACHE_FILE).write_text(json.dumps(cached), encoding="utf-8")
        with patch.object(f1_service, "_build", side_effect=OSError("offline")):
            result = f1_service.get_f1(force=True)
        self.assertTrue(result["stale"])
        self.assertIn("offline", result["errors"][-1])

    def test_openf1_live_snapshot_normalizes_provisional_laps(self):
        now = datetime(2026, 9, 4, 14, 30, tzinfo=timezone.utc)
        payloads = {
            "sessions": [{"session_key": 123, "meeting_name": "Italian Grand Prix",
                "country_name": "Italy", "circuit_short_name": "Monza",
                "session_name": "Practice 2", "session_type": "Practice",
                "date_start": "2026-09-04T14:00:00+00:00",
                "date_end": "2026-09-04T15:00:00+00:00"}],
            "drivers": [{"driver_number": 4, "name_acronym": "NOR",
                "full_name": "Lando Norris", "team_name": "McLaren",
                "team_colour": "FF8700"}],
            "session_result": [],
            "laps": [{"driver_number": 4, "lap_duration": 80.125,
                      "lap_number": 12}],
            "weather": [{"air_temperature": 25.2, "track_temperature": 39.1}],
        }
        with patch.object(f1_service, "_openf1_json",
                          side_effect=lambda endpoint, **params: payloads[endpoint]):
            result = f1_service._openf1_snapshot(now)
        self.assertTrue(result["provisional"])
        self.assertEqual("NOR", result["rows"][0]["code"])
        self.assertEqual("1:20.125", result["rows"][0]["time"])
        self.assertEqual(12, result["rows"][0]["laps"])

    def test_openf1_snapshot_ignores_non_live_window(self):
        now = datetime(2026, 9, 5, 14, 30, tzinfo=timezone.utc)
        sessions = [{"session_key": 123, "date_start": "2026-09-04T14:00:00+00:00",
                     "date_end": "2026-09-04T15:00:00+00:00"}]
        with patch.object(f1_service, "_openf1_json", return_value=sessions):
            self.assertIsNone(f1_service._openf1_snapshot(now))


if __name__ == "__main__":
    unittest.main()
