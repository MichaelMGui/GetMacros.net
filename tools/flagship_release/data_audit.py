"""Independent, read-only restaurant release audit. Standard-library core.

Only writes docs/flagship-release-2026-10-18/data-audit. No shared data edits.
Source spot checks are separately recorded and never called visual screenshots.
"""
from pathlib import Path
from collections import Counter, defaultdict
from decimal import Decimal
from urllib.parse import urlparse
import math
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/flagship-release-2026-10-18/data-audit'
DATE = '2026-10-18'
NUTRIENTS = ('cal', 'p', 'c', 'fat', 'f', 'na', 'sugar', 'sat', 'trans', 'cholesterol')
CORE = ('cal', 'p', 'c', 'fat')
UNITS = {k: ('kcal' if k == 'cal' else 'mg' if k in ('na', 'cholesterol') else 'g') for k in NUTRIENTS}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def decimal(value):
    return Decimal(str(value))


def known(value):
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def issue(issues, severity, code, row, message, **extra):
    issues.append(dict(severity=severity, code=code, id=row.get('id'), market=row.get('market'), chain=row.get('chain'), name=row.get('name'), message=message, **extra))


def check_record(row, pool, sources, issues, legacy_market=None):
    market = row.get('market')
    if not market or row.get('country') != market:
        issue(issues, 'error', 'market-identity', row, 'Market and country differ or are absent.')
    if not str(row.get('id', '')).startswith(str(market) + '|') and legacy_market != market:
        issue(issues, 'error', 'id-market', row, 'Record ID is not prefixed by the country.')
    if row.get('restaurantMarketId') != str(market) + '|' + str(row.get('restaurantId')):
        issue(issues, 'error', 'restaurant-market', row, 'Restaurant/market identity contradicts its components.')
    if not row.get('name') or not row.get('serving'):
        issue(issues, 'error', 'missing-identity', row, 'Exact name or serving definition absent.')
    for field in NUTRIENTS:
        value = row.get(field)
        if value is None:
            continue
        if not known(value):
            issue(issues, 'error', 'invalid-number', row, 'Nutrient is negative, nonfinite or not numeric.', field=field, value=str(value))
            continue
        if row.get('units', {}).get(field) != UNITS[field]:
            issue(issues, 'error', 'nutrient-unit', row, 'Normalized nutrient has the wrong or missing unit.', field=field, unit=row.get('units', {}).get(field), expected=UNITS[field])
        if field in CORE + ('f', 'na', 'sugar', 'sat') and not row.get('nutrientProvenance', {}).get(field):
            issue(issues, 'error', 'nutrient-provenance', row, 'Published/calculated non-null field has no provenance.', field=field)
    if row.get('macroComplete') != all(known(row.get(f)) for f in CORE):
        issue(issues, 'error', 'macro-completeness', row, 'Core macro completeness does not match the actual known fields.')
    explicit_partial=(row.get('verificationStatus')=='official-calories-only-reviewed' and row.get('coverageStatus')=='calories-only' and row.get('macroComplete') is False and known(row.get('cal')) and all(row.get(k) is None for k in ('p','c','fat')))
    if row.get('finderSupported') and not explicit_partial and not (known(row.get('cal')) and known(row.get('p'))):
        issue(issues, 'error', 'finder-missing', row, 'Finder-enabled item lacks energy/protein.')
    for child, parent in [('sugar', 'c'), ('sat', 'fat')]:
        if known(row.get(child)) and known(row.get(parent)) and row[child] > row[parent]:
            difference = row[child] - row[parent]
            issue(issues, 'warning' if difference <= 0.5 else 'error', child + '-exceeds-' + parent, row, 'Subset nutrient exceeds its parent nutrient; inspect original source.', difference=round(difference, 5), child=row[child], parent=row[parent])
    grams = row.get('servingGrams')
    if grams is not None:
        if not known(grams) or grams <= 0:
            issue(issues, 'error', 'invalid-mass', row, 'Serving mass must be positive or unknown.', value=str(grams))
        elif grams > 10000:
            issue(issues, 'warning', 'large-mass', row, 'Source portion exceeds 10 kg; confirm catering/pack size.', grams=grams)
        elif all(known(row.get(k)) for k in ('p', 'c', 'fat')) and sum(row[k] for k in ('p', 'c', 'fat')) > grams * 1.12 + 2:
            issue(issues, 'error', 'macros-exceed-mass', row, 'Protein/carbohydrate/fat mass exceeds source serving mass beyond rounding tolerance.', grams=grams, macroMass=round(sum(row[k] for k in ('p', 'c', 'fat')), 3))
    if known(row.get('cal')) and row['cal'] > 5000:
        issue(issues, 'warning', 'large-calories', row, 'Over 5,000 kcal; confirm whole order/catering scope.', cal=row['cal'])
    if known(row.get('na')) and row['na'] > 20000:
        issue(issues, 'warning', 'large-sodium', row, 'Over 20,000 mg sodium; inspect serving scope.', sodium=row['na'])
    if all(known(row.get(k)) for k in CORE):
        energy = row['p'] * 4 + row['c'] * 4 + row['fat'] * 9
        if abs(energy - row['cal']) > max(50, row['cal'] * 0.25):
            issue(issues, 'warning', 'energy-screen', row, 'Large 4/4/9 difference; not itself proof of a label error (fiber/polyols/source factors can differ).', stated=row['cal'], screen=round(energy, 3))
    source = row.get('source')
    if not isinstance(source, str) or urlparse(source).scheme != 'https' or not urlparse(source).netloc:
        issue(issues, 'error', 'source-url', row, 'Source is not a concrete HTTPS URL.')
    if source not in sources:
        issue(issues, 'error', 'unregistered-source', row, 'Source URL not found in the staged official source registers.', source=source)
    else:
        hashes = {s.get('sha256') for s in sources[source]}
        if row.get('sourceHash') not in hashes:
            issue(issues, 'error', 'source-hash', row, 'Record source hash is absent from registered exact captures.', sourceHash=row.get('sourceHash'))
    if not row.get('sourcePage') or not row.get('sourceCaptureMethod'):
        issue(issues, 'error', 'source-location', row, 'Source row/page or capture method is missing.')
    for key in ('checked', 'retrievedAt', 'sourceDate'):
        if str(row.get(key, ''))[:10] > DATE:
            value = str(row.get(key, ''))[:10]
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                issue(issues, 'error', 'future-date', row, 'Record date is in the future.', field=key, value=row.get(key))
    native = row.get('nativeNutrients') or {}
    hundred = row.get('nativePer100g') or {}
    provenance = row.get('nutrientProvenance') or {}
    conversions = row.get('conversions') or []
    if known(row.get('cal')) and any(c.get('from') == 'kJ' and c.get('to') == 'cal' for c in conversions):
        if not known(native.get('kJ')):
            issue(issues, 'error', 'energy-conversion-source', row, 'kJ conversion lacks the exact source energy.')
        elif abs(decimal(row['cal']) - decimal(native['kJ']) / Decimal('4.184')) > Decimal('0.011'):
            issue(issues, 'error', 'energy-conversion', row, 'kJ-to-kcal conversion differs from source kJ /4.184.', sourceKj=native['kJ'], kcal=row['cal'])
    for field in CORE + ('f', 'sugar', 'sat'):
        method = provenance.get(field, {}).get('method', '').lower()
        if known(row.get(field)) and 'per-100' in method and known(hundred.get(field)):
            if not known(grams) or grams <= 0:
                issue(issues, 'error', 'per100-without-mass', row, 'Per-100g conversion lacks a source gram weight.', field=field)
            else:
                expected = decimal(hundred[field]) * decimal(grams) / 100
                if abs(decimal(row[field]) - expected) > Decimal('0.051'):
                    issue(issues, 'error', 'per100-conversion', row, 'Converted per-serving value disagrees with native per100g × serving grams.', field=field, expected=str(expected), value=row[field])
    if known(row.get('na')) and any(c.get('to') == 'na' and c.get('from') == 'salt' for c in conversions):
        method = provenance.get('na', {}).get('method', '').lower()
        salt = native.get('salt')
        if 'per-100' in method and known(hundred.get('salt')) and known(grams):
            salt = float(decimal(hundred['salt']) * decimal(grams) / 100)
        if not known(salt):
            issue(issues, 'error', 'salt-source', row, 'Salt conversion has no native salt value.')
        elif abs(decimal(row['na']) - decimal(salt) * 400) > Decimal('1.01'):
            issue(issues, 'error', 'salt-conversion', row, 'Normalized sodium disagrees with salt g ×400.', saltGrams=salt, sodium=row['na'])
    if known(row.get('na')) and any(c.get('to') == 'na' and c.get('from') == 'na' and c.get('fromUnit') == 'g' for c in conversions) and known(native.get('na')):
        if abs(decimal(row['na']) - decimal(native['na']) * 1000) > Decimal('1.01'):
            issue(issues, 'error', 'sodium-unit-conversion', row, 'Sodium g→mg conversion disagrees with source.')
    if row.get('verificationStatus') == 'calculated-from-official-components':
        parts = []
        for component in row.get('components', []):
            part = pool.get(component.get('id'))
            if not part:
                issue(issues, 'error', 'component-missing', row, 'Composed order references an absent exact component.', component=component)
                continue
            if part.get('market') != market:
                issue(issues, 'error', 'component-market', row, 'Composed order leaks another country’s food.')
            quantity = component.get('quantity', 1)
            if not known(quantity) or quantity <= 0:
                issue(issues, 'error', 'component-quantity', row, 'Component quantity invalid.')
            parts.append((part, quantity))
        for field in CORE + ('f', 'na', 'sugar', 'sat'):
            if any(part.get(field) is None for part, _ in parts):
                if row.get(field) is not None:
                    issue(issues, 'error', 'unknown-component-total', row, 'Unknown component became a known total.', field=field)
            elif parts:
                total = sum(decimal(part[field]) * decimal(q) for part, q in parts)
                if row.get(field) is None or abs(decimal(row[field]) - total) > Decimal('0.051'):
                    issue(issues, 'error', 'component-sum', row, 'Order total differs from exact component sum.', field=field, expected=str(total), value=row.get(field))


