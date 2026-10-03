"""Verify the release build is repeatable and record actual command outcomes."""
from pathlib import Path
import subprocess, sys, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/cozy-redesign-2026-10-03'
steps=['apply_audited_data.py','build_release_resources.py','rebuild_publication.py','strengthen_meal_comparisons.py','sync_restaurant_release.py','release_copy_audit.py','refresh_release_search.py','finish_release_metadata.py','stamp_assets.py']
records=[]
def run(args):
    result=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    records.append({'command':' '.join(args[1:]) if args[0]==sys.executable else ' '.join(args),'exitCode':result.returncode,'output':result.stdout+result.stderr})
    print(records[-1]['command'],result.returncode,flush=True)
    if result.returncode:
        (OUT/'build-checks.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
        raise SystemExit(result.returncode)
def snapshot():
    files=list(ROOT.glob('*.html'))+[ROOT/'css/publication.css',ROOT/'js/site-search.js',ROOT/'sitemap.xml']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.exists()}
for script in steps:
    args=[sys.executable,'-X','utf8','tools/'+script]
    if script=='release_copy_audit.py':args+=['--apply-reviewed','--output','docs/cozy-redesign-2026-10-03/copy-audit.json']
    run(args)
first=snapshot()
for script in steps:
    args=[sys.executable,'-X','utf8','tools/'+script]
    if script=='release_copy_audit.py':args+=['--apply-reviewed','--output','docs/cozy-redesign-2026-10-03/copy-audit.json']
    run(args)
assert first==snapshot(),'Rebuilding changed the generated public output'
records.append({'check':'Two full builds produce identical public HTML, stylesheet, search index and sitemap','pass':True})
for script in ['validate_site.py','test_publication.py','test_search_visibility.py','test-content-value.py','test-release-content.py']:
    run([sys.executable,'-X','utf8','tools/'+script])
for script in ['test_macro_math.js','test-companion-engine.cjs']:
    run(['node','tools/'+script])
(OUT/'build-checks.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('PASS repeatable build and all static/data/math gates')
