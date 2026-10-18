"""Final product integration: one shared experience across existing markets."""
from pathlib import Path
from html import escape
import json,re,subprocess,hashlib,xml.etree.ElementTree as ET
from functools import lru_cache
from normalize_calculator_layouts import Document

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/flagship-release-2026-10-18'
def e(value):return escape(str(value),quote=True)
def write(path,text):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def find(text,cls):return next((n for n in Document(text).nodes if cls in n['attrs'].get('class','').split()),None)
def replace(text,node,value):return text[:node['start']]+value+text[node['end']:] if node else text
def pages():return list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html'))
@lru_cache(maxsize=1)
def markets():return json.loads(re.search(r'window.GM_MARKETS=(.*);',(ROOT/'js/market-definitions.js').read_text(encoding='utf-8'))[1])
def character(name):return '<span data-food-character="'+name+'" aria-hidden="true"><svg viewBox="0 0 160 160" aria-hidden="true"><use href="/images/food-characters.svg#food-'+name+'"/></svg></span>'
ICONS={
 'menu':'M4 7h16M4 12h16M4 17h16','close':'m6 6 12 12M18 6 6 18','search':'M15 15l6 6',
 'meal':'M3 12h18M5 12a7 7 0 0 1 14 0M12 3v2M5 16h14',
 'calculator':'M7 3h10a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2ZM8 7h8M8 11h1m3 0h1m3 0h.1M8 15h1m3 0h1m3 0h.1M8 18h1m3 0h1m3 0h.1',
 'log':'M6 4h12v17H6zM9 1v6m6-6v6M9 11h6m-6 4h6',
 'save':'M6 4h12v17l-6-4-6 4Z','play':'m9 6 10 6-10 6Z','compare':'M5 5v14m14-14v14M2 8h6m8 8h6',
 'sun':'M12 2v2m0 16v2M2 12h2m16 0h2M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2',
 'moon':'M20.5 14.7A8.8 8.8 0 0 1 9.3 3.5a8.8 8.8 0 1 0 11.2 11.2Z',
 'info':'M12 10v7m0-10v.1','check':'m5 12 4 4 10-10'}
def icon(name):
    extra='<circle cx="10" cy="10" r="6.5"/>' if name=='search' else '<circle cx="12" cy="12" r="4"/>' if name=='sun' else '<circle cx="12" cy="12" r="9"/>' if name=='info' else ''
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+extra+'<path d="'+ICONS[name]+'"/></svg>'
def dialog_head(id,title):return '<header class="panel-heading"><h2 id="'+id+'">'+title+'</h2><button type="button" class="panel-close" data-panel-close aria-label="Close '+title.lower()+'">'+icon('close')+'</button></header>'
def market_of(path,text=''):
    explicit=next((c for c in markets() if path.relative_to(ROOT).as_posix().startswith(c.lower()+'/en/')),None)
    scope=re.search(r'data-market-scope="([A-Z]{2})"',text)
    return explicit or (scope[1] if scope and scope[1] in markets() else 'US')
def nav_link(href,label,kind=None,quiz=False,icon_name=None):
    attrs=(' data-market-route="'+kind+'"' if kind else ' data-market-context="true"')+(' data-quiz-entry' if quiz else '')
    return '<a href="'+e(href)+'"'+attrs+'>'+ (icon(icon_name) if icon_name else '')+'<span>'+label+'</span></a>'

