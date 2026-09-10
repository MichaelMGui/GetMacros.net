"""Consistent reading sections, hidden symbol definitions and usable contact drafts."""
from pathlib import Path
import re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
READING={'sources.html','privacy.html','terms.html','corrections.html','editorial-policy.html','accessibility.html'}

def run():
 for path in ROOT.glob('*.html'):
  s=path.read_text(encoding='utf-8')
  # Symbol definitions are not illustrations: an unsized SVG reserved 150 px.
  s=re.sub(r'<svg xmlns="http://www.w3.org/2000/svg">(?=\s*<symbol)', '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" focusable="false" style="position:absolute;overflow:hidden">',s)
  if path.name in READING or 'class="article-container submission-article"' in s:
   s=re.sub(r'(<body[^>]*class=")([^\"]*)',lambda m:m[1]+m[2]+(' reading-page' if 'reading-page' not in m[2] else ''),s,count=1)
   s=s.replace('By GetMacros · Updated','Updated') if path.name in READING else s
   d=Document(s)
   containers=[n for n in d.nodes if 'submission-article' in n['attrs'].get('class','').split() and 'close' in n]
   for article in reversed(containers):
    inner=s[article['inner']:article['close']]
    if 'class="reading-section"' in inner:continue
    children=[n for n in d.nodes if n['parent'] is article]
    edits=[]
    for i,n in enumerate(children):
     if n['tag']!='h2':continue
     end=next((other['start'] for other in children[i+1:] if other['tag'] in {'h2','nav','section'}),article['close'])
     chunk=s[n['start']:end]
     edits.append((n['start'],end,'<section class="reading-section">'+chunk+'</section>'))
    for start,end,replacement in reversed(edits):s=s[:start]+replacement+s[end:]
  if path.name=='contact.html':
   s=re.sub(r'<main\b[^>]*>.*?</main>',(ROOT/'tools/contact-page.inc').read_text(encoding='utf-8'),s,count=1,flags=re.S)
   s=re.sub(r'(<body[^>]*class=")([^\"]*)',lambda m:m[1]+m[2]+(' contact-page' if 'contact-page' not in m[2] else ''),s,count=1)
   if 'js/contact.js' not in s:s=s.replace('</body>','<script src="js/contact.js" defer></script></body>')
  path.write_text(s,encoding='utf-8')

if __name__=='__main__':run()
