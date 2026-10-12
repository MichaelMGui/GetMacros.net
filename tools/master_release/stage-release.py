"""Stage only reviewed release paths in the isolated publisher."""
from pathlib import Path
import hashlib,json,subprocess,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/master-release-2026-10-12';DEST=OUT/'publisher'
assert DEST.resolve().is_relative_to(ROOT/'docs') and (DEST/'.git').is_dir()
baseline=json.loads((OUT/'baseline.json').read_text())['hashes']
original=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=DEST,text=True).splitlines())
staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=DEST,text=True).splitlines()
removed=[]
for name in staged:
    if name.startswith('assets/generated/') and re.fullmatch(r'[A-Za-z0-9._-]+-[a-f0-9]{12}\.(css|js|json)',Path(name).name) and not (ROOT/name).exists():
        target=(DEST/name).resolve()
        assert target.is_relative_to((DEST/'assets/generated').resolve()) and target.is_file()
        subprocess.run(['git','rm','--cached','--',name],cwd=DEST,check=True,stdout=subprocess.DEVNULL)
        target.unlink()
        removed.append(name)
        continue
    if name in baseline and name not in original and hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==baseline[name]:
        target=(DEST/name).resolve()
        assert target.is_relative_to(DEST.resolve()) and target.is_file()
        subprocess.run(['git','rm','--cached','--',name],cwd=DEST,check=True,stdout=subprocess.DEVNULL)
        target.unlink()
        removed.append(name)
rows=json.loads((OUT/'stage-paths.json').read_text())
rows+=subprocess.check_output(['git','diff','--name-only'],cwd=DEST,text=True).splitlines()
rows+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=DEST,text=True).splitlines()
rows=sorted(set(rows))
assert all(not name.startswith(('music-platform/','server/private/')) and '/sources/' not in name for name in rows)
for i in range(0,len(rows),40):
    subprocess.run(['git','-c','core.safecrlf=false','add','--']+rows[i:i+40],cwd=DEST,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('Staged',len(rows),'new/updated paths; omitted',len(removed),'inherited helpers or obsolete generated assets.')
