from pathlib import Path
import re,subprocess
R=Path.cwd();P=R/'docs/food-reset-2026-10-03/baseline-build';P.mkdir(exist_ok=True)
files=subprocess.run(['git','ls-files'],capture_output=True,text=True,check=True).stdout.splitlines()
for f in files:
 if f.endswith(('.html','.js','.css','.woff2','.svg','.png','.webp','.jpg')) and (not '/' in f or f.split('/')[0] in ['js','css','images','fonts']):
  data=subprocess.run(['git','show','HEAD:'+f],capture_output=True,check=True).stdout;p=P/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
print('Captured prior committed site for comparative lab measurements')
