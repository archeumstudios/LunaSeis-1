import unittest

from scripts.build_shallow_download_plan import expected_names


class BuildShallowDownloadPlanTests(unittest.TestCase):
    def test_expected_products_include_timing_and_short_period_data_with_labels(self):
        self.assertEqual(
            expected_names("S15", 1975, 82),
            [
                "xa.s15..att.1975.082.0.mseed",
                "xa.s15..att.1975.082.0.xml",
                "xa.s15..shz.1975.082.0.mseed",
                "xa.s15..shz.1975.082.0.xml",
            ],
        )


if __name__ == "__main__":
    unittest.main()
