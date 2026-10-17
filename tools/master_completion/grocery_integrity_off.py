"""Validate all published OFF rows against their retained licensed source subset."""
from pathlib import Path
from collections import Counter
import gzip, hashlib, json, math, re, sys
from grocery_import_off import ROOT, OUT, normalize, barcode, text
import import_branded_foods as base
sys.path.insert(0,str(ROOT/'tools'))
from source_json import read_json,source_path

def run_legacy():
    manifest=read_json((OUT/'manifest.json'));assert manifest['derivativeLicense']=='ODbL-1.0';assert manifest['recordShardPrefix']==3
    source={}
    with gzip.open(OUT/'source-records.ndjson.gz','rt',encoding='utf-8') as file:
        for line in file:
            row=json.loads(line);assert row['code'] not in source;source[row['code']]=row
    records={};markets=Counter();brands=Counter();zero=Counter();missing=Counter();volumes=0
    for shard in manifest['recordShards']:
        assert re.fullmatch(r'[0-9a-f]{3}',shard)
        for row in read_json((OUT/'records'/(shard+'.json'))):
            assert hashlib.sha256(row['id'].encode()).hexdigest()[:3]==shard;assert row['id'] not in records;records[row['id']]=row
            assert row['market'] in row['markets'];assert row['license']=='ODbL-1.0';assert row['contentsLicense']=='DbCL-1.0';assert row['sourceChecked'] is None;assert row['labelDate'] is None;assert row['status']=='community-label-imported';assert barcode(row['barcode'])==row['barcodeNormalized'];assert row['sourceRef'] in source
            normalized,error=normalize(source[row['sourceRef']]);assert error is None;expected=next(record for record in normalized if record['id']==row['id'])
            actual={key:value for key,value in row.items() if key!='catalogOrdinal'};assert actual==expected,(row['id'],'source normalization mismatch')
            for key,value in row['nutrients'].items():
                if value is None:missing[key]+=1
                else:assert isinstance(value,(int,float)) and math.isfinite(value) and value>=0
                if value==0:zero[key]+=1
            if row['sourceServing']['unit']=='ml':
                volumes+=1;assert row['basis']=={'amount':1,'unit':'serving'};assert not row['portions']
            else:assert row['basis']=={'amount':100,'unit':'g'};assert row['portions'][0]['grams']==row['sourceServing']['amount']
            markets[row['market']]+=1;brands[row['brand']]+=1
    assert len(records)==manifest['profileCount'];assert dict(markets)==manifest['markets'];assert dict(brands)==manifest['brands']
    indexes={}
    for page in manifest['indexPages']:
        for row in read_json((OUT/'index'/(page+'.json'))):
            assert row['id'] in records;assert row['ordinal'] not in indexes;indexes[row['ordinal']]=row;assert row['ordinal']==records[row['id']]['catalogOrdinal'];assert row['shard']==hashlib.sha256(row['id'].encode()).hexdigest()[:3];assert row['search']==text(' '.join([records[row['id']].get('sourceName') or row['name'],row.get('brand') or '',records[row['id']].get('brandOwner') or '']))
    assert len(indexes)==len(records)
    for prefix in manifest['barcodePrefixes']:
        for code,ids in read_json((OUT/'barcodes'/(prefix+'.json'))).items():
            assert code.startswith(prefix);assert len(ids)==len(set(ids));assert all(indexes[i]['barcodeNormalized']==code for i in ids)
    assert manifest['marketPostings'] is True;assert manifest['marketPostingPrefix']=='markets'
    market_postings={}
    for market,count in manifest['markets'].items():
        ids=read_json((OUT/'markets'/(market+'.json')));assert ids==sorted(set(ids));assert len(ids)==count;assert all(indexes[i]['market']==market for i in ids);assert set(ids)=={ordinal for ordinal,row in indexes.items() if row['market']==market};market_postings[market]=ids
        brands=read_json((OUT/'brands'/(market+'.json')));expected=Counter(indexes[i]['brand'] for i in ids);assert brands==dict(expected)
    assert manifest['marketPostingsVersion']==base.hash_value(dict(sorted(market_postings.items())))
    assert manifest['version']==base.hash_value({'records':manifest['recordsVersion'],'marketPostings':manifest['marketPostingsVersion']})
    posting_count=0
    for prefix in manifest['tokenPrefixes']:
        for token,ids in read_json((OUT/'tokens'/(prefix+'.json'))).items():
            assert token.startswith(prefix);assert all(token in indexes[i]['search'].split() for i in ids);assert len(ids)==len(set(ids));posting_count+=len(ids)
    exported=0
    with gzip.open(OUT/'records.ndjson.gz','rt',encoding='utf-8') as file:
        for line in file:
            row=json.loads(line);expected={k:v for k,v in records[row['id']].items() if k!='catalogOrdinal'};assert row==expected;exported+=1
    assert exported==len(records)
    quarantine=read_json((OUT/'quarantined.json'));assert quarantine['status']=='excluded-pending-label-or-rounding-review'
    for row in quarantine['records']:
        assert not any(record['sourceRef']==row['code'] for record in records.values());assert row['reason']=='zero-energy-positive-macros-pending-label-or-rounding-review'
    assert (OUT/'RIGHTS.txt').is_file();assert 'ODbL' in (OUT/'RIGHTS.txt').read_text(encoding='utf-8');assert (OUT/'normalization.py').is_file()
    report={'profilesChecked':len(records),'quarantinedSourceProductsChecked':len(quarantine['records']),'sourceProductsChecked':len(source),'indexesChecked':len(indexes),'tokenPostingsChecked':posting_count,'markets':dict(markets),'volumeServingProfiles':volumes,'missingFields':dict(missing),'trueZeroFields':dict(zero),'largestRecordShardBytes':max(source_path(OUT/'records'/(shard+'.json')).stat().st_size for shard in manifest['recordShards']),'largestTokenPrefixBytes':max(source_path(OUT/'tokens'/(prefix+'.json')).stat().st_size for prefix in manifest['tokenPrefixes']),'largestIndexPageBytes':max(source_path(OUT/'index'/(page+'.json')).stat().st_size for page in manifest['indexPages']),'manifestBytes':(OUT/'manifest.json').stat().st_size,'marketPostingProfilesChecked':sum(len(ids) for ids in market_postings.values()),'sourceMatch':'All normalized public profiles recomputed from retained source subset; imports are not independent package verification.'}
    base.dump(ROOT/'docs/master-completion-2026-10-13/grocery-integrity.json',report);print(json.dumps(report,indent=2))

