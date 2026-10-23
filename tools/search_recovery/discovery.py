"""Useful, crawlable discovery paths for the existing source-backed pages.

Search Console on October 23 showed regional guides as discovered, not crawled.
This improves relevant links and headings; it does not force Google to index.
No new URLs, nutrition records, keywords hidden from readers, or ranking claims.
"""
from pathlib import Path
from html import escape, unescape
import json
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalize_calculator_layouts import Document
from build_flagship_release import markets, find, replace
from build_global_coverage_release import html_path, eligible

ROOT = Path(__file__).resolve().parents[2]
DATE = '2026-10-23'
BASE = 'https://getmacros.net'
e = lambda s: escape(str(s), quote=True)

# Explicit editorial relationships, not guesses based on matching brand names.
RELATED = {
 '/ca/en/restaurants/tim-hortons/': ['tim-hortons-canada-breakfast-muffin-biscuit-wrap', 'tim-hortons-canada-protein-latte-vs-latte'],
 '/ca/en/restaurants/harvey-s/': ['harveys-canada-burger-fries-onion-rings-order'],
 '/gb/en/restaurants/greggs/': ['greggs-breakfast-baguette-calories-protein'],
 '/gb/en/restaurants/kfc/': ['kfc-uk-burger-twister-wrap-nutrition'],
 '/gb/en/restaurants/subway/': ['subway-uk-six-inch-chicken-sandwich-nutrition'],
 '/gb/en/restaurants/wagamama/': ['wagamama-uk-ramen-calories-protein-salt'],
 '/gb/en/restaurants/wasabi/': ['wasabi-sushi-set-dressing-nutrition'],
 '/gb/en/restaurants/pizzaexpress/': ['pizzaexpress-classic-romana-margherita-nutrition'],
 '/gb/en/restaurants/tortilla/': ['tortilla-uk-burrito-bowl-rice-portions'],
 '/gb/en/restaurants/caffe-nero/': ['caffe-nero-latte-milk-size-nutrition'],
 '/gb/en/restaurants/five-guys/': ['five-guys-uk-little-hamburger-cheeseburger'],
 '/gb/en/restaurants/chopstix/': ['chopstix-uk-box-base-toppings-calories'],
 '/gb/en/restaurants/starbucks/': ['starbucks-uk-pumpkin-spice-latte-hot-iced'],
 '/gb/en/restaurants/leon/': ['leon-uk-chicken-wrap-rice-box-nutrition'],
 '/burger-king-healthy-meals-macros.html': ['burger-king-us-breakfast-hash-browns-order'],
 '/grocery-food-coverage.html': [
  'fage-plain-greek-yogurt-0-2-5-percent', 'daisy-cottage-cheese-2-4-percent-portions',
  'peanut-butter-powder-vs-creamy-spread', 'silk-unsweet-soy-vs-almondmilk',
  'original-vs-honey-nut-cheerios-labels', 'barilla-australia-protein-plus-vs-spaghetti',
  'house-foods-firm-vs-super-firm-tofu', 'bushs-black-beans-vs-chickpeas',
  'starkist-light-vs-albacore-tuna-pouches', 'hersheys-special-dark-bar-vs-kisses',
  'chocolate-protein-shakes-country-portions', 'quaker-old-fashioned-vs-quick-oats'],
 '/how-to-log-food-portions.html': ['back-up-and-move-food-diary', 'barcode-food-search-label-check'],
}

HOME_STORIES = {
 'US': ['burger-king-us-breakfast-hash-browns-order', 'original-vs-honey-nut-cheerios-labels', 'quaker-old-fashioned-vs-quick-oats', 'how-to-read-a-nutrition-label'],
 'CA': ['tim-hortons-canada-breakfast-muffin-biscuit-wrap', 'harveys-canada-burger-fries-onion-rings-order', 'tim-hortons-canada-protein-latte-vs-latte', 'chocolate-protein-shakes-country-portions'],
 'GB': ['greggs-breakfast-baguette-calories-protein', 'kfc-uk-burger-twister-wrap-nutrition', 'subway-uk-six-inch-chicken-sandwich-nutrition', 'caffe-nero-latte-milk-size-nutrition'],
 'AU': ['barilla-australia-protein-plus-vs-spaghetti', 'how-to-read-a-nutrition-label', 'raw-vs-cooked-food-weight', 'compare-menu-ingredients-worldwide'],
 'MX': ['subway-mexico-chicken-sandwich-comparison', 'subway-turkey-breast-canada-vs-mexico', 'how-to-read-a-nutrition-label', 'compare-menu-ingredients-worldwide'],
}

