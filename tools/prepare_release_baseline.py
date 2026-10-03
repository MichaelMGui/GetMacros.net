"""Export only baseline files needed by the repeatable local lab; never published."""
from pathlib import Path
import subprocess,re
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-2026-10-03/baseline-site'
def run():
 paths=subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT,text=True).splitlines()
 chosen={p for p in paths if ('/' not in p and p.endswith('.html')) or p.startswith(('js/','fonts/')) or p in ('css/publication.css','favicon.svg','site.webmanifest','apple-touch-icon.png')}
 for p in list(chosen):
  if not p.endswith('.html'):continue
  content=subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT).decode('utf-8')
  for ref in re.findall(r'(?:src|href)="([^"?#]+)',content):
   ref=ref.lstrip('/')
   if ref in paths and ref.startswith('images/'):chosen.add(ref)
 for p in sorted(chosen):
  dest=OUT/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(subprocess.check_output(['git','show','HEAD:'+p],cwd=ROOT))
 print('Prepared '+str(len(chosen))+' committed baseline files for local before/after diagnostics; excluded from publication.')
if __name__=='__main__':run()
