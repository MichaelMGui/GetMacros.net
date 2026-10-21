"""One final presentation pass; authored food data and existing routes stay intact."""
from pathlib import Path
from html import escape, unescape
import json,re,sys,importlib,hashlib,xml.etree.ElementTree as ET
from normalize_calculator_layouts import Document
from build_flagship_release import find,replace,markets,market_of,navigation,icon,character,pages

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/ultimate-release-2026-10-19'
DATE='2026-10-19'
BOOT="try{var p=localStorage.getItem('gm-theme');document.documentElement.dataset.theme=['light','citrus','berry','dark'].includes(p)?p:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');document.documentElement.classList.add('js');document.documentElement.dataset.motion=localStorage.getItem('gm-motion')==='calm'?'calm':'full'}catch(e){document.documentElement.dataset.theme='light'}"

def e(s):return escape(str(s),quote=True)
def put(path,text):path.write_text(text,encoding='utf-8',newline='\n')
def us_spelling(text):
    d=Document(text);protected=[(n['start'],n['end']) for n in d.nodes if n['tag'] in ['script','style']];edits=[]
    swap=lambda value:re.sub(r'\bfibre\b',lambda m:'Fiber' if m[0][0].isupper() else 'fiber',value,flags=re.I)
    for m in re.finditer(r'>([^<>]*)<',text):
        if not any(a<=m.start(1)<b for a,b in protected) and swap(m[1])!=m[1]:edits.append((m.start(1),m.end(1),swap(m[1])))
    for n in d.nodes:
        if n['tag']=='meta' and (n['attrs'].get('name') in ['description','twitter:title','twitter:description'] or n['attrs'].get('property') in ['og:title','og:description']):
            tag=text[n['start']:n['end']];m=re.search(r'content="([^"]*)"',tag)
            if m and swap(m[1])!=m[1]:edits.append((n['start']+m.start(1),n['start']+m.end(1),swap(m[1])))
        if n['tag']=='script' and n['attrs'].get('type')=='application/ld+json':
            value=json.loads(text[n['inner']:n['close']]);changed=False
            for key in ['headline','description']:
                if isinstance(value,dict) and key in value and swap(value[key])!=value[key]:value[key]=swap(value[key]);changed=True
            if changed:edits.append((n['inner'],n['close'],json.dumps(value,ensure_ascii=False,separators=(',',':'))))
    for a,b,value in sorted(edits,reverse=True):text=text[:a]+value+text[b:]
    return text
def appearance(text):
    text=text.replace('class="product-panel appearance-picker"','class="product-panel theme-dialog"')
    node=next((n for n in Document(text).nodes if n['attrs'].get('id')=='appearance-dialog'),None)
    if not node:return text
    fragment=text[node['inner']:node['close']]
    head=find(fragment,'panel-heading');head=fragment[head['start']:head['end']]
    choices=''.join('<button type="button" data-theme-choice="'+key+'" aria-pressed="'+('true' if key=='light' else 'false')+'"><span class="theme-preview theme-preview-'+key+'" aria-hidden="true"><i></i><i></i><i></i></span><span>'+label+'</span>'+icon('check')+'</button>' for key,label in [('light','Garden Day'),('citrus','Citrus Morning'),('berry','Berry Bloom'),('dark','Forest Night')])
    body=head+'<div class="theme-segment" role="group" aria-label="Color theme">'+choices+'</div><button type="button" class="system-theme-button" data-system-theme aria-pressed="false">'+icon('sun')+' Follow device appearance</button><label class="motion-preference"><input type="checkbox" data-calm-motion><span>Calm motion<small>Less movement, same personality.</small></span></label>'
    return text[:node['inner']]+body+text[node['close']:]

def homepage(text,code):
    from botanical_release.layout import homepage as compose
    return compose(text,code,markets,find,replace,character,icon)


