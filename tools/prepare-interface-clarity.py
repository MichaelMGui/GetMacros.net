"""Copy only this UI fix and its generated asset references to the publisher."""
from pathlib import Path
import hashlib, json, re, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/master-release-2026-10-12/publisher'
OUT=ROOT/'docs/interface-clarity-2026-10-18'
BASE='059dc787961348c9d1d93c09446ee5f7eb5fa732'
PROTECTED={'docs/playful-release-2026-10-04/editorial/existing-intent-review.json','docs/playful-release-2026-10-04/editorial/integration.json','tools/restaurant_release/metadata-overrides.json','tools/restaurant_release/review-records.json','tools/restaurant_release/validation-report.json'}
SOURCES=['tools/build_master_diary.py','tools/build_visible_workspace.py','tools/food-design.css','tools/release-product.css','tools/release-library.css','css/food-app.css','js/food-app.js','js/meal-guide.js','tools/master_release/check-diary-meals.cjs','tools/check-interface-clarity.cjs','tools/prepare-interface-clarity.py']
def git(*args):return subprocess.check_output(['git','-c','gc.auto=0',*args],cwd=DEST,text=True).strip()
def target(name):
    rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and '.git' not in rel.parts and name not in PROTECTED,name
    path=DEST/rel;assert path.resolve().is_relative_to(DEST.resolve()),name
    for p in [path,*path.parents]:
        assert not p.is_symlink() and not getattr(p,'is_junction',lambda:False)(),str(p)
        if p==DEST:break
    return path
def same(a,b):return b.is_file() and a.read_bytes().replace(b'\r\n',b'\n')==b.read_bytes().replace(b'\r\n',b'\n')
def normalized(text):
    text=re.sub(r'<script data-public-assets>.*?</script>','',text,flags=re.S)
    def logical(m):
        tag=m[0];source=re.search(r'data-source-path="([^"]+)"',tag)
        return re.sub(r'\b(href|src)="[^"]+"',lambda x:x[1]+'="/'+source[1]+'"',tag,count=1) if source else tag
    return re.sub(r'<(?:link|script)\b[^>]*>',logical,text).replace('\r\n','\n')
assert git('rev-parse','HEAD')==BASE
assert git('remote','get-url','origin')=='https://github.com/MichaelMGui/GetMacros.net.git'
assert not git('diff','--name-only') and not git('diff','--cached','--name-only'),'Preserve existing publisher work'
protected={name:hashlib.sha256((DEST/name).read_bytes()).hexdigest() for name in PROTECTED}
pages=list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html'))
for p in pages:
    name=p.relative_to(ROOT).as_posix()
    if name not in ['food-diary.html','food-library.html','compare-foods.html']:
        assert normalized(p.read_text(encoding='utf-8'))==normalized((DEST/name).read_text(encoding='utf-8')),'Unexpected page content change: '+name
manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
old_manifest=json.loads((DEST/'assets/generated/manifest.json').read_text(encoding='utf-8'))
paths={p.relative_to(ROOT).as_posix() for p in pages}|set(SOURCES)|set(manifest)|{v['url'].lstrip('/') for v in manifest.values()}|{'assets/generated/manifest.json','sw.js'}
paths.update(p.relative_to(ROOT).as_posix() for p in OUT.glob('*') if p.suffix in ['.json','.md'] and p.name not in ['publication.json'])
if '--check' in sys.argv:
    print(json.dumps({'base':BASE,'pageContentScopeChecked':len(pages),'candidateFiles':len(paths),'protectedUntrackedPreserved':len(protected)}))
    sys.exit(0)
changed=[]
for name in sorted(paths):
    source=ROOT/name;dest=target(name);assert source.is_file(),name
    if same(source,dest):continue
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);changed.append(name)
new_urls={v['url'] for v in manifest.values()}
for row in old_manifest.values():
    if row['url'] in new_urls:continue
    name=row['url'].lstrip('/');assert re.fullmatch(r'assets/generated/[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',name),name
    p=target(name)
    if p.is_file():p.unlink();changed.append(name)
for i in range(0,len(changed),50):git('add','--',*changed[i:i+50])
assert set(git('diff','--cached','--name-only','--no-renames').splitlines())==set(changed)
assert all(hashlib.sha256((DEST/name).read_bytes()).hexdigest()==digest for name,digest in protected.items())
report={'base':BASE,'files':changed,'count':len(changed),'scope':'Shared search/select presentation; diary picker structure and copy; open quiz choices. Nutrition records and article bodies preserved.','protectedUntrackedPreserved':len(protected)}
(OUT/'publication.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'staged':len(changed),'base':BASE,'protectedUntrackedPreserved':len(protected)}))
