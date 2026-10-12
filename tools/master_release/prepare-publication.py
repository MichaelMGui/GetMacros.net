"""Sync this release into a clean, isolated checkout; never touch root .git."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/master-release-2026-10-12'
DEST=OUT/'publisher'
assert DEST.resolve().is_relative_to(ROOT/'docs') and (DEST/'.git').is_dir()
assert subprocess.check_output(['git','remote','get-url','origin'],cwd=DEST,text=True).strip()=='https://github.com/MichaelMGui/GetMacros.net.git'
baseline=json.loads((OUT/'baseline.json').read_text())['hashes']
original=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=DEST,text=True).splitlines())
candidates=[ROOT/name for name in baseline if (ROOT/name).is_file()]
candidates += [p for p in ROOT.glob('*.html')]
for directory in ['ca','mx','gb','ie','au','nz','jp','data/branded-foods','assets/generated','tools/master_release']:
    candidates.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ['data/restaurant-presence.json','images/game-family-motifs.svg','tools/master-audit-css.py','tools/test_master_homepages.py','tools/test-master-interface.cjs','tools/master-calibrate-details.cjs','tools/master-calibrate-surfaces.cjs','tools/playful-system.css','tools/food-design.css','tools/play-release.css','tools/run_food_build.py','tools/test_asset_stamps.py','.github/workflows/site-quality.yml']:
    candidates.append(ROOT/name)
for name in ['sitemap.xml','site.webmanifest','robots.txt']:
    candidates.append(ROOT/name)
candidates.extend(ROOT.glob('tools/build_master_*.py'))
candidates.append(ROOT/'tools/restore_asset_sources.py')
candidates.extend(ROOT/name for name in ['tools/market-content.css','tools/food-characters.css','tools/release-product.css'])
candidates.extend(ROOT/name for name in ['tools/international/test-markets.cjs','tools/product_release/test-food.cjs','tools/product_release/test-generators.py'])
candidates.extend(ROOT/name for name in json.loads((ROOT/'assets/generated/manifest.json').read_text()))
candidates.extend(p for p in OUT.iterdir() if p.is_file() and p.suffix in ['.md','.json','.csv','.txt'] and not p.name.startswith(('baseline','deployment')))
changed=[]
for p in sorted(set(candidates)):
    if not p.is_file():continue
    name=p.relative_to(ROOT).as_posix()
    if name.startswith('docs/master-release-2026-10-12/publisher/'):continue
    if p.suffix in ['.zip','.pdf','.png','.jpg'] or p.name.startswith('.env'):continue
    data=p.read_bytes()
    if name in baseline and name not in original and hashlib.sha256(data).hexdigest()==baseline[name]:continue
    target=DEST/name
    if target.exists() and target.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):continue
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(p,target)
    changed.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'deployment-files.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
(OUT/'stage-paths.json').write_text(json.dumps([r['path'] for r in changed]),encoding='utf-8')
print('Prepared',len(changed),'release files;',sum(r['bytes'] for r in changed),'bytes. Root .git, unrelated projects, source downloads and private data untouched.')
