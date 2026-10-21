"""Search landing-page repairs from the October 21 Search Console review.

This pass owns presentation and discovery, never nutrient records or rankings.
Run after the existing presentation build and before search/asset generation.
"""
from collections import defaultdict
from html import escape
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_flagship_release import markets, find, replace
from build_global_coverage_release import eligible, html_path, table
from normalize_calculator_layouts import Document

ROOT = Path(__file__).resolve().parents[2]
DATE = '2026-10-21'
BASE = 'https://getmacros.net'
e = lambda value: escape(str(value), quote=True)


def metadata(text, title, description):
    title += ' | GetMacros'
    text = re.sub(r'<title>.*?</title>', '<title>'+e(title)+'</title>', text, count=1)
    for n in sorted(Document(text).nodes, key=lambda n:n['start'], reverse=True):
        if n['tag'] != 'meta': continue
        key = n['attrs'].get('name') or n['attrs'].get('property')
        value = title if key in ('og:title','twitter:title') else description if key in ('description','og:description','twitter:description') else None
        if value is not None:
            tag = re.sub(r'content="[^"]*"', 'content="'+e(value)+'"', text[n['start']:n['end']])
            text = replace(text,n,tag)
    return text


def app_schema(text, title, description):
    for n in sorted(Document(text).nodes,key=lambda n:n['start'],reverse=True):
        if n['tag']!='script' or n['attrs'].get('type')!='application/ld+json':continue
        value=json.loads(text[n['inner']:n['close']])
        if isinstance(value,dict) and value.get('@type') in ('WebApplication','CollectionPage'):
            value.update(name=title,description=description,dateModified=DATE)
            text=text[:n['inner']]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+text[n['close']:]
    return text


def individual_examples(rows, limit=12):
    """A diverse editorial sample of individual mains, not catering rankings.

    Explicit published values only. Limits describe this collection, not health
    targets; the complete finder retains every supported portion unchanged.
    """
    groups = defaultdict(list)
    for r in rows:
        if not eligible(r) or r.get('category') not in (None,'entree','breakfast'): continue
        if any(r.get(k) is None for k in ('cal','p','c','fat')): continue
        if not (250 <= r['cal'] <= 900 and r['p'] >= 25): continue
        if (r.get('servingGrams') or 0) > 800: continue
        if re.search(r'\b(catering|sharing|party|platter|bucket|family|[2-9] pack)\b', r['name'], re.I): continue
        groups[r['chain']].append(r)
    for group in groups.values(): group.sort(key=lambda r:(r['cal'],r['name'],r.get('id','')))
    result=[]
    # Two rounds give different chains a place before repeating one brand.
    for index in range(2):
        for brand in sorted(groups):
            if len(groups[brand]) > index: result.append(groups[brand][index])
            if len(result) == limit: return result
    return result


def strip_block(text, key):
    return re.sub(r'<!-- '+key+r':start -->.*?<!-- '+key+r':end -->','',text,flags=re.S)


def block(key, body):
    return '<!-- '+key+':start -->'+body+'<!-- '+key+':end -->'


def local_links(rows):
    guides={}
    for r in rows:
        if r.get('url'): guides.setdefault(r['chain'],'/'+r['url'].lstrip('/'))
    return '<ul>'+''.join('<li><a href="'+e(url)+'">'+e(chain)+' nutrition &amp; portions</a></li>' for chain,url in sorted(guides.items()))+'</ul>'


def sourced_table(rows):
    content=table(rows,'Exact local source servings. The calorie range is an editorial selection, not a personal target or a healthiest-food ranking.')
    source_rows=iter(rows)
    def add_source(match):
        row=next(source_rows)
        return match[0].replace('</small>','</small><a href="'+e(row['source'])+'">Official nutrition source</a>',1)
    return re.sub(r'<tr><th scope="row">.*?</th>',add_source,content,flags=re.S)