def articles():
    result=[]
    for name in ['editorial_restaurants','editorial_foodtools']:
        path=ROOT/'tools/ultimate_release'/f'{name}.py'
        if path.exists():result.extend(importlib.import_module('ultimate_release.'+name).articles())
    return result

def render_articles(rows):
    from build_global_product import page
    for row in rows:
        slug=row['slug'].removesuffix('.html');route='/'+slug+'.html'
        toc=[];body=row['body_html']
        def heading(m):
            title=re.sub('<[^>]+>','',m[1]);id='read-'+re.sub('[^a-z0-9]+','-',unescape(title).lower()).strip('-');toc.append((id,title));return '<h2 id="'+id+'">'+m[1]+'</h2>'
        body=re.sub(r'<h2>(.*?)</h2>',heading,body,flags=re.S)
        for node in sorted([n for n in Document(body).nodes if 'table-wrap' in n['attrs'].get('class','').split()],key=lambda n:n['start'],reverse=True):
            opening=body[node['start']:node['inner']]
            if 'tabindex=' not in opening:opening=opening[:-1]+' tabindex="0" role="region" aria-label="Nutrition comparison table; scroll horizontally if needed">'
            body=body[:node['start']]+opening+body[node['inner']:]
        checked_dates=sorted({s['checked_on'] for s in row['sources'] if s.get('checked_on')})
        checked='Sources checked '+', '.join(checked_dates)+'.' if checked_dates else 'Source-check date unavailable.'
        sources='<section class="editorial-sources" id="article-sources"><h2>Sources &amp; serving notes</h2><ul>'+''.join('<li><a href="'+e(s['url'])+'">'+e(s['title'])+'</a>'+('<p>'+e(s['notes'])+'</p>' if s.get('notes') else '')+'</li>' for s in row['sources'])+'</ul><p>'+e(checked)+' '+e(row['review'].get('limitations',''))+'</p></section>'
        related='<nav class="editorial-next" aria-label="Keep exploring"><h2>Put it into practice.</h2>'+''.join('<a href="'+e(l['href'])+'">'+e(l['label'])+icon('meal' if 'finder' in l['href'] else 'log')+'</a>' for l in row['related'])+'</nav>'
        intro='<header class="editorial-hero"><a href="/articles.html" class="editorial-category">'+e(row['category'])+'</a><h1>'+e(row['title'])+'</h1><p class="editorial-answer">'+e(row['answer'])+'</p><p class="editorial-byline">GetMacros editorial · <time datetime="'+DATE+'">October 19, 2026</time>'+(' · '+e(markets()[row['country']]['name']) if row['country'] in markets() else '')+'</p></header>'
        contents='<aside class="editorial-contents"><span>On this page</span><nav aria-label="Article sections">'+''.join('<a href="#'+id+'">'+title+'</a>' for id,title in toc)+'</nav><a href="#article-sources">Sources &amp; notes</a></aside>'
        markup='<article class="editorial-story" data-editorial-topic="'+e(row['category'])+'">'+intro+'<div class="editorial-layout">'+contents+'<div class="editorial-body">'+body+sources+related+'</div></div></article>'
        page(route,row['title'],row['description'],markup,'article',market=row['country'] if row['country'] in markets() else 'US')
        p=ROOT/route[1:];text=p.read_text(encoding='utf-8');text=navigation(text,row['country'] if row['country'] in markets() else 'US')
        schema={'@context':'https://schema.org','@type':'Article','headline':row['title'],'description':row['description'],'mainEntityOfPage':'https://getmacros.net'+route,'datePublished':DATE,'dateModified':DATE,'inLanguage':'en','author':{'@type':'Organization','name':'GetMacros editorial','url':'https://getmacros.net/editorial-policy.html'},'publisher':{'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/'}}
        text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head>')
        put(p,text)

