"""Open Food Facts 2026-10-13 TSV subset normalization, audited 2026-10-17.
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

DATE = '2026-10-13'
MARKETS = {'en:canada': 'CA', 'en:united-states': 'US', 'en:mexico': 'MX', 'en:united-kingdom': 'GB', 'en:ireland': 'IE', 'en:australia': 'AU', 'en:new-zealand': 'NZ', 'en:japan': 'JP'}
MAP = {'cal': ('energy-kcal_100g', 1), 'p': ('proteins_100g', 1), 'c': ('carbohydrates_100g', 1), 'fat': ('fat_100g', 1), 'f': ('fiber_100g', 1), 'na': ('sodium_100g', 1000), 'sugar': ('sugars_100g', 1), 'sat': ('saturated-fat_100g', 1), 'chol': ('cholesterol_100g', 1000), 'calcium': ('calcium_100g', 1000), 'iron': ('iron_100g', 1000), 'magnesium': ('magnesium_100g', 1000), 'phosphorus': ('phosphorus_100g', 1000), 'potassium': ('potassium_100g', 1000), 'zinc': ('zinc_100g', 1000), 'selenium': ('selenium_100g', 1000000), 'vitaminC': ('vitamin-c_100g', 1000), 'thiamin': ('vitamin-b1_100g', 1000), 'riboflavin': ('vitamin-b2_100g', 1000), 'niacin': ('vitamin-pp_100g', 1000), 'vitaminB6': ('vitamin-b6_100g', 1000), 'folate': ('folates_100g', 1000000), 'vitaminB12': ('vitamin-b12_100g', 1000000), 'vitaminD': ('vitamin-d_100g', 1000000), 'vitaminE': ('vitamin-e_100g', 1000), 'monoFat': ('monounsaturated-fat_100g', 1), 'polyFat': ('polyunsaturated-fat_100g', 1)}
previous = SimpleNamespace(base=SimpleNamespace(NUTRIENTS=['cal', 'p', 'c', 'fat', 'f', 'na', 'sugar', 'sat', 'chol', 'calcium', 'iron', 'magnesium', 'phosphorus', 'potassium', 'zinc', 'selenium', 'vitaminC', 'thiamin', 'riboflavin', 'niacin', 'vitaminB6', 'folate', 'folateDFE', 'vitaminB12', 'vitaminA', 'vitaminD', 'vitaminE', 'vitaminK', 'monoFat', 'polyFat']))
def text(value):
    value=''.join(c for c in unicodedata.normalize('NFKD',str(value)).lower() if not unicodedata.combining(c))
    return re.sub(r'[^\w]+',' ',value.replace('_',' '),flags=re.UNICODE).strip()


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
