"""Improve five existing articles with precise titles and source-based utilities.

The tools read retained article tables and the existing restaurant registry.
They add no catalog records and do not imply that Google will rank a page.
"""
from pathlib import Path
from html import escape, unescape
import json
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from normalize_calculator_layouts import Document
from build_flagship_release import replace

ROOT = Path(__file__).resolve().parents[2]
DATE = '2026-10-24'
SLUGS = {
 'greggs-breakfast-baguette-calories-protein': (
  'Greggs Breakfast Baguette Calories & Protein',
  'Greggs breakfast baguette calories and protein',
  'Compare Greggs bacon, sausage and omelette breakfast baguettes at 441–550 calories. Add a regular coffee and calculate the calories and protein in your order.'),
 'tim-hortons-canada-breakfast-muffin-biscuit-wrap': (
  'Tim Hortons Breakfast Calories & Protein: Canada',
  'Tim Hortons breakfast calories and protein in Canada',
  'Compare Canadian Tim Hortons breakfast sandwiches and Farmer’s Wraps. Calculate calories, protein, carbs and fat with an optional hash brown and black coffee.'),
 'fage-plain-greek-yogurt-0-2-5-percent': (
  'FAGE 0% vs 2% vs 5%: Calories & Protein',
  'FAGE 0% vs 2% vs 5%: calories and protein',
  'Compare FAGE Total 0%, 2% and 5% plain Greek yogurt using U.S. labels. Enter your portion in grams to calculate calories, protein, carbs, fat and saturated fat.'),
 'barilla-australia-protein-plus-vs-spaghetti': (
  'Barilla Protein+ vs Regular Pasta: Australia Nutrition',
  'Barilla Protein+ vs regular pasta: calories and protein',
  'Compare Barilla Protein+ and classic spaghetti using Australian nutrition panels. Calculate your dry portion’s calories, protein and fibre without mixing cooked weights.'),
 'barcode-food-search-label-check': (
  'Food Barcode Lookup: Find Calories & Check the Label',
  'Look up food by barcode and check its nutrition',
  'Search a food barcode for calories and macros, then check the exact product and portion. Learn what to do when a barcode returns the wrong food or no match.'),
}
FIELDS = [{'key': k, 'label': label} for k, label in [('cal', 'kcal'), ('p', 'Protein (g)'), ('c', 'Carbs (g)'), ('fat', 'Fat (g)')]]
CONTEXT_LINKS = {
 'fast-food-breakfast-protein-comparison.html': [
  ('greggs-breakfast-baguette-calories-protein', 'UK: calculate a Greggs baguette and coffee'),
  ('tim-hortons-canada-breakfast-muffin-biscuit-wrap', 'Canada: calculate a Tim Hortons breakfast')],
 'high-protein-foods-list.html': [('fage-plain-greek-yogurt-0-2-5-percent', 'Compare FAGE yogurt protein in your portion · U.S. labels')],
 'serving-size-vs-portion-size.html': [
  ('fage-plain-greek-yogurt-0-2-5-percent', 'Scale a bowl of FAGE yogurt · U.S. labels'),
  ('barilla-australia-protein-plus-vs-spaghetti', 'Scale dry Barilla pasta · Australian labels'),
  ('barcode-food-search-label-check', 'Look up a barcode and check the label serving')],
}


def e(value):
    return escape(str(value), quote=True)


def plain(value):
    return re.sub(r'\s+', ' ', unescape(re.sub('<[^>]*>', ' ', value))).strip()


