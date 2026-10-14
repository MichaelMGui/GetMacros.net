"""Late integration of the clarity release, preserving source formulas and routes."""
from pathlib import Path
from html import escape,unescape
from urllib.parse import urlencode
import csv,json,re,subprocess,sys,xml.etree.ElementTree as ET
from normalize_calculator_layouts import Document
from build_global_product import page,head,MARKETS
from build_master_diary import search_ui,review,SCRIPTS
from build_master_restaurants import table
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/clarity-release-2026-10-14'
DATE='2026-10-14'
def e(v):return escape(str(v),quote=True)
def write(p,s):p.write_text(s,encoding='utf-8')
def public_pages():return sorted(list(ROOT.glob('*.html'))+[p for c in MARKETS if c!='US' for p in (ROOT/c.lower()/'en').rglob('index.html')])
def replace_node(text,cls,value):
    nodes=[n for n in Document(text).nodes if cls in n['attrs'].get('class','').split()]
    for n in reversed(nodes):text=text[:n['start']]+value+text[n['end']:]
    return text
def compare_section(workspace=False):
    return '<section class="food-portion-comparison" data-food-comparison '+('data-comparison-workspace ' if workspace else 'hidden ')+'aria-labelledby="food-comparison-title"><header class="food-review-header"><h2 id="food-comparison-title">'+('Your comparison' if workspace else 'Compare portions')+'</h2><button type="button" data-food-compare-clear>Clear</button></header><label>Comparison basis<select data-food-compare-basis><option value="portions">Reviewed portions</option><option value="100g">100 g of each food</option></select></label><p data-food-compare-status role="status" aria-live="polite"></p><div data-food-compare-content></div></section>'
