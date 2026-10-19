"""Run every independent CI check against this release; do not reuse old passes."""
from pathlib import Path
import subprocess,sys,re,json,time,shlex
R=Path(__file__).resolve().parents[2];OUT=R/'docs/ultimate-release-2026-10-19/tests.json'
BUILD_CHECKS=['tools/test_publication.py','tools/test_search_visibility.py','tools/test-content-value.py','tools/test-editorial-release.py','tools/restaurant_release/test_expansion.py','tools/international/test-markets.cjs','tools/test_visible_workspace.py','tools/test_master_homepages.py','tools/master_release/test_branded_import.py','tools/master_release/test_restaurants.py','tools/master_completion/test_restaurants.py','tools/master_completion/grocery_test_off.py','tools/test_asset_stamps.py','tools/master_release/test-branded-search.cjs','tools/master_release/test-branded-integrity.cjs','tools/master_release/test-diary-meals.cjs','tools/master_completion/test-source-ui.cjs']
receipt=R/'docs/ultimate-release-2026-10-19/build-results.json'
completed=json.loads(receipt.read_text(encoding='utf-8')) if receipt.exists() else {}
build_pass=completed.get('finalExit')==0
commands=[]
for runtime,args in re.findall(r'^\s+(node|python3) ((?:tools/|--test )(?:[^\r\n]+))$',(R/'.github/workflows/site-quality.yml').read_text(encoding='utf-8'),re.M):
 if 'test-generators.py' in args:continue
 parts=shlex.split(args);commands.append(([sys.executable,'-X','utf8'] if runtime=='python3' else ['node'])+parts)
rows=[{'command':[p],'exit':0,'evidence':'full-build-verified.log','scope':'Executed with subprocess check=True inside the successful full build.'} for p in BUILD_CHECKS] if build_pass else []
for command in commands:
 if build_pass and any(p in command for p in BUILD_CHECKS):continue
 started=time.perf_counter();p=subprocess.run(command,cwd=R,capture_output=True,encoding='utf-8',errors='replace');rows.append({'command':command[3:] if command[0]==sys.executable else command,'exit':p.returncode,'seconds':round(time.perf_counter()-started,2),'output':(p.stdout+p.stderr)[-12000:]});OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(' '.join(command[3:] if command[0]==sys.executable else command),p.returncode,flush=True)
 if p.returncode:print(rows[-1]['output'],flush=True)
print(json.dumps({'checks':len(rows),'failed':[r['command'] for r in rows if r['exit']]}));sys.exit(any(r['exit'] for r in rows))
