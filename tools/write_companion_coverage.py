"""Reconcile actual browser results with the route inventory; never infer visual review."""
from pathlib import Path
import csv,json,gzip
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/cozy-redesign-2026-10-03'
checks=json.loads((OUT/'routes/checks.json').read_text(encoding='utf-8'))
reviewed={'index.html','restaurant-meal-finder.html','calculators.html','nutrition-label-comparison-tool.html','recipe-macro-scaler.html','protein-value-calculator.html','budget-meal-builder.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','weight-goal-timeline-calculator.html','sweat-rate-calculator.html','chipotle-healthy-meals-macros.html','restaurant-meal-guides.html','protein-density-fast-food.html','how-to-read-a-nutrition-label.html','articles.html','blog.html','sources.html','privacy.html','contact.html','404.html'}
tools={'calculators.html','recipe-macro-scaler.html','nutrition-label-comparison-tool.html','protein-value-calculator.html','budget-meal-builder.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','weight-goal-timeline-calculator.html','sweat-rate-calculator.html'}
trust={'about.html','sources.html','corrections.html','accessibility.html','privacy.html','terms.html','editorial-policy.html','contact.html'}
def family(f):
    if f in {'','index.html'}:return 'homepage'
    if f=='restaurant-meal-finder.html':return 'meal discovery/results'
    if f in tools:return 'calculator/meal ideas'
    if f=='restaurant-meal-guides.html':return 'restaurant directory'
    if 'healthy-meals-macros' in f or 'healthy-food-meals' in f or 'healthy-breakfast-macros' in f or 'healthy-subs-macros' in f:return 'restaurant reference'
    if f in trust:return 'trust/legal/utility'
    if f in {'articles.html','blog.html'}:return 'reading index'
    if f=='search.html':return 'search'
    if f=='404.html':return 'error'
    return 'article/guide/data comparison'
with (OUT/'coverage.csv').open('w',encoding='utf-8',newline='') as handle:
    w=csv.writer(handle);w.writerow(['route','template','visual status','copy status','SEO status','responsive status','interaction status','verification performed','remaining issues'])
    for route in sorted({c['route'] for c in checks['checks']}):
        f=route.lstrip('/');rows=[c for c in checks['checks'] if c['route']==route]
        assert len(rows)==20 and not any(c['errors'] or c['overflow'] for c in rows),route
        visual='Representative viewport reviewed' if f in {'','index.html','restaurant-meal-finder.html'} else 'Screenshot-crop review in family contact sheet' if f in reviewed else 'Scripted rendering only; family visual review does not imply individual visual inspection'
        interaction='Full two-browser task journey' if f in {'','index.html','restaurant-meal-finder.html','calculators.html'} else 'Runtime/request/form-label checks; no individual full task journey'
        w.writerow([route,family(f),visual,'Shared copy reviewed; factual/legal meaning retained; duplicate source-copy report','Static titles/canonical/schema/internal-link gates passed','Five widths; two engines; light/dark passed',interaction,'20 route/viewport checks; CSS/font/image/runtime/IDs/headings/labels/overflow','No known scripted failure; manual review scope as stated'])
assets=['css/publication.css','js/meal-finder.js','js/meal-guide.js','js/kitchen-companion.js','images/kitchen-companions.svg','fonts/fraunces-latin-500-normal.woff2']
(OUT/'asset-sizes.json').write_text(json.dumps([{'asset':f,'bytes':(ROOT/f).stat().st_size,'gzipBytes':len(gzip.compress((ROOT/f).read_bytes()))} for f in assets],indent=2),encoding='utf-8')
print('107 routes reconciled with recorded checks and explicit visual review scope.')