def restaurants():
    source=ROOT/'tools/clarity_release/restaurant_additions.json'
    if not source.exists():return
    additions=json.loads(source.read_text(encoding='utf-8'));rows=additions['records'];ids={r['id'] for r in rows}
    p=ROOT/'js/order-registry.json';v=json.loads(p.read_text(encoding='utf-8'));v['records']=[r for r in v['records'] if r.get('id') not in ids]+rows;write(p,json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n')
    ca=[r for r in v['records'] if r['market']=='CA'];p=ROOT/'js/canada-meals.json';data=json.loads(p.read_text(encoding='utf-8'));data['records']=ca;write(p,json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    finder=[r for r in ca if r.get('category') not in ['component','sauce'] and r.get('finderSupported',True)]
    p=ROOT/'js/market-definitions.js';markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',p.read_text(encoding='utf-8'))[1]);markets['CA']['chains']=sorted({r['chain'] for r in finder});write(p,'window.GM_MARKETS='+json.dumps(markets,ensure_ascii=False,separators=(',',':'))+';\n')
    write(ROOT/'js/canada-meals.js','window.GM_MEALS='+json.dumps(finder,ensure_ascii=False,separators=(',',':'))+';window.GM_THRESHOLDS={protein:25,energy:600,light:400,fibre:5,sodium:600};\n')
    p=ROOT/'data/restaurant-presence.json';presence=json.loads(p.read_text(encoding='utf-8'));relationships=presence['relationships'];keys={r['id'] for r in additions['presenceRelationships']};presence['relationships']=[r for r in relationships if r['id'] not in keys]+additions['presenceRelationships'];write(p,json.dumps(presence,ensure_ascii=False,separators=(',',':'))+'\n')
    shell=subprocess.run(['node','tools/product_release/render-finder.cjs'],input=json.dumps(dict(rows=finder,markets=markets)),capture_output=True,encoding='utf-8',check=True,cwd=ROOT).stdout
    page('/ca/en/find-a-meal/','Canada meal finder: local menus, calories & protein','Compare exact Canadian servings. Filter calories, protein and available nutrients using local sources, with missing values kept visible.','<header class="finder-page-head"><h1>Find a meal in Canada.</h1></header><section id="meal-quiz" aria-label="Meal finder">'+shell+'</section>','finder',market='CA',template=(ROOT/'ca/en/find-a-meal/index.html').read_text(encoding='utf-8'))
    guide=additions['guide'];named=[r for r in rows if not r.get('calculatedFrom')];orders=[r for r in rows if r.get('calculatedFrom')]
    comparison_rows=[r for r in named if r['name'].startswith('Chicken Bacon Cheddar')]
    body='<article class="food-app food-reading">'+head(guide['h1'],guide['firstAction'])+'<nav class="food-actions"><a class="btn btn-primary" href="/ca/en/find-a-meal/?chain=Triple+O%E2%80%99s">Find an order →</a><a href="/food-library.html?market=CA&amp;type=restaurant&amp;q=Triple+O%E2%80%99s">Search exact servings →</a></nav><section><h2>Chicken Bacon Cheddar: check the sauce variant</h2><p>The printed standard serving has 791 kcal and 44 g protein. The separately listed Without Sauce serving has 567 kcal and 44 g protein. These are two source rows, not an estimated subtraction.</p>'+table(comparison_rows,'Official named Canadian servings; same protein, different published builds.')+'</section><section><h2>Breakfast</h2>'+table([r for r in named if r.get('meal')=='breakfast'],'Check the printed build and its native gram weight. Hashbrown is listed as five pieces, 70 g.')+'</section><section><h2>Chicken, fish &amp; sides</h2>'+table([r for r in named if r.get('meal')!='breakfast' and r.get('category') not in ['sauce','drink']],'Tracked Canadian servings. Extras are included only when the source names them.')+'</section><section><h2>Three complete-order examples</h2>'+table(orders,'GetMacros component sums, not restaurant-published combo totals.')+'<p>Each example adds exactly the source servings named in its portion. A drink or sauce is counted only when included. Published nutrient rounding applies.</p></section><details class="food-product-details"><summary>Coffee, small shakes &amp; sauces</summary>'+table([r for r in named if r.get('category') in ['sauce','drink']],'Exact source-listed portions; sauces are not standalone finder meals.')+'</details><section><h2>Source &amp; limits</h2><p>The <a href="'+e(rows[0]['source'])+'">official June 2025 nutrition guide</a> is the edition currently linked from the Canadian menu. The selected rows were reviewed October 14, 2026. This is a tracked selection, not a full audit of every location or current inventory.</p><p>Rows with contradictory calories and macros were withheld rather than corrected by guessing. Airport and venue menus can differ. No customization, dietary certification or allergen safety is inferred.</p></section></article>'
    page(guide['route'],guide['title'],guide['description'],body,'restaurant',market='CA')
    p=ROOT/'ca/en/restaurants/index.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- clarity-chain:start -->.*?<!-- clarity-chain:end -->','',text,flags=re.S);text=text.replace('</main>','<!-- clarity-chain:start --><section class="food-guide-section"><h2>Triple O’s</h2><p>Breakfast, chicken, fish, sides and named sauce variants. 37 official servings and three calculated orders.</p><a href="'+guide['route']+'">Browse the Canadian guide →</a></section><!-- clarity-chain:end --></main>',1);write(p,text)
    for route in ['ca/en/restaurants/index.html','world-restaurant-menus.html']:
        p=ROOT/route;text=p.read_text(encoding='utf-8');text=text.replace('383 tracked servings','423 tracked servings').replace('281 finder entries','318 finder entries').replace('74 verified country–chain relationships','75 verified country–chain relationships');write(p,text)
    p=ROOT/'world-restaurant-menus.html';text=p.read_text(encoding='utf-8');directory='<div class="food-directory">'
    for code,info in markets.items():
        local=[r for r in v['records'] if r['market']==code];supported=[r for r in local if r.get('category') not in ['component','sauce'] and r.get('finderSupported',True)]
        directory+='<article><h2><a href="'+info['home']+'">'+e(info['name'])+'</a></h2><p>'+str(len(local))+' tracked servings; '+str(len(supported))+' finder entries.</p><p>'+e(', '.join(sorted({r['chain'] for r in local})))+'</p><a class="text-action" href="'+info['restaurants']+'">Local chains &amp; coverage →</a></article>'
    text=replace_node(text,'food-directory',directory+'</div>');write(p,text)
    write(OUT/'restaurant-integration.json',json.dumps(dict(newRecords=len(rows),officialNamed=len(named),calculatedOrders=len(orders),registryRecords=len(v['records']),canadaRecords=len(ca),canadaFinder=len(finder),presenceRelationships=len(presence['relationships']),routes=[guide['route']],source=additions['source'],withheld=additions['withheld']),ensure_ascii=False,indent=2)+'\n')
def comparison():
    scripts=list(SCRIPTS);scripts.insert(scripts.index('food-portion-compare.js'),'food-comparison-state.js')
    body='<div class="food-app food-library-app comparison-workspace" data-food-app="library">'+head('Put two foods side by side.','Choose foods or restaurant orders. Review the portion, then compare.')+compare_section(True)+'<section class="comparison-add"><h2>Choose a food</h2>'+search_ui()+'</section><nav class="comparison-more" aria-label="Other comparisons"><a href="/compare-complete-restaurant-orders.html">Build a complete order →</a><a href="/compare-menu-ingredients-worldwide.html">Compare country ingredients →</a><a href="/nutrition-label-comparison-tool.html">Enter two food labels →</a></nav><details class="food-product-details"><summary>How to read the comparison</summary><p>Reviewed portions show the amounts you selected. The 100 g view is available only when both sources supply a weight. A drink without a verified density is not converted from millilitres to grams.</p><p>Different recipes, regions and source editions remain separate. Unknown nutrients stay unknown. No automatic winner or health score is assigned. The retained comparison contains public food records and portions, never private diary notes.</p><a href="/food-library-sources.html">Data sources, editions &amp; licenses →</a></details></div>'+review()
    page('/compare-foods.html','Compare food nutrition: portions, calories & macros','Compare two restaurant orders, ingredients or branded foods. Keep country, source edition and portion visible; use equal weights only where supported.',body,'comparison',scripts)
    p=ROOT/'food-library.html';text=p.read_text(encoding='utf-8');text=replace_node(text,'food-portion-comparison',compare_section());text=text.replace('<script src="/js/food-portion-compare.js"','<script src="/js/food-comparison-state.js" defer></script><script src="/js/food-portion-compare.js"');text=text.replace('Open your diary →','Log food →');text=text.replace('<a class="text-action" href="/grocery-food-coverage.html">','<a class="text-action" href="/compare-foods.html">Compare foods →</a><a class="text-action" href="/grocery-food-coverage.html">',1);write(p,text)
def nav_group(label,links):return '<div class="nav-group"><button class="nav-group-trigger" type="button" aria-expanded="false">'+label+'</button><div class="nav-popover">'+''.join('<a '+attrs+' href="'+href+'"><strong>'+title+'</strong></a>' for href,title,attrs in links)+'</div></div>'
def shell():
    for p in public_pages():
        text=p.read_text(encoding='utf-8');scope=re.search(r'data-market-scope="([A-Z]{2})"',text);code=next((c for c in MARKETS if c!='US' and p.relative_to(ROOT).as_posix().startswith(c.lower()+'/en/')),scope[1] if scope and scope[1] in MARKETS else 'US');m=MARKETS[code]
        # Reuse existing menu interaction and focus management, not a second nav.
        doc=Document(text);nav=next((n for n in doc.nodes if n['attrs'].get('id')=='primary-navigation'),None)
        if nav:
            old=text[nav['start']:nav['end']];mobile=Document(old).find(cls='mobile-menu-head');mobile=old[mobile['start']:mobile['end']]
            menu='<div class="full-nav-links" id="primary-navigation">'+mobile+'<a class="nav-direct" data-market-route="finder" href="'+m['finder']+'">Find a meal</a>'+nav_group('Restaurants',[(m['restaurants'],'All restaurants','data-market-route="restaurants"'),('/world-restaurant-menus.html','Countries &amp; menu coverage',''),('/compare-menu-ingredients-worldwide.html','Country ingredients','')])+'<a class="nav-direct" data-market-context="true" href="/compare-foods.html'+('' if code=='US' else '?market='+code)+'">Compare</a>'+nav_group('Log food',[('/food-diary.html'+('' if code=='US' else '?market='+code),'Food diary','data-market-context="true" data-product-diary-link'),('/food-library.html','Food library','data-market-context="true"'),('/food-shelf.html','Saved orders','data-market-context="true"'),('/grocery-food-coverage.html','Grocery brands','')])+nav_group('Calculators',[('/calculators.html','Macro calculator','data-market-context="true"'),('/recipe-macro-scaler.html','Recipe portions',''),('/nutrition-label-comparison-tool.html','Food labels',''),('/protein-value-calculator.html','Protein value','')])+nav_group('Learn',[('/articles.html','All guides','data-market-context="true"'),('/articles.html#learn-eating-out','Eating out',''),('/articles.html#learn-breakfast','Breakfast',''),('/articles.html#learn-coffee-drinks','Coffee &amp; drinks',''),('/articles.html#learn-portions-labels','Portions &amp; labels',''),('/read-and-watch.html','Read &amp; watch',''),('/play.html','Play',''),('/sources.html','Sources &amp; methods','')])+'<a class="nav-mobile-search" data-market-context="true" href="/search.html">Search the site</a></div>'
            if code!='US':menu=re.sub(r'(data-market-context="true"[^>]*href="/[^"?#]+)(?:\?market=[A-Z]+)?("[^>]*>)',lambda h:h[1]+'?market='+code+h[2],menu)
            text=text[:nav['start']]+menu+text[nav['end']:]
        # Current language is a label; do not advertise a non-existent language menu.
        text=replace_node(text,'language-picker','<span class="language-current-label" aria-label="Interface language: English">English</span>')
        # Retain breadcrumb function; shorten only redundant current-page labels.
        for n in reversed([n for n in Document(text).nodes if 'breadcrumb' in n['attrs'].get('class','').split()]):
            fragment=text[n['start']:n['end']]
            fragment=re.sub(r'<(?:span|li)[^>]*aria-current="page"[^>]*>.*?</(?:span|li)>','<span aria-current="page">This page</span>',fragment,flags=re.S)
            text=text[:n['start']]+fragment+text[n['end']:]
        if 'data-home-template=' in text:
            text=text.replace('class="food-ensemble" aria-hidden="true"','class="food-ensemble"')
            text=text.replace('A little notebook.<br>For what you actually ate.','Log what you ate.').replace('Keep breakfast, lunch, dinner and snacks together. Your diary stays in this browser.','Breakfast, lunch, dinner and snacks. Saved in this browser.')
            text=text.replace('A quiet puzzle. A familiar face.','').replace('Make a little time to play','Play')
            rows={}
            for r in json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']:
                if r['market']!=code:continue
                for key in [r.get('id'),r['chain']+'||'+r['name'],r.get('restaurantMarketId','')+'|'+r['name']]:
                    if key:rows[key]=r
            for n in reversed([n for n in Document(text).nodes if 'data-home-record' in n['attrs']]):
                r=rows.get(n['attrs']['data-home-record'])
                if r:
                    fragment=text[n['start']:n['end']];record='order:'+code+':'+(r.get('id') or r['chain']+'||'+r['name']);href='/compare-foods.html?'+urlencode({'item':record,'append':'1','market':code});fragment=fragment.replace('</article>','<a class="home-compare-action" href="'+e(href)+'">Compare portion →</a></article>');fragment=re.sub(r'(<a class="text-action home-menu-action" href=")[^"]*',lambda h:h[1]+e('/food-library.html?'+urlencode({'food':record,'market':code})),fragment);text=text[:n['start']]+fragment+text[n['end']:]
            text=re.sub(r'<p>\s*</p>','',text)
        if 'data-food-app="diary"' in text:
            text=text.replace('<p>Breakfast, lunch, dinner and everything between.</p>','').replace('<h1>Today’s food.</h1>','<h1 data-diary-title>Today’s food.</h1>')
            doc=Document(text);toolbar=doc.find(cls='diary-toolbar');fragment=text[toolbar['start']:toolbar['end']];text=text[:toolbar['start']]+text[toolbar['end']:];summary=Document(text).find(cls='diary-summary');text=text[:summary['start']]+fragment+'<p class="diary-empty-day" data-diary-empty-day hidden>No food recorded for this day.</p>'+text[summary['start']:]
        if p.name=='privacy.html' and '<!-- diary-privacy:start -->' in text:
            # Keep the substantive diary notice inside the same reading column.
            start=text.index('<!-- diary-privacy:start -->');end=text.index('<!-- diary-privacy:end -->',start)+len('<!-- diary-privacy:end -->')
            notice=text[start:end];text=text[:start]+text[end:]
            body=Document(text).find(cls='reference-body')
            if body:
                insert=body['end']-len('</div>');text=text[:insert]+notice+text[insert:]
        if not p.relative_to(ROOT).as_posix().startswith('ca/en/'):
            text=text.replace('Fibre (g)','Fiber (g)').replace('Fibre, g','Fiber, g')
        write(p,text)
def calculators():
    p=ROOT/'calculators.html';text=p.read_text(encoding='utf-8');text=replace_node(text,'calculator-waiting','')
    text=text.replace('Enter your details for an adult calorie and macro estimate.','An estimate for adults. Enter your details to begin.')
    text=text.replace('<h2>Other nutrition tools</h2>','<h2>Choose your next task</h2>')
    write(p,text)
def discovery():
    for p in public_pages():
        text=p.read_text(encoding='utf-8')
        if 'data-family="restaurant"' in text or '/restaurants/' in p.relative_to(ROOT).as_posix():
            text=re.sub(r'<!-- clarity-comparison:start -->.*?<!-- clarity-comparison:end -->','',text,flags=re.S)
            text=text.replace('</main>','<!-- clarity-comparison:start --><nav class="contextual-tools" aria-label="Next food tasks"><a href="/compare-foods.html">Compare foods →</a><a href="/food-diary.html">Log a portion →</a><a href="/food-library.html">Search menu records →</a></nav><!-- clarity-comparison:end --></main>',1)
            write(p,text)
def index_and_inventory():
    p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- clarity-search:start -->.*?<!-- clarity-search:end -->','',text,flags=re.S)
    routes=['/compare-foods.html']
    for manifest in ['editorial-manifest.json','restaurant-integration.json']:
        path=OUT/manifest
        if path.exists():
            v=json.loads(path.read_text(encoding='utf-8'));routes.extend(x['route'] if isinstance(x,dict) else x for x in v.get('routes',[]))
    editorial=json.loads((OUT/'editorial-manifest.json').read_text(encoding='utf-8'))
    for row in editorial['routes']:
        file=ROOT/row['route'].lstrip('/');article=file.read_text(encoding='utf-8');node=Document(article).find(cls='page-intro-content');fragment=article[node['start']:node['end']]
        if 'data-shelf-save' not in fragment:
            action='<div class="article-actions"><button type="button" data-shelf-save data-kind="article" data-url="'+e(row['route'].lstrip('/'))+'" data-title="'+e(row['title'])+'" aria-pressed="false">Save this guide</button><a class="text-action" href="/food-shelf.html">Saved guides →</a></div>'
            article=article[:node['close']]+action+article[node['close']:];write(file,article)
    index=ROOT/'articles.html';library=index.read_text(encoding='utf-8');library=re.sub(r'<!-- clarity-editorial:start -->.*?<!-- clarity-editorial:end -->','',library,flags=re.S)
    clusters={'Eating out':'eating-out','Breakfast':'breakfast','Coffee & drinks':'coffee-drinks','Meal comparisons':'meal-comparisons','Complete orders':'meal-comparisons','Country comparisons':'meal-comparisons','Protein & value':'protein-value','Portions & labels':'portions-labels','Groceries & labels':'portions-labels','Original analysis':'portions-labels'}
    for n in reversed([n for n in Document(library).nodes if 'data-reading-topic' in n['attrs']]):
        slug=n['attrs'].get('id','').removeprefix('learn-');rows=[r for r in editorial['routes'] if clusters.get(r['cluster'],'meal-comparisons')==slug]
        if not rows:continue
        fragment=library[n['start']:n['end']];group=Document(fragment).find(cls='library-reads');links=''.join('<a class="library-read" href="'+e(r['route'])+'"><span>'+e(r['title'])+'</span><small>'+e(r['description'])+'</small><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg></a>' for r in rows)
        fragment=fragment[:group['inner']]+'<!-- clarity-editorial:start -->'+links+'<!-- clarity-editorial:end -->'+fragment[group['inner']:];count=fragment.count('class="library-read"');fragment=re.sub(r'<p>\d+ reads</p>','<p>'+str(count)+' reads</p>',fragment,count=1);library=library[:n['start']]+fragment+library[n['end']:]
    write(index,library)
    links=[]
    for route in sorted(set(routes)):
        file=ROOT/(route.strip('/')+'/index.html' if route.endswith('/') else route.lstrip('/'))
        if file.exists():
            s=file.read_text(encoding='utf-8');title=unescape(re.search(r'<title>(.*?)</title>',s,re.S)[1]);description=unescape(re.search(r'<meta name="description" content="([^"]*)',s)[1]);links.append('<a class="search-hit" href="'+route+'" data-search="'+e(title)+'"><span class="search-hit-name">'+e(title)+'</span><span class="search-hit-copy">'+e(description)+'</span></a>')
    text=text.replace('</main>','<!-- clarity-search:start --><section class="search-group"><h2>Comparisons &amp; new guides <span data-count>'+str(len(links))+'</span></h2>'+''.join(links)+'</section><!-- clarity-search:end --></main>',1);write(p,text)
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';tree=ET.parse(ROOT/'sitemap.xml');nodes={n.find(ns+'loc').text:n for n in tree.getroot()}
    for route in sorted(set(routes)):
        url='https://getmacros.net'+route;node=nodes.get(url)
        if node is None:node=ET.SubElement(tree.getroot(),ns+'url');ET.SubElement(node,ns+'loc').text=url
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text=DATE
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    entries=[]
    for p in public_pages():
        rel=p.relative_to(ROOT).as_posix();route='/' if rel=='index.html' else '/'+rel.removesuffix('index.html') if rel.endswith('/index.html') else '/'+rel;text=p.read_text(encoding='utf-8');family=re.search(r'data-family="([^"]+)"',text)
        entries.append(dict(route=route,template=family[1] if family else 'legacy-public',issue='Feature discovery and shared composition reviewed',planned_change='Shared navigation; task-led contextual links; family-specific refinement',data_dependency='Source records retained; reviewed additions recorded separately',implementation='Shared shell migrated',functional_checks='Pending final checks',visual_checks='Not individually visually inspected; family review and automated route checks pending',remaining_blockers=''))
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'coverage.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=entries[0]);writer.writeheader();writer.writerows(entries)
    write(OUT/'feature-discovery.csv','feature,primary entry,contextual entry,destination\nMeal finder,Find a meal,Homepage and restaurants,/restaurant-meal-finder.html\nComparison,Compare,Meals and food review and articles,/compare-foods.html\nFood diary,Log food,Comparison and food review,/food-diary.html\nFood library,Log food menu,Comparison and diary search,/food-library.html\nSaved orders,Log food menu,Finder save and diary saved tab,/food-shelf.html\nCalculators,Calculators,Articles and portion example,/calculators.html\nLearn,Learn,Restaurant guides and calculator explanation,/articles.html\nPlay,Learn menu,Homepage games module,/play.html\nRead and watch,Learn menu,Editorial and footer,/read-and-watch.html\n')
def build():
    OUT.mkdir(parents=True,exist_ok=True)
    file=ROOT/'tools/clarity_release/restaurant_ingest.py'
    if file.exists():subprocess.run([sys.executable,'-X','utf8',str(file)],cwd=ROOT,check=True)
    restaurants()
    from build_master_interface import build as shared_build
    shared_build()
    for name in ['editorial.py','character-media.py']:
        file=ROOT/'tools/clarity_release'/name
        if file.exists():subprocess.run([sys.executable,'-X','utf8',str(file)],cwd=ROOT,check=True)
    comparison();shell();calculators();discovery();index_and_inventory()
    # Recreated Canadian finder must retain real reciprocal regional versions.
    from build_master_completion import regional_annotations
    regional_annotations()
    media=ROOT/'tools/clarity_release/character-media.css'
    if media.exists():
        write(ROOT/'css/clarity-media.css',media.read_text(encoding='utf-8'))
        write(ROOT/'js/clarity-media.js',(media.with_suffix('.js')).read_text(encoding='utf-8'))
        for p in public_pages():
            text=p.read_text(encoding='utf-8')
            if p.name=='read-and-watch.html' or 'clarity-game' in text or 'data-food-character="steak"' in text:
                for n in reversed([n for n in Document(text).nodes if n['tag']=='link' and (n['attrs'].get('data-source-path','').lstrip('/')=='css/clarity-media.css' or n['attrs'].get('href','').split('?')[0].lstrip('/')=='css/clarity-media.css')]):text=text[:n['start']]+text[n['end']:]
                text=text.replace('</head>','<link rel="stylesheet" href="/css/clarity-media.css"></head>',1)
                if 'clarity-game' in text:
                    for n in reversed([n for n in Document(text).nodes if n['tag']=='script' and (n['attrs'].get('data-source-path','').lstrip('/')=='js/clarity-media.js' or n['attrs'].get('src','').split('?')[0].lstrip('/')=='js/clarity-media.js')]):text=text[:n['start']]+text[n['end']:]
                    text=text.replace('</body>','<script src="/js/clarity-media.js" defer></script></body>',1)
                write(p,text)
    from build_edition_css import build as css_build
    css_build()
    print('Clarity release integrated: shared discovery, retained comparison, calculator workspace and route inventory.')
if __name__=='__main__':build()
