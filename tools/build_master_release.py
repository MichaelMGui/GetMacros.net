"""Integrate the reviewed master-release data before shared design and asset stamps."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json,re,subprocess,xml.etree.ElementTree as ET
import build_global_product as product
from build_master_restaurants import build as restaurant_guides

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/master-release-2026-10-12'
DATE='2026-10-12'
def dump(path,data):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
def e(x):return escape(str(x),quote=True)
def complete(r):return all(isinstance(r.get(k),(int,float)) and r[k]>=0 for k in ['cal','p','c','fat'])

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    registry=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))
    additions=json.loads((ROOT/'tools/master_release/restaurant_records.json').read_text(encoding='utf-8'))['records']
    ids={r['id'] for r in additions}
    for r in additions:
        r['nutrientBasis']='per named serving'
    registry['records']=[r for r in registry['records'] if r.get('id') not in ids]+additions
    dump('js/order-registry.json',registry)
    canada_source=json.loads((ROOT/'js/canada-meals.json').read_text(encoding='utf-8'))
    canada_source['records']=[r for r in registry['records'] if r['market']=='CA']
    dump('js/canada-meals.json',canada_source)
    markets=json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
    for code,info in markets.items():
        info['chains']=sorted({r['chain'] for r in registry['records'] if r['market']==code and r.get('category')!='component' and r.get('finderSupported',True)})
    (ROOT/'js/market-definitions.js').write_text('window.GM_MARKETS='+json.dumps(markets,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    restaurant_guides(lambda route,title,description,**kw: product.page(route,title,description,**kw))
    presence=json.loads((ROOT/'data/restaurant-presence.json').read_text(encoding='utf-8'))
    ca=[r for r in registry['records'] if r['market']=='CA' and r.get('category')!='component' and r.get('finderSupported',True)]
    (ROOT/'js/canada-meals.js').write_text('window.GM_MEALS='+json.dumps(ca,ensure_ascii=False,separators=(',',':'))+';window.GM_THRESHOLDS={protein:25,energy:600,light:400,fibre:5,sodium:600};\n',encoding='utf-8')
    template=(ROOT/'ca/en/find-a-meal/index.html').read_text(encoding='utf-8')
    shell=subprocess.run(['node','tools/product_release/render-finder.cjs'],input=json.dumps({'rows':ca,'markets':markets},ensure_ascii=False),encoding='utf-8',capture_output=True,check=True,cwd=ROOT).stdout
    body='<header class="finder-page-head"><h1>Find a meal in Canada.</h1><p>Choose an exact Canadian serving, then refine calories and protein.</p></header><section id="meal-quiz" aria-label="Meal finder">'+shell+'</section><noscript><p>Filters need JavaScript. The source meals remain visible below.</p></noscript>'
    product.page('/ca/en/find-a-meal/','Canada meal finder: local menus, calories & protein','Compare source-defined Canadian restaurant servings. Filter calories, protein and available nutrients without substituting U.S. menu values.',body,'finder',market='CA',template=template)
    # Guide links and evidence for chains without published macro records.
    rows=sorted([r for r in presence['relationships'] if r['country']=='CA'],key=lambda r:r['restaurantBrand'])
    groups=[]
    for r in rows:
        matches=[x for x in registry['records'] if x['market']=='CA' and x['chain']==r['restaurantBrand']]
        href=matches[0]['url'] if matches else r['officialCountryWebsite']
        if matches:
            copy=str(len(matches))+' tracked servings. '+('Complete macros are unavailable; calorie-only servings stay outside the macro finder.' if not r['finderSupported'] else 'Check the exact recipe and source edition.')
        else:copy='Operates in Canada. Nutrition records are not yet available in GetMacros.'
        groups.append('<article class="presence-row"><div><h2><a href="'+e(href)+'">'+e(r['restaurantBrand'])+'</a></h2><p>'+e(copy)+'</p></div><a class="text-action" href="'+e(href)+'">'+('View servings' if matches else 'Official Canadian site')+' →</a></article>')
    body='<section class="food-app"><header class="food-app-head"><div><h1>Restaurants in Canada.</h1><p>Local menus, regardless of where the chain began.</p></div></header><div class="restaurant-presence-list">'+''.join(groups)+'</div><details class="food-product-details"><summary>What the coverage means</summary><p>Operating in Canada, publishing Canadian nutrition and having usable GetMacros records are different things. These links reflect the cited country websites and tracked menu sources; they are not a full live-menu or branch-availability audit.</p><a href="/world-restaurant-menus.html">Other published countries →</a></details></section>'
    product.page('/ca/en/restaurants/','Canadian restaurant nutrition: chains, menus & coverage','Browse Canadian restaurant menus and official local sources. Find tracked Subway, Domino’s, Mary Brown’s, Booster Juice, Tim Hortons, A&W, Harvey’s and pizza servings.',body,'restaurant-index',market='CA')
    # Useful logging guide; no page is generated for each barcode or filter state.
    body='''<article class="food-app food-reading"><header class="food-app-head"><div><h1>Log the portion you ate.</h1><p>Match the food first. Check the amount second.</p></div></header><section><h2>1. Find the right food</h2><p>Search the name, brand or barcode in the <a href="/food-library.html">food library</a>. For a restaurant, choose the country you ordered in. Check raw versus cooked preparation, flavour, recipe and package before selecting a record.</p><p>A barcode identifies the imported package record. It does not prove that a formulation is unchanged or that a product is stocked at your local warehouse.</p></section><section><h2>2. Choose a supported serving</h2><p>Use grams when you weighed the food, or a household measure with a source gram weight. For restaurant records, a named serving may be the only supported unit. Millilitres do not become grams without a source density or portion weight.</p><p>For example, the <a href="https://fdc.nal.usda.gov/food-details/171413/nutrients">historical USDA olive-oil profile</a> gives 884 kcal per 100 g. A weighed 13.5 g portion is 884 × 13.5 ÷ 100 = 119.34 kcal. Another source edition can report a different value; keep that edition attached to the entry.</p></section><section><h2>3. Review, then add</h2><p>Check the food, country, portion, calories and macros. Choose breakfast, lunch, dinner or snack. The <a href="/food-diary.html">diary</a> saves the reviewed source snapshot in this browser. Editing the amount uses those saved values; later menu imports cannot silently rewrite yesterday’s log.</p></section><section><h2>4. Keep missing values visible</h2><p>A blank nutrient is unknown, not zero. If one logged slice has calories but no protein information, the day’s protein figure is a known subtotal, not a complete total.</p></section><section><h2>Recipes, repeats and backups</h2><p>Add each reviewed ingredient to a recipe and enter the number of servings in the whole batch. Oil and sauces need their own entries when you want them counted. Recipe nutrients remain unknown wherever an ingredient lacks that field.</p><p>Recent foods and favorites reopen the saved portion for review. Preferences contains export, validated import and deletion. There is no account or cloud synchronization; export before clearing browser data.</p></section><nav class="food-actions"><a class="btn btn-primary" href="/food-diary.html">Add food →</a><a class="text-action" href="/food-library-sources.html">Sources &amp; units →</a></nav></article>'''
    product.page('/how-to-log-food-portions.html','How to log food: barcodes, grams, recipes & missing macros','Match a food, choose its source-supported portion and keep unknown nutrients visible. Worked oil calculation, restaurant markets, recipes and private diary backups.',body,'guide')
    # Source-specific licenses stay separate; imports are not independent verification.
    p=ROOT/'food-library-sources.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- master-food-sources:start -->.*?<!-- master-food-sources:end -->','',text,flags=re.S)
    sources='''<!-- master-food-sources:start --><section class="food-guide-section"><h2>Packaged groceries and Canadian references</h2><p>USDA Branded Food Data uses manufacturer/provider label information. Records are imported, not independently verified by GetMacros or an endorsement from USDA. Match the market, barcode, flavour, serving and label date. Imported availability does not establish present warehouse inventory.</p><p><a href="/data/branded-foods/usda/manifest.json">USDA branded edition and coverage</a> · <a href="/data/branded-foods/usda/license.txt">Public-domain/CC0 source license</a> · <a href="https://fdc.nal.usda.gov/download-datasets/">Official downloads</a></p><p>The Canadian Nutrient File reference partition uses Health Canada’s published 2026 release, with underlying nutrient and household-measure dates preserved. It is a reference dataset, not a catalogue of Canadian store-brand products.</p><p><a href="/data/branded-foods/cnf/manifest.json">Canadian reference coverage</a> · <a href="/data/branded-foods/cnf/license.txt">Open Government Licence—Canada attribution</a> · <a href="https://open.canada.ca/data/en/dataset/1b6139bd-ed7e-4043-bc28-ff00e10f3109">Official source</a></p><p>Open Food Facts was researched but is not republished in this release. Its database and image licensing differ; its records are not silently blended into these partitions.</p><a href="/how-to-log-food-portions.html">How to log a source portion →</a></section><!-- master-food-sources:end -->'''
    sources=sources.replace('/license.txt','/LICENSE.txt')
    sources=sources.replace('Open Food Facts was researched but is not republished in this release. Its database and image licensing differ; its records are not silently blended into these partitions.','Open Food Facts is not used in this library. Its database and image licensing differ from the sources above.')
    sources=sources.replace('<p>Open Food Facts was researched', '<p>Four Canadian Kirkland products use factual nutrition tables from official Costco Canada and Business Centre product pages, with named servings and source item identifiers. They are not a licensed full Costco catalogue or live warehouse inventory. <a href="/data/branded-foods/retailer-ca/manifest.json">Canadian retailer-label coverage</a> · <a href="/data/branded-foods/retailer-ca/RIGHTS.txt">Rights and limitations</a>.</p><p>Open Food Facts was researched')
    p.write_text(text.replace('</main>',sources+'</main>'),encoding='utf-8')
    # Copied homepage shells are not language alternates of games or general articles.
    for path in list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html')):
        source=path.read_text(encoding='utf-8')
        source=re.sub(r'<link\b(?=[^>]*\bhreflang=)[^>]*>','',source)
        path.write_text(source,encoding='utf-8')
    # Restore genuine reciprocal equivalents after rebuilding Canadian entry pages.
    for kind in ['home','finder','restaurants']:
        annotation=''.join('<link rel="alternate" hreflang="en-'+code+'" href="https://getmacros.net'+info[kind]+'">' for code,info in markets.items())+'<link rel="alternate" hreflang="x-default" href="https://getmacros.net'+markets['US'][kind]+'">'
        for info in markets.values():
            route=info[kind];path=ROOT/('index.html' if route=='/' else route.strip('/')+'/index.html' if route.endswith('/') else route.lstrip('/'))
            source=path.read_text(encoding='utf-8');source=re.sub(r'<link rel="alternate"[^>]*>','',source);path.write_text(source.replace('</head>',annotation+'</head>'),encoding='utf-8')
    sitemap=ET.parse(ROOT/'sitemap.xml');ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';urls={n.find(ns+'loc').text:n for n in sitemap.getroot()}
    for s in product.PAGES:
        url='https://getmacros.net'+s['route'];node=urls.get(url)
        if node is None:node=ET.SubElement(sitemap.getroot(),ns+'url');ET.SubElement(node,ns+'loc').text=url;urls[url]=node
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text=DATE
    ET.register_namespace('',ns[1:-1]);sitemap.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    # New guides are crawlable from the country directory and the existing search.
    p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- master-search:start -->.*?<!-- master-search:end -->','',text,flags=re.S)
    group='<section class="search-group" data-group="Local menus & food logging"><h2>Local menus &amp; food logging <span data-count>'+str(len(product.PAGES))+'</span></h2>'+''.join('<a class="search-hit"'+(' data-market="CA"' if s['market']=='CA' else '')+' href="'+e(s['route'])+'" data-search="'+e(s['title']+' '+s['description'])+'"><span class="search-hit-name">'+e(s['title'])+'</span><span class="search-hit-copy">'+e(s['description'])+'</span></a>' for s in product.PAGES)+'</section>'
    p.write_text(text.replace('</main>','<!-- master-search:start -->'+group+'<!-- master-search:end --></main>'),encoding='utf-8')
    dump('docs/master-release-2026-10-12/published-manifest.json',product.PAGES)
    print('Integrated',len(additions),'new Canadian records;',len(product.PAGES),'new/improved page specs; Canadian finder',len(ca),'supported servings.')
if __name__=='__main__':main()
