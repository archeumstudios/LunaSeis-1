import unittest
from datetime import datetime

from scripts.reconcile_shallow_catalog import KO_EVENTS, YN_EVENTS, calendar_time, parse_lines


class ReconcileShallowCatalogTests(unittest.TestCase):
    def test_corrected_table_counts(self):
        self.assertEqual(len(parse_lines(YN_EVENTS)), 28)
        self.assertEqual(len(parse_lines(KO_EVENTS)), 46)
        self.assertEqual(len({row[0] for row in parse_lines(YN_EVENTS + KO_EVENTS)}), 74)

    def test_calendar_time_handles_doy_and_seconds(self):
        self.assertEqual(calendar_time(1972, 2, "22:32"), datetime(1972, 1, 2, 22, 32))
        self.assertEqual(calendar_time(1976, 337, "12:45:41"), datetime(1976, 12, 2, 12, 45, 41))


if __name__ == "__main__":
    unittest.main()
