"""Research-time selected-value checks; remove unrelated response geolocation.

Run after editorial_restaurant_sources.cjs. No network or public-site mutation.
The Wagamama retained artifact is explicitly the decoded official menu payload,
not a claim to preserve every byte of a response containing request metadata.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from flagship_release.uk_extract import nuxt_extract, leon_extract

DIRECTORY = ROOT / 'docs/ultimate-release-2026-10-19/editorial/sources'
records = json.loads((DIRECTORY.parent / 'restaurant-records.json').read_text(encoding='utf-8'))['records']
raw_path = DIRECTORY / 'GB-wagamama.html'
menu_path = DIRECTORY / 'GB-wagamama-menu.json'
if raw_path.exists():
    document = nuxt_extract(raw_path.read_text(encoding='utf-8'))
    menu_path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    checks_path = DIRECTORY / 'source-checks.json'
    checks = json.loads(checks_path.read_text(encoding='utf-8'))
    for check in checks:
        if check['market'] == 'GB' and check['chain'] == 'Wagamama':
            check['responseSha256'] = check['sha256']
            check['sha256'] = hashlib.sha256(menu_path.read_bytes()).hexdigest()
            check['file'] = menu_path.name
            check['artifactContentType'] = 'application/json'
            check['captureMethod'] = 'Decoded official server-rendered menu data; unrelated request metadata omitted'
    checks_path.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    raw_path.unlink()  # Exact named nonrecursive file within this workstream only.
else:
    document = json.loads(menu_path.read_text(encoding='utf-8'))


def items(section):
    yield from section.get('Recipes', [])
    for child in section.get('Sections', []):
        yield from items(child)


fresh = {}
for item in items(document['Menus'][0]):
    for size in item['Sizes']:
        fresh[item['Ident'] + '|' + size['Code']] = item

results = []
names = {'cal': 'energy (kcal)', 'p': 'protein (g)', 'c': 'carb (g)', 'fat': 'fat (g)', 'f': 'fibre (g)', 'sugar': 'of which sugars (g)'}
for row in records:
    if row['chain'] != 'Wagamama':
        continue
    item = fresh[row['sourcePage']]
    lookup = {value['Desc'].lower(): value for value in item['Nutrs']}
    checks = {field: float(lookup[label]['PerServ'].replace(',', '')) == row[field] for field, label in names.items()}
    checks['salt'] = float(lookup['salt (g)']['PerServ']) == row['nativeNutrients']['salt']
    checks['na'] = float(lookup['sodium (g)']['PerServ']) * 1000 == row['na']
    assert all(checks.values()), (row['name'], checks)
    results.append({'id': row['id'], 'sourcePage': row['sourcePage'], 'name': row['name'], 'checks': checks, 'result': 'matches current official embedded source'})

_, leon = leon_extract((DIRECTORY / 'GB-leon.html').read_text(encoding='utf-8'))
leon_by_id = {item['_id']: item for item in leon}
for row in records:
    if row['chain'] != 'LEON':
        continue
    fresh = leon_by_id[row['sourcePage']]['nutritionInfo']
    names = {'cal': 'kcal', 'p': 'protein', 'c': 'carb', 'fat': 'fat', 'f': 'fibre', 'sugar': 'sugar'}
    checks = {field: fresh[label] == row[field] for field, label in names.items()}
    checks['salt'] = fresh['salt'] == row['nativeNutrients']['salt']
    checks['grams'] = fresh['totalPortionWeight'] == row['servingGrams']
    assert all(checks.values()), (row['name'], checks)
    results.append({'id': row['id'], 'sourcePage': row['sourcePage'], 'name': row['name'], 'checks': checks, 'result': 'matches current official embedded source'})

(DIRECTORY / 'selected-dynamic-values.json').write_text(json.dumps({'checkedAt': '2026-10-19', 'selectedRecords': results}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'{len(results)} current dynamic source rows match selected nutrients; unrelated request metadata excluded')
