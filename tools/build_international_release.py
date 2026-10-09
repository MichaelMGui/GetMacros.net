"""Publish reviewed markets; never manufacture a country from a flag or a name."""
from pathlib import Path
from html import escape,unescape
from urllib.parse import urlsplit
import csv,json,re,subprocess,xml.etree.ElementTree as ET
from normalize_calculator_layouts import Document
from site_scope import KEEP_ROOT_HTML
ROOT=Path(__file__).resolve().parents[1]
BASE='https://getmacros.net'
DATE='2026-10-09'
DATA=json.loads((ROOT/'tools/international/records.json').read_text(encoding='utf-8'))
MEALS=DATA['records']
for r in MEALS:
 r['t']=[key for key,passed in [('protein',r['p'] is not None and r['p']>=25),('light',r['cal'] is not None and r['cal']<=400),('energy',r['cal'] is not None and r['cal']>=600),('fibre',r['f'] is not None and r['f']>=5),('lowsodium',r['na'] is not None and r['na']<=600)] if passed]
PAGES=[]
def e(s):return escape(str(s),quote=True)
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def write(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def replace_node(text,cls,value):
 n=Document(text).find(cls=cls)
 return text[:n['start']]+value+text[n['end']:] if n else text
def root_links(text):
 return re.sub(r'\b(href|src|action)="((?!https?:|//|/|#|mailto:|tel:|data:)[^"]+)"',lambda m:m[1]+'="/'+m[2]+'"',text)
def flag_controls():
 us='<svg data-flag-us viewBox="0 0 28 20" aria-hidden="true"><path fill="#fff" d="M0 0h28v20H0z"/><path fill="#ad3140" d="M0 0h28v3H0zm0 6h28v3H0zm0 6h28v3H0zm0 6h28v2H0z"/><path fill="#284574" d="M0 0h12v11H0z"/><path fill="#fff" d="m6 2 1 2 2 .3-1.5 1.5.4 2.2L6 7l-1.9 1 .4-2.2L3 4.3 2-.3z"/></svg>'
 ca='<svg data-flag-ca viewBox="0 0 28 20" aria-hidden="true" hidden><path fill="#fff" d="M0 0h28v20H0z"/><path fill="#b32a34" d="M0 0h6v20H0zm22 0h6v20h-6zM14 3l2 4 2-1-1 4 3-1-1 4-4 2 .5 3h-3l.5-3-4-2-1-4 3 1-1-4 2 1z"/></svg>'
 return '<details class="country-picker"><summary><span class="country-flag" data-country-flag>'+us+ca+'</span><span data-country-name>United States</span></summary><div class="country-panel"><form data-country-form><label>Restaurant market<select data-country-select><option value="US">United States</option><option value="CA">Canada</option></select></label><button class="btn btn-primary" type="submit">Apply country</button></form><p>Changes menus, orders and official sources. Canada currently covers A&amp;W, Harvey’s and Tim Hortons; not their entire menus.</p><p><a href="/ca/en/menu-sources/">Canadian coverage &amp; updates</a></p></div></details><details class="language-picker"><summary>English</summary><div class="language-panel"><p>Content language</p><ul><li>English — current language</li><li>French — unavailable until reviewed</li></ul><p>Language and restaurant country are separate. Choosing Canada does not translate a U.S. menu.</p></div></details>'
def shared():
 from refine_content_value import finder_methodology
 from build_restaurant_pages import parse_meals
 restaurant_routes={m['url'] for m in parse_meals()}
 finder_methodology()
 # The shared source is updated, and late generation reconciles all active output.
 header=ROOT/'tools/market-header.inc';s=header.read_text(encoding='utf-8')
 s=re.sub(r'<!-- market-controls:start -->.*?<!-- market-controls:end -->','',s,flags=re.S)
 s=s.replace('<div class="nav-utility">','<div class="nav-utility"><!-- market-controls:start -->'+flag_controls()+'<!-- market-controls:end -->',1)
 for target in ['calculators.html','articles.html','blog.html','food-shelf.html','search.html']:
  s=re.sub(r'<a([^>]*?)href="'+re.escape(target)+r'"',lambda m:'<a'+re.sub(r'\sdata-market-context="[^"]*"','',m[1])+'data-market-context="true" href="'+target+'"',s)
 for target,kind in [('index.html','home'),('restaurant-meal-finder.html','finder'),('restaurant-meal-guides.html','restaurants'),('healthy-fast-food.html','collection')]:
  s=re.sub(r'<a([^>]*?)href="'+re.escape(target)+r'"',lambda m:'<a'+re.sub(r'\sdata-market-route="[^"]*"','',m[1])+'data-market-route="'+kind+'" href="'+target+'"',s)
 header.write_text(s,encoding='utf-8')
 footer=(ROOT/'tools/market-footer.inc').read_text(encoding='utf-8')
 logo=re.search(r'<span class="brand-mark"[^>]*>(.*?)</span>',(ROOT/'index.html').read_text(encoding='utf-8'),re.S)[1]
 s=s.replace('__LOGO__',logo)
 for route in sorted(KEEP_ROOT_HTML):
  p=ROOT/route;text=p.read_text(encoding='utf-8');text=replace_node(text,'market-header',s);text=replace_node(text,'market-footer',footer)
  # Keep the detailed comparison once, instead of repeating it above the tool.
  doc=Document(text);head=next((n for n in doc.nodes if any(c in n['attrs'].get('class','').split() for c in ['market-page-head','guide-masthead'])),None)
  if head and route in restaurant_routes:
   paragraphs=[n for n in doc.nodes if n['tag']=='p' and 'end' in n];original=text
   for n in reversed(paragraphs):
    if head['start']<n['start']<head['end']:
     value=unescape(re.sub('<[^>]+>','',original[n['start']:n['end']])).strip()
     if len(value)>100 and any(x['start']>head['end'] and unescape(re.sub('<[^>]+>','',original[x['start']:x['end']])).strip().startswith(value) for x in paragraphs):
      text=text[:n['start']]+text[n['end']:]
  # Some game generators clone the homepage; market alternates must not leak.
  text=re.sub(r'<link rel="alternate" hreflang="en-(?:CA|US)"[^>]*>','',text)
  scope='US' if route in restaurant_routes or route in ['index.html','restaurant-meal-finder.html','restaurant-meal-guides.html','healthy-fast-food.html'] or 'healthy-meals-macros' in route or 'nutrition-guide' in route or 'healthy-breakfast-macros' in route else 'global'
  text=re.sub(r'\sdata-market-scope="[^"]*"','',text);text=text.replace('<html ','<html data-market-scope="'+scope+'" ',1)
  text=re.sub(r'<(?:script|link)\b[^>]*(?:src|href)="/?(?:js/markets.js|css/markets.css)(?:\?[^"]*)?"[^>]*>(?:</script>)?','',text)
  text=text.replace('</head>','<link rel="stylesheet" href="css/markets.css"><script src="js/markets.js" defer></script></head>')
  write(route,text)
def page(route,title,desc,body,scripts=(),family='guide',equivalent=None):
 template=(ROOT/'about.html').read_text(encoding='utf-8');n=next(n for n in Document(template).nodes if n['tag']=='main');main='<main id="main-content" class="container"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/ca/en/">Canada</a> / '+e(title)+'</nav>'+body+'</main>'
 text=template[:n['start']]+main+template[n['end']:];canonical=BASE+route;fulltitle=title+' | GetMacros Canada'
 text=re.sub('<title>.*?</title>','<title>'+e(fulltitle)+'</title>',text,flags=re.S,count=1)
 for attr,key,value in [('name','description',desc),('property','og:title',fulltitle),('property','og:description',desc),('property','og:url',canonical),('name','twitter:title',fulltitle),('name','twitter:description',desc)]:
  text=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*',lambda m:m[1]+e(value),text,count=1)
 text=re.sub('<link rel="canonical" href="[^"]*">','<link rel="canonical" href="'+canonical+'">',text,count=1)
 text=re.sub(r'<script type="application/ld\+json">.*?</script>','',text,flags=re.S)
 text=text.replace('data-market-scope="global"','data-market-scope="CA"').replace('lang="en"','lang="en-CA"')
 text=root_links(text)
 text=text.replace('data-family="trust"','data-family="'+family+'"').replace('recovery-page about-page','market-country-page')
 if 'data-order-tool=' in body:text=text.replace('</head>','<link rel="stylesheet" href="/css/growth-tools.css"></head>')
 # Header and footer carry crawlable market links even without script execution.
 for a,b in [('/index.html','/ca/en/'),('/restaurant-meal-finder.html','/ca/en/find-a-meal/'),('/restaurant-meal-guides.html','/ca/en/restaurants/'),('/healthy-fast-food.html','/ca/en/collections/protein-meals/')]:text=text.replace('href="'+a+'"','href="'+b+'"')
 for target in ['calculators.html','articles.html','blog.html','food-shelf.html','search.html']:
  text=text.replace('href="/'+target+'"','href="/'+target+'?market=CA"')
 text=text.replace('data-country-name>United States','data-country-name>Canada').replace('data-flag-us viewBox','data-flag-us hidden viewBox').replace('aria-hidden="true" hidden><path fill="#fff"','aria-hidden="true"><path fill="#fff"')
 text=re.sub(r'<a([^>]*data-market-only="(US|CA)"[^>]*)>',lambda m:'<a'+re.sub(r'\s+hidden(?:="[^"]*")?','',m[1])+(' hidden' if m[2]=='US' else '')+'>',text)
 text=text.replace('© 2026 GetMacros · U.S. menus','© 2026 GetMacros · Canadian selection')
 text=text.replace('GetMacros · U.S. menus','GetMacros · Canadian selection')
 text=re.sub(r'<script[^>]*src="/?js/(?:food-shelf|search-meals)\.js[^>]*>\s*</script>','',text)
 added=''.join('<script src="/js/'+name+'" defer></script>' for name in scripts);text=text.replace('</body>',added+'</body>')
 crumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Canada','item':BASE+'/ca/en/'},{'@type':'ListItem','position':2,'name':title,'item':canonical}]}
 if route=='/ca/en/':crumbs['itemListElement']=crumbs['itemListElement'][:1]
 text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(crumbs,ensure_ascii=False,separators=(',',':'))+'</script></head>')
 if equivalent:
  annotations='<link rel="alternate" hreflang="en-CA" href="'+canonical+'"><link rel="alternate" hreflang="en-US" href="'+BASE+equivalent+'">'
  text=text.replace('</head>',annotations+'</head>');p=ROOT/('index.html' if equivalent=='/' else equivalent.lstrip('/'));s=p.read_text(encoding='utf-8');s=re.sub(r'<link rel="alternate" hreflang="en-(?:CA|US)"[^>]*>','',s);write(p.relative_to(ROOT).as_posix(),s.replace('</head>',annotations+'</head>'))
 path=route.strip('/')+'/index.html';write(path,text);PAGES.append(dict(route=route,path=path,title=title,description=desc,template=family,market='CA',language='en',lastmod=DATE))
