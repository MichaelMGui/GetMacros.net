"""Run the existing CI test commands exactly, with a retained result per command."""
from pathlib import Path
import json, re, shlex, subprocess, sys, time
ROOT=Path.cwd()
OUT=ROOT/'docs/global-coverage-2026-10-17'
OUT.mkdir(parents=True,exist_ok=True)
commands=[]
for line in (ROOT/'.github/workflows/site-quality.yml').read_text(encoding='utf-8').splitlines():
    value=line.strip()
    if re.match(r'^(node|python3) ',value):commands.append(shlex.split(value))
results=[]
if '--resume' in sys.argv:
    previous=json.loads((OUT/'ci-command-results.json').read_text(encoding='utf-8'))
    for expected,row in zip(commands,previous['results']):
        if row['exitCode']!=0:break
        assert row['command']==' '.join(expected)
        results.append(row)
for ordinal,args in enumerate(commands,1):
    if ordinal<=len(results):continue
    display=' '.join(args)
    if args[0]=='python3':args=[sys.executable,'-X','utf8',*args[1:]]
    started=time.monotonic()
    result=subprocess.run(args,cwd=ROOT,capture_output=True,encoding='utf-8',errors='replace')
    log=OUT/('ci-'+str(ordinal).zfill(2)+'.log');log.write_text(result.stdout+result.stderr,encoding='utf-8')
    row=dict(command=display,exitCode=result.returncode,seconds=round(time.monotonic()-started,2),log=log.relative_to(ROOT).as_posix())
    results.append(row);(OUT/'ci-command-results.json').write_text(json.dumps(dict(passAll=all(r['exitCode']==0 for r in results),completed=len(results),planned=len(commands),results=results),indent=2)+'\n',encoding='utf-8')
    print(('PASS ' if result.returncode==0 else 'FAIL ')+display+' ('+str(row['seconds'])+'s)',flush=True)
    if result.returncode:
        print((result.stdout+result.stderr)[-8000:],flush=True)
        raise SystemExit(result.returncode)
print('PASS all '+str(len(results))+' existing CI test commands.',flush=True)