def navigation(text,code):
    info=markets()[code];old=find(text,'site-header');old_fragment=text[old['start']:old['end']]
    brand=find(old_fragment,'modern-brand');brand_html=old_fragment[brand['start']:brand['end']]
    countries=[]
    for continent in dict.fromkeys(m['continent'] for m in markets().values()):
        links=''.join('<li><a href="'+m['home']+'" data-country-choice="'+c+'"'+(' aria-current="true"' if c==code else '')+'><span class="country-flag" aria-hidden="true"><svg viewBox="0 0 30 20"><use href="/images/market-flags.svg#flag-'+c+'"/></svg></span><span>'+e(m['name'])+'</span>'+icon('check')+'</a></li>' for c,m in markets().items() if m['continent']==continent)
        countries.append('<section data-country-continent><h3>'+e(continent)+'</h3><ul>'+links+'</ul></section>')
    menu_groups=[('Find your food',[(info['finder']+'?quiz=1','Find my meal','finder',True,'meal'),(info['finder'],'Browse meals','finder',False,'meal'),(info['finder']+'?meal=breakfast','Breakfast finder',None,False,'meal'),(info['restaurants'],'Restaurants','restaurants',False,'meal'),('/compare-complete-restaurant-orders.html','Build a complete order',None,False,'meal'),('/compare-foods.html','Compare foods',None,False,'compare')]),('Your everyday tools',[('/calculators.html','Macro calculator',None,False,'calculator'),('/food-diary.html','Log food',None,False,'log'),('/food-shelf.html','Saved orders',None,False,'save'),('/food-library.html','Food library',None,False,'search'),('/recipe-macro-scaler.html','Recipe portions',None,False,'calculator'),('/protein-value-calculator.html','Protein value',None,False,'calculator')]),('Learn & play',[('/articles.html','Nutrition guides',None,False,'log'),('/play.html','Play',None,False,'play'),('/read-and-watch.html','Read & watch',None,False,'play'),('/sources.html','Sources & methods',None,False,'info'),('/whats-new.html','What’s new',None,False,'info')])]
    menu=''.join('<section><h3>'+heading+'</h3><nav aria-label="'+heading+'">'+''.join(nav_link(*row) for row in rows)+'</nav></section>' for heading,rows in menu_groups)
    header='<header id="site-top" class="site-header product-header"><nav class="product-nav" aria-label="Main navigation">'+brand_html+'<div class="product-nav-links">'+nav_link(info['finder']+'?quiz=1','Find my meal','finder',True)+nav_link('/calculators.html','Macro calculator')+nav_link('/food-diary.html','Log food')+nav_link('/play.html','Play')+'<span class="product-nav-glide" aria-hidden="true"></span></div><div class="product-nav-market"><button type="button" class="country-button" data-open-country aria-haspopup="dialog"><span class="country-flag" data-country-flag aria-hidden="true"><svg viewBox="0 0 30 20"><use data-market-flag href="/images/market-flags.svg#flag-'+code+'"/></svg></span><span data-country-name>'+e(info['name'])+'</span></button></div><div class="product-nav-tools"><button type="button" class="appearance-button" data-open-appearance aria-haspopup="dialog" aria-label="Appearance">'+icon('sun')+icon('moon')+'<span class="sr-only" data-appearance-current>Light</span></button><button type="button" class="header-search-button" data-open-search aria-haspopup="dialog" aria-label="Search the site">'+icon('search')+'</button><button type="button" class="site-menu-button" data-open-site-menu aria-haspopup="dialog">'+icon('menu')+'<span>Menu</span></button></div></nav></header>'
    dialogs='<dialog id="site-menu" class="product-panel site-menu-panel" aria-labelledby="site-menu-title">'+dialog_head('site-menu-title','Make yourself at home.')+'<div class="site-menu-grid">'+menu+'</div><p class="panel-footnote">English · <a href="/world-restaurant-menus.html">Country &amp; menu coverage</a> · <a href="/contact.html">Contact</a></p></dialog>'
    dialogs+='<dialog id="country-dialog" class="product-panel country-dialog" aria-labelledby="country-dialog-title">'+dialog_head('country-dialog-title','Where are you ordering?')+'<label class="country-search">Find a country<input type="search" data-country-search autocomplete="off" placeholder="Country name"></label><nav class="country-list" aria-label="Restaurant country">'+''.join(countries)+'</nav><p data-country-empty role="status" hidden>No countries match.</p><a class="panel-footnote" href="/world-restaurant-menus.html">See menu coverage</a></dialog>'
    dialogs+='<dialog id="appearance-dialog" class="product-panel appearance-picker" aria-labelledby="appearance-title">'+dialog_head('appearance-title','Make yourself comfortable.')+'<div class="theme-segment" role="group" aria-label="Color theme"><button type="button" data-theme-choice="light" aria-pressed="true">'+icon('sun')+'<span>Light</span></button><button type="button" data-theme-choice="dark" aria-pressed="false">'+icon('moon')+'<span>Dark</span></button></div><label class="motion-preference"><input type="checkbox" data-calm-motion><span>Calm motion<small>Keep the interface still.</small></span></label></dialog>'
    dialogs+='<dialog id="site-search-dialog" class="product-panel site-search-dialog" aria-labelledby="site-search-title">'+dialog_head('site-search-title','Find something useful.')+'<form class="site-search-form" action="/search.html"><label class="sr-only" for="quick-search">Meals, restaurants, tools or guides</label><div><input type="search" id="quick-search" name="q" placeholder="Meals, restaurants or guides" required><button class="btn btn-primary" type="submit">Search</button><input type="hidden" name="market" value="'+code+'"></div></form><nav class="search-shortcuts" aria-label="Search shortcuts">'+nav_link('/food-library.html','Search foods & barcodes')+nav_link(info['restaurants'],'Browse restaurants','restaurants')+'</nav></dialog>'
    bottom='<nav class="mobile-task-nav" aria-label="Everyday tasks">'+nav_link(info['finder']+'?quiz=1','Find my meal','finder',True,'meal')+nav_link('/calculators.html','Macros',None,False,'calculator')+nav_link('/food-diary.html','Log food',None,False,'log')+nav_link('/food-shelf.html','Saved',None,False,'save')+'</nav>'
    if code!='US':
        localize=lambda fragment:re.sub(r'href="(/[^"?#]+\.html)"',lambda m:'href="'+m[1]+'?market='+code+'"',fragment)
        header=localize(header);dialogs=localize(dialogs);bottom=localize(bottom)
    text=replace(text,old,header)
    for node in sorted([n for n in Document(text).nodes if n['attrs'].get('id') in ['site-menu','country-dialog','appearance-dialog','site-search-dialog'] or 'mobile-task-nav' in n['attrs'].get('class','').split() or (n['tag']=='details' and set(n['attrs'].get('class','').split())&{'appearance-picker','country-picker','language-picker','nav-search'})],key=lambda n:n['start'],reverse=True):text=replace(text,node,'')
    text=text.replace('</body>',dialogs+bottom+'</body>',1)
    return text

