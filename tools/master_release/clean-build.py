"""Build a Git-index export and compare public bytes to the tested application."""
from pathlib import Path
import json,os,re,subprocess,tempfile,difflib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/master-release-2026-10-12';CHECKOUT=OUT/'publisher'
PYTHON='C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
with tempfile.TemporaryDirectory(prefix='getmacros-master-index-') as directory:
    clean=Path(directory)
    subprocess.run(['git','checkout-index','--all','--prefix='+clean.as_posix()+'/'],cwd=CHECKOUT,check=True)
    environment={**os.environ,'GIT_DIR':str(CHECKOUT/'.git'),'GIT_WORK_TREE':str(clean)}
    with (OUT/'clean-source-build.log').open('w',encoding='utf-8') as log:
        result=subprocess.run([PYTHON,'-X','utf8','tools/run_food_build.py'],cwd=clean,env=environment,stdout=log,stderr=subprocess.STDOUT)
    differences=[]
    excluded={'docs','tools','server','music-platform','node_modules','.git','.github','design'}
    for p in clean.rglob('*'):
        relative=p.relative_to(clean)
        if not p.is_file() or relative.parts[0] in excluded:continue
        active=ROOT/relative
        if not active.exists():differences.append({'path':relative.as_posix(),'reason':'unexpected generated public file'})
        elif p.read_bytes().replace(b'\r\n',b'\n')!=active.read_bytes().replace(b'\r\n',b'\n'):
            if relative.as_posix()=='js/meal-data.js':
                script="const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');const x=JSON.parse(fs.readFileSync(0,'utf8')),load=s=>{const c={window:{}};vm.runInNewContext(s,c);return JSON.parse(JSON.stringify(c.window.GM_MEALS))};assert.deepEqual(load(x.a),load(x.b));"
                check=subprocess.run(['node','-e',script],input=json.dumps({'a':p.read_text(encoding='utf-8'),'b':active.read_text(encoding='utf-8')}),text=True,capture_output=True)
                if check.returncode:differences.append({'path':relative.as_posix(),'reason':'meal fields differ','error':check.stderr[:1200]})
            else:
                row={'path':relative.as_posix(),'reason':'public bytes differ from verified source'}
                if len(differences)<4 or relative.suffix in ['.json','.js']:
                    left=p.read_text(encoding='utf-8');right=active.read_text(encoding='utf-8')
                    first=next((i for i,(a,b) in enumerate(zip(left,right)) if a!=b),min(len(left),len(right)))
                    row['firstDifference']={'position':first,'clean':left[max(0,first-80):first+400],'active':right[max(0,first-80):first+400]}
                differences.append(row)
    report={'buildExitCode':result.returncode,'publicDifferences':differences,'source':'isolated publisher Git index; no inherited untracked inputs'}
    (OUT/'clean-source-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print('Clean source build exit:',result.returncode,'; public differences:',len(differences))
    for row in differences[:20]:print(row)
    if result.returncode or differences:raise SystemExit(1)
