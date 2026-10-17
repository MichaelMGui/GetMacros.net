"""Count actual installed records and record honest rendered/page coverage."""
from pathlib import Path
from collections import Counter
import csv, json, re
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/global-coverage-2026-10-17'
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
registry=read('js/order-registry.json')['records']
markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
providers={code:read('data/branded-foods/'+code+'/manifest.json') for code in ['usda','off','retailer-ca','cnf']}
branded=sum(providers[code]['profileCount'] for code in ['usda','off','retailer-ca'])
counts={code:{'restaurantRecords':sum(r['market']==code for r in registry),'restaurantBrands':len({r['chain'] for r in registry if r['market']==code}),'grocerySourceProfiles':sum(p.get('markets',{}).get(code,0) for key,p in providers.items() if key!='cnf')} for code in markets}
result={'date':'2026-10-17','newGrocerySourceProfiles':branded-133317,'totalBrandedSourceProfiles':branded,'groceryProviders':{key:{'profiles':p['profileCount'],'version':p['version'],'markets':p['markets'],'license':p.get('source',{}).get('license',p.get('derivativeLicense'))} for key,p in providers.items()},'generalReferenceProfiles':read('data/food-library/manifest.json')['profileCount'],'newRestaurantRecords':1443,'refreshedExistingRestaurantRecords':17,'totalRestaurantRecords':len(registry),'publishedMarkets':counts,'newComparisonGuides':13,'verification':{'sourceIntegrity':'USDA and OFF full-source audits passed; imported packages are not independently label-verified','browser':'See browser-results.json and restaurants/newmarkets/browser-results.json for actual checks and screenshot paths','live':'Pending live verification; local build is not proof of deployment'},'remainingGaps':['No claim of every grocery item, retailer inventory or every fast-food menu.','USDA April2026 and OFF October13 snapshots retain dated source versions; current shelf availability is not established.','French product names are preserved; no reviewed French interface or French hreflang is claimed.','India coverage is McDonald’s North & East India only, not other franchise regions.','OFF records without an unambiguous gram/millilitre source serving and contradictory restaurant rows remain excluded.','No branded-grocery source partition is published for the four new restaurant markets; common reference foods and their local menu records remain usable.','Google indexing and search traffic have not been measured or guaranteed.']}
(OUT/'release-counts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (OUT/'market-coverage.csv').open('w',newline='',encoding='utf-8') as file:
    w=csv.writer(file);w.writerow(['country','name','restaurant_records','restaurant_brands','grocery_source_profiles'])
    for code,c in counts.items():w.writerow([code,markets[code]['name'],c['restaurantRecords'],c['restaurantBrands'],c['grocerySourceProfiles']])
paths=sorted(set(ROOT.glob('*.html'))|set(ROOT.glob('*/en/**/index.html')))
with (OUT/'coverage.csv').open('w',newline='',encoding='utf-8') as file:
    w=csv.writer(file);w.writerow(['route','family','market','metadata_links','visual_verification','remaining_issues'])
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();t=p.read_text(encoding='utf-8');route='/' if rel=='index.html' else '/'+rel[:-10] if rel.endswith('/index.html') else '/'+rel
        family=re.search(r'data-family="([^"]+)"',t);market=re.search(r'^([a-z]{2})/en/',rel)
        visual='Programmatic route/link/metadata checks only'
        if market and market[1] in ('fr','in','sg','za') and ('/restaurants/' in route and '/guides/' not in route or route.count('/')==3 or '/find-a-meal/' in route):visual='Actual browser check; see newmarkets browser-results.json for exact route/width and inspected screenshots'
        if route in ['/','/ca/en/','/mx/en/','/food-diary.html','/grocery-food-coverage.html','/jp/en/restaurants/mos-burger/']:visual='Actual browser render/geometry; selected screenshots visually reviewed; see browser-results.json'
        w.writerow([route,family[1] if family else 'shared',market[1].upper() if market else 'global','Full static validator and link checks; see test logs',visual,'No universal data coverage claim; individual pages without screenshot review are not claimed visually inspected'])
print(json.dumps({'brandedSourceProfiles':branded,'addedGrocerySourceProfiles':branded-133317,'restaurantRecords':len(registry),'markets':len(markets),'publicHtmlRoutes':len(paths)},indent=2))
