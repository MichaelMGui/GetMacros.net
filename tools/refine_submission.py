"""Apply the final editorial review after all legacy content generators."""
from pathlib import Path
import re, html, json, math
from submission_content import PAGES

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-09-09'
def plain(s):return html.unescape(re.sub('<[^>]+>',' ',s)).strip()
def main(s,body):return re.sub(r'(<main\b[^>]*>).*?(</main>)',lambda m:m[1]+body+m[2],s,count=1,flags=re.S)
def label(target):
    name=target.split('#')[0]
    if name in PAGES:return PAGES[name]['title']
    s=(ROOT/name).read_text(encoding='utf-8')
    return plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',s,re.S)[1])
def metadata(s,title,intro):
    title=title+' | GetMacros' if len(title)<64 and 'GetMacros' not in title else title
    s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',s,count=1,flags=re.S)
    for attr,key,value in [('property','og:title',title),('name','twitter:title',title),('name','description',intro),('property','og:description',intro),('name','twitter:description',intro)]:
        s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
    return s

for path in ROOT.glob('*.html'):
    s=path.read_text(encoding='utf-8')
    s=s.replace('The GetMacros.net editorial team','GetMacros').replace('Written and reviewed for clarity by the GetMacros.net editorial team','By GetMacros')
    s=s.replace('Five common reasons the number moved','Six common reasons the number moved')
    s=s.replace('Keep reading: Full macro calculator','Keep reading: Free macro calculator')
    s=s.replace('>Eating out without wrecking it<','>Eating out with your goals in mind<')
    if path.name in PAGES:
        c=PAGES[path.name]
        # Preserve the page's visual hero and decorative illustration where present.
        hero=re.search(r'<(?:section|header)\b[^>]*class="[^"]*(?:page-hero|policy-hero|article-hero)[^"]*"[^>]*>.*?</(?:section|header)>',s,re.S)
        head=hero[0] if hero else '<section class="page-hero liquid-surface"><div class="container"><h1></h1><p></p></div></section>'
        head=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(c['title'])+m[2],head,count=1,flags=re.S)
        head=re.sub(r'<p\b[^>]*>.*?</p>','',head,flags=re.S)
        head=head.replace('</h1>','</h1><p>'+html.escape(c['intro'])+'</p>',1)
        head=re.sub(r'<div class="article-facts">.*?</div>','',head,flags=re.S)
        body=c['body']
        def label_table(match):
            table=match[0]
            header=re.search(r'<thead>(.*?)</thead>',table,re.S)
            labels=re.findall(r'<th\b[^>]*>(.*?)</th>',header[1],re.S) if header else []
            def row(match):
                cells=match[0];index=1
                def cell(match):
                    nonlocal index
                    label=plain(labels[index]) if index<len(labels) else ''
                    index+=1
                    return '<td data-label="'+html.escape(label,quote=True)+'">'+match[1]+'</td>'
                return re.sub(r'<td\b[^>]*>(.*?)</td>',cell,cells,flags=re.S)
            return re.sub(r'<tr>.*?</tr>',row,table,flags=re.S)
        body=re.sub(r'<table class="data-table">.*?</table>',label_table,body,flags=re.S)
        # Preserve old section fragments linked elsewhere without duplicating visible copy.
        old_main=re.search(r'<main\b[^>]*>(.*?)</main>',s,re.S)[1]
        old_ids=set(re.findall(r'\bid="([^"]+)"',old_main))
        new_ids=set(re.findall(r'\bid="([^"]+)"',head+body))
        anchors=''.join('<span id="'+x+'" class="submission-anchor" aria-hidden="true"></span>' for x in sorted(old_ids-new_ids) if x.startswith(('read-','recipe-')))
        sources=''
        if c['sources']:sources='<section class="submission-sources"><h2>Sources</h2><ul>'+''.join('<li><a href="'+html.escape(url,quote=True)+'">'+html.escape(text)+'</a></li>' for url,text in c['sources'])+'</ul></section>'
        actions='<nav class="submission-next" aria-label="Related pages">'+''.join('<a class="btn" href="'+url+'">'+html.escape(label(url))+'</a>' for url in c['related'])+'</nav>'
        s=main(s,head+'<article class="article-container submission-article"><p class="submission-byline">By GetMacros · Updated September 9, 2026</p>'+anchors+body+sources+actions+'</article>')
        s=metadata(s,c['title'],c['intro'])
        def schema(m):
            data=json.loads(m[1])
            if data.get('@type')=='FAQPage':return ''
            if data.get('@type') in ['Article','BlogPosting']:
                data.update(headline=c['title'],description=c['intro'],dateModified=DATE,author={'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/about.html'})
            if data.get('@type')=='BreadcrumbList' and data.get('itemListElement'):data['itemListElement'][-1]['name']=c['title']
            return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
        s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,s,flags=re.S)
    if path.name=='about.html':
        s=s.replace('Food choices are easier when the numbers make sense.','GetMacros is an independent site for finding restaurant meals and understanding everyday nutrition.')
    if path.name=='privacy.html':
        s=s.replace('The site has no registration form. ','')
        s=s.replace('Some pages may also remember a language preference. ','')
        s=re.sub(r'This site is hosted on GitHub Pages, behind Cloudflare\..*?</p>','Cloudflare helps deliver and protect the site. Hosting and network services may process technical details such as IP addresses, browser information and requested URLs for security and operation. These logs are separate from calculator arithmetic, which runs in your browser.</p>',s,flags=re.S)
        s=s.replace('Last updated August 2026.','Last updated September 9, 2026.')
    if path.name=='terms.html':
        s=s.replace("If you don't agree with them, the only enforceable request we can make is that you stop using the site.","If you do not agree, please stop using the site.")
        s=s.replace('articles, calculators, quizzes, glossary','articles, calculators and the meal finder')
        s=s.replace('This site displays ads from Google AdSense, and links out to external sources for citations.','The site includes Google AdSense code and links to external sources. Whether ads appear depends on account approval and Google’s serving decisions.')
    if path.name=='budget-meal-builder.html':s=s.replace('Select at least one item, then build. Suggestions use broad ingredient roles rather than exact recipes.','Choose at least one ingredient, then select “Build meals.” You’ll get meal ideas, not step-by-step recipes.')
    if path.name=='weight-goal-timeline-calculator.html':s=s.replace('How to actually get there','Planning your next steps').replace('TDEE vs BMR','Maintenance calories explained')
    if path.name=='restaurant-meal-guides.html':
        s=s.replace('Choose a chain to compare every menu option in the GetMacros dataset and see goal-based picks, protein efficiency, official sources and checked dates.','Choose a restaurant to compare selected meals, calories, protein and ordering tips.')
        s=s.replace('Fast-food meal finder compares all chains at once and can combine cutting, bulking, high-protein and dietary preferences.','Use the meal finder to compare restaurants for weight loss, weight gain, high protein or dietary preferences.')
        s=s.replace('Used as a way to compare options before you order, this data is reliable. Used as a precise accounting of what you ate, it is not, and no restaurant data is.','Use these figures to compare named menu options, then confirm the current item and portion with the restaurant.')
    if path.name=='healthy-fast-food.html':
        s=re.sub(r'<div class="stat-row">.*?</div>','',s,count=1,flags=re.S)
        s=s.replace('Explore meals from 15 restaurants, or find a match for your goals.','Compare 83 tracked menu options from 15 restaurants, or find a meal for your goals.')
        s=s.replace('>High-protein breakfasts<','>Breakfast protein<').replace('>Plant-based meals<','>Plant-based options<')
    if path.name=='sources.html':
        s=re.sub(r'<p[^>]*>A note on how these were compiled:.*?</p>','',s,flags=re.S)
        s=re.sub(r'\[\d+\]\s*','',s)
        s=s.replace('A citation supports a claim; it does not imply endorsement or authorship by the source. Read the complete editorial and source methodology, including evidence hierarchy and medical boundaries. Material factual changes appear in the public corrections log.','Sources support individual claims; they do not endorse this site. Our editorial policy explains how we use evidence, and our corrections page records important factual changes.')
        s=s.replace('Unpublished values stay unknown;','Unconfirmed values stay unknown;')
    # Remove repeated end-of-article essays, keeping research, sources and a concise conclusion.
    cuts={
      'how-much-protein-can-your-body-absorb.html':'Turn the evidence into a normal day',
      'does-creatine-cause-hair-loss.html':'What would change the conclusion?',
      'are-diet-drinks-bad-for-you.html':'Three questions to ask about your own drink',
    }
    if path.name in cuts:
        title=cuts[path.name]
        section=re.search(r'<h2\b[^>]*>'+re.escape(title)+r'</h2>.*?(?=<h2\b)',s,re.S)
        if section:
            ids=re.findall(r'id="([^"]+)"',section[0]);s=s.replace(section[0],'')
            for id in ids:s=re.sub(r'<a href="#'+re.escape(id)+r'">.*?</a>','',s)
        s=s.replace('Updated September 8, 2026','Updated September 9, 2026')
        s=re.sub(r'("dateModified":\s*")[^"]+',r'\g<1>'+DATE,s)
        article=re.search(r'<article class="article-container">(.*?)</article>',s,re.S)
        if article:s=re.sub(r'\d+ minute read',str(max(1,math.ceil(len(plain(article[1]).split())/220)))+' minute read',s)
    if path.name=='index.html':
        s=s.replace('Estimate a useful starting point without false precision.','Find a daily calorie starting point.')
        s=s.replace('Compare chains for cutting, protein and higher-calorie meals.','Compare meals for weight loss, more protein or a bigger appetite.')
        s=metadata(s,'Healthy Fast Food Finder for Your Goals','Find healthy fast-food meals from 15 restaurants. Compare calories and protein for weight loss, weight gain or your next meal.')
        s=re.sub(r'<script src="js/(?:home-calculator|macro-math)\.js(?:\?[^"]*)?"[^>]*></script>','',s)
        s=s.replace('Use the free GetMacros healthy fast food finder to get restaurant meals ranked for cutting, bulking, high protein and more across 15 chains.','Find healthy fast-food meals from 15 restaurants. Compare calories and protein for weight loss, weight gain or your next meal.')
    if path.name=='calories-vs-macros-what-matters-more.html':
        s=s.replace('Your goal decides which layer needs attention first.','Your goal helps you decide which numbers to focus on.')
        s=s.replace('For weight change, energy is the first gate','Calories and weight change').replace('A low-friction setup','A simple way to start')
        s=s.replace('protect the protein and minimum fat your plan needs','include enough protein and fat').replace('Next layer','Also consider')
        s=s.replace('Keep fat above a sensible minimum.','Include fat-rich foods such as olive oil, nuts, seeds or oily fish.')
        s=s.replace('the guide to label rounding','the guide to reading a food label')
    # Current restaurant data is linked at the point of use. A dash is unknown, never zero.
    if 'restaurant-guide' in s and 'source-box' in s:
        s=re.sub(r'<div class="stat-row">.*?</div>','',s,count=1,flags=re.S)
        s=re.sub(r'<article class="advice-card"><h2>Match the order to your goal</h2>.*?</article>','',s,count=1,flags=re.S)
        s=re.sub(r'(<article class="chain-pick-group"><header>.*?)<p>.*?</p>',r'\1',s,flags=re.S)
        s=s.replace('U.S. menu items. A dash means the restaurant has not published a verified value.','U.S. menu items. A dash means we could not confirm that value.')
        s=s.replace('Lighter, substantial orders','Lower-calorie meals here').replace('Larger options for bigger appetites, with protein kept in view.','The highest-calorie meals listed in this guide.')
        s=s.replace('Make the rest of the day fit around it','More nutrition guides')
        s=re.sub(r'<p>A single .*? order is one decision\. These guides cover the ones on either side of it\.</p>','',s)
        s=s.replace('How to eat out without wrecking your goal','Eating out with your goals in mind')
        s=s.replace('Work out the daily target this meal has to fit inside.','Find a starting point for your daily calories.')
        s=s.replace('Restaurant meals carry most of it. See what a day&rsquo;s worth looks like.','Understand sodium labels and daily references.')
        s=re.sub(r'("dateModified":\s*")[^"]+',r'\g<1>'+DATE,s)
        # Keep repeated menu rankings available without making every restaurant
        # page display the same orders four times before the source information.
        from normalize_calculator_layouts import Document
        doc=Document(s)
        groups=[n for n in doc.nodes if n['tag']=='article' and 'chain-pick-group' in n['attrs'].get('class','').split() and 'end' in n]
        for node in sorted(groups,key=lambda n:n['start'],reverse=True):
            block=s[node['start']:node['end']]
            header=re.search(r'<header>(.*?)</header>',block,re.S)
            if not header:continue
            title=plain(re.search(r'<h3>(.*?)</h3>',header[1],re.S)[1])
            icon=re.search(r'<span class="chain-pick-icon">.*?</span>',header[1],re.S)
            summary='<summary>'+(icon[0] if icon else '')+'<strong>'+html.escape(title)+'</strong><span class="ranking-toggle" aria-hidden="true">+</span></summary>'
            block=block.replace('<article class="chain-pick-group">','<details class="chain-pick-group compact-chain-ranking">',1)
            block=block.replace(header[0],summary,1)
            block=block.rsplit('</article>',1)[0]+'</details>'
            s=s[:node['start']]+block+s[node['end']:]
        reviews=json.loads((ROOT/'tools/restaurant-review.json').read_text(encoding='utf-8'))
        from build_restaurant_pages import parse_meals
        tracked=[m for m in parse_meals() if m['url']==path.name]
        chain=tracked[0]['chain'] if tracked else None
        records=[r for r in reviews if r['chain']==chain]
        if records:
            sources=list(dict.fromkeys(u for r in records for u in [r['source'],r.get('additional_source')] if u))
            links=''.join('<li><a href="'+html.escape(u,quote=True)+'">'+('Official nutrition guide' if len(sources)==1 else html.escape(next((r['name'] for r in records if r['source']==u),'Official menu announcement')))+'</a></li>' for u in sources)
            note='Figures checked against the linked official sources on September 9, 2026. Recipes, portions and local availability can change.'
            if chain=='Taco Bell':note='Current menu calories are shown below. Protein is confirmed for the Cantina Chicken Bowl; other unconfirmed nutrients are left blank and do not qualify for nutrient filters.'
            if chain=='CAVA':note='Figures match the linked CAVA nutrition guide. Curated bowls and ingredients vary by location and season; confirm the current build before ordering.'
            source='<div class="source-box"><h2>Menu sources</h2><p>'+note+'</p><details><summary>View official sources</summary><ul>'+links+'</ul></details><p>GetMacros is independent of '+html.escape(chain or '')+'.</p></div>'
            s=re.sub(r'<div class="source-box">.*?</div>',source,s,count=1,flags=re.S)
        s=s.replace('Official source checked August 2026','Menu sources below')
        s=s.replace('Nutrition data checked: August 2026.','Check the current menu before ordering.')
    s=re.sub(r'(?m)[ \t]+$','',s)
    path.write_text(s,encoding='utf-8')

