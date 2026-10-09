"""Inventory active pages, metadata/links, and editorial repetition candidates."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
from collections import defaultdict,Counter
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from site_scope import KEEP_ROOT_HTML
OUT=ROOT/'docs/international-release-2026-10-09';BASE='https://getmacros.net'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.inmain=False;self.skip=0;self.tag=None;self.parts=[];self.paragraphs=[];self.headings=[];self.links=[];self.ids=[];self.title='';self.meta={};self.canonical=None;self.alternates=[];self.family=None;self.scope=None;self.feed(text)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='main':self.inmain=True
  if t=='html':self.scope=a.get('data-market-scope')
  if t=='body':self.family=a.get('data-family')
  if a.get('id'):self.ids.append(a['id'])
  if t=='a' and a.get('href'):self.links.append(a['href'])
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if t=='link' and a.get('rel')=='canonical':self.canonical=a.get('href')
  if t=='link' and a.get('hreflang'):self.alternates.append((a['hreflang'],a.get('href')))
  if self.inmain and t in ['script','style']:self.skip+=1
  if (self.inmain and not self.skip and t in ['p','h1','h2','h3']) or t=='title':self.tag=t;self.parts=[]
 def handle_data(self,s):
  if self.tag and not self.skip:self.parts.append(s)
 def handle_endtag(self,t):
  if self.inmain and t in ['script','style']:self.skip-=1
  if t==self.tag:
   text=' '.join(''.join(self.parts).split())
   if t=='title':self.title=text
   elif t=='p':self.paragraphs.append(text)
   else:self.headings.append((t,text))
   self.tag=None
  if t=='main':self.inmain=False
manifest=json.loads((ROOT/'tools/international/routes.json').read_text(encoding='utf-8'))
routes={('/' if f=='index.html' else '/'+f):ROOT/f for f in sorted(KEEP_ROOT_HTML)}|{r['route']:ROOT/r['path'] for r in manifest}
pages={route:Page(path.read_text(encoding='utf-8')) for route,path in routes.items()}
games=json.loads((ROOT/'tools/play_release/manifest.json').read_text(encoding='utf-8'))['games']
for g in games:
 if '/'+g['route'] in pages:pages['/'+g['route']].family='game'
if '/play.html' in pages:pages['/play.html'].family='game-index'
def target(url):
 u=urlsplit(url);path=unquote(u.path);p=ROOT/(path.lstrip('/') or 'index.html')
 if p.is_dir():p=p/'index.html'
 return p,u.fragment
errors=[];incoming=Counter();duplicates=defaultdict(list);internal=[]
for route,p in pages.items():
 expected=BASE+route
 if route!='/404.html' and p.canonical!=expected:errors.append({'route':route,'error':'canonical','value':p.canonical,'expected':expected})
 if route=='/404.html' and 'noindex' not in p.meta.get('robots',''):errors.append({'route':route,'error':'404 missing noindex'})
 if len([h for h,t in p.headings if h=='h1'])!=1:errors.append({'route':route,'error':'main h1 count'})
 if not p.title or not p.meta.get('description'):errors.append({'route':route,'error':'missing title/description'})
 for href in p.links:
  url=urljoin(BASE+route,href);u=urlsplit(url)
  if u.netloc=='getmacros.net':
   path,fragment=target(url)
   if not path.exists():errors.append({'route':route,'error':'broken link','href':href})
   else:
    found=next((r for r,f in routes.items() if f==path),None)
    if found:incoming[found]+=1
    if fragment and path.suffix=='.html' and found and fragment not in pages[found].ids:errors.append({'route':route,'error':'missing anchor','href':href})
 for language,url in p.alternates:
  equivalent=urlsplit(url).path;other=pages.get(equivalent)
  if not other or not any(v==expected for l,v in other.alternates):errors.append({'route':route,'error':'nonreciprocal hreflang','href':url})
 for text in p.paragraphs:
  if len(text)>80:duplicates[text].append(route)
  if re.search(r'\b(?:release|repository|baseline|rollout|integration|data pipeline|fixture|dataset|captured|records)\b',text,re.I):internal.append({'route':route,'text':text})
duplicates=[{'text':t,'routes':sorted(set(rs)),'status':'editorial review candidate; shared factual limits are not automatically removed'} for t,rs in duplicates.items() if len(set(rs))>=3]
report={'routes':len(routes),'families':dict(Counter(p.family for p in pages.values())),'pages':[{'route':r,'family':p.family,'market_scope':p.scope,'title':p.title,'description':p.meta.get('description'),'main_paragraphs':len(p.paragraphs),'incoming_links':incoming[r]} for r,p in pages.items()],'orphans':[r for r in routes if not incoming[r] and r!='/404.html'],'errors':errors}
(OUT/'inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'copy-audit.json').write_text(json.dumps({'method':'Scripted main-content paragraph review candidates; not a claim that every page was visually read. Necessary disclosures/source notes require editorial retention.','repeated_paragraphs':duplicates,'internal_language_candidates':internal},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(routes),'active routes;',len(errors),'metadata/link/hreflang errors;',len(report['orphans']),'orphans;',len(duplicates),'repeated paragraphs;',len(internal),'language candidates')
for row in errors[:12]:print(row)
