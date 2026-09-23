"""Botanical structural migration. Preserve factual bodies, dates and tool hooks."""
from html import escape
import re
from normalize_calculator_layouts import Document
from redesign_inventory import family,plain

LOGO='<svg viewBox="0 0 40 40" fill="none" aria-hidden="true"><path d="M20 34V19M20 26C7 27 5 17 6 11c10-1 16 5 14 15ZM20 21C18 9 27 5 34 6c1 10-4 16-14 15Z" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/><circle cx="30" cy="30" r="4" fill="currentColor" opacity=".45"/></svg>'
ICONS={
 'leaf':'<path d="M12 21V11M12 16C3 17 2 10 3 5c7 0 11 4 9 11ZM12 11C11 4 17 2 22 3c0 7-4 10-10 8Z"/>',
 'calculator':'<rect x="5" y="2" width="14" height="20" rx="3"/><path d="M8 6h8M8 10h2m4 0h2M8 14h2m4 0h2M8 18h2m4 0h2"/>',
 'food':'<circle cx="13" cy="12" r="7"/><path d="M2 3v6m3-6v6M2 6h3M3.5 9v12M22 3v18"/>',
 'book':'<path d="M12 5C8 2 4 2 2 3v17c3-1 6-1 10 2 4-3 7-3 10-2V3c-3-1-6-1-10 2Zm0 0v17"/>',
 'compare':'<rect x="2" y="4" width="8" height="16" rx="2"/><rect x="14" y="2" width="8" height="16" rx="2"/><path d="M4 8h4m-4 4h4m8-6h4m-4 4h4"/>'}
def icon(name):return '<svg class="botanical-sprig" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'+ICONS[name]+'</svg>'
ICONS.update(person='<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',search='<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>')

