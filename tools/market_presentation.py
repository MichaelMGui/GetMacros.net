"""Structural page-family presentation. Nutrition/content bodies remain source HTML."""
import re
from build_restaurant_pages import parse_meals
from normalize_calculator_layouts import Document
from redesign_inventory import family
LOGO='<svg viewBox="0 0 40 40" aria-hidden="true"><path fill="currentColor" d="M20 19C4 20 5 4 12 5c6 0 8 7 8 14Zm1 1C20 4 36 5 35 12c0 6-7 8-14 8Zm-1 1c16-1 15 15 8 14-6 0-8-7-8-14Zm-1-1c1 16-15 15-14 8 0-6 7-8 14-8Z"/><circle cx="20" cy="20" r="3" fill="currentColor"/></svg>'

def transform(text,name):
 kind=family(name,text)
 text=text.replace('<p>Choose what matters, then compare the tracked orders. Check the restaurant menu before making a swap.</p>','')
 text=text.replace('<header class="site-header market-header">','<header class="site-header market-header" id="site-top">')
 text=text.replace('<a href="#main-content">Back to top</a>','<a href="#site-top">Back to top</a>')
 text=text.replace('<strong>Restaurant directory</strong>','<strong>All restaurants</strong>').replace('<strong>Nutrition basics</strong>','<strong>Nutrition guides</strong>')
 text=re.sub(r'\sdata-design="[^"]*"','',text)
 text=text.replace('<body','<body data-design="market"',1)
 text=re.sub(r'(class="[^"]*)\btool-workspace\b',r'\1market-tool-layout',text)
 text=text.replace('class="calc-wrap"','class="calculation-workbench"').replace('class="tool-workspace"','class="market-tool-layout"')
 text=text.replace('class="garden-reading"','class="market-reading-layout"')
 if 'class="reading-contents"' not in text:
  text=re.sub(r'(<nav class="garden-toc".*?</nav>)',r'<details class="reading-contents"><summary>In this guide</summary>\1</details>',text,flags=re.S)
 if name not in ('index.html','blog.html','search.html','restaurant-meal-finder.html','404.html') and 'class="market-page-head"' not in text:
  doc=Document(text)
  h=next((n for n in doc.nodes if n['tag']=='h1'),None)
  ancestor=h['parent'] if h else None
  hero=None
  while ancestor and ancestor['tag']!='main':
   if any(c in ancestor['attrs'].get('class','').split() for c in ['hub-hero','page-hero','focus-page-hero','tool-hero','clear-page-intro','calc-hub-hero','policy-hero','article-hero','focused-hero']):hero=ancestor;break
   ancestor=ancestor['parent']
  if hero and 'end' in hero and name!='contact.html':
   fragment=text[hero['start']:hero['end']];hd=Document(fragment)
   heading=next(n for n in hd.nodes if n['tag']=='h1')
   paragraphs=[n for n in hd.nodes if n['tag']=='p' and 'end' in n]
   actions=[n for n in hd.nodes if any(c in n['attrs'].get('class','').split() for c in ['hero-actions','focus-actions']) and 'end' in n]
   content=fragment[heading['start']:heading['end']]+''.join(fragment[n['start']:n['end']] for n in paragraphs)+''.join(fragment[n['start']:n['end']] for n in actions)
   label={'restaurant':'Restaurant field guide','article':'The GetMacros reader','calculator':'The number studio','calculator-hub':'The number studio','trust':'Behind GetMacros','legal':'Site information'}.get(kind,'Explore GetMacros')
   text=text[:hero['start']]+'<section class="market-page-head"><div class="container page-head-grid"><div class="page-category">'+label+'</div><div class="page-intro-content">'+content+'</div></div></section>'+text[hero['end']:]
 if name=='search.html' and 'market-search-head' not in text:
  doc=Document(text);q=next(n for n in doc.nodes if n['attrs'].get('id')=='site-search');parent=q
  while parent and parent['tag']!='section':parent=parent['parent']
  if parent:
   fragment=text[parent['start']:parent['end']]
   fragment=fragment.replace('class="container"','class="container market-search-head"',1)
   text=text[:parent['start']]+fragment+text[parent['end']:]
 if name=='contact.html' and 'data-copy-address' not in text:
  text=text.replace('<p class="contact-hint">Opens your mail service in a new tab. Sign in if needed.</p>',CONTACT)
 if name=='search.html' and 'search-entry' not in text:
  text=re.sub(r'(<h1>.*?</h1>)(\s*)(<label class="search-box".*?<p id="search-status".*?</p>)',r'<div class="search-title"><span class="eyebrow">The GetMacros directory</span>\1</div><div class="search-entry">\3</div>',text,count=1,flags=re.S)
 if kind=='restaurant' and 'restaurant-menu-sheet' not in text:
  doc=Document(text);menu=next((n for n in doc.nodes if n['attrs'].get('id')=='menu-comparison'),None);picks=next((n for n in doc.nodes if 'chain-picks-section' in n['attrs'].get('class','').split()),None)
  if menu and picks:
   frag=text[menu['start']:menu['end']]
   frag=frag.replace('<details class="restaurant-menu-details">','<div class="restaurant-menu-sheet">').replace('</details>','</div>')
   frag=re.sub(r'<summary><span><small>Complete nutrition table</small><strong>(.*?)</strong></span><b>Open table</b></summary>',r'<div class="section-heading"><div><p class="section-overline">The recorded menu</p><h2>\1</h2></div></div>',frag,flags=re.S)
   text=text[:menu['start']]+text[menu['end']:]
   text=text[:picks['start']]+frag+text[picks['start']:]
 if name=='about.html' and 'page-record-count' not in text:
  meals=parse_meals()
  text=re.sub(r'(<h1\b[^>]*>.*?</h1>)',lambda m:m[1]+'<p class="page-record-count">'+str(len(meals))+' menu options from '+str(len(set(m['chain'] for m in meals)))+' U.S. restaurant chains.</p>',text,count=1,flags=re.S)
 # Home loads the very same finder component and source records.
 if name=='index.html':
  text=re.sub(r'<script[^>]*src="js/(?:editorial-home|meal-data|meal-provenance|meal-finder)\.js[^>]*>.*?</script>','',text,flags=re.S)
  text=text.replace('</body>','<script src="js/meal-data.js" defer></script><script src="js/meal-provenance.js" defer></script><script src="js/meal-finder.js" defer></script></body>')
 text=re.sub(r'(<meta name="theme-color" content=")[^"]*',r'\g<1>#fffefb',text)
 return text

CONTACT='<div class="contact-direct"><span class="eyebrow">Email me directly</span><a class="contact-address" href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a><div class="contact-direct-actions"><button class="btn btn-secondary" type="button" data-copy-address>Copy email address</button><a class="btn btn-primary" href="#contact-draft" data-contact-topic="idea">Suggest an improvement</a><a class="btn btn-quiet" href="#contact-draft" data-contact-topic="problem">Report a problem</a></div></div>'
