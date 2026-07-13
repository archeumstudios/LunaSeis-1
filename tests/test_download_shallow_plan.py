import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.download_shallow_plan import verify_one


class VerifyShallowProductTests(unittest.TestCase):
    def test_reuses_valid_file_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "safe" / "file.xml"
            target.parent.mkdir()
            target.write_bytes(b"abc")
            product = {
                "path": "safe/file.xml",
                "url": "https://example.invalid/file.xml",
                "bytes": 3,
                "md5": "900150983cd24fb0d6963f7d28e17f72",
            }
            with patch("scripts.download_shallow_plan.fetch") as fetch:
                _, size, reused = verify_one(product, root)
            self.assertEqual(size, 3)
            self.assertTrue(reused)
            fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