def homepages():
    registry=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    lookup={r.get('id') or r['restaurantMarketId']+'|'+r['name']:r for r in registry}
    for code,info in markets().items():
        p=ROOT/('index.html' if code=='US' else info['home'].strip('/')+'/index.html');text=p.read_text(encoding='utf-8')
        old=find(text,'food-hero');fragment=text[old['start']:old['end']];art=find(fragment,'food-ensemble');artwork=fragment[art['start']:art['end']] if art else ''
        hero='<section class="food-hero flagship-hero container"><div class="hero-copy"><h1>Find a meal.<br><span>That fits you.</span></h1><p>Choose what matters. We’ll help you find a restaurant order.</p><div class="hero-actions"><a class="btn btn-primary home-quiz-action" data-quiz-entry href="'+e(info['finder'])+'?quiz=1">Find my meal</a><a class="btn btn-secondary" href="'+e(info['finder'])+'">Browse meals</a></div><a class="hero-macro-link" href="/calculators.html?market='+code+'#macro-calculator"><span>Macro calculator</span><small>A starting point for your day.</small></a><p class="home-market-note">'+e(info['name'])+' menus · <a href="/world-restaurant-menus.html" data-open-country>Change country</a></p></div>'+artwork+'</section>'
        text=replace(text,old,hero)
        text=re.sub(r'<!-- flagship-macro:start -->.*?<!-- flagship-macro:end -->','',text,flags=re.S)
        menu=find(text,'home-menu-section')
        macro='<!-- flagship-macro:start --><section class="home-macro-feature container"><div class="home-macro-art">'+character('broccoli')+'</div><div><h2>Your day, in a few numbers.</h2><p>Estimate calories, protein, carbs and fat. Then choose a meal.</p></div><a class="btn btn-secondary" href="/calculators.html?market='+code+'#macro-calculator">Calculate my macros</a></section><!-- flagship-macro:end -->'
        if menu:text=text[:menu['end']]+macro+text[menu['end']:]
        text=text.replace('class="market-home home-composed"','class="market-home home-composed flagship-home"')
        for card in sorted([n for n in Document(text).nodes if 'data-home-record' in n['attrs']],key=lambda n:n['start'],reverse=True):
            row=lookup[card['attrs']['data-home-record']];name=row['name'].lower()
            category='pizza' if 'pizza' in name else 'bowl' if any(w in name for w in ['bowl','rice','noodle']) else 'salad' if 'salad' in name else 'burger' if any(w in name for w in ['burger','whopper','mac']) else 'wrap' if any(w in name for w in ['wrap','burrito']) else 'sandwich' if any(w in name for w in ['sandwich','muffin','baguette','sub']) else 'chicken' if 'chicken' in name else 'breakfast' if row.get('meal')=='breakfast' else 'side'
            fragment=re.sub(r'<figure class="home-meal-visual">.*?</figure>','',text[card['inner']:card['close']],flags=re.S)
            picture='<figure class="home-meal-visual"><img src="/images/meal-cutouts/'+category+'.svg" width="400" height="300" alt="" loading="lazy" decoding="async"><figcaption>Illustration</figcaption></figure>'
            text=text[:card['inner']]+picture+fragment+text[card['close']:]
        p.write_text(text,encoding='utf-8')

