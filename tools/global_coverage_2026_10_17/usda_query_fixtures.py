"""Prove U.S. retailer-label search coverage using actual staged USDA records."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

from usda_expand import DATE, OUT, REPORT_DIR, ROOT, baseline_ids, compact_brand_manifest, dump_json, load_data_json, text


LABELS = [
    ('Publix', ['publix']), ('H-E-B', ['h e b', 'heb']),
    ('Wegmans', ['wegmans']), ('Meijer', ['meijer']),
    ('ALDI', ['aldi']), ('Millville', ['millville']),
    ('Food Lion', ['food lion']), ('Hy-Vee', ['hy vee']),
    ('Hannaford', ['hannaford']),
]


def brand_matches(brand, terms):
    normalized = text(brand)
    return any(normalized == term or normalized.startswith(term + ' ') for term in terms)


def make_query(label, row):
    remove = set(text(row['brand']).split()) | set(text(label).split())
    remove.update(('a', 'an', 'the', 'and', 'of', 'with', 'for', 'in', 'to', 'oz', 'ounce', 'ounces', 'pint', 'fl'))
    words = []
    for word in text(row['name']).split():
        if word not in remove and not word.isdigit() and word not in words:
            words.append(word)
    return label + (' ' + ' '.join(words[:5]) if words else '')


def fixtures(output=OUT, report_dir=REPORT_DIR):
    manifest = load_data_json(output / 'manifest.json')
    original_report = load_data_json(report_dir / 'expansion-report.json')
    previous_manifest_path = ROOT / 'data/branded-foods/usda/manifest.json'
    previous_manifest = load_data_json(previous_manifest_path) if previous_manifest_path.exists() else {}
    compare_previous = previous_manifest.get('profileCount') == original_report['establishedIds']
    previous_ids = baseline_ids(previous_manifest_path.parent) if compare_previous else set()
    coverage = {label: {'sourceBrandLabels': Counter(), 'sourceProfiles': 0, 'latestSourceProfiles': 0, 'versionGroups': set(), 'preferred': [], 'fallback': []} for label, _ in LABELS}
    for page in manifest['indexPages']:
        for row in load_data_json(output / 'index' / (page + '.json')):
            if row['market'] != 'US':
                continue
            for label, terms in LABELS:
                if not brand_matches(row['brand'], terms):
                    continue
                found = coverage[label]
                found['sourceProfiles'] += 1
                found['sourceBrandLabels'][row['brand']] += 1
                found['versionGroups'].add(row['versionGroup'])
                if row.get('sourceVersionRank', 1) != 1:
                    continue
                found['latestSourceProfiles'] += 1
                if not row.get('barcodeNormalized'):
                    continue
                candidates = found['preferred'] if row['barcodeNormalized'].startswith('0') else found['fallback']
                if len(candidates) < 2 and all(r['versionGroup'] != row['versionGroup'] for r in candidates):
                    candidates.append(row)
    flat, summaries = [], []
    token_cache, barcode_cache = {}, {}
    us_ordinals = set(load_data_json(output / 'markets/US.json'))
    for label, terms in LABELS:
        found = coverage[label]
        if not found['sourceProfiles']:
            summaries.append({'label': label, 'market': 'US', 'sourceProfiles': 0, 'note': 'No matching source brand label was found; no example invented.'})
            continue
        candidates = (found['preferred'] + found['fallback'])[:2]
        examples = []
        for meta in candidates:
            shard = hashlib.sha256(meta['id'].encode()).hexdigest()[:manifest['recordShardPrefix']]
            record = next(row for row in load_data_json(output / 'records' / (shard + '.json')) if row['id'] == meta['id'])
            assert record['market'] == 'US' and brand_matches(record['brand'], terms)
            entry = {key: record.get(key) for key in ('id', 'name', 'brand', 'brandOwner', 'brandName', 'barcode', 'barcodeNormalized', 'sourceServing', 'market', 'basis', 'sourceUrl', 'sourcePublished', 'sourceModified', 'sourceVersionRole', 'latestSourceId', 'sourceId')}
            entry.update({'label': label, 'query': make_query(label, record), 'barcodeQuery': record['barcode'], 'expectedIds': [record['id']], 'sourceChecked': record['sourceChecked'], 'inPreviousPublishedCatalogue': record['id'] in previous_ids if compare_previous else None})
            assert record['sourceChecked'] is None
            matches = None
            aliases = {'yoghurt': 'yogurt', 'fibre': 'fiber', 'kirklands': 'kirkland', 'oreos': 'oreo'}
            for token in (aliases.get(word, word) for word in text(entry['query']).split() if word not in ('a', 'an', 'the', 'and', 'of', 'with')):
                prefix = token[:2]
                if prefix not in token_cache:
                    token_cache[prefix] = load_data_json(output / 'tokens' / (prefix + '.json'))
                posting = set(n for word, rows in token_cache[prefix].items() if word == token or word.startswith(token) for n in rows)
                matches = posting if matches is None else matches & posting
            local = sorted((matches or set()) & us_ordinals)
            assert meta['ordinal'] in local, 'Fixture query misses its actual source record: ' + entry['query']
            assert local.index(meta['ordinal']) < 120, 'Fixture falls outside the bounded runtime candidate window'
            code = record['barcodeNormalized']
            prefix = code[:3]
            if prefix not in barcode_cache:
                barcode_cache[prefix] = load_data_json(output / 'barcodes' / (prefix + '.json'))
            assert meta['ordinal'] in barcode_cache[prefix][code]
            entry.update({'queryPostingValidated': True, 'barcodePostingValidated': True, 'queryCandidateRank': local.index(meta['ordinal']) + 1, 'queryCandidatesInUSSource': len(local)})
            flat.append(entry); examples.append(record['id'])
        summaries.append({'label': label, 'market': 'US', 'sourceProfiles': found['sourceProfiles'], 'sourceVersionGroups': len(found['versionGroups']), 'latestSourceProfiles': found['latestSourceProfiles'], 'matchedSourceBrands': dict(sorted(found['sourceBrandLabels'].items())), 'representativeIds': examples, 'matchRule': 'Normalized source brand label equals or begins with one of: ' + ', '.join(terms)})
    report = {'source': 'USDA Global Branded Food Products Database', 'sourcePartition': 'usda', 'sourceVersion': manifest['version'], 'sourceRelease': manifest['source']['edition'], 'sourceReleaseSnapshot': manifest['source'].get('releaseDate'), 'generatedAt': DATE, 'market': 'US', 'license': 'CC0-1.0', 'evidenceRule': 'Counts and example identities come only from actual published staged rows. Latest means latest source publication in this archive; current packages and retailer inventory were not independently checked. ALDI and Millville are counted as separate source labels; no additional retailer affiliation or availability is inferred.', 'previousPublishedCatalogueCompared': compare_previous, 'previousPublishedCatalogueProfiles': len(previous_ids) if compare_previous else None, 'coverage': summaries, 'fixtures': flat}
    dump_json(report_dir / 'query-fixtures.json', report)
    print(json.dumps({'labelsWithActualRecords': len([s for s in summaries if s['sourceProfiles']]), 'fixtures': len(flat), 'allRepresentativesNewToPreviousCatalogue': all(e['inPreviousPublishedCatalogue'] is False for e in flat) if compare_previous else None, 'counts': {s['label']: s['sourceProfiles'] for s in summaries}, 'fixtureIds': [e['id'] for e in flat]}, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT)
    parser.add_argument('--report-dir', type=Path, default=REPORT_DIR)
    parser.add_argument('--compact-manifest', action='store_true')
    args = parser.parse_args()
    if args.compact_manifest:
        print(json.dumps(compact_brand_manifest(args.output, args.report_dir), indent=2))
    fixtures(args.output, args.report_dir)
