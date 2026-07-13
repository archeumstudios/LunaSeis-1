import unittest

from scripts.audit_nonshallow_batch import complete_channels_in_batch, edge_fraction


class NonshallowBatchAuditTests(unittest.TestCase):
    def test_edge_fraction_is_descriptive(self):
        self.assertEqual(edge_fraction([1, 1, 2, 3, 3]), 0.8)
        self.assertEqual(edge_fraction([4, 4, 4]), 1.0)

    def test_channel_requires_att_and_data_for_all_days_in_same_batch(self):
        request = {"station": "S12", "required_station_days": "1971-210", "complete_positive_channels": "MH1"}
        base = "data/xa/continuous_waveform/s12/1971/210/"
        names = ["xa.s12..att.1971.210.0.mseed", "xa.s12..att.1971.210.0.xml", "xa.s12.00.mh1.1971.210.0.mseed", "xa.s12.00.mh1.1971.210.0.xml"]
        self.assertEqual(complete_channels_in_batch(request, {base + name: 1 for name in names}, 1), ["MH1"])


if __name__ == "__main__":
    unittest.main()
