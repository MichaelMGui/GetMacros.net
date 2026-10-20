"""Recheck the final source after the specific issues found in rendered QA."""
from pathlib import Path
import subprocess,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/botanical-release-2026-10-20'
commands=[['tools/master_completion/test_integration.py'],['tools/validate_site.py'],['tools/test_publication.py'],['tools/test_asset_stamps.py'],['tools/test_visible_workspace.py'],['tools/test_master_homepages.py'],['tools/ultimate_release/test_release.py']]
rows=[]
for args in commands:
    r=subprocess.run([sys.executable,'-X','utf8',*args],cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace')
    rows.append({'command':args,'exit':r.returncode,'output':(r.stdout+r.stderr)[-6000:]})
    (OUT/'final-static-checks.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(args[0],r.returncode,flush=True)
    if r.returncode:print(rows[-1]['output'],flush=True)
baseline=json.loads((OUT/'data-baseline.json').read_text());preservation={f:{'before':digest,'after':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f,digest in baseline.items()}
(OUT/'data-preservation.json').write_text(json.dumps(preservation,indent=2)+'\n')
assert all(row['before']==row['after'] for row in preservation.values()),'Source data, calculations or storage changed'
results=json.loads((OUT/'tests.json').read_text())
for replacement in rows:
    for old in results:
        if old['command']==replacement['command']:
            if old['exit']:old['originalFailureEvidence']='tests-before-directory-name-fix.json'
            old.update(replacement);old['evidence']='final-static-checks.json'
(OUT/'tests.json').write_text(json.dumps(results,indent=2)+'\n')
failed=[r['command'] for r in rows+results if r['exit']]
print(json.dumps({'CIgroups':len(results),'finalScopedGroups':len(rows),'unchangedDataFormulaAndStorageFiles':len(preservation),'failed':failed}));sys.exit(bool(failed))
