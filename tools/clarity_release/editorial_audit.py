"""Source-only editorial inventory. It does not claim rendered inspection."""
from pathlib import Path
from html import unescape
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import json,re,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/clarity-release-2026-10-14'
def plain(s):return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>',' ',s))).strip()
def audit():
 rows=[];exact=defaultdict(list);headings=defaultdict(list)
 for p in sorted(list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/*.html'))):
  text=p.read_text(encoding='utf-8');main=re.search(r'<main\b.*?</main>',text,re.S)
  if not main:continue
  main=main[0];ps=[plain(x) for x in re.findall(r'<p\b[^>]*>(.*?)</p>',main,re.S)]
  hs=[plain(x) for x in re.findall(r'<h[12]\b[^>]*>(.*?)</h[12]>',main,re.S)]
  route='/'+p.relative_to(ROOT).as_posix();route=route[:-10] if route.endswith('index.html') else route
  article=bool(re.search(r'(?:article-container|food-reading|data-family="article"|class="reading-article)',main)) and not route.startswith('/play')
  row=dict(route=route,title=hs[0] if hs else '',headings=hs,paragraphs=ps,article=article,body=plain(main),inspection='source HTML text extracted; no visual inspection')
  rows.append(row)
  for heading in set(hs):headings[heading].append(route)
  for paragraph in set(ps):
   if len(paragraph)>=75:exact[paragraph].append(route)
 near=[];articles=[r for r in rows if r['article']]
 for i,a in enumerate(articles):
  pa=next((p for p in a['paragraphs'] if len(p)>90 and not p.startswith('By ')), '')
  for b in articles[i+1:]:
   pb=next((p for p in b['paragraphs'] if len(p)>90 and not p.startswith('By ')), '')
   if pa and pb and pa!=pb:
    score=SequenceMatcher(None,pa.lower(),pb.lower()).ratio()
    if score>=.72:near.append(dict(routes=[a['route'],b['route']],similarity=round(score,3),introductions=[pa,pb]))
 report=dict(date='2026-10-14',method='HTML main text, exact paragraph and heading groups, SequenceMatcher first substantive paragraph at 0.72. Shared labels and necessary disclosures require human editorial decisions, not blind deletion.',routeCount=len(rows),articleCandidates=len(articles),headings=[dict(text=k,routes=v) for k,v in headings.items() if len(v)>2],repeatedParagraphs=[dict(text=k,routes=v) for k,v in exact.items() if len(v)>1],nearIntroductions=sorted(near,key=lambda r:-r['similarity']))
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'editorial-source-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/'editorial-duplicate-copy.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({k:report[k] for k in ['routeCount','articleCandidates']}));print('Repeated paragraphs',len(report['repeatedParagraphs']),'near introductions',len(near))
if __name__=='__main__':audit()
