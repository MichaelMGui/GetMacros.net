"""Reproducible factual imports from licensed USDA downloads; no web-page scraping."""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, hashlib, json, math, re, zipfile

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'docs/global-product-release-2026-10-11/sources'
OUT = ROOT / 'data/food-library'
DATE = '2026-10-11'
NUTRIENTS = {
    'cal': ('Calories', 'kcal', [2048, 2047, 1008]),
    'p': ('Protein', 'g', [1003]), 'c': ('Carbohydrate', 'g', [1005]),
    'fat': ('Fat', 'g', [1004]), 'f': ('Fiber', 'g', [1079]),
    'na': ('Sodium', 'mg', [1093]), 'sugar': ('Total sugars', 'g', [2000, 1063]),
    'sat': ('Saturated fat', 'g', [1258]), 'chol': ('Cholesterol', 'mg', [1253]),
    'calcium': ('Calcium', 'mg', [1087]), 'iron': ('Iron', 'mg', [1089]),
    'magnesium': ('Magnesium', 'mg', [1090]), 'phosphorus': ('Phosphorus', 'mg', [1091]),
    'potassium': ('Potassium', 'mg', [1092]), 'zinc': ('Zinc', 'mg', [1095]),
    'selenium': ('Selenium', 'µg', [1103]), 'vitaminC': ('Vitamin C', 'mg', [1162]),
    'thiamin': ('Thiamin (B1)', 'mg', [1165]), 'riboflavin': ('Riboflavin (B2)', 'mg', [1166]),
    'niacin': ('Niacin', 'mg', [1167]), 'vitaminB6': ('Vitamin B6', 'mg', [1175]),
    'folate': ('Folate, total', 'µg', [1177]), 'folateDFE': ('Folate DFE', 'µg', [1190]),
    'vitaminB12': ('Vitamin B12', 'µg', [1178]), 'vitaminA': ('Vitamin A, RAE', 'µg', [1106]),
    'vitaminD': ('Vitamin D (D2 + D3)', 'µg', [1114]),
    'vitaminE': ('Vitamin E (alpha-tocopherol)', 'mg', [1109]),
    'vitaminK': ('Vitamin K (phylloquinone)', 'µg', [1185]),
    'monoFat': ('Monounsaturated fat', 'g', [1292]), 'polyFat': ('Polyunsaturated fat', 'g', [1293]),
}
SOURCES = {
    'foundation': {'id':'usda-foundation-2026-04','name':'USDA Foundation Foods','edition':'April 2026 download', 'kind':'foundation', 'scope':'U.S. food composition reference; not local restaurant menu data'},
    'sr-legacy': {'id':'usda-sr-legacy-2018','name':'USDA SR Legacy','edition':'April 2018 final historical edition', 'kind':'legacy', 'scope':'Historical U.S. reference; named branded formulations may have changed'},
    'survey': {'id':'usda-fndds-2021-2023','name':'USDA FNDDS','edition':'2021–2023 survey foods, published October 2024', 'kind':'prepared', 'scope':'U.S. survey food profiles; prepared dishes are reference recipes, not your exact recipe'},
}

def finite(value): return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def hash_value(value): return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:16]
def normalize_unit(unit): return str(unit).lower().replace('μ','µ').replace('ug','µg')

def record(food, source, methods):
    raw={row['nutrient']['id']:row for row in food.get('foodNutrients',[]) if row.get('nutrient')}
    values={};provenance={};conflicts=[]
    for key,(label,unit,ids) in NUTRIENTS.items():
        match=next((raw[i] for i in ids if i in raw and finite(raw[i].get('amount')) and normalize_unit(raw[i]['nutrient'].get('unitName'))==normalize_unit(unit)),None)
        values[key]=match['amount'] if match else None
        if match:
            derive=match.get('foodNutrientDerivation',{})
            method=derive.get('code','source-reported')
            methods[method]=derive.get('description','Source-reported nutrient value')
            provenance[key]={'nutrientId':match['nutrient']['id'],'method':method}
    if not any(values[k] is not None for k in ['cal','p','c','fat']):return None
    # USDA carbohydrate methods can differ. Flag these instead of "correcting" source values.
    if values['sugar'] is not None and values['c'] is not None and values['sugar']>values['c']+1:conflicts.append('Source total sugars exceed carbohydrate; different source methods or rounding may apply.')
    portions=[]
    for portion in food.get('foodPortions',[]):
        grams=portion.get('gramWeight')
        if not finite(grams) or grams==0:continue
        label=portion.get('portionDescription')
        if not label:
            measure=portion.get('measureUnit',{}).get('name','')
            if measure in ['undetermined','RACC','Quantity not specified']:measure=''
            modifier=portion.get('modifier','')
            quantity=portion.get('amount',portion.get('value',1))
            label=' '.join(str(x) for x in [f'{quantity:g}' if finite(quantity) else '1',measure,modifier] if x)
        if label and not re.fullmatch(r'\d+(?:\.\d+)?',label):portions.append({'id':str(portion['id']),'label':label,'grams':grams})
    category=food.get('foodCategory',{}).get('description') or food.get('wweiaFoodCategory',{}).get('wweiaFoodCategoryDescription') or 'Other foods'
    data={'id':'fdc:'+str(food['fdcId']),'name':food['description'],'type':source['kind'],'category':category,
          'market':'US-reference','language':'en','sourceId':source['id'],'sourceRef':str(food['fdcId']),
          'sourcePublished':food.get('publicationDate'),'basis':{'amount':100,'unit':'g'},
          'nutrients':values,'portions':portions,'provenance':provenance,
          'status':'source-imported','flags':conflicts,'note':food.get('footnote','')}
    data['version']=hash_value(data)
    return data

