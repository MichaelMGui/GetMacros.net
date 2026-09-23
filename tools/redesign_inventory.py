"""Discover public routes, authored copy and duplicate candidates without claiming visual review."""
from pathlib import Path
from html import unescape
from collections import defaultdict
from difflib import SequenceMatcher
import csv,json,re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/redesign';OUT.mkdir(parents=True,exist_ok=True)
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def family(name,text):
 if name=='index.html':return 'home'
 if name=='404.html':return 'error'
 if name=='restaurant-meal-finder.html':return 'finder'
 if 'class="chain-finder-intro"' in text:return 'restaurant'
 if name=='search.html':return 'search'
 if name=='blog.html':return 'journal'
 if name in ('about.html','sources.html','editorial-policy.html','corrections.html'):return 'trust'
 if name in ('privacy.html','terms.html','accessibility.html'):return 'legal'
 if name=='contact.html':return 'contact'
 if name=='calculators.html':return 'calculator-hub'
 if name=='budget-meal-builder.html':return 'meal-ideas'
 if any(s in text for s in ['class="tool-workspace','class="toolbox tool-workspace','data-focused-calculator']):return 'calculator'
 if 'article-container' in text or 'focused-guide-body' in text:return 'article'
 return 'reference-index'
def run():
 rows=[];corpus=[];repeats=defaultdict(list);paras=[]
 existing={}
 if (OUT/'coverage.csv').exists():
  with (OUT/'coverage.csv').open(encoding='utf-8',newline='') as f:existing={r['route']:r for r in csv.DictReader(f)}
 for p in sorted(ROOT.glob('*.html')):
  text=p.read_text(encoding='utf-8');doc=Document(text);main=next(n for n in doc.nodes if n['tag']=='main');body=text[main['inner']:main['close']]
  route='/'+p.name;kind=family(p.name,text)
  row=existing.get(route,dict(route=route,template=kind,visual_status='Not yet visually inspected',copy_status='Extracted; review pending',SEO_status='Pending',responsive_status='Pending',interaction_status='Pending',verification_performed='',remaining_issues='Baseline'))
  row['template']=kind;rows.append(row)
  blocks=[]
  for n in Document(body).nodes:
   if n['tag'] not in ('h1','h2','h3','p','label','legend','button','summary','li','th','td','figcaption','option') or 'close' not in n:continue
   value=plain(body[n['inner']:n['close']])
   if not value:continue
   blocks.append({'tag':n['tag'],'text':value})
   if len(value)>35:repeats[value].append(p.name)
   if n['tag']=='p' and len(value)>120:paras.append((p.name,value))
  title=plain(re.search(r'<title>(.*?)</title>',text,re.S)[1]);h1=next((b['text'] for b in blocks if b['tag']=='h1'),title)
  corpus.append({'route':route,'template':kind,'title':title,'h1':h1,'blocks':blocks})
 alias=dict(next(r for r in rows if r['route']=='/index.html'));alias['route']='/';rows.insert(0,existing.get('/',alias))
 for name in ['Main.dc.html','Contrast.dc.html','Soft.dc.html']:
  if (ROOT/'design'/name).exists():
   rows.append(dict(route='/design/'+name,template='development artifact',visual_status='Excluded development preview; not migrated',copy_status='Not public editorial content',SEO_status='Excluded by _config.yml',responsive_status='Not a public route',interaction_status='Not a public route',verification_performed='Tracked source found; no active public links; publication exclusion added',remaining_issues='Production exclusion must be checked after an authorized deployment'))
 with (OUT/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (OUT/'copy-corpus.json').write_text(json.dumps(corpus,ensure_ascii=False,indent=2),encoding='utf-8')
 repeated=[{'text':t,'pages':sorted(set(ps))} for t,ps in repeats.items() if len(set(ps))>1]
 near=[]
 for i,(p,t) in enumerate(paras):
  for q,u in paras[i+1:]:
   if p==q or t==u or abs(len(t)-len(u))>max(len(t),len(u))*.18:continue
   if SequenceMatcher(None,t,u).quick_ratio()<.88:continue
   score=SequenceMatcher(None,t,u).ratio()
   if score>=.86:near.append({'pages':[p,q],'similarity':round(score,3),'text':[t,u]})
 (OUT/'duplicate-copy.json').write_text(json.dumps({'exact':repeated,'near':near},ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'{len(rows)} scope records (including root alias and excluded development previews); {len(repeated)} exact repeated blocks; {len(near)} near-duplicate pairs.')
if __name__=='__main__':run()