def apply():
    registry=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    changed=set(); report=[]
    for code,info in markets().items():
        rows=[r for r in registry if r['market']==code and eligible(r)]
        chains=sorted({r['chain'] for r in rows})
        country='UK' if code=='GB' else info['name']
        path=ROOT/html_path(info['finder']); text=path.read_text(encoding='utf-8')
        title=country+' Fast Food Nutrition & Meal Finder' if code!='US' else 'Fast Food Meal Finder: Calories & Protein'
        description='Compare '+f'{len(rows):,}'+' '+country+' restaurant menu portions across '+str(len(chains))+' chains. Filter calories and protein, check serving sizes, and compare or log your order.'
        text=metadata(text,title,description)
        text=app_schema(text,title,description)
        # Preserve the full no-script source-order links and their identities;
        # the old source batch is a selection of the now larger integrated catalog.
        text=text.replace('<h2>All recorded orders</h2>','<h2>Selected source orders</h2>')
        text=strip_block(text,'local-menu-context')
        head=find(text,'finder-page-head') or find(text,'finder-introduction') or find(text,'market-page-head')
        if head:
            fragment=text[head['start']:head['end']]
            fragment=re.sub(r'<h1\b[^>]*>.*?</h1>','<h1>'+e(country+' restaurant calories & protein')+'</h1>',fragment,count=1,flags=re.S)
            # Current presentation may have an older generic paragraph.
            fragment=re.sub(r'<p>.*?</p>','',fragment,flags=re.S)
            fragment=fragment.replace('</h1>','</h1><p>'+e(f'{len(rows):,} source-defined menu portions from {len(chains)} chains. Choose a meal, compare the serving, then save or log it.')+'</p>',1)
            text=replace(text,head,fragment)
        complete=sum(all(r.get(k) is not None for k in ('cal','p','c','fat')) for r in rows)
        completeness=('<p>'+f'{complete:,}'+' portions have complete calories, protein, carbs and fat. The other '+str(len(rows)-complete)+' have missing values; use “Include missing macros” in the filters to view those partial records.</p>') if complete<len(rows) else ''
        context='<section class="food-reading" aria-labelledby="local-menu-heading"><h2 id="local-menu-heading">'+e(country)+' restaurant nutrition guides</h2><p>Open a restaurant’s local table for portions, ingredients where supplied, and official sources. A listed main is not a complete meal unless its sides and drink are included.</p>'+completeness+local_links(rows)+'<p><a href="'+e(info['collection'])+'">Compare high-protein options</a> · <a href="'+e(info['restaurants'])+'">See all restaurant coverage</a></p><p>Unknown nutrients remain unknown. These records are a sourced menu selection, not a claim to cover every current item or location.</p></section>'
        main=next(n for n in Document(text).nodes if n['tag']=='main')
        text=text[:main['close']]+block('local-menu-context',context)+text[main['close']:]
        path.write_text(text,encoding='utf-8'); changed.add(info['finder'])

        # The established U.S. collection is a richer guide and retains its
        # authored sections. Every other existing market gets useful local
        # examples instead of sorting huge catering portions to the top.
        if code!='US':
            selected=individual_examples(rows)
            cp=ROOT/html_path(info['collection']); content=cp.read_text(encoding='utf-8')
            main=next(n for n in Document(content).nodes if n['tag']=='main')
            display=[dict(r,name=r['chain']+' — '+r['name']) for r in selected]
            intro='<header class="food-app-head"><div><h1>High-protein fast food in '+e('the UK' if code=='GB' else country)+'</h1><p>Compare individual restaurant portions with at least 25 g protein and 250–900 calories. This selection includes mains and breakfast items, with up to two examples per chain.</p></div></header>'
            selection=sourced_table(display) if selected else '<p>No supported individual portions meet this collection’s stated limits. Browse the local finder for other known servings.</p>'
            body='<article class="food-app food-reading">'+intro+'<p>'+e(info.get('officialOperatorScope','Local menus and availability can vary by restaurant.'))+'</p>'+selection+'<section><h2>Build the rest of your order</h2><p>These are the named portions in the table. Add the actual side, sauce and drink separately unless the source explicitly includes them. Sharing packs and catering portions are excluded from this selection, but remain in the full catalog where supported.</p><p><a class="btn btn-primary" href="'+e(info['finder'])+'?minProtein=25">Find a meal with 25 g protein</a> <a href="'+e(info['restaurants'])+'">Browse '+e(country)+' restaurants</a></p></section><section><h2>Check the local menu</h2>'+local_links(selected)+'<p>Values are from the linked local source editions; they are not guarantees of current stock or preparation at a particular location. Open the restaurant guide for dates and source notes.</p></section></article>'
            content=content[:main['inner']]+body+content[main['close']:]
            content=metadata(content,'High-Protein Fast Food '+country+': Calories & Portions','Compare '+country+' restaurant mains and breakfast portions with 25 g+ protein. See local calories, carbs, fat, serving sizes and official nutrition sources.')
            # These eleven collections now serve the same intent and portion
            # scope. The broader U.S. guide is not an equivalent of this list.
            content=re.sub(r'<link rel="alternate"[^>]*>','',content)
            counterparts=''.join('<link rel="alternate" hreflang="en-'+c+'" href="'+BASE+v['collection']+'">' for c,v in markets().items() if c!='US')
            content=content.replace('</head>',counterparts+'</head>',1)
            cp.write_text(content,encoding='utf-8');changed.add(info['collection'])
        report.append({'market':code,'finderPortions':len(rows),'chains':len(chains),'curatedIndividualPortions':len(individual_examples(rows)) if code!='US' else None})

    # Preserve the established guide and its correct worked comparisons.
    p=ROOT/'healthy-fast-food.html';text=p.read_text(encoding='utf-8')
    us=[r for r in registry if r['market']=='US' and eligible(r)];total=len(us);brands=len({r['chain'] for r in us})
    text=re.sub(r'Compare \d+ recorded orders for more protein',f'Compare {total:,} supported menu portions for more protein',text)
    desc=f'Compare {total:,} U.S. fast-food menu portions across {brands} chains. Explore high-protein orders, options under 500 calories and the sides that complete a meal.'
    text=metadata(text,'Healthy Fast Food Options: Calories & Protein',desc)
    text=app_schema(text,'Healthy Fast Food Options: Calories & Protein',desc)
    text=strip_block(text,'fast-food-answer')
    intro='<section class="container" aria-labelledby="fast-food-choice"><h2 id="fast-food-choice">What makes a useful fast-food comparison?</h2><p>Start with the exact order and portion. A grilled sandwich, a rice bowl and a breakfast wrap can each fit different preferences; the full order changes when you add fries, dressing, sauce or a drink. Compare calories and protein together, then check fiber and sodium where reported.</p><p>The finder currently supports '+f'{total:,}'+' U.S. menu portions across '+str(brands)+' chains, including mains, sides, drinks and breakfast items. The lists below are selected examples, not a ranking of the healthiest restaurants or every item on today’s menu.</p><p><a href="/restaurant-meal-finder.html?quiz=1">Find my meal</a> · <a href="/high-protein-fast-food-under-500-calories.html">High-protein orders under 500 calories</a> · <a href="/fast-food-breakfast-protein-comparison.html">Compare breakfast protein</a> · <a href="/gb/en/collections/protein-meals/">UK high-protein options</a> · <a href="/ca/en/collections/protein-meals/">Canadian high-protein options</a></p></section>'
    main=next(n for n in Document(text).nodes if n['tag']=='main')
    # Answer the reader near the start, before the expandable example lists.
    head=find(text,'market-page-head')
    at=head['end'] if head else main['inner']
    text=text[:at]+block('fast-food-answer',intro)+text[at:]
    p.write_text(text,encoding='utf-8');changed.add('/healthy-fast-food.html')

    # A deliberate crawlable path from each shared homepage to its local guide.
    for code,info in markets().items():
        p=ROOT/html_path(info['home']);text=p.read_text(encoding='utf-8');text=strip_block(text,'local-collection-link')
        node=find(text,'home-restaurant-section') or find(text,'home-restaurants')
        if not node:
            node=next((n for n in Document(text).nodes if n['tag']=='section' and 'restaurant-shortcut' in text[n['inner']:n['close']]),None)
        if node:
            target='/healthy-fast-food.html' if code=='US' else info['collection']
            label='Compare healthy fast-food options' if code=='US' else 'Compare high-protein options in '+('the UK' if code=='GB' else info['name'])
            text=text[:node['close']]+block('local-collection-link','<p><a class="text-action" href="'+e(target)+'">'+e(label)+'</a></p>')+text[node['close']:]
            p.write_text(text,encoding='utf-8');changed.add(info['home'])
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    tree=ET.parse(ROOT/'sitemap.xml')
    for n in tree.getroot():
        if n.find(ns+'loc').text in {BASE+r for r in changed}:
            mod=n.find(ns+'lastmod')
            if mod is None:mod=ET.SubElement(n,ns+'lastmod')
            mod.text=DATE
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    out=ROOT/'docs/search-recovery-2026-10-21';out.mkdir(parents=True,exist_ok=True)
    (out/'implementation.json').write_text(json.dumps({'date':DATE,'routes':sorted(changed),'markets':report,'nutritionRecordsChanged':0,'indexing':'Requests and Google decisions tracked separately; a build is not indexing.'},indent=2)+'\n',encoding='utf-8')
    print('Search landing-page repairs:',len(changed),'existing routes; no nutrient changes.')


if __name__=='__main__':apply()