def intro(title,lead):return '<section class="market-page-head"><h1>'+e(title)+'</h1><p class="market-intro">'+lead+'</p></section>'
def links(items,primary=False):return '<nav class="market-links" aria-label="Related tasks">'+''.join('<a class="'+('btn btn-primary' if primary and i==0 else 'text-action')+'" href="'+u+'">'+t+' →</a>' for i,(u,t) in enumerate(items))+'</nav>'
def table(rows,caption):
 return '<p class="table-scroll-note">Scroll sideways to compare all nutrients.</p><div class="table-wrap" role="region" aria-label="Canadian nutrition comparison" tabindex="0"><table class="market-table"><caption>'+caption+'</caption><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in ['Exact item / serving','kcal','Protein (g)','Carbs (g)','Fat (g)','Fibre (g)','Sodium (mg)'])+'</tr></thead><tbody>'+''.join('<tr><th scope="row"><a href="'+r['source']+'">'+e(r['chain']+' — '+r['name'])+'</a><small>'+e(r['serving'])+'</small></th>'+''.join('<td>'+('Unknown' if r[k] is None else f'{r[k]:g}')+'</td>' for k in ['cal','p','c','fat','f','na'])+'</tr>' for r in rows)+'</tbody></table></div>'
def choose(chain,name):return next(r for r in MEALS if r['chain']==chain and r['name']==name)
def tool(id,mode,title):
 return '<section class="growth-tool" id="'+id+'" data-order-tool="'+mode+'"><h2>'+title+'</h2><p>Exact Canadian portions, with source links. Unknown values stay unknown.</p><button class="btn btn-primary" type="button" data-order-load>Open '+('order builder' if mode=='builder' else 'drink comparison')+'</button><p role="status" data-order-status></p><div data-order-workspace hidden></div><noscript><p>The interactive tool needs JavaScript. The source-linked comparison above remains readable.</p></noscript></section>'
