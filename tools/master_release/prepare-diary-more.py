"""Publish only this diary task and its regenerated public assets in the approved checkout."""
from pathlib import Path
import json,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/master-release-2026-10-12/publisher'
OUT=ROOT/'docs/diary-more-2026-10-12'
assert DEST.resolve().is_relative_to(ROOT/'docs') and (DEST/'.git').is_dir()
assert subprocess.check_output(['git','remote','get-url','origin'],cwd=DEST,text=True).strip()=='https://github.com/MichaelMGui/GetMacros.net.git'
owned=['css/food-app.css','js/food-app.js','js/food-library.js','js/diary-edit.js','js/food-diary-store.js','js/diary-actions.js','sw.js',
       'tools/build_master_diary.py','tools/build_diary_catalogue.py','tools/stamp_assets.py',
       'tools/build_site.sh','tools/run_food_build.py','.github/workflows/site-quality.yml',
       'tools/master_release/test-diary-meals.cjs','tools/master_release/check-diary-meals.cjs',
       'tools/master_release/test-diary-upgrade.cjs','tools/master_release/prepare-diary-more.py','tools/master_release/check-diary-more.cjs','tools/master_release/verify-diary-live.cjs']
routes=set(r['route'] for r in json.loads((ROOT/'docs/master-release-2026-10-12/route-renders.json').read_text())['renders'])
pages=[ROOT/('index.html' if r=='/' else r.strip('/')+'/index.html' if r.endswith('/') else r.lstrip('/')) for r in routes]
candidates=[ROOT/p for p in owned]+pages+list((ROOT/'assets/generated').glob('*'))+list((ROOT/'data/food-library').glob('diary-foods-*.json'))
candidates += [p for p in OUT.rglob('*') if p.is_file() and p.suffix in ['.md','.json','.csv'] and p.name not in ['baseline.json','stage-paths.json','publication-files.json','deployment-verification.json']]
changed=[]
for p in sorted(set(candidates)):
    assert p.resolve().is_relative_to(ROOT)
    if not p.is_file():continue
    name=p.relative_to(ROOT).as_posix();data=p.read_bytes();target=DEST/name
    if target.exists() and target.read_bytes().replace(b'\r\n',b'\n')==data.replace(b'\r\n',b'\n'):continue
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);changed.append(name)
# Check deletion targets are within fixed, generator-owned directories before removal.
for folder,pattern in [('assets/generated',r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)'),('data/food-library',r'diary-foods-[a-f0-9]{12}\.json')]:
    base=DEST/folder
    for p in base.iterdir():
        assert p.resolve().is_relative_to(base.resolve())
        if p.is_file() and re.fullmatch(pattern,p.name) and not (ROOT/folder/p.name).exists():p.unlink();changed.append(p.relative_to(DEST).as_posix())
for name in ['js/order-registry.json','data/food-library/index.json','data/food-library/manifest.json']:
    assert (ROOT/name).read_bytes().replace(b'\r\n',b'\n')==(DEST/name).read_bytes().replace(b'\r\n',b'\n'),name+' source data unexpectedly changed'
allowed={p.relative_to(ROOT).as_posix() for p in candidates}
pending=[]
for entry in subprocess.check_output(['git','status','--porcelain','--untracked-files=all','-z'],cwd=DEST,text=True).split('\0'):
    if not entry:continue
    name=entry[3:]
    obsolete=re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)|data/food-library/diary-foods-[a-f0-9]{12}\.json',name)
    if name in allowed or obsolete:pending.append(name)
(OUT/'stage-paths.json').write_text(json.dumps(sorted(set(pending)),indent=2),encoding='utf-8')
summary={'previousRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=DEST,text=True).strip(),
         'changedFiles':len(set(changed)),'paths':sorted(set(changed)),'scope':'Expanded shared source browsing, preparation choices, native day navigation, reviewed meal repeats and bounded date lookups; nutrition source records unchanged.'}
(OUT/'publication-files.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'changedFiles':summary['changedFiles'],'htmlPages':sum(p.endswith('.html') for p in changed),'previousRevision':summary['previousRevision']}))
