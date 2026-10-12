"""Read-only checkpoint and route inventory before the master release."""
from pathlib import Path
import csv, hashlib, json, re, subprocess, zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/master-release-2026-10-12'
OUT.mkdir(parents=True, exist_ok=True)
routes = []
files = list(ROOT.glob('*.html'))
for market in ['ca','mx','gb','ie','au','nz','jp']:
    files.extend((ROOT / market / 'en').rglob('index.html'))
for p in sorted(files):
    text = p.read_text(encoding='utf-8')
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', text)
    if not canonical and p.name != '404.html':
        continue
    relative = p.relative_to(ROOT).as_posix()
    route = '/' if relative == 'index.html' else '/' + relative.removesuffix('index.html') if relative.endswith('/index.html') else '/' + relative
    family = 'homepage' if route == '/' or re.fullmatch(r'/[a-z]{2}/en/',route) else 'game' if 'play-' in route else 'finder' if 'find-a-meal' in route or 'meal-finder' in route else 'diary' if 'food-diary' in route else 'food-library' if 'food-library' in route else 'calculator' if 'calculator' in route or 'scaler' in route else 'restaurant' if '/restaurants/' in route or 'nutrition-guide' in route or 'healthy-meals-macros' in route else 'editorial/support'
    routes.append({'route':route,'template':family,'current_visual_problems':'Pending actual render review','required_changes':'Shared interface, geometry and concise copy review','localization_status':relative[:2].upper() if '/en/' in relative else 'US/global','data_source_status':'Preserve existing source snapshots; additional imports separately recorded','content_SEO_status':'Baseline canonical present' if canonical else 'Noindex error document','functional_testing':'Not rerun yet','mobile_testing':'Not rerun yet','visual_verification':'Not yet inspected this release','remaining_blockers':''})
with (OUT/'coverage.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(routes[0]));w.writeheader();w.writerows(routes)
public = files + list((ROOT/'js').glob('*')) + list((ROOT/'css').glob('*')) + list((ROOT/'tools').glob('*.py')) + [ROOT/'tools/build_site.sh', ROOT/'sw.js', ROOT/'site.webmanifest']
hashes = {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in public if p.is_file()}
with zipfile.ZipFile(OUT/'baseline-source.zip','w',zipfile.ZIP_DEFLATED) as z:
    for relative in hashes: z.write(ROOT/relative,relative)
record={'capturedAt':'2026-10-12','rootHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'publicRoutes':len(routes),'hashes':hashes,'note':'Root dirty working tree preserved. Snapshot excludes private credentials, .git and unrelated music-platform. Prior live implementation revision 93e873b.'}
(OUT/'baseline.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Checkpoint and inventory:', len(routes), 'routes;',len(hashes),'files')
