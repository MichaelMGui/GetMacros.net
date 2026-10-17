from source_json import read_json
"""Publish reviewed additions and a factual source/brand navigator, before shared UI."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlencode
from html import escape
import json, re, xml.etree.ElementTree as ET
import build_global_product as product
from build_master_restaurants import table

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/master-completion-2026-10-13"
DATE="2026-10-13"
def e(value):return escape(str(value),quote=True)
def read(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def dump(path,value):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
def lookup(brand,market):
    return "/food-library.html?"+urlencode(dict(market=market,brand=brand))

def restaurants():
    additions=read("tools/master_completion/restaurant_records.json")["records"]
    for r in additions:r["nutrientBasis"]="per named serving"
    registry=read("js/order-registry.json");ids={r["id"] for r in additions}
    registry["records"]=[r for r in registry["records"] if r.get("id") not in ids]+additions
    dump("js/order-registry.json",registry)
    canada=read("js/canada-meals.json");canada["records"]=[r for r in registry["records"] if r["market"]=="CA"];dump("js/canada-meals.json",canada)
    markets=json.loads(re.search(r"window.GM_MARKETS=(.*);",(ROOT/"js/market-definitions.js").read_text(encoding="utf-8"))[1])
    ca=[r for r in canada["records"] if r.get("category") not in ["component","sauce"] and r.get("finderSupported",True)]
    markets["CA"]["chains"]=sorted({r["chain"] for r in ca})
    (ROOT/"js/market-definitions.js").write_text("window.GM_MARKETS="+json.dumps(markets,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    (ROOT/"js/canada-meals.js").write_text("window.GM_MEALS="+json.dumps(ca,ensure_ascii=False,separators=(",",":"))+";window.GM_THRESHOLDS={protein:25,energy:600,light:400,fibre:5,sodium:600};\n",encoding="utf-8")
    shell=product.subprocess.run(["node","tools/product_release/render-finder.cjs"],input=json.dumps(dict(rows=ca,markets=markets)),encoding="utf-8",capture_output=True,check=True,cwd=ROOT).stdout
    template=(ROOT/"ca/en/find-a-meal/index.html").read_text(encoding="utf-8")
    product.page("/ca/en/find-a-meal/","Canada meal finder: local menus, calories & protein","Compare exact Canadian servings. Filter calories, protein and available nutrients using local sources, with missing values kept visible.",'<header class="finder-page-head"><h1>Find a meal in Canada.</h1><p>Choose an exact Canadian serving, then refine calories and protein.</p></header><section id="meal-quiz" aria-label="Meal finder">'+shell+'</section><noscript><p>Filters need JavaScript. The source meals remain visible below.</p></noscript>',"finder",market="CA",template=template)
    sizes=[r for r in additions if r["name"].startswith("Fries,")];extras=[r for r in additions if r["category"]=="component"];orders=[r for r in additions if r.get("calculatedFrom")]
    body='<article class="food-app food-reading"><header class="food-app-head"><div><h1>New York Fries Canada nutrition.</h1><p>Choose the size, then count the extras.</p></div></header><nav class="food-actions"><a class="btn btn-primary" href="/ca/en/find-a-meal/?chain=New+York+Fries">Find an order →</a><a class="text-action" href="/food-diary.html?market=CA">Log a serving →</a></nav>'
    body+='<section><h2>Snack, regular or large?</h2><p>The Canadian guide gives each size its own weight and values. A regular portion is not two snack orders; use the named size you ordered.</p>'+table(sizes,"Canadian fries sizes; no unlisted condiments, drink or toppings.")+'</section>'
    body+='<section><h2>Hot dog plus fries</h2>'+table(orders,"GetMacros sums two named official servings; these are not separately published restaurant combo values.")+'<p>The snack-fries order is 910 kcal and 28 g protein. The regular-fries order is 1,320 kcal and 33 g protein. Both include one hot dog with its bun; drinks, dips and extra condiments remain separate.</p></section>'
    body+='<details class="food-product-details"><summary>Poutine, hot dogs and the other listed servings</summary>'+table([r for r in additions if r["category"]!="component" and not r.get("calculatedFrom")],"Tracked Canadian servings from the August 20, 2026 guide; not a full live-menu audit.")+'</details>'
    body+='<details class="food-product-details"><summary>Extra toppings and their portions</summary><p>The source defines one extra topping serving for a snack, two for a regular order and three for a large order. Multiply only that extra ingredient: fries and poutine sizes keep their separately published values. An unspecified scoop is not assigned a guessed weight.</p>'+table(extras,"Individual extras, not complete meals. Add only the amount actually supported by the source.")+'</details>'
    body+='<section><h2>Source and recipe limits</h2><p>The <a href="'+e(additions[0]["source"])+'">official Canadian nutrition guide</a> is dated August 20, 2026. Its two rendered pages and the selected values were checked October 13, 2026. Published rounding means component sums may differ from a separately tested order.</p><p>This is Canadian menu information. A U.S. location or a familiar menu name does not establish an identical recipe. Branch availability, preparation and later menu changes can differ; these records do not certify allergen safety.</p><a class="text-action" href="/ca/en/restaurants/">Canadian restaurants →</a></section></article>'
    product.page("/ca/en/restaurants/new-york-fries/","New York Fries Canada nutrition: sizes, poutine & hot-dog orders","Compare Canadian fries sizes, poutine, hot dogs and exact extra portions. See 27 sourced records and two honestly calculated orders from the August 2026 guide.",body,"restaurant",market="CA")
    presence_path=ROOT/"tools/master_completion/restaurant_presence.json"
    if presence_path.exists():
        changes=json.loads(presence_path.read_text(encoding="utf-8"))
        presence=read("data/restaurant-presence.json");byid={r["id"]:r for r in presence["relationships"]}
        for r in changes["relationships"]:byid[r["id"]]=r
        for r in changes["updates"]:
            if r["id"] not in byid:raise ValueError("Unknown presence update "+r["id"])
            byid[r["id"]]={**byid[r["id"]],**r}
        for rel in byid.values():
            matched=[r for r in registry["records"] if r["market"]==rel["country"] and r["chain"]==rel["restaurantBrand"]]
            rel["trackedRecords"]=len(matched)
            rel["completeMacroRecords"]=sum(all(r.get(k) is not None for k in ["cal","p","c","fat"]) for r in matched)
            rel["finderRecords"]=sum(r.get("category") not in ["component","sauce"] and r.get("finderSupported",True) for r in matched)
            rel["finderSupported"]=rel["finderRecords"]>0
            rel["calculatedOrders"]=sum(bool(r.get("calculatedFrom")) for r in matched)
            rel["partialMacroRecords"]=sum(r.get("cal") is not None and any(r.get(k) is None for k in ["p","c","fat"]) and any(r.get(k) is not None for k in ["p","c","fat"]) for r in matched)
            rel["caloriesOnlyRecords"]=sum(r.get("cal") is not None and all(r.get(k) is None for k in ["p","c","fat"]) for r in matched)
            if matched:rel["coverageStatus"]="tracked-macro-selection" if rel["finderSupported"] else "calories-only"
            if rel["country"]=="CA" and rel["restaurantBrand"]=="New York Fries":
                rel.update(nutritionAvailable=True,nutritionSourceStatus="official-table-reviewed",nutritionSources=[additions[0]["source"]],localMenuSource=additions[0]["sourceParent"],lastCheckedDate=DATE,limitations="Canadian named servings and exact extras; tracked selection, not a complete live menu or inventory.")
                rel["presence"]["observation"]="Official locator distinguishes Canadian from overseas stores. Canadian source servings are published separately from U.S. menus."
        presence["relationships"]=list(byid.values());presence["checkedAt"]=DATE
        dump("data/restaurant-presence.json",presence)
    else:presence=read("data/restaurant-presence.json")
    listing=[]
    for rel in sorted([r for r in presence["relationships"] if r["country"]=="CA"],key=lambda r:r["restaurantBrand"]):
        rows=[r for r in registry["records"] if r["market"]=="CA" and r["chain"]==rel["restaurantBrand"]]
        href=rows[0]["url"] if rows else rel["officialCountryWebsite"]
        copy=f'{len(rows)} tracked servings. '+("Complete macros are unavailable; calorie-only servings stay outside the macro finder." if rows and not rel.get("finderSupported") else "Check the named serving and source edition.") if rows else "Operates in Canada. Local nutrition records are not yet available here."
        listing.append('<article class="presence-row"><div><h2><a href="'+e(href)+'">'+e(rel["restaurantBrand"])+'</a></h2><p>'+copy+'</p></div><a class="text-action" href="'+e(href)+'">'+("View servings" if rows else "Official Canadian site")+' →</a></article>')
    product.page("/ca/en/restaurants/","Canadian restaurant nutrition: chains, menus & coverage","Browse Canadian restaurant operations and local nutrition sources. Tracked servings remain separate from full-menu coverage, including New York Fries, Subway and Canadian pizza chains.",'<section class="food-app"><header class="food-app-head"><div><h1>Restaurants in Canada.</h1><p>Local menus, wherever the chain began.</p></div></header><div class="restaurant-presence-list">'+''.join(listing)+'</div><details class="food-product-details"><summary>What coverage means</summary><p>Operating here, having an accessible local nutrition source and supporting the finder are different things. Unsupported chains link to their official Canadian sites; no U.S. values are substituted.</p><a href="/world-restaurant-menus.html">Other published countries →</a></details></section>',"restaurant-index",market="CA")
    for code,info in markets.items():
        if code in ["US","CA"]:continue
        p=ROOT/(info["restaurants"].strip("/")+"/index.html");text=p.read_text(encoding="utf-8")
        text=re.sub(r"<!-- presence-links:start -->.*?<!-- presence-links:end -->","",text,flags=re.S)
        unsupported=[r for r in presence["relationships"] if r["country"]==code and not r["trackedRecords"]]
        module='<!-- presence-links:start --><details class="food-product-details"><summary>Other chains operating here</summary><p>Official local links. Nutrition coverage is not published here yet; another country’s values are not substituted.</p><ul>'+''.join('<li><a href="'+e(r["officialCountryWebsite"])+'">'+e(r["restaurantBrand"])+'</a></li>' for r in sorted(unsupported,key=lambda r:r["restaurantBrand"]))+'</ul></details><!-- presence-links:end -->'
        text=text.replace("</main>",module+"</main>",1);p.write_text(text,encoding="utf-8")
    country_rows=[]
    for code,info in markets.items():
        rows=[r for r in registry["records"] if r["market"]==code]
        supported=[r for r in rows if r.get("category") not in ["component","sauce"] and r.get("finderSupported",True)]
        chains=sorted({r["chain"] for r in rows})
        country_rows.append('<article><h2><a class="text-action" href="'+info["home"]+'">'+e(info["name"])+' →</a></h2><p>'+e(info["continent"])+' · '+str(len(rows))+' tracked servings; '+str(len(supported))+' finder entries.</p><p>'+e(", ".join(chains))+'</p><a class="text-action" href="'+info["restaurants"]+'">Local chains &amp; coverage →</a></article>')
    product.page("/world-restaurant-menus.html","Restaurant nutrition by country: local menus & source coverage","Browse eight published restaurant markets with actual local servings, operations links, source coverage and country comparisons. U.S. values are not substituted abroad.",'<section class="food-app"><header class="food-app-head"><div><h1>Menus around the world.</h1><p>Choose the country where you are ordering.</p></div></header><div class="food-directory">'+''.join(country_rows)+'</div><a class="text-action" href="/compare-menu-ingredients-worldwide.html">Compare country ingredients →</a><details class="food-product-details"><summary>What the numbers mean</summary><p>Tracked servings can include components; finder entries exclude components and unsupported records. These are source-edition selections, not every local menu or a live availability service. A confirmed local chain can appear in the directory before it has usable nutrition records.</p><a href="/food-library-sources.html">Sources &amp; limits →</a></details></section>',"directory")
    dump("docs/master-completion-2026-10-13/restaurant-integration.json",dict(newRecords=len(additions),canadaRecords=len(canada["records"]),canadaFinder=len(ca),registryRecords=len(registry["records"]),newOfficial=sum(not r.get("calculatedFrom") for r in additions),newCalculated=sum(bool(r.get("calculatedFrom")) for r in additions)))

def coverage():
    """Counts are from actual published records; provider totals are not our coverage."""
    markets=product.MARKETS
    sources=[];counts=Counter();brands={k:Counter() for k in markets};examples={}
    for directory in sorted((ROOT/"data/branded-foods").iterdir()):
        if not (directory/"manifest.json").exists():continue
        manifest=json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
        own=Counter()
        if manifest.get('brandCountsPrefix'):
            # Counts are generated and audited from every source record at
            # ingestion. Do not decompress the entire catalogue to render links.
            for market,total in manifest['markets'].items():
                local=read_json(directory/manifest['brandCountsPrefix']/(market+'.json'))
                assert sum(local.values())==total
                own[market]=total;counts[market]+=total
                brands.setdefault(market,Counter()).update(local)
        else:
            for shard in manifest["recordShards"]:
                for r in read_json(directory/"records"/(shard+".json")):
                    if r["type"]!="branded":continue
                    own[r["market"]]+=1;counts[r["market"]]+=1;brands.setdefault(r["market"],Counter())[r["brand"]]+=1
        sources.append(dict(id=directory.name,count=manifest["profileCount"],markets=dict(own),source=manifest["source"]))
    sections=[]
    preferred={
        "CA":["Kirkland Signature","Great Value","President’s Choice","President's Choice","No Name","Compliments","Selection","Irresistibles","Our Finest","Western Family","Oreo"],
        "US":["Kirkland Signature","Great Value","Trader Joe's","Good & Gather","Market Pantry","365 Everyday Value","Simple Truth","Kroger","Member's Mark","Signature Select","Oreo"]}
    for code,info in markets.items():
        raw=brands.get(code,{})
        # Collapse capitalization/punctuation variants only in navigation. Source
        # products, formulations, packages and named sub-brands remain separate.
        key=lambda name:re.sub(r"[^a-z0-9]","",name.casefold())
        grouped=Counter();labels={}
        for name,count in raw.items():grouped[key(name)]+=count;labels.setdefault(key(name),name)
        desired=[]
        for target in preferred.get(code,[]):
            if key(target) in grouped and key(target) not in desired:desired.append(key(target));labels[key(target)]=target
        topkeys=list(dict.fromkeys(desired+[name for name,_ in grouped.most_common(12)]))[:12]
        b={labels[name]:grouped[name] for name in topkeys};top=list(b)
        total=counts[code]
        if total:
            def brand_links(names):return '<ul class="food-brand-links">'+''.join('<li><a class="text-action" href="'+e(lookup(name,code))+'"><span>'+e(name)+'</span><small>'+f'{b[name]:,}'+' source records</small></a></li>' for name in names)+'</ul>'
            links=brand_links(top[:6])+('<details class="food-product-details"><summary>More represented brands</summary>'+brand_links(top[6:])+'</details>' if len(top)>6 else '')
            copy=f'{total:,} packaged label profiles.'
        else:
            links='<p>Packaged-product coverage is not published here yet. <a href="/food-diary.html?market='+code+'">Log reference ingredients or supported local menu servings</a>.</p>'
            copy="No packaged labels are published for this market. Another country's label is not substituted."
        sections.append('<section id="grocery-'+code.lower()+'"><h2>'+e(info["name"])+'</h2><p>'+copy+'</p>'+links+'</section>')
    source_rows=[]
    for s in sources:
        source=s["source"];name=source.get("name") or s["id"];url=source.get("url") or source.get("downloadUrl") or "/food-library-sources.html"
        source_rows.append('<tr><th scope="row"><a href="'+e(url)+'">'+e(name)+'</a></th><td>'+f'{s["count"]:,}'+'</td><td>'+e(source.get("license") or "See source rights")+'</td></tr>')
    body='<article class="food-app food-reading"><header class="food-app-head"><div><h1>Find the right package.</h1><p>Browse the brands actually represented in each country.</p></div></header><nav class="food-actions" aria-label="Grocery tools"><a class="btn btn-primary" href="/food-library.html">Search food →</a><a class="text-action" href="/how-to-log-food-portions.html">Check a portion →</a></nav>'
    body+='<p>A familiar brand name is a starting point. Match the product, flavour, country, serving and source edition to the package you have. Imports are not independent package verification. Counts include distinct source versions and packages, not warehouse inventory.</p>'
    body+='<nav class="food-actions" aria-label="Published grocery markets">'+''.join('<a class="text-action" href="#grocery-'+code.lower()+'">'+e(info["name"])+'</a>' for code,info in markets.items())+'</nav>'+''.join(sections)
    body+='<section><h2>Where the records come from</h2><div class="table-wrap" tabindex="0" role="region" aria-label="Food source coverage"><table><caption>Published source records, including reference foods where identified.</caption><thead><tr><th scope="col">Source</th><th scope="col">Records</th><th scope="col">Rights</th></tr></thead><tbody>'+''.join(source_rows)+'</tbody></table></div><p>Source datasets remain separate. We do not copy a proprietary food app database or treat a community import as verified. Missing nutrients remain unavailable.</p>'
    body+='<p>Costco’s online listings do not establish availability in every warehouse. Store-brand names do not imply endorsement, a partnership or real-time inventory.</p><a class="text-action" href="/food-library-sources.html">Sources, units &amp; licensing →</a></section></article>'
    product.page("/grocery-food-coverage.html","Grocery food lookup: Canadian & U.S. brands, sources and portions","Find represented grocery brands by country. Match real product labels and servings, see source coverage and search without substituting another market’s nutrition.",body,"guide")
    dump("docs/master-completion-2026-10-13/grocery-coverage.json",dict(date=DATE,byMarket=dict(counts),brandCounts={k:len(v) for k,v in brands.items()},sources=sources))
    return counts

def link_resources():
    # Fixed marker makes repeat builds replace, rather than duplicate, the module.
    for name in ["food-library-sources.html","how-to-log-food-portions.html"]:
        path=ROOT/name;text=path.read_text(encoding="utf-8")
        text=re.sub(r"<!-- grocery-coverage:start -->.*?<!-- grocery-coverage:end -->","",text,flags=re.S)
        section='<!-- grocery-coverage:start --><section class="food-guide-section"><h2>Brands by country</h2><p>Check which label sources and grocery brands are available, then search the exact package.</p><a class="text-action" href="/grocery-food-coverage.html">Browse grocery coverage →</a></section><!-- grocery-coverage:end -->'
        text=text.replace("</main>",section+"</main>",1);path.write_text(text,encoding="utf-8")
    # Real public-domain link, not a public diary query or personal input.
    path=ROOT/"search.html";text=path.read_text(encoding="utf-8")
    text=re.sub(r"<!-- master-completion-search:start -->.*?<!-- master-completion-search:end -->","",text,flags=re.S)
    entries=[p for p in product.PAGES]
    text=text.replace("</main>",'<!-- master-completion-search:start --><section class="search-group" data-group="Packages & local menus"><h2>Packages &amp; local menus <span data-count>'+str(len(entries))+'</span></h2>'+''.join('<a class="search-hit"'+(' data-market="'+e(p["market"])+'"' if p["market"] in product.MARKETS else '')+' href="'+e(p["route"])+'" data-search="'+e(p["title"])+'"><span class="search-hit-name">'+e(p["title"])+'</span><span class="search-hit-copy">'+e(p["description"])+'</span></a>' for p in entries)+'</section><!-- master-completion-search:end --></main>',1);path.write_text(text,encoding="utf-8")
    ns="{http://www.sitemaps.org/schemas/sitemap/0.9}";tree=ET.parse(ROOT/"sitemap.xml");root=tree.getroot();urls={n.find(ns+"loc").text:n for n in root}
    for p in entries:
        if not p["indexable"]:continue
        url="https://getmacros.net"+p["route"];node=urls.get(url)
        if node is None:node=ET.SubElement(root,ns+"url");ET.SubElement(node,ns+"loc").text=url
        mod=node.find(ns+"lastmod")
        if mod is None:mod=ET.SubElement(node,ns+"lastmod")
        mod.text=DATE
    ET.register_namespace("",ns[1:-1]);tree.write(ROOT/"sitemap.xml",encoding="utf-8",xml_declaration=True)

def regional_annotations():
    # page() deliberately clears inherited alternates. Restore only genuine
    # equivalent regional home/finder/directory sets after all late replacements.
    markets=json.loads(re.search(r"window.GM_MARKETS=(.*);",(ROOT/"js/market-definitions.js").read_text(encoding="utf-8"))[1])
    for kind in ["home","finder","restaurants"]:
        links=''.join('<link rel="alternate" hreflang="en-'+code+'" href="https://getmacros.net'+info[kind]+'">' for code,info in markets.items())+'<link rel="alternate" hreflang="x-default" href="https://getmacros.net'+markets["US"][kind]+'">'
        for info in markets.values():
            route=info[kind];p=ROOT/("index.html" if route=="/" else route.strip("/")+"/index.html" if route.endswith("/") else route.lstrip("/"))
            text=p.read_text(encoding="utf-8");text=re.sub(r'<link\b[^>]*hreflang="[^"]*"[^>]*>',"",text)
            p.write_text(text.replace("</head>",links+"</head>",1),encoding="utf-8")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    restaurants()
    counts=coverage()
    link_resources()
    regional_annotations()
    dump("docs/master-completion-2026-10-13/published-manifest.json",product.PAGES)
    print("Published grocery navigator from actual source partitions:",dict(counts))
if __name__=="__main__":main()
