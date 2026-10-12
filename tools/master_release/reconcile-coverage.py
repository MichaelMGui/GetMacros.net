"""Reconcile automatic render evidence without claiming every page was viewed."""
from pathlib import Path
import csv,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/master-release-2026-10-12'
render=json.loads((OUT/'route-renders.json').read_text());assert not render['failures']
routes=sorted({r['route'] for r in render['renders']})
manual={'/','/ca/en/','/mx/en/','/gb/en/','/au/en/','/jp/en/','/food-diary.html','/food-library.html','/calculators.html','/ca/en/restaurants/','/ca/en/restaurants/subway/','/ca/en/restaurants/pizza-nova/','/search.html','/play.html','/play-market-memory.html','/play-fruit-catch.html','/play-plate-art.html','/play-garden-glide.html'}
rows=[]
for route in routes:
    family='homepage' if route=='/' or re.fullmatch(r'/[a-z]{2}/en/',route) else 'game' if '/play' in route else 'finder' if 'find-a-meal' in route or 'meal-finder' in route else 'diary' if 'food-diary' in route else 'food-library' if 'food-library' in route else 'calculator' if 'calculator' in route or 'scaler' in route else 'restaurant' if '/restaurants/' in route or 'nutrition-guide' in route or 'healthy-meals-macros' in route else 'editorial/support'
    path=ROOT/('index.html' if route=='/' else route.lstrip('/')+'index.html' if route.endswith('/') else route.lstrip('/'))
    html=path.read_text(encoding='utf-8')
    issues=[]
    if 'pizza-nova' in route:issues.append('Calories only; other macros and signature-pizza denominator unresolved; excluded from macro finder')
    if 'food-library' in route or 'food-diary' in route:issues.append('Canadian branded coverage limited to four reviewed labels; no live AI, account sync or reviewed French interface')
    if family=='restaurant':issues.append('Tracked source selection, not full-menu or live local availability audit')
    rows.append({'route':route,'template':family,'visual_status':'Representative screenshots manually inspected' if route in manual else 'Automated render checks; not manually visually inspected','copy_status':'Concise new task/country copy reviewed' if family in {'homepage','diary','food-library'} or '/ca/en/restaurants/' in route or 'how-to-log-food' in route else 'Retained sourced copy; automated repetition/internal-language audit','SEO_status':'Canonical, heading, metadata and internal links checked; noindex intentional' if 'noindex' in html else 'Canonical, heading, metadata/internal links checked; genuine equivalents only','responsive_status':'Rendered at 390 and 1280 in both themes; family/outlier checks also 320/768/1440','interaction_status':'Family/source journey tests; see specific reports' if family in {'homepage','diary','food-library','calculator','finder','game'} or route=='/search.html' else 'Links/disclosures rendered; not every source link manually followed','verification_performed':'HTTP fixture render, heading/theme/CSS/error/overflow checks; static link and metadata checks','remaining_issues':'; '.join(issues)})
with (OUT/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print('Reconciled',len(rows),'routes; manual evidence distinguished from automatic-only entries.')