def label_rows(slug):
    """Read the original authored source table, never generated output/tool totals."""
    from ultimate_release.editorial_foodtools import build_articles
    row = next(r for r in build_articles() if r['slug'] == slug+'.html')
    text = row['body_html']
    table = next(n for n in Document(text).nodes if n['tag'] == 'table')
    fragment = text[table['inner']:table['close']]
    rows = re.findall(r'<tr>(.*?)</tr>', fragment, re.S)[1:]
    extra = [{'key': 'sat', 'label': 'Saturated fat (g)'}] if slug.startswith('fage-') else [
        {'key': 'f', 'label': 'Fibre (g)'}, {'key': 'na', 'label': 'Sodium (mg)'}]
    fields = FIELDS+extra
    data = []
    for row in rows:
        cells = [plain(x) for x in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.S)]
        assert len(cells) == len(fields)+1, cells
        data.append(dict(name=cells[0], **{field['key']: float(value) for field, value in zip(fields, cells[1:])}))
    return dict(kind='scale', baseGrams=170 if slug.startswith('fage-') else 100, fields=fields, rows=data)


def breakfast_model(slug):
    registry = json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    greggs = slug.startswith('greggs-')
    market, chain = ('GB', 'Greggs') if greggs else ('CA', 'Tim Hortons')
    names = ['Omelette Breakfast Baguette', 'Bacon Breakfast Baguette', 'Sausage Breakfast Baguette', 'Bacon & Sausage Breakfast Baguette'] if greggs else [
        'Egg & Cheese English Muffin', 'Egg & Cheese Homestyle Biscuit', 'Bacon English Muffin', 'Sausage English Muffin', "Bacon Farmer's Wrap", "Sausage Farmer's Wrap"]
    def take(name):
        rows = [r for r in registry if r['market'] == market and r['chain'] == chain and r['name'] == name]
        assert len(rows) == 1, (market, chain, name)
        r = rows[0]
        assert r.get('verificationStatus', '').startswith('official-'), r['id']
        return {k: r.get(k) for k in ['id', 'name', 'serving', 'market', 'source', 'cal', 'p', 'c', 'fat']}
    mains = [take(name) for name in names]
    drinks = [take(name) for name in (['Americano Regular', 'Latte Regular'] if greggs else ['Original Blend Coffee - Medium'])]
    assert len({r['source'] for r in mains+drinks}) == 1
    return dict(kind='breakfast', market=market, fields=FIELDS, mains=mains, drinks=drinks,
                side=None if greggs else take('Hash Brown'))