def data():
 # Add subsequent source reviews without erasing the original inspection trail.
 from meal_provenance import read,pack
 proof_path=ROOT/'js/meal-provenance.js';proof=read(proof_path)
 catalogue=json.loads((ROOT/'js/order-catalogue.json').read_text(encoding='utf-8'))
 for r in catalogue['records']:
  if r['isNew'] or r.get('baselineKey') not in proof:continue
  p=proof[r['baselineKey']]
  p['sourceReview']={'reviewedAt':r['source']['checkedAt'],'source':r['source']['url'],'method':'official full nutrition table reviewed','fields':['cal','p','c','fat','f','na'],'serving':r['portion']['label']}
  p['checked']=r['source']['checkedAt']
  p['notes']='Full official table rechecked '+r['source']['checkedAt']+'. Original per-nutrient source dates are retained below; this later review does not establish a recipe publication date.'
 write('js/meal-provenance.js',pack(proof))
 # Existing U.S. identity and source dates are retained, not recertified today.
 script="const fs=require('fs'),vm=require('vm'),s={window:{}};vm.createContext(s);for(const f of ['meal-data','meal-provenance'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);console.log(JSON.stringify(s.window.GM_MEALS));"
 rows=json.loads(subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True,check=True,encoding='utf-8').stdout)
 fats={r['chain']+'||'+r['name']:r.get('fat') for r in rows};p=ROOT/'js/meal-data.js';s=p.read_text(encoding='utf-8');s=re.sub(r'/\* market-model:start \*/.*?/\* market-model:end \*/','',s,flags=re.S)
 s+='\n/* market-model:start */\n(function(){const fats='+json.dumps(fats,ensure_ascii=False,separators=(',',':'))+';window.GM_MEALS.forEach(m=>{m.market="US";m.country="US";m.fat=fats[m.chain+"||"+m.name]??null;});})();\n/* market-model:end */\n';write('js/meal-data.js',s)
 for r in rows:r.update(market='US',country='US',restaurantId=slug(r['chain']),units={'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg'},retrievedAt=r.get('checked'),sourceDate=r.get('sourceDate'),verificationStatus=r.get('verificationStatus','legacy-source-record; not reverified for the Canadian launch'),conversions=[])
 # Keep new and reverified U.S. component records without duplicate identities.
 catalogue=json.loads((ROOT/'js/order-catalogue.json').read_text(encoding='utf-8'))
 for r in catalogue['records']:
  n=r['nutrients'];row=dict(id=r['id'] if r['isNew'] else r.get('baselineKey'),chain=r.get('restaurant',r.get('chain')),name=r['name'],market='US',country='US',region='U.S.',serving=r['portion']['label'],source=r['source']['url'],checked=r['source']['checkedAt'],sourceDate=None,category=r['category'],notes=' '.join(r.get('notes',[])) if isinstance(r.get('notes'),list) else r.get('notes',''),url='/chick-fil-a-healthy-meals-macros.html',cal=n['calories'],p=n['proteinG'],c=n['carbsG'],fat=n['fatG'],f=n['fiberG'],na=n['sodiumMg'],sugar=n['totalSugarG'],verificationStatus='official-table-reviewed',retrievedAt=r['source']['checkedAt'],units={'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g'},conversions=[])
  if r['isNew']:rows.append(row)
  else:
   at=next((i for i,m in enumerate(rows) if m['chain']+'||'+m['name']==r.get('baselineKey')),None)
   if at is not None:rows[at].update(row)
 for r in rows+MEALS:
  r['restaurantMarketId']=r['country']+'|'+r.get('restaurantId',slug(r['chain']))
  r['nutrientBasis']='per named serving'
 write('js/order-registry.json',json.dumps({'markets':['US','CA'],'records':rows+MEALS},ensure_ascii=False,separators=(',',':'))+'\n')
 write('js/canada-meals.json',json.dumps(DATA,ensure_ascii=False,separators=(',',':'))+'\n')
 write('js/canada-meals.js','/* Reviewed Canadian selection; original source editions are retained. */\nwindow.GM_MEALS='+json.dumps(MEALS,ensure_ascii=False,separators=(',',':'))+';\nwindow.GM_THRESHOLDS={protein:25,energy:600,light:400,fibre:5,sodium:600};\n')
