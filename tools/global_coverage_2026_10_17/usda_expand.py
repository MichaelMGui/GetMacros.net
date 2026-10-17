"""Expand USDA branded coverage from the official bulk archive, without brand caps.

The staging output uses the existing food model and source-separated gzip shards.
No production file is changed. Historical FDC references carry no invented nutrients.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import gzip
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/product_release'))
from import_food_library import NUTRIENTS, finite, normalize_unit, hash_value

DATE = '2026-10-17'
SOURCE_RETRIEVED = '2026-10-12'
SOURCE_ID = 'usda-branded-2026-04'
DOWNLOAD_URL = 'https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_branded_food_json_2026-04-30.zip'
ARCHIVE = ROOT / 'docs/master-release-2026-10-12/sources/usda-branded-2026-04.zip'
REPORT_DIR = ROOT / 'docs/global-coverage-2026-10-17/usda'
OUT = REPORT_DIR / 'staged'
MARKETS = {'United States': 'US', 'US': 'US', 'New Zealand': 'NZ', 'NZ': 'NZ'}
# GS1 T0055: GRM=gram, MLT=millilitre. No density or quantity conversion.
SERVING_UNITS = {'g': 'g', 'ml': 'ml', 'grm': 'g', 'mlt': 'ml'}
CORE = ('cal', 'p', 'c', 'fat')


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def text(value):
    """Match the existing ASCII USDA search index normalization."""
    return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode().lower()).strip()


def iso_date(value):
    if not isinstance(value, str) or not value.strip():
        return None
    for pattern in ('%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y'):
        try:
            return datetime.strptime(value.strip(), pattern).date().isoformat()
        except ValueError:
            pass
    return None


def barcode(value):
    code = str(value or '').strip()
    return code.zfill(14) if re.fullmatch(r'\d{8}|\d{12,14}', code) else None


def stream_array(handle):
    """Stream the named BrandedFoods array; reject unrelated/truncated JSON."""
    decoder = json.JSONDecoder()
    buffer = ''
    while True:
        part = handle.read(1024 * 1024)
        if not part:
            raise ValueError('Source has no BrandedFoods array')
        buffer += part
        match = re.search(r'"BrandedFoods"\s*:\s*\[', buffer)
        if match:
            buffer = buffer[match.end():]
            break
    while True:
        buffer = buffer.lstrip(' \n\r\t,')
        if buffer.startswith(']'):
            return
        try:
            row, end = decoder.raw_decode(buffer)
            buffer = buffer[end:]
            if not isinstance(row, dict):
                raise ValueError('BrandedFoods array contains a non-object row')
            yield row
        except json.JSONDecodeError:
            part = handle.read(1024 * 1024)
            if not part:
                raise ValueError('Truncated branded archive')
            buffer += part


def normalized_nutrients(food):
    """Only a finite nonnegative source amount in the documented nutrient unit."""
    raw = defaultdict(list)
    for row in food.get('foodNutrients') or []:
        raw[row.get('nutrient', {}).get('id')].append(row)
    values, provenance = {}, {}
    for key, (_, unit, ids) in NUTRIENTS.items():
        matches = [row for nutrient_id in ids for row in raw[nutrient_id]
                   if finite(row.get('amount')) and normalize_unit(row.get('nutrient', {}).get('unitName')) == normalize_unit(unit)]
        match = matches[0] if matches else None
        values[key] = match['amount'] if match else None
        if match:
            derive = match.get('foodNutrientDerivation') or {}
            provenance[key] = {'nutrientId': match['nutrient']['id'], 'method': derive.get('code') or 'manufacturer-reported'}
    return values, provenance


def normalize(food):
    market = MARKETS.get(food.get('marketCountry'))
    if not market:
        return None, 'unsupported-source-market'
    source_ref = food.get('fdcId')
    if isinstance(source_ref, bool) or not isinstance(source_ref, int) or source_ref <= 0:
        return None, 'invalid-source-id'
    source_name = str(food.get('description') or '').strip()
    brand = str(food.get('brandName') or food.get('brandOwner') or '').strip()
    if not source_name or not brand:
        return None, 'missing-product-identity'
    values, provenance = normalized_nutrients(food)
    if not any(values[k] is not None for k in CORE):
        return None, 'missing-core-nutrition'
    serving = food.get('servingSize')
    raw_unit = str(food.get('servingSizeUnit') or '').strip()
    unit = SERVING_UNITS.get(raw_unit.lower())
    if unit is None or not finite(serving) or serving <= 0:
        return None, 'unsupported-or-absent-serving-basis'
    name = source_name if len(source_name) <= 240 else source_name[:237].rstrip() + '…'
    label = str(food.get('householdServingFullText') or '').strip() or f'{serving:g} {unit} source serving'
    source_values = values.copy()
    portions = [{'id': 'source-serving', 'label': label, 'grams': serving}] if unit == 'g' else []
    basis = {'amount': 100, 'unit': 'g'} if unit == 'g' else {'amount': 1, 'unit': 'serving'}
    if unit == 'ml':
        values = {k: v * serving / 100 if v is not None else None for k, v in values.items()}
        if any(v is not None and not math.isfinite(v) for v in values.values()):
            return None, 'nonfinite-scaled-nutrient'
    code = str(food.get('gtinUpc') or '').strip()
    normalized = barcode(code)
    ingredients = food.get('ingredients') or None
    flags = ["Manufacturer-label record imported from USDA; not independently checked against today's package."]
    if normalized is None:
        flags.append('Source barcode is missing or has an unsupported length.')
    if name != source_name:
        flags.append('Long source wording shortened for display; sourceName retains the original wording.')
    if unit == 'ml':
        flags.append('Values use the source milliliter serving; no gram weight or density is assumed.')
    if values['sugar'] is not None and values['c'] is not None and values['sugar'] > values['c'] + 1:
        flags.append('Source total sugars exceed carbohydrate; check the current product label.')
    if food.get('discontinuedDate'):
        flags.append('Source marks this product discontinued; this is a historical label, not availability information.')
    identity = {'barcode': normalized, 'market': market, 'brand': text(brand), 'name': text(source_name),
                'ingredients': text(ingredients), 'package': food.get('packageWeight') or '',
                'serving': serving, 'unit': unit, 'sourceNutrients': source_values}
    history = {}
    for entry in food.get('foodUpdateLog') or []:
        ref = entry.get('fdcId')
        if isinstance(ref, int) and not isinstance(ref, bool) and ref > 0:
            history[str(ref)] = iso_date(entry.get('publicationDate'))
    history[str(source_ref)] = iso_date(food.get('publicationDate'))
    record = {
        'id': 'branded:usda:' + str(source_ref), 'name': name, 'brand': brand,
        'brandOwner': food.get('brandOwner') or None, 'brandName': food.get('brandName') or None,
        'type': 'branded', 'category': food.get('brandedFoodCategory') or 'Packaged foods',
        'market': market, 'markets': [market], 'language': 'en', 'barcode': code or None,
        'barcodeNormalized': normalized, 'package': food.get('packageWeight') or None,
        'formulation': hash_value(identity), 'ingredients': ingredients,
        'sourceId': SOURCE_ID, 'sourceOrigin': 'USDA FoodData Central — manufacturer labels',
        'sourceRef': str(source_ref), 'sourceUrl': f'https://fdc.nal.usda.gov/food-details/{source_ref}/nutrients',
        'sourcePublished': iso_date(food.get('publicationDate')), 'sourceChecked': None,
        'retrievedAt': SOURCE_RETRIEVED, 'sourceRelease': 'April 2026 bulk release (2026-04-30)',
        'sourceModified': iso_date(food.get('modifiedDate')),
        'labelDate': iso_date(food.get('availableDate')) or iso_date(food.get('modifiedDate')),
        'status': 'manufacturer-label-imported', 'basis': basis, 'nutrients': values,
        'portions': portions, 'serving': label,
        'sourceServing': {'amount': serving, 'unit': unit, 'rawUnit': raw_unit, 'label': food.get('householdServingFullText') or None},
        'sourcePer100': {'unit': unit, 'nutrients': source_values}, 'provenance': provenance,
        'flags': flags, 'availability': 'Source market attribution; current retailer/warehouse inventory not checked.',
        'license': 'CC0-1.0', 'discontinuedDate': iso_date(food.get('discontinuedDate')),
        'versionGroup': 'usda:' + hash_value([market, normalized or 'fdc:' + str(source_ref)]),
        # References are audit metadata. Presence here never means its nutrients are available.
        'sourceHistory': [{'sourceRef': ref, 'sourcePublished': published} for ref, published in sorted(history.items(), key=lambda r: (r[1] or '', int(r[0])), reverse=True)],
    }
    if name != source_name:
        record['sourceName'] = source_name
    for field in ('publicationDate', 'modifiedDate', 'availableDate', 'discontinuedDate'):
        if food.get(field) and not iso_date(food[field]):
            record['flags'].append('Unrecognized source date retained as raw source evidence: ' + field)
            record.setdefault('sourceDatesRaw', {})[field] = food[field]
    return record, None


def dump_json(path, value, compressed=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (compact(value) + '\n').encode('utf-8')
    path.write_bytes(gzip.compress(data, compresslevel=9, mtime=0) if compressed else data)
    return len(data)


def load_data_json(path):
    """Read gzip staging and older uncompressed source partitions."""
    if path.exists():
        data = path.read_bytes()
        return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)
    compressed = path.with_suffix(path.suffix + '.gz')
    return json.loads(gzip.decompress(compressed.read_bytes()))


def load_brand_counts(output, manifest):
    """Aggregate actual per-market counts, with legacy manifest fallback."""
    prefix = manifest.get('brandCountsPrefix')
    if not prefix:
        return Counter(manifest.get('brands') or {}), None
    if prefix != 'brands':
        raise ValueError('Unsupported brand-count directory')
    by_market = {}
    combined = Counter()
    for market in sorted(manifest['markets']):
        counts = load_data_json(output / prefix / (market + '.json'))
        if any(not isinstance(brand, str) or not brand or not isinstance(n, int) or isinstance(n, bool) or n <= 0 for brand, n in counts.items()):
            raise ValueError('Invalid source brand counts for market ' + market)
        by_market[market] = Counter(counts)
        combined.update(counts)
    return combined, by_market


def partition_sizes(output):
    stored_bytes, file_counts = Counter(), Counter()
    for path in output.rglob('*'):
        if path.is_file():
            kind = path.relative_to(output).parts[0]
            stored_bytes[kind] += path.stat().st_size
            file_counts[kind] += 1
    return dict(stored_bytes), dict(file_counts)


def compact_brand_manifest(output=OUT, report_dir=REPORT_DIR):
    """Trim an existing stage from its actual metadata, without touching records."""
    manifest_path = output / 'manifest.json'
    manifest = load_data_json(manifest_path)
    before = manifest_path.stat().st_size
    by_market = defaultdict(Counter)
    raw_brand_bytes = 0
    for page in manifest['indexPages']:
        for row in load_data_json(output / 'index' / (page + '.json')):
            by_market[row['market']][row['brand']] += 1
    combined = Counter()
    for market, counts in sorted(by_market.items()):
        if sum(counts.values()) != manifest['markets'][market]:
            raise ValueError('Market brand count differs from published profiles')
        combined.update(counts)
        raw_brand_bytes += dump_json(output / 'brands' / (market + '.json.gz'), dict(sorted(counts.items())), compressed=True)
    old_counts, _ = load_brand_counts(output, manifest)
    if old_counts and old_counts != combined:
        raise ValueError('Existing global brand dictionary disagrees with actual metadata')
    manifest.pop('brands', None)
    manifest.update({'brandCount': len(combined), 'brandCountsPrefix': 'brands'})
    dump_json(manifest_path, manifest)
    stored_bytes, file_counts = partition_sizes(output)
    report = {'pass': True, 'catalogueVersion': manifest['version'], 'profiles': manifest['profileCount'], 'brandCount': len(combined), 'brandCountsByMarket': {market: len(counts) for market, counts in by_market.items()}, 'sourceProfilesByMarket': {market: sum(counts.values()) for market, counts in by_market.items()}, 'manifestBytesBefore': before, 'manifestBytesAfter': manifest_path.stat().st_size, 'manifestBytesSaved': before - manifest_path.stat().st_size, 'recordBodiesTouched': False, 'storedBytesByPartition': stored_bytes, 'stagedTotalBytes': sum(stored_bytes.values())}
    dump_json(report_dir / 'manifest-brand-compaction.json', report)
    expansion_path = report_dir / 'expansion-report.json'
    if expansion_path.exists():
        expansion = load_data_json(expansion_path)
        expansion.setdefault('rawJsonBytesByPartition', {})['brands'] = raw_brand_bytes
        expansion.update({'gzipAndManifestBytesByPartition': stored_bytes, 'stagedTotalBytes': sum(stored_bytes.values()), 'fileCounts': file_counts, 'manifestBrandCountMode': 'per-market source counts in brands/*.json.gz'})
        dump_json(expansion_path, expansion)
    return report


def json_array(path, rows):
    """Write one deterministic gzip JSON array without holding a whole partition."""
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_bytes = 0
    with path.open('wb') as target:
        with gzip.GzipFile(filename='', mode='wb', fileobj=target, compresslevel=9, mtime=0) as zipped:
            zipped.write(b'['); raw_bytes += 1
            for i, row in enumerate(rows):
                chunk = ((',' if i else '') + compact(row)).encode('utf-8')
                zipped.write(chunk); raw_bytes += len(chunk)
            zipped.write(b']\n'); raw_bytes += 2
    return raw_bytes


def baseline_ids(directory):
    """Read the established catalogue with either legacy JSON or gzip shards."""
    manifest_path = directory / 'manifest.json'
    if not manifest_path.exists():
        return set()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    ids = set()
    for shard in manifest['recordShards']:
        path = directory / 'records' / (shard + '.json')
        if path.exists():
            records = json.loads(path.read_text(encoding='utf-8'))
        else:
            records = json.loads(gzip.decompress(path.with_suffix('.json.gz').read_bytes()))
        ids.update(record['id'] for record in records)
    return ids


def build(archive_path=ARCHIVE, output=OUT, report_dir=REPORT_DIR):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use an empty output directory; existing staging is never silently replaced')
    report_dir.mkdir(parents=True, exist_ok=True)
    scratch = report_dir / 'usda-expansion-work.sqlite'
    if scratch.exists():
        raise ValueError('Existing scratch database must be explicitly inspected/removed before retrying')
    required_ids = baseline_ids(ROOT / 'data/branded-foods/usda')
    archive_sha = hashlib.file_digest(archive_path.open('rb'), 'sha256').hexdigest()
    db = sqlite3.connect(scratch)
    db.execute('PRAGMA journal_mode=OFF'); db.execute('PRAGMA synchronous=OFF')
    # Windows sandbox's default TEMP can be read-only; sorting stays in memory.
    db.execute('PRAGMA temp_store=MEMORY')
    db.execute('CREATE TABLE food(id TEXT PRIMARY KEY, source_ref INTEGER, published TEXT, modified TEXT, group_id TEXT, shard TEXT, payload BLOB)')
    stats, markets, units, reasons, rejected_units, published_markets, brands = (Counter() for _ in range(7))
    brands_by_market = defaultdict(Counter)
    examples, source_ids, sample_ids = {}, set(), {}
    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = [n for n in archive.namelist() if n.endswith('.json')]
            if len(entries) != 1:
                raise ValueError('Expected exactly one JSON source archive member')
            member = archive.getinfo(entries[0])
            with io.TextIOWrapper(archive.open(member), encoding='utf-8') as handle:
                for i, food in enumerate(stream_array(handle), 1):
                    stats['sourceRows'] += 1
                    markets[str(food.get('marketCountry'))] += 1
                    units[str(food.get('servingSizeUnit'))] += 1
                    record, reason = normalize(food)
                    if reason:
                        reasons[reason] += 1
                        if reason == 'unsupported-or-absent-serving-basis':
                            rejected_units[str(food.get('servingSizeUnit'))] += 1
                        if reason not in examples:
                            examples[reason] = {'sourceRef': food.get('fdcId'), 'name': food.get('description'), 'servingSize': food.get('servingSize'), 'servingSizeUnit': food.get('servingSizeUnit')}
                        continue
                    record_id = record['id']
                    if record_id in source_ids:
                        raise ValueError('Duplicate source FDC ID: ' + record_id)
                    source_ids.add(record_id)
                    stats['acceptedRows'] += 1
                    published_markets[record['market']] += 1
                    brands[record['brand']] += 1
                    brands_by_market[record['market']][record['brand']] += 1
                    stats['sourceHistoryReferences'] += len(record['sourceHistory'])
                    for label, condition in [('grams', record['sourceServing']['unit'] == 'g'), ('milliliters', record['sourceServing']['unit'] == 'ml'), ('newBrand', record['brand'] == "MICHELE'S GRANOLA"), ('nullNutrients', any(v is None for v in record['nutrients'].values()))]:
                        if condition and label not in sample_ids:
                            sample_ids[label] = record_id
                    db.execute('INSERT INTO food VALUES (?,?,?,?,?,?,?)', (record_id, int(record['sourceRef']), record['sourcePublished'] or '', record['sourceModified'] or '', record['versionGroup'], hashlib.sha256(record_id.encode()).hexdigest()[:3], zlib.compress(compact(record).encode(), level=1)))
                    if i % 25000 == 0:
                        db.commit()
                        print(compact({'phase': 'normalize', 'sourceRows': i, 'acceptedRows': stats['acceptedRows']}), flush=True)
        db.commit()
        missing = sorted(required_ids - source_ids)
        if missing:
            dump_json(report_dir / 'missing-established-ids.json', missing)
            raise ValueError(f'{len(missing)} established IDs would disappear; expansion blocked before publication')
        # USDA says repeated same-market GTINs are source versions. Keep every ID.
        db.execute('CREATE TABLE ordered AS SELECT id, ROW_NUMBER() OVER (ORDER BY published DESC, source_ref DESC)-1 AS ordinal, ROW_NUMBER() OVER (PARTITION BY group_id ORDER BY published DESC, source_ref DESC) AS version_rank, COUNT(*) OVER (PARTITION BY group_id) AS version_count, FIRST_VALUE(id) OVER (PARTITION BY group_id ORDER BY published DESC, source_ref DESC) AS latest_id FROM food')
        db.execute('CREATE UNIQUE INDEX ordered_id ON ordered(id)')
        db.execute('CREATE INDEX food_shard ON food(shard)')
        db.execute('CREATE TABLE meta(ordinal INTEGER PRIMARY KEY, payload TEXT, market TEXT)')
        db.execute('CREATE TABLE token(prefix TEXT, word TEXT, ordinal INTEGER)')
        db.execute('CREATE TABLE codes(prefix TEXT, code TEXT, ordinal INTEGER)')
        shards = [row[0] for row in db.execute('SELECT DISTINCT shard FROM food ORDER BY shard')]
        raw_bytes = Counter()
        versions_digest = hashlib.sha256()
        for shard_i, shard in enumerate(shards):
            def rows():
                cursor = db.execute('SELECT f.payload,o.ordinal,o.version_rank,o.version_count,o.latest_id FROM food f JOIN ordered o USING(id) WHERE f.shard=? ORDER BY o.ordinal', (shard,))
                for payload, ordinal, rank, count, latest_id in cursor:
                    record = json.loads(zlib.decompress(payload))
                    record.update({'catalogOrdinal': ordinal, 'sourceVersionRank': rank, 'sourceVersionCount': count, 'latestSourceId': latest_id, 'sourceVersionRole': 'latest-in-bulk' if rank == 1 else 'historical-in-bulk'})
                    for history in record['sourceHistory']:
                        history['availableInCatalogue'] = 'branded:usda:' + history['sourceRef'] in source_ids
                    record['version'] = hash_value(record)
                    versions_digest.update(compact([record['id'], record['version']]).encode())
                    meta = {k: record.get(k) for k in ('id', 'name', 'type', 'category', 'market', 'brand', 'barcode', 'barcodeNormalized', 'formulation', 'sourceId', 'package', 'status', 'versionGroup', 'sourcePublished', 'sourceModified', 'sourceVersionRank', 'sourceVersionCount', 'latestSourceId', 'sourceVersionRole')}
                    meta.update({'shard': shard, 'ordinal': ordinal, 'search': text(' '.join((record.get('sourceName') or record['name'], record['brand'], record.get('brandOwner') or '')))})
                    db.execute('INSERT INTO meta VALUES (?,?,?)', (ordinal, compact(meta), record['market']))
                    db.executemany('INSERT INTO token VALUES (?,?,?)', [(word[:2], word, ordinal) for word in sorted(set(meta['search'].split()))])
                    code = record['barcodeNormalized']
                    if code:
                        db.execute('INSERT INTO codes VALUES (?,?,?)', (code[:3], code, ordinal))
                    yield record
            raw_bytes['records'] += json_array(output / 'records' / (shard + '.json.gz'), rows())
            if shard_i % 256 == 0:
                db.commit()
                print(compact({'phase': 'records', 'shardsDone': shard_i + 1, 'shardsTotal': len(shards)}), flush=True)
        db.commit()
        index_pages = []
        for page, group in itertools.groupby(db.execute('SELECT ordinal,payload FROM meta ORDER BY ordinal'), key=lambda r: r[0] // 64):
            key = str(page).zfill(4); index_pages.append(key)
            raw_bytes['index'] += json_array(output / 'index' / (key + '.json.gz'), (json.loads(row[1]) for row in group))
        for table, field, directory, manifest_key in [('token', 'word', 'tokens', 'tokenPrefixes'), ('codes', 'code', 'barcodes', 'barcodePrefixes')]:
            db.execute(f'CREATE INDEX {table}_ordering ON {table}(prefix,{field},ordinal)')
            prefixes = [r[0] for r in db.execute(f'SELECT DISTINCT prefix FROM {table} ORDER BY prefix')]
            for prefix in prefixes:
                grouped = {key: [row[1] for row in group] for key, group in itertools.groupby(db.execute(f'SELECT {field},ordinal FROM {table} WHERE prefix=? ORDER BY {field},ordinal', (prefix,)), key=lambda r: r[0])}
                raw_bytes[directory] += dump_json(output / directory / (prefix + '.json.gz'), grouped, compressed=True)
            if directory == 'tokens':
                token_prefixes = prefixes
            else:
                barcode_prefixes = prefixes
        for market in sorted(published_markets):
            raw_bytes['markets'] += dump_json(output / 'markets' / (market + '.json.gz'), [r[0] for r in db.execute('SELECT ordinal FROM meta WHERE market=? ORDER BY ordinal', (market,))], compressed=True)
            raw_bytes['brands'] += dump_json(output / 'brands' / (market + '.json.gz'), dict(sorted(brands_by_market[market].items())), compressed=True)
        source = {'id': SOURCE_ID, 'name': 'USDA Global Branded Food Products Database', 'edition': 'April 2026', 'releaseDate': '2026-04-30', 'url': 'https://fdc.nal.usda.gov/download-datasets/', 'downloadUrl': DOWNLOAD_URL, 'sha256': archive_sha, 'license': 'CC0 1.0', 'licenseUrl': 'https://fdc.nal.usda.gov/api-guide/#bkmk-9', 'retrievedAt': SOURCE_RETRIEVED, 'documentationChecked': DATE, 'quality': 'Source manufacturer labels; arithmetic and identities checked, not independent current-package verification.', 'geographicRule': 'Exact source marketCountry only; no national equivalence inferred.'}
        grouping = db.execute('SELECT COUNT(*),SUM(CASE WHEN version_count>1 AND version_rank=1 THEN 1 ELSE 0 END),SUM(CASE WHEN version_rank>1 THEN 1 ELSE 0 END) FROM ordered').fetchone()
        manifest = {'schemaVersion': 1, 'publishedAt': DATE, 'jsonEncoding': 'gzip', 'recordShardPrefix': 3, 'profileCount': stats['acceptedRows'], 'markets': dict(published_markets), 'brandCount': len(brands), 'brandCountsPrefix': 'brands', 'version': versions_digest.hexdigest()[:16], 'source': source, 'indexPageSize': 64, 'indexPages': index_pages, 'tokenPrefixes': token_prefixes, 'barcodePrefixes': barcode_prefixes, 'recordShards': shards, 'marketPostings': True, 'searchPolicy': 'Exact barcode first. Brand/name tokens and partial words; chronological source publication order. Every source-supported brand is eligible. Source versions retain separate FDC IDs and nutrient bodies.', 'availability': 'Tracked source labels, not live retailer inventory. Imported values are not independently package-verified.', 'versionPolicy': 'Same-market normalized GTIN identifies a source version group. Latest means latest publication in this bulk archive, not current retailer availability. Source history references without a catalogue row have no imported nutrients.'}
        dump_json(output / 'manifest.json', manifest)
        stored_bytes = Counter()
        file_counts = Counter()
        for path in output.rglob('*'):
            if path.is_file():
                kind = path.relative_to(output).parts[0]
                stored_bytes[kind] += path.stat().st_size; file_counts[kind] += 1
        report = {'pass': True, 'importedAt': DATE, 'sourceArchive': str(archive_path.relative_to(ROOT)), 'sourceMember': member.filename, 'sourceSha256': archive_sha, 'sourceReleaseDate': '2026-04-30', 'sourceRetrievedAt': SOURCE_RETRIEVED, 'officialDownloadsCheckedAt': DATE, 'latestOfficialBulkReleaseOnCheck': 'April 2026', 'sourceUncompressedBytes': member.file_size, 'sourceCompressedBytes': archive_path.stat().st_size, 'sourceRows': stats['sourceRows'], 'sourceRowsByMarket': dict(markets), 'sourceServingUnits': dict(units), 'acceptedRows': stats['acceptedRows'], 'acceptedByMarket': dict(published_markets), 'acceptedBrandCount': len(brands), 'rejected': dict(reasons), 'rejectedServingUnits': dict(rejected_units), 'rejectedExamples': examples, 'establishedIds': len(required_ids), 'establishedIdsPreserved': len(required_ids & source_ids), 'missingEstablishedIds': 0, 'sameMarketBarcodeGroupsWithMultipleSourceRows': grouping[1], 'historicalRowsWithActualNutrients': grouping[2], 'sourceHistoryReferences': stats['sourceHistoryReferences'], 'representativeIds': sample_ids, 'rawJsonBytesByPartition': dict(raw_bytes), 'gzipAndManifestBytesByPartition': dict(stored_bytes), 'stagedTotalBytes': sum(stored_bytes.values()), 'fileCounts': dict(file_counts), 'version': manifest['version'], 'stagedPath': str(output.relative_to(ROOT)), 'licenseSeparation': 'USDA CC0-1.0 only. No Open Food Facts rows, imagery, or ODbL data enter this source partition.'}
        dump_json(report_dir / 'expansion-report.json', report)
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    finally:
        db.close()
    # This scratch file is this import's own temporary database, never source data.
    scratch.unlink()
    return manifest, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ARCHIVE)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--report-dir', type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    build(args.archive.resolve(), args.output.resolve(), args.report_dir.resolve())


if __name__ == '__main__':
    main()
