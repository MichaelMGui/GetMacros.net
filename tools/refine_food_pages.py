"""Progressive page-family layouts after data synchronization, without deleting content."""
from pathlib import Path
import re
from normalize_calculator_layouts import Document
from redesign_inventory import family
R=Path(__file__).resolve().parents[1]
for path in R.glob('*.html'):
 text=path.read_text(encoding='utf-8')
 text=re.sub(r'<div class="page-category">.*?</div>','',text,flags=re.S)
 text=re.sub(r'<legend><span>[12]</span> (Food [12])</legend>',r'<legend>\1</legend>',text)
 if path.name=='search.html':
  text=re.sub(r'<span class="eyebrow">The GetMacros directory</span>','',text)
  text=text.replace('What would you like help with?','Search GetMacros')
  text=re.sub(r'<span class="search-start-num">.*?</span>','',text,flags=re.S)
 if path.name=='404.html':
  text=text.replace('Let’s find your next meal instead.','This page isn’t here.')
 if path.name=='articles.html':
  doc=Document(text);edits=[]
  for n in doc.nodes:
   if n['tag']=='section' and 'hub-topic' in n['attrs'].get('class','').split():
    inner=text[n['inner']:n['close']]
    if 'guide-category' in inner:continue
    title=re.search(r'<h2>(.*?)</h2>',inner,re.S)
    grid=Document(inner).find(cls='guide-grid')
    replacement='<div class="container"><details class="guide-category"'+(' open' if n['attrs'].get('id')=='macros-and-goals' else '')+'><summary>'+title[1]+'</summary>'+inner[grid['start']:grid['end']]+'</details></div>'
    edits.append((n['inner'],n['close'],replacement))
  for a,b,v in reversed(edits):text=text[:a]+v+text[b:]
  if 'class="learn-feature container"' not in text:
   feature='<section class="learn-feature container"><span data-food-character="broccoli" aria-hidden="true"><svg viewBox="0 0 160 160"><use href="images/food-characters.svg#food-broccoli"/></svg></span><div><h2>A food label, clearly.</h2><p>Start with the portion. Then compare the nutrients that matter to you.</p><a class="text-action" href="how-to-read-a-nutrition-label.html">Read the guide <span aria-hidden="true">→</span></a></div></section>'
   text=text.replace('<nav class="container hub-topics"',feature+'<nav class="container hub-topics"',1)
 if family(path.name,text)=='restaurant':
  doc=Document(text);edits=[]
  for n in doc.nodes:
   cls=n['attrs'].get('class','').split()
   if n['tag']=='div' and 'restaurant-menu-sheet' in cls:
    inner=text[n['inner']:n['close']];title=re.search(r'<h2>(.*?)</h2>',inner,re.S)
    if title:
     inner=re.sub(r'<div class="section-heading">.*?</div></div>','',inner,count=1,flags=re.S)
     edits.append((n['start'],n['end'],'<details class="restaurant-menu-sheet"><summary>'+title[1]+'</summary>'+inner+'</details>'))
   if n['tag']=='section' and 'chain-picks-section' in cls:
    inner=text[n['inner']:n['close']]
    if 'restaurant-more' in inner:continue
    title=re.search(r'<h2>(.*?)</h2>',inner,re.S)
    if title:
     inner=re.sub(r'<h2>.*?</h2>','',inner,count=1,flags=re.S)
     # Keep the original container and complete source-linked comparison.
     container=Document(inner).find(cls='container')
     v=inner[:container['inner']]+'<details class="restaurant-more"><summary>'+title[1]+'</summary>'+inner[container['inner']:container['close']]+'</details>'+inner[container['close']:]
     edits.append((n['inner'],n['close'],v))
  for a,b,v in sorted(edits,reverse=True):text=text[:a]+v+text[b:]
 if path.name=='nutrition-label-comparison-tool.html':
  doc=Document(text);edits=[]
  for panel in [n for n in doc.nodes if 'food-panel' in n['attrs'].get('class','').split()]:
   fields=[n for n in doc.nodes if n['attrs'].get('class')=='fields' and n['parent'] is panel]
   if not fields:continue
   block=fields[0];kids=[n for n in doc.nodes if n['parent'] is block and 'field' in n['attrs'].get('class','').split()]
   if len(kids)==7:
    a,b=kids[4]['start'],kids[-1]['end'];edits.append((a,b,'<details class="label-extra"><summary>Fiber, added sugar &amp; sodium</summary>'+text[a:b]+'</details>'))
  for a,b,v in reversed(edits):text=text[:a]+v+text[b:]
 # Generated body hooks/data/citations and all existing URLs remain unchanged.
 doc=Document(text);edits=[]
 for parent in doc.nodes:
  if parent['tag'] not in ('div','p') or 'action-row' in parent['attrs'].get('class','').split():continue
  children=[n for n in doc.nodes if n['parent'] is parent]
  if len(children)>1 and all('btn' in n['attrs'].get('class','').split() for n in children):
   opening=text[parent['start']:parent['inner']]
   opening=re.sub(r'class="([^"]*)"',r'class="\1 action-row"',opening,count=1) if 'class="' in opening else opening[:-1]+' class="action-row">'
   edits.append((parent['start'],parent['inner'],opening))
 for a,b,value in sorted(edits,reverse=True):text=text[:a]+value+text[b:]
 path.write_text(text,encoding='utf-8')
print('Progressive Learn categories, restaurant tables/comparisons and food-label fields applied.')
