"""Cache versions must survive checkout platforms and invalidate real edits."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import stamp_assets


class AssetVersions(unittest.TestCase):
    def test_newlines_are_equivalent_but_real_content_changes(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(stamp_assets, 'ROOT', directory):
            asset = Path(directory) / 'test.js'
            asset.write_bytes(b'const value=1;\r\n')
            windows = stamp_assets.digest('test.js', {})
            asset.write_bytes(b'const value=1;\n')
            self.assertEqual(windows, stamp_assets.digest('test.js', {}))
            asset.write_bytes(b'const value=2;\n')
            self.assertNotEqual(windows, stamp_assets.digest('test.js', {}))


if __name__ == '__main__':
    unittest.main()
