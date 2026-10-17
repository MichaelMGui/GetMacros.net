"""Recompute OFF source arithmetic and verify gzip catalogue relationships.

Only one source row/record shard/index page is decoded at a time. A temporary
SQLite file stores compact expected identities and postings, never full labels.
Both gzip and legacy JSON shards are supported for parent integration/CI.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import time

import off_expand as off


def read_json(path):
    path = Path(path)
    compressed = path if str(path).endswith('.gz') else Path(str(path) + '.gz')
    if compressed.exists():
        with gzip.open(compressed, 'rt', encoding='utf-8') as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(off.encoded(value)).hexdigest()


def meta_for(record, ordinal, shard):
    value = {key: record.get(key) for key in ['id', 'name', 'type', 'category', 'market', 'brand', 'barcode', 'barcodeNormalized', 'formulation', 'sourceId', 'package', 'status']}
    value.update({'shard': shard, 'ordinal': ordinal, 'search': off.text(' '.join([record.get('sourceName') or record['name'], record['brand'], record.get('brandOwner') or '']))})
    return value


def verify(partition=off.OUT / 'partition', report_path=off.OUT / 'off-integrity.json', baseline=off.ROOT / 'data/branded-foods/off/records.ndjson.gz'):
    partition = Path(partition).resolve()
    manifest = read_json(partition / 'manifest.json')
    assert manifest['derivativeLicense'] == 'ODbL-1.0'
    assert manifest['recordShardPrefix'] == 3
    assert manifest['marketPostings'] is True and manifest['marketPostingPrefix'] == 'markets'
    assert manifest['source']['licenseUrl'] == 'https://opendatacommons.org/licenses/odbl/1-0/'
    assert 'Open Food Facts' in manifest['source']['attribution']
    assert manifest['downloadUrl'].endswith('/off/records.ndjson.gz')
    assert manifest['normalizationUrl'].endswith('/off/normalization.py')
    assert manifest['source']['sourceSubsetUrl'].endswith('/off/source-records.ndjson.gz')
    rights = (partition / 'RIGHTS.txt').read_text(encoding='utf-8')
    assert 'Open Food Facts' in rights and 'ODbL' in rights and 'dbcl/1-0' in rights
    normalizer = (partition / 'normalization.py').read_text(encoding='utf-8')
    assert 'def normalize(' in normalizer and 'source-records.ndjson.gz' in normalizer
    historical = read_json(off.OUT / 'off-baseline-invariants.json')
    assert historical['sourceSha256'] == manifest['source']['sha256'], 'Historical baseline must be explicitly reviewed for a different source release'
    started = time.monotonic()
    counts = Counter()
    markets = Counter()
    errors = []
    max_record_shard_bytes = 0
    # Workspace-owned temporary paths avoid dependence on sandbox temp ACLs.
    with tempfile.TemporaryDirectory(prefix='off-verify-', dir=off.OUT) as directory:
        assert Path(directory).resolve().is_relative_to(off.OUT.resolve())
        database = sqlite3.connect(str(Path(directory) / 'expected.sqlite'))
        database.execute('PRAGMA journal_mode=OFF')
        database.execute('PRAGMA synchronous=OFF')
        database.execute('PRAGMA cache_size=-12000')
        database.execute('CREATE TABLE expected (id TEXT PRIMARY KEY, version TEXT, digest TEXT, formulation TEXT, market TEXT, brand TEXT, barcode TEXT, ordinal INTEGER UNIQUE, shard TEXT, metadigest TEXT, search TEXT, indexed INTEGER DEFAULT 0, exported INTEGER DEFAULT 0)')
        database.execute('CREATE INDEX expected_barcode ON expected(barcode,ordinal)')
        database.execute('CREATE INDEX expected_market ON expected(market,ordinal)')
        database.execute('CREATE TABLE tokens (token TEXT, ordinal INTEGER, PRIMARY KEY(token,ordinal)) WITHOUT ROWID')
        database.execute('CREATE TABLE baseline (id TEXT PRIMARY KEY, formulation TEXT, market TEXT)')
        with gzip.open(partition / 'source-records.ndjson.gz', 'rt', encoding='utf-8') as source:
            for line in source:
                row = json.loads(line)
                historical_records, ignored_reason = off.previous.normalize(row)
                database.executemany('INSERT INTO baseline VALUES (?,?,?)', ((record['id'], record['formulation'], record['market']) for record in historical_records))
                selected, reason = off.normalize(row)
                if reason:
                    raise AssertionError('Published source fails current normalizer: ' + reason)
                for record in selected:
                    database.execute('INSERT INTO expected (id,version,digest,formulation,market,brand,barcode) VALUES (?,?,?,?,?,?,?)',
                                     (record['id'], record['version'], digest(record), record['formulation'], record['market'], record['brand'], record['barcodeNormalized']))
                    # Independently verify the source conversions, including true zeros/nulls.
                    factor = record['sourceServing']['amount'] / 100 if record['sourceServing']['unit'] == 'ml' else 1
                    for key, (field, unit_factor) in off.MAP.items():
                        value = off.number(row.get(field))
                        expected = value * unit_factor * factor if value is not None else None
                        if key == 'cal' and expected is None:
                            kj = off.number(row.get('energy-kj_100g'))
                            expected = kj / 4.184 * factor if kj is not None else None
                        actual = record['nutrients'][key]
                        if expected is None:
                            assert actual is None, (record['id'], key, 'unknown became a value')
                        else:
                            assert actual is not None and abs(actual - expected) <= max(1e-8, abs(expected) * 1e-10), (record['id'], key)
                        counts['nutrientSourceComparisons'] += 1
                counts['sourceProducts'] += 1
                if counts['sourceProducts'] % 100000 == 0:
                    print(json.dumps({'phase': 'source', 'products': counts['sourceProducts'], 'elapsedSeconds': round(time.monotonic() - started)}), flush=True)
        database.commit()
        print(json.dumps({'phase': 'record-shards', 'expectedProfiles': database.execute('SELECT count(*) FROM expected').fetchone()[0]}), flush=True)
        for shard in manifest['recordShards']:
            file = partition / 'records' / (shard + '.json')
            physical = Path(str(file) + '.gz') if Path(str(file) + '.gz').exists() else file
            max_record_shard_bytes = max(max_record_shard_bytes, physical.stat().st_size)
            for record in read_json(file):
                ordinal = record.pop('catalogOrdinal')
                expected = database.execute('SELECT digest FROM expected WHERE id=?', (record['id'],)).fetchone()
                assert expected and digest(record) == expected[0], 'Source/record mismatch: ' + record['id']
                assert hashlib.sha256(record['id'].encode()).hexdigest()[:manifest.get('recordShardPrefix', 2)] == shard
                assert record['market'] in record['markets']
                assert record['status'] == 'community-label-imported'
                assert record['sourceChecked'] is None and record['labelDate'] is None
                assert record['license'] == 'ODbL-1.0' and record['contentsLicense'] == 'DbCL-1.0'
                assert record['retrievedAt'] == manifest['source']['retrievedAt']
                if record['sourceServing']['unit'] == 'ml':
                    assert record['basis'] == {'amount': 1, 'unit': 'serving'} and record['portions'] == []
                    counts['volumeProfilesWithoutInferredGrams'] += 1
                meta = meta_for(record, ordinal, shard)
                database.execute('UPDATE expected SET ordinal=?,shard=?,metadigest=?,search=? WHERE id=?', (ordinal, shard, digest(meta), meta['search'], record['id']))
                database.executemany('INSERT INTO tokens VALUES (?,?)', ((token, ordinal) for token in set(meta['search'].split()) if token))
                counts['marketProfiles'] += 1
                counts['completeCoreProfiles' if all(record['nutrients'].get(key) is not None for key in ['cal', 'p', 'c', 'fat']) else 'partialCoreProfiles'] += 1
                markets[record['market']] += 1
        database.commit()
        assert counts['marketProfiles'] == manifest['profileCount']
        assert dict(markets) == manifest['markets']
        expected_global_brands = dict(database.execute('SELECT brand,count(*) FROM expected GROUP BY brand'))
        assert manifest.get('brandCount', len(manifest.get('brands', {}))) == len(expected_global_brands)
        if 'brands' in manifest:
            assert expected_global_brands == manifest['brands']
        assert database.execute('SELECT count(*) FROM expected WHERE ordinal IS NULL').fetchone()[0] == 0
        assert database.execute('SELECT min(ordinal),max(ordinal) FROM expected').fetchone() == (0, manifest['profileCount'] - 1)
        historical_count = database.execute('SELECT count(*) FROM baseline').fetchone()[0]
        assert historical_count == historical['profileCount']
        assert dict(database.execute('SELECT market,count(*) FROM baseline GROUP BY market')) == historical['markets']
        baseline_hash = hashlib.sha256(b'[')
        for index, pair in enumerate(database.execute('SELECT id,formulation FROM baseline ORDER BY id')):
            if index:
                baseline_hash.update(b',')
            baseline_hash.update(off.encoded(list(pair)))
        baseline_hash.update(b']')
        assert baseline_hash.hexdigest() == historical['idAndFormulationSha256']
        assert database.execute('SELECT count(*) FROM baseline b LEFT JOIN expected e ON b.id=e.id WHERE e.id IS NULL OR b.formulation!=e.formulation').fetchone()[0] == 0
        counts['historicalIdsAndFormulationsPreserved'] = historical_count
        for page in manifest['indexPages']:
            for meta in read_json(partition / 'index' / (page + '.json')):
                expected = database.execute('SELECT metadigest FROM expected WHERE ordinal=? AND id=?', (meta['ordinal'], meta['id'])).fetchone()
                assert expected and digest(meta) == expected[0], 'Index/source mismatch: ' + meta['id']
                assert int(page) == meta['ordinal'] // manifest['indexPageSize']
                database.execute('UPDATE expected SET indexed=indexed+1 WHERE id=?', (meta['id'],))
                counts['indexProfiles'] += 1
        assert counts['indexProfiles'] == counts['marketProfiles']
        assert database.execute('SELECT count(*) FROM expected WHERE indexed!=1').fetchone()[0] == 0
        print(json.dumps({'phase': 'postings', 'indexProfiles': counts['indexProfiles']}), flush=True)
        for prefix in manifest['tokenPrefixes']:
            for token, ids in read_json(partition / 'tokens' / (prefix + '.json')).items():
                expected = [row[0] for row in database.execute('SELECT ordinal FROM tokens WHERE token=? ORDER BY ordinal', (token,))]
                assert ids == expected and token.startswith(prefix), ('token', token)
                counts['tokenPostings'] += len(ids)
        assert counts['tokenPostings'] == database.execute('SELECT count(*) FROM tokens').fetchone()[0]
        for prefix in manifest['barcodePrefixes']:
            for code, ids in read_json(partition / 'barcodes' / (prefix + '.json')).items():
                expected = [row[0] for row in database.execute('SELECT ordinal FROM expected WHERE barcode=? ORDER BY ordinal', (code,))]
                assert ids == expected and code.startswith(prefix), ('barcode', code)
                counts['barcodePostings'] += len(ids)
        assert counts['barcodePostings'] == counts['marketProfiles']
        aggregated_country_brands = Counter()
        for market in manifest['markets']:
            expected_ids = [row[0] for row in database.execute('SELECT ordinal FROM expected WHERE market=? ORDER BY ordinal', (market,))]
            assert read_json(partition / 'markets' / (market + '.json')) == expected_ids
            expected_brands = dict(database.execute('SELECT brand,count(*) FROM expected WHERE market=? GROUP BY brand', (market,)))
            actual_brands = read_json(partition / 'brands' / (market + '.json'))
            assert actual_brands == expected_brands
            aggregated_country_brands.update(actual_brands)
            counts['countryPostings'] += len(expected_ids)
        assert dict(aggregated_country_brands) == expected_global_brands
        quarantine = read_json(partition / 'quarantined.json')
        assert quarantine['status'] == 'excluded-pending-label-or-rounding-review'
        assert quarantine['license'] == 'ODbL-1.0' and 'Open Food Facts' in quarantine['attribution']
        quarantine_codes = set()
        for row in quarantine['records']:
            assert row['code'] not in quarantine_codes
            quarantine_codes.add(row['code'])
            assert row['reason'] == 'zero-energy-positive-macros-pending-label-or-rounding-review'
            assert row['sourceUrl'] == 'https://world.openfoodfacts.org/product/' + row['code']
            assert any(off.number(row['nativePer100'].get(key)) is not None and off.number(row['nativePer100'][key]) > 1 for key in ['p', 'fat'])
            assert database.execute('SELECT count(*) FROM expected WHERE id GLOB ?', ('branded:off:' + row['code'] + ':*',)).fetchone()[0] == 0
        assert set(historical['quarantinedSourceCodes']) <= quarantine_codes
        counts['quarantinedSourceProductsChecked'] = len(quarantine_codes)
        if baseline and Path(baseline).exists() and Path(baseline).resolve() != (partition / 'records.ndjson.gz').resolve():
            with gzip.open(baseline, 'rt', encoding='utf-8') as source:
                for line in source:
                    record = json.loads(line)
                    expected = database.execute('SELECT formulation FROM expected WHERE id=?', (record['id'],)).fetchone()
                    assert expected and record['formulation'] == expected[0], 'Baseline identity missing/changed: ' + record['id']
                    counts['baselineIdsAndFormulationsPreserved'] += 1
        with gzip.open(partition / 'records.ndjson.gz', 'rt', encoding='utf-8') as source:
            for line in source:
                record = json.loads(line)
                ordinal = record.pop('catalogOrdinal')
                expected = database.execute('SELECT digest,ordinal FROM expected WHERE id=?', (record['id'],)).fetchone()
                assert expected == (digest(record), ordinal), 'Redistributable export differs: ' + record['id']
                database.execute('UPDATE expected SET exported=exported+1 WHERE id=?', (record['id'],))
                counts['redistributableExportProfiles'] += 1
        assert counts['redistributableExportProfiles'] == counts['marketProfiles']
        assert database.execute('SELECT count(*) FROM expected WHERE exported!=1').fetchone()[0] == 0
        records_hash = hashlib.sha256(b'[')
        for number, (record_id, version) in enumerate(database.execute('SELECT id,version FROM expected ORDER BY id')):
            if number:
                records_hash.update(b',')
            records_hash.update(off.encoded([record_id, version]))
        records_hash.update(b']')
        assert manifest['recordsVersion'] == records_hash.hexdigest()[:16]
        postings = {market: [row[0] for row in database.execute('SELECT ordinal FROM expected WHERE market=? ORDER BY ordinal', (market,))] for market in sorted(markets)}
        assert manifest['marketPostingsVersion'] == off.hash_value(postings)
        assert manifest['version'] == off.hash_value({'records': manifest['recordsVersion'], 'marketPostings': manifest['marketPostingsVersion']})
        database.close()
    report = {'ok': True, 'partition': str(partition), 'sourceRetrievedAt': manifest['source']['retrievedAt'],
              'counts': dict(counts), 'markets': dict(markets), 'jsonEncoding': manifest.get('jsonEncoding', 'identity'),
              'maximumCompressedRecordShardBytes': max_record_shard_bytes, 'version': manifest['version'],
              'memoryPolicy': 'One source row/record shard/index page at a time; compact SQLite expected identities and postings; no all-record object list.',
              'elapsedSeconds': round(time.monotonic() - started, 3)}
    off.dump(report_path, report)
    print(json.dumps(report, indent=2), flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partition', type=Path, default=off.OUT / 'partition')
    parser.add_argument('--report', type=Path, default=off.OUT / 'off-integrity.json')
    parser.add_argument('--baseline', type=Path, default=off.ROOT / 'data/branded-foods/off/records.ndjson.gz')
    args = parser.parse_args()
    verify(args.partition, args.report, args.baseline)
