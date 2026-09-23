"""Final, repeatable publication presentation. Preserve page URLs and tool hooks.

Reviewed HTML is the source for inner pages. Historical redesign generators are
retired. This pass owns the homepage, examples, stylesheet and advertising state.
"""
from pathlib import Path
from html import escape
import json,re
from normalize_calculator_layouts import Document
from publication_examples import EXAMPLES
from build_restaurant_pages import parse_meals

ROOT=Path(__file__).resolve().parents[1]
LOGO='<svg viewBox="0 0 36 36" fill="none" aria-hidden="true"><circle cx="18" cy="18" r="14" stroke="currentColor" stroke-width="2.5"/><path d="M18 4v28M18 18h14" stroke="currentColor" stroke-width="2.5"/><path d="M8 18c0-5 3-8 6-8v16c-3 0-6-3-6-8Z" fill="currentColor"/></svg>'
CHAIN_SLUG={'CAVA':'cava','Chick-fil-A':'chick-fil-a','Chipotle':'chipotle','Dunkin’':'dunkin','Jersey Mike’s':'jersey-mikes','KFC':'kfc','McDonald’s':'mcdonalds','Panda Express':'panda-express','Panera':'panera','Popeyes':'popeyes','Starbucks':'starbucks','Subway':'subway','Sweetgreen':'sweetgreen','Taco Bell':'taco-bell','Wendy’s':'wendys'}
CHAIN_PAGE={'Dunkin’':'dunkin-healthy-breakfast-macros.html','Jersey Mike’s':'jersey-mikes-healthy-subs-macros.html','Starbucks':'starbucks-healthy-food-meals-macros.html'}

def home_markup():
 meals=parse_meals()
 chains=sorted(set(m['chain'] for m in meals),key=str.casefold)
 options=''.join('<option value="'+escape(c,quote=True)+'">'+escape(c)+'</option>' for c in chains)
 links=''.join('<a href="'+CHAIN_PAGE.get(c,CHAIN_SLUG[c]+'-healthy-meals-macros.html')+'" data-chain-name="'+escape(c,quote=True)+'"><span class="restaurant-initial" aria-hidden="true">'+escape(''.join(w[0] for w in c.replace('’',' ').replace('-',' ').split())[:2])+'</span><span>'+escape(c)+'</span><span aria-hidden="true">↗</span></a>' for c in chains)
 # Only display recorded values. Missing fat is a gap in the source records.
 featured=[]
 for chain,name in [('Chick-fil-A','Grilled Chicken Sandwich'),('Chipotle','Chicken Bowl with white rice and black beans'),('Sweetgreen','Chicken Pesto Parm')]:
  m=next(x for x in meals if x['chain']==chain and x['name']==name)
  fat='11 g' if chain=='Chick-fil-A' else '—'
  featured.append('<article class="featured-meal"><div><span class="featured-chain">'+escape(chain)+'</span><h3>'+escape(name)+'</h3><p>'+escape(m['why'])+'</p></div><dl><div><dt>Calories</dt><dd>'+str(m['cal'])+'</dd></div><div><dt>Protein</dt><dd>'+str(m['p'])+' g</dd></div><div><dt>Carbs</dt><dd>'+str(m['c'])+' g</dd></div><div><dt>Fat</dt><dd>'+fat+'</dd></div></dl><a href="'+m['url']+'">View restaurant guide <span aria-hidden="true">↗</span></a></article>')
 return (ROOT/'tools/editorial-home.inc').read_text(encoding='utf-8').replace('__CHAIN_COUNT__',str(len(chains))).replace('__MEAL_COUNT__',str(len(meals))).replace('__RESTAURANT_OPTIONS__',options).replace('__RESTAURANT_LINKS__',links).replace('__FEATURED_MEALS__',''.join(featured))

def replace_node(text,node,replacement):return text[:node['start']]+replacement+text[node['end']:]