PREFERRED = {
 'US': ['Chick-fil-A', 'Chipotle', 'McDonald’s', 'Burger King'],
 'CA': ['Tim Hortons', 'Harvey’s', 'A&W Canada', 'Chick-fil-A'],
 'GB': ['Greggs', 'KFC', 'Subway', 'Nando’s'],
}


def plain(s):
    return re.sub(r'\s+', ' ', unescape(re.sub('<[^>]+>', ' ', s))).strip()


def story(slug):
    page = ROOT/(slug+'.html')
    if not page.is_file(): raise ValueError('Missing editorial destination '+slug)
    text = page.read_text(encoding='utf-8')
    if re.search(r'<meta[^>]*name="robots"[^>]*content="[^"]*noindex', text):
        raise ValueError('Non-indexable editorial destination '+slug)
    title = plain(re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.S)[1])
    description = unescape(re.search(r'<meta name="description" content="([^"]*)"', text)[1])
    return '/'+slug+'.html', title, description


def strip(text, key):
    return re.sub(r'<!-- '+key+r':start -->.*?<!-- '+key+r':end -->', '', text, flags=re.S)


def section(key, heading, links, intro=''):
    return ('<!-- '+key+':start --><section class="container food-reading" aria-labelledby="'+key+'">'
        '<h2 id="'+key+'">'+e(heading)+'</h2>'+(('<p>'+e(intro)+'</p>') if intro else '')+
        '<ul>'+''.join('<li><a href="'+e(url)+'">'+e(title)+'</a></li>' for url,title in links)+
        '</ul></section><!-- '+key+':end -->')


def append_before_main_end(text, key, body):
    text = strip(text, key)
    main = next(n for n in Document(text).nodes if n['tag']=='main')
    return text[:main['close']]+body+text[main['close']:]


