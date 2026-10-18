"""Record remaining CI checks and the changed data/payload regressions."""
from pathlib import Path
import json,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/flagship-release-2026-10-18/tests.json'
def key(parts):return ' '.join(x for x in parts if x not in ['node','python','python3',sys.executable])
def run():
    rows=json.loads(OUT.read_text(encoding='utf-8'))
    seen={key(r['command']) for r in rows if not r['exit']}
    commands=re.findall(r'^\s+(node|python3) (tools/[^\r\n]+|--test server/test/service.test.cjs)$',(ROOT/'.github/workflows/site-quality.yml').read_text(encoding='utf-8'),re.M)
    always={'tools/flagship_release/data_audit.py','tools/flagship_release/test_finder_payload.py','tools/international/test-markets.cjs'}
    for runtime,line in commands:
        args=line.split()
        if 'test-generators.py' in line:continue # recorded separately; mutating repeat build
        if key(args) in seen and args[0] not in always:continue
        command=[sys.executable,'-X','utf8',*args] if runtime=='python3' else ['node',*args]
        started=time.perf_counter();p=subprocess.run(command,cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace')
        record=dict(command=args,exit=p.returncode,seconds=round(time.perf_counter()-started,2),output=(p.stdout+p.stderr)[-13000:])
        rows=[r for r in rows if key(r['command'])!=key(args)]+[record]
        OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(line,p.returncode,flush=True)
        if p.returncode:print(record['output'],flush=True)
    failed=[r['command'] for r in rows if r['exit']]
    print(json.dumps(dict(commands=len(rows),failed=failed)))
    return bool(failed)
if __name__=='__main__':sys.exit(run())
