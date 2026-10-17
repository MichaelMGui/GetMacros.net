"""Search previews follow the actual retained page, not old generator copy."""
from pathlib import Path
from html import escape,unescape
import re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
def plain(value):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',value))).strip()
def run():
 p=ROOT/'search.html';text=p.read_text(encoding='utf-8');d=Document(text);edits=[];seen=set();retained=0
 for n in d.nodes:
  if n['tag']!='a' or 'search-hit' not in n['attrs'].get('class','').split():continue
  route=n['attrs']['href'].split('?')[0].lstrip('/');target=ROOT/route
  if target.is_dir():target=target/'index.html'
  if not target.exists():raise ValueError('Missing search destination '+str(target))
  page=target.read_text(encoding='utf-8');title=plain(re.search(r'<title>(.*?)</title>',page,re.S)[1]);h1=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',page,re.S)[1]);meta=unescape(re.search(r'<meta name="description" content="([^"]*)"',page)[1])
  if route in seen or re.search(r'<meta\s+name="robots"[^>]*content="[^"]*noindex',page):
   edits.append((n['start'],n['end'],''));continue
  seen.add(route);retained+=1
  country=re.match(r'^([a-z]{2})/en/',route)
  market=country[1].upper() if country else 'US' if 'data-market-scope="US"' in page else ''
  fragment='<a class="search-hit"'+(' data-market="'+market+'"' if market else '')+' href="'+escape(n['attrs']['href'],quote=True)+'" data-search="'+escape(title+' '+meta+' '+h1,quote=True)+'"><span class="search-hit-name">'+escape(h1)+'</span><span class="search-hit-copy">'+escape(meta)+'</span></a>'
  edits.append((n['start'],n['end'],fragment))
 for a,b,value in reversed(edits):text=text[:a]+value+text[b:]
 groups=Document(text);counts=[]
 for n in groups.nodes:
  if 'search-group' not in n['attrs'].get('class','').split():continue
  fragment=text[n['start']:n['end']];count=len(re.findall(r'class="search-hit"',fragment));fragment=re.sub(r'(<span data-count>)\d+',lambda m:m[1]+str(count),fragment);counts.append((n['start'],n['end'],fragment))
 for a,b,value in reversed(counts):text=text[:a]+value+text[b:]
 text=re.sub(r'Show all \d+ pages','Show all '+str(retained)+' pages',text);p.write_text(text,encoding='utf-8')
 print('Refreshed '+str(retained)+' distinct indexable search previews from current headings and metadata.')
if __name__=='__main__':run()