TOPICS={'learn-eating-out':'Eating out','learn-breakfast':'Breakfast','learn-coffee-drinks':'Coffee & drinks','learn-meal-comparisons':'Meal comparisons','learn-protein-value':'Protein & value','learn-portions-labels':'Portions & labels','learn-nutrition-basics':'Nutrition basics'}
def topic_for(row):
    term=(row['category']+' '+row['title']).lower()
    if any(w in term for w in ['coffee','latte','drink','caffè']):return 'learn-coffee-drinks'
    if 'breakfast' in term:return 'learn-breakfast'
    if any(w in term for w in ['value','price','protein shake']):return 'learn-protein-value'
    if row['country'] in ('US','CA','GB','MX','JP','NZ','FR','IE','SG','ZA') and 'restaurant' in row['category'].lower():return 'learn-eating-out'
    if any(w in term for w in ['burger','chicken','burrito','ramen','sushi','pizza','kfc','subway','tortilla','five guys','greggs']):return 'learn-meal-comparisons'
    return 'learn-portions-labels'

def editorial_index(rows):
    p=ROOT/'articles.html';text=p.read_text(encoding='utf-8')
    old=json.loads((ROOT/'tools/ultimate_release/existing-library.json').read_text(encoding='utf-8'))
    latest=[{'href':'/'+r['slug'].removesuffix('.html')+'.html','title':r['title'],'description':r['description'],'topic':topic_for(r),'new':True} for r in rows]
    allrows=list({r['href']:r for r in latest+old}.values())
    features=latest[:1]+latest[15:16]+latest[3:4] if len(latest)>15 else old[:3]
    feature=''.join('<a class="editorial-feature-story" href="'+e(r['href'])+'"><span class="editorial-feature-art" aria-hidden="true"><img src="/images/meal-cutouts/'+art+'.svg" width="400" height="300" alt="" loading="lazy"><small class="editorial-art-note">Illustration</small></span><span class="editorial-category">'+TOPICS.get(r['topic'],'Food & numbers')+'</span><h2>'+e(r['title'])+'</h2><p>'+e(r['description'])+'</p><span class="editorial-read-label">Read the story '+icon('log')+'</span></a>' for r,art in zip(features,['breakfast','yogurt','chicken']))
    filters='<div class="reader-controls"><label class="reader-search">'+icon('search')+'<span class="sr-only">Search guides</span><input type="search" data-reader-search placeholder="Find a guide" maxlength="150"></label><div class="reader-topics" role="group" aria-label="Reading topics"><button type="button" data-reader-topic="all" aria-pressed="true">All stories</button>'+''.join('<button type="button" data-reader-topic="'+key+'" aria-pressed="false">'+label+'</button>' for key,label in TOPICS.items())+'</div></div>'
    groups=''
    for key,label in TOPICS.items():
        links=''.join('<a class="reader-story" href="'+e(r['href'])+'"><div><span class="reader-story-type">'+('New story' if r.get('new') else label)+'</span><h3>'+e(r['title'])+'</h3><p>'+e(r['description'])+'</p></div>'+icon('log')+'</a>' for r in allrows if r['topic']==key)
        groups+='<section class="reader-group" id="'+key+'" data-reader-group><h2>'+label+'</h2><div class="reader-stories">'+links+'</div><button type="button" class="reader-more" data-reader-more hidden>More '+label.lower()+'</button></section>'
    body='<section class="editorial-index-head"><div><h1>Good food.<br><span>Fresh perspective.</span></h1><p>Practical answers, real portions, sources you can follow.</p></div>'+character('avocado')+'</section><section class="editorial-features" aria-label="Featured reading">'+feature+'</section><section class="reader-library" aria-label="All nutrition guides">'+filters+'<p class="reader-status" data-reader-status role="status"></p>'+groups+'<p data-reader-empty hidden>No stories match. Try a restaurant, ingredient or portion.</p></section>'
    main=next(n for n in Document(text).nodes if n['tag']=='main');text=text[:main['start']]+'<main id="main-content" class="container" data-family="editorial-index">'+body+'</main>'+text[main['end']:]
    if 'js/editorial-browser.js' not in text:text=text.replace('</body>','<script src="/js/editorial-browser.js" defer></script></body>')
    if 'css/release-library.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/css/release-library.css"></head>')
    put(p,text)