def check_source_samples(pool, by_group, issues):
    """Replay human-transcribed source samples; never infer all-row source review."""
    path = OUT / 'source-spot-checks.json'
    samples = json.loads(path.read_text(encoding='utf-8'))['observations']
    counts = Counter()
    for sample in samples:
        counts[sample['group']] += 1
        row = pool.get(sample['id'])
        if not row:
            issue(issues, 'error', 'sample-record-absent', sample, 'Independently checked source portion is absent from current inputs.')
            continue
        if row.get('sourceHash') != sample['sourceHash'] or row.get('source') != sample['sourceUrl']:
            issue(issues, 'error', 'sample-source-changed', row, 'Source of manually checked portion changed; recheck the sample.')
        source = ROOT / sample['sourceFile']
        if not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest() != sample['sourceHash']:
            issue(issues, 'error', 'sample-capture-changed', row, 'Original capture of manual sample changed or is absent.')
        for key, expected in sample['expectedNormalized'].items():
            actual = row.get(key)
            if expected is None:
                okay = actual is None
            else:
                okay = known(actual) and abs(decimal(actual) - decimal(expected)) <= Decimal('0.011')
            if not okay:
                issue(issues, 'error', 'source-sample-mismatch', row, 'Current normalized value differs from independently transcribed official source sample.', field=key, expected=expected, value=actual)
    for group in by_group:
        if counts[group] < 2:
            issue(issues, 'error', 'source-sample-coverage', dict(chain=group), 'Fewer than two independent original-source portion checks in country/chain group.')
    return dict(samplePortions=len(samples), marketChainGroups=len(counts), minimumPerGroup=min(counts.values()), method='Original official capture reading and numeric replay; no screenshot, laboratory or every-row human review implied.')


