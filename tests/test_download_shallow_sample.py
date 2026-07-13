import unittest

from scripts.download_shallow_sample import select_products


class SelectShallowProductsTests(unittest.TestCase):
    def test_selects_exact_station_day(self):
        products = [
            {"path": f"data/xa/continuous_waveform/s15/1975/082/file-{i}"}
            for i in range(4)
        ] + [{"path": "data/xa/continuous_waveform/s15/1975/083/other"}]
        self.assertEqual(len(select_products({"products": products}, "S15", 1975, 82)), 4)


if __name__ == "__main__":
    unittest.main()