def apply():
    from search_recovery.build import metadata
    changed = set()
    relationships = []
    for parent, slugs in RELATED.items():
        path = ROOT/html_path(parent)
        text = path.read_text(encoding='utf-8')
        links = [(url,title) for url,title,_ in map(story,slugs)]
        heading = 'Compare grocery labels' if 'grocery' in parent else 'Food logging guides' if 'log-food' in parent else 'Compare specific orders'
        intro = 'Exact products and source-market labels, with serving-based examples. These guides do not establish current retailer stock.' if 'grocery' in parent else ''
        text = append_before_main_end(text, 'related-order-guides', section('related-order-guides',heading,links,intro))
        path.write_text(text,encoding='utf-8');changed.add(parent)
        relationships.extend({'from':parent,'to':url} for url,_ in links)

    registry = json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    for code,info in markets().items():
        path = ROOT/html_path(info['home']);text = path.read_text(encoding='utf-8')
        guides = {}
        for r in registry:
            if r['market']!=code or not eligible(r) or not r.get('url'): continue
            url = '/'+r['url'].lstrip('/')
            if code!='US' and not url.startswith('/'+code.lower()+'/en/'):raise ValueError('Cross-market guide '+url)
            if not (ROOT/html_path(url)).is_file():raise ValueError('Missing local guide '+url)
            guides.setdefault(r['chain'],url)
        brands = [b for b in PREFERRED.get(code,[]) if b in guides]
        brands += [b for b in sorted(guides) if b not in brands]
        links = [(guides[b],b+' nutrition') for b in brands[:4]]
        text = strip(text,'direct-nutrition-guides')
        node = find(text,'home-restaurants')
        if node and links:
            body = '<!-- direct-nutrition-guides:start --><nav class="market-links" aria-label="Local nutrition tables">'+''.join('<a class="text-action" href="'+e(url)+'">'+e(title)+'</a>' for url,title in links)+'</nav><!-- direct-nutrition-guides:end -->'
            text = text[:node['close']]+body+text[node['close']:]
            relationships.extend({'from':info['home'],'to':url,'market':code} for url,_ in links)
        if code in HOME_STORIES:
            node = find(text,'home-reading')
            part = text[node['start']:node['end']]
            rows = list(map(story,HOME_STORIES[code]))
            feature = find(part,'reading-feature')
            original = part[feature['start']:feature['end']]
            original = re.sub(r'href="[^"]+"','href="'+e(rows[0][0])+'"',original,count=1)
            original = re.sub(r'<h3>.*?</h3>','<h3>'+e(rows[0][1])+'</h3>',original,count=1,flags=re.S)
            original = re.sub(r'<p>.*?</p>','<p>'+e(rows[0][2])+'</p>',original,count=1,flags=re.S)
            # Existing artwork remains an original illustration, not a meal photo.
            original = re.sub(r'<b>(?:Nutrition facts|Portion notes|Food)</b>', '', original)
            part = replace(part,feature,original)
            listing = find(part,'reading-links')
            part = replace(part,listing,'<div class="reading-links">'+''.join('<a href="'+e(url)+'">'+e(title)+'</a>' for url,title,_ in rows[1:])+'</div>')
            text = replace(text,node,part)
            relationships.extend({'from':info['home'],'to':url,'market':code} for url,_,_ in rows)
        path.write_text(text,encoding='utf-8');changed.add(info['home'])

        path = ROOT/html_path(info['restaurants']);text = path.read_text(encoding='utf-8')
        name = 'U.S.' if code=='US' else 'UK' if code=='GB' else info['name']
        text = re.sub(r'<h1\b[^>]*>.*?</h1>','<h1>'+e(name+' restaurant nutrition')+'</h1>',text,count=1,flags=re.S)
        text = metadata(text,name+' Restaurant Nutrition: Calories & Macros','Find '+name+' restaurant nutrition tables, calories, protein and exact portions. Open a local guide or compare supported orders; directory-only chains are labeled.')
        if code in HOME_STORIES:
            local = [story(s)[:2] for s in HOME_STORIES[code][:3]]
            text = append_before_main_end(text,'directory-order-guides',section('directory-order-guides','Start with an order comparison',local))
            relationships.extend({'from':info['restaurants'],'to':url,'market':code} for url,_ in local)
        path.write_text(text,encoding='utf-8');changed.add(info['restaurants'])

    # This intent already appears in Search Console. Keep the existing tool and
    # example arithmetic, and align its title, heading and description.
    path = ROOT/'nutrition-label-comparison-tool.html';text = path.read_text(encoding='utf-8')
    text = re.sub(r'<h1\b[^>]*>.*?</h1>','<h1>Compare nutrition facts</h1>',text,count=1,flags=re.S)
    text = metadata(text,'Compare Nutrition Facts: Two Food Labels','Compare two foods per serving, per 100 g or per 100 calories. Calculate calories, protein, fiber, added sugar and sodium from your nutrition labels.')
    text = append_before_main_end(text,'comparison-reading',section('comparison-reading','Check the portion before comparing',[
        ('/serving-size-vs-portion-size.html','Serving size versus the portion you eat'),
        ('/grocery-food-coverage.html','Compare exact branded grocery labels'),
        ('/compare-foods.html','Compare foods already in the food library')]))
    path.write_text(text,encoding='utf-8');changed.add('/nutrition-label-comparison-tool.html')

    # Actual changed-page dates only. Preserve publication dates and every URL.
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    tree=ET.parse(ROOT/'sitemap.xml')
    for n in tree.getroot():
        if n.find(ns+'loc').text in {BASE+r for r in changed}:
            mod=n.find(ns+'lastmod')
            if mod is None:mod=ET.SubElement(n,ns+'lastmod')
            mod.text=DATE
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    out=ROOT/'docs/search-discovery-2026-10-23';out.mkdir(parents=True,exist_ok=True)
    (out/'implementation.json').write_text(json.dumps({'date':DATE,'routes':sorted(changed),'links':relationships,'newPublicPages':0,'nutritionRecordsChanged':0,'indexingGuaranteed':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Search discovery:',len(changed),'existing pages;',len(relationships),'explicit, relevant link placements.')


if __name__=='__main__': apply()
