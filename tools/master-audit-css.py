"""Conservative advisory report: selectors absent from final public HTML/JS.

No files are modified. Review named selectors before removing rules.
"""
from pathlib import Path
from urllib.parse import urlparse
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
urls=[n.text for n in ET.parse(ROOT/'sitemap.xml').iter() if n.tag.endswith('loc')]
paths=[ROOT/('index.html' if urlparse(u).path=='/' else urlparse(u).path.strip('/')+'/index.html' if urlparse(u).path.endswith('/') else urlparse(u).path.lstrip('/')) for u in urls]
paths.extend(ROOT/p for p in ['404.html','food-diary.html','offline.html'])
html='\n'.join(p.read_text(encoding='utf-8') for p in paths if p.exists())
scripts=set(re.findall(r'src="/?(js/[^"?]+)(?:\?[^" ]*)?"',html))
# Modules are also loaded lazily by script insertion or imported from JS.
runtime='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'js').glob('*.js'))
art='\n'.join(p.read_text(encoding='utf-8') for p in (ROOT/'images').glob('*.svg'))
active=html+'\n'+runtime+'\n'+art+'\n'+(ROOT/'tools/build_master_interface.py').read_text(encoding='utf-8')
files=['market-content.css','food-design.css','food-characters.css','release-product.css','playful-system.css'];rows=[]
for name in files:
 s=(ROOT/'tools'/name).read_text(encoding='utf-8')
 for m in re.finditer(r'([^{}]+)\{([^{}]*)\}',s):
  selector=m[1].strip()
  if selector.startswith('@') or selector in ['from','to'] or re.fullmatch(r'[0-9%, ]+',selector):continue
  for part in selector.split(','):
   classes=re.findall(r'\.([a-zA-Z][\w-]*)',part)
   unknown=[c for c in classes if c not in active and not c.startswith(('is-','has-','show-','game-','play-'))]
   if unknown:rows.append({'file':name,'selector':part.strip(),'unknownClasses':unknown,'bytes':len(m[0].encode())})
out=ROOT/'docs/master-release-2026-10-12/legacy-css-candidates.json';out.write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print('Advisory candidates:',len(rows),'estimated whole-rule bytes',sum(r['bytes'] for r in rows))
for r in rows:print(r['file'],r['bytes'],r['selector'])
