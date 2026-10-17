"""Audit and stage an all-brand OFF expansion without changing production data.

The retained 2026-10-13 official TSV is a dated snapshot, not a new retrieval.
Only source-attributed supported markets and explicit matching g/mL servings
are accepted. This deliberately avoids guessing whether a bare _100g column
means 100 g or 100 mL. No image, rating, or marketing fields are copied.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import time
from contextlib import ExitStack

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/master_completion'))
import grocery_import_off as previous

RAW = previous.RAW
OUT = ROOT / 'docs/global-coverage-2026-10-17/off'
DATE = '2026-10-13'
AUDIT_DATE = '2026-10-17'
MARKETS = previous.MARKETS
MAP = previous.MAP
SOURCE_FIELDS = list(dict.fromkeys(previous.SOURCE_FIELDS + ['product_quantity', 'states_tags']))
text = previous.text
number = previous.number
barcode = previous.barcode
source_serving = previous.source_serving


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def hash_value(value):
    return previous.base.hash_value(value)


def json_gzip(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as handle:
        with gzip.GzipFile(fileobj=handle, filename='', mode='wb', mtime=0) as archive:
            archive.write(encoded(value))


def source_market_codes(row):
    tags = set(str(row.get('countries_tags') or '').split(','))
    return [market for tag, market in MARKETS.items() if tag in tags]


def validate(row):
    """Apply factual quality boundaries, with no brand selection or filling."""
    markets = source_market_codes(row)
    if not markets:
        return None, 'no-supported-source-market'
    name = str(row.get('product_name') or '').strip()
    brand = str(row.get('brands') or '').strip()
    if not name or not brand:
        return None, 'missing-product-or-brand'
    code = str(row.get('code') or '').strip()
    gtin = barcode(code)
    if not gtin:
        return None, 'invalid-or-missing-barcode'
    if row.get('no_nutrition_data') == 'on':
        return None, 'source-no-nutrition'
    if any(tag in str(row.get('categories_tags') or '') for tag in
           ['en:food-supplements', 'en:baby-foods', 'en:infant-formula']):
        return None, 'excluded-supplement-or-infant-product'
    if row.get('data_quality_errors_tags'):
        return None, 'source-quality-errors'
    serving = source_serving(row)
    if not serving:
        return None, 'ambiguous-or-missing-serving-unit'
    native = {key: number(row.get(field)) for key, (field, _) in MAP.items()}
    values = {key: native[key] * factor if native[key] is not None else None
              for key, (_, factor) in MAP.items()}
    if values['cal'] is None:
        kj = number(row.get('energy-kj_100g'))
        if kj is not None:
            values['cal'] = kj / 4.184
    if not any(values[key] is not None for key in ['cal', 'p', 'c', 'fat']):
        return None, 'missing-core-nutrition'
    if values['cal'] == 0 and any(values[key] is not None and values[key] > 1 for key in ['p', 'fat']):
        return None, 'zero-energy-positive-macros-pending-label-or-rounding-review'
    if (values['cal'] is not None and values['cal'] > 950) or any(
            values[key] is not None and values[key] > 100.5
            for key in ['p', 'c', 'fat', 'f', 'sugar', 'sat']):
        return None, 'implausible-source-density'
    if all(values[key] is not None for key in ['p', 'c', 'fat']) and sum(values[key] for key in ['p', 'c', 'fat']) > 110:
        return None, 'contradictory-core-density'
    if values['sugar'] is not None and values['c'] is not None and values['sugar'] > values['c'] + 1:
        return None, 'sugars-exceed-carbohydrate'
    if values['sat'] is not None and values['fat'] is not None and values['sat'] > values['fat'] + 1:
        return None, 'saturated-exceeds-total-fat'
    return {'markets': markets, 'code': code, 'gtin': gtin, 'name': name, 'brand': brand,
            'serving': serving, 'native': native, 'values': values}, None


def rows(path=RAW):
    csv.field_size_limit(100_000_000)
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        if not set(previous.SOURCE_FIELDS) <= set(reader.fieldnames):
            raise ValueError('Official source schema changed: required fields missing')
        yield from reader


def formulation(row, values, market):
    return hash_value({'barcode': values['gtin'], 'market': market,
                       'name': text(values['name']), 'brand': text(values['brand']),
                       'package': row.get('quantity') or '',
                       'ingredients': text(row.get('ingredients_text') or ''),
                       'serving': values['serving']})


def normalize(row):
    parsed, reason = validate(row)
    if reason:
        return [], reason
    source_values = dict(parsed['values'])
    for key in previous.base.NUTRIENTS:
        source_values.setdefault(key, None)
    serving = parsed['serving']
    volume = serving['unit'] == 'ml'
    nutrients = {key: value * serving['amount'] / 100 if volume and value is not None else value
                 for key, value in source_values.items()}
    name = parsed['name']
    shown_name = name if len(name) <= 240 else name[:237].rstrip() + '…'
    flags = ['Open Food Facts community record imported; not independently verified against the current package.',
             'Community country tags indicate reported markets, not current store stock or a guarantee of the local formulation.',
             'Carbohydrate retains the OFF carbohydrates_100g field. This TSV does not establish whether the package uses total or available carbohydrate; no fiber adjustment is made.']
    if len(parsed['markets']) > 1:
        flags.append('One source record is tagged for multiple markets; confirm the exact local package before logging.')
    if volume:
        flags.append('Uses the named milliliter serving; no gram weight or density is assumed.')
    if not all(nutrients[key] is not None for key in ['cal', 'p', 'c', 'fat']):
        flags.append('Some core nutrition fields are unavailable; unknown values are not zero.')
    provenance = {key: {'sourceField': field, 'sourceValue': parsed['native'][key], 'unitFactor': factor}
                  for key, (field, factor) in MAP.items() if parsed['native'][key] is not None}
    if parsed['native']['cal'] is None and source_values['cal'] is not None:
        provenance['cal'] = {'sourceField': 'energy-kj_100g', 'sourceValue': number(row.get('energy-kj_100g')), 'unitFactor': 1 / 4.184}
    output = []
    for market in parsed['markets']:
        record = {'id': 'branded:off:' + parsed['code'] + ':' + market, 'name': shown_name,
                  'brand': parsed['brand'], 'brandName': parsed['brand'], 'brandOwner': row.get('brand_owner') or None,
                  'type': 'branded', 'market': market, 'markets': parsed['markets'], 'language': 'und',
                  'category': row.get('categories_en') or 'Packaged products', 'barcode': parsed['code'],
                  'barcodeNormalized': parsed['gtin'], 'package': row.get('quantity') or None,
                  'formulation': formulation(row, parsed, market), 'ingredients': row.get('ingredients_text') or None,
                  'sourceId': 'off-products-' + DATE, 'sourceOrigin': 'Open Food Facts — community product records',
                  'sourceRef': parsed['code'], 'sourceUrl': 'https://world.openfoodfacts.org/product/' + parsed['code'],
                  'sourcePublished': None, 'sourceChecked': None, 'sourceModified': row.get('last_modified_datetime') or None,
                  'labelDate': None, 'retrievedAt': DATE, 'sourceRelease': DATE + ' official bulk export retrieval',
                  'status': 'community-label-imported',
                  'basis': {'amount': 1, 'unit': 'serving'} if volume else {'amount': 100, 'unit': 'g'},
                  'nutrients': nutrients, 'portions': [] if volume else [{'id': 'source-serving', 'label': serving['label'], 'grams': serving['amount']}],
                  'serving': serving['label'], 'sourceServing': serving,
                  'sourcePer100': {'unit': serving['unit'], 'nutrients': source_values}, 'provenance': provenance,
                  'provenanceBasis': {'method': 'OFF normalized as-sold field; standard source grams converted to displayed units',
                                      'sourceBasis': '100 ' + serving['unit'], 'displayFactor': serving['amount'] / 100 if volume else 1},
                  'carbohydrateDefinition': 'source-reported; total-versus-available not established by retained TSV',
                  'flags': flags, 'availability': 'Community-reported country attribution; current local package and store availability not independently established.',
                  'license': 'ODbL-1.0', 'licenseUrl': 'https://opendatacommons.org/licenses/odbl/1-0/',
                  'contentsLicense': 'DbCL-1.0', 'attribution': 'Contains information from Open Food Facts, made available under the Open Database License (ODbL).',
                  'attributionUrl': 'https://world.openfoodfacts.org/', 'redistributionUrl': '/data/branded-foods/off/source-records.ndjson.gz'}
        if shown_name != name:
            record['sourceName'] = name
        record['version'] = hash_value(record)
        output.append(record)
    return output, None


def standalone_normalizer():
    """Export the transformation itself with only Python standard-library dependencies."""
    import inspect
    preamble = '''"""Open Food Facts 2026-10-13 TSV subset normalization, audited 2026-10-17.
