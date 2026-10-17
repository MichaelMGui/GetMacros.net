"""Late integration of reviewed country menus and all-brand source partitions.

Source importers are offline operations. Normal site builds use the committed
query shards and reviewed menu records, never a provider API or invented data.
"""
from pathlib import Path
from collections import Counter
from html import escape
from urllib.parse import quote, urlencode
import csv, hashlib, importlib.util, json, re, subprocess, xml.etree.ElementTree as ET
import build_global_product as product
from normalize_calculator_layouts import Document
from build_master_restaurants import table as source_table

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/global-coverage-2026-10-17'
DATE='2026-10-17'
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write(path,text):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
def dump(path,value): write(path,json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n')
def e(value): return escape(str(value),quote=True)
def html_path(route): return 'index.html' if route=='/' else route.strip('/')+'/index.html' if route.endswith('/') else route.lstrip('/')
def eligible(row): return row.get('category') not in ('component','sauce') and row.get('finderSupported',True)
def action(route,label): return '<a class="text-action" href="'+e(route)+'">'+e(label)+' →</a>'
def section(title,body): return '<section><h2>'+e(title)+'</h2>'+body+'</section>'
def table(*args,**kwargs): return source_table(*args,**kwargs).replace('aria-label="Canadian serving','aria-label="Source serving')

def integrate():
    additions=read('tools/global_coverage_2026_10_17/restaurant-records.json')
    new_market_file=ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-records.json'
    if new_market_file.exists():
        newer=read(new_market_file.relative_to(ROOT))
        additions['records']+=newer['records'];additions['updates']+=newer.get('updates',[])
    registry=read('js/order-registry.json')
    incoming=additions['records']+additions['updates'];ids={r['id'] for r in incoming}
    registry['records']=[r for r in registry['records'] if r.get('id') not in ids]+incoming
    explicit=[r['id'] for r in registry['records'] if r.get('id')]
    assert len(set(explicit))==len(explicit)
    dump('js/order-registry.json',registry)
    markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
    presence=read('data/restaurant-presence.json');upserts=read('tools/global_coverage_2026_10_17/restaurant-presence-upserts.json')['relationships']
    if new_market_file.exists():
        markets.update(read('tools/global_coverage_2026_10_17/restaurant-newmarkets-definitions.json'))
        upserts+=read('tools/global_coverage_2026_10_17/restaurant-newmarkets-presence-upserts.json')['relationships']
    registry['markets']=list(markets);dump('js/order-registry.json',registry)
    from source_json import write_json
    restaurant_manifest={'version':hashlib.sha256(json.dumps(registry['records'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:16],'markets':{}}
    for code in markets:
        rows=[r for r in registry['records'] if r['market']==code]
        write_json(ROOT/'data/restaurant-foods'/(code+'.json'),rows,compressed=True)
        restaurant_manifest['markets'][code]={'count':len(rows),'file':code+'.json.gz'}
    dump('data/restaurant-foods/manifest.json',restaurant_manifest)
    # Seed new countries from the current production compositions, then use the
    # same shared homepage renderer as every established market.
    for code,info in markets.items():
        if not (ROOT/html_path(info['home'])).exists():
            product.page(info['home'],info['name']+' restaurant meals','Browse country-specific source servings in '+info['name']+'.','<section></section>','home',market=code,template=(ROOT/'index.html').read_text(encoding='utf-8'))
        if not (ROOT/html_path(info['finder'])).exists():
            seed=(ROOT/'ca/en/find-a-meal/index.html').read_text(encoding='utf-8')
            seed=re.sub(r'<script[^>]*src="/?(?:js/canada-meals\.js|assets/generated/js-canada-meals-[^" ]+\.js)[^>]*>\s*</script>','',seed)
            product.page(info['finder'],info['name']+' meal finder','Filter exact local servings by calories, protein and other known nutrients.','<header class="finder-page-head"><h1>Find a meal in '+e(info['name'])+'.</h1></header><section id="meal-quiz" aria-label="Meal finder"></section>','finder',market=code,template=seed)
        if code in ('FR','IN','SG','ZA'):
            rows=sorted([r for r in registry['records'] if r['market']==code and eligible(r) and r.get('p') is not None and r['p']>=25],key=lambda r:-r['p'])[:12]
            product.page(info['collection'],info['name']+' restaurant servings with 25 g protein','Compare named '+info['name']+' portions with at least 25 g protein, alongside calories, carbs, fat and available sodium.','<article class="food-app food-reading">'+product.head('Protein options in '+info['name']+'.','Compare the named serving, not just the protein number.')+'<p>'+e(info['officialOperatorScope'])+'</p>'+table(rows,'At least 25 g protein per listed source serving. No healthiest-food ranking or full-menu claim.')+action(info['finder']+'?minProtein=25','Refine the selection')+'</article>','collection',market=code)
    relations={r['id']:r for r in presence['relationships']};relations.update({r['id']:r for r in upserts})
    for key,r in relations.items():
        local=[x for x in registry['records'] if x.get('restaurantMarketId')==key or (x['market']==r['country'] and x['chain']==r['restaurantBrand'])]
        r['trackedRecords']=len(local);r['finderRecords']=sum(eligible(x) for x in local)
        r['completeMacroRecords']=sum(all(x.get(k) is not None for k in ('cal','p','c','fat')) for x in local)
        r['partialMacroRecords']=len(local)-r['completeMacroRecords']
        r['finderSupported']=bool(r['finderRecords']);r['calculatedOrders']=sum(bool(x.get('calculatedFrom')) for x in local)
        r['caloriesOnlyRecords']=sum(x.get('cal') is not None and all(x.get(k) is None for k in ('p','c','fat')) for x in local)
    presence['relationships']=sorted(relations.values(),key=lambda r:r['id']);presence['checkedAt']=DATE
    dump('data/restaurant-presence.json',presence)
    for code,info in markets.items():
        local=[r for r in registry['records'] if r['market']==code];finder=[r for r in local if eligible(r)]
        info['chains']=sorted({r['chain'] for r in finder})
        name='canada' if code=='CA' else code.lower()
        write('js/'+name+'-meals.js','window.GM_MEALS='+json.dumps(finder,ensure_ascii=False,separators=(',',':'))+';window.GM_THRESHOLDS={protein:25,energy:600,light:400,fibre:5,sodium:600};\n')
        if code=='CA':
            ca=read('js/canada-meals.json');ca['records']=local;dump('js/canada-meals.json',ca)
        path=html_path(info['finder']);text=(ROOT/path).read_text(encoding='utf-8')
        if code in ('FR','IN','SG','ZA'):
            description='Compare '+', '.join(info['chains'])+' servings in '+info['name']+'. Filter calories and protein; check local portions, source editions and missing nutrients.'
            for key in ('description','og:description','twitter:description'):
                text=re.sub(r'(<meta (?:name|property)="'+re.escape(key)+'" content=")[^"]*',lambda m:m[1]+e(description),text,count=1)
        node=Document(text).find(id='meal-quiz');assert node
        shell=subprocess.run(['node','tools/product_release/render-finder.cjs'],input=json.dumps(dict(rows=finder,markets=markets)),capture_output=True,encoding='utf-8',check=True,cwd=ROOT).stdout
        shell=shell.replace('href="restaurant-meal-finder.html"','href="'+info['finder']+'"')
        text=text[:node['inner']]+shell+text[node['close']:]
        text=re.sub(r'<!-- operator-scope:start -->.*?<!-- operator-scope:end -->','',text,flags=re.S)
        if code=='IN':text=text.replace('<section id="meal-quiz"','<!-- operator-scope:start --><p class="market-notice">North &amp; East India only · McDonald’s operated by Connaught Plaza Restaurants Private Limited. Other Indian regions may use different menus.</p><!-- operator-scope:end --><section id="meal-quiz"',1)
        # A single explicit market dataset is loaded immediately before the
        # finder. The U.S. retains existing data assets used by other tools.
        text=re.sub(r'<script[^>]*src="/?js/'+name+r'-meals\.js(?:\?[^" ]*)?"[^>]*>\s*</script>','',text)
        text=re.sub(r'(?=<script[^>]*src="/?(?:js/meal-finder\.js|assets/generated/js-meal-finder-[^" ]+\.js))',lambda _: '<script src="/js/'+name+'-meals.js" defer></script>',text,count=1)
        write(path,text)
    write('js/market-definitions.js','window.GM_MARKETS='+json.dumps(markets,ensure_ascii=False,separators=(',',':'))+';\n')
    path=ROOT/'restaurant-meal-guides.html';text=path.read_text(encoding='utf-8');doc=Document(text)
    entries=[n for n in doc.nodes if 'restaurant-entry' in n['attrs'].get('class','').split()]
    for node in reversed(entries):
        fragment=text[node['start']:node['end']];heading=re.search(r'<h2>(.*?)</h2>',fragment,re.S)
        if not heading:continue
        from html import unescape
        chain=unescape(re.sub('<[^>]+>','',heading[1]));count=sum(r['market']=='US' and r['chain']==chain and eligible(r) for r in registry['records'])
        if count:
            fragment=re.sub(r'\b\d+ recorded orders\b',str(count)+' recorded orders',fragment)
            fragment=re.sub(r'Compare \d+ tracked '+re.escape(chain)+r' portions',str('Compare '+str(count)+' tracked '+chain+' portions'),fragment)
        text=text[:node['start']]+fragment+text[node['end']:]
    path.write_text(text,encoding='utf-8')
    return additions,registry,markets,presence

def guides(additions,registry,markets,presence):
    briefs=read('docs/global-coverage-2026-10-17/restaurants/guide-briefs.json')['briefs']
    newer=ROOT/'docs/global-coverage-2026-10-17/restaurants/newmarkets/guide-briefs.json'
    if newer.exists():briefs+=read(newer.relative_to(ROOT))['briefs']
    by_chain={}
    for brief in briefs:
        code=brief['market'];country=markets[code]['name'];route=('/'+brief['slug']+'.html') if code=='US' else markets[code]['home']+'guides/'+brief['slug']+'/'
        rows=brief['comparisonRows'];chain=next(r['chain'] for r in registry['records'] if r.get('id')==brief['recordIds'][0])
        by_chain.setdefault((code,chain),[]).append((route,brief['title']))
        body='<article class="food-app food-reading"><header class="food-app-head"><h1>'+e(brief['title'])+'</h1></header>'
        body+='<p>'+e(brief['paragraphs'][0])+'</p>'+table(rows,'Exact '+country+' source servings. Unknown nutrients remain unknown.')
        body+=''.join('<p>'+e(p)+'</p>' for p in brief['paragraphs'][1:])
        body+=section('Try the portions',action('/food-library.html?'+urlencode(dict(market=code,type='restaurant',q=chain)),'Search these servings')+' '+action('/compare-foods.html?market='+code,'Compare portions')+' '+action('/food-diary.html?market='+code,'Log a meal'))
        body+=section('Sources & limits','<ul>'+''.join('<li><a href="'+e(url)+'">Official '+e(chain)+' nutrition source</a></li>' for url in dict.fromkeys(r['source'] for r in rows))+'</ul><p>Source rows reviewed October 17, 2026. Edition dates remain attached to each menu record. GetMacros did not test these meals or audit every local branch. Different recipes, added sauces and later menu changes need their own source values.</p>')+'</article>'
        if code=='US':body=re.sub(r'\bfibre\b','fiber',body,flags=re.I)
        product.page(route,brief['title'],brief['paragraphs'][0][:300],body,'article',market=code)
    for code,chain in sorted({(r['market'],r['chain']) for r in additions['records']+additions['updates']}):
        local=[r for r in registry['records'] if r['market']==code and r['chain']==chain]
        route=next(r['url'] for r in local if r.get('id') in {x['id'] for x in additions['records']+additions['updates']})
        if not route.startswith('/'):route='/'+route
        country=markets[code]['name'];finder=markets[code]['finder']+'?'+urlencode(dict(chain=chain))
        body='<article class="food-app food-reading">'+product.head(chain+' in '+country+'.','Check the exact serving before choosing or logging an order.')
        body+='<nav class="food-actions">'+action(finder,'Find a meal')+' '+action('/food-library.html?'+urlencode(dict(market=code,type='restaurant',q=chain)),'Search every tracked item')+'</nav>'
        body+=section('A closer comparison',''.join('<p>'+action(url,label)+'</p>' for url,label in by_chain.get((code,chain),[])))
        for category,label in [('entree','Meals & mains'),('breakfast','Breakfast'),('side','Sides'),('drink','Drinks'),('component','Ingredients'),('sauce','Sauces')]:
            rows=[r for r in local if (r.get('category')=='entree' and r.get('meal')=='breakfast' and category=='breakfast') or (r.get('category')==category and not(category=='entree' and r.get('meal')=='breakfast'))]
            if rows:body+=section(label,table(rows,'Per named '+country+' serving; sides and drinks are separate unless included in the name.'))
        other=[r for r in local if r.get('category') not in ('entree','side','drink','component','sauce')]
        if other:body+=section('Other tracked servings',table(other,'Source-defined portions.'))
        sources=list(dict.fromkeys((r['source'],r.get('sourceDate')) for r in local))
        body+=section('Source editions & portions','<p>'+str(len(local))+' tracked entries. This is a source selection, not a complete live menu or local-stock guarantee.</p><ul>'+''.join('<li><a href="'+e(url)+'">Official nutrition table</a> · edition '+e(date or 'not supplied')+'</li>' for url,date in sources)+'</ul><details class="food-product-details"><summary>Recipe and measurement limits</summary>'+''.join('<p>'+e(note)+'</p>' for note in dict.fromkeys(r.get('notes','') for r in local) if note)+'<p>Ingredients, substitutions and allergen safety are not inferred. Less-than source values and missing nutrients are not treated as exact zeros.</p></details>')+'</article>'
        if code=='US' and (ROOT/html_path(route)).exists():
            # Keep the established U.S. guide, worked examples and finder form.
            # Append the new source selection instead of replacing that work.
            text=(ROOT/html_path(route)).read_text(encoding='utf-8')
            text=re.sub(r'<!-- global-menu-selection:start -->.*?<!-- global-menu-selection:end -->','',text,flags=re.S)
            extra=section('More exact menu portions',''.join('<p>'+action(url,label)+'</p>' for url,label in by_chain.get((code,chain),[]))+table([r for r in additions['records'] if r['market']==code and r['chain']==chain],'Additional official U.S. source servings; not automatic combo totals.'))
            extra=extra.replace('Fibre','Fiber')
            write(html_path(route),text.replace('</main>','<!-- global-menu-selection:start -->'+extra+'<!-- global-menu-selection:end --></main>',1))
        else:
            product.page(route,chain+' '+country+' nutrition: menu portions & macros','Compare '+str(len(local))+' tracked '+chain+' servings in '+country+'. Check calories, protein, carbs, fat, exact portions and official source editions.',body,'restaurant',market=code)
    for code,info in markets.items():
        relationships=[r for r in presence['relationships'] if r['country']==code]
        rows=[]
        for rel in relationships:
            local=[r for r in registry['records'] if r.get('restaurantMarketId')==rel['id'] or (r['market']==code and r['chain']==rel['restaurantBrand'])]
            route=local[0]['url'] if local else rel.get('officialCountryWebsite')
            if not route:continue
            if not route.startswith(('https://','/')):route='/'+route
            text=(str(len(local))+' tracked servings; '+str(sum(eligible(r) for r in local))+' finder entries.') if local else 'Local operations confirmed. Usable nutrition records are not published here yet.'
            rows.append('<article class="presence-row"><div><h2>'+action(route,rel['restaurantBrand'])+'</h2><p>'+e(text)+'</p></div>'+action(route,'View servings' if local else 'Official local site')+'</article>')
        body='<section class="food-app">'+product.head('Restaurants in '+info['name']+'.','Local menus and named servings.')+'<div class="restaurant-presence-list">'+''.join(rows)+'</div><details class="food-product-details"><summary>What coverage means</summary><p>A chain operating locally, publishing nutrition and having usable GetMacros records are separate facts. Tracked selections are not full live menus. Country recipes are kept separate.</p></details></section>'
        if code!='US':
            product.page(info['restaurants'],info['name']+' restaurant menus, nutrition & coverage','Browse local restaurant nutrition for '+info['name']+'. Compare tracked portions and see where reliable nutrition is still unavailable.',body,'restaurant-index',market=code)
    body='<section class="food-app">'+product.head('Menus around the world.','Choose the country where you are ordering.')+'<div class="food-directory">'
    for code,info in markets.items():
        local=[r for r in registry['records'] if r['market']==code]
        body+='<article><h2>'+action(info['home'],info['name'])+'</h2><p>'+str(len(local))+' tracked servings; '+str(sum(eligible(r) for r in local))+' finder entries.</p><p>'+e(', '.join(sorted({r['chain'] for r in local})))+'</p>'+action(info['restaurants'],'Menus & coverage')+'</article>'
    body+='</div><p>These are country-specific source selections, not every restaurant or the entire current menu. Missing countries are not filled with another country’s values.</p>'+action('/compare-menu-ingredients-worldwide.html','Compare country ingredients')+'</section>'
    product.page('/world-restaurant-menus.html','World restaurant menus: country-specific nutrition','Choose a country to browse tracked restaurant menus, exact source portions, calories, protein and known coverage gaps.',body,'country-index')

def metadata_and_manifest(markets,additions,registry):
    # Existing new-market files must remain discoverable on a repeat build too.
    for code,info in markets.items():
        for kind in ('home','finder'):
            route=info[kind];text=(ROOT/html_path(route)).read_text(encoding='utf-8')
            title=re.search(r'<title>(.*?)</title>',text,re.S)[1].replace(' | GetMacros','')
            description=re.search(r'<meta name="description" content="([^"]*)',text)[1]
            product.PAGES.append(dict(route=route,path=html_path(route),title=title,description=description,kind=kind,market=code,indexable=True))
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';tree=ET.parse(ROOT/'sitemap.xml');root=tree.getroot();existing={x.find(ns+'loc').text:x for x in root}
    entries={p['route']:p for p in product.PAGES}
    for route,p in entries.items():
        url='https://getmacros.net'+route;node=existing.get(url)
        if node is None:node=ET.SubElement(root,ns+'url');ET.SubElement(node,ns+'loc').text=url
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text=DATE
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- global-coverage-search:start -->.*?<!-- global-coverage-search:end -->','',text,flags=re.S)
    group='<section class="search-group" data-group="New country menus"><h2>Country menus &amp; portions <span data-count>'+str(len(entries))+'</span></h2>'+''.join('<a class="search-hit" href="'+e(r)+'" data-search="'+e(x['title'])+'"'+(' data-market="'+x['market']+'"' if x['market'] in markets else '')+'><span class="search-hit-name">'+e(x['title'])+'</span><span class="search-hit-copy">'+e(x['description'])+'</span></a>' for r,x in entries.items())+'</section>'
    write('search.html',text.replace('</main>','<!-- global-coverage-search:start -->'+group+'<!-- global-coverage-search:end --></main>',1))
    with (OUT/'published-pages.csv').open('w',newline='',encoding='utf-8') as file:
        writer=csv.writer(file);writer.writerow(['url','kind','market','status'])
        for route,x in entries.items():writer.writerow(['https://getmacros.net'+route,x['kind'],x['market'],'generated; live verification pending'])
    dump('docs/global-coverage-2026-10-17/integration.json',dict(date=DATE,newRestaurantRecords=len(additions['records']),refreshedRestaurantRecords=len(additions['updates']),registryRecords=len(registry['records']),restaurantsByMarket={code:dict(records=sum(r['market']==code for r in registry['records']),chains=len({r['chain'] for r in registry['records'] if r['market']==code})) for code in markets},pages=list(entries.values())))

def refresh_coverage_article(markets):
    # Update the existing analysis from the installed records, keeping its
    # original publication date distinct from this substantive data update.
    spec=importlib.util.spec_from_file_location('current_coverage_editorial',ROOT/'tools/clarity_release/editorial.py')
    ed=importlib.util.module_from_spec(spec);spec.loader.exec_module(ed)
    ed.COUNTRIES={code:info['name'] for code,info in markets.items()}
    rows,_=ed.new_articles();row=next(r for r in rows if r['route']=='/international-menu-data-coverage-explained.html')
    row['description']='Compare coverage across '+str(len(markets))+' markets, with exact tracked-record, finder, macro and fiber counts. Catalogue coverage does not rank countries or national diets.'
    row['body']=row['body'].replace('October 14, 2026; tracked source rows','October 17, 2026; tracked source rows')
    template=(ROOT/'about.html').read_text(encoding='utf-8')
    text=ed.render(row,template).replace('Published October 14, 2026</p>','Published October 14, 2026 · Coverage updated October 17, 2026</p>')
    def schema(match):
        data=json.loads(match[1]);items=data if isinstance(data,list) else [data]
        for item in items:
            if item.get('@type')=='Article':item['dateModified']=DATE
        return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,text,flags=re.S)
    write(html_path(row['route']),text)
    product.PAGES.append(dict(route=row['route'],path=html_path(row['route']),title=row['title'],description=row['description'],kind='article-updated',market='global',indexable=True))

def build():
    OUT.mkdir(parents=True,exist_ok=True);product.PAGES.clear()
    additions,registry,markets,presence=integrate()
    flag_path=ROOT/'images/market-flags.svg';flags=flag_path.read_text(encoding='utf-8')
    drawings={
        'FR':'<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#002654" d="M0 0h10v20H0z"/><path fill="#ed2939" d="M20 0h10v20H20z"/>',
        'IN':'<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#ff9933" d="M0 0h30v6.67H0z"/><path fill="#138808" d="M0 13.33h30V20H0z"/><circle cx="15" cy="10" r="2.5" fill="none" stroke="#000080" stroke-width=".4"/>'+''.join('<path d="M15 10v-2.5" stroke="#000080" stroke-width=".18" transform="rotate('+str(i*15)+' 15 10)"/>' for i in range(24)),
        'SG':'<path fill="#fff" d="M0 0h30v20H0z"/><path fill="#ef3340" d="M0 0h30v10H0z"/><circle cx="6" cy="5" r="3.5" fill="#fff"/><circle cx="7.3" cy="4.5" r="3" fill="#ef3340"/>'+''.join('<path fill="#fff" d="m0-1 .3.7.8.1-.6.5.2.8-.7-.4-.7.4.2-.8-.6-.5.8-.1z" transform="translate('+str(x)+' '+str(y)+')"/>' for x,y in [(10,2.6),(12,4),(11.3,6.4),(8.8,6.4),(8.2,4)]),
        'ZA':'<path fill="#de3831" d="M0 0h30v10H0z"/><path fill="#002395" d="M0 10h30v10H0z"/><path fill="#fff" d="M0 0h4l10 6h16v8H14L4 20H0z"/><path fill="#007a4d" d="M0 0l14 8h16v4H14L0 20z"/><path fill="#ffb612" d="m0 1 13 9L0 19z"/><path fill="#000" d="m0 3 10 7L0 17z"/>',
    }
    for code,drawing in drawings.items():
        if code in markets and 'id="flag-'+code+'"' not in flags:flags=flags.replace('</svg>','<symbol id="flag-'+code+'" viewBox="0 0 30 20">'+drawing+'</symbol></svg>')
    flag_path.write_text(flags,encoding='utf-8')
    guides(additions,registry,markets,presence)
    refresh_coverage_article(markets)
    from build_master_completion import coverage,regional_annotations
    product.MARKETS.update(markets);coverage()
    from build_master_interface import build as shared_home
    shared_home()
    from build_visible_workspace import build as workspace
    workspace()
    if 'IN' in markets:
        path=html_path(markets['IN']['home']);text=(ROOT/path).read_text(encoding='utf-8')
        text=text.replace('India menus ·','North &amp; East India · McDonald’s ·')
        write(path,text)
    regional_annotations()
    metadata_and_manifest(markets,additions,registry)
    print('Integrated',len(additions['records']),'new restaurant records;',len(additions['updates']),'source refreshes; all-brand groceries across existing markets.')

if __name__=='__main__':build()