def build_pages():
 common=[('/ca/en/find-a-meal/','Find a Canadian meal'),('/ca/en/restaurants/','Browse Canadian restaurants'),('/ca/en/tools/complete-order/','Build a complete order')]
 body=intro('Find a meal in Canada.','Compare actual Canadian servings from A&amp;W, Harvey’s and Tim Hortons. Start with calories and protein; check the whole order before deciding.')+links(common,primary=True)
 body+='<section class="market-section"><h2>A few places to start</h2>'+table([choose('Tim Hortons','Egg & Cheese English Muffin'),choose('A&W Canada','Teen Burger™'),choose('Harvey’s','Grilled Chicken Sandwich')],'Canadian source servings. These are individual items, not meals with a side and drink.')+'</section>'+links([('/ca/en/collections/breakfast/','Compare breakfasts'),('/ca/en/collections/protein-meals/','Compare protein and sodium'),('/ca/en/tools/drink-comparison/','Compare drinks')])+'<p class="country-coverage">A tracked selection, not a full-menu audit. McDonald’s Canada is awaiting complete source verification; U.S. McDonald’s records are not shown here.</p>'
 page('/ca/en/','Canadian fast-food meals','Find Canadian restaurant meals with explicit portions, calories, protein and official Canadian nutrition sources.',body,family='home',equivalent='/')
 dirs=''
 for chain in sorted({r['chain'] for r in MEALS}):
  rows=[r for r in MEALS if r['chain']==chain];dirs+='<article><h2><a href="/ca/en/restaurants/'+slug(chain)+'/">'+e(chain)+'</a></h2><p>'+str(len(rows))+' source-checked items, drinks and sides. Individual portions; not an audited full menu.</p><a class="text-action" href="/ca/en/find-a-meal/?chain='+__import__('urllib.parse',fromlist=['quote']).quote(chain)+'">Browse these items →</a></article>'
 page('/ca/en/restaurants/','Canadian restaurant nutrition guides','Browse source-backed Canadian guides for Tim Hortons, A&W Canada and Harvey’s, with explicit serving and coverage limits.',intro('Restaurants in Canada.','Choose a chain to compare its Canadian servings and build the order you actually want.')+'<div class="market-directory">'+dirs+'</div>'+links([('/ca/en/menu-sources/','Sources and coverage'),('/restaurant-meal-guides.html','U.S. restaurant directory')]),family='restaurant-index',equivalent='/restaurant-meal-guides.html')
 for chain in sorted({r['chain'] for r in MEALS}):
  rows=[r for r in MEALS if r['chain']==chain];head={'Tim Hortons':'Compare breakfast sandwiches, wraps and named latte sizes using the July 2026 Canadian edition. Drink totals include the listed recipe; milk and syrup changes need their own verified values.','A&W Canada':'Compare the standard burger build with breakfast, sides and named drinks. Ingredient names come from the Canadian menu, but individual ingredient quantities are not available for subtraction.','Harvey’s':'Compare the listed burger or chicken serving first, then add the side and separately selected sauces. Garnish quantities and custom builds need their own information; do not assume a plain sandwich and a dressed order have the same total.'}[chain]
  body=intro(chain+' nutrition in Canada.',head)+links([('/ca/en/find-a-meal/?chain='+__import__('urllib.parse',fromlist=['quote']).quote(chain),'Filter '+e(chain)),('/ca/en/tools/complete-order/','Build an order')])+table(rows,f'{len(rows)} tracked Canadian items. Source editions and recipes apply; local availability is not guaranteed.')+'<details class="market-section"><summary>Portions, ingredients and source limits</summary><p>'+e(rows[0]['notes'])+'</p><p>We do not certify allergens or dietary suitability. Confirm ingredients and preparation with the restaurant. Source retrieval and edition dates are separate.</p><p><a href="'+rows[0].get('sourceParent',rows[0]['source'])+'">Official Canadian nutrition source</a> · Retrieved and reviewed October 9, 2026.</p></details>'+links([('/ca/en/menu-sources/','Coverage and update history'),('/protein-value-calculator.html?market=CA','Use your Canadian receipt prices')])
  page('/ca/en/restaurants/'+slug(chain)+'/',chain+' Canadian nutrition',f'Compare exact {chain} Canadian servings, calories, protein, carbs, fat, fibre and sodium, with official sources and clear limitations.',body,family='restaurant')
 # Static results use the same engine/view as the interactive finder.
 script="const fs=require('fs'),vm=require('vm'),s={window:{}};vm.createContext(s);for(const f of ['canada-meals','meal-engine','meal-view'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);const E=s.window.GetMacrosMeals,V=s.window.GetMacrosMealView,all=s.window.GM_MEALS,state=E.normalize({},all),matches=E.results(all,state);console.log(V.shell(all,state,E,{rows:matches.slice(0,12).map(m=>V.card(m,all.indexOf(m))).join(''),count:matches.length}));"
 markup=subprocess.run(['node','-e',script],cwd=ROOT,capture_output=True,text=True,check=True,encoding='utf-8').stdout
 body=intro('Canadian restaurant meal finder','Compare Canadian main items, breakfast, sides and drinks by their listed portions. A match meets your limits; use the order builder to add your whole meal.')+'<section id="meal-quiz" class="meal-finder-workspace">'+markup+'</section><noscript><p>Filters need JavaScript. Browse the source-linked Canadian restaurant tables instead.</p></noscript>'
 page('/ca/en/find-a-meal/','Canadian restaurant meal finder','Filter Canadian restaurant orders by calories, protein, fibre and sodium. Compare exact portions without substituting U.S. menus.',body,scripts=['canada-meals.js','meal-engine.js','meal-view.js','order-tools-core.js','order-notebook.js','order-share.js','meal-guide.js','meal-finder.js'],family='finder',equivalent='/restaurant-meal-finder.html')
 breakfast=[r for r in MEALS if r['category']=='breakfast']
 body=intro('Canadian fast-food breakfasts.','Compare the sandwich or wrap first, then count the coffee and side you order with it. More protein and fewer calories do not always point to the same choice.')+table(breakfast,'Standard breakfast servings. A&W: current Canadian panels; Tim Hortons: July 2026 Canadian edition.')+'<section class="market-section"><h2>Sandwich, wrap, or the whole breakfast?</h2><p>Tim Hortons’ Egg &amp; Cheese English Muffin lists 270 kcal and 14 g protein. Its Sausage Farmer’s Wrap lists 640 kcal and 21 g protein. The larger wrap adds 370 kcal and 7 g protein; those figures alone do not make it a better choice for every appetite.</p><p>A medium Tim Hortons Protein Latte contributes another 170 kcal and 20 g protein in the listed recipe. Adding it to the egg-and-cheese English muffin gives a calculated 440 kcal and 34 g protein. That total excludes a hash brown and any unlisted customisation.</p></section>'+links([('/ca/en/find-a-meal/?meal=breakfast','Filter breakfasts'),('/ca/en/tools/drink-comparison/','Choose the drink'),('/ca/en/tools/complete-order/','Count the complete breakfast')])
 page('/ca/en/collections/breakfast/','Canadian fast-food breakfast comparison','Compare A&W and Tim Hortons Canadian breakfast portions, calories, protein and sodium, then count your drink and side separately.',body,family='collection')
 proteins=sorted([r for r in MEALS if r['category'] in ['entree','breakfast'] and r['p']>=25],key=lambda r:(r['cal'],-r['p']))
 body=intro('Protein in Canadian restaurant meals.','These tracked items provide at least 25 g protein per listed serving. Compare calories and sodium alongside protein; the table is not a ranking of the healthiest foods.')+table(proteins,'Threshold: at least 25 g protein in a verified Canadian serving. Sorted by calories, not a health score.')+'<section class="market-section"><h2>A useful trade-off to check</h2><p>Harvey’s Grilled Chicken Sandwich lists 270 kcal, 28 g protein and 670 mg sodium. A&amp;W’s Teen Burger lists 500 kcal, 27 g protein and 910 mg sodium. Each is its own standard serving; neither includes a side or drink in this comparison.</p><p>A minimum-protein filter helps make a shortlist. A sodium limit can change that shortlist, and the whole order can change it again. Use the builder to add the portions you actually plan to order.</p></section>'+links([('/ca/en/find-a-meal/?minProtein=25','Filter protein meals'),('/ca/en/tools/complete-order/','Add the side and drink'),('/protein-value-calculator.html?market=CA','Compare actual receipt costs')])
 page('/ca/en/collections/protein-meals/','Canadian high-protein restaurant meals','Compare tracked Canadian restaurant items with at least 25 g protein, including calories, portions and sodium rather than a made-up health score.',body,family='collection')
 combo=[choose('A&W Canada',n) for n in ['Teen Burger™','Russet Thick-Cut Fries (Regular)','A&W Root Beer® (Small)'] if any(r['name']==n and r['chain']=='A&W Canada' for r in MEALS)]
 # Select by source slug IDs if branded display names vary.
 if len(combo)!=3:combo=[next(r for r in MEALS if r.get('officialDataUrl','').endswith('/'+s+'/default')) for s in ['teen-burger','russet-thick-cut-fries-regular','aw-root-beer-small']]
 totals={k:sum(r[k] for r in combo) for k in ['cal','p','c','fat','f','na']}
 body=intro('Build a Canadian restaurant order.','A sandwich, side and drink count together. Add whole source-defined portions and keep any unknown totals visible.')+table(combo,'Worked example: A&W Canada standard Teen Burger + regular Russet Thick-Cut Fries + small A&W Root Beer.')+'<p>Calculated complete-order example: <strong>'+f'{totals["cal"]:g} kcal and {totals["p"]:g} g protein</strong>; '+f'{totals["na"]:g} mg sodium. This is a GetMacros sum of three published components, not a restaurant-published combo. It excludes extra packets and substitutions.</p>'+tool('order-builder','builder','Count your exact components')+links([('/ca/en/tools/drink-comparison/','Compare Canadian drinks'),('/ca/en/menu-sources/','Check the source coverage')])
 page('/ca/en/tools/complete-order/','Canadian complete-order builder','Add exact Canadian entrées, sides and drinks, with honest known subtotals and a source-backed A&W complete-order example.',body,scripts=['order-tools-core.js','order-notebook.js','order-tools.js'],family='tool')
 drinks=[choose('Tim Hortons',n) for n in ['Latte - Medium','Protein Latte - Medium','Double Double Coffee - Medium']]
 body=intro('Compare Canadian coffee and drinks.','Choose the named size and recipe. A protein latte, a regular latte and a sweetened coffee are different orders—not interchangeable ingredients.')+table(drinks,'Tim Hortons July 2026 Canadian edition, medium named recipes. Added sugars are not separately established here.')+'<p>The medium Protein Latte lists 20 g protein versus 10 g in the medium Latte, with 170 versus 140 kcal. Total sugars are 9 versus 13 g. These are the printed recipes; “sugar free” in a syrup name would not establish zero total sugars in the complete drink.</p>'+tool('drink-comparison','drink','Compare exact drinks')+links([('/ca/en/collections/breakfast/','Pair with breakfast'),('/ca/en/tools/complete-order/','Add it to your order')])
 page('/ca/en/tools/drink-comparison/','Canadian drink and protein-latte comparison','Compare Canadian Tim Hortons and A&W named drink sizes, calories, protein and total sugars without guessing customisation values.',body,scripts=['order-tools-core.js','order-tools.js'],family='tool')
 history=intro('Canadian menu sources & coverage.','A source-checked selection of individual Canadian items and components. Retrieval is not a claim that every restaurant changed its recipes that day.')+'<div class="market-directory">'+dirs+'</div><section class="market-section"><h2>What was checked</h2><ul><li>A&amp;W: current Canadian menu nutrition drawers and their underlying public records, reviewed October 9, 2026. Serving mass is kept in grams as displayed, including drinks; it is not silently converted into millilitres.</li><li>Tim Hortons: the July 2026 Canadian PDF linked by its current nutrition page, retrieved and reviewed October 9. Named drink sizes are retained; missing volume is not guessed.</li><li>Harvey’s: the current Canadian nutrition table, reviewed through its official page text October 9. Selected garnishes need their own portions.</li></ul></section><section class="market-section"><h2>Unavailable or unresolved</h2><p>McDonald’s Canada has not launched here: the public product pages did not expose complete numerical nutrition in our available interface, and direct browser access was denied. U.S. values are never used as replacements.</p><p>A&amp;W’s regular Mango Passionfruit Shake is withheld because its current source reports 94 g total sugars within 91 g carbohydrates. We have not guessed a correction.</p><p>UK, Australia and Japan remain research queues. French content is unavailable pending actual French editorial review.</p></section><section class="market-source-history"><h2>Update history</h2><p><time datetime="2026-10-09">October 9, 2026</time>: initial Canadian selection published after source review. Original nutrition editions are retained. No full-menu, local-stock or allergy audit is claimed.</p><p><a href="/js/canada-meals.json" download>Download the Canadian factual snapshot</a> · <a href="/corrections.html">Report a source discrepancy</a></p></section>'
 page('/ca/en/menu-sources/','Canadian menu-data sources and coverage','Check the Canadian restaurant selection, source editions, retrieval dates, missing fields, withheld values and menu update history.',history,family='methodology')