def run():
    retrieval={row['file']:row for row in json.loads((RAW/'retrieval.json').read_text(encoding='utf-8')) if 'sha256' in row}
    records=[];methods={};excluded=[]
    for name,source in SOURCES.items():
        path=RAW/(name+'.zip')
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha==retrieval[path.name]['sha256'], 'Source bytes changed after retrieval'
        source.update({'url':'https://fdc.nal.usda.gov/download-datasets/','downloadUrl':retrieval[path.name]['url'],
                       'license':'CC0 1.0','licenseUrl':'https://fdc.nal.usda.gov/api-guide/#bkmk-9',
                       'retrievedAt':DATE,'importCheckedAt':DATE,'sha256':sha,
                       'verification':'Schema, source units, identity and import arithmetic checked; individual food chemistry was not independently remeasured.'})
        with zipfile.ZipFile(path) as archive:
            entry=next(x for x in archive.namelist() if x.endswith('.json'))
            data=json.loads(archive.read(entry))
        foods=next(v for v in data.values() if isinstance(v,list))
        for food in foods:
            if not isinstance(food,dict) or not isinstance(food.get('fdcId'),int):
                excluded.append({'id':None,'source':source['id'],'reason':'Empty source entry or absent food identity'})
                continue
            normalized=record(food,source,methods)
            if normalized:records.append(normalized)
            else:excluded.append({'id':food.get('fdcId'),'reason':'No usable core nutrient values in this source profile'})
        print(name, len(foods),'source profiles read')
    assert len({r['id'] for r in records})==len(records)
    shards=defaultdict(list)
    for r in records:shards[hashlib.sha256(r['id'].encode()).hexdigest()[:2]].append(r)
    index=[]
    for shard,rows in sorted(shards.items()):
        dump(OUT/'records'/f'{shard}.json',rows)
        index.extend({'id':r['id'],'name':r['name'],'type':r['type'],'category':r['category'],'shard':shard} for r in rows)
    index.sort(key=lambda r:(r['name'].casefold(),r['id']))
    dump(OUT/'index.json',index)
    manifest={'schemaVersion':1,'importedAt':DATE,'profileCount':len(records),'sources':list(SOURCES.values()),
              'fields':{k:{'label':v[0],'unit':v[1]} for k,v in NUTRIENTS.items()},'methods':methods,
              'sourceCounts':dict(Counter(r['sourceId'] for r in records)),
              'categoryCounts':dict(Counter(r['category'] for r in records)),
              'indexUrl':'/data/food-library/index.json','recordRoot':'/data/food-library/records/',
              'basis':'Values per 100 g edible food; household measures are source-specific gram conversions.',
              'searchDuplicatePolicy':'Different source profiles retained; search collapses identical descriptions unless requested.',
              'libraryVersion':hash_value([(r['id'],r['version']) for r in records]),
              'shards':sorted(shards),'excludedProfiles':excluded}
    dump(OUT/'manifest.json',manifest)
    dump(ROOT/'tools/product_release/source-register.json',manifest['sources'])
    dump(ROOT/'docs/global-product-release-2026-10-11/food-import.json',{'profiles':len(records),'sources':manifest['sourceCounts'],'excluded':excluded,'flaggedProfiles':[r['id'] for r in records if r['flags']],'bytes':sum(p.stat().st_size for p in OUT.rglob('*.json')),'version':manifest['libraryVersion']})
    print(f'Imported {len(records)} source-defined profiles into {len(shards)} lazy-loaded shards; unknowns retained.')

if __name__=='__main__':run()
