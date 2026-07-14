import unittest
import numpy as np

from scripts.audit_continuous_scanning_errors import safe_correlation


class ContinuousScanningErrorAuditTests(unittest.TestCase):
    def test_safe_correlation(self):
        self.assertAlmostEqual(safe_correlation([1,2,3],[2,4,6]),1.)
        self.assertEqual(safe_correlation(np.ones(3),[1,2,3]),0.)
