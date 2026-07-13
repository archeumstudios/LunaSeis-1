import unittest

from scripts.download_nonshallow_batch import select_batch


class SelectNonshallowBatchTests(unittest.TestCase):
    def test_selects_and_reconciles_batch(self):
        plan = {
            "products": [{"batch_id": 1, "bytes": 2}, {"batch_id": 2, "bytes": 3}],
            "batch_summaries": [{"batch_id": 1, "product_count": 1, "bytes": 2}],
        }
        self.assertEqual(select_batch(plan, 1), [{"batch_id": 1, "bytes": 2}])

    def test_rejects_bad_summary(self):
        with self.assertRaises(RuntimeError):
            select_batch({"products": [], "batch_summaries": [{"batch_id": 1, "product_count": 1, "bytes": 0}]}, 1)


if __name__ == "__main__":
    unittest.main()