def render_tool(slug, text):
    barcode = slug.startswith('barcode-')
    if barcode:
        return ('<section class="article-tool" id="article-tool" aria-labelledby="article-tool-title">'
            '<h2 id="article-tool-title">Find a food by barcode</h2><p>Type the number printed below the bars. Keep any leading zeros.</p>'
            '<form action="/food-library.html" method="get"><label for="article-barcode">Barcode number'
            '<input type="search" id="article-barcode" name="q" inputmode="numeric" pattern="[0-9]{8}|[0-9]{12,14}" maxlength="14" required aria-describedby="barcode-help" placeholder="UPC or EAN number"></label>'
            '<button type="submit" class="btn btn-primary">Look up food</button></form>'
            '<p class="article-tool-note" id="barcode-help">Manual number lookup; no camera needed. A match still needs the product, country and serving checks below. A missing result is not a zero-calorie food.</p></section>')
    model = breakfast_model(slug) if slug.startswith(('greggs-', 'tim-hortons-')) else label_rows(slug)
    if model['kind'] == 'scale':
        title = 'Calculate your yogurt portion' if slug.startswith('fage-') else 'Calculate your dry pasta portion'
        controls = '<label for="article-grams">Portion weight (g)<input id="article-grams" name="grams" type="number" min="0.1" max="2000" step="0.1" value="'+str(model['baseGrams'])+'" required aria-describedby="article-tool-error article-tool-note"></label>'
        from ultimate_release.editorial_foodtools import build_articles
        original = next(r['body_html'] for r in build_articles() if r['slug'] == slug+'.html')
        node = next(n for n in Document(original).nodes if n['tag'] == 'table')
        result = original[node['start']:node['end']]
        note = 'Calculated from the source-market label values below, including label rounding. Toppings, sauce and cooking water are not included.'
    else:
        title = 'Calculate your Greggs breakfast' if model['market'] == 'GB' else 'Calculate your Canadian breakfast'
        controls = '<label for="article-main">Breakfast item<select id="article-main" name="main">'+''.join('<option value="'+str(i)+'">'+e(r['name'])+'</option>' for i, r in enumerate(model['mains']))+'</select></label>'
        controls += '<label for="article-drink">Drink<select id="article-drink" name="drink"><option value="">No drink added</option>'+''.join('<option value="'+str(i)+'">'+e(r['name'])+'</option>' for i, r in enumerate(model['drinks']))+'</select></label>'
        if model['side']:
            controls += '<label><input type="checkbox" name="side">Add one separate hash brown</label>'
        r = model['mains'][0]
        result = '<table><caption>Selected breakfast · no side or drink added</caption><thead><tr><th scope="col">Order</th>'+''.join('<th scope="col">'+e(f['label'])+'</th>' for f in FIELDS)+'</tr></thead><tbody><tr><th scope="row">'+e(r['name'])+'</th>'+''.join('<td>'+str(r[f['key']])+'</td>' for f in FIELDS)+'</tr></tbody></table>'
        note = 'GetMacros adds the selected source portions once. This is a calculated order, not a restaurant-published combo. No extra milk, sugar, sauce or substitutions are inferred.'
    encoded = json.dumps(model, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    return ('<section class="article-tool" id="article-tool" data-article-tool aria-labelledby="article-tool-title">'
        '<h2 id="article-tool-title">'+title+'</h2><form hidden>'+controls+'<button class="btn btn-primary" type="submit">Update comparison</button></form>'
        '<p class="article-tool-error" id="article-tool-error" data-tool-error role="status"></p><p data-tool-selection></p>'
        '<div class="table-wrap" data-tool-results tabindex="0" role="region" aria-label="Calculated nutrition">'+result+'</div>'
        '<p class="article-tool-note" id="article-tool-note">'+note+' <a href="#article-sources">Source editions and limits</a>.</p>'
        '<script type="application/json" data-tool-model>'+encoded+'</script></section>')


def apply():
    from search_recovery.build import metadata
    changed = []
    for slug, (title, h1, description) in SLUGS.items():
        path = ROOT/(slug+'.html')
        text = path.read_text(encoding='utf-8')
        # Replace the owned panel in place. Its retained source table remains
        # available to no-script readers and repeat publication builds.
        existing = next((n for n in Document(text).nodes if n['attrs'].get('id') == 'article-tool'), None)
        tool = render_tool(slug, text)
        if existing:
            text = replace(text, existing, tool)
        elif slug.startswith(('fage-', 'barilla-')):
            node = next(n for n in Document(text).nodes if 'table-wrap' in n['attrs'].get('class', '').split())
            text = replace(text, node, tool)
        else:
            body = next(n for n in Document(text).nodes if 'editorial-body' in n['attrs'].get('class', '').split())
            at = body['inner']
            if slug.startswith(('greggs-', 'tim-hortons-')):
                first = next(n for n in Document(text).nodes if 'table-wrap' in n['attrs'].get('class', '').split())
                at = first['end']
            text = text[:at]+tool+text[at:]
        text = re.sub(r'<h1\b[^>]*>.*?</h1>', '<h1>'+e(h1)+'</h1>', text, count=1, flags=re.S)
        text = metadata(text, title, description)
        if slug.startswith('barilla-'):
            text = text.replace('Sources checked 2026-10-19.', 'Sources checked 2026-10-24.')
        # The original publication and source-check dates remain truthful.
        text = re.sub(r'<!-- article-tool-update:start -->.*?<!-- article-tool-update:end -->', '', text, flags=re.S)
        byline = next(n for n in Document(text).nodes if 'editorial-byline' in n['attrs'].get('class', '').split())
        label = '<!-- article-tool-update:start --> · Updated <time datetime="'+DATE+'">October 24, 2026</time><!-- article-tool-update:end -->'
        text = text[:byline['close']]+label+text[byline['close']:]
        for n in sorted(Document(text).nodes, key=lambda n:n['start'], reverse=True):
            if n['tag'] != 'script' or n['attrs'].get('type') != 'application/ld+json': continue
            value = json.loads(text[n['inner']:n['close']])
            if isinstance(value, dict) and value.get('@type') == 'Article':
                value.update(headline=h1, description=description, dateModified=DATE)
                text = text[:n['inner']]+json.dumps(value, ensure_ascii=False)+text[n['close']:]
        if '/css/article-tools.css' not in text and 'data-source-path="css/article-tools.css"' not in text:
            text = text.replace('</head>', '<link rel="stylesheet" href="/css/article-tools.css"></head>')
        if not slug.startswith('barcode-') and '/js/article-tools.js' not in text and 'data-source-path="js/article-tools.js"' not in text:
            text = text.replace('</body>', '<script src="/js/article-tools.js" defer></script></body>')
        toc = next(n for n in Document(text).nodes if n['tag'] == 'nav' and n['attrs'].get('aria-label') == 'Article sections')
        if 'href="#article-tool"' not in text[toc['inner']:toc['close']]:
            text = text[:toc['inner']]+'<a href="#article-tool">'+('Look up a barcode' if slug.startswith('barcode-') else 'Calculate your portion' if slug.startswith(('fage-', 'barilla-')) else 'Build your breakfast')+'</a>'+text[toc['inner']:]
        path.write_text(text, encoding='utf-8')
        changed.append('/'+slug+'.html')
    # Intentional links from existing practical guides, without new SEO pages.
    from search_recovery.discovery import append_before_main_end, section
    for parent, links in CONTEXT_LINKS.items():
        path = ROOT/parent; text = path.read_text(encoding='utf-8')
        text = append_before_main_end(text, 'worked-portion-tools', section(
            'worked-portion-tools', 'Try it with an actual food', [('/'+slug+'.html', label) for slug, label in links]))
        path.write_text(text, encoding='utf-8'); changed.append('/'+parent)
    # Match discovery-card copy to the updated destinations, preserving layout.
    path = ROOT/'articles.html'; text = path.read_text(encoding='utf-8')
    for node in sorted(Document(text).nodes, key=lambda n:n['start'], reverse=True):
        if node['tag'] != 'a': continue
        slug = node['attrs'].get('href', '').lstrip('/').removesuffix('.html')
        if slug not in SLUGS: continue
        fragment = text[node['start']:node['end']]
        fragment = re.sub(r'(<h3\b[^>]*>).*?(</h3>)', lambda m:m[1]+e(SLUGS[slug][1])+m[2], fragment, flags=re.S)
        teaser = re.sub(r'\bfibre\b', 'fiber', SLUGS[slug][2])
        fragment = re.sub(r'(<p\b[^>]*>).*?(</p>)', lambda m:m[1]+e(teaser)+m[2], fragment, flags=re.S)
        text = replace(text, node, fragment)
    path.write_text(text, encoding='utf-8'); changed.append('/articles.html')
    ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    tree=ET.parse(ROOT/'sitemap.xml')
    for node in tree.getroot():
        if node.find(ns+'loc').text in {'https://getmacros.net'+r for r in changed}:
            node.find(ns+'lastmod').text=DATE
    ET.register_namespace('', ns[1:-1]);tree.write(ROOT/'sitemap.xml', encoding='utf-8', xml_declaration=True)
    out=ROOT/'docs/article-utility-2026-10-24';out.mkdir(exist_ok=True)
    (out/'implementation.json').write_text(json.dumps({'date':DATE,'articleRoutes':['/'+s+'.html' for s in SLUGS], 'routes':changed,
        'newCatalogRecords':0,'newPublicPages':0,'interactiveCalculators':4,'manualBarcodeForms':1,'contextLinks':CONTEXT_LINKS},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Five existing articles: intent-specific metadata, four calculators and one manual barcode lookup; no new catalog records.')


if __name__ == '__main__':
    apply()
