"""Sync this task's changed source files into the existing approved isolated checkout.

No protected root Git operations; unrelated inherited files and raw source evidence
are not staged. Production is still published by the existing Git workflow.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/global-product-release-2026-10-11';DEST=OUT/'publisher-local'
assert DEST.resolve().is_relative_to(ROOT/'docs') and (DEST/'.git').is_dir()
remote=subprocess.check_output(['git','remote','get-url','origin'],cwd=DEST,text=True).strip();assert remote=='https://github.com/MichaelMGui/GetMacros.net.git'
baseline={r['path']:r['sha256'] for r in json.loads((OUT/'baseline-files.json').read_text())['files']}
candidates=[p for p in ROOT.iterdir() if p.is_file() and (p.suffix in ['.html','.js','.json','.svg','.xml','.yml','.txt'] or p.name in ['.gitignore','CNAME','.nojekyll'])]
for directory in ['css','js','images','fonts','tools','.github','ca','mx','gb','ie','au','nz','jp','data/food-library','server']:
 candidates.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and not set(p.parts)&{'__pycache__','node_modules','private','.git'} and not (p.name.startswith('.env') and p.name!='.env.example'))
candidates.extend(p for p in OUT.iterdir() if p.is_file() and p.suffix in ['.md','.json','.csv'] and not p.name.startswith('baseline-'))
candidates.extend(p for p in (OUT/'distribution').glob('*') if p.is_file())
candidates.extend(p for p in (OUT/'final').glob('*.png') if p.is_file())
changed=[]
for p in sorted(set(candidates)):
 name=p.relative_to(ROOT).as_posix();data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
 if baseline.get(name)==digest and name!='js/meal-data.js':continue
 if name=='docs/global-product-release-2026-10-11/deployment-files.json':continue
 if name.startswith('docs/global-product-release-2026-10-11/') and 'sources/' in name:continue
 target=DEST/name
 if not target.exists() or target.read_bytes().replace(b'\r\n',b'\n')!=data.replace(b'\r\n',b'\n'):
  target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 changed.append({'path':name,'bytes':len(data),'sha256':digest})
(OUT/'deployment-files.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
(DEST/'global-product-stage-paths.txt').write_text('\n'.join(r['path'] for r in changed)+'\n',encoding='utf-8')
print('Prepared',len(changed),'task-changed paths in the approved checkout. No push performed; raw snapshots, unrelated music project and private databases excluded.')
