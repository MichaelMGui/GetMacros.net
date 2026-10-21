"""Shared reference-led compositions, using existing records and diary hooks."""
from html import escape
from normalize_calculator_layouts import Document

def initials(name):
    words=name.replace('’', '').replace("'", '').replace('-', ' ').split()
    return ''.join(w[0] for w in words[:2]).upper() if len(words)>1 else name[:2].upper()

def leaf():
    return '<svg class="botanical-line" viewBox="0 0 180 260" fill="none" aria-hidden="true"><path d="M52 248C67 171 108 104 135 26M87 151C24 135 25 89 44 83c29-9 46 36 43 68Zm11-30c58-3 84-44 65-61-20-18-54 11-65 61ZM117 77C78 56 82 14 99 13c21-2 26 35 18 64Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def homepage(text,code,markets,find,replace,character,icon):
    info=markets()[code];e=lambda s:escape(str(s),quote=True)
    hero='<section class="food-hero flagship-hero botanical-hero container"><div class="hero-copy"><h1>Find a meal<br><span>that fits.</span></h1><p>Restaurant meals. Clear macros.<br>A little help choosing.</p><div class="hero-actions"><a class="btn btn-primary home-quiz-action" data-quiz-entry href="'+e(info['finder'])+'?quiz=1">Find my meal '+icon('meal')+'</a><a class="btn btn-secondary" href="'+e(info['finder'])+'">Browse meals</a></div><a class="hero-macro-link" href="/calculators.html?market='+code+'#macro-calculator">'+icon('calculator')+'<span>Start with my macros</span></a><p class="home-market-note">'+e(info['name'])+' menus · <a href="/world-restaurant-menus.html" data-open-country>Change country</a></p></div><div class="food-ensemble" aria-hidden="true">'+leaf()+'<span class="ensemble-egg">'+character('egg')+'</span><span class="ensemble-strawberry">'+character('strawberry')+'</span></div></section>'
    # The opening composition uses original characters, not unrelated food photography.
    import re
    hero=hero.replace('Find a meal<br><span>that fits.</span>','Find food that<br><span>fits your macros.</span>').replace('Restaurant meals. Clear macros.<br>A little help choosing.','Compare restaurant calories, protein, carbs and fat. Choose a meal, then save or log it.')
    text=replace(text,find(text,'food-hero'),hero)
    title=('Fast Food Nutrition & Restaurant Macros' if code=='US' else info['name']+' Restaurant Calories & Macros')+' | GetMacros'
    description='Compare '+info['name']+' restaurant meals by calories, protein, carbs and fat. Find a high-protein order, compare portions, and save or log your food.'
    text=re.sub(r'<title>.*?</title>','<title>'+e(title)+'</title>',text,count=1)
    for node in sorted(Document(text).nodes,key=lambda n:n['start'],reverse=True):
        if node['tag']!='meta':continue
        key=node['attrs'].get('name') or node['attrs'].get('property')
        value=title if key in ['og:title','twitter:title'] else description if key in ['description','og:description','twitter:description'] else None
        if value is not None:text=replace(text,node,re.sub(r'content="[^"]*"','content="'+e(value)+'"',text[node['start']:node['end']]))
    macro='<section class="home-macro-feature container"><div class="home-macro-copy"><h2>Your day.<br>Your starting point.</h2><p>A simple estimate for calories, protein, carbs and fat.</p><a class="btn btn-primary" href="/calculators.html?market='+code+'#macro-calculator">Calculate my macros '+icon('calculator')+'</a></div><div class="home-macro-art" aria-hidden="true"><div class="macro-orbit"><span class="orbit-protein">Protein</span><span class="orbit-carbs">Carbs</span><span class="orbit-fat">Fat</span>'+character('broccoli')+'</div></div></section>'
    text=replace(text,find(text,'home-macro-feature'),macro)
    text=text.replace('A few good orders.','A few good places to start.').replace('class="market-home home-composed flagship-home"','class="market-home home-composed flagship-home ultimate-home"')
    for card in sorted([n for n in Document(text).nodes if 'data-home-record' in n['attrs']],key=lambda n:n['start'],reverse=True):
        fragment=text[card['start']:card['end']]
        if 'Grilled Chicken Sandwich' in card['attrs']['data-home-record']:
            import re
            fragment=re.sub(r'(/images/meal-cutouts/)[^/" ]+\.svg',r'\1grilled-sandwich.svg',fragment)
        text=replace(text,card,fragment)
    # Existing local links and real chain names stay intact. These are type marks,
    # deliberately not imitations of restaurant logos.
    for n in sorted([n for n in Document(text).nodes if 'restaurant-shortcut' in n['attrs'].get('class','').split()],key=lambda n:n['start'],reverse=True):
        fragment=text[n['start']:n['end']];d=Document(fragment)
        name=next((fragment[k['inner']:k['close']] for k in d.nodes if k['tag']=='span' and not k['attrs'].get('class')),'')
        mark=find(fragment,'shortcut-mark')
        if mark:fragment=replace(fragment,mark,'<span class="shortcut-mark" aria-hidden="true">'+e(initials(name))+'</span>')
        text=replace(text,n,fragment)
    text=text.replace('<h2>A little notebook.<br>For what you actually ate.</h2>','<h2>A place for<br>your everyday food.</h2>')
    text=text.replace('<h2>At the reading table.</h2>','<h2>A fresh perspective.</h2>')
    return text

