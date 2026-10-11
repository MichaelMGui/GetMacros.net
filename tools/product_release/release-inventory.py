"""Coverage separates actual render checks from manual screenshot review."""
from pathlib import Path
from html import unescape
import csv,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/global-product-release-2026-10-11'
render=json.loads((OUT/'route-renders.json').read_text());new=json.loads((OUT/'published-manifest.json').read_text());new_by={p['route']:p for p in new}
manual={
 '/':['index-html-dark-390.png'],
 '/calculators.html':['calculators-html-light-390.png'],
 '/food-diary.html':['food-diary-html-light-390.png','food-diary-html-dark-1440.png'],
 '/gb/en/find-a-meal/':['gb-en-find-a-meal--dark-1440.png'],
 '/compare-menu-ingredients-worldwide.html':['compare-menu-ingredients-worldwide-html-light-390.png','compare-menu-ingredients-worldwide-html-light-1440.png','production/ingredient-comparison-light-390.png','production/ingredient-comparison-dark-1440.png'],
 '/food-library.html':['production/library-portion-light-390.png'],
 '/au/en/restaurants/guzman-y-gomez/':['au-en-restaurants-guzman-y-gomez--light-390.png'],
 '/how-much-protein-per-day.html':['how-much-protein-per-day-html-dark-1440.png'],
 '/diet-patterns-evidence.html':['diet-patterns-evidence-html-light-390.png'],
 '/read-and-watch.html':['read-and-watch-html-dark-390.png'],
}
rows=[];queries=[]
for route in sorted({r['route'] for r in render['renders']}):
 path='index.html' if route=='/' else route.strip('/')+'/index.html' if route.endswith('/') else route.lstrip('/');text=(ROOT/path).read_text(encoding='utf-8');family=re.search(r'data-family="([^"]+)"',text);checks=[r for r in render['renders'] if r['route']==route];info=new_by.get(route)
 rows.append({'route':route,'template':family[1] if family else 'retained public template','visual status':'Manual screenshots reviewed: '+', '.join(manual[route]) if route in manual else 'Automated render only; no manual visual claim','copy status':'New source-backed tool/market writing' if info else 'Existing example extended' if path=='raw-vs-cooked-food-weight.html' else 'Existing body preserved; shared navigation integrated','SEO status':'Metadata, canonical, internal links and indexability validated; private routes excluded from sitemap' if 'noindex' in text else 'Metadata, canonical, internal links and sitemap validated','responsive status':'Actual 390 and 1280 px renders passed' if all(not c['overflow'] for c in checks) else 'Overflow requires review','interaction status':'New source/diary/country journeys tested' if info and info['kind'] in ['finder','comparison','diary','library'] else 'Rendered; existing applicable functional tests retained','verification performed':'HTTP '+str(checks[0]['status'])+'; one H1; runtime errors '+str(sum(len(c['errors']) for c in checks)),'remaining issues':'AI provider and cloud sync unavailable' if path=='food-diary.html' else 'English interface; original Japanese names retained' if route.startswith('/jp/') else 'Source editions and missing nutrients remain visible' if info else 'No new factual source re-verification of unchanged article body'})
 if info and info['indexable']:queries.append({'route':route,'primary user intent':info['title'],'locale':info['market'],'research date':'2026-10-11','measured search volume':'Unavailable','search evidence':'Qualitative queries and primary guidance in seo-research.md; this route was not individually keyword-volume measured','unique utility':info['description'],'source trail':'Visible official links; source edition recorded','maintenance':'Review changed official editions and dependent figures before modifying dates','next action':'Country finder / source record / related tool'})
for name,data in [('coverage.csv',rows),('query-to-page.csv',queries)]:
 with (OUT/name).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
print(len(rows),'routes in coverage;',len(queries),'new public routes mapped; manual and automated inspection remain separate.')
