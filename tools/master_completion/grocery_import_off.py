"""Reproducible source-separated Open Food Facts bulk ingestion.

Read the official TSV gzip once. Only explicitly source-attributed supported markets,
identifiable brands/products, valid GTINs, explicit gram/milliliter source servings,
and plausible available nutrients are published. Missing data remain null.
This derived partition is ODbL 1.0, never combined with CC0/OGL nutrient records.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse, csv, gzip, hashlib, json, math, re, sys, unicodedata
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/master_release'))
import import_branded_foods as base
DATE='2026-10-13'
SOURCE_URL='https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'
OUT=ROOT/'data/branded-foods/off'
RAW=ROOT/'docs/master-completion-2026-10-13/grocery-sources/openfoodfacts-products-2026-10-13.tsv.gz'
REPORT=ROOT/'docs/master-completion-2026-10-13/grocery-import.json'
MARKETS={'en:canada':'CA','en:united-states':'US','en:mexico':'MX','en:united-kingdom':'GB','en:ireland':'IE','en:australia':'AU','en:new-zealand':'NZ','en:japan':'JP'}
BRANDS=base.BRANDS+['President\'s Choice','No Name','Compliments','Selection','Irresistibles','Our Finest','Western Family','Nature\'s Emporium','Tesco','Sainsbury','Asda','Morrisons','Waitrose','Marks & Spencer','Aldi','Lidl','M&S','Woolworths','Coles','Pam\'s','Watties','Sanitarium','Lala','Bimbo','Barcel','Gamesa','La Costena','La Moderna','Maruchan','Nissin','Meiji','Morinaga','Kewpie','Calbee','Glico','Ito En','明治','森永','日清','キユーピー','カルビー','グリコ','伊藤園']
def text(value):
    value=''.join(c for c in unicodedata.normalize('NFKD',str(value)).lower() if not unicodedata.combining(c))
    return re.sub(r'[^\w]+',' ',value.replace('_',' '),flags=re.UNICODE).strip()

BRAND_TERMS=[text(x) for x in BRANDS]

MAP={'cal':('energy-kcal_100g',1),'p':('proteins_100g',1),'c':('carbohydrates_100g',1),'fat':('fat_100g',1),'f':('fiber_100g',1),'na':('sodium_100g',1000),'sugar':('sugars_100g',1),'sat':('saturated-fat_100g',1),'chol':('cholesterol_100g',1000),'calcium':('calcium_100g',1000),'iron':('iron_100g',1000),'magnesium':('magnesium_100g',1000),'phosphorus':('phosphorus_100g',1000),'potassium':('potassium_100g',1000),'zinc':('zinc_100g',1000),'selenium':('selenium_100g',1000000),'vitaminC':('vitamin-c_100g',1000),'thiamin':('vitamin-b1_100g',1000),'riboflavin':('vitamin-b2_100g',1000),'niacin':('vitamin-pp_100g',1000),'vitaminB6':('vitamin-b6_100g',1000),'folate':('folates_100g',1000000),'vitaminB12':('vitamin-b12_100g',1000000),'vitaminD':('vitamin-d_100g',1000000),'vitaminE':('vitamin-e_100g',1000),'monoFat':('monounsaturated-fat_100g',1),'polyFat':('polyunsaturated-fat_100g',1)}
# Vitamin A RAE, folate DFE and phylloquinone are intentionally not inferred from
# OFF's differently named generic vitamin A, folic acid or vitamin K fields.
SOURCE_FIELDS=['code','product_name','brands','brand_owner','quantity','countries_tags','ingredients_text','serving_size','serving_quantity','no_nutrition_data','categories_en','categories_tags','last_modified_t','last_modified_datetime','data_quality_errors_tags','energy-kj_100g',*[field for field,_ in MAP.values()]]
def number(value):
    try: value=float(value)
    except (TypeError,ValueError):return None
    return value if math.isfinite(value) and value>=0 else None

def barcode(value):
    raw=str(value or '').strip()
    if not re.fullmatch(r'\d{8}|\d{12,14}',raw):return None
    if len(set(raw))==1:return None
    # GS1 modulo-10 check prevents numeric-looking strings becoming fake identifiers.
    if (sum(int(x)*(3 if i%2==0 else 1) for i,x in enumerate(reversed(raw[:-1])))+int(raw[-1]))%10:return None
    return raw.zfill(14)

def source_serving(row):
    label=str(row.get('serving_size') or '').strip()
    if any(symbol in label for symbol in ['<','>','≤','≥']):return None
    matches=re.findall(r'(\d+(?:[.,]\d+)?)\s*(ml|mL|g|grams?)\b',label)
    types={'ml' if u.lower()=='ml' else 'g' for _,u in matches}
    if len(types)!=1:return None
    unit=next(iter(types)); amount=number(row.get('serving_quantity'))
    parsed=[number(n.replace(',','.')) for n,_ in matches]
    if not amount or amount>10000 or len(parsed)!=1 or abs(parsed[0]-amount)>max(.01,amount*.001):return None
    return {'amount':amount,'unit':unit,'label':label}

def normalize(row):
    markets=[market for tag,market in MARKETS.items() if tag in str(row.get('countries_tags','')).split(',')]
    if not markets:return [],'no-supported-source-market'
    name=str(row.get('product_name') or '').strip();brand=str(row.get('brands') or '').strip()
    if not name or not brand:return [],'missing-product-or-brand'
    normalized_brand=' '+text(brand)+' '
    if 'CA' not in markets and not any(' '+term+' ' in normalized_brand for term in BRAND_TERMS):return [],'outside-published-brand-selection'
    code=str(row.get('code') or '').strip();gtin=barcode(code)
    if not gtin:return [],'invalid-or-missing-barcode'
    if row.get('no_nutrition_data')=='on':return [],'source-no-nutrition'
    if any(tag in str(row.get('categories_tags') or '') for tag in ['en:food-supplements','en:baby-foods','en:infant-formula']):return [],'excluded-supplement-or-infant-product'
    if row.get('data_quality_errors_tags'):return [],'source-quality-errors'
    serving=source_serving(row)
    if not serving:return [],'ambiguous-or-missing-serving-unit'
    native={key:number(row.get(field)) for key,(field,_) in MAP.items()}
    values={key:(native[key]*factor if native[key] is not None else None) for key,(_,factor) in MAP.items()}
    if values['cal'] is None:
        kj=number(row.get('energy-kj_100g'))
        if kj is not None:values['cal']=kj/4.184
    for key in base.NUTRIENTS:values.setdefault(key,None)
    if not any(values[key] is not None for key in ['cal','p','c','fat']):return [],'missing-core-nutrition'
    if values['cal']==0 and any(values[key] is not None and values[key]>1 for key in ['p','fat']):return [],'zero-energy-positive-macros-pending-label-or-rounding-review'
    if values['cal'] is not None and values['cal']>950 or any(values[key] is not None and values[key]>100.5 for key in ['p','c','fat','f','sugar','sat']):return [],'implausible-source-density'
    if all(values[key] is not None for key in ['p','c','fat']) and sum(values[key] for key in ['p','c','fat'])>110:return [],'contradictory-core-density'
    if values['sugar'] is not None and values['c'] is not None and values['sugar']>values['c']+1:return [],'sugars-exceed-carbohydrate'
    if values['sat'] is not None and values['fat'] is not None and values['sat']>values['fat']+1:return [],'saturated-exceeds-total-fat'
    basis={'amount':100,'unit':'g'};portions=[{'id':'source-serving','label':serving['label'],'grams':serving['amount']}]
    source_values=values.copy()
    if serving['unit']=='ml':
        basis={'amount':1,'unit':'serving'};portions=[]
        values={key:(value*serving['amount']/100 if value is not None else None) for key,value in values.items()}
    original_name=name
    if len(name)>240:name=name[:237].rstrip()+'…'
    ingredients=str(row.get('ingredients_text') or '').strip() or None
    source_date=row.get('last_modified_datetime') or None
    records=[]
    for market in markets:
        identity={'barcode':gtin,'market':market,'name':text(original_name),'brand':text(brand),'package':row.get('quantity') or '', 'ingredients':text(ingredients or ''),'serving':serving}
        flags=['Open Food Facts community record imported; not independently verified against the current package.','Source country tags indicate reported markets, not current store inventory or a guarantee of the local formulation.']
        if len(markets)>1:flags.append('One source record is tagged for multiple markets; confirm the exact local package before logging.')
        if serving['unit']=='ml':flags.append('Uses the named milliliter serving; no gram weight or density is assumed.')
        if not all(values[key] is not None for key in ['cal','p','c','fat']):flags.append('Some core nutrition fields are unavailable; unknown values are not zero.')
        record={'id':'branded:off:'+code+':'+market,'name':name,'brand':brand,'brandName':brand,'brandOwner':row.get('brand_owner') or None,'type':'branded','market':market,'markets':markets,'language':'und','category':row.get('categories_en') or 'Packaged products',
            'barcode':code,'barcodeNormalized':gtin,'package':row.get('quantity') or None,'formulation':base.hash_value(identity),'ingredients':ingredients,'sourceId':'off-products-'+DATE,'sourceOrigin':'Open Food Facts — community product records','sourceRef':code,'sourceUrl':'https://world.openfoodfacts.org/product/'+code,'sourcePublished':None,'sourceChecked':None,'sourceModified':source_date,'labelDate':None,'retrievedAt':DATE,'sourceRelease':DATE+' official bulk export retrieval','status':'community-label-imported','basis':basis,'nutrients':values,'portions':portions,'serving':serving['label'],'sourceServing':serving,'sourcePer100':{'unit':serving['unit'],'nutrients':source_values},
            'provenance':{key:{'method':'OFF normalized as-sold field; standard source grams converted to displayed units','sourceField':field,'sourceValue':native[key],'unitFactor':factor,'sourceBasis':'100 '+serving['unit']} for key,(field,factor) in MAP.items() if native[key] is not None},'flags':flags,'availability':'Community-reported country attribution; retailer stock and national formulation not independently established.','license':'ODbL-1.0','licenseUrl':'https://opendatacommons.org/licenses/odbl/1-0/','contentsLicense':'DbCL-1.0','attribution':'Contains information from Open Food Facts, made available under the Open Database License (ODbL).','attributionUrl':'https://world.openfoodfacts.org/','redistributionUrl':'/data/branded-foods/off/source-records.ndjson.gz'}
        if native['cal'] is None and values['cal'] is not None:record['provenance']['cal']={'method':'OFF energy-kJ normalized value divided by 4.184; then source-serving scaling where needed','sourceField':'energy-kj_100g','sourceValue':number(row.get('energy-kj_100g')),'sourceBasis':'100 '+serving['unit']}
        if name!=original_name:record['sourceName']=original_name
        record['version']=base.hash_value(record);records.append(record)
    return records,None

def source_sha256(path):
    with path.open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()

def merge_quarantine(previous, current):
    """Keep excluded-source review evidence when rebuilding an eligible subset."""
    merged={}
    for record in [*previous, *current]:
        code=record.get('code')
        if not code:raise ValueError('Quarantine ledger record has no source product code')
        merged[code]=record
    return [merged[code] for code in sorted(merged)]

def run(path=RAW,output=OUT,subset=False):
    global DATE
    stats=Counter();records={};source_rows={};quarantined=[];csv.field_size_limit(100_000_000)
    prior_manifest=json.loads((output/'manifest.json').read_text(encoding='utf-8')) if subset else None
    prior_report=json.loads(REPORT.read_text(encoding='utf-8')) if subset else None
    quarantine_file=output/'quarantined.json'
    previous_quarantine=json.loads(quarantine_file.read_text(encoding='utf-8'))['records'] if subset and quarantine_file.exists() else []
    if not isinstance(previous_quarantine,list):raise ValueError('Quarantine ledger records must be a list')
    if subset:DATE=prior_manifest['source']['retrievedAt']
    subset_sha=source_sha256(path) if subset else None
    with gzip.open(path,'rt',encoding='utf-8',newline='') as handle:
        if subset:
            reader=(json.loads(line) for line in handle)
        else:
            reader=csv.DictReader(handle,delimiter='\t')
            if not set(SOURCE_FIELDS)<=set(reader.fieldnames):raise ValueError('Official source schema changed: required fields missing')
        for i,row in enumerate(reader,1):
            if subset and not set(SOURCE_FIELDS)<=set(row):raise ValueError('Retained source subset schema changed')
            selected,error=normalize(row)
            if error:
                stats[error]+=1
                if error=='zero-energy-positive-macros-pending-label-or-rounding-review':quarantined.append({'code':row['code'],'name':row['product_name'],'brand':row['brands'],'countries':row['countries_tags'],'sourceUrl':'https://world.openfoodfacts.org/product/'+row['code'],'reason':error,'nativePer100':{key:row.get(field) for key,(field,factor) in MAP.items() if key in ['cal','p','c','fat']}})
            else:
                for record in selected:
                    key=(record['barcodeNormalized'],record['market'],record['formulation'])
                    old=records.get(key)
                    if old and (old.get('sourceModified') or '')>(record.get('sourceModified') or ''):continue
                    records[key]=record
                source_rows[row['code']]={key:row.get(key,'') for key in SOURCE_FIELDS}
            if i%250000==0:print('read',i,'published-market-records',len(records),flush=True)
    if not records:raise ValueError('No source records passed review; existing partition is not replaced')
    quarantined=merge_quarantine(previous_quarantine,quarantined)
    output.mkdir(parents=True,exist_ok=True)
    # Publish the actual source subset freely in a machine-readable compressed form.
    # No images, trademarks, ratings, marketing text, allergen inference or extra
    # private/user-created contents are imported into this ODbL partition.
    with (output/'source-records.ndjson.gz').open('wb') as handle:
        with gzip.GzipFile(fileobj=handle,mode='wb',mtime=0) as archive:
            for code,row in sorted(source_rows.items()):archive.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    with (output/'records.ndjson.gz').open('wb') as handle:
        with gzip.GzipFile(fileobj=handle,mode='wb',mtime=0) as archive:
            for record in sorted(records.values(),key=lambda record:record['id']):archive.write((json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    base.DATE=DATE
    base.text=text
    source={'id':'off-products-'+DATE,'name':'Open Food Facts — source-separated community product subset','url':'https://world.openfoodfacts.org/','downloadUrl':SOURCE_URL,'retrievedAt':DATE,'sha256':prior_manifest['source']['sha256'] if subset else source_sha256(path),'edition':DATE+' official bulk export retrieval','license':'ODbL 1.0','licenseUrl':'https://opendatacommons.org/licenses/odbl/1-0/','contentsLicense':'Database Contents License 1.0','contentsLicenseUrl':'https://opendatacommons.org/licenses/dbcl/1-0/','attribution':'Contains information from Open Food Facts, made available under the Open Database License (ODbL).','sourceSubsetUrl':'/data/branded-foods/off/source-records.ndjson.gz','quality':'Community labels imported, not independent current-package verification. Valid identity, explicit source serving unit, available nutrients and import arithmetic checked.','scope':'Source-attributed Canadian products plus a curated brand selection in other supported markets. Explicit source servings and quality gates apply; not full retailer inventory.','images':'No product images copied. OFF images have separate CC BY-SA and package rights.'}
    if subset:source['reprocessedSourceSubsetSha256']=subset_sha
    base.dump(output/'quarantined.json',{'status':'excluded-pending-label-or-rounding-review','license':'ODbL-1.0','licenseUrl':'https://opendatacommons.org/licenses/odbl/1-0/','attribution':source['attribution'],'source':source['url'],'records':quarantined,'policy':'No corrected calories are invented. Tiny-serving label rounding can produce ambiguous normalized values; these entries are not used by search or logging until reviewed.'})
    manifest=base.publish(list(records.values()),output=output,source=source)
    # Three hex characters keep each label fetch small as the catalogue grows.
    from collections import defaultdict
    shards=defaultdict(list)
    for record in records.values():shards[hashlib.sha256(record['id'].encode()).hexdigest()[:3]].append(record)
    record_root=(output/'records').resolve()
    assert record_root.is_relative_to(output.resolve())
    for file in record_root.glob('*.json'):
        if re.fullmatch(r'[0-9a-f]{2,3}\.json',file.name):file.unlink()
    for shard,rows in sorted(shards.items()):base.dump(record_root/(shard+'.json'),sorted(rows,key=lambda row:row['catalogOrdinal']))
    for page in manifest['indexPages']:
        file=output/'index'/(page+'.json');rows=json.loads(file.read_text(encoding='utf-8'))
        for row in rows:row['shard']=hashlib.sha256(row['id'].encode()).hexdigest()[:3]
        base.dump(file,rows)
    manifest['recordShardPrefix']=3;manifest['recordShards']=sorted(shards)
    country_ids=defaultdict(list);country_brands=defaultdict(Counter)
    for record in records.values():country_ids[record['market']].append(record['catalogOrdinal']);country_brands[record['market']][record['brand']]+=1
    for market,ids in sorted(country_ids.items()):
        base.dump(output/'markets'/(market+'.json'),sorted(ids));base.dump(output/'brands'/(market+'.json'),dict(sorted(country_brands[market].items())))
    manifest['marketPostings']=True;manifest['marketPostingPrefix']='markets';manifest['marketPostingsVersion']=base.hash_value({market:sorted(ids) for market,ids in sorted(country_ids.items())});manifest['brandCountsPrefix']='brands'
    manifest['recordsVersion']=manifest['version'];manifest['version']=base.hash_value({'records':manifest['recordsVersion'],'marketPostings':manifest['marketPostingsVersion']})
    manifest['availability']='Community source labels, not live retailer inventory or independent package verification.'
    manifest['derivativeLicense']='ODbL-1.0';manifest['downloadUrl']='/data/branded-foods/off/records.ndjson.gz';manifest['normalizationUrl']='/data/branded-foods/off/normalization.py'
    base.dump(output/'manifest.json',manifest)
    (output/'normalization.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
    (output/'RIGHTS.txt').write_text('Open Food Facts source-separated derivative partition\n\nContains information from Open Food Facts (https://world.openfoodfacts.org/), made available under the Open Database License (ODbL) 1.0: https://opendatacommons.org/licenses/odbl/1-0/\nIndividual database contents: https://opendatacommons.org/licenses/dbcl/1-0/\n\nThe independently licensed USDA CC0, Canadian Nutrient File OGL, and factual retailer partitions are not incorporated into this derivative. No nutrient values are fused across providers.\nFree machine-readable source subset: source-records.ndjson.gz. Free normalized export: records.ndjson.gz. Free normalized records and indexes: manifest.json and its named shards. Transformation algorithm: normalization.py. Retain these notices and share-alike requirements when redistributing this partition.\n\nNo product imagery is included. Brand names identify products; no partnership or endorsement is implied. Country tags are community-reported; no live retail inventory or independent package verification is claimed.\n',encoding='utf-8')
    source_read=i
    if subset:
        stats=Counter(prior_report.get('skipped',{}))+stats
        # A preserved exclusion is one source product, not another new failure
        # each time the same subset is reprocessed.
        if quarantined:stats['zero-energy-positive-macros-pending-label-or-rounding-review']=len(quarantined)
        source_read=prior_report['sourceRowsRead']
    report={'sourceUrl':SOURCE_URL,'retrievedAt':DATE,'sourceRowsRead':source_read,'sourceSubsetReprocessedRows':i if subset else None,'quarantinedSourceProducts':len(quarantined),'sourceProductsSelected':len(source_rows),'publishedMarketRecords':len(records),'byMarket':manifest['markets'],'byBrand':manifest['brands'],'coreMacrosAvailable':sum(all(record['nutrients'][key] is not None for key in ['cal','p','c','fat']) for record in records.values()),'partialCoreRecords':sum(not all(record['nutrients'][key] is not None for key in ['cal','p','c','fat']) for record in records.values()),'volumeServingRecords':sum(record['sourceServing']['unit']=='ml' for record in records.values()),'skipped':dict(stats),'sourceSha256':source['sha256'],'publishedBytes':sum(file.stat().st_size for file in output.rglob('*') if file.is_file()),'sourceSubsetBytes':(output/'source-records.ndjson.gz').stat().st_size,'version':manifest['version']}
    base.dump(REPORT,report);print(json.dumps({key:value for key,value in report.items() if key!='byBrand'},indent=2),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,default=RAW);parser.add_argument('--output',type=Path,default=OUT);parser.add_argument('--retrieval-date',default=DATE);parser.add_argument('--source-subset',action='store_true',help='Reprocess the retained licensed source subset, preserving the original bulk provenance');args=parser.parse_args();datetime.strptime(args.retrieval_date,'%Y-%m-%d');DATE=args.retrieval_date;run(args.source,args.output,args.source_subset)
