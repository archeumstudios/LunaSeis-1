import unittest
from pathlib import PurePosixPath

from scripts.download_catalog import parse_manifest


class ParseManifestTests(unittest.TestCase):
    def test_normalizes_pds_paths(self) -> None:
        text = "ABCDEF0123456789ABCDEF0123456789  data\\events.csv\n"
        self.assertEqual(
            parse_manifest(text),
            [("abcdef0123456789abcdef0123456789", PurePosixPath("data/events.csv"))],
        )


    def test_rejects_traversal(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            parse_manifest("ABCDEF0123456789ABCDEF0123456789  ..\\secret\n")


if __name__ == "__main__":
    unittest.main()