def run():
 for path in ROOT.glob('*.html'):
  text=path.read_text(encoding='utf-8')
  if path.name=='index.html':
   doc=Document(text);main=next(n for n in doc.nodes if n['tag']=='main')
   text=replace_node(text,main,home_markup())
   text=re.sub(r'<title>.*?</title>','<title>Find a fast-food meal that fits your macros | GetMacros</title>',text,count=1,flags=re.S)
   text=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Find real fast-food meals by calories, protein, fiber and restaurant. Compare the order, portion and nutrition before you eat.">',text,count=1)
   for attr,key,value in [('property','og:title','Find a fast-food meal that fits your macros | GetMacros'),('property','og:description','Find real fast-food meals by calories, protein, fiber and restaurant. Compare the order, portion and nutrition before you eat.'),('name','twitter:title','Find a fast-food meal that fits your macros | GetMacros'),('name','twitter:description','Find real fast-food meals by calories, protein, fiber and restaurant. Compare the order, portion and nutrition before you eat.')]:
    text=re.sub(r'(<meta '+attr+'="'+key+r'" content=")[^"]*',lambda m:m.group(1)+value,text,count=1)
  if path.name=='blog.html':
   doc=Document(text);main=next(n for n in doc.nodes if n['tag']=='main')
   text=replace_node(text,main,(ROOT/'tools/editorial-blog.inc').read_text(encoding='utf-8'))
   journal_title='GetMacros Journal | Eating Out and Nutrition Guides'
   journal_description='Clear, source-linked answers about restaurant meals, protein, calories and everyday nutrition. Read the GetMacros Journal.'
   text=re.sub(r'<title>.*?</title>','<title>'+journal_title+'</title>',text,count=1,flags=re.S)
   text=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+journal_description+'">',text,count=1)
   for attr,key,value in [('property','og:title',journal_title),('property','og:description',journal_description),('name','twitter:title',journal_title),('name','twitter:description',journal_description)]:
    text=re.sub(r'(<meta '+attr+'="'+key+r'" content=")[^"]*',lambda m:m.group(1)+value,text,count=1)
  if path.name in EXAMPLES and 'id="worked-comparison"' not in text:
   doc=Document(text)
   candidates=[n for n in doc.nodes if 'article-container' in n['attrs'].get('class','').split()]
   if candidates:
    n=candidates[0]
    text=text[:n['inner']]+EXAMPLES[path.name]+text[n['inner']:]
    text=text.replace('Updated September 9, 2026','Updated September 22, 2026')
    text=re.sub(r'("dateModified"\s*:\s*")[^"]+',r'\g<1>2026-09-22',text)
  # Remove obsolete presentation at the source, not behind a second cascade.
  text=re.sub(r'<header\b[^>]*>.*?</header>',(ROOT/'tools/editorial-header.inc').read_text(encoding='utf-8').replace('__LOGO__',LOGO),text,count=1,flags=re.S)
  text=re.sub(r'<footer\b[^>]*>.*?</footer>',(ROOT/'tools/editorial-footer.inc').read_text(encoding='utf-8').replace('__LOGO__',LOGO),text,count=1,flags=re.S)
  text=re.sub(r'<style\b[^>]*>.*?</style>','',text,flags=re.S)
  text=re.sub(r'<link\b(?=[^>]*rel="stylesheet")[^>]*>','',text)
  text=re.sub(r'<link\b(?=[^>]*rel="preload")(?=[^>]*as="font")[^>]*>','',text)
  text=re.sub(r'<link\b[^>]*rel="preconnect"[^>]*href="https://pagead2\.googlesyndication\.com"[^>]*>','',text)
  text=text.replace('</head>','<link rel="stylesheet" href="css/publication.css"><link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="fonts/inter-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin></head>')
  # Publisher verification is retained. Ad serving awaits account-side CMP
  # verification; a home-made banner would not meet Google's CMP requirement.
  text=re.sub(r'<script\b[^>]*src="https://pagead2\.googlesyndication\.com/[^>]*>.*?</script>','',text,flags=re.S)
  text=re.sub(r'<script\b[^>]*src="js/(?:main|lang|tide-motion|polish|site-motion|studio-v6|atelier-v5|calculator-suite)\.js[^>]*>.*?</script>','',text,flags=re.S)
  text=re.sub(r'(<body\b[^>]*?)\sdata-ads="[^"]*"',r'\1',text)
  text=re.sub(r'(<body\b[^>]*?)\sdata-publication="[^"]*"',r'\1',text)
  text=re.sub(r'<body\b', '<body data-ads="off" data-publication="2026-09"',text,count=1)
  # Presentational inline styles were remnants of older generated templates.
  text=re.sub(r'\sstyle="[^"]*"','',text)
  doc=Document(text)
  edits=[]
  for n in doc.nodes:
   if 'brand-mark' in n['attrs'].get('class','').split(): edits.append((n['inner'],n['close'],LOGO))
  for a,b,value in reversed(edits):text=text[:a]+value+text[b:]
  text=text.replace('How I write the guides','Editorial policy')
  if path.name=='privacy.html':
   text=re.sub(r'<p>This site integrates Google AdSense\..*?</p>','<p>GetMacros has applied to Google AdSense. Publisher ownership verification remains on the site, but advertising scripts are currently paused. No Google ad requests are made by the site code. Before enabling ads, we will configure the required consent controls, verify their behavior and update this notice.</p><p>If advertising is enabled later, Google and its partners may use cookies or similar technologies. See <a href="https://policies.google.com/technologies/partner-sites">how Google uses information from sites that use its services</a> and <a href="https://myadcenter.google.com">Google’s advertising controls</a>.</p>',text,flags=re.S)
  # Clarify the educational scope next to the full macro form.
  if path.name=='calculators.html' and 'publication-calculator-note' not in text:
   text=text.replace('<form class="calc-form" id="macro-form">','<form class="calc-form" id="macro-form"><p class="clarity-hint publication-calculator-note">Adult estimates, not a prescription. Uses Mifflin–St Jeor resting energy, an activity multiplier and your chosen goal. <a href="sources.html">Formula and limitations</a>.</p>')
  if 'class="chain-finder-intro"' in text:
   text=text.replace('<header class="chain-finder-intro"><h2>Find your meal</h2></header>','<header class="chain-finder-intro"><h2>Find your meal</h2><p>Choose what matters, then compare the tracked orders. Check the restaurant menu before making a swap.</p></header>')
  # Attach provenance before any meal consumer executes. All unknown fat
  # values remain null; f in the historical dataset explicitly means fiber.
  if 'js/meal-data.js' in text:
   text=re.sub(r'<script[^>]+src="js/meal-provenance.js[^>]*>.*?</script>','',text,flags=re.S)
   text=re.sub(r'(<script[^>]+src="js/meal-data\.js[^>]*>\s*</script>)',r'\1<script src="js/meal-provenance.js" defer></script>',text)
  if path.name=='index.html' and 'js/editorial-home.js' not in text:
   text=text.replace('</body>','<script src="js/editorial-home.js" defer></script></body>')
  if path.name=='search.html':
   section='<section class="search-meals container" id="search-meals" hidden aria-live="polite"><div class="editorial-section-head"><div><h2>Matching restaurant meals</h2><p data-meal-count></p></div></div><div class="search-meal-list" id="search-meal-list"></div><p data-meal-more hidden>Showing the first 12 matches. <a href="restaurant-meal-finder.html">Use the meal finder</a> to narrow your choices.</p></section>'
   if 'id="search-meals"' not in text:text=text.replace('<section class="search-start"',section+'<section class="search-start"',1)
   if 'js/search-meals.js' not in text:text=text.replace('</body>','<script src="js/meal-data.js" defer></script><script src="js/search-meals.js" defer></script></body>')
  # Keep every retained article's factual body and current verification date.
  text=re.sub(r'\n{3,}','\n\n',text)
  path.write_text(text,encoding='utf-8')
 records=json.loads((ROOT/'tools/restaurant-review.json').read_text(encoding='utf-8'))
 metadata={r['chain']+'||'+r['name']:{'source':r['source'],'checked':r['checked'],'region':'U.S.','serving':'1 listed order','fat':None} for r in records}
 metadata['Chick-fil-A||Grilled Chicken Sandwich'].update(fat=11,serving='1 sandwich (206 g)',checked='2026-09-22',source='https://www.chick-fil-a.com/nutrition-allergens')
 script='/* Source records; missing fat is not estimated from calories. */\n(function(){var records='+json.dumps(metadata,ensure_ascii=False,separators=(',',':'))+'; (window.GM_MEALS||[]).forEach(function(m){var r=records[m.chain+"||"+m.name];if(r)Object.assign(m,r);});})();\n'
 (ROOT/'js/meal-provenance.js').write_text(script,encoding='utf-8')
 sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
 for name in [*EXAMPLES,'','blog.html','search.html','calculators.html','restaurant-meal-finder.html','privacy.html']:
  url='https://getmacros.net/'+name
  sitemap=re.sub(r'(<loc>'+re.escape(url)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-09-23' if name in ('','blog.html','search.html') else r'\g<1>2026-09-22',sitemap)
 (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
 print('Publication layout applied to all retained pages; publisher verification retained, ad requests paused.')

if __name__=='__main__':run()
