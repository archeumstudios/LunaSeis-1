import tempfile
import unittest
from pathlib import Path

from scripts.build_contiguous_evaluation_plan import candidate_blocks, channel_product_names, prior_station_days, select_nonoverlapping, station_day_from_path


class ContiguousEvaluationPlanTests(unittest.TestCase):
    def test_path_and_block_exclusion(self):
        self.assertEqual(station_day_from_path("data/xa/continuous_waveform/s12/1971/123/file"),("S12",1971,123))
        archive={1971:list(range(1,31))};excluded={("S12",1971,4)}
        candidates=candidate_blocks("S12",archive,excluded,3)
        self.assertTrue(all(not (start<=4<start+3) for _,_,start in candidates))
        selected=select_nonoverlapping(candidates,2,3)
        self.assertEqual(len(selected),2)
        self.assertTrue(set(range(selected[0][1],selected[0][1]+3)).isdisjoint(range(selected[1][1],selected[1][1]+3)))

    def test_prior_days_from_manifests(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/"plan.json").write_text('{"products":[{"path":"data/xa/continuous_waveform/s14/1972/042/x"}]}')
            self.assertEqual(prior_station_days(root),{("S14",1972,42)})

    def test_channel_discovery_accepts_location_01(self):
        listing={"xa.s12.01.mhz.1975.006.0.mseed":10,"xa.s12.01.mhz.1975.006.0.xml":20}
        self.assertEqual(channel_product_names(listing,"MHZ"),list(listing))