def audit():
    OUT.mkdir(parents=True, exist_ok=True)
    batches = [('uk', load('tools/flagship_release/uk_records.json')), ('markets', load('tools/flagship_release/markets_release_records.json'))]
    batches.append(('mexico-calories',load('tools/flagship_release/markets_mexico_calories.json')))
    registry = load('js/order-registry.json')['records']
    legacy_markets = {r['id']:r.get('market') for r in registry if r.get('id')}
    pool = {r['id']: r for r in registry if r.get('id')}
    all_rows = []
    for batch, data in batches:
        for scope in ('records', 'updates'):
            for row in data.get(scope, []):
                pool[row['id']] = row
                all_rows.append((batch, scope, row))
    source_rows = load('docs/flagship-release-2026-10-18/uk/source-register.json') + batches[1][1]['sources']+batches[2][1]['sources']
    sources = defaultdict(list)
    for row in source_rows:
        sources[row['url']].append(row)
    issues = []
    verified_files = set()
    for source in source_rows:
        file = ROOT / source['file']
        if str(file) in verified_files:
            continue
        verified_files.add(str(file))
        if not file.exists() or hashlib.sha256(file.read_bytes()).hexdigest() != source.get('sha256'):
            issue(issues, 'error', 'capture-hash', dict(chain=source.get('chain'), market=source.get('marketScope')), 'Registered capture file is absent or hash mismatch.', file=source['file'])
    by_group = defaultdict(list)
    seen_id, seen_identity = {}, {}
    for batch, scope, row in all_rows:
        key = (batch, scope, row['id'])
        if key in seen_id:
            issue(issues, 'error', 'duplicate-id', row, 'Duplicate ID within one staged scope.')
        seen_id[key] = row
        identity = (batch, scope, row['market'], row['restaurantId'], row['name'], row['serving'])
        if identity in seen_identity:
            previous = seen_identity[identity]
            issue(issues, 'warning', 'duplicate-named-serving', row, 'Same named serving has multiple identities; inspect edition/recipe distinction.', other=previous['id'])
        seen_identity[identity] = row
        check_record(row, pool, sources, issues, legacy_markets.get(row['id']) if scope == 'updates' else None)
        by_group[row['market'] + '|' + row['chain']].append(row)
    sample_checks = check_source_samples(pool, by_group, issues)
    checks = dict(checkedAt=DATE, inputRecords=len(all_rows), newRecords=sum(len(b['records']) for _, b in batches), refreshedRecords=sum(len(b.get('updates', [])) for _, b in batches), groups={k:len(v) for k,v in by_group.items()}, sourceCaptureFiles=len(verified_files), originalSourceSampleChecks=sample_checks, errorCount=sum(i['severity']=='error' for i in issues), warningCount=sum(i['severity']=='warning' for i in issues), issuesByCode=dict(Counter(i['code'] for i in issues)), inputHashes={str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['tools/flagship_release/uk_records.json','tools/flagship_release/markets_release_records.json','tools/flagship_release/markets_mexico_calories.json']},scope='Read-only data screens, source-file integrity and 60 source-sampled portions. No visual or lab verification inferred.')
    (OUT/'audit.json').write_text(json.dumps(dict(summary=checks, issues=issues), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    candidates = {key:[{k:r.get(k) for k in ('id','market','chain','name','serving','servingGrams','source','sourcePage','sourceHash','nativeNutrients','nativePer100g')+NUTRIENTS} for r in rows[:2]] for key, rows in by_group.items()}
    (OUT/'spot-check-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(checks,ensure_ascii=False,indent=2))
    for row in issues[:15]:
        print(json.dumps(row,ensure_ascii=False))
    return checks


def self_test():
    issues = []
    row = dict(id='CA|test|1',market='CA',country='US',restaurantId='test',restaurantMarketId='US|test',name='Fixture',serving='1',cal=float('nan'),p=-1,c=3,fat=1,sugar=5,sat=2,na=0,units={'cal':'kJ'},source='http://invalid.test',macroComplete=True,finderSupported=True)
    check_record(row,{}, {},issues)
    codes={i['code'] for i in issues}
    assert {'market-identity','restaurant-market','invalid-number','sugar-exceeds-c','sat-exceeds-fat','source-url','unregistered-source','source-location','macro-completeness','finder-missing'}<=codes
    assert not known(True) and not known(float('inf')) and known(0)
    clean = dict(id='CA|test|valid',market='CA',country='CA',restaurantId='test',restaurantMarketId='CA|test',name='Fixture',serving='100 g',servingGrams=100,cal=100,p=10,c=15,fat=0,f=1,na=400,sugar=5,sat=0,units=UNITS,source='https://test.invalid/menu',sourceHash='abc',sourcePage='row1',sourceCaptureMethod='fixture',macroComplete=True,finderSupported=True,nutrientProvenance={k:{'method':'source per portion'} for k in CORE+('f','na','sugar','sat')},nativeNutrients={'salt':1},conversions=[{'from':'salt','to':'na'}])
    registered = {clean['source']:[{'sha256':'abc'}]}
    fixtures = []
    def fixture(name, changes, expected):
        candidate = dict(clean, **changes)
        found = []
        check_record(candidate, {}, registered, found)
        actual_codes = {x['code'] for x in found}
        assert expected <= actual_codes, (name, expected, actual_codes)
        fixtures.append(name)
    base = []
    check_record(clean, {}, registered, base)
    assert not base, base
    fixture('wrong salt conversion', {'na':40}, {'salt-conversion'})
    fixture('wrong sodium grams', {'na':.4,'nativeNutrients':{'na':.4},'conversions':[{'from':'na','fromUnit':'g','to':'na'}]}, {'sodium-unit-conversion'})
    fixture('wrong kJ conversion', {'cal':80,'nativeNutrients':{'kJ':418.4},'conversions':[{'from':'kJ','to':'cal'}]}, {'energy-conversion'})
    fixture('per100g needs mass', {'servingGrams':None,'nativePer100g':{'p':10},'nutrientProvenance':dict(clean['nutrientProvenance'],p={'method':'per-100-g conversion'})}, {'per100-without-mass'})
    fixture('per100g scale error', {'servingGrams':50,'nativePer100g':{'p':10},'nutrientProvenance':dict(clean['nutrientProvenance'],p={'method':'per-100-g conversion'})}, {'per100-conversion'})
    fixture('zero mass rejected', {'servingGrams':0}, {'invalid-mass'})
    fixture('source hash mismatch', {'sourceHash':'bad'}, {'source-hash'})
    fixture('future source date', {'sourceDate':'2099-01-01'}, {'future-date'})
    fixture('incorrect normalized unit', {'units':dict(UNITS,na='g')}, {'nutrient-unit'})
    fixture('untraceable known nutrient', {'nutrientProvenance':{}}, {'nutrient-provenance'})
    part = dict(clean,id='CA|test|part')
    order = dict(clean, id='CA|test|order', verificationStatus='calculated-from-official-components', components=[{'id':part['id'],'quantity':2}])
    found=[]
    check_record(order,{part['id']:part},registered,found)
    assert 'component-sum' in {x['code'] for x in found}
    part['market']='US'
    part['f']=None
    found=[]
    check_record(order,{part['id']:part},registered,found)
    assert {'component-market','unknown-component-total'} <= {x['code'] for x in found}
    return dict(invalidFixture='rejected',nonfinite='rejected',booleanNutrients='rejected',explicitZero='retained',cleanFixture='accepted',conversionAndProvenanceRegressions=fixtures,wrongComponentSum='rejected',crossMarketComponent='rejected',unknownComponentTotal='rejected')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/'self-tests.json').write_text(json.dumps(self_test(),indent=2)+'\n',encoding='utf-8')
    summary = audit()
    sys.exit(1 if summary['errorCount'] else 0)