def finder_screens():
    rows=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    definitions=markets()
    for code,info in definitions.items():
        p=ROOT/('restaurant-meal-finder.html' if code=='US' else info['finder'].strip('/')+'/index.html');text=p.read_text(encoding='utf-8')
        node=next(n for n in Document(text).nodes if n['attrs'].get('id')=='meal-quiz')
        local=[r for r in rows if r['market']==code and r.get('category') not in ('component','sauce') and r.get('finderSupported',True)]
        markup=subprocess.run(['node','tools/product_release/render-finder.cjs'],input=json.dumps({'rows':local,'markets':definitions}),capture_output=True,encoding='utf-8',check=True,cwd=ROOT).stdout
        markup=markup.replace('href="restaurant-meal-finder.html"','href="'+info['finder']+'"')
        text=text[:node['inner']]+markup+text[node['close']:]
        p.write_text(text,encoding='utf-8')

def presentation(text,path):
    """Replace crowded disclosure stacks while preserving live form hooks."""
    classes={'home-serving','diary-more-nutrients','food-review-source','calc-assumptions','work-result-note','food-product-details','diary-entry-source','individual-macro-tools'}
    counts={}
    for node in sorted([n for n in Document(text).nodes if n['tag']=='details' and classes&set(n['attrs'].get('class','').split())],key=lambda n:n['start'],reverse=True):
            cls=next(iter(classes&set(node['attrs']['class'].split())));index=counts.get(cls,0);counts[cls]=index+1
            fragment=text[node['inner']:node['close']];summary=next((n for n in Document(fragment).nodes if n['tag']=='summary'),None)
            if not summary:continue
            label=fragment[summary['inner']:summary['close']];content=replace(fragment,summary,'')
            identity='secondary-'+hashlib.sha256((str(path.relative_to(ROOT))+'|'+cls+'|'+str(index)).encode()).hexdigest()[:12]
            text=replace(text,node,'<div class="secondary-information '+cls+'"><button class="secondary-information-action" type="button" aria-expanded="false" aria-controls="'+identity+'" data-toggle-section="'+identity+'">'+label+'</button><section id="'+identity+'" hidden>'+content+'</section></div>')
    tools=find(text,'food-search-tools')
    if tools and 'id="food-refinement"' not in text[tools['start']:tools['end']]:
        fragment=text[tools['inner']:tools['close']]
        fragment=re.sub(r'<summary>.*?</summary>','',fragment,flags=re.S)
        fragment=re.sub(r'<details\b([^>]*)>',r'<section\1>',fragment).replace('</details>','</section>')
        text=replace(text,tools,'<div class="food-search-tools"><button type="button" class="search-refine-button" data-open-panel="food-refinement">Refine search '+icon('filter' if 'filter' in ICONS else 'search')+'</button><dialog id="food-refinement" class="product-panel food-refinement" aria-labelledby="food-refinement-title">'+dialog_head('food-refinement-title','Refine your search')+fragment+'<button type="button" class="btn btn-primary" data-panel-close>Show foods</button></dialog></div>')
    if path.name=='food-diary.html':
        for label in ['Backup &amp; restore','Storage &amp; offline use','Delete diary']:
            for node in sorted([n for n in Document(text).nodes if n['tag']=='details'],key=lambda n:n['start'],reverse=True):
                fragment=text[node['inner']:node['close']]
                if '<summary>'+label+'</summary>' in fragment:text=replace(text,node,'<section class="diary-setting-section">'+fragment.replace('<summary>'+label+'</summary>','<h3>'+label+'</h3>')+'</section>')
        text=text.replace('Breakfast, lunch, dinner and everything between.','')
    if path.name=='calculators.html':
        text=text.replace('class="calculation-workbench"','class="calculation-workbench flagship-calculator"')
    for node in sorted([n for n in Document(text).nodes if n['tag']=='details' and 'footer-details' in n['attrs'].get('class','').split()],key=lambda n:n['start'],reverse=True):
        fragment=re.sub(r'<summary>.*?</summary>','',text[node['inner']:node['close']],flags=re.S)
        text=replace(text,node,'<div class="footer-destinations">'+fragment+'</div>')
    if 'js/meal-view.js' in text and 'js/meal-images.js' not in text:text=re.sub(r'(?=<script[^>]+src="/?js/meal-view.js)', '<script src="/js/meal-images.js" defer></script>',text,count=1)
    return text

