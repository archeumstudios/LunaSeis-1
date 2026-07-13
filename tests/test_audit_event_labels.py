import unittest
from datetime import datetime

from scripts.audit_event_labels import event_time


class EventTimeTests(unittest.TestCase):
    def test_converts_two_digit_year_day_and_hhmm(self) -> None:
        row = {"Y": "71", "JD": "210", "S": "2058"}
        self.assertEqual(event_time(row), datetime(1971, 7, 29, 20, 58))

    def test_rejects_invalid_hhmm(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid HHMM"):
            event_time({"Y": "71", "JD": "210", "S": "2060"})


if __name__ == "__main__":
    unittest.main()
