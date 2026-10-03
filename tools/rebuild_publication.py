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
from market_presentation import transform, LOGO as MARKET_LOGO
from restaurant_identity import mark

ROOT=Path(__file__).resolve().parents[1]
LOGO=MARKET_LOGO
CHAIN_SLUG={'CAVA':'cava','Chick-fil-A':'chick-fil-a','Chipotle':'chipotle','Dunkin’':'dunkin','Jersey Mike’s':'jersey-mikes','KFC':'kfc','McDonald’s':'mcdonalds','Panda Express':'panda-express','Panera':'panera','Popeyes':'popeyes','Starbucks':'starbucks','Subway':'subway','Sweetgreen':'sweetgreen','Taco Bell':'taco-bell','Wendy’s':'wendys'}
CHAIN_PAGE={'Dunkin’':'dunkin-healthy-breakfast-macros.html','Jersey Mike’s':'jersey-mikes-healthy-subs-macros.html','Starbucks':'starbucks-healthy-food-meals-macros.html'}

def home_markup():
 meals=parse_meals()
 chains=sorted(set(m['chain'] for m in meals),key=str.casefold)
 links=''.join('<a href="'+CHAIN_PAGE.get(c,CHAIN_SLUG[c]+'-healthy-meals-macros.html')+'" data-chain-name="'+escape(c,quote=True)+'">'+mark(c)+'<span>'+escape(c)+'</span></a>' for c in chains)
 return (ROOT/'tools/market-home.inc').read_text(encoding='utf-8').replace('__CHAIN_COUNT__',str(len(chains))).replace('__MEAL_COUNT__',str(len(meals))).replace('__RESTAURANT_LINKS__',links).replace('__HOME_FINDER__',(ROOT/'tools/market-home-finder.inc').read_text(encoding='utf-8'))

def replace_node(text,node,replacement):return text[:node['start']]+replacement+text[node['end']:]

def run():
 from build_edition_css import build
 build()
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
   text=replace_node(text,main,(ROOT/'tools/market-blog.inc').read_text(encoding='utf-8'))
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
  text=re.sub(r'<header\b[^>]*>.*?</header>',(ROOT/'tools/market-header.inc').read_text(encoding='utf-8').replace('__LOGO__',LOGO),text,count=1,flags=re.S)
  text=re.sub(r'<footer\b[^>]*class="market-footer"[^>]*>.*?</footer>',(ROOT/'tools/market-footer.inc').read_text(encoding='utf-8').replace('__LOGO__',LOGO),text,count=1,flags=re.S)
  text=re.sub(r'<style\b[^>]*>.*?</style>','',text,flags=re.S)
  text=re.sub(r'<link\b(?=[^>]*rel="stylesheet")[^>]*>','',text)
  text=re.sub(r'<link\b(?=[^>]*rel="preload")(?=[^>]*as="font")[^>]*>','',text)
  text=re.sub(r'<link\b[^>]*rel="preconnect"[^>]*href="https://pagead2\.googlesyndication\.com"[^>]*>','',text)
  text=text.replace('</head>','<link rel="stylesheet" href="css/publication.css"><link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="fonts/inter-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin></head>')
  # Publisher verification is retained. Ad serving awaits account-side CMP
  # verification; a home-made banner would not meet Google's CMP requirement.
  text=re.sub(r'<script\b[^>]*src="https://pagead2\.googlesyndication\.com/[^>]*>.*?</script>','',text,flags=re.S)
  text=re.sub(r'<div class="ad-auto-anchor"[^>]*>\s*</div>','',text)
  text=re.sub(r'<script\b[^>]*src="js/(?:main|lang|tide-motion|polish|site-motion|studio-v6|atelier-v5|calculator-suite|page-experience)\.js[^>]*>.*?</script>','',text,flags=re.S)
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
  text=transform(text,path.name)
  # One shared runtime for characters, non-identifying event boundaries and
  # optional advertising. Serving stays disabled until an approved adapter
  # and affirmative consent are supplied.
  for script in ['product-events','food-characters','ad-placements']:
   text=re.sub(r'<script[^>]+src="js/'+script+r'\.js[^>]*>.*?</script>','',text,flags=re.S)
  text=text.replace('</body>','<script src="js/product-events.js" defer></script><script src="js/food-characters.js" defer></script><script src="js/ad-placements.js" defer></script></body>')
  if 'js/meal-finder.js' in text:
   text=re.sub(r'<script[^>]+src="js/meal-engine.js[^>]*>.*?</script>','',text,flags=re.S)
   text=re.sub(r'(<script[^>]+src="js/meal-finder\.js)',r'<script src="js/meal-engine.js" defer></script>\1',text,count=1)
  # Keep every retained article's factual body and current verification date.
  text=re.sub(r'\n{3,}','\n\n',text)
  text=re.sub(r'(?m)^[ \t]+$','',text)
  path.write_text(text,encoding='utf-8')
 records=json.loads((ROOT/'tools/restaurant-review.json').read_text(encoding='utf-8'))
 metadata={r['chain']+'||'+r['name']:{'source':r['source'],'checked':r['checked'],'region':'U.S.','serving':'1 listed order','fat':None} for r in records}
 metadata['Chick-fil-A||Grilled Chicken Sandwich'].update(fat=11,serving='1 sandwich (206 g)',checked='2026-09-22',source='https://www.chick-fil-a.com/nutrition-allergens')
 patches=ROOT/'docs/release-2026-10-03/data-audited-patches.json'
 if patches.exists():
  for r in json.loads(patches.read_text(encoding='utf-8'))['records']:
   metadata[r['recordKey']].update(source=r['source'],checked=r['retrievalDate'],serving=r['serving'],fat=r['values'].get('fat'),sourceDate=r['sourceDate'],nutrientProvenance=next(item['nutrientProvenance'] for item in records if item['chain']+'||'+item['name']==r['recordKey']),components=r['components'],verificationStatus=r['verificationStatus'],notes=r['notes'])
 from meal_provenance import pack
 (ROOT/'js/meal-provenance.js').write_text(pack(metadata),encoding='utf-8')
 sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
 for name in [*EXAMPLES,'','blog.html','search.html','calculators.html','restaurant-meal-finder.html','privacy.html']:
  url='https://getmacros.net/'+name
  sitemap=re.sub(r'(<loc>'+re.escape(url)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-09-23' if name in ('','blog.html','search.html','serving-size-vs-portion-size.html') else r'\g<1>2026-09-22',sitemap)
 (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
 print('Publication layout applied to all retained pages; publisher verification retained, ad requests paused.')

if __name__=='__main__':run()