def run(partition=OUT, report_path=ROOT/'docs/master-completion-2026-10-13/grocery-integrity.json'):
    """Expanded partitions use bounded-memory source, rights and index verification.

    The retained public source subset is sufficient; the original multi-GB bulk
    archive is never opened by this audit. Historical snapshots keep their
    unchanged legacy normalizer and checks.
    """
    partition=Path(partition).resolve()
    manifest=read_json(partition/'manifest.json')
    if manifest.get('source',{}).get('normalizationAuditDate')=='2026-10-17':
        sys.path.insert(0,str(ROOT/'tools/global_coverage_2026_10_17'))
        from off_verify_partition import verify
        result=verify(partition=partition,report_path=report_path,baseline=None)
        counts=result['counts']
        result.update({'profilesChecked':counts['marketProfiles'],
                       'quarantinedSourceProductsChecked':counts['quarantinedSourceProductsChecked'],
                       'sourceProductsChecked':counts['sourceProducts'],
                       'indexesChecked':counts['indexProfiles'],
                       'tokenPostingsChecked':counts['tokenPostings'],
                       'volumeServingProfiles':counts['volumeProfilesWithoutInferredGrams'],
                       'marketPostingProfilesChecked':counts['countryPostings'],
                       'manifestBytes':(partition/'manifest.json').stat().st_size,
                       'sourceMatch':'All normalized public profiles recomputed from retained source subset; imports are not independent package verification.'})
        base.dump(report_path,result)
        return result
    if partition!=OUT.resolve():raise ValueError('Legacy audit supports the original production path only')
    return run_legacy()

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partition',type=Path,default=OUT)
    parser.add_argument('--report',type=Path,default=ROOT/'docs/master-completion-2026-10-13/grocery-integrity.json')
    arguments=parser.parse_args()
    run(arguments.partition,arguments.report)
