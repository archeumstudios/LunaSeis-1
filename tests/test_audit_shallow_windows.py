import unittest
import numpy as np

from scripts.audit_shallow_windows import gap_statistics, integrity_status


class ShallowWindowAuditTests(unittest.TestCase):
    def test_gap_runs_and_fraction(self):
        result = gap_statistics(np.array([0, -1, -1, 2, -1, 3]))
        self.assertEqual(result["gap_sample_count"], 3)
        self.assertEqual(result["gap_run_count"], 2)
        self.assertEqual(result["longest_gap_samples"], 2)
        self.assertEqual(result["gap_fraction"], 0.5)

    def test_integrity_thresholds_do_not_use_signal_strength(self):
        self.assertEqual(integrity_status(0.2, 0.3), "usable_integrity")
        self.assertEqual(integrity_status(0.21, 0.3), "questionable_integrity")
        self.assertEqual(integrity_status(0.51, 0.3), "reject_integrity")
        self.assertEqual(integrity_status(0.0, 2.0), "questionable_integrity")
        self.assertEqual(integrity_status(0.0, 11.0), "reject_integrity")


if __name__ == "__main__":
    unittest.main()
