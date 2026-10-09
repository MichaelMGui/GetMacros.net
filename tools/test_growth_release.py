"""Guard reviewed content integration against data drift and duplicate output."""
from pathlib import Path
from urllib.parse import parse_qs,urlparse
import json,sys,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_meal_finder import parse_meals
from meal_provenance import read
payload=json.loads((ROOT/'tools/growth_release/editorial-improvements.json').read_text(encoding='utf-8'))
provenance=read(ROOT/'js/meal-provenance.js')
meals={m['chain']+'||'+m['name']:{**m,**provenance.get(m['chain']+'||'+m['name'],{})} for m in parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))}
checked=0
sitemap=ET.fromstring((ROOT/'sitemap.xml').read_text(encoding='utf-8'));ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
dates={n.find('s:loc',ns).text:n.find('s:lastmod',ns).text for n in sitemap.findall('s:url',ns)}
for row in payload['improvements']:
 assert row['status']=='checked' and row['route'].endswith('.html')
 text=(ROOT/row['route']).read_text(encoding='utf-8')
 assert text.count('growth:editorial:start')==1 and text.count('id="growth-'+row['route'].removesuffix('.html')+'"')==1,row['route']
 assert row['heading'] in text,row['route']
 for expected in row['checks']['sourceRecordAssertions']:
  m=meals[expected['chain']+'||'+expected['name']]
  for key,value in expected.items():assert m.get(key)==value,(row['route'],key,m.get(key),value)
  checked+=1
 assert parse_qs(urlparse(row['comparatorHref']).query)['compare']==row['comparedKeys']
 assert all(key in meals for key in row['comparedKeys'])
 assert 'complete-order-builder.html' not in row['sectionHTML']
 assert dates['https://getmacros.net/'+row['route']]=='2026-10-09',row['route']
 if row.get('removeLegacyComparisonSelector'):assert 'chain-picks-section' not in text,row['route']
 if row.get('directoryCorrection'):
  assert len(row['directoryCorrection']['entries'])==25 and 'Browse all 25 restaurants' in text
  assert sum(r['recordCount'] for r in row['directoryCorrection']['entries'])==len(meals)
assert len(payload['improvements'])==20
for route in ('compare-complete-restaurant-orders.html','breakfast-drinks-and-add-ons.html','food-shelf.html','protein-value-calculator.html','restaurant-meal-finder.html'):
 text=(ROOT/route).read_text(encoding='utf-8');assert text.index('js/order-tools-core.js')<text.index('js/protein-value.js' if route.startswith('protein-value') else 'js/order-notebook.js'),route
print(f'PASS 20 substantive integrations, {checked} exact record checks, comparator IDs, source dates, 25-chain directory and dependency ordering.')