def transform(text,name):
 kind=family(name,text)
 text=text.replace('GetMacros.net editorial team','GetMacros').replace('GetMacros editorial team','GetMacros')
 # This worked arithmetic example was newly added in this migration; unlike
 # a design-only edit, it has an explicit substantive revision date.
 if name=='serving-size-vs-portion-size.html' and 'id="worked-comparison"' in text:
  text=text.replace('Updated August 13, 2026','Updated September 23, 2026')
  text=re.sub(r'("dateModified"\s*:\s*")[^"]+',r'\g<1>2026-09-23',text)
 if name=='404.html':
  main='<main id="main-content" class="not-found"><p class="section-overline">Page not found</p>'+icon('leaf')+'<h1>Let’s find your next meal instead.</h1><p>This address is unavailable. Try the meal finder, look up a restaurant, or search for the page you need.</p><div class="focus-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Find a meal</a><a class="btn" href="search.html">Search GetMacros</a></div><p><a href="restaurant-meal-guides.html">Restaurant guides</a> · <a href="calculators.html">Free macro calculator</a> · <a href="contact.html">Report a broken link</a></p></main>'
  text=re.sub(r'<main\b.*?</main>',main,text,count=1,flags=re.S)
 text=text.replace('Light and dark themes, plus a motion pause control in the footer.','Light and dark themes.')
 if name=='privacy.html':
  text=text.replace('The current site stores your theme and motion preferences and saved restaurant meals in your browser.','The current site stores your theme preference and saved restaurant meals in your browser.')
 if name=='terms.html':
  text=text.replace('The site includes Google AdSense code and links to external sources. Whether ads appear depends on account approval and Google’s serving decisions.','The site retains Google AdSense publisher verification and links to external sources. Ad serving is currently paused. If enabled later, ads will depend on account approval, consent requirements and Google’s serving decisions.')
 if name=='healthy-fast-food.html' and 'id="quick-meal-limits"' not in text:
  doc=Document(text);hero=next(n for n in doc.nodes if 'hub-hero' in n['attrs'].get('class','').split())
  quick='<section class="container" id="quick-meal-limits"><h2>Start with a number.</h2><div class="focus-actions"><a class="btn" href="restaurant-meal-finder.html?maxCal=500&amp;minProtein=30">Up to 500 calories, 30 g+ protein</a><a class="btn" href="restaurant-meal-finder.html?maxSodium=600">Up to 600 mg sodium</a><a class="btn" href="restaurant-meal-finder.html?minFiber=8">8 g+ fiber</a></div><p class="clarity-hint">These limits compare tracked orders. They are not personal nutrition targets.</p></section>'
  text=text[:hero['end']]+quick+text[hero['end']:]
 # These two guides use a third, older article body variant.
 text=text.replace('class="container article-body"','class="article-container"')
 # Reconcile publisher/legal reference layouts into a single reading column.
 if kind in ('trust','legal') and name!='about.html' and 'class="garden-reading"' not in text:
  text=re.sub(r'<!-- reading-map:start -->.*?<!-- reading-map:end -->','',text,flags=re.S)
  doc=Document(text);main=next(n for n in doc.nodes if n['tag']=='main')
  sections=[n for n in doc.nodes if n['parent'] is main and n['tag']=='section']
  if len(sections)>1:
   a,b=sections[1]['start'],sections[-1]['end']
   text=text[:a]+'<div class="article-container reference-body">'+text[a:b]+'</div>'+text[b:]
 if 'class="article-container"' in text:
  text=re.sub(r'<!-- reading-map:start -->.*?<!-- reading-map:end -->','',text,flags=re.S)
 text=re.sub(r'(<body\b[^>]*?)\sdata-family="[^"]*"',r'\1',text)
 text=re.sub(r'<body\b','<body data-family="'+kind+'" data-design="botanical"',text,count=1) if 'data-design="botanical"' not in text else re.sub(r'<body\b','<body data-family="'+kind+'"',text,count=1)
 text=re.sub(r'(<meta name="theme-color" content=")[^"]*',r'\g<1>#f7faf3',text)
 if 'as="font"' in text:
  text=text.replace('</head>','<link rel="preload" href="fonts/fraunces-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin></head>')
 # Decorative coloured collage SVGs are replaced with a coherent line family.
 doc=Document(text);edits=[]
 for n in doc.nodes:
  if n['tag']!='svg' or 'colour-art' not in n['attrs'].get('class','').split() or 'end' not in n:continue
  parent=n['parent'];classes=parent['attrs'].get('class','') if parent else ''
  choice='leaf'
  if any(s in classes for s in ['clarity-icon','suite-hero-mark']):choice='calculator'
  if 'meal-idea-art' in classes:choice='food'
  if 'colour-tile-art' in classes:
   anc=parent['parent'];href=anc['attrs'].get('href','') if anc else ''
   choice='calculator' if 'calculator' in href else 'book' if 'articles' in href else 'food'
  edits.append((n['start'],n['end'],icon(choice)))
 for a,b,v in reversed(edits):text=text[:a]+v+text[b:]
 aliases={'icon-person':'person','icon-molecule':'leaf','icon-calculator':'calculator','icon-article':'book','icon-quiz':'compare','icon-book':'book','icon-search':'search'}
 text=re.sub(r'<svg\b[^>]*>\s*<use\b[^>]*href="#([^"]+)"[^>]*(?:/>|></use>)\s*</svg>',lambda m:icon(aliases.get(m[1],'leaf')),text)
 # All old symbol consumers are replaced above; remove the unused sprite payload.
 text=re.sub(r'<svg\b[^>]*>\s*<symbol\b.*?</svg>','',text,flags=re.S)
 if name=='sources.html':
  text=re.sub(r'(<h2[^>]*>)<span class="pill [^"]*">([^<]+)</span>',r'\1\2',text)
 if name=='high-protein-foods-list.html':
  text=re.sub(r'(<article class="protein-food-card"[^>]*>)<svg.*?</svg>',r'\1',text,flags=re.S)
 # No repeated generic instruction between the chain-specific intro and form.
 text=text.replace('<p>Choose what matters, then compare the tracked orders. Check the restaurant menu before making a swap.</p>','')
 text=re.sub(r'<span class="ranking-toggle" aria-hidden="true">.*?</span>','',text,flags=re.S)
 # Remove ornamental filled icons from chain controls; labels carry the meaning.
 text=re.sub(r'(<input[^>]+name="chain-goal"[^>]*><span>)<svg.*?</svg>',r'\1',text,flags=re.S)
 text=re.sub(r'<span class="single-card-icon"[^>]*>.*?</span>','',text,flags=re.S)
 text=text.replace('<span class="result-placeholder"></span>','<span class="result-placeholder">Enter calories to see your range.</span>')
 for redundant in ['Ranked by published protein, with the rest of the meal still visible.','The highest-calorie meals listed in this guide.','Compare portions, sauces and sides before ordering.','Find a starting point for your daily calories.']:
  if kind=='restaurant':text=text.replace('<p>'+redundant+'</p>','')
 # Clear title for the food tool; the old URL remains canonical.
 text=text.replace('Private in-browser comparison','Portion calculator')
 text=text.replace('Open table <span aria-hidden="true">+</span>','Open table')
 edits={
  'Build a flexible protein bench':'Choose a few affordable staples',
  'Three no-nonsense meal templates':'Three simple meal ideas',
  'Vegetables, fruit, grains and fats still have jobs.':'Include vegetables, fruit, grains and fats too.',
  'One high restaurant meal.':'One higher-calorie restaurant meal.',
  'One of the highest protein-per-calorie items in fast food. Rarely a whole meal on its own.':'A small grilled-nugget portion. Sides, sauces and drinks are separate.',
  'The larger count turns it into a proper protein-led meal.':'A larger grilled-nugget portion. Add any sides or sauces separately.',
  'A rare fast-food breakfast that clears 25 g protein under 300 calories.':'A breakfast sandwich; sides and drinks are separate.',
  'Tiny sides are excluded so these still function as an entrée or meal.':'Small sides are excluded from this meal comparison.',
  'Grilled nuggets are exceptionally protein-efficient, but the smaller count may need a side to become a complete meal.':'Compare the nugget count, then include any sides or sauces you plan to order.',
  'Baked potatoes work as a carbohydrate side or base; toppings determine whether they stay simple or become a larger entrée.':'Start with the tracked sandwich, salad or chili portion, then account for any extras.',
  'If you ate a mixed meal before training, you have even less reason to panic on the walk back to the car.':'If you ate a mixed meal before training, an immediate snack may be less important.',
  'Rewarding every workout with unplanned calories.':'Forgetting to include recovery food in your daily intake.',
  'One polished meal cannot rescue chronically inadequate energy, protein or sleep.':'Consistent energy, protein and sleep matter beyond one meal.',
  'Recovery is a pattern, not a single photograph of a “perfect” plate.':'A repeatable routine matters more than one meal.',
  'The fair conclusion is stronger than “we know nothing” but narrower than “impossible.”':'The findings are reassuring, but limited.',
  'That makes the claim less credible, not mathematically impossible.':'Longer studies would help establish whether that finding holds over time.',
  'Probably far more than the famous 20–30 grams. The real question is what your body does with it—and whether a different meal pattern would be more practical.':'Your body can absorb more than 30 grams at a meal. Here is how absorption differs from muscle growth, and what that means for planning meals.',
  'But “even distribution” is not a moral rule.':'An even distribution is optional.',
  'Larger servings remain useful; they are not erased at gram 31.':'Larger servings can still contribute to your daily needs.',
  'You do not need to split it into timed containers to “unlock” absorption.':'You do not need to divide it into smaller servings for absorption.',
  'For muscle gain, the surplus should support training without turning every rest day into an uncontrolled refeed.':'For muscle gain, keep the surplus consistent with your training plan.',
 }
 for old,new in edits.items():text=text.replace(old,new)
 if kind=='restaurant':text=text.replace('<p>Use the finder to rank all 83 tracked options, or return to the chain directory.</p>','')
 text=re.sub(r'<!--journal-contents:start-->.*?<!--journal-contents:end-->','',text,flags=re.S)
 # Tables keep readable columns; narrow screens scroll only the table region.
 doc=Document(text);tables=[]
 for n in doc.nodes:
  if n['tag']!='table' or 'end' not in n:continue
  ancestor=n['parent'];wrapped=False
  while ancestor:
   if any(c in ancestor['attrs'].get('class','').split() for c in ['table-wrap','table-scroll','comparison-output']):wrapped=True
   ancestor=ancestor['parent']
  if not wrapped:tables.append((n['start'],n['end']))
 for a,b in reversed(tables):text=text[:a]+'<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable reference table">'+text[a:b]+'</div>'+text[b:]
 # Existing table wrappers also need keyboard access when they overflow.
 doc=Document(text);changes=[]
 for n in doc.nodes:
  if n['tag']!='div' or not any(c in n['attrs'].get('class','').split() for c in ['table-wrap','table-scroll']):continue
  additions=''.join(' '+key+'="'+value+'"' for key,value in [('tabindex','0'),('role','region'),('aria-label','Scrollable nutrition table')] if key not in n['attrs'])
  if additions:changes.append((n['start'],n['inner'],text[n['start']:n['inner']].replace('>',additions+'>',1)))
 for a,b,v in reversed(changes):text=text[:a]+v+text[b:]
 text=text.replace('A useful pre-workout meal gives you fuel without making the session feel like digestion practice.','Choose familiar food and a portion that feels comfortable before training.')
 text=text.replace('Recovery food should fit the work you did and the next thing your body has to do.','Plan your next meal around the workout and how soon you will train again.')
 text=text.replace('A deficit describes an energy gap. It does not tell you which foods to eat or how aggressive the plan should be.','Understand what a calorie deficit means, how it is estimated and why weight changes over time.')
 # Reading navigation is real HTML. Existing section anchors remain intact.
 if 'class="garden-reading"' not in text:
  doc=Document(text)
  target=next((n for n in doc.nodes if any(c in n['attrs'].get('class','').split() for c in ['article-container','focused-guide-body','reading-map'])),None)
  if target and 'close' in target:
   body=text[target['start']:target['end']];bd=Document(body);headings=[];changes=[]
   for i,n in enumerate(n for n in bd.nodes if n['tag']=='h2' and 'close' in n):
    title=plain(body[n['inner']:n['close']]);anchor=n['attrs'].get('id') or 'guide-section-'+str(i+1)
    if not n['attrs'].get('id'):changes.append((n['start'],n['inner'],body[n['start']:n['inner']].replace('<h2','<h2 id="'+anchor+'"',1)))
    headings.append((title,anchor))
   for a,b,v in reversed(changes):body=body[:a]+v+body[b:]
   if len(headings)>1:
    toc='<nav class="garden-toc" aria-label="On this page"><strong>On this page</strong>'+''.join('<a href="#'+a+'">'+escape(t)+'</a>' for t,a in headings)+'</nav>'
    text=text[:target['start']]+'<div class="garden-reading">'+toc+body+'</div>'+text[target['end']:]
 return text
