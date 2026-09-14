"""Keep search entry pages specific, useful and consistent with visible content.

This is a final build pass: no new pages, invented nutrition or keyword lists.
"""
from pathlib import Path
import html
import json
import re

from build_restaurant_pages import parse_meals, item_type

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://getmacros.net/'

COPY = {
    'healthy-fast-food.html': (
        'Healthy Fast Food Options: Calories & Protein | GetMacros',
        'Compare 83 U.S. fast-food options across 15 restaurants. Find high-protein orders, meals under 500 calories and vegetarian choices with nutrition details.'),
    'restaurant-meal-guides.html': (
        'Healthy Fast-Food Restaurant Guides | GetMacros',
        'Choose from 15 U.S. restaurant guides. Compare specific orders, calories and protein, with ingredients, ordering tips and official nutrition sources.'),
    'chipotle-healthy-meals-macros.html': (
        'Healthy Chipotle Orders: Bowls, Calories & Protein | GetMacros',
        'Compare six Chipotle bowls and salads by calories and protein. See exact ingredients, vegetarian options and high-protein orders on the U.S. menu.'),
    'chick-fil-a-healthy-meals-macros.html': (
        'Healthy Chick-fil-A Orders: Calories & Protein | GetMacros',
        'Compare Chick-fil-A grilled nuggets, sandwiches, salads and breakfast. See calories and protein for each U.S. order, plus what sauces and sides change.'),
    'taco-bell-healthy-meals-macros.html': (
        'Healthy Taco Bell Orders: Bowls, Tacos & Calories | GetMacros',
        'Compare Taco Bell bowls, tacos and burritos by calories. Check U.S. menu portions, vegetarian choices and available protein values before ordering.'),
    'nutrition-label-comparison-tool.html': (
        'Nutrition Label Comparison Tool: Compare Two Foods | GetMacros',
        'Compare two nutrition labels per serving, per 100 g or per 100 calories. Check protein, fiber, added sugar and sodium when choosing between foods.'),
}


def metadata(text, title, description):
    text = re.sub(r'<title>.*?</title>', lambda m: '<title>'+html.escape(title)+'</title>', text, count=1, flags=re.S)
    for attribute, key, value in [('name','description',description),
            ('property','og:title',title),('name','twitter:title',title),
            ('property','og:description',description),('name','twitter:description',description)]:
        pattern = r'(<meta '+attribute+'="'+key+r'" content=")[^"]*(")'
        text = re.sub(pattern, lambda m: m[1]+html.escape(value,quote=True)+m[2], text)
    return text


def order_rows(meals, metric):
    result = []
    units = {'p':'g protein','cal':'cal','f':'g fiber','na':'mg sodium'}
    for meal in meals:
        secondary = [meal['chain']]
        if metric != 'cal': secondary.append(f"{meal['cal']:g} calories")
        if metric != 'p' and meal.get('p') is not None: secondary.append(f"{meal['p']:g} g protein")
        href = meal['url']+'#menu-comparison'
        result.append('<li><strong><a href="'+html.escape(href,quote=True)+'">'+html.escape(meal['name'])+
            '</a><small>'+html.escape(' · '.join(secondary))+'</small></strong>'+
            f'<span>{meal[metric]:g} {units[metric]}</span></li>')
    return ''.join(result)


def rankings(text, meals):
    main = [m for m in meals if item_type(m) not in {'Side','Side / snack'}]
    substantial = [m for m in main if m['cal'] >= 250]
    selections = [
        ('high-protein-orders','High protein under 600 calories','p',
         sorted([m for m in substantial if m['cal'] < 600 and (m.get('p') or 0) >= 25],key=lambda m: (-m['p'],m['cal']))[:6]),
        ('under-500-calories','Meals and entrées under 500 calories','cal',
         sorted([m for m in substantial if m['cal'] < 500],key=lambda m: m['cal'])[:6]),
        ('higher-calorie-orders','Higher-calorie meals','cal',
         sorted([m for m in substantial if (m.get('p') or 0) >= 20],key=lambda m:-m['cal'])[:8]),
        ('fiber-orders','More fiber','f',sorted([m for m in main if m.get('f') is not None],key=lambda m:-m['f'])[:8]),
        ('sodium-orders','Less sodium','na',sorted([m for m in substantial if m.get('na') is not None],key=lambda m:m['na'])[:8]),
        ('vegetarian-orders','Vegetarian meals','p',sorted([m for m in main if 'vegetarian' in m.get('diet',[]) and m.get('p') is not None],key=lambda m:-m['p'])[:8]),
        ('plant-based-orders','Plant-based meals','p',sorted([m for m in main if 'plant' in m.get('diet',[]) and m.get('p') is not None],key=lambda m:-m['p'])[:8]),
        ('breakfast-orders','Breakfast protein','p',sorted([m for m in main if m.get('meal') == 'breakfast' and m.get('p') is not None],key=lambda m:-m['p'])[:8]),
    ]
    cards = ''.join('<details class="ranking-card ranking-disclosure" id="'+key+'"><summary>'+label+
        '</summary><ol class="ranking-list">'+order_rows(items,metric)+'</ol></details>'
        for key,label,metric,items in selections)
    section = ('<section id="rankings" class="data-section"><div class="container"><div class="section-head">'
        '<h2>Find an order for your goal</h2><p>Open a list, then choose an order to see its full nutrition. '
        'Count any extra sides, sauces and drinks separately.</p></div><div class="ranking-grid">'+cards+'</div></div></section>')
    text = re.sub(r'<section id="rankings".*?</section>',lambda m:section,text,count=1,flags=re.S)
    return text, selections[0][3]