def finish():
 write('tools/international/routes.json',json.dumps(PAGES,ensure_ascii=False,indent=2)+'\n')
 tree=ET.parse(ROOT/'sitemap.xml');root=tree.getroot();ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
 for n in list(root):
  loc=n.find(ns+'loc')
  if loc is not None and loc.text.startswith(BASE+'/ca/'):root.remove(n)
 for r in PAGES:
  n=ET.SubElement(root,ns+'url');ET.SubElement(n,ns+'loc').text=BASE+r['route'];ET.SubElement(n,ns+'lastmod').text=r['lastmod']
 changed={BASE+p for p in ['/','/calculators.html','/breakfast-dataset-not-opening-hours.html','/exact-fiber-coverage-denominator.html','/menu-pdf-filename-not-edition-date.html','/sources.html','/fast-food-nutrition-data-report.html','/restaurant-search-result-count-scope.html','/same-restaurant-name-different-market-data.html','/menu-average-chain-weighting.html','/published-vs-calculated-restaurant-rows.html','/burger-variants-not-nine-base-burgers.html']}
 for n in root:
  if n.find(ns+'loc').text in changed:
   mod=n.find(ns+'lastmod')
   if mod is None:mod=ET.SubElement(n,ns+'lastmod')
   mod.text=DATE
 ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
 # Writing changes are dated separately from the retained restaurant-source checks.
 for route in changed:
  local=ROOT/(urlsplit(route).path.lstrip('/') or 'index.html')
  if not local.exists():continue
  text=local.read_text(encoding='utf-8')
  def modified(m):
   value=json.loads(m[1])
   if isinstance(value,dict) and value.get('@type')=='Article':value['dateModified']=DATE
   return '<script type="application/ld+json">'+json.dumps(value,ensure_ascii=False,separators=(',',':'))+'</script>'
  text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',modified,text,flags=re.S)
  write(local.relative_to(ROOT).as_posix(),text)

 text=(ROOT/'search.html').read_text(encoding='utf-8');text=re.sub(r'<!-- ca-search:start -->.*?<!-- ca-search:end -->','',text,flags=re.S)
 text=re.sub(r'(<a class="search-hit" )(?!data-market=)(href="(?:'+ '|'.join(re.escape(r) for r in ['restaurant-meal-finder.html','restaurant-meal-guides.html','healthy-fast-food.html','mcdonalds-healthy-meals-macros.html','chick-fil-a-healthy-meals-macros.html','chipotle-healthy-meals-macros.html']) +')")',r'\1data-market="US" \2',text)
 group='<section class="search-group" data-group="Canada"><h2>Canada <span data-count>'+str(len(PAGES))+'</span></h2>'+''.join('<a class="search-hit" data-market="CA" href="'+r['route']+'" data-search="'+e(r['title']+' '+r['description'])+'"><span class="search-hit-name">'+e(r['title'])+'</span><span class="search-hit-copy">'+e(r['description'])+'</span></a>' for r in PAGES)+'</section>'
 text=text.replace('<div class="search-results-actions">','<!-- ca-search:start -->'+group+'<!-- ca-search:end --><div class="search-results-actions">')
 write('search.html',text)
 out=ROOT/'docs/international-release-2026-10-09';out.mkdir(exist_ok=True)
 with (out/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
  fields=['route','template','market','visual_status','copy_status','SEO_status','responsive_status','interaction_status','verification_performed','remaining_issues'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in sorted(KEEP_ROOT_HTML):w.writerow(dict(route='/'+r,template='existing public route',market='US or global',visual_status='baseline families viewed; final QA pending',copy_status='copy audit pending',SEO_status='automated check pending',responsive_status='pending',interaction_status='pending',verification_performed='baseline build passed',remaining_issues='final QA pending'))
  for r in PAGES:w.writerow(dict(route=r['route'],template=r['template'],market='CA',visual_status='render QA pending',copy_status='source-backed original copy reviewed',SEO_status='self canonical; eligible equivalents only',responsive_status='pending',interaction_status='pending',verification_performed='source tables reviewed; final QA pending',remaining_issues='McDonald’s CA and French not published'))
 print('International release:',len(PAGES),'Canadian routes;',len(MEALS),'Canadian items; existing routes preserved.')
if __name__=='__main__':
 shared();data();build_pages();finish()
