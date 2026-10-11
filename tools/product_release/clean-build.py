"""Verify only staged Git sources, without inherited untracked build inputs."""
from pathlib import Path
import json, os, re, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/global-product-release-2026-10-11'
CHECKOUT = OUT / 'publisher-local'
PYTHON = 'C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
with tempfile.TemporaryDirectory(prefix='getmacros-staged-source-') as temporary:
    clean = Path(temporary)
    subprocess.run(['git', 'checkout-index', '--all', '--prefix='+clean.as_posix()+'/'], cwd=CHECKOUT, check=True)
    # The legacy copy audit reads tracked filenames with git ls-files. Point that
    # read at the same staged index while all application I/O stays in the export.
    environment = {**os.environ, 'GIT_DIR':str(CHECKOUT/'.git'), 'GIT_WORK_TREE':str(clean)}
    with (OUT/'clean-source-build.log').open('w', encoding='utf-8') as log:
        result = subprocess.run([PYTHON, '-X', 'utf8', 'tools/run_food_build.py'], cwd=clean, env=environment, stdout=log, stderr=subprocess.STDOUT)
    report = {'source': 'Export of the isolated publisher Git index; no untracked inputs', 'buildExitCode': result.returncode}
    differences = []
    equivalent = []
    excluded = {'docs','tools','server','music-platform','node_modules','.git','.github','design'}
    for path in clean.rglob('*'):
        relative = path.relative_to(clean)
        if not path.is_file() or relative.parts[0] in excluded:
            continue
        counterpart = ROOT / relative
        if not counterpart.exists():
            differences.append({'path':relative.as_posix(),'reason':'No corresponding active source file'})
        elif path.read_bytes().replace(b'\r\n',b'\n') != counterpart.read_bytes().replace(b'\r\n',b'\n'):
            first, second = path.read_text(encoding='utf-8'), counterpart.read_text(encoding='utf-8')
            if relative.suffix == '.html' and re.sub(r'\?v=[a-f0-9]+','?v=HASH',first) == re.sub(r'\?v=[a-f0-9]+','?v=HASH',second):
                equivalent.append({'path':relative.as_posix(),'reason':'Only content-hash asset stamps differ'})
            elif relative.as_posix() == 'sw.js' and re.sub(r"VERSION='[^']+'","VERSION='HASH'",first) == re.sub(r"VERSION='[^']+'","VERSION='HASH'",second):
                equivalent.append({'path':relative.as_posix(),'reason':'Only content-hash cache version differs'})
            elif relative.as_posix() == 'js/meal-data.js':
                program="const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');const input=JSON.parse(fs.readFileSync(0,'utf8'));const load=s=>{const c={window:{}};vm.runInNewContext(s,c);return JSON.parse(JSON.stringify(c.window.GM_MEALS))};assert.deepEqual(load(input.a),load(input.b));console.log('PASS evaluated meal fields, including market and fat');"
                check = subprocess.run(['node','-e',program],input=json.dumps({'a':first,'b':second}),text=True,capture_output=True)
                if not check.returncode:
                    equivalent.append({'path':relative.as_posix(),'reason':'Serialization differs; every evaluated meal field and array order matches'})
                else:
                    differences.append({'path':relative.as_posix(),'reason':'Evaluated meal data differs','output':check.stderr[:1500]})
            else:
                differences.append({'path':relative.as_posix(),'reason':'Clean generated output differs from verified active application'})
    report['publicDifferences'] = differences
    report['equivalentSerializationAndStamps'] = equivalent
    (OUT/'clean-source-check.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Clean staged-source build exit:', result.returncode)
    print('Meaningful public output differences:', len(differences), '; equivalent serialization/stamps:',len(equivalent))
    for item in differences[:25]: print(item['path'], item['reason'])
    if result.returncode:
        raise SystemExit('Clean source build failed; see retained log.')
    if differences:
        raise SystemExit('Clean source output requires reconciliation; see retained report.')
