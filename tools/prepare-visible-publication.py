"""Publish only the reviewed workspace changes through the established checkout."""
from pathlib import Path
import json,re,shutil,subprocess,difflib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/visible-pass-2026-10-17'
DEST=ROOT/'docs/master-release-2026-10-12/publisher'
BASE='e1eeee003a5e440ac0a6f456bba5b7d0033693a5'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=DEST,text=True).strip()==BASE
assert subprocess.check_output(['git','remote','get-url','origin'],cwd=DEST,text=True).strip()=='https://github.com/MichaelMGui/GetMacros.net.git'
assert not subprocess.check_output(['git','diff','--name-only'],cwd=DEST,text=True).strip(),'Unstaged publisher work must be preserved.'
manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
owned=['tools/build_visible_workspace.py','tools/home-workspace.css','tools/food-design.css','tools/playful-system.css','tools/build_edition_css.py','tools/build_clarity_release.py','tools/run_food_build.py','tools/build_site.sh','tools/test_visible_workspace.py','tools/test_publication.py','tools/visible-pass-qa.cjs','tools/visible-pass-journeys.cjs','tools/verify-visible-live.cjs','tools/visible-clean-check.py','tools/prepare-visible-publication.py','js/food-app.js','css/food-app.css','css/publication.css','css/home-workspace.css','sw.js','assets/generated/manifest.json']
pages=list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html'))
def normalized(text):
    def logical(m):
        tag=m[0];source=re.search(r'data-source-path="([^"]+)"',tag)
        if source:tag=re.sub(r'\b(href|src)="[^"]+"',lambda n:n[1]+'="/'+source[1]+'"',tag,count=1)
        return tag
    return re.sub(r'<(?:link|script)\b[^>]*>',logical,text).replace('\r\n','\n')
for p in pages:
    name=p.relative_to(ROOT).as_posix();before=(DEST/name).read_text(encoding='utf-8');after=p.read_text(encoding='utf-8')
    if name not in ['index.html','food-diary.html','search.html'] and not re.fullmatch(r'(ca|mx|gb|ie|au|nz|jp)/en/index.html',name):
        assert normalized(before)==normalized(after),'Unexpected public page content change: '+name
paths={p.relative_to(ROOT).as_posix() for p in pages}|set(owned)|set(manifest)|{v['url'].lstrip('/') for v in manifest.values()}
paths.update(p.relative_to(ROOT).as_posix() for p in OUT.glob('*') if p.suffix in ['.json','.md'] and p.name not in ['publication.json'])
changed=[]
for name in sorted(paths):
    p=ROOT/name;target=DEST/name
    assert p.is_file(),name
    data=p.read_bytes();previous=target.read_bytes() if target.exists() else None
    if previous is not None and data.replace(b'\r\n',b'\n')==previous.replace(b'\r\n',b'\n'):continue
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);changed.append(name)
# Remove only this asset generator's stale content-addressed outputs.
asset_dir=DEST/'assets/generated'
for p in asset_dir.iterdir():
    if p.is_file() and re.fullmatch(r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',p.name) and not (ROOT/'assets/generated'/p.name).exists():
        assert p.resolve().is_relative_to(asset_dir.resolve());p.unlink();changed.append(p.relative_to(DEST).as_posix())
for offset in range(0,len(changed),50):subprocess.run(['git','-c','core.safecrlf=false','-c','gc.auto=0','add','--',*changed[offset:offset+50]],cwd=DEST,check=True,capture_output=True)
actual=subprocess.check_output(['git','diff','--cached','--name-only','--no-renames'],cwd=DEST,text=True).splitlines()
assert all(name in paths or (name.startswith('assets/generated/') and not (ROOT/name).exists()) for name in actual),'Unrelated staged work must be preserved.'
worker=(DEST/'sw.js').read_text(encoding='utf-8');assets=json.loads(re.search(r'const APP_ASSETS=(\[.*?\]);',worker)[1]);assert all((DEST/name.lstrip('/')).is_file() for name in assets)
report={'base':BASE,'files':actual,'count':len(actual),'scope':'Eight market homepage compositions, private diary workspace, their sources and immutable asset references. Other page content preserved.'}
(OUT/'publication.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'staged':len(actual),'base':BASE,'offlineAssets':len(assets)}))
