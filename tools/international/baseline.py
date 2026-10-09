"""Checkpoint actual active files without resetting the protected original tree."""
from pathlib import Path
import hashlib,json,tarfile,subprocess
R=Path(__file__).resolve().parents[2];O=R/'docs/international-release-2026-10-09';O.mkdir(exist_ok=True)
files=list(R.glob('*.html'))+list(R.glob('*.xml'))+[R/'_config.yml',R/'CNAME']
for folder in ('css','js','images','fonts','tools','.github'):
 files += [p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in str(p) and p.suffix.lower() in ('.css','.js','.cjs','.mjs','.json','.py','.inc','.svg','.woff2','.txt','.sh','.yml')]
files=sorted(set(files))
manifest=[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
with tarfile.open(O/'baseline-active-files.tar.gz','w:gz') as tar:
 for p in files:tar.add(p,arcname=p.relative_to(R).as_posix())
status=subprocess.run(['git','status','--porcelain'],cwd=R,capture_output=True,text=True,check=True).stdout
(O/'baseline.json').write_text(json.dumps({'publishedRevision':'64aefd0eb2af9fb38a5b99e58ea533c52b061f0e','files':manifest,'workingTreeStatus':status,'checkpoint':'baseline-active-files.tar.gz','instructions':'No AGENTS.md was found in the repository or ancestor directories. Original dirty work is preserved.'},indent=2),encoding='utf-8')
print('Saved actual active baseline:',len(files),'files; original working tree unchanged')
