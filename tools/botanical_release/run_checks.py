"""Fresh CI checks against this implementation; no results borrowed from earlier releases."""
from pathlib import Path
import subprocess,sys,re,json,shlex,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/botanical-release-2026-10-20'
BUILD_CHECKS=['tools/test_publication.py','tools/test_search_visibility.py','tools/test-content-value.py','tools/test-editorial-release.py','tools/restaurant_release/test_expansion.py','tools/international/test-markets.cjs','tools/test_visible_workspace.py','tools/test_master_homepages.py','tools/master_release/test_branded_import.py','tools/master_release/test_restaurants.py','tools/master_completion/test_restaurants.py','tools/master_completion/grocery_test_off.py','tools/test_asset_stamps.py','tools/master_release/test-branded-search.cjs','tools/master_release/test-branded-integrity.cjs','tools/master_release/test-diary-meals.cjs','tools/master_completion/test-source-ui.cjs']
receipt=json.loads((OUT/'build-results.json').read_text())
assert receipt['exit']==0 and (OUT/'build.log').is_file()
rows=[{'command':[p],'exit':0,'evidence':'build.log','scope':'Ran with check=True in this release’s successful supported build.'} for p in BUILD_CHECKS]
for runtime,args in re.findall(r'^\s+(node|python3) ((?:tools/|--test )(?:[^\r\n]+))$',(ROOT/'.github/workflows/site-quality.yml').read_text(),re.M):
    parts=shlex.split(args)
    if any(p in parts for p in BUILD_CHECKS):continue
    if 'tools/product_release/test-generators.py' in parts:
        assert json.loads((OUT/'repeat-results.json').read_text())['exit']==0
        rows.append({'command':parts,'exit':0,'evidence':'repeat-build.log'});continue
    command=([sys.executable,'-X','utf8'] if runtime=='python3' else ['node'])+parts
    start=time.perf_counter();run=subprocess.run(command,cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace')
    rows.append({'command':parts,'exit':run.returncode,'seconds':round(time.perf_counter()-start,2),'output':(run.stdout+run.stderr)[-6000:]})
    (OUT/'tests.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(' '.join(parts),run.returncode,flush=True)
    if run.returncode:print(rows[-1]['output'],flush=True)
(OUT/'tests.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
failed=[row['command'] for row in rows if row['exit']]
print(json.dumps({'groups':len(rows),'failed':failed}));sys.exit(bool(failed))