ODbL derivative database; individual contents DbCL. No product images copied.
Run: python normalization.py source-records.ndjson.gz > normalized.ndjson
Source carbohydrate definition is retained; fiber is never added or removed.
"""
import gzip, hashlib, json, math, re, sys, unicodedata
from types import SimpleNamespace
def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
def hash_value(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
'''
    constants = '\nDATE = ' + repr(DATE) + '\nMARKETS = ' + repr(MARKETS) + '\nMAP = ' + repr(MAP) + '\n'
    compatibility = 'previous = SimpleNamespace(base=SimpleNamespace(NUTRIENTS=' + repr(list(previous.base.NUTRIENTS)) + '))\n'
    functions = '\n\n'.join(inspect.getsource(function) for function in
                            [text, number, barcode, source_serving, source_market_codes, validate, formulation, normalize])
    cli = '''
if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python normalization.py source-records.ndjson.gz')
    with gzip.open(sys.argv[1], 'rt', encoding='utf-8') as source:
        for line in source:
            records, reason = normalize(json.loads(line))
            if reason:
                raise SystemExit('Source subset failed normalization: ' + reason)
            for record in records:
                print(json.dumps(record, ensure_ascii=False, separators=(',', ':')))
'''
    return preamble + constants + compatibility + functions + cli


def stage(path=RAW, output=OUT / 'partition'):
    """Bound memory with 16 temporary compressed buckets and compact sort data."""
    output = output.resolve()
    if output == previous.OUT.resolve() or not output.is_relative_to(OUT.resolve()):
        raise ValueError('Expansion staging must remain inside the dedicated OFF evidence directory')
    if (output / 'manifest.json').exists():
        raise ValueError('A staged manifest already exists; use a fresh staging directory')
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    source_path = output / 'source-records.ndjson.gz'
    candidates = {}
    winners = {}
    source_codes = set()
    rejects = Counter()
    quarantine = []
    total = 0
    source_bytes = 0
    with source_path.open('wb') as source_file:
        with gzip.GzipFile(fileobj=source_file, filename='', mode='wb', mtime=0) as source_archive:
            for total, row in enumerate(rows(path), 1):
                parsed, reason = validate(row)
                if reason:
                    rejects[reason] += 1
                    if reason == 'zero-energy-positive-macros-pending-label-or-rounding-review':
                        quarantine.append({'code': row['code'], 'name': row['product_name'], 'brand': row['brands'], 'countries': row['countries_tags'],
                                           'reason': reason, 'sourceUrl': 'https://world.openfoodfacts.org/product/' + row['code'],
                                           'nativePer100': {k: row.get(MAP[k][0]) for k in ['cal', 'p', 'c', 'fat']}})
                    continue
                code = parsed['code']
                if code in source_codes:
                    raise ValueError('Duplicate source code needs explicit version resolution: ' + code)
                source_codes.add(code)
                payload = encoded({key: row.get(key, '') for key in SOURCE_FIELDS}) + b'\n'
                source_archive.write(payload)
                source_bytes += len(payload)
                for market in parsed['markets']:
                    identity = formulation(row, parsed, market)
                    record_id = 'branded:off:' + code + ':' + market
                    rank = (row.get('last_modified_datetime') or '', record_id)
                    key = (parsed['gtin'], market, identity)
                    old = winners.get(key)
                    if old and candidates[old] >= rank:
                        rejects['duplicate-same-identity-older-source'] += 1
                        continue
                    if old:
                        candidates.pop(old)
                        rejects['duplicate-same-identity-older-source'] += 1
                    winners[key] = record_id
                    candidates[record_id] = rank
                if total % 500000 == 0:
                    print(json.dumps({'stageRead': total, 'profiles': len(candidates), 'elapsedSeconds': round(time.monotonic() - started)}), flush=True)
    if not candidates:
        raise ValueError('No eligible source products; staged partition not published')
    ordered = sorted(candidates, key=candidates.get, reverse=True)
    ordinals = {record_id: ordinal for ordinal, record_id in enumerate(ordered)}
    del candidates, winners, ordered, source_codes
    buckets = [output / ('off-spool-' + format(n, 'x') + '.ndjson.gz') for n in range(16)]
    metadata = {}
    markets = defaultdict(list)
    brands = Counter()
    market_brands = defaultdict(Counter)
    tokens = defaultdict(lambda: defaultdict(list))
    barcodes = defaultdict(lambda: defaultdict(list))
    versions = []
    count = 0
    normalized_bytes = 0
    with ExitStack() as stack:
        bucket_archives = [stack.enter_context(gzip.GzipFile(fileobj=stack.enter_context(file.open('wb')), filename='', mode='wb', mtime=0)) for file in buckets]
        with gzip.open(source_path, 'rt', encoding='utf-8') as source:
            for line in source:
                selected, reason = normalize(json.loads(line))
                if reason:
                    raise AssertionError('Staged source no longer passes: ' + reason)
                for record in selected:
                    ordinal = ordinals.get(record['id'])
                    if ordinal is None:
                        continue
                    record['catalogOrdinal'] = ordinal
                    shard = hashlib.sha256(record['id'].encode()).hexdigest()[:3]
                    payload = encoded(record) + b'\n'
                    normalized_bytes += len(payload)
                    bucket_archives[int(shard[0], 16)].write(payload)
                    meta = {key: record.get(key) for key in ['id', 'name', 'type', 'category', 'market', 'brand', 'barcode', 'barcodeNormalized', 'formulation', 'sourceId', 'package', 'status']}
                    meta.update({'shard': shard, 'ordinal': ordinal, 'search': text(' '.join([record.get('sourceName') or record['name'], record['brand'], record.get('brandOwner') or '']))})
                    metadata[ordinal] = meta
                    for token in set(meta['search'].split()):
                        if token:
                            tokens[token[:2]][token].append(ordinal)
                    barcodes[record['barcodeNormalized'][:3]][record['barcodeNormalized']].append(ordinal)
                    markets[record['market']].append(ordinal)
                    brands[record['brand']] += 1
                    market_brands[record['market']][record['brand']] += 1
                    versions.append((record['id'], record['version']))
                    count += 1
    if count != len(ordinals):
        raise AssertionError('Source-to-index count mismatch')
    record_shards = []
    with (output / 'records.ndjson.gz').open('wb') as export_file:
        with gzip.GzipFile(fileobj=export_file, filename='', mode='wb', mtime=0) as export:
            for bucket in buckets:
                grouped = defaultdict(list)
                with gzip.open(bucket, 'rt', encoding='utf-8') as source:
                    for line in source:
                        record = json.loads(line)
                        grouped[hashlib.sha256(record['id'].encode()).hexdigest()[:3]].append(record)
                for shard, records in sorted(grouped.items()):
                    records.sort(key=lambda record: record['catalogOrdinal'])
                    json_gzip(output / 'records' / (shard + '.json.gz'), records)
                    record_shards.append(shard)
                    for record in records:
                        export.write(encoded(record) + b'\n')
                bucket.unlink()
    index_pages = []
    for start in range(0, count, 64):
        page = str(start // 64).zfill(4)
        index_pages.append(page)
        json_gzip(output / 'index' / (page + '.json.gz'), [metadata[n] for n in range(start, min(start + 64, count))])
    for prefix, postings in sorted(tokens.items()):
        json_gzip(output / 'tokens' / (prefix + '.json.gz'), {token: sorted(ids) for token, ids in sorted(postings.items())})
    for prefix, postings in sorted(barcodes.items()):
        json_gzip(output / 'barcodes' / (prefix + '.json.gz'), {code: sorted(ids) for code, ids in sorted(postings.items())})
    for market, ids in sorted(markets.items()):
        json_gzip(output / 'markets' / (market + '.json.gz'), sorted(ids))
        json_gzip(output / 'brands' / (market + '.json.gz'), dict(sorted(market_brands[market].items())))
    previous_manifest = json.loads((ROOT / 'data/branded-foods/off/manifest.json').read_text(encoding='utf-8'))
    source = dict(previous_manifest['source'])
    source.update({'scope': 'All source brands in eight existing supported markets; explicit g/mL servings and quality gates. Community imports, not full retailer inventory.',
                   'quality': 'Identity, source serving units and arithmetic checked. Source community data are not independently current-package verified.',
                   'normalizationAuditDate': AUDIT_DATE,
                   'carbohydrateDefinition': 'Retained carbohydrates_100g field; total-versus-available not established by TSV. No fiber adjustment.'})
    records_version = hash_value(sorted(versions))
    posting_version = hash_value({market: sorted(ids) for market, ids in sorted(markets.items())})
    manifest = {'schemaVersion': 1, 'publishedAt': AUDIT_DATE, 'profileCount': count,
                'markets': {market: len(ids) for market, ids in sorted(markets.items())}, 'brandCount': len(brands),
                'version': hash_value({'records': records_version, 'marketPostings': posting_version}), 'recordsVersion': records_version,
                'source': source, 'jsonEncoding': 'gzip', 'indexPageSize': 64, 'indexPages': index_pages,
                'tokenPrefixes': sorted(tokens), 'barcodePrefixes': sorted(barcodes), 'recordShardPrefix': 3, 'recordShards': sorted(record_shards),
                'marketPostings': True, 'marketPostingPrefix': 'markets', 'marketPostingsVersion': posting_version, 'brandCountsPrefix': 'brands',
                'searchPolicy': 'Exact barcode first; brand/name tokens; source modified date descending. Market, package and formulation identities remain distinct.',
                'availability': 'Community source labels, not live retailer inventory or independent package verification.',
                'derivativeLicense': 'ODbL-1.0', 'downloadUrl': '/data/branded-foods/off/records.ndjson.gz',
                'normalizationUrl': '/data/branded-foods/off/normalization.py'}
    dump(output / 'quarantined.json', {'status': 'excluded-pending-label-or-rounding-review', 'license': 'ODbL-1.0',
                                     'attribution': source['attribution'], 'records': sorted(quarantine, key=lambda row: row['code'])})
    (output / 'normalization.py').write_text(standalone_normalizer(), encoding='utf-8')
    (output / 'RIGHTS.txt').write_text((previous.OUT / 'RIGHTS.txt').read_text(encoding='utf-8') + '\nExpansion audited 2026-10-17 from retained 2026-10-13 snapshot. All brands in existing markets; no new retrieval or independent label verification claimed. Source carbohydrate definition is not changed or fiber-adjusted. Gzip JSON shards are directly downloadable; decompress as UTF-8 JSON.\n', encoding='utf-8')
    dump(output / 'manifest.json', manifest)
    sizes = Counter()
    for file in output.rglob('*'):
        if file.is_file():
            sizes[file.parent.name if file.parent != output else file.name] += file.stat().st_size
    report = {'sourceRowsRead': total, 'selectedSourceProducts': sum(1 for _ in gzip.open(source_path, 'rt', encoding='utf-8')),
              'publishedMarketProfiles': count, 'byMarket': manifest['markets'], 'additionalByMarket': {m: manifest['markets'][m] - previous_manifest['markets'].get(m, 0) for m in manifest['markets']},
              'sourceSnapshotRetrievedAt': DATE, 'auditDate': AUDIT_DATE, 'sourceSha256': source['sha256'],
              'sourceCompressedBytes': path.stat().st_size, 'selectedSourceUncompressedBytes': source_bytes,
              'normalizedUncompressedBytes': normalized_bytes, 'stagedBytesByPart': dict(sizes), 'stagedBytesTotal': sum(sizes.values()),
              'quarantinedSourceProducts': len(quarantine), 'rejections': dict(rejects), 'version': manifest['version'],
              'elapsedSeconds': round(time.monotonic() - started, 3)}
    dump(OUT / 'off-stage-report.json', report)
    print(json.dumps(report, indent=2), flush=True)
    return report


def audit(path=RAW, output=OUT):
    output.mkdir(parents=True, exist_ok=True)
    prior = json.loads((ROOT / 'data/branded-foods/off/manifest.json').read_text(encoding='utf-8'))
    counts = Counter()
    available = Counter()
    accepted = Counter()
    units = Counter()
    brand_counts = {market: Counter() for market in MARKETS.values()}
    samples = {market: [] for market in MARKETS.values()}
    dates = Counter()
    seen = set()
    total = 0
    started = time.monotonic()
    for total, row in enumerate(rows(path), 1):
        markets = source_market_codes(row)
        available.update(markets)
        values, reason = validate(row)
        if reason:
            counts[reason] += 1
        else:
            for market in values['markets']:
                key = (values['gtin'], market, row.get('product_name'), row.get('brands'), row.get('quantity'), row.get('ingredients_text'), row.get('serving_size'), row.get('serving_quantity'))
                if key in seen:
                    counts['duplicate-same-source-identity'] += 1
                    continue
                seen.add(key)
                accepted[market] += 1
                brand_counts[market][values['brand']] += 1
                units[values['serving']['unit']] += 1
                if len(samples[market]) < 3:
                    samples[market].append({k: row.get(k) for k in ['code', 'product_name', 'brands', 'quantity', 'serving_size', 'last_modified_datetime']})
            dates[str(row.get('last_modified_datetime') or '')[:10]] += 1
        if total % 500000 == 0:
            print(json.dumps({'read': total, 'acceptedProfiles': sum(accepted.values()), 'elapsedSeconds': round(time.monotonic() - started)}), flush=True)
    meta = json.loads((Path(str(path) + '.json')).read_text(encoding='utf-8'))
    report = {'auditDate': AUDIT_DATE, 'sourceRetrievedAt': DATE, 'sourceUrl': previous.SOURCE_URL,
              'sourceCompressedBytes': path.stat().st_size, 'sourceMetadata': meta,
              'sourceRowsRead': total, 'availableMarketTaggedRows': dict(available),
              'acceptedMarketProfiles': dict(accepted), 'currentProductionMarketProfiles': prior['markets'],
              'additionalProfilesBeforeCanonicalDedupe': {m: accepted[m] - prior['markets'].get(m, 0) for m in sorted(accepted)},
              'acceptedDistinctSourceBrandStrings': {m: len(b) for m, b in brand_counts.items()},
              'acceptedSourceServingUnits': dict(units), 'rejections': dict(counts),
              'acceptedSourceModifiedRange': [min(d for d in dates if d), max(dates)],
              'estimatedNormalizedUncompressedBytes': sum(accepted.values()) * 5300,
              'estimatedNormalizedGzipBytes': sum(accepted.values()) * 420,
              'estimateNote': 'Planning estimate using existing production record size; staging will measure exact compressed/sharded sizes.',
              'policy': 'All source brands; explicit matching source g/mL serving; supported source country tags; existing nutrient, GTIN and quality gates.',
              'missingServingPolicy': 'TSV _100g alone is ambiguous between 100g and 100mL. Missing source unit remains excluded pending explicit basis evidence.',
              'samples': samples, 'elapsedSeconds': round(time.monotonic() - started, 3)}
    dump(output / 'off-audit.json', report)
    print(json.dumps({k: report[k] for k in ['sourceRowsRead', 'availableMarketTaggedRows', 'acceptedMarketProfiles', 'additionalProfilesBeforeCanonicalDedupe', 'acceptedDistinctSourceBrandStrings', 'estimatedNormalizedUncompressedBytes', 'estimatedNormalizedGzipBytes', 'elapsedSeconds']}, indent=2), flush=True)
    return report


def footprint(path=RAW, output=OUT):
    """Measure the retained archive without extracting its multi-GB TSV."""
    length = 0
    started = time.monotonic()
    with gzip.open(path, 'rb') as source:
        while chunk := source.read(8 * 1024 * 1024):
            length += len(chunk)
    with path.open('rb') as source:
        sha = hashlib.file_digest(source, 'sha256').hexdigest()
    report = {'sourceRetrievedAt': DATE, 'auditDate': AUDIT_DATE,
              'compressedBytes': path.stat().st_size, 'uncompressedTsvBytes': length,
              'sha256': sha, 'elapsedSeconds': round(time.monotonic() - started, 3)}
    dump(output / 'off-source-footprint.json', report)
    print(json.dumps(report, indent=2), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'stage', 'footprint'])
    parser.add_argument('--source', type=Path, default=RAW)
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    if args.command == 'audit':
        audit(args.source, args.output)
    elif args.command == 'footprint':
        footprint(args.source, args.output)
    else:
        stage(args.source, args.output / 'partition')


if __name__ == '__main__':
    main()