def index_release(entries):
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    tree=ET.parse(ROOT/'sitemap.xml');root=tree.getroot();known={n.find(ns+'loc').text:n for n in root}
    for row in entries:
        if not row['indexable']:continue
        url='https://getmacros.net'+row['route'];node=known.get(url)
        if node is None:node=ET.SubElement(root,ns+'url');ET.SubElement(node,ns+'loc').text=url
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text='2026-10-18'
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- flagship-search:start -->.*?<!-- flagship-search:end -->','',text,flags=re.S)
    links=''.join('<a class="search-hit" href="'+e(row['route'])+'" data-search="'+e(row['title'])+'"'+(' data-market="'+row['market']+'"' if row['market'] in markets() else '')+'><span class="search-hit-name">'+e(row['title'])+'</span><span class="search-hit-copy">'+e(row['description'])+'</span></a>' for row in entries if row['indexable'])
    text=text.replace('</main>','<!-- flagship-search:start --><section class="search-group"><h2>New menus &amp; comparisons <span data-count>'+str(len(entries))+'</span></h2>'+links+'</section><!-- flagship-search:end --></main>',1);p.write_text(text,encoding='utf-8')

def build():
    OUT.mkdir(parents=True,exist_ok=True)
    import build_global_product as product
    product.PAGES.clear()
    from flagship_release.integrate import build as data
    registry,definitions=data()
    markets.cache_clear()
    from build_global_product import page
    from flagship_release.editorial import ARTICLES
    for article in ARTICLES:
        route=article['route'] if article['route'].startswith('/') else '/'+article['route']
        body='<article class="food-app food-reading"><header class="food-app-head"><h1>'+e(article['title'])+'</h1></header><p class="submission-byline">Published October 18, 2026 · '+e(definitions.get(article['market'],{}).get('name',article['market']))+' source servings</p>'+article['body']+'</article>'
        page(route,article['title'],article['description'],body,'article',market=article['market'])
        p=ROOT/route.lstrip('/');text=p.read_text(encoding='utf-8')
        schema={'@context':'https://schema.org','@type':'Article','headline':article['title'],'description':article['description'],'mainEntityOfPage':'https://getmacros.net'+route,'datePublished':'2026-10-18','dateModified':'2026-10-18','inLanguage':'en'}
        text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False,separators=(',',':'))+'</script></head>');p.write_text(text,encoding='utf-8')
    links=''.join('<a class="library-read" href="/'+a['route'].lstrip('/')+'"><span>'+e(a['title']).replace('fibre','fiber')+'</span><small>'+e(a['description']).replace('fibre','fiber')+'</small></a>' for a in ARTICLES)
    p=ROOT/'articles.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- flagship-reads:start -->.*?<!-- flagship-reads:end -->','',text,flags=re.S);text=text.replace('</main>','<!-- flagship-reads:start --><section class="guide-group"><h2>A closer look at your order</h2><div class="library-reads">'+links+'</div></section><!-- flagship-reads:end --></main>',1);p.write_text(text,encoding='utf-8')
    page('/whats-new.html','What’s new at GetMacros','Try the meal quiz, choose a per-meal calculator target, log a usual order and explore sourced local menus.','<article class="food-app food-reading"><header class="food-app-head"><h1>A little easier to choose.</h1></header><p>New ways to find, compare and remember your meals.</p><section><h2>Start with a question</h2><p>The meal quiz now leads from the homepage. Choose a meal time, restaurants and priorities, then set optional limits.</p><a class="btn btn-primary" data-quiz-entry data-market-route="finder" href="/restaurant-meal-finder.html?quiz=1">Find my meal</a></section><section><h2>From your day to one meal</h2><p>The macro calculator keeps the daily estimate separate from the meal you want to find.</p><a href="/calculators.html">Calculate my macros</a></section><section><h2>Your usual, ready to log</h2><p>Recent foods, favorites and saved orders sit together in the diary. Review a portion before adding it to breakfast, lunch, dinner or snacks.</p><a href="/food-diary.html">Open the food log</a></section><section><h2>Local menus, named portions</h2><p>Restaurant data stays separate by country. Browse the source selection and exact serving before comparing orders.</p><a href="/world-restaurant-menus.html">Browse country menus</a></section><section><h2>Movement, on your terms</h2><p>Selections, menus and results have short, responsive transitions. Choose Calm motion in Appearance for a quieter interface.</p></section></article>','guide')
    homepages()
    finder_screens()
    for p in pages():
        text=p.read_text(encoding='utf-8');text=presentation(text,p);text=navigation(text,market_of(p,text))
        if 'js/liquid-motion.js' not in text:text=text.replace('</body>','<script src="/js/liquid-motion.js" defer></script></body>',1)
        p.write_text(text,encoding='utf-8')
    manifest=list({row['route']:row for row in product.PAGES}.values())
    index_release(manifest)
    from build_master_completion import regional_annotations
    regional_annotations()
    (OUT/'published-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    from build_edition_css import build as css
    css()
    print('Flagship release: shared quiz-first homepages across',len(markets()),'existing markets.')
if __name__=='__main__':build()
