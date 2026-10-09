"""Connect the checked release to real navigation, indexing and source notes.

No network, new nutrition claims, fabricated counts, or publication placeholders.
Run after all page generators and shared presentation, before asset stamping.
"""
from pathlib import Path
from html import escape, unescape
from collections import defaultdict
import re, json, xml.etree.ElementTree as ET
from normalize_calculator_layouts import Document
from redesign_inventory import family
from build_meal_finder import parse_meals
from build_playful_interface import shell, food, ARROW
from restaurant_identity import mark, MARKS
from build_restaurant_expansion import preview_orders
from strengthen_meal_comparisons import CHOICES
from meal_provenance import read as read_provenance
from urllib.parse import urlencode

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/playful-release-2026-10-04'

def plain(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',s))).strip()
def metadata(path):
 s=path.read_text(encoding='utf-8')
 return {'route':path.name,'family':family(path.name,s),'title':plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',s,re.S)[1]),'description':unescape(re.search(r'<meta name="description" content="([^"]*)"',s)[1])}
def replace_main(text,main):
 n=next(n for n in Document(text).nodes if n['tag']=='main')
 old_ids={a['attrs']['id'] for a in Document(text[n['inner']:n['close']]).nodes if 'id' in a['attrs']}
 new_ids={a['attrs']['id'] for a in Document(main).nodes if 'id' in a['attrs']}
 aliases=''.join('<span id="'+escape(i,quote=True)+'"></span>' for i in sorted(old_ids-new_ids) if not i.startswith('reading-topic-'))
 main=main.replace('</main>',aliases+'</main>')
 return text[:n['start']]+main+text[n['end']:]
def reading_link(row):
 return '<a class="library-read" href="'+row['route']+'"><span>'+escape(row['title'])+'</span><small>'+escape(row['description'])+'</small>'+ARROW+'</a>'
def add_library_style(text):
 text=re.sub(r'<link[^>]*href="css/release-library.css[^>]*>','',text)
 text=re.sub(r'<script[^>]*src="js/article-library.js[^>]*>.*?</script>','',text,flags=re.S)
 return text.replace('</head>','<link rel="stylesheet" href="css/release-library.css"></head>')

