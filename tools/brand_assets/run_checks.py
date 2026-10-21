"""Relevant regression checks; results belong only to this release run."""
from pathlib import Path
import subprocess,json,sys,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/brand-assets-2026-10-21'
tests=['tools/brand_assets/test.cjs','tools/diary_reference/test_goals.cjs','tools/product_release/test-food.cjs','tools/test_macro_math.js','tools/flagship_release/test_finder_payload.py','tools/test-meal-view.cjs','tools/test-edition-finder.cjs','tools/test-botanical-finder.cjs','tools/test_asset_stamps.py','tools/test_master_homepages.py','tools/master_release/test-branded-search.cjs','tools/master_release/test-diary-meals.cjs','tools/test_publication.py','tools/validate_site.py']
results=[]
for test in tests:
    if not (ROOT/test).is_file():raise RuntimeError('Unknown check '+test)
    cmd=([sys.executable,'-X','utf8'] if test.endswith('.py') else ['node','--test'] if test in ['tools/brand_assets/test.cjs','tools/diary_reference/test_goals.cjs'] else ['node'])+[test]
    start=time.perf_counter();r=subprocess.run(cmd,cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace');results.append({'test':test,'exit':r.returncode,'seconds':round(time.perf_counter()-start,2),'output':(r.stdout+r.stderr)[-6500:]})
    print(test,r.returncode,flush=True)
    (OUT/'tests.json').write_text(json.dumps(results,indent=2)+'\n')
    if r.returncode:print(results[-1]['output'],flush=True)
sys.exit(any(r['exit'] for r in results))