# Refresh search and guide snippets from the final page wording, without rebuilding layouts.
for name in ['search.html','articles.html']:
    path=ROOT/name;s=path.read_text(encoding='utf-8')
    def card(m):
        block=m[0];href=re.search(r'href="([^"#]+)',block)
        if not href or not (ROOT/href[1]).is_file():return block
        target=(ROOT/href[1]).read_text(encoding='utf-8')
        title=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',target,re.S)[1])
        desc=html.unescape(re.search(r'<meta name="description" content="([^"]+)"',target)[1])
        block=re.sub(r'(<span class="search-hit-name">).*?(</span>)',lambda a:a[1]+html.escape(title)+a[2],block,flags=re.S)
        block=re.sub(r'(<span class="search-hit-copy">).*?(</span>)',lambda a:a[1]+html.escape(desc)+a[2],block,flags=re.S)
        if 'data-search=' in block:block=re.sub(r'data-search="[^"]*"','data-search="'+html.escape(title+' '+desc,quote=True)+'"',block)
        if name=='articles.html' and href[1] in PAGES:
            block=re.sub(r'<h3\b[^>]*>.*?</h3>','<h3>'+html.escape(title)+'</h3>',block,flags=re.S)
            block=re.sub(r'<p>.*?</p>','<p>'+html.escape(desc)+'</p>',block,flags=re.S)
        return block
    s=re.sub(r'<a\b[^>]*class="[^"]*(?:search-hit|guide-card)[^"]*"[^>]*>.*?</a>',card,s,flags=re.S)
    path.write_text(s,encoding='utf-8')
