"""Report the inspected Mexico sources without admitting unreviewed menu rows.

No network, shared data mutation, or inference from another country's menu.
The anonymous CMS is evidence for exclusions, not proof of a live local menu.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'docs/global-coverage-2026-10-17/restaurants/mexico-supplement'
DATE = '2026-10-17'


def read(name):
    return json.loads((DEST / name).read_text(encoding='utf-8'))


def write(name, value):
    (DEST / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def mexico_baseline():
    rows = json.loads((ROOT / 'js/order-registry.json').read_text(encoding='utf-8'))['records']
    return sorted([{key: row.get(key) for key in
                    ('id', 'chain', 'name', 'serving', 'servingGrams', 'cal', 'p', 'c',
                     'fat', 'f', 'na', 'sugar', 'sat', 'source', 'sourceVersion')}
                   for row in rows if row.get('market') == 'MX'], key=lambda row: row['id'])


def build():
    payload = read('bk-mx-public-counts.json')['result']
    source = next(row for row in read('retrieval.json')
                  if row['file'] == 'bk-mx-public-counts.json')
    withheld = []
    for item in payload['macroItems']:
        nutrition = item['nutrition']
        spanish_name = item['name'].get('es')
        reasons = ['Membership in a currently published Mexican menu and its exact local serving '
                   'was not verified. Anonymous CMS inclusion alone is insufficient.']
        if not spanish_name:
            reasons.append('No Spanish local product name in this object; legacy/template menu '
                           'objects coexist in this dataset. No country equivalence inferred.')
        if 'test' in (spanish_name or '').lower():
            reasons.append('Explicit PLU CONFIG TEST product; excluded from consumer menu coverage.')
        portion = re.fullmatch(r'(\d+(?:\.\d+)?)\s*Gramos', item.get('productSize') or '', re.I)
        if portion and nutrition.get('weight') is not None and float(portion[1]) != nutrition['weight']:
            reasons.append('Conflicting source portion: productSize is ' + item['productSize'] +
                           ' but nutrition.weight is ' + str(nutrition['weight']) + ' g. Neither chosen.')
        estimate = 4 * nutrition['proteins'] + 4 * nutrition['carbohydrates'] + 9 * nutrition['fat']
        if abs(nutrition.get('calories', 0) - estimate) > max(65, nutrition.get('calories', 0) * 0.25):
            reasons.append('Large energy/macronutrient discrepancy: source calories ' +
                           str(nutrition.get('calories')) + '; 4/4/9 screening estimate ' +
                           str(round(estimate, 6)) + ' kcal. No corrected values invented.')
        withheld.append({'sourceObjectId': item['_id'], 'name': item['name'],
                         'sourceUpdatedAt': item['_updatedAt'],
                         'productSize': item.get('productSize'), 'nativeNutrients': nutrition,
                         'source': source['url'], 'sourceHash': source['sha256'],
                         'sourcePage': 'result.macroItems[_id=' + item['_id'] + ']',
                         'accepted': False, 'reasons': reasons})
    write('withheld.json', withheld)
    baseline = mexico_baseline()
    assert len(baseline) == 100 and {row['chain'] for row in baseline} == {'Subway'}
    report = {'reviewedAt': DATE, 'status': 'withheld-source-quality-and-access',
              'acceptedRecords': 0, 'updates': 0, 'presenceUpserts': 0, 'guideBriefs': 0,
              'mexicoBaseline': {'records': len(baseline), 'chain': 'Subway',
                                 'identityNutritionSourceSha256': digest(baseline)},
              'publicDataset': {'nutritionItems': payload['nutritionItems'],
                                'fatItems': payload['fatItems'], 'proteinItems': payload['proteinItems'],
                                'carbItems': payload['carbItems'], 'completeMacroObjects': len(withheld),
                                'withoutSpanishName': sum(not r['name'].get('es') for r in withheld),
                                'explicitTestName': sum('test' in r['name'].get('es', '').lower()
                                                        for r in withheld),
                                'menuNames': [row['name'] for row in payload['menus']],
                                'scope': 'Anonymous public CMS objects, not a verified current-menu count.'},
              'sourcePayloadHash': source['sha256'],
              'limits': ['McDonald’s Mexico direct downloads returned HTTP 403; web text exposes '
                         'nutrition accordion headings without numerical values.',
                         'No enabled browser surface was available to operate those public accordions.',
                         'Burger King legacy Big King page reports only 224 g and 570 kcal; '
                         'protein/carbohydrate/fat values are absent.',
                         'Burger King regional nutrition links point to a burgerking.es storage path; '
                         'not established as Mexican data.',
                         'No KFC Mexico source rows, foreign substitutions, private credentials, '
                         'guessed portions, image copies, or unknown-to-zero conversion used.']}
    write('summary.json', report)
    empty = {'schemaVersion': 1, 'reviewedAt': DATE,
             'scope': 'Withheld supplement: inspected sources do not establish usable exact current '
                      'Mexican menu portions plus complete macros. No release changes.',
             'marketCounts': {}, 'chainCounts': {}, 'records': [], 'updates': []}
    target = ROOT / 'tools/global_coverage_2026_10_17/mexico-supplement-records.json'
    target.write_text(json.dumps(empty, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'accepted': 0, 'withheldObjects': len(withheld),
                      'existingMexicoRecords': len(baseline)}, ensure_ascii=False))


if __name__ == '__main__':
    build()
