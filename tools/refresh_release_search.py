"""Search previews follow the actual retained page, not old generator copy."""
from pathlib import Path
from html import escape,unescape
import re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
def plain(value):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',value))).strip()
def run():
 p=ROOT/'search.html';text=p.read_text(encoding='utf-8');d=Document(text);edits=[]
 for n in d.nodes:
  if n['tag']!='a' or 'search-hit' not in n['attrs'].get('class','').split():continue
  target=ROOT/n['attrs']['href'].split('?')[0]
  if not target.exists():raise ValueError('Missing search destination '+str(target))
  page=target.read_text(encoding='utf-8');title=plain(re.search(r'<title>(.*?)</title>',page,re.S)[1]);h1=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',page,re.S)[1]);meta=unescape(re.search(r'<meta name="description" content="([^"]*)"',page)[1])
  fragment='<a class="search-hit" href="'+escape(n['attrs']['href'],quote=True)+'" data-search="'+escape(title+' '+meta+' '+h1,quote=True)+'"><span class="search-hit-name">'+escape(h1)+'</span><span class="search-hit-copy">'+escape(meta)+'</span></a>'
  edits.append((n['start'],n['end'],fragment))
 for a,b,value in reversed(edits):text=text[:a]+value+text[b:]
 text=re.sub(r'Show all \d+ pages','Show all '+str(len(edits))+' pages',text);p.write_text(text,encoding='utf-8')
 print('Refreshed '+str(len(edits))+' search previews from current page headings and metadata.')
if __name__=='__main__':run()
