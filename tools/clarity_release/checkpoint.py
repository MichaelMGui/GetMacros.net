from pathlib import Path
import csv,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'docs/master-release-2026-10-12/publisher';OUT=ROOT/'docs/clarity-release-2026-10-14'
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=P,text=True).strip()
hashes={p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for folder in ['js','css'] for p in (P/folder).glob('*') if p.is_file()}
hashes.update({p.relative_to(P).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest() for p in P.glob('*.html')})
record={'date':'2026-10-14','publishedRevision':revision,'checkpoint':'Existing isolated publisher Git history preserves all prior production files. Root working tree is not reset or staged.','hashes':hashes,'rootBranch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'inheritedRootChanges':len(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines()),'scope':'Preserve unrelated work, server/private, source archives, music-platform and inherited publisher untracked files.'}
(OUT/'baseline.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Reversible production checkpoint',revision)
