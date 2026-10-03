"""Reconcile the public scope with actual release and browser evidence."""
from pathlib import Path
from html import unescape
import csv,json,re
from collections import Counter
from build_release_resources import load
from site_scope import RESTAURANT_PAGES, TOOL_PAGES, KEEP_ROOT_HTML

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-2026-10-03'
resources={r['slug']:r for r in load()}
checks=json.loads((OUT/'routes/checks.json').read_text(encoding='utf-8'))
assert len(checks['checks'])==2140 and not checks['failures']
visual=json.loads((OUT/'routes/visual-inspection.json').read_text(encoding='utf-8'))['inspections']
visual+=json.loads((OUT/'parent-visual-inspection.json').read_text(encoding='utf-8'))['inspections']
files=sorted(p.name for p in ROOT.glob('*.html'))
assert set(files)==KEEP_ROOT_HTML
substantive={'healthy-fast-food.html','best-fast-food-restaurants-for-your-goals.html','are-diet-drinks-bad-for-you.html','calories-vs-macros-what-matters-more.html','does-creatine-cause-hair-loss.html','how-much-protein-can-your-body-absorb.html'}
trust={'about.html','sources.html','editorial-policy.html','corrections.html','contact.html','accessibility.html','privacy.html','terms.html'}
rows=[];intents=[]
for route in ['']+files:
    file=route or 'index.html';text=(ROOT/file).read_text(encoding='utf-8')
    plain=lambda s:re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>','',s))).strip()
    title=plain(re.search(r'<title>(.*?)</title>',text,re.S)[1])
    h1=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',text,re.S)[1])
    if file in resources:family='data resource' if resources[file].get('tableFacts') else 'worked practical guide'
    elif file in RESTAURANT_PAGES:family='restaurant guide'
    elif file in TOOL_PAGES or file=='calculators.html':family='calculator/food tool'
    elif file in trust:family='trust/legal/contact'
    elif file=='index.html':family='product homepage'
    elif file=='restaurant-meal-finder.html':family='meal finder/results'
    elif file=='search.html':family='search'
    elif file=='404.html':family='error'
    elif file in {'articles.html','blog.html','restaurant-meal-guides.html'}:family='directory/editorial index'
    else:family='retained editorial article'
    public='/'+route
    scripted=[c for c in checks['checks'] if c['route']==public]
    assert len(scripted)==20,public
    humans=[v for v in visual if v['route']==public]
    inspection='; '.join(sorted({str(v.get('width',''))+'px '+v.get('theme','')+' '+v.get('region','') for v in humans})) if humans else 'Scripted renders only; not individually human inspected'
    new=resources.get(file)
    content='New original resource with distinct recorded utility' if new else 'Restaurant portions, tables and decision copy synchronized' if file in RESTAURANT_PAGES else 'Targeted editorial/data improvement' if file in substantive else 'Existing factual body retained; shared copy/duplicate audit'
    source='Official source inspection or explicitly illustrative arithmetic; see content/source manifests' if new else 'Per-record dates and limits; eight chains partly refreshed, others retained' if file in RESTAURANT_PAGES else 'Existing citations/disclosures retained; no automatic review-date refresh'
    functional='Guide/browse/filter/save/three-meal compare/share/print journeys tested' if file in {'index.html','restaurant-meal-finder.html'} else 'Six meal ideas, category/ingredient selections, expanded details and no-JS content tested' if file=='budget-meal-builder.html' else 'Examples and recalculation tested; invalid-input recovery where supported; unit changes where available' if file in TOOL_PAGES or file=='calculators.html' else 'Search matches/no-match tested' if file=='search.html' else 'All local links/anchors and render runtime checked; shared menu/theme journeys tested'
    blockers='No known implementation blocker. Source/access limits documented; no full medical or screen-reader review.'
    if new and file in {'fast-food-nutrition-data-report.html','chipotle-vs-cava-chicken-bowls.html'}:blockers+=' CAVA freshness unresolved; Starbucks indexed-source access limitation.'
    rows.append({'route':public,'template':family,'required changes':'Shared Market system, readable controls, route-specific content/data integrity','content status':content,'source status':source,'visual checks':inspection,'functional checks':functional,'verification performed':'20 scripted render checks: Chromium/WebKit × light/dark × 320/390/768/1024/1440; static metadata/link/source gates','unresolved blockers':blockers})
    intent=new['intent'] if new else h1
    value=new['originalUtility'] if new else 'Working source-backed tool and supported output' if family=='calculator/food tool' else 'Tracked portions, numerical comparisons and restaurant-specific caveats' if family=='restaurant guide' else 'Existing distinct content and relevant product navigation'
    nextAction='Find and compare meals' if family not in {'meal finder/results','product homepage'} else 'Refine, save, share or compare matching orders'
    intents.append({'route':public,'title':title,'primary user intent':intent,'unique value':value,'next action':nextAction,'evidence':'Qualitative live-query/source observations where recorded in seo-research.md; other intents derived from actual page purpose, not keyword-volume research'})
def write(name,items):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
write('release-manifest.csv',rows);write('query-to-page.csv',intents)
(OUT/'scope.json').write_text(json.dumps({'rootHTML':len(files),'publicRoutesWithRootAlias':len(rows),'newResources':len(resources),'pageFamilies':dict(Counter(r['template'] for r in rows)),'automatedViewportChecks':len(checks['checks']),'resilienceChecks':len(checks['resilience']),'humanInspectionRecords':len(visual),'humanInspectionLimit':'Regions and screens listed in visual manifests; all individual pages rendered but not all individually human inspected','excludedFromPages':'docs, tools and design directories via _config.yml; includes baseline fixtures, art gallery, screenshots and research reports'},indent=2),encoding='utf-8')
print(f'Reconciled {len(rows)} public routes, {len(resources)} new resources and 2140 scripted render checks.')
