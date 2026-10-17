"""Recheck the complete staged build and generated public bytes after the link-order fix.

The earlier focused run already passed its four additional suites; its output
comparison found stylesheet ordering differences. No suite is removed from CI.
"""
from pathlib import Path
import os,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/visible-pass-2026-10-17';PUBLISHER=ROOT/'docs/master-release-2026-10-12/publisher'
with tempfile.TemporaryDirectory(prefix='getmacros-visible-build-') as directory:
    clean=Path(directory)
    subprocess.run(['git','checkout-index','--all','--prefix='+clean.as_posix()+'/'],cwd=PUBLISHER,check=True)
    environment={**os.environ,'GIT_DIR':str(PUBLISHER/'.git'),'GIT_WORK_TREE':str(clean)}
    commands=[[sys.executable,'-X','utf8','tools/run_food_build.py']]
    results=[]
    with (OUT/'isolated-build.log').open('w',encoding='utf-8') as log:
        for command in commands:
            result=subprocess.run(command,cwd=clean,env=environment,stdout=log,stderr=subprocess.STDOUT)
            results.append({'command':command,'exitCode':result.returncode})
            if result.returncode:break
    # Check all public pages, active source/immutable assets, and the offline shell.
    manifest=json.loads((ROOT/'assets/generated/manifest.json').read_text(encoding='utf-8'))
    paths={p.relative_to(ROOT).as_posix() for p in [*ROOT.glob('*.html'),*ROOT.glob('*/en/**/index.html')]}
    paths|=set(manifest)|{v['url'].lstrip('/') for v in manifest.values()}|{'sw.js','sitemap.xml','assets/generated/manifest.json'}
    differences=[]
    for name in sorted(paths):
        expected=(ROOT/name).read_bytes().replace(b'\r\n',b'\n');file=clean/name
        if not file.exists() or file.read_bytes().replace(b'\r\n',b'\n')!=expected:differences.append(name)
    report={'commands':results,'checkedPublicFiles':len(paths),'differences':differences,'source':'isolated staged Git index; full production build including its tests'}
    (OUT/'isolated-build-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report),flush=True)
    if differences or any(r['exitCode'] for r in results):raise SystemExit(1)
