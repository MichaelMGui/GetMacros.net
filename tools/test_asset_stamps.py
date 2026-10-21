"""Cache versions must survive checkout platforms and invalidate real edits."""
from pathlib import Path
import tempfile
import unittest
import hashlib
import json
import re
from unittest.mock import patch
import stamp_assets


class AssetVersions(unittest.TestCase):
    def test_hreflang_only_identifies_genuine_reciprocal_equivalents(self):
        root=Path(stamp_assets.ROOT)
        markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',(root/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
        expected={}
        for kind in ['home','finder','restaurants']:
            alternates={f'en-{code}':'https://getmacros.net'+item[kind] for code,item in markets.items()}
            alternates['x-default']='https://getmacros.net'+markets['US'][kind]
            for item in markets.values():expected[item[kind]]=alternates
        # The regional protein collections now share a reviewed individual-main
        # scope. The broader U.S. healthy-fast-food guide is not an equivalent.
        regional={code:item for code,item in markets.items() if code!='US'}
        collection_alternates={f'en-{code}':'https://getmacros.net'+item['collection'] for code,item in regional.items()}
        for item in regional.values():expected[item['collection']]=collection_alternates
        for page in list(root.glob('*.html'))+list(root.glob('*/en/**/index.html')):
            html=page.read_text(encoding='utf-8')
            relative=page.relative_to(root).as_posix()
            route='/' if relative=='index.html' else '/'+relative.removesuffix('index.html') if relative.endswith('/index.html') else '/'+relative
            actual={}
            for tag in re.findall(r'<link\b[^>]*hreflang=[^>]*>',html):
                attrs=dict(re.findall(r'([\w-]+)="([^"]*)"',tag))
                self.assertNotIn(attrs['hreflang'],actual,str(page))
                actual[attrs['hreflang']]=attrs['href']
            self.assertEqual(actual,expected.get(route,{}),str(page))

    def test_published_immutable_assets_match_sources_and_filenames(self):
        root = Path(stamp_assets.ROOT)
        manifest = json.loads((root / 'assets/generated/manifest.json').read_text(encoding='utf-8'))
        self.assertIn('js/order-registry.json', manifest)
        for source, record in manifest.items():
            original = (root / source).read_bytes().replace(b'\r\n', b'\n')
            public = (root / record['url'].lstrip('/')).read_bytes()
            self.assertEqual(hashlib.sha256(original).hexdigest(), record['sourceSha256'], source)
            digest = hashlib.sha256(public).hexdigest()
            self.assertEqual(digest, record['assetSha256'], source)
            self.assertIn('-' + digest[:12] + '.', record['url'], source)
            if source.endswith('.css'):
                for value in re.findall(r'url\(([^)]+)\)', public.decode('utf-8')):
                    self.assertTrue(value.strip('\"\' ').startswith(('/', '#', 'data:', 'http:', 'https:')), source)
        pages = list(root.glob('*.html')) + list(root.glob('*/en/**/index.html'))
        for page in pages:
            html = page.read_text(encoding='utf-8')
            scripts = re.findall(r'<script\b[^>]*data-source-path="([^"]+)"', html)
            self.assertEqual(len(scripts), len(set(scripts)), str(page) + ': duplicate active modules')
            for tag in re.findall(r'<(?:link|script)\b[^>]*data-source-path="[^"]+"[^>]*>', html):
                source = re.search(r'data-source-path="([^"]+)"', tag)[1]
                self.assertIn(source, manifest, str(page))
                self.assertIn('="' + manifest[source]['url'] + '"', tag, str(page))
            self.assertIn(manifest['js/order-registry.json']['url'], html, str(page))

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
