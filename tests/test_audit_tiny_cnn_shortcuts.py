import unittest
import numpy as np

from scripts.audit_tiny_cnn_shortcuts import safe_correlation


class TinyCNNShortcutAuditTests(unittest.TestCase):
    def test_safe_correlation(self):
        self.assertAlmostEqual(safe_correlation(np.array([1.,2.,3.]),np.array([2.,4.,6.])),1.0)
        self.assertEqual(safe_correlation(np.ones(3),np.arange(3)),0.0)
