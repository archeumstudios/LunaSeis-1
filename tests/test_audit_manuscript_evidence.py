import unittest

from scripts.audit_manuscript_evidence import binomial_exact, poisson_rate_exact


class ManuscriptEvidenceAuditTests(unittest.TestCase):
    def test_exact_binomial_bounds_cover_observed_rate(self):
        low, high = binomial_exact(12, 63)
        self.assertAlmostEqual(low, 0.1024842436)
        self.assertAlmostEqual(high, 0.3090884691)
        self.assertLess(low, 12 / 63)
        self.assertGreater(high, 12 / 63)

    def test_zero_success_has_zero_lower_bound(self):
        low, high = binomial_exact(0, 3)
        self.assertEqual(low, 0.0)
        self.assertAlmostEqual(high, 0.7075982262)

    def test_poisson_bounds_cover_observed_rate(self):
        low, high = poisson_rate_exact(1306, 1505.35)
        rate = 1306 / 1505.35
        self.assertLess(low, rate)
        self.assertGreater(high, rate)

