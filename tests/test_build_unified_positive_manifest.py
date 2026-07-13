import unittest
from datetime import datetime

from scripts.build_unified_positive_manifest import corrected_time, split_group


class UnifiedPositiveManifestTests(unittest.TestCase):
    def test_corrected_second_precision_time(self):
        row = {"year": "1975", "doy": "082", "start_time_utc": "21:10:13"}
        self.assertEqual(corrected_time(row), datetime(1975, 3, 23, 21, 10, 13))

    def test_split_group_prioritizes_deep_family(self):
        self.assertEqual(split_group("levent-1", "deep_moonquake_assigned", "A12"), ("deep-family:A12", "deep_repeating_family"))

    def test_repeating_shallow_pair_is_indivisible(self):
        left = split_group("KO-SMQ-26", "shallow_moonquake", "")
        right = split_group("KO-SMQ-40", "shallow_moonquake", "")
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
