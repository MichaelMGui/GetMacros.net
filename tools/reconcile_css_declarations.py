"""Reconcile identical selectors within identical media scopes, at source."""
from pathlib import Path
import re,json
R=Path(__file__).resolve().parents[1]
FILES=['market-content.css','food-design.css','food-characters.css','release-product.css','playful-system.css']
rules=[];sources={}
def walk(name,s,a,b,scope=()):
 pos=a
 while pos<b:
  opening=s.find('{',pos,b)
  if opening<0:return
  depth=1;end=opening+1;quote=None
  while end<b and depth:
   c=s[end]
   if quote:
    if c==quote and s[end-1]!='\\':quote=None
   elif c in "\"'":quote=c
   elif c=='{':depth+=1
   elif c=='}':depth-=1
   end+=1
  selector=re.sub(r'/\*.*?\*/','',s[pos:opening],flags=re.S).strip()
  if selector.startswith(('@media','@supports')):walk(name,s,opening+1,end-1,scope+(re.sub(r'\s+','',selector),))
  elif not selector.startswith('@'):
   declarations=re.split(r';(?![^\(]*\))',s[opening+1:end-1])
   rules.append((name,opening+1,end-1,scope,tuple(x.strip() for x in selector.split(',')),declarations))
  pos=end
seen={};edits={n:[] for n in FILES};removed=[]
for name in FILES:
 s=(R/'tools'/name).read_text(encoding='utf-8');sources[name]=s;walk(name,s,0,len(s))
for name,a,b,scope,selectors,declarations in reversed(rules):
 keep=[]
 for declaration in declarations:
  if ':' not in declaration:continue
  prop,value=declaration.split(':',1);prop=prop.strip()
  if all((scope,selector,prop) in seen for selector in selectors):removed.append({'file':name,'selectors':selectors,'property':prop})
  else:keep.append(declaration)
  for selector in selectors:seen[(scope,selector,prop)]=value
 edits[name].append((a,b,';'.join(keep)))
for name,changes in edits.items():
 s=sources[name]
 for a,b,value in sorted(changes,reverse=True):s=s[:a]+value+s[b:]
 s=re.sub(r'[^{}]+\{\s*\}','',s)
 (R/'tools'/name).write_text(s,encoding='utf-8')
(R/'docs/playful-release-2026-10-04/reconciled-declarations.json').write_text(json.dumps(removed,indent=2),encoding='utf-8')
print('Reconciled',len(removed),'superseded declarations in original source rules.')
