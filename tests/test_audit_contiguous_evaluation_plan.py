import unittest
from datetime import datetime

from scripts.audit_contiguous_evaluation_plan import calendar_time


class ContiguousEvaluationAuditTests(unittest.TestCase):
    def test_calendar_time(self):
        self.assertEqual(calendar_time(1972,60,"01:02:03"),datetime(1972,2,29,1,2,3))
