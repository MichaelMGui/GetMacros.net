"""Stream the official CC0 USDA Branded download; preserve product identity and units.

No API keys, proprietary scraping, cross-country substitutions, or private logs.
The raw archive remains release evidence, not a runtime dependency.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, io, json, math, re, sys, unicodedata, zipfile

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'docs/master-release-2026-10-12/sources'
OUT=ROOT/'data/branded-foods/usda'
DATE='2026-10-12'
sys.path.insert(0,str(ROOT/'tools/product_release'))
from import_food_library import NUTRIENTS, finite, normalize_unit, dump, hash_value

BRANDS=['Kirkland','Great Value','President','No Name','Compliments','Selection','Irresistibles','Our Finest','Western Family','Trader Joe','Good & Gather','Market Pantry','365','Simple Truth','Kroger','Member','Signature Select','Oreo','Nabisco','Erewhon','Nature\'s Emporium','Quaker','Chobani','Fage','Oikos','Dannon','Yoplait','Dole','Del Monte','Nature Valley','Kellogg','General Mills','Cheerios','Heinz','Campbell','Barilla','Rao','Tyson','Perdue','Foster Farms','Bumble Bee','Starkist','Fairlife','Silk','Almond Breeze','Horizon','Land O Lakes','Philadelphia','Sargento','Tillamook','Jif','Skippy','Smucker','Justin','Kind','Clif','Quest','Premier Protein','Ensure','Orgain','Muscle Milk','Gatorade','Coca-Cola','Pepsi','Dr Pepper','La Croix','Spindrift','Amy','Annie','Birds Eye','Green Giant','Lean Cuisine','Healthy Choice','Stouffer','Ben & Jerry','Haagen','Breyer','Lindt','Ghirardelli','Hershey','Cadbury','Lays','Doritos','Tostitos','Pringles','Ritz','Triscuit','Wheat Thins','Belvita','Welch','Ocean Spray','Minute Maid','Simply','Chiquita','Fresh Express','Taylor Farms','Califia','Vital Farms','Eggland','Dave','Sara Lee','Thomas','Pepperidge Farm','Nature\'s Own','Arnold','Mission','Guerrero','Siete','Bob\'s Red Mill','King Arthur','Gold Medal','Diamond','Blue Diamond','Planters','Wonderful','Nutella','Ferrero','Ferrara','Haribo','Reese','M&M','Snickers','Mars','Duncan Hines','Betty Crocker','Pillsbury','Bisquick','Jimmy Dean','Johnsonville','Oscar Mayer','Applegate','Boar','Hillshire','Hormel','Jennie-O','Butterball','Crisco','Bertolli','Pompeian','Spectrum','Chosen Foods','Wesson','Mazola','Daisy','Breakstone','Lactaid','Siggi','Two Good','Violife','Daiya','Beyond Meat','Impossible','MorningStar','Gardein','Tofurky','Lightlife','Garden of Life','Optimum Nutrition','PBfit','PB2','RXBAR']
def text(value):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode().lower()).strip()
BRAND_TERMS=[text(x) for x in BRANDS]
MARKETS={'United States':'US','US':'US','Canada':'CA','CA':'CA','New Zealand':'NZ','NZ':'NZ','Australia':'AU','United Kingdom':'GB','Mexico':'MX','Japan':'JP','Ireland':'IE'}

def stream_array(handle):
    """Decode one object at a time, keeping memory bounded for the 3.1 GB JSON."""
    decoder=json.JSONDecoder();buffer='';started=False;eof=False
    while True:
        if not started:
            part=handle.read(1024*1024);buffer+=part
            if not part:raise ValueError('Source has no branded food array')
            pos=buffer.find('[')
            if pos<0:continue
            buffer=buffer[pos+1:];started=True
        buffer=buffer.lstrip(' \n\r\t,')
        if buffer.startswith(']'):return
        try:
            row,end=decoder.raw_decode(buffer)
            buffer=buffer[end:];yield row
        except json.JSONDecodeError:
            part=handle.read(1024*1024)
            if not part:raise ValueError('Truncated branded archive')
            buffer+=part

def barcode(value):
    raw=str(value or '').strip()
    if not re.fullmatch(r'\d{8}|\d{12,14}',raw):return None
    return raw.zfill(14)

def normalize(food):
    market=MARKETS.get(food.get('marketCountry'))
    if not market:return None,'unknown-market'
    brand=food.get('brandName') or food.get('brandOwner') or ''
    source_name=str(food.get('description','')).strip()
    if not source_name or not brand:return None,'missing-product-identity'
    name=source_name if len(source_name)<=240 else source_name[:237].rstrip()+'…'
    # Canadian/non-U.S. source rows are retained independently regardless of brand.
    if market=='US' and not any(t in text(brand) for t in BRAND_TERMS):return None,'outside-published-brand-selection'
    raw={row.get('nutrient',{}).get('id'):row for row in food.get('foodNutrients',[])}
    values={};provenance={}
    for key,(_,unit,ids) in NUTRIENTS.items():
        match=next((raw[i] for i in ids if i in raw and finite(raw[i].get('amount')) and normalize_unit(raw[i]['nutrient'].get('unitName'))==normalize_unit(unit)),None)
        values[key]=match['amount'] if match else None
        if match:provenance[key]={'nutrientId':match['nutrient']['id'],'method':match.get('foodNutrientDerivation',{}).get('code','manufacturer-reported')}
    if not any(values[k] is not None for k in ['cal','p','c','fat']):return None,'missing-core-nutrition'
    serving=food.get('servingSize');unit=str(food.get('servingSizeUnit','')).lower().strip()
    if unit not in ['g','ml'] or not finite(serving) or serving<=0:return None,'unsupported-or-absent-serving-basis'
    # USDA normalizes per 100 source units, not always grams. Never infer ml=g.
    portions=[];basis={'amount':100,'unit':'g'};source_values=values.copy()
    if unit=='g':portions=[{'id':'source-serving','label':food.get('householdServingFullText') or f'{serving:g} g source serving','grams':serving}]
    else:
        basis={'amount':1,'unit':'serving'}
        values={k:(v*serving/100 if v is not None else None) for k,v in values.items()}
    code=str(food.get('gtinUpc','')).strip();normalized=barcode(code)
    flags=['Manufacturer-label record imported from USDA; not independently checked against today\'s package.']
    if name!=source_name:flags.append('Long source product wording shortened for display; original wording retained in the source record.')
    if normalized is None:flags.append('Source barcode is missing or has an unsupported length.')
    if unit=='ml':flags.append('Values use the source milliliter serving; no gram weight or density is assumed.')
    if values['sugar'] is not None and values['c'] is not None and values['sugar']>values['c']+1:flags.append('Source total sugars exceed carbohydrate; check the current product label.')
    if food.get('discontinuedDate'):flags.append('Source marks this product discontinued; this is a historical label, not availability information.')
    ingredients=food.get('ingredients') or None
    identity={'barcode':normalized,'market':market,'brand':text(brand),'name':text(source_name),'ingredients':text(ingredients or ''),'package':food.get('packageWeight') or '', 'serving':serving,'unit':unit}
    formulation=hash_value(identity)
    record={'id':'branded:usda:'+str(food['fdcId']),'name':name,'brand':brand,'brandOwner':food.get('brandOwner') or None,'brandName':food.get('brandName') or None,
            'type':'branded','category':food.get('brandedFoodCategory') or 'Packaged foods','market':market,'markets':[market],'language':'en',
            'barcode':code or None,'barcodeNormalized':normalized,'package':food.get('packageWeight') or None,'formulation':formulation,'ingredients':ingredients,
            'sourceId':'usda-branded-2026-04','sourceOrigin':'USDA FoodData Central — manufacturer labels','sourceRef':str(food['fdcId']),
            'sourceUrl':'https://fdc.nal.usda.gov/food-details/'+str(food['fdcId'])+'/nutrients','sourcePublished':food.get('publicationDate'),
            'sourceChecked':None,'retrievedAt':DATE,'sourceRelease':'April 2026 bulk release','sourceModified':food.get('modifiedDate') or None,
            'labelDate':food.get('availableDate') or food.get('modifiedDate') or None,'status':'manufacturer-label-imported','basis':basis,'nutrients':values,'portions':portions,
            'serving':food.get('householdServingFullText') or f'{serving:g} {unit} source serving','sourceServing':{'amount':serving,'unit':unit,'label':food.get('householdServingFullText') or None},
            'sourcePer100':{'unit':unit,'nutrients':source_values},'provenance':provenance,'flags':flags,
            'availability':'Source market attribution; current retailer/warehouse inventory not checked.','license':'CC0-1.0','discontinuedDate':food.get('discontinuedDate') or None}
    if name!=source_name:record['sourceName']=source_name
    record['version']=hash_value(record)
    return record,None

def publish(records,output=OUT,source=None):
    """Token postings keep full labels and nutrient bodies out of the initial page load."""
    records=sorted(records,key=lambda r:(r.get('sourceModified') or r.get('sourcePublished') or '',r['id']),reverse=True)
    shards=defaultdict(list);indexes=defaultdict(list);tokens=defaultdict(list);barcodes=defaultdict(dict);counts=Counter();brands=Counter()
    for i,r in enumerate(records):
        shard=hashlib.sha256(r['id'].encode()).hexdigest()[:2];r['catalogOrdinal']=i
        shards[shard].append(r)
        meta={k:r.get(k) for k in ['id','name','type','category','market','brand','barcode','barcodeNormalized','formulation','sourceId','package','status']}
        meta.update({'shard':shard,'ordinal':i,'search':text(' '.join([r.get('sourceName') or r['name'],r.get('brand') or '',r.get('brandOwner') or '',*(r.get('aliases') or [])]))})
        indexes[str(i//64).zfill(4)].append(meta)
        for token in set(meta['search'].split()):
            if token:tokens[token[:2]].append((token,i))
        code=r.get('barcodeNormalized')
        if code:barcodes[code[:3]].setdefault(code,[]).append(i)
        counts[r['market']]+=1;brands[r.get('brand') or 'Reference foods']+=1
    for shard,rows in sorted(shards.items()):dump(output/'records'/f'{shard}.json',rows)
    for shard,rows in sorted(indexes.items()):dump(output/'index'/f'{shard}.json',rows)
    for shard,rows in sorted(tokens.items()):
        grouped=defaultdict(list)
        for token,ordinal in rows:grouped[token].append(ordinal)
        dump(output/'tokens'/f'{shard}.json',dict(sorted(grouped.items())))
    for shard,rows in sorted(barcodes.items()):dump(output/'barcodes'/f'{shard}.json',rows)
    manifest={'schemaVersion':1,'publishedAt':DATE,'profileCount':len(records),'markets':dict(counts),'brands':dict(brands),'version':hash_value([(r['id'],r['version']) for r in records]),
              'source':source,'indexPageSize':64,'indexPages':sorted(indexes),'tokenPrefixes':sorted(tokens),'barcodePrefixes':sorted(barcodes),'recordShards':sorted(shards),
              'searchPolicy':'Exact barcode first. Brand/name tokens and partial words; updated source versions first. Market, recipe/formulation and package identities remain distinct.',
              'availability':'Tracked source labels, not live retailer inventory. Imported values are not independently package-verified.'}
    dump(output/'manifest.json',manifest)
    return manifest

def run():
    path=RAW/'usda-branded-2026-04.zip';stats=Counter();markets=Counter();records={};source_brands=Counter();duplicate=0
    sha=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
    with zipfile.ZipFile(path) as archive:
        entry=next(n for n in archive.namelist() if n.endswith('.json'))
        with io.TextIOWrapper(archive.open(entry),encoding='utf-8') as handle:
            for i,food in enumerate(stream_array(handle),1):
                if not isinstance(food,dict):continue
                markets[food.get('marketCountry','missing')]+=1
                if i%100000==0:print('read',i,'selected',len(records),flush=True)
                record,reason=normalize(food)
                if reason:stats[reason]+=1;continue
                key=(record['barcodeNormalized'] or record['id'],record['market'],record['formulation'])
                old=records.get(key)
                if old:
                    duplicate+=1
                    if (record.get('sourceModified') or '',record['sourceRef'])<(old.get('sourceModified') or '',old['sourceRef']):continue
                records[key]=record
    source={'id':'usda-branded-2026-04','name':'USDA Global Branded Food Products Database','edition':'April 2026','url':'https://fdc.nal.usda.gov/download-datasets/',
            'downloadUrl':json.loads((RAW/'usda-branded-url.json').read_text())['url'],'sha256':sha,'license':'CC0 1.0','licenseUrl':'https://fdc.nal.usda.gov/api-guide/#bkmk-9','retrievedAt':DATE,
            'quality':'Manufacturer-label imports. Identity, source units and arithmetic checked, not independent current-package verification.',
            'geographicRule':'Exact source marketCountry only; no national equivalence inferred.'}
    manifest=publish(list(records.values()),source=source)
    report={'sourceRowsByMarket':dict(markets),'publishedRows':manifest['profileCount'],'publishedByMarket':manifest['markets'],'publishedByBrand':manifest['brands'],'skipped':dict(stats),'duplicateSameIdentityAndFormulation':duplicate,
            'sourceSha256':sha,'bytes':sum(p.stat().st_size for p in OUT.rglob('*.json')),'sourceFile':path.name,'version':manifest['version']}
    dump(ROOT/'docs/master-release-2026-10-12/branded-import.json',report);print(json.dumps({k:v for k,v in report.items() if k!='publishedByBrand'},indent=2),flush=True)
if __name__=='__main__':run()