# Reading-time labels and sitemap dates must describe the final content.
hub=ROOT/'blog.html';s=hub.read_text(encoding='utf-8')
def blog_card(m):
    block=m[0];href=re.search(r'href="([^"]+)"',block)
    if not href or not (ROOT/href[1]).exists():return block
    article=(ROOT/href[1]).read_text(encoding='utf-8')
    body=re.search(r'<article\b[^>]*>(.*?)</article>',article,re.S)
    if body:block=re.sub(r'\d+ min read',str(max(1,math.ceil(len(plain(body[1]).split())/220)))+' min read',block)
    return block
s=re.sub(r'<a class="blog-card.*?</a>',blog_card,s,flags=re.S);hub.write_text(s,encoding='utf-8')
updated=set(PAGES)|set(cuts)|{'index.html','about.html','articles.html','blog.html','privacy.html','terms.html','search.html','restaurant-meal-finder.html','healthy-fast-food.html','restaurant-meal-guides.html','calories-vs-macros-what-matters-more.html'}
updated|={p.name for p in ROOT.glob('*macros.html')}
updated|={'high-protein-foods-list.html','sources.html'}
site=ROOT/'sitemap.xml';s=site.read_text(encoding='utf-8')
for name in updated:
    url='' if name=='index.html' else re.escape(name)
    s=re.sub(r'(<loc>https://getmacros.net/'+url+r'</loc><lastmod>)[^<]+',r'\g<1>'+DATE,s)
site.write_text(s,encoding='utf-8')
# Feed summaries should match the published page, not an earlier generator draft.
import xml.etree.ElementTree as ET
feed=ROOT/'feed.xml';tree=ET.parse(feed)
for item in tree.findall('./channel/item'):
    link=item.findtext('link','');name=link.rsplit('/',1)[-1]
    if not name or not (ROOT/name).exists():continue
    content=(ROOT/name).read_text(encoding='utf-8')
    item.find('title').text=plain(re.search(r'<title>(.*?)</title>',content,re.S)[1])
    item.find('description').text=html.unescape(re.search(r'<meta name="description" content="([^"]+)"',content)[1])
tree.write(feed,encoding='utf-8',xml_declaration=True)
print(f'Reviewed copy applied to {len(PAGES)} guides and policies; search descriptions refreshed.')
