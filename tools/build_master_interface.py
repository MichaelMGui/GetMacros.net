"""One country-aware homepage and shared control treatment, after product builds.

The registry supplies exact servings; this module does not invent local menus.
Existing URLs, source notes, fonts, SVG characters and tool hooks are retained.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlencode
from collections import defaultdict
import json,re
from normalize_calculator_layouts import Document

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/master-release-2026-10-12'
ARROW='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>'
SUN='<svg class="appearance-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/></svg>'
MOON='<svg class="appearance-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M20.5 14.7A8.8 8.8 0 0 1 9.3 3.5a8.8 8.8 0 1 0 11.2 11.2Z"/></svg>'
def e(v):return escape(str(v),quote=True)
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def character(name):return '<span data-food-character="'+name+'" aria-hidden="true"><svg viewBox="0 0 160 160" aria-hidden="true"><use href="/images/food-characters.svg#food-'+name+'"/></svg></span>'
def absolute(text):return re.sub(r'\b(href|src|action)="((?!https?:|//|/|#|mailto:|tel:|data:)[^"]+)"',lambda m:m[1]+'="/'+m[2]+'"',text)
def element_replace(text,cls,replacement):
 # Newer route templates can already have a native dialog shell. This optional
 # legacy-control migration must not require a superseded disclosure to exist.
 n=next((n for n in Document(text).nodes if cls in n['attrs'].get('class','').split()),None)
 return text[:n['start']]+replacement+text[n['end']:] if n else text
def market_file(info):return ROOT/('index.html' if info['home']=='/' else info['home'].strip('/')+'/index.html')
def countries():return json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
def menu_card(row,code,info):
 values=lambda key: 'Unknown' if row.get(key) is None else f'{row[key]:g}'
 secondary=lambda key: 'Unknown' if row.get(key) is None else f'{row[key]:g} g'
 guide=row['url'] if row['url'].startswith('/') else '/'+row['url']
 title='<span lang="ja">'+e(row['name'])+'</span>' if row.get('language')=='ja' else e(row['name'])
 source_urls=list(dict.fromkeys([row.get('source')]+[value.get('source') for value in row.get('nutrientProvenance',{}).values() if isinstance(value,dict)]));source_urls=[url for url in source_urls if url]
 source=' · '.join('<a href="'+e(url)+'">'+('Official nutrition source' if i==0 else 'Additional nutrient source')+'</a>' for i,url in enumerate(source_urls)) or '<a href="/sources.html">Source notes</a>'
 edition='Source edition: '+e(row['sourceDate']) if row.get('sourceDate') else 'Source edition not supplied'
 return '<article class="home-menu-card" data-home-record="'+e(row.get('id') or row['restaurantMarketId']+'|'+row['name'])+'" data-record-market="'+code+'"><a class="home-menu-brand" href="'+e(guide)+'">'+e(row['chain'])+'</a><h3>'+title+'</h3><dl class="home-menu-values"><div><dt>Calories</dt><dd>'+values('cal')+'<span> kcal</span></dd></div><div><dt>Protein</dt><dd>'+values('p')+'<span> g</span></dd></div></dl><details class="home-serving"><summary>Portion &amp; source</summary><p>'+e(row.get('serving') or 'Named source serving')+'</p><p>'+edition+'. '+source+'</p><p>'+e(row.get('notes') or 'The listed portion is a source snapshot, not a guarantee of local availability.')+'</p><p>Carbs: '+secondary('c')+' · Fat: '+secondary('fat')+'</p></details><a class="text-action home-menu-action" href="'+e(guide)+'">View order '+ARROW+'</a></article>'
def featured(rows):
 eligible=[r for r in rows if r.get('cal') is not None and r.get('p') is not None and r.get('source') and r.get('category') not in ['component','drink','side'] and r.get('cal',0)>=180]
 preferred=[('Chick-fil-A','Grilled Chicken Sandwich'),('Chipotle','High Protein-High Fiber Bowl'),('CAVA','Greek Salad bowl'),('Panda Express','Grilled Teriyaki Chicken'),('Tim Hortons','Egg & Cheese English Muffin'),('Harvey’s','Grilled Chicken Sandwich'),('A&W Canada','Teen Burger™')]
 choices=[]
 for chain,name in preferred:
  item=next((r for r in eligible if r['chain']==chain and r['name']==name),None)
  if item and len(choices)<4:choices.append(item)
 # Give chains a place before repeating one, then diversify the order name.
 for chain in dict.fromkeys(r['chain'] for r in eligible):
  if len(choices)>=4:break
  if any(r['chain']==chain for r in choices):continue
  candidate=next((r for r in eligible if r['chain']==chain and r.get('p',0)>=15),None) or next(r for r in eligible if r['chain']==chain)
  choices.append(candidate)
 for item in eligible:
  if len(choices)>=4:break
  if item not in choices:choices.append(item)
 return choices
def home(info,code,rows,scene):
 finder=info['finder'];directory=info['restaurants'];query='?market='+code
 chosen=featured(rows)
 cards=''.join(menu_card(r,code,info) for r in chosen)
 if len(chosen)<4:cards+='<article class="home-menu-card home-menu-alternative">'+character('egg')+'<h3>A little more to explore.</h3><p>The published selection is smaller here. Check each local serving and source.</p><a class="text-action" href="'+directory+'">Browse local menus '+ARROW+'</a></article>'
 chains=list(dict.fromkeys(r['chain'] for r in rows if r.get('category')!='component'))
 shortcuts=''.join('<a class="restaurant-shortcut" href="'+finder+'?'+e(urlencode({'chain':chain}))+'"><span class="shortcut-mark" aria-hidden="true">'+ARROW+'</span><span>'+e(chain)+'</span></a>' for chain in chains[:8])
 return '<main id="main-content" class="market-home" data-home-template="shared-market-v1" data-home-market="'+code+'">'+'''<section class="food-hero container"><div class="hero-copy"><h1>Find a meal<br>that fits.</h1><p>Compare restaurant meals by calories, protein, carbs and fat.</p><form class="home-finder-entry" action="'''+finder+'''" method="get"><label>Calories, up to<input name="maxCal" type="number" inputmode="numeric" min="150" max="2500" placeholder="Any"></label><label>Protein, at least (g)<input name="minProtein" type="number" inputmode="numeric" min="0" max="200" placeholder="Any"></label><button class="btn btn-primary" type="submit">Find my meal '''+ARROW+'''</button></form><a class="text-action" href="'''+directory+'">Browse restaurants '+ARROW+'</a><p class="home-market-note">'+e(info['name'])+' menus · <a href="/world-restaurant-menus.html">Change country</a></p></div>'+scene+'</section><section class="home-menu-section container"><header class="section-heading"><h2>On the menu</h2><a class="text-action" href="'+finder+'">See all meals '+ARROW+'</a></header><div class="home-menu-grid">'+cards+'</div><p class="home-data-note">'+e(info['name'])+' source servings. Sides, drinks and changes are included only when listed.</p></section><section class="home-restaurants container"><header class="section-heading"><h2>Your usual spot?</h2><a class="text-action" href="'+directory+'">All restaurants '+ARROW+'</a></header><div class="home-restaurant-shortcuts">'+shortcuts+'</div></section>'+'''
<section class="home-notebook container"><div>'''+character('broccoli')+'''<div><h2>A little notebook.<br>For what you actually ate.</h2><p>Check a portion. Log your food. Keep it on this device.</p><a class="btn btn-primary" href="/food-diary.html'''+query+'">Add food '+ARROW+'''</a></div></div><nav aria-label="Food tools"><a href="/food-library.html'''+query+'"><span>Look up a food</span><small>Ingredients and source-defined portions.</small>'+ARROW+'</a><a href="/calculators.html'+query+'"><span>Find your daily macros</span><small>An adult calorie and macro estimate.</small>'+ARROW+'</a><a href="/recipe-macro-scaler.html'+query+'"><span>Recipe portions</span><small>The whole recipe, divided clearly.</small>'+ARROW+'</a><a href="/protein-value-calculator.html'+query+'"><span>Compare protein value</span><small>Use your own prices and currency.</small>'+ARROW+'''</a></nav></section>
<section class="home-reading container"><header class="section-heading"><h2>At the reading table.</h2><a class="text-action" href="/articles.html'''+query+'">Learn '+ARROW+'</a></header><div class="home-reading-layout"><a class="reading-feature" href="/how-to-read-a-nutrition-label.html"><span class="reading-feature-art" aria-hidden="true">'+character('avocado')+'<span class="label-art"><b>Nutrition facts</b><i></i><i></i><i></i></span></span><h3>Make sense of a food label.</h3><p>Serving size, nutrients and the numbers to compare.</p></a><div class="reading-links"><a href="/compare-menu-ingredients-worldwide.html">Same name. Different country.'+ARROW+'</a><a href="/raw-vs-cooked-food-weight.html">Raw or cooked weight?'+ARROW+'</a><a href="/sources.html">Where our numbers come from'+ARROW+'</a></div></div></section><section class="home-play container"><div class="home-play-copy">'+character('strawberry')+'<div><h2>Food for the fun of it.</h2><p>A quiet puzzle. A familiar face.</p><a class="text-action" href="/play.html'+query+'">Make a little time to play '+ARROW+'</a></div></div><div class="home-play-links"><a href="/play-market-memory.html">Market Memory '+ARROW+'</a><a href="/play-fruit-catch.html">Fruit Catch '+ARROW+'</a><a href="/play-build-a-plate.html">Build-a-Plate '+ARROW+'</a></div></section></main>'
def controls(markets,current):
 options=''.join('<li><a href="'+v['home']+'" data-country-choice="'+code+'"'+(' aria-current="true"' if code==current else '')+'><span class="country-flag" aria-hidden="true"><svg viewBox="0 0 30 20"><use href="/images/market-flags.svg#flag-'+code+'"/></svg></span><span>'+e(v['name'])+'</span><svg class="country-selected-mark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="m5 12 4 4 10-10"/></svg></a></li>' for code,v in markets.items())
 return '<!-- market-controls:start --><details class="country-picker"><summary aria-label="Restaurant country: '+e(markets[current]['name'])+'. Choose country"><span class="country-flag" data-country-flag aria-hidden="true"><svg viewBox="0 0 30 20"><use data-market-flag href="/images/market-flags.svg#flag-'+current+'"/></svg></span><span data-country-name>'+e(markets[current]['name'])+'</span></summary><nav class="country-panel" aria-label="Restaurant country"><p class="country-panel-title">Where are you ordering?</p><label class="country-search" hidden>Find a country<input type="search" data-country-search autocomplete="off"></label><ul>'+options+'</ul><a class="country-coverage-link" href="/world-restaurant-menus.html">See menu coverage '+ARROW+'</a></nav></details><details class="language-picker"><summary aria-label="Interface language: English">English</summary><div class="language-panel"><strong>Interface language</strong><p class="language-current"><span>English</span>'+ARROW+'</p><p>More languages will appear when translations are reviewed.</p></div></details><!-- market-controls:end -->'
def appearance():return '<details class="appearance-picker"><summary aria-label="Appearance: light mode">'+SUN+MOON+'<span data-appearance-current>Light</span></summary><div class="appearance-panel"><p>Appearance</p><div class="theme-segment" role="group" aria-label="Color theme"><button type="button" data-theme-choice="light" aria-pressed="true">'+SUN+'<span>Light</span></button><button type="button" data-theme-choice="dark" aria-pressed="false">'+MOON+'<span>Dark</span></button></div><label><input type="checkbox" data-calm-motion> Calm motion</label></div></details>'
def reconcile_shell(markets):
 from site_scope import KEEP_ROOT_HTML
 paths=list(ROOT.glob('*.html'))+[p for code in markets if code!='US' for p in (ROOT/code.lower()/'en').rglob('*.html')]
 for p in paths:
  text=p.read_text(encoding='utf-8');code=next((k for k in markets if k!='US' and p.relative_to(ROOT).as_posix().startswith(k.lower()+'/en/')),'US')
  text=re.sub(r'<!-- market-controls:start -->.*?<!-- market-controls:end -->',lambda _:controls(markets,code),text,flags=re.S)
  text=element_replace(text,'appearance-picker',appearance())
  def error_semantics(m):
   return m[0] if re.search(r'\brole=',m[2]) else '<'+m[1]+m[2]+' role="alert">'
  text=re.sub(r'<(div|p)([^>]*class="[^"]*\berror-msg\b[^"]*"[^>]*)>',error_semantics,text)
  learn='<div class="nav-group"><button class="nav-group-trigger" type="button" aria-expanded="false">Learn</button><div class="nav-popover nav-learning"><a data-market-context="true" href="/articles.html"><strong>All guides</strong></a><div class="nav-topic-grid">'+''.join('<a href="/articles.html#learn-'+slug+'">'+label+'</a>' for slug,label in [('eating-out','Eating out'),('breakfast','Breakfast'),('coffee-drinks','Coffee &amp; drinks'),('meal-comparisons','Meal comparisons'),('protein-value','Protein &amp; value'),('portions-labels','Portions &amp; labels')])+'</div><a href="/food-library.html"><strong>Food library</strong></a><a href="/play.html"><strong>Food puzzles &amp; games</strong></a><a href="/read-and-watch.html"><strong>Read &amp; watch</strong></a><a href="/sources.html"><strong>Sources &amp; methods</strong></a></div></div>'
  text=re.sub(r'<div class="nav-group"><button class="nav-group-trigger"[^>]*>Learn</button><div class="nav-popover(?: nav-learning)?">.*?</div></div>',lambda _:learn,text,flags=re.S)
  # Server-rendered links must already target the explicit market. JavaScript
  # enhancement also handles a saved preference on global utility pages.
  def local_link(match):
   tag=match[0]
   kind=re.search(r'data-market-route="([^"]+)"',tag)
   if kind and kind[1] in markets[code]:
    tag=re.sub(r'href="[^"]*"','href="'+markets[code][kind[1]]+'"',tag)
   elif code!='US' and 'data-market-context="true"' in tag:
    tag=re.sub(r'href="/?([^"?#]+)(?:\?market=[A-Z]+)?"',lambda h:'href="/'+h[1]+'?market='+code+'"',tag)
   if 'data-market-only=' in tag:
    only=re.search(r'data-market-only="([^"]+)"',tag)[1]
    tag=re.sub(r'\s+hidden(?:="[^"]*")?','',tag)
    if only!=code:tag=tag[:-1]+' hidden>'
   return tag
  text=re.sub(r'<a\b[^>]*>',local_link,text)
  # Current header labels should remain full names; enhanced links retain context.
  text=text.replace('class="mobile-menu-title">A little help<br>with food.','class="mobile-menu-title">Make yourself<br>at home.')
  write(p,text)
def games():
 catalogue=json.loads((ROOT/'js/play-catalogue.json').read_text(encoding='utf-8'))
 family_map={'Numbers & labels':'numbers','Meal decisions':'kitchen','Coordination':'orchard','Memory & observation':'memory','Spatial puzzles':'logic','Words & knowledge':'words','Creative studio':'studio','Advanced puzzles':'logic'}
 for item in catalogue:
  p=ROOT/item['route'];text=p.read_text(encoding='utf-8');family=family_map.get(item['category'],'logic')
  text=re.sub(r'<main id="main-content" class="play-page container"(?: data-play-family="[^"]*")?','<main id="main-content" class="play-page container" data-play-family="'+family+'"',text)
  text=re.sub(r'<!-- master-game-entry:start -->.*?<!-- master-game-entry:end -->','',text,flags=re.S)
  head=Document(text).find(cls='play-head')
  if head:
   entry='<div class="play-family-entry"><svg class="play-family-art" viewBox="0 0 160 90" aria-hidden="true"><use href="/images/game-family-motifs.svg#game-'+family+'"/></svg><span>'+e(item['category'])+'</span></div>'
   text=text[:head['end']]+'<!-- master-game-entry:start -->'+entry+'<!-- master-game-entry:end -->'+text[head['end']:]
  text=text.replace('Touch the controls or use Tab and Enter. There is no time limit or mandatory sound. Pause at any point; restarting repeats this puzzle and New puzzle changes its seed.','Use touch or Tab and Enter. Restart repeats the puzzle; New puzzle changes it. There is no timer or mandatory sound.')
  write(p,text)
 p=ROOT/'play.html';text=p.read_text(encoding='utf-8')
 for category,family in family_map.items():
  slug=category.lower().replace(' & ','-').replace(' ','-')
  text=text.replace('<details id="'+slug+'"','<details data-play-family="'+family+'" id="'+slug+'"')
 text=re.sub(r'<!-- master-game-art:start -->.*?<!-- master-game-art:end -->','',text,flags=re.S)
 for n in sorted([n for n in Document(text).nodes if 'play-game-link' in n['attrs'].get('class','').split()],key=lambda n:n['inner'],reverse=True):
  route=n['attrs']['href'];item=next(i for i in catalogue if i['route']==route);family=family_map.get(item['category'],'logic')
  art='<!-- master-game-art:start --><svg class="play-family-art" viewBox="0 0 160 90" aria-hidden="true"><use href="/images/game-family-motifs.svg#game-'+family+'"/></svg><!-- master-game-art:end -->'
  text=text[:n['inner']]+art+text[n['inner']:]
 text=text.replace('Untimed · touch &amp; keyboard','Touch &amp; keyboard').replace('Small puzzles, good company. Make something, solve something, or take a little break.','A quiet puzzle, a familiar face, a little time to play.')
 text=text.replace('56 original games. No account, reaction timer or mandatory sound. Nutrition examples are labeled; games are for play and learning, not dietary prescriptions.','No account, timer or mandatory sound. Nutrition examples are fictional where labeled; games are not dietary prescriptions.')
 write(p,text)
def build():
 markets=countries();registry=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
 original=(ROOT/'index.html').read_text(encoding='utf-8');ensemble=Document(original).find(cls='food-ensemble');scene=absolute(original[ensemble['start']:ensemble['end']]);scene=scene.replace('aria-label="Original egg, strawberry and broccoli characters"','aria-hidden="true"')
 manifest=[]
 for code,info in markets.items():
  p=market_file(info);text=p.read_text(encoding='utf-8');rows=[r for r in registry if r['market']==code];main=next(n for n in Document(text).nodes if n['tag']=='main');text=text[:main['start']]+home(info,code,rows,scene)+text[main['end']:]
  text=re.sub(r'data-family="[^"]*"','data-family="home"',text);text=absolute(text)
  title='Find restaurant meals in '+info['name']+' | GetMacros';description='Compare '+info['name']+' restaurant meals by calories and protein. Check exact servings, official sources and available macros, then log food privately.'
  text=re.sub(r'<title>.*?</title>','<title>'+e(title)+'</title>',text,count=1,flags=re.S)
  for key,value in [('description',description),('og:title',title),('og:description',description),('twitter:title',title),('twitter:description',description)]:text=re.sub(r'(<meta (?:name|property)="'+re.escape(key)+'" content=")[^"]*',lambda m:m[1]+e(value),text,count=1)
  def schema(match):
   value=json.loads(match[1])
   if value.get('@type')=='WebSite':value['description']='Compare country-specific restaurant meals, check source-defined portions and keep a private food diary.'
   return '<script type="application/ld+json">'+json.dumps(value,ensure_ascii=False,separators=(',',':'))+'</script>'
  text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,text,flags=re.S)
  # The direct entry is native GET navigation, so no full food dataset is loaded.
  text=re.sub(r'<script[^>]*src="/?js/(?:meal-data|meal-provenance|meal-engine|meal-view|meal-guide|meal-finder|home-calculator)\.js[^>]*>\s*</script>','',text)
  write(p,text);manifest.append({'market':code,'route':info['home'],'template':'shared-market-v1','featured':[{'id':r.get('id'),'chain':r['chain'],'name':r['name'],'market':code,'cal':r['cal'],'p':r['p'],'serving':r.get('serving'),'source':r['source']} for r in featured(rows)],'chainCount':len({r['chain'] for r in rows})})
 reconcile_shell(markets);games()
 from build_edition_css import build as css_build
 css_build()
 (ROOT/'css/play-release.css').write_text((ROOT/'tools/play-release.css').read_text(encoding='utf-8'),encoding='utf-8')
 OUT.mkdir(parents=True,exist_ok=True);write(OUT/'homepage-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print('Shared homepage architecture for',len(markets),'markets; crawlable country links; complete appearance choices; existing game families refined.')
if __name__=='__main__':build()
