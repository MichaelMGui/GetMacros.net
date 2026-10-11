"""Run the existing quality gates plus product-specific source arithmetic."""
from pathlib import Path
import json,subprocess,sys,time
root=Path(__file__).resolve().parents[2]
node=['tools/test_macro_math.js','tools/test-companion-engine.cjs','tools/test-meal-view.cjs','tools/test-growth-tools.cjs','tools/international/test-markets.cjs','tools/play_release/test-rules.cjs','tools/product_release/test-food.cjs','tools/product_release/test-image.cjs']
python=['tools/validate_site.py','tools/test_publication.py','tools/test_search_visibility.py','tools/test-content-value.py','tools/test-editorial-release.py','tools/test_growth_release.py','tools/test-release-content.py','tools/test_asset_stamps.py']
checks=[]
for command in [['node',p] for p in node]+[[sys.executable,'-X','utf8',p] for p in python]+[[sys.executable,'-X','utf8','tools/growth_release/review-source.py','--validate']]:
 start=time.time();r=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8');checks.append({'command':command,'exitCode':r.returncode,'seconds':round(time.time()-start,2),'output':r.stdout+r.stderr});print(command[-1],r.returncode,flush=True)
 if r.returncode:print(r.stdout+r.stderr)
(root/'docs/global-product-release-2026-10-11/test-results.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
sys.exit(int(any(r['exitCode'] for r in checks)))