def diary(text,find,replace):
    if 'botanical-diary' in text:return text
    overview=find(text,'diary-overview');body=text[overview['start']:overview['end']]
    companion=find(body,'food-companion');summary=find(body,'diary-summary');tools=find(body,'diary-quick-tools')
    if not all([overview,companion,summary,tools]):raise ValueError('Expected current diary workspace')
    buddy=body[companion['start']:companion['end']]
    totals=body[summary['start']:summary['end']]
    utilities=body[tools['start']:tools['end']]
    overview_markup='<section class="diary-overview" aria-label="Daily overview"><div class="diary-overview-content"><h2>Day at a glance</h2><p class="diary-empty-message" data-diary-empty-day>Nothing logged yet. Start with something you ate.</p>'+totals+'</div>'+buddy+'</section>'
    text=replace(text,overview,overview_markup)
    columns=find(text,'diary-columns');main=find(text,'diary-main')
    main_markup=text[main['start']:main['end']]
    text=replace(text,columns,'<div class="diary-columns">'+overview_markup+main_markup+'<aside class="diary-utilities"><h2>Your notebook</h2>'+utilities+'<p class="diary-storage-note">Saved on this device.</p></aside></div>')
    text=text.replace('diary-app diary-workspace','diary-app diary-workspace botanical-diary')
    text=text.replace('<span>Breakfast to bedtime</span>','')
    return text


def update_sitemap(root,markets):
    import xml.etree.ElementTree as ET
    namespace='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    tree=ET.parse(root/'sitemap.xml')
    changed={'https://getmacros.net'+info['home'] for info in markets().values()}
    changed.update('https://getmacros.net'+route for route in ['/articles.html','/calculators.html','/whats-new.html'])
    for node in tree.getroot():
        if node.find(namespace+'loc').text in changed:
            date=node.find(namespace+'lastmod')
            if date is None:date=ET.SubElement(node,namespace+'lastmod')
            date.text='2026-10-21' if node.find(namespace+'loc').text in {'https://getmacros.net'+info['home'] for info in markets().values()} else '2026-10-20'
    ET.register_namespace('',namespace[1:-1]);tree.write(root/'sitemap.xml',encoding='utf-8',xml_declaration=True)


def directory(text,find,replace):
    from html import unescape
    import re
    for node in sorted([n for n in Document(text).nodes if 'restaurant-entry' in n['attrs'].get('class','').split()],key=lambda n:n['start'],reverse=True):
        fragment=text[node['start']:node['end']]
        title=next((n for n in Document(fragment).nodes if n['tag']=='h2'),None)
        if not title:continue
        name=unescape(re.sub('<[^>]+>','',fragment[title['inner']:title['close']]))
        mark=find(fragment,'restaurant-mark')
        if mark:fragment=replace(fragment,mark,'<span class="restaurant-mark" aria-hidden="true" data-restaurant-initials="'+escape(initials(name))+'"></span>')
        # These previews repeat the linked guide introductions. The actual guide,
        # recorded-order count and every local destination remain intact.
        for paragraph in sorted([n for n in Document(fragment).nodes if n['tag']=='p'],key=lambda n:n['start'],reverse=True):
            fragment=replace(fragment,paragraph,'')
        text=replace(text,node,fragment)
    return text
