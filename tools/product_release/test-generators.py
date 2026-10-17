"""Regression checks for repeatable product integration and app configuration."""
from pathlib import Path
import hashlib, json, re, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]

def integrate():
    for script in ['restore_asset_sources.py','build_global_product.py','build_master_release.py','build_master_completion.py','build_master_diary.py','build_master_interface.py','build_clarity_release.py','build_global_coverage_release.py','refresh_release_search.py','stamp_assets.py']:
        subprocess.run([sys.executable, str(ROOT/'tools'/script)], cwd=ROOT, check=True)
    manifest = json.loads((ROOT/'site.webmanifest').read_text(encoding='utf-8'))
    assert manifest['scope'] == '/' and manifest['id'] == '/'
    assert manifest['shortcuts'][0]['url'] == '/food-diary.html'
    html = (ROOT/'protein-value-calculator.html').read_text(encoding='utf-8')
    market_definitions=json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
    for currency in sorted(set(['USD','CAD','GBP','EUR','AUD','NZD','MXN','JPY'])|{info['currency'] for info in market_definitions.values()}):
        assert html.count('value="'+currency+'"') == 1, 'Duplicate or missing currency '+currency
    pages = json.loads((ROOT/'docs/global-product-release-2026-10-11/published-manifest.json').read_text(encoding='utf-8'))
    master = json.loads((ROOT/'docs/master-release-2026-10-12/published-manifest.json').read_text(encoding='utf-8'))
    completion = json.loads((ROOT/'docs/master-completion-2026-10-13/published-manifest.json').read_text(encoding='utf-8'))
    current=json.loads((ROOT/'docs/global-coverage-2026-10-17/integration.json').read_text(encoding='utf-8'))['pages']
    paths = [ROOT/p['path'] for p in pages+master+completion]+[ROOT/p for p in ['site.webmanifest','sw.js','search.html','privacy.html','protein-value-calculator.html','js/order-registry.json','js/canada-meals.json','js/market-definitions.js','index.html','ca/en/index.html','data/restaurant-presence.json']]
    paths += [ROOT/p['path'] for p in current]
    paths += list((ROOT/'data/restaurant-foods').glob('*'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

before, after = integrate(), integrate()
assert before == after, 'Repeat integration changed public product output'
print('PASS: repeat integration, unique local currencies, app shortcuts and deterministic public product output.')
