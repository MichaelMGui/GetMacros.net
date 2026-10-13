"""Regression checks for repeatable product integration and app configuration."""
from pathlib import Path
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]

def integrate():
    for script in ['restore_asset_sources.py','build_global_product.py','build_master_release.py','build_master_completion.py','build_master_diary.py','build_master_interface.py','refresh_release_search.py','stamp_assets.py']:
        subprocess.run([sys.executable, str(ROOT/'tools'/script)], cwd=ROOT, check=True)
    manifest = json.loads((ROOT/'site.webmanifest').read_text(encoding='utf-8'))
    assert manifest['scope'] == '/' and manifest['id'] == '/'
    assert manifest['shortcuts'][0]['url'] == '/food-diary.html'
    html = (ROOT/'protein-value-calculator.html').read_text(encoding='utf-8')
    for currency in ['USD','CAD','GBP','EUR','AUD','NZD','MXN','JPY']:
        assert html.count('value="'+currency+'"') == 1, 'Duplicate or missing currency '+currency
    pages = json.loads((ROOT/'docs/global-product-release-2026-10-11/published-manifest.json').read_text(encoding='utf-8'))
    master = json.loads((ROOT/'docs/master-release-2026-10-12/published-manifest.json').read_text(encoding='utf-8'))
    completion = json.loads((ROOT/'docs/master-completion-2026-10-13/published-manifest.json').read_text(encoding='utf-8'))
    paths = [ROOT/p['path'] for p in pages+master+completion]+[ROOT/p for p in ['site.webmanifest','sw.js','search.html','privacy.html','protein-value-calculator.html','js/order-registry.json','js/canada-meals.json','js/market-definitions.js','index.html','ca/en/index.html','data/restaurant-presence.json']]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

before, after = integrate(), integrate()
assert before == after, 'Repeat integration changed public product output'
print('PASS: repeat integration, unique local currencies, app shortcuts and deterministic public product output.')
