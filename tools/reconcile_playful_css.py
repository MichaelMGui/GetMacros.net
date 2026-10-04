"""Remove demonstrably obsolete rules and superseded declarations at their source.

Media scopes are kept separate. Dynamic selectors are retained from loaded JS
and active templates, rather than inferred only from initial screenshots.
"""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
FILES=['market-content.css','food-design.css','food-characters.css','release-product.css','playful-system.css']
html='\n'.join(p.read_text(encoding='utf-8') for p in R.glob('*.html'))
scripts={m.split('?')[0] for m in re.findall(r'src="(js/[^" ]+)',html)}
live=html+'\n'+'\n'.join((R/p).read_text(encoding='utf-8') for p in scripts if (R/p).exists())
live+='\n'+'\n'.join(p.read_text(encoding='utf-8') for p in (R/'tools').glob('market-*.inc'))
live+='\n'+(R/'tools/build_playful_interface.py').read_text(encoding='utf-8')
live+='\n'+'\n'.join(p.read_text(encoding='utf-8') for p in (R/'images').glob('*.svg'))
removed=[]
for name in FILES:
 p=R/'tools'/name;s=p.read_text(encoding='utf-8')
 def rule(m):
  selector=m[1].strip();body=m[2]
  if selector.startswith('@') or selector in ('from','to') or re.fullmatch('[0-9%, ]+',selector):return m[0]
  parts=selector.split(',');keep=[]
  for part in parts:
   classes=re.findall(r'\.([a-zA-Z][\w-]*)',part)
   # Dynamic boolean state classes may be assigned indirectly.
   unknown=[c for c in classes if c not in live and not c.startswith(('is-','has-','show-','game-','play-'))]
   if unknown:removed.append({'file':name,'selector':part.strip(),'reason':'Class absent from public HTML, loaded runtime and active templates','classes':unknown})
   else:keep.append(part)
  return ','.join(keep)+'{'+body+'}' if keep else ''
 s=re.sub(r'([^{}]+)\{([^{}]*)\}',rule,s)
 p.write_text(s,encoding='utf-8')
(R/'docs/playful-release-2026-10-04/legacy-css-removed.json').write_text(json.dumps(removed,indent=2),encoding='utf-8')
print('Removed',len(removed),'unreferenced legacy selectors from their source.')
