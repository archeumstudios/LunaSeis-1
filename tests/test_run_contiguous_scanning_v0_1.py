import unittest
import numpy as np

from scripts.run_contiguous_scanning_v0_1 import catalog_references, match_triggers, recall_threshold


class ContinuousScanningTests(unittest.TestCase):
    def test_recall_threshold_is_highest_meeting_target(self):
        scores=np.array([.1,.2,.8,.9]);labels=np.array([0,0,1,1])
        self.assertEqual(recall_threshold(scores,labels,.5),.9)
        self.assertEqual(recall_threshold(scores,labels,1.),.8)

    def test_one_to_one_matching_and_false_trigger(self):
        catalogs=catalog_references([{"station":"S12","reference_time":"1971-01-01T00:00:00","unified_candidate_id":"E1"}],{"E1"})
        triggers=[{"station":"S12","trigger_time":"1971-01-01T00:00:10","peak_score":.9},{"station":"S12","trigger_time":"1971-01-01T00:00:20","peak_score":.8}]
        rows,counts=match_triggers(triggers,catalogs,60)
        self.assertEqual(counts["eligible_true_triggers"],1);self.assertEqual(counts["false_triggers"],1)
        self.assertEqual([row["match_status"] for row in rows],["eligible_true_trigger","false_trigger"])