def run():
 OUT.mkdir(parents=True,exist_ok=True)
 new=json.loads((ROOT/'tools/editorial_release/articles.json').read_text(encoding='utf-8'))
 new=[r for r in new if r['status']=='checked' and (ROOT/r['slug']).exists()]
 games=json.loads((ROOT/'tools/play_release/manifest.json').read_text(encoding='utf-8'))['games']
 extra=json.loads((ROOT/'tools/restaurant_release/expansion-payload.json').read_text(encoding='utf-8'))
 pages=[metadata(p) for p in sorted(ROOT.glob('*.html'))]
 articles=[p for p in pages if p['family']=='article']
 byroute={p['route']:p for p in pages}
 groups={'Eating Out':[], 'Breakfast':[], 'Coffee & Drinks':[], 'Meal Comparisons':[], 'Protein & Value':[], 'Portions & Labels':[], 'Nutrition Basics':[]}
 aliases=defaultdict(list)
 old_categories=list(dict.fromkeys(r['category'] for r in new))
 def reading_group(row):
  title=byroute[row['slug']]['title'].lower();category=row['category']
  if row['slug']=='breakfast-drinks-and-add-ons.html' or any(w in title for w in ('drink','coffee','latte','cold foam')):return 'Coffee & Drinks'
  if category=='Breakfast decisions':return 'Breakfast'
  if category=='Restaurant comparisons':return 'Meal Comparisons'
  if category in ('Protein questions','Practical protein','Food costs','Budget and value'):return 'Protein & Value'
  if category in ('Recipe arithmetic','Food labels','Calculator notes','Recipe portions','Kitchen calculations'):return 'Portions & Labels'
  if category in ('Macro fundamentals','Nutrition numbers','Sources and methods'):return 'Nutrition Basics'
  return 'Eating Out'
 for row in new:groups[reading_group(row)].append(byroute[row['slug']])
 for i,category in enumerate(old_categories):aliases[reading_group(next(r for r in new if r['category']==category))].append('reading-topic-'+str(i))
 old=[p for p in articles if p['route'] not in {r['slug'] for r in new}]
 for page in old:
  title=page['title'].lower()
  if page['route']=='breakfast-drinks-and-add-ons.html' or any(w in title for w in ('drink','coffee','latte','cold foam')):topic='Coffee & Drinks'
  elif 'breakfast' in title:topic='Breakfast'
  elif any(w in title for w in ('protein on a budget','protein cost','protein value')):topic='Protein & Value'
  elif any(w in title for w in ('recipe','portion','food label','nutrition label')):topic='Portions & Labels'
  elif page['route'] in ('compare-complete-restaurant-orders.html','best-fast-food-restaurants-for-your-goals.html'):topic='Meal Comparisons'
  else:topic='Nutrition Basics'
  groups[topic].append(page)
 aliases['Nutrition Basics'].append('reading-topic-'+str(len(old_categories)))
 topics={k:v for k,v in groups.items() if v}
 # A short editorial selection precedes a compact, complete topic library.
 featured=[byroute[r] for r in ['total-sugars-added-sugars-label.html','how-to-read-a-nutrition-label.html','compare-complete-restaurant-orders.html'] if r in byroute]
 if len(featured)<3:featured=(featured+[byroute[r['slug']] for r in new])[:3]
 topic_id=lambda topic:'learn-'+topic.lower().replace(' & ','-').replace(' ','-')
 options=''.join('<option value="'+topic_id(topic)+'">'+escape(topic)+'</option>' for topic in topics)
 sections=''.join('<section class="reading-topic" id="'+topic_id(topic)+'" data-topic-alias="'+' '.join(aliases[topic])+'" data-reading-topic><header><h3>'+escape(topic)+'</h3><p>'+str(len(rows))+' reads</p></header><div class="library-reads">'+''.join(reading_link(r) for r in rows)+'</div><button class="text-action" type="button" data-more-reads hidden>Show more reads '+ARROW+'</button></section>' for topic,rows in topics.items())
 features=''.join(reading_link(r).replace('<span>',food(c)+'<span>',1) for r,c in zip(featured,['strawberry','broccoli','egg']))
 main='<main id="main-content"><section class="library-masthead container"><div><h1>A little food<br>for thought.</h1><p>Useful answers. Clear examples. Sources you can follow.</p></div>'+food('avocado',True)+'</section><section class="library-feature container" aria-label="Start reading">'+features+'</section><section class="container topic-library"><div class="reading-browser-head"><h2>Find your next read.</h2><label class="reading-topic-choice" hidden>Read about<select id="reading-topic-select">'+options+'</select></label></div><p id="reading-topic-status" class="sr-only" role="status"></p>'+sections+'</section><section class="library-next container"><div><h2>Try it for yourself.</h2><p>Small games about portions, patterns and food.</p></div><a class="btn btn-primary" href="play.html">Make a little time to play '+ARROW+'</a></section></main>'
 p=ROOT/'articles.html';p.write_text(add_library_style(replace_main(p.read_text(encoding='utf-8'),main)),encoding='utf-8')
 text=p.read_text(encoding='utf-8');text=re.sub(r'<script[^>]*src="js/library-browser.js[^>]*>.*?</script>','',text,flags=re.S);p.write_text(text.replace('</body>','<script src="js/library-browser.js" defer></script></body>'),encoding='utf-8')
 # Journal is a small editorial front door, not a duplicate of the full library.
 chosen=[byroute[r['slug']] for r in new[:6]]
 journal='<main id="main-content" class="market-journal"><section class="library-masthead container"><div><h1>The lunch table.</h1><p>A few good reads from the GetMacros Journal.</p></div>'+food('tomato',True)+'</section><section class="journal-selection container">'+''.join(reading_link(r) for r in chosen)+'</section><section class="library-next container"><h2>Something on your mind?</h2><a class="text-action" href="articles.html">Browse every guide '+ARROW+'</a></section></main>'
 p=ROOT/'blog.html';p.write_text(add_library_style(replace_main(p.read_text(encoding='utf-8'),journal)),encoding='utf-8')
 meals=parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))
 chains=defaultdict(list)
 for m in meals:chains[m['chain']].append(m)
 provenance=read_provenance(ROOT/'js/meal-provenance.js')
 # The existing restaurant source bodies and comparison IDs remain intact;
 # their opening product composition now belongs to the same guide system.
 for name,entries in chains.items():
  if name not in CHOICES:continue
  p=ROOT/entries[0]['url'];text=p.read_text(encoding='utf-8');doc=Document(text)
  head=next((n for n in doc.nodes if any(c in n['attrs'].get('class','').split() for c in ('market-page-head','guide-masthead'))),None)
  entry=next((n for n in doc.nodes if any(c in n['attrs'].get('class','').split() for c in ('chain-finder-section','guide-discovery'))),None)
  if not head or not entry:raise ValueError('Missing restaurant composition '+p.name)
  character={'bowl':'avocado','chicken':'chicken','cup':'egg','sub':'tomato','sandwich':'potato','taco':'broccoli','leaf':'broccoli'}[MARKS[name][1]]
  intro=' '.join(re.split(r'(?<=[.!?])\s+',CHOICES[name][3])[:2])
  heading='<section class="guide-masthead container"><div><div class="guide-identity">'+mark(name)+'<span>'+str(len(entries))+' recorded orders · U.S.</span></div><h1>'+escape(name)+' nutrition</h1><p>'+escape(intro)+'</p></div><div class="guide-character">'+food(character,True)+'</div></section>'
  form='<section class="guide-discovery container" id="chain-meal-finder"><header><h2>Choose your limits.</h2></header><form class="guide-filter-entry" action="restaurant-meal-finder.html" method="get"><input type="hidden" name="chain" value="'+escape(name,quote=True)+'"><label>Calories, up to<input type="number" name="maxCal" min="150" max="2500" placeholder="Any" inputmode="numeric"></label><label>Protein, at least (g)<input type="number" name="minProtein" min="0" max="200" placeholder="Any" inputmode="numeric"></label><button class="btn btn-primary" type="submit">Find meals '+ARROW+'</button></form></section>'
  chosen=[next(m for m in entries if m['name']==n) for n in CHOICES[name][1:3]]
  rows=[{'meal':m,'values':m,'provenance':provenance[name+'||'+m['name']]} for m in chosen]
  preview='<section class="guide-preview container" aria-labelledby="guide-preview-title"><div class="guide-preview-head"><h2 id="guide-preview-title">Two places to start.</h2><p>Different listed orders. Compare the portions, too.</p></div><div class="guide-orders">'+preview_orders(rows)+'</div></section>'
  previous=next((n for n in doc.nodes if 'guide-preview' in n['attrs'].get('class','').split()),None)
  edits=[(head['start'],head['end'],heading),(entry['start'],entry['end'],form if previous else form+preview)]
  if previous:edits.append((previous['start'],previous['end'],preview))
  for a,b,v in sorted(edits,reverse=True):text=text[:a]+v+text[b:]
  text=text.replace('<main id="main-content">','<main id="main-content" class="restaurant-reference">',1)
  p.write_text(add_library_style(text),encoding='utf-8')
 intros={c['chain']:c['intro'] for c in extra['chains']}
 directory=''.join('<a class="restaurant-entry" href="'+entries[0]['url']+'">'+mark(chain)+'<div><h2>'+escape(chain)+'</h2><p>'+escape(intros.get(chain,byroute[entries[0]['url']]['description']))+'</p><small>'+str(len(entries))+' recorded orders · U.S.</small></div>'+ARROW+'</a>' for chain,entries in sorted(chains.items(),key=lambda x:x[0].casefold()))
 main='<main id="main-content"><section class="library-masthead container"><div><h1>Your usual spot.<br>A clearer choice.</h1><p>Compare recorded U.S. orders, with portions and linked nutrition sources.</p></div>'+food('potato')+'</section><section class="container restaurant-library" aria-label="Restaurant guides">'+directory+'</section><section class="library-next container"><div><h2>Want to compare across restaurants?</h2><p>Use calories, protein and the other nutrients we have recorded.</p></div><a class="btn btn-primary" href="restaurant-meal-finder.html">Find my meal '+ARROW+'</a></section><section class="container hub-notes"><p>Recipes, portions and availability can change. A guide describes the linked U.S. source; it does not establish local availability, allergen safety or Canadian menu equivalence. <a href="sources.html">Sources &amp; methods</a>.</p></section></main>'
 p=ROOT/'restaurant-meal-guides.html';p.write_text(add_library_style(replace_main(p.read_text(encoding='utf-8'),main)),encoding='utf-8')
 for chain in extra['chains']:
  p=ROOT/chain['route'];p.write_text(add_library_style(p.read_text(encoding='utf-8')),encoding='utf-8')
 # Guide forms navigate directly; their nutrition and portions are static,
 # source-checked HTML. Do not download the full interactive dataset there.
 for entries in chains.values():
  p=ROOT/entries[0]['url'];text=p.read_text(encoding='utf-8');text=re.sub(r'<script[^>]+src="js/meal-(?:data|provenance)\.js[^>]*>.*?</script>','',text,flags=re.S);p.write_text(text,encoding='utf-8')
 # Discovery keeps one global search field; indexed links stay crawlable.
 pages=[metadata(p) for p in sorted(ROOT.glob('*.html'))]
 grouped=defaultdict(list)
 game_routes={g['route'] for g in games}
 for row in pages:
  if row['route'] in {'404.html','search.html'}:continue
  kind='Games' if row['route'] in game_routes or row['route']=='play.html' else 'Restaurants' if row['family']=='restaurant' else 'Calculators' if row['family'] in {'calculator','calculator-hub','meal-ideas'} else 'Articles' if row['family']=='article' else 'Meals & site information'
  grouped[kind].append(row)
 search=''
 for kind in ['Restaurants','Calculators','Articles','Games','Meals & site information']:
  rows=grouped[kind]
  search+='<section class="search-group" data-group><h2>'+kind+' <span data-count>'+str(len(rows))+'</span></h2><div class="search-hits">'+''.join('<a class="search-hit" href="'+r['route']+'" data-search="'+escape(r['title']+' '+r['description']+' '+kind,quote=True)+'"><span class="search-hit-name">'+escape(r['title'])+'</span><span class="search-hit-copy">'+escape(r['description'])+'</span></a>' for r in rows)+'</div></section>'
 p=ROOT/'search.html';text=p.read_text(encoding='utf-8');doc=Document(text);n=doc.find(id='search-results')
 section='<section class="search-library" id="search-results"><h2 class="search-library-head">Browse the library</h2>'+search+'<div class="search-results-actions"><button type="button" id="search-results-toggle" aria-expanded="false">Browse all topics</button></div></section>'
 text=text[:n['start']]+section+text[n['end']:]
 # The old inline search controller is retired in favour of its shared source.
 text=re.sub(r'<script>\s*\(function \(\).*?</script>','',text,flags=re.S)
 text=re.sub(r'<script[^>]*src="js/site-search.js[^>]*>.*?</script>','',text,flags=re.S)
 text=text.replace('</body>','<script src="js/site-search.js" defer></script></body>')
 p.write_text(text,encoding='utf-8')
 # Replace the obsolete, hidden second meal browser with an honest no-script
 # reference list. Each order links to its full source/portion guide.
 p=ROOT/'restaurant-meal-finder.html';text=p.read_text(encoding='utf-8');doc=Document(text)
 obsolete=next((n for n in doc.nodes if 'meal-browser-shell' in n['attrs'].get('class','').split()),None)
 if obsolete:text=text[:obsolete['start']]+text[obsolete['end']:]
 text=re.sub(r'<script[^>]*src="js/meal-browser.js[^>]*>.*?</script>','',text,flags=re.S)
 text=re.sub(r'<!-- order-reference:start -->.*?<!-- order-reference:end -->','',text,flags=re.S)
 fallback='<noscript><section class="container"><h2>All recorded orders</h2><p>The interactive filters need JavaScript. You can still inspect each recorded order and its source.</p><ul>'+''.join('<li data-reference-order="'+escape(m['chain']+'||'+m['name'],quote=True)+'"><a href="'+escape(m['url'],quote=True)+'#menu-comparison">'+escape(m['chain']+' · '+m['name'])+'</a></li>' for m in meals)+'</ul></section></noscript>'
 n=next(n for n in Document(text).nodes if n['tag']=='main');text=text[:n['close']]+'<!-- order-reference:start -->'+fallback+'<!-- order-reference:end -->'+text[n['close']:];p.write_text(text,encoding='utf-8')
 p=ROOT/'privacy.html';text=p.read_text(encoding='utf-8');text=text.replace('saved restaurant meals, and an unfinished meal quiz','saved restaurant meals, article and game bookmarks, and an unfinished meal quiz');text=re.sub(r'<!-- play-privacy:start -->.*?<!-- play-privacy:end -->','',text,flags=re.S);n=Document(text).find(id='read-2');pos=text.find('</p>',n['end'])+4;text=text[:pos]+'<!-- play-privacy:start --><p>Game completions, the last puzzle seed and saved artwork are also stored locally. They are not an account or cross-device sync. Clearing site storage removes these records.</p><!-- play-privacy:end -->'+text[pos:];p.write_text(text,encoding='utf-8')
 for name in ['about.html','healthy-fast-food.html']:
  p=ROOT/name;text=p.read_text(encoding='utf-8')
  text=re.sub(r'\b83 (?:U\.S\. )?menu options',str(len(meals))+' recorded orders',text)
  text=re.sub(r'from 15 U\.S\. restaurant chains','from '+str(len(chains))+' U.S. restaurant chains',text)
  p.write_text(text,encoding='utf-8')
 # Reconcile canonical public routes without inventing data verification dates.
 ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
 tree=ET.parse(ROOT/'sitemap.xml');old_dates={e.find('s:loc',ns).text:e.find('s:lastmod',ns).text for e in tree.getroot() if e.find('s:lastmod',ns) is not None}
 urls=['https://getmacros.net/']+['https://getmacros.net/'+p.name for p in sorted(ROOT.glob('*.html')) if p.name not in {'index.html','404.html'}]
 fresh={m['url'] for m in meals}|{r['slug'] for r in new}|game_routes|{c['route'] for c in extra['chains']}|{'play.html','food-shelf.html','articles.html','blog.html','search.html','restaurant-meal-guides.html','calculators.html','restaurant-meal-finder.html','sources.html','privacy.html','what-are-macros.html','nutrition-label-comparison-tool.html'}
 xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 for url in urls:
  route=url.removeprefix('https://getmacros.net/')
  modified='2026-10-04' if route in fresh or not route else old_dates.get(url)
  xml+=' <url><loc>'+escape(url)+'</loc>'+('<lastmod>'+modified+'</lastmod>' if modified else '')+'</url>\n'
 xml+='</urlset>\n';(ROOT/'sitemap.xml').write_text(xml,encoding='utf-8')
 # Historical source inspection is kept; new inspection is a separate note.
 p=ROOT/'sources.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- expansion-note:start -->.*?<!-- expansion-note:end -->','',text,flags=re.S)
 text=text.replace('41 of the 83 tracked order records','41 of the 83 records in the earlier dataset')
 note='<section class="reading-section" id="october-4-source-expansion"><h2>October 4 restaurant-source expansion</h2><p>'+str(extra['newOrders'])+' additional recorded orders from '+str(extra['newChains'])+' U.S. chains were transcribed from inspected official sources. The complete dataset now contains '+str(len(meals))+' orders across '+str(len(chains))+' chains. A single taco or slider remains one named portion, not a full combo meal.</p><p>Exact fiber is unavailable in ten added orders, including published less-than amounts. These stay unknown. Two Raising Cane’s builds are explicit sums of individual portions, not the restaurant’s named combos. Conflicting QDOBA fat rows and a Taco John’s fiber row were excluded.</p><p>Printed source editions and retrieval dates are different. Culver’s uses a July 2025 official document; unestablished publication dates stay blank. These are U.S. records, with no inferred allergen safety, prices or local menu availability. <a href="restaurant-meal-guides.html">Inspect each restaurant’s portions and source notes</a>.</p></section>'
 n=next(n for n in Document(text).nodes if 'article-container' in n['attrs'].get('class','').split());text=text[:n['close']]+'<!-- expansion-note:start -->'+note+'<!-- expansion-note:end -->'+text[n['close']:];p.write_text(text,encoding='utf-8')
 # A compact reference within the existing nutrition guide, rather than another
 # thin standalone route. Definitions describe label accounting, not prescriptions.
 p=ROOT/'what-are-macros.html';text=p.read_text(encoding='utf-8')
 text=re.sub(r'<!-- nutrition-glossary:start -->.*?<!-- nutrition-glossary:end -->','',text,flags=re.S)
 terms=[('Calories (kcal)','A measure of food energy. GetMacros uses kcal when showing calories.'),('Serving size','The amount the printed nutrient figures describe. A U.S. label serving is not a recommendation for how much to eat.'),('Portion','The amount you actually eat. It can differ from the label serving.'),('Total carbohydrate','The carbohydrate total on the source label. Do not add the sugar and fiber lines to that total again.'),('Added sugars','Sugars in the added-sugars category are already included in total sugars.'),('Sodium (mg)','The sodium amount, shown in milligrams. A milligram is one thousandth of a gram.'),('Percent Daily Value (%DV)','A nutrient’s share of its label reference amount per serving. Different nutrients have different references; the column does not add to 100%.'),('Unknown value','A value the source does not establish exactly. A dash or missing figure is not zero; a published bound such as “less than 1 g” is not an exact amount.')]
 glossary='<section class="reading-section" id="nutrition-glossary"><h2>Nutrition terms, plainly</h2>'+''.join('<details><summary>'+escape(term)+'</summary><p>'+escape(body)+'</p></details>' for term,body in terms)+'<p>Label terms follow the <a href="https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label">FDA’s U.S. label guide</a>. Unknown-value handling describes GetMacros. Added October 4, 2026; the earlier article review date is unchanged.</p></section>'
 text=re.sub(r'("dateModified"\s*:\s*")[^"]+',r'\g<1>2026-10-04',text)
 pos=text.index('<section class="submission-sources"');text=text[:pos]+'<!-- nutrition-glossary:start -->'+glossary+'<!-- nutrition-glossary:end -->'+text[pos:]
 text=text.replace('<a href="#nutrition-glossary">Nutrition terms</a>','').replace('</nav></details><article','<a href="#nutrition-glossary">Nutrition terms</a></nav></details><article',1);p.write_text(text,encoding='utf-8')
 for name in ['restaurant-meal-finder.html','nutrition-label-comparison-tool.html']:
  p=ROOT/name;text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- glossary-link:start -->.*?<!-- glossary-link:end -->','',text,flags=re.S)
  n=next(n for n in Document(text).nodes if n['tag']=='main');link='<p class="container"><a href="what-are-macros.html#nutrition-glossary">Nutrition terms, plainly</a></p>'
  text=text[:n['close']]+'<!-- glossary-link:start -->'+link+'<!-- glossary-link:end -->'+text[n['close']:];p.write_text(text,encoding='utf-8')
 # Manifests report actual implementation, not browser or editorial approval.
 summary={'date':'2026-10-04','publicHtmlRoutes':len(pages),'rootAlias':1,'newArticlesGenerated':len(new),'gamesGenerated':len(games),'newChains':extra['newChains'],'newRecordedOrders':extra['newOrders'],'totalRecordedOrders':len(meals),'totalChains':len(chains),'searchResources':sum(map(len,grouped.values())),'verification':'Pending integrated browser review; no completion claim'}
 (OUT/'integration.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print('Connected release: '+json.dumps(summary))

if __name__=='__main__':run()