def index_articles(rows):
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}';tree=ET.parse(ROOT/'sitemap.xml');root=tree.getroot();known={n.find(ns+'loc').text:n for n in root}
    for r in rows:
        url='https://getmacros.net/'+r['slug'].removesuffix('.html')+'.html'
        node=known.get(url)
        if node is None:node=ET.SubElement(root,ns+'url');ET.SubElement(node,ns+'loc').text=url
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text=DATE
    # Only pages whose main content changed, rather than every page inheriting
    # a new shared stylesheet, receive this release's modification date.
    changed=['/','/articles.html','/calculators.html','/food-library.html','/compare-foods.html','/whats-new.html','/about.html','/privacy.html','/sources.html']
    changed += [m['home'] for code,m in markets().items() if code!='US']
    for route in changed:
        node=known.get('https://getmacros.net'+route)
        if node is None:continue
        mod=node.find(ns+'lastmod')
        if mod is None:mod=ET.SubElement(node,ns+'lastmod')
        mod.text=DATE
    ET.register_namespace('',ns[1:-1]);tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- ultimate-search:start -->.*?<!-- ultimate-search:end -->','',text,flags=re.S)
    links=''.join('<a class="search-hit" href="/'+e(r['slug'].removesuffix('.html'))+'.html" data-search="'+e(r['title'])+'"><span class="search-hit-name">'+e(r['title'])+'</span><span class="search-hit-copy">'+e(r['description'])+'</span></a>' for r in rows)
    text=text.replace('</main>','<!-- ultimate-search:start --><section class="search-group"><h2>New food &amp; restaurant guides <span data-count>'+str(len(rows))+'</span></h2>'+links+'</section><!-- ultimate-search:end --></main>',1);put(p,text)
    (OUT/'publication-manifest.json').write_text(json.dumps([{'route':'/'+r['slug'].removesuffix('.html')+'.html','title':r['title'],'status':'integrated locally; production verification pending','sourceReview':r['review'],'sources':r['sources']} for r in rows],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def whats_new():
    from build_global_product import page
    body='''<article class="food-app food-reading"><header class="food-app-head"><h1>A little more room to enjoy food.</h1><p>A botanical homepage, a calmer diary, and clearer restaurant choices.</p></header><p class="submission-byline">October 20, 2026</p><section><h2>A fresh first impression</h2><p>The meal quiz stays first, with original food characters, botanical line artwork and credited food inspiration. Every supported country shares the composition.</p><a class="text-action" href="/">Find my meal</a></section><section><h2>Your food, simply recorded</h2><p>Daily totals sit above breakfast, lunch, dinner and snacks. Search, review a portion and log it. Repeat meals, recipes and backups have their own quieter place.</p><a class="text-action" href="/food-diary.html">Open my diary</a></section><section><h2>Choose a familiar restaurant</h2><p>Compact selections show the full name and a clear check. Restaurant search now handles punctuation and accents, and tells you when a name has no matches.</p><a class="text-action" href="/restaurant-meal-finder.html?quiz=1">Help me choose</a></section><section><h2>A clearer starting point</h2><p>The macro calculator has one aligned workspace, followed by your result and a meal preference you choose.</p><a class="text-action" href="/calculators.html">Calculate my macros</a></section><section><h2>Recently published</h2><p>The 29 restaurant, grocery and food-logging guides published October 19 are still available with their portions, sources and original dates.</p><a class="text-action" href="/articles.html">Read the guides</a></section></article>'''
    page('/whats-new.html','What’s new at GetMacros: botanical design & simpler logging','See the botanical GetMacros homepage, simpler food diary, compact restaurant selections and refined macro calculator.',body,'guide')


def apply():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=articles()
    whats_new()
    assets=ROOT/'images/meal-cutouts/provenance.json';provenance=json.loads(assets.read_text(encoding='utf-8'))
    for kind in ['grilled-sandwich','yogurt']:
        path=ROOT/'images/meal-cutouts'/f'{kind}.svg';item={'id':'getmacros-original-'+kind,'path':'/images/meal-cutouts/'+kind+'.svg','kind':'original-category-illustration','exactMealPhotograph':False,'width':400,'height':300,'background':'transparent','source':'Original SVG source authored in this release: images/meal-cutouts/'+kind+'.svg','creator':'GetMacros project artwork','rights':'Original project SVG source; no third-party imagery or brand trade dress.','permittedTransformations':['resize','crop','recolor','compose'],'attributionRequired':False,'reviewedAt':DATE,'sha256':hashlib.sha256(path.read_bytes().replace(b'\r\n',b'\n')).hexdigest()}
        provenance['assets']=[r for r in provenance['assets'] if r['id']!=item['id']]+[item]
    assets.write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    (OUT/'image-provenance.json').write_text(json.dumps({'date':DATE,'newAssets':provenance['assets'][-2:],'characterChanges':'Layered blush details for egg, strawberry and broccoli; original broccoli florets. Existing original cast retained.','inlineArt':['Original botanical hero SVG','Fifteen restaurant comparison SVG charts','Original food-diary backup diagram'],'exactMealPhotosAdded':0,'photographicCutoutsAdded':0,'exactPhotoGaps':10327,'referenceScreenshots':'Composition references only; no restaurant/manufacturer photographs copied into the public interface.'},indent=2)+'\n',encoding='utf-8')
    render_articles(rows)
    editorial_index(rows)
    index_articles(rows)
    changes=[]
    for p in pages():
        text=p.read_text(encoding='utf-8');old=text
        text=re.sub(r'<script>try\{var p=localStorage.getItem\(\x27gm-theme\x27\);.*?</script>','<script>'+BOOT+'</script>',text,count=1,flags=re.S)
        text=appearance(text)
        if p.name=='food-diary.html':
            from botanical_release.layout import diary as compose_diary
            text=compose_diary(text,find,replace)
            from diary_reference.layout import apply as compose_reference_diary
            text=compose_reference_diary(text,find,replace)
            # The async diary painter reveals real saved totals. Do not flash
            # an empty nutrient-details row before that initial storage read.
            if 'data-reference-diary' not in text:text=text.replace('class="diary-summary" aria-label="Logged nutrition"','class="diary-summary" hidden aria-label="Logged nutrition"')
        if 'data-home-template="shared-market-v1"' in text:text=homepage(text,market_of(p,text))
        if p.name=='calculators.html':
            head=find(text,'tools-masthead')
            if head:
                fragment=text[head['start']:head['end']]
                art=next((n for n in Document(fragment).nodes if 'data-food-character' in n['attrs']),None)
                if art:text=replace(text,head,replace(fragment,art,''))
            work=find(text,'calculation-workbench')
            if work and 'class="calculator-journey"' not in text:
                rail='<aside class="calculator-journey" aria-label="Calculator steps"><h2>Your daily<br>starting point.</h2><ol>'+''.join('<li data-calculator-stage="'+str(i)+'"><span>'+str(i+1)+'</span>'+label+'</li>' for i,label in enumerate(['About you','Your activity','Your goal']))+'</ol>'+character('broccoli')+'</aside>'
                text=text[:work['inner']]+rail+text[work['inner']:]
        if p.name=='restaurant-meal-guides.html':
            from botanical_release.layout import directory as compose_directory
            text=compose_directory(text,find,replace)
        if p.name=='food-library.html':
            text=re.sub(r'<!-- library-starts:start -->.*?<!-- library-starts:end -->','',text,flags=re.S)
            search=find(text,'food-search-region')
            if search:
                shortcuts=''.join('<a href="/food-library.html?q='+query+'&amp;type='+kind+'"><img src="/images/meal-cutouts/'+art+'.svg" width="100" height="75" alt=""><span>'+label+'</span></a>' for query,kind,art,label in [('chicken+roasted','reference','chicken','Cooked chicken'),('rice+cooked','reference','bowl','Rice & grains'),('Greek+yogurt','reference','yogurt','Greek yogurt')])
                text=text[:search['end']]+'<!-- library-starts:start --><section class="library-quick-starts" aria-label="Food search shortcuts"><h2>Start with a familiar food.</h2><div>'+shortcuts+'</div></section><!-- library-starts:end -->'+text[search['end']:]
        if 'js/liquid-motion.js' not in text and 'data-source-path="js/liquid-motion.js"' not in text:text=text.replace('</body>','<script src="/js/liquid-motion.js" defer></script></body>')
        if p.name=='about.html':text=text.replace('463 recorded orders from 25 U.S. restaurant chains.','Country-specific restaurant portions, with sources you can inspect.')
        if p.name=='sources.html':text=text.replace('The complete dataset now contains 463 orders across 25 chains.','That October 4 U.S. snapshot contained 463 entries across 25 chains. <a href="/fast-food-nutrition-data-report.html">Current menu coverage</a> is reported separately.')
        if p.name=='privacy.html':
            from diary_reference.layout import privacy as diary_goals_privacy
            text=diary_goals_privacy(text)
            for n in reversed([n for n in Document(text).nodes if n['tag']=='p']):
                fragment=text[n['inner']:n['close']]
                if fragment.startswith('Cloudflare adds a web analytics script'):
                    text=replace(text,n,'<p>The current GetMacros release does not load Google Analytics 4 or an advertising provider. Cloudflare’s Web Analytics beacon is present on the live site and measures visits and page performance. These reports and hosting requests are separate from GA4 sessions. GetMacros does not send diary entries, notes or calculator inputs to the beacon. See <a href="https://developers.cloudflare.com/web-analytics/about/">Cloudflare Web Analytics</a> and <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>. Any future analytics integration requires its actual configuration and this notice to be reviewed.</p>')
            text=text.replace('The current GetMacros release does not load Google Analytics 4 or an advertising provider. Cloudflare hosting and security services may process the technical information described above. Hosting traffic reports are not the same as GA4 sessions. Any future analytics integration requires its actual configuration and this notice to be reviewed.','The current GetMacros release does not load Google Analytics 4 or an advertising provider. Cloudflare’s Web Analytics beacon is present on the live site and measures visits and page performance. These reports and hosting requests are separate from GA4 sessions. GetMacros does not send diary entries, notes or calculator inputs to the beacon. See <a href="https://developers.cloudflare.com/web-analytics/about/">Cloudflare Web Analytics</a> and <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>. Any future analytics integration requires its actual configuration and this notice to be reviewed.')
            text=text.replace('appearance, light/dark and calm-motion preferences','appearance, color-theme and calm-motion preferences')
        if 'class="editorial-story"' in text and 'css/release-library.css' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/css/release-library.css"></head>')
        if not re.search(r'data-market-scope="(CA|GB|IE|AU|NZ)"',text) and not re.match(r'^[a-z]{2}/en/',p.relative_to(ROOT).as_posix()):
            # House spelling on global/U.S. presentation. Keep exact URL identifiers.
            text=us_spelling(text)
        if text!=old:put(p,text);changes.append(p.relative_to(ROOT).as_posix())
    from botanical_release.layout import update_sitemap
    update_sitemap(ROOT,markets)
    from build_edition_css import build
    build()
    (OUT/'presentation.json').write_text(json.dumps({'date':DATE,'routes':changes,'newArticles':len(rows),'themes':['Garden Day','Citrus Morning','Berry Bloom','Forest Night'],'scope':'Implementation; publication and rendered verification tracked separately.'},indent=2)+'\n',encoding='utf-8')
    print('Shared presentation:',len(changes),'routes;',len(rows),'existing source-checked editorial pages maintained.')

if __name__=='__main__':apply()
