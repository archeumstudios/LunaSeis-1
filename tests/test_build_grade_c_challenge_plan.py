import unittest
from scripts.build_grade_c_challenge_plan import ranked


class GradeCChallengePlanTests(unittest.TestCase):
    def test_ranking_is_deterministic_and_station_specific(self):
        rows=[{"event_key":f"e{i}"} for i in range(10)]
        self.assertEqual(ranked(rows,"S12"),ranked(rows,"S12"))
        self.assertNotEqual(ranked(rows,"S12"),ranked(rows,"S14"))
