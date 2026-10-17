"""Inspect every staged USDA row and search posting; no site build required."""
from collections import Counter
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

from usda_expand import NUTRIENTS, OUT, REPORT_DIR, iso_date, load_brand_counts


def load(path):
    return json.loads(gzip.decompress(path.read_bytes())) if path.suffix == '.gz' else json.loads(path.read_text(encoding='utf-8'))


def check(path=OUT, report_dir=REPORT_DIR):
    manifest = load(path / 'manifest.json')
    assert manifest['jsonEncoding'] == 'gzip'
    assert manifest['recordShardPrefix'] == 3
    count = manifest['profileCount']
    ids, ordinals, groups, market_counts = set(), set(), {}, Counter()
    unknown = 0
    units, raw_units = Counter(), Counter()
    available_history, unavailable_history = 0, 0
    sample = {}
    actual_brands = Counter()
    actual_market_brands = {market: Counter() for market in manifest['markets']}
    for shard in manifest['recordShards']:
        rows = load(path / 'records' / (shard + '.json.gz'))
        for row in rows:
            assert row['id'] not in ids, row['id']
            ids.add(row['id'])
            assert hashlib.sha256(row['id'].encode()).hexdigest()[:3] == shard
            assert row['catalogOrdinal'] not in ordinals
            assert 0 <= row['catalogOrdinal'] < count
            ordinals.add(row['catalogOrdinal'])
            assert row['name'] and len(row['name']) <= 240 and row['brand']
            assert row['status'] == 'manufacturer-label-imported'
            assert row['sourceChecked'] is None
            assert row['license'] == 'CC0-1.0'
            assert set(row['nutrients']) == set(NUTRIENTS)
            assert row['sourceServing']['amount'] > 0
            assert row['sourceServing']['unit'] in ('g', 'ml')
            units[row['sourceServing']['unit']] += 1
            raw_units[row['sourceServing']['rawUnit']] += 1
            for key, value in row['nutrients'].items():
                if value is None:
                    unknown += 1
                    assert key not in row['provenance']
                    assert row['sourcePer100']['nutrients'][key] is None
                else:
                    assert isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0
                    assert key in row['provenance']
                    source_value = row['sourcePer100']['nutrients'][key]
                    factor = row['sourceServing']['amount'] / 100 if row['sourceServing']['unit'] == 'ml' else 1
                    assert math.isclose(value, source_value * factor, rel_tol=1e-12, abs_tol=1e-12)
            if row['sourceServing']['unit'] == 'ml':
                assert row['basis'] == {'amount': 1, 'unit': 'serving'}
                assert row['portions'] == []
            else:
                assert row['basis'] == {'amount': 100, 'unit': 'g'}
                assert row['portions'][0]['grams'] == row['sourceServing']['amount']
            for field in ('sourcePublished', 'sourceModified', 'labelDate', 'discontinuedDate'):
                assert row[field] is None or iso_date(row[field]) == row[field]
            assert row['sourceVersionRank'] >= 1
            assert row['sourceVersionCount'] >= row['sourceVersionRank']
            group = groups.setdefault(row['versionGroup'], [])
            group.append((row['id'], row['sourcePublished'] or '', int(row['sourceRef']), row['sourceVersionRank'], row['sourceVersionCount'], row['latestSourceId']))
            for history in row['sourceHistory']:
                assert 'nutrients' not in history
                assert isinstance(history['availableInCatalogue'], bool)
                if history['availableInCatalogue']:
                    available_history += 1
                else:
                    unavailable_history += 1
            market_counts[row['market']] += 1
            actual_brands[row['brand']] += 1
            actual_market_brands[row['market']][row['brand']] += 1
            for key in ('grams', 'milliliters', 'gs1Grams', 'gs1Milliliters'):
                matches = {'grams': row['sourceServing']['unit'] == 'g', 'milliliters': row['sourceServing']['unit'] == 'ml', 'gs1Grams': row['sourceServing']['rawUnit'] == 'GRM', 'gs1Milliliters': row['sourceServing']['rawUnit'] == 'MLT'}
                if matches[key] and key not in sample:
                    sample[key] = {k: row[k] for k in ('id', 'name', 'brand', 'sourceServing', 'basis', 'nutrients')}
    assert len(ids) == count == len(ordinals)
    assert dict(market_counts) == manifest['markets']
    declared_brands, declared_market_brands = load_brand_counts(path, manifest)
    assert declared_brands == actual_brands
    assert manifest.get('brandCount', len(manifest.get('brands', {}))) == len(actual_brands)
    if declared_market_brands is not None:
        assert declared_market_brands == actual_market_brands
        assert sum(declared_brands.values()) == count
    for group in groups.values():
        ordered = sorted(group, key=lambda r: (r[1], r[2]), reverse=True)
        for rank, row in enumerate(ordered, 1):
            assert row[3] == rank and row[4] == len(group) and row[5] == ordered[0][0]
    metadata_ids = set()
    metadata_rows = 0
    for page in manifest['indexPages']:
        for row in load(path / 'index' / (page + '.json.gz')):
            assert row['id'] in ids
            assert row['id'] not in metadata_ids
            metadata_ids.add(row['id'])
            assert str(row['ordinal'] // manifest['indexPageSize']).zfill(4) == page
            assert hashlib.sha256(row['id'].encode()).hexdigest()[:3] == row['shard']
            metadata_rows += 1
    assert metadata_ids == ids
    posting_counts = Counter()
    for directory, prefixes in [('tokens', manifest['tokenPrefixes']), ('barcodes', manifest['barcodePrefixes'])]:
        for prefix in prefixes:
            for key, posting in load(path / directory / (prefix + '.json.gz')).items():
                assert key.startswith(prefix)
                assert posting == sorted(set(posting))
                assert all(isinstance(i, int) and 0 <= i < count for i in posting)
                if directory == 'barcodes':
                    assert len(key) == 14 and key.isdigit()
                posting_counts[directory] += len(posting)
    market_ordinals = set()
    for market in manifest['markets']:
        postings = load(path / 'markets' / (market + '.json.gz'))
        assert len(postings) == manifest['markets'][market]
        assert postings == sorted(set(postings))
        assert not market_ordinals.intersection(postings)
        market_ordinals.update(postings)
    assert market_ordinals == ordinals
    unexpected = [str(p) for p in path.rglob('*.json') if p.name != 'manifest.json']
    assert not unexpected, unexpected[:3]
    report = {'pass': True, 'recordsInspected': count, 'byMarket': dict(market_counts), 'brandCount': len(actual_brands), 'brandCountsByMarket': {market: len(counts) for market, counts in actual_market_brands.items()}, 'brandCountsValidatedAgainstEveryRecord': True, 'brandCountsMode': 'per-market' if declared_market_brands is not None else 'legacy-manifest', 'nutrientUnknownsPreserved': unknown, 'normalizedServingUnits': dict(units), 'sourceRawServingUnits': dict(raw_units), 'sourceVersionGroups': len(groups), 'groupsWithMultipleActualSourceRows': sum(len(g) > 1 for g in groups.values()), 'availableSourceHistoryReferences': available_history, 'unavailableSourceHistoryReferencesWithoutInventedNutrients': unavailable_history, 'metadataRowsInspected': metadata_rows, 'postingsInspected': dict(posting_counts), 'allMarketPostingsCoverExactlyAllRecords': True, 'allDataPartitionsGzip': True, 'representativeRecords': sample}
    (report_dir / 'staged-integrity.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'representativeRecords'}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=Path, default=OUT)
    parser.add_argument('--report-dir', type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    check(args.path, args.report_dir)