def run():
    meals = parse_meals()
    featured = []
    intros = {
        'chipotle-healthy-meals-macros.html': 'Looking for a high-protein Chipotle order? The High Protein-High Fiber Bowl has 540 calories and 46 g protein; the High Protein-Low Calorie Salad has 470 calories and 36 g. Compare the exact U.S. builds below before changing ingredients.',
        'chick-fil-a-healthy-meals-macros.html': 'The Grilled Chicken Sandwich has 390 calories and 28 g protein before extra sauces, sides or drinks. Compare it with nuggets, salads and breakfast orders from the U.S. menu below.',
        'taco-bell-healthy-meals-macros.html': 'Choosing between a bowl, taco or burrito? Compare the U.S. orders below by portion and calories. Protein is shown only where we have a published value; a dash does not mean zero.',
    }
    for path in sorted(ROOT.glob('*.html')):
        text = path.read_text(encoding='utf-8')
        if path.name == 'healthy-fast-food.html':
            text = text.replace('Compare 83 menu options for more protein, fewer calories or a bigger meal.',
                'Compare 83 U.S. menu options for more protein, fewer calories or a bigger meal.')
            text = text.replace('These are comparisons of specific menu options, not an overall health score. Consider the full order and the nutrients that matter to you.',
                'These lists compare options in our database, not every item on each restaurant’s menu. The calorie lists start at 250 calories and exclude sides. High-protein picks have at least 25 g protein. These are selection rules, not an overall health score.')
            text, featured = rankings(text, meals)
        if path.name == 'restaurant-meal-guides.html':
            text = text.replace('Pick a restaurant. See menu options, macros and simple ordering tips.',
                'Pick a restaurant. Compare U.S. menu options, calories, protein and ordering tips.')
        if path.name in intros:
            text = re.sub(r'(<h1\b[^>]*>.*?</h1>\s*<p>).*?(</p>)',
                lambda m:m[1]+html.escape(intros[path.name])+m[2],text,count=1,flags=re.S)
        if path.name in COPY: text = metadata(text,*COPY[path.name])

        def schema(match):
            data = json.loads(match[1])
            before = json.dumps(data,ensure_ascii=False)
            def update(node):
                if isinstance(node,list):
                    for item in node:update(item)
                elif isinstance(node,dict):
                    if node.get('@type') == 'WebSite': node.pop('potentialAction',None)
                    if path.name in COPY and node.get('@type') in {'WebPage','CollectionPage','SoftwareApplication'}:
                        node['description'] = COPY[path.name][1]
                    if path.name == 'healthy-fast-food.html' and node.get('@type') == 'ItemList':
                        node.update(name='High-protein fast food under 600 calories',numberOfItems=len(featured),
                            itemListElement=[{'@type':'ListItem','position':i,'name':m['name'],'url':SITE+m['url']+'#menu-comparison'} for i,m in enumerate(featured,1)])
                    for value in node.values():
                        if isinstance(value,(dict,list)):update(value)
            update(data)
            after = json.dumps(data,ensure_ascii=False)
            return match[0] if before == after else '<script type="application/ld+json">'+after+'</script>'
        text = re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,text,flags=re.S)
        if text != path.read_text(encoding='utf-8'):path.write_text(text,encoding='utf-8')

    # The on-site search is static HTML; keep snippets and searchable text in sync.
    path = ROOT/'search.html'; text=path.read_text(encoding='utf-8')
    def search_card(match):
        block=match[0];href=re.search(r'href="([^"#?]+)',block)
        if not href or href[1] not in COPY:return block
        target=(ROOT/href[1]).read_text(encoding='utf-8')
        title=html.unescape(re.sub('<[^>]+>','',re.search(r'<h1\b[^>]*>(.*?)</h1>',target,re.S)[1]))
        description=COPY[href[1]][1]
        block=re.sub(r'(<span class="search-hit-copy">).*?(</span>)',lambda m:m[1]+html.escape(description)+m[2],block,flags=re.S)
        block=re.sub(r'data-search="[^"]*"',lambda m:'data-search="'+html.escape(title+' '+description,quote=True)+'"',block)
        return block
    text=re.sub(r'<a\b[^>]*class="[^"]*search-hit[^\"]*"[^>]*>.*?</a>',search_card,text,flags=re.S)
    path.write_text(text,encoding='utf-8')
    # Only materially changed pages receive a new modification date.
    path=ROOT/'sitemap.xml';text=path.read_text(encoding='utf-8')
    for name in set(COPY)|{'search.html'}:
        pattern=r'(<loc>'+re.escape(SITE+name)+r'</loc>\s*<lastmod>)[^<]*(</lastmod>)'
        text=re.sub(pattern,lambda m:m[1]+'2026-09-14'+m[2],text)
    path.write_text(text,encoding='utf-8')
    print('Search visibility: useful meal lists, six page descriptions, U.S. coverage and clean website schema.')

if __name__ == '__main__':run()
