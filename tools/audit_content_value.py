"""Mechanical content inventory, with editorial actions explicitly distinguished."""
from pathlib import Path
from html import unescape
from collections import defaultdict
import csv,json,re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/adsense-2026-09-28';OUT.mkdir(exist_ok=True)
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',s))).strip()
rows=[];paragraphs=defaultdict(set)
for p in sorted(ROOT.glob('*.html')):
 t=p.read_text(encoding='utf-8');d=Document(t);main=next(n for n in d.nodes if n['tag']=='main');body=t[main['inner']:main['close']]
 for n in Document(body).nodes:
  if n['tag']=='p' and 'close' in n:
   s=plain(body[n['inner']:n['close']])
   if len(s)>120:paragraphs[s].add(p.name)
 action='Retained; mechanical inventory only in this pass. No arbitrary minimum word count applied.'
 if 'id="ordering-comparison"' in body:action='Repeated ranked meal cards replaced by a restaurant-specific decision, two recorded portions, interpretation and direct sources.'
 if p.name=='body-recomposition-explained.html':action='Rewritten to focus on measurement and interpretation, distinct from the calorie-deficit evidence article.'
 if p.name=='sources.html':action='Corrected explanation of complete records, missing values, filter exclusions and preference ordering.'
 rows.append(dict(route='/'+p.name,title=plain(re.search('<title>(.*?)</title>',t,re.S)[1]),main_words=len(plain(body).split()),external_links=len(re.findall('href="https://(?!getmacros.net)',body)),action=action))
with (OUT/'content-inventory.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
duplicates=[dict(text=t,pages=sorted(p)) for t,p in paragraphs.items() if len(p)>1]
(OUT/'repeated-paragraphs.json').write_text(json.dumps(duplicates,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(rows)} pages inventoried; {len(duplicates)} cross-page repeated paragraphs flagged for context, not automatically removed.')
