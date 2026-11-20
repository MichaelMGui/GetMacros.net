"""Build the source-backed first wellness release and its compact food explorer."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))

from build_release_resources import resource_main
from normalize_calculator_layouts import Document

TODAY = '2026-11-20'
HOST = 'https://getmacros.net'
DOCS = ROOT / 'docs/wellness-expansion-2026-11-20'
SOURCE = Path(__file__).parent
EXPLORER = 'nutrient-density-explorer.html'
CLAIM_LIBRARY = 'wellness-claim-evidence.html'
PILLARS = [
    'Nutrient Density, Vitamins & Minerals',
    'Protein, Foods, Diets & Food Comparisons',
    'Cortisol, Stress, Sleep & Recovery',
    'Appearance, Skin, Looksmaxxing & Wellness Culture',
    'Supplements, Peptides & Evidence-Based Wellness',
    'Practical Nutrition, Restaurants & Original Data Studies',
]
FDC = 'https://fdc.nal.usda.gov/food-details/{}/nutrients'
ODS = 'https://ods.od.nih.gov/factsheets/{}-HealthProfessional/'
# Evidence about treatment stays out of the public release queue pending specialist review.
ARTICLES = [
    ('P01-01', 'magnesium', 'magnesium-foods-by-portion.html', 'Which foods have the most magnesium in a real serving?',
     'Compare pumpkin seeds, black beans and spinach by weight and on the plate, with a worked bean-bowl example.',
     [ODS.format('Magnesium'), *[FDC.format(i) for i in (170557, 173735, 168463)]], 'Reference food composition.'),
    ('P01-02', 'choline', 'choline-foods-eggs-soybeans-quinoa.html', 'How much choline is in an egg, soybeans or quinoa?',
     'Compare three NIH reference servings and see how much choline they contribute to a mixed bowl.',
     [ODS.format('Choline')], 'Reference food composition and U.S. label interpretation.'),
    ('P01-03', 'potassium', 'potassium-banana-potato-lentils.html', 'Do lentils or potatoes have more potassium than a banana?',
     'See how a banana, a baked potato and two sizes of cooked lentils compare using NIH food data.',
     [ODS.format('Potassium')], 'Reference food composition.'),
    ('P01-04', 'calcium-dairy-free', 'calcium-without-dairy-milk-soy-tofu.html', 'Can soymilk or tofu match the calcium in a cup of milk?',
     'Compare selected calcium-fortified soymilk, calcium-sulfate tofu and milk, with a worked example and a label check.',
     [ODS.format('Calcium'), 'https://www.healthlinkbc.ca/healthlinkbc-files/calcium-and-your-health'],
     'Reference food composition. Product ingredients, fortification and serving sizes vary.'),
    ('P01-05', 'iron-beans-beef', 'iron-in-lentils-beans-and-beef.html', 'Do lentils have more iron than beef? Compare the actual servings',
     'Use NIH reference servings to compare iron in lentils, chickpeas, trimmed beef and liver, with a worked bowl example.',
     [ODS.format('Iron')], 'Reference food composition and general explanation of bioavailability.'),
    ('P01-07', 'folate', 'folate-folic-acid-dfe-label.html', 'Folate vs. folic acid: what does mcg DFE mean on a label?',
     'Read folate and folic acid on the same label without double counting. Includes a worked U.S. label example.',
     [ODS.format('Folate'), 'https://www.fda.gov/food/nutrition-facts-label/folate-and-folic-acid-nutrition-and-supplement-facts-labels'],
     'U.S. label literacy. The example uses invented label amounts.'),
    ('P01-08', 'b12-without-dairy', 'vitamin-b12-foods-without-dairy.html', 'Which foods have vitamin B12 without dairy?',
     'Compare selected seafood and fortified foods for vitamin B12, then put two label amounts on the same volume basis.',
     [ODS.format('VitaminB12')], 'Reference food composition and a hypothetical label comparison.'),
    ('P01-37', 'vitamin-c-pepper-orange', 'vitamin-c-red-pepper-vs-orange.html', 'Does red pepper have more vitamin C than an orange?',
     'A half cup and a quarter cup can give opposite answers. Compare pepper, orange and strawberries using NIH values.',
     [ODS.format('VitaminC')], 'Reference food composition and food preparation limits.'),
    ('P02-01', 'raw-milk', 'is-raw-milk-more-nutritious.html', 'Is raw milk more nutritious than pasteurized milk?',
     'Compare the nutrition and food-safety questions separately, using FDA and Health Canada guidance.',
     ['https://www.fda.gov/food/buy-store-serve-safe-food/raw-milk-questions-answers',
      'https://www.canada.ca/en/health-canada/services/milk-infant-formula/raw-or-unpasteurized-milk.html'],
     'General food safety education from public health guidance.'),
    ('P02-02', 'grass-fed-beef', 'grass-fed-vs-grain-fed-ribeye-omega-3.html', 'Grass-fed vs. grain-fed ribeye: how much more omega-3?',
     'A North American study found a difference in ribeye fat. Compare the authors’ standardized serving model and the actual limits.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC13012854/'], 'Analytical comparison of commercial samples.'),
    ('P03-01', 'caffeine', 'caffeine-before-bed-dose-and-timing.html', 'How late is too late for caffeine? What two trials tested',
     'Compare the dose, timing and limits of two placebo-controlled sleep studies before drawing a cutoff.',
     ['https://pubmed.ncbi.nlm.nih.gov/24235903/', 'https://pubmed.ncbi.nlm.nih.gov/39377163/'],
     'Research summary with no individualized advice or universal cutoff.'),
    ('P03-04', 'cortisol-awakening', 'cortisol-awakening-response-explained.html', 'Cortisol after waking: the time on the clock can mislead',
     'See how cortisol-awakening research distinguishes time since waking from clock time, with a worked timeline.',
     ['https://pubmed.ncbi.nlm.nih.gov/26563991/', 'https://pubmed.ncbi.nlm.nih.gov/36252387/'],
     'Research methods. Individual test interpretation and diagnosis are outside this guide.'),
    ('P03-22', 'infrared-sauna', 'infrared-sauna-recovery-soreness-study.html', 'Does infrared sauna help recovery? What a soreness study measured',
     'See how a crossover study distinguished soreness, jump performance and perceived recovery after resistance exercise.',
     ['https://pubmed.ncbi.nlm.nih.gov/37398966/',
      'https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/heat-and-cold-illness-in-travelers.html'],
      'Evidence interpretation. No heat exposure protocol or individualized advice.'),
    ('P04-01', 'acne', 'diet-and-acne-what-the-trial-tested.html', 'Can diet affect acne? What the trial changed besides sugar',
     'Read what a 12-week acne trial tested and compare its conclusions with the dermatology guideline.',
     ['https://pubmed.ncbi.nlm.nih.gov/17616769/', 'https://www.aad.org/news/updated-guidelines-acne-management'],
     'Specialist review pending.'),
    ('P04-07', 'gua-sha', 'gua-sha-jawline-what-study-measured.html', 'Can gua sha change your jawline? What researchers measured',
     'A small gua sha trial measured distances along the face. See what those measurements tell us about a permanent jawline claim.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC12121324/'],
     'Media literacy. No cosmetic technique, treatment recommendation or before-and-after claim.'),
    ('P05-01', 'supplement-label', 'read-supplement-facts-per-serving.html', 'Supplement Facts: is that amount per capsule or per serving?',
     'Compare fictional Supplement Facts labels and learn what a U.S. ingredient amount or proprietary blend represents.',
     ['https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements'],
     'U.S. label literacy. No supplement dosing or product endorsements.'),
    ('P05-03', 'peptide-labels', 'collagen-peptides-vs-peptide-drugs.html', 'Collagen peptides and peptide drugs: what the labels tell you',
     'See why collagen powder, a peptide face cream and a peptide drug need different evidence and regulatory checks.',
     ['https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements',
      'https://www.fda.gov/cosmetics/cosmetics-laws-regulations/it-cosmetic-drug-or-both-or-it-soap',
      'https://www.fda.gov/drugs/human-drug-compounding/compounding-and-fda-questions-and-answers'],
     'U.S. regulatory and label literacy. No eligibility or advice for a particular product.'),
    ('P05-22', 'creatine-hair', 'creatine-hair-loss-what-trials-measured.html', 'Does creatine cause hair loss? Two trials tested different things',
     'Compare an older DHT study with a 12-week randomized trial that measured hair directly.',
     ['https://pubmed.ncbi.nlm.nih.gov/19741313/', 'https://pubmed.ncbi.nlm.nih.gov/40265319/'],
     'Study interpretation. No dosing, supplement recommendation or clinical assessment.'),
    ('P06-01', 'breakfast-fiber', 'fast-food-breakfast-fiber-data.html', 'How much fiber do U.S. fast-food breakfasts actually list?',
     'An audit of the fiber figures in U.S. breakfast rows, with totals by chain and examples of how portion size affects comparisons.',
     ['https://getmacros.net/fast-food-nutrition-data-report.html',
      'https://www.chick-fil-a.com/nutrition-allergens', 'https://www.bk.com/nutrition-explorer'],
     'GetMacros registry snapshot. Includes counted portions, sides and named variants with a breakfast tag.'),
]
# The source IDs refer to the already retained USDA reference shards.
FOODS = {
    'Fruit & vegetables': {171688:'Raw apple with skin', 173944:'Raw banana', 169097:'Raw orange',
      170457:'Raw tomato', 169967:'Boiled broccoli, drained, no salt',
      168463:'Boiled spinach, drained, no salt', 170033:'Baked potato flesh, no salt'},
    'Legumes & grains': {173735:'Boiled black beans, no salt', 172421:'Boiled lentils, no salt',
      172475:'Firm tofu, calcium sulfate', 173904:'Dry oats, unfortified',
      173905:'Oats cooked in water, no salt'},
    'Nuts & seeds': {170158:'Dry roasted almonds, no salt', 170557:'Roasted pumpkin seed kernels, no salt'},
    'Dairy, eggs, meat & fish': {170886:'Plain low-fat yogurt', 173424:'Hard-boiled egg',
      171477:'Roasted chicken breast, meat only', 175139:'Atlantic sardines, oil-packed, drained with bones'},
}
NUTRIENTS = ('magnesium', 'potassium', 'calcium', 'iron', 'zinc', 'selenium', 'vitaminC',
             'vitaminB12', 'vitaminA', 'vitaminD', 'vitaminE', 'vitaminK', 'folate', 'p', 'f')
SOURCE_TITLES = {
    ODS.format('Magnesium'): 'NIH Office of Dietary Supplements: Magnesium, selected foods and U.S. label rules',
    ODS.format('Choline'): 'NIH Office of Dietary Supplements: Choline, Table 2',
    ODS.format('Potassium'): 'NIH Office of Dietary Supplements: Potassium, Table 2',
    ODS.format('Folate'): 'NIH Office of Dietary Supplements: Folate, folic acid and dietary folate equivalents',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC12121324/': 'Ahn et al. (2025): Facial roller versus gua sha randomized trial',
    'https://pubmed.ncbi.nlm.nih.gov/24235903/': 'Drake et al. (2013): Caffeine at bedtime or 3 or 6 hours earlier',
    'https://pubmed.ncbi.nlm.nih.gov/39377163/': 'Gardiner et al. (2025): Caffeine dose and timing crossover trial',
    'https://pubmed.ncbi.nlm.nih.gov/17616769/': 'Smith et al. (2007): Low-glycemic-load diet and acne trial',
    'https://www.aad.org/news/updated-guidelines-acne-management': 'American Academy of Dermatology: Evidence in the updated acne guidelines',
    'https://www.fda.gov/food/buy-store-serve-safe-food/raw-milk-questions-answers': 'FDA: Raw milk and pasteurization questions and answers',
    'https://www.canada.ca/en/health-canada/services/milk-infant-formula/raw-or-unpasteurized-milk.html': 'Health Canada: Raw or unpasteurized milk ',
    'https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements': 'FDA: U.S. supplement labels, blend disclosures and regulation',
}


def public_articles():
    return [row for row in ARTICLES if row[1] != 'acne']


def replace_section(text, section_id, replacement):
    node = next((node for node in Document(text).nodes if node['attrs'].get('id') == section_id), None)
    if node:
        return text[:node['start']] + replacement + text[node['end']:]
    main = next(node for node in Document(text).nodes if node['tag'] == 'main')
    return text[:main['close']] + replacement + text[main['close']:]


def projection():
    library = ROOT / 'data/food-library'
    fields = json.loads((library / 'manifest.json').read_bytes())['fields']
    index = {row['id']: row for row in json.loads((library / 'index.json').read_bytes())}
    rows = []
    for group, foods in FOODS.items():
        for source_id, label in foods.items():
            id_ = f'fdc:{source_id}'
            shard = index[id_]['shard']
            data = json.loads((library / 'records' / f'{shard}.json').read_bytes())
            record = next(row for row in data if row['id'] == id_)
            assert record['basis'] == {'amount': 100, 'unit': 'g'} and record['market'] == 'US-reference'
            portions = record.get('portions', [])
            portion = next((p for p in portions if p['label'] == '1 oz' and p['grams'] > 0),
                           next((p for p in portions if p['grams'] > 0), None))
            rows.append(dict(id=source_id, label=label, name=record['name'], group=group, portion=portion,
                             values={key: record['nutrients'].get(key) for key in (*NUTRIENTS, 'cal')}))
    return dict(rows=rows, nutrients={key: fields[key] for key in NUTRIENTS})


def shell(slug, title, summary, main, schema=None, *, private=False):
    # Reuse the retained shared header, theme, footer and reading styles.
    template = (ROOT / 'how-to-read-a-nutrition-label.html').read_text(encoding='utf8')
    doc = Document(template)
    node = next(n for n in doc.nodes if n['tag'] == 'main')
    page = template[:node['start']] + main + template[node['end']:]
    # The source guide has a save-to-shelf control inside its main content.
    # That control is not part of the wellness article or tool template.
    unused_assets = [n for n in Document(page).nodes
                     if n['attrs'].get('data-source-path') in ('css/food-shelf.css', 'js/food-shelf.js')]
    for asset in reversed(unused_assets):
        page = page[:asset['start']] + page[asset['end']:]
    url = HOST + '/' + slug
    full_title = title + ' | GetMacros'
    page = re.sub(r'<title>.*?</title>', lambda _: '<title>' + escape(full_title) + '</title>', page, count=1, flags=re.S)
    page = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{url}">', page)
    page = re.sub(r'<link\b[^>]*hreflang="[^"]*"[^>]*>', '', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', '', page, flags=re.S)
    for field, value in {'description':summary, 'og:description':summary, 'twitter:description':summary,
                        'og:title':full_title, 'twitter:title':full_title, 'og:url':url}.items():
        page = re.sub(r'(<meta (?:name|property)="' + re.escape(field) + r'" content=")[^"]*',
                      lambda match: match[1] + escape(value, quote=True), page)
    if private:
        page = re.sub(r'(<meta name="robots" content=")[^"]*', r'\1noindex, nofollow', page)
    if schema and not private:
        breadcrumb = {'@type':'BreadcrumbList', 'itemListElement':[
            {'@type':'ListItem', 'position':1, 'name':'Guides', 'item':HOST + '/articles.html'},
            {'@type':'ListItem', 'position':2, 'name':title, 'item':url}]}
        data = {'@context':'https://schema.org', '@graph':[schema | {'url':url}, breadcrumb]}
        page = page.replace('</head>', '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=True) +
                            '</script></head>', 1)
    return page


def explorer_page(data, script_url):
    def options(values):
        return ''.join(f'<option value="{escape(key, quote=True)}">{escape(label)}</option>' for key,label in values)
    rows = sorted(data['rows'], key=lambda row: row['values']['magnesium'] if row['values']['magnesium'] is not None else -1, reverse=True)
    initial = ''.join('<tr><th scope="row">' + escape(row['label']) + '</th><td>100 g</td><td>' +
                      (str(row['values']['magnesium']) + ' mg' if row['values']['magnesium'] is not None else 'Unknown') +
                      f'</td><td><a href="{FDC.format(row["id"])}">USDA record {row["id"]}</a></td></tr>' for row in rows)
    summary = f'Compare {len(rows)} USDA reference foods by vitamins, minerals, protein or fiber per 100 g, per portion or per 100 calories.'
    nutrient_options = options((key, value['label']) for key, value in data['nutrients'].items())
    category_options = options((name, name) for name in FOODS)
    payload = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    main = f'''<main id="main-content" class="container"><article class="article-container release-article">
<nav aria-label="Breadcrumb"><a href="/articles.html">Guides</a></nav>
<h1>Nutrient Density Explorer</h1><p>{escape(summary)}</p>
<section data-nutrient-explorer aria-label="Food nutrient comparison">
<form class="form-grid" hidden>
<div><label for="explorer-nutrient">Nutrient</label> <select id="explorer-nutrient" name="nutrient">{nutrient_options}</select></div>
<div><label for="explorer-basis">Compare by</label> <select id="explorer-basis" name="basis"><option value="100g">100 g</option><option value="portion">Listed portion</option><option value="100kcal">100 kcal</option></select></div>
<div><label for="explorer-category">Food category</label> <select id="explorer-category" name="category"><option value="">All categories</option>{category_options}</select></div>
<div><label for="explorer-food">Find a food</label> <input id="explorer-food" type="search" name="food" placeholder="e.g. black beans"></div>
<label><input type="checkbox" name="unknown" checked> Include unknown values</label>
</form>
<p role="status"></p><noscript><p>Magnesium per 100 g is shown below. Enable JavaScript to change nutrients and portions.</p></noscript>
<div class="table-wrap" role="region" aria-label="Food nutrient values" tabindex="0"><table>
<caption>Selected USDA SR Legacy reference foods</caption>
<thead><tr><th scope="col">Food</th><th scope="col">Amount of food</th><th scope="col" data-amount-label>Magnesium per 100 g</th><th scope="col">Source</th></tr></thead>
<tbody>{initial}</tbody></table></div>
<script type="application/json">{payload}</script></section>
<h2>How the amounts are calculated</h2>
<p>A listed portion uses a measure with a weight in the source. For 100 calories, the tool divides by the source energy per 100 g and multiplies by 100. A missing amount or unavailable conversion stays unknown. The results show total nutrient content, which can differ from the amount absorbed.</p>
<p>These are selected U.S. reference foods. Use the exact preparation and source when comparing your own meal. For choline examples, see the separate <a href="/choline-foods-eggs-soybeans-quinoa.html">egg, soybeans and quinoa comparison</a>.</p>
<p><a href="/food-library.html">Search a larger set of reference and packaged foods</a> or <a href="/compare-foods.html">review exact portions side by side</a>.</p></article></main>'''
    page = shell(EXPLORER, 'Nutrient Density Explorer', summary, main)
    page = page.replace('data-family="article"', 'data-family="tool"', 1)
    page = page.replace('data-analytics-page="public"', 'data-analytics-page="off"', 1)
    page = page.replace('</head>', '''<style>
[data-nutrient-explorer] form:not([hidden]){display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem 1rem;align-items:start}
[data-nutrient-explorer] form>div{min-width:0}
[data-nutrient-explorer] form>div>label{display:block;margin-bottom:.25rem}
[data-nutrient-explorer] form :is(select,input[type="search"]){width:100%;min-inline-size:0;min-block-size:44px}
[data-nutrient-explorer] form>label{grid-column:1/-1}
@media(max-width:350px){[data-nutrient-explorer] form:not([hidden]){grid-template-columns:1fr}}
</style></head>''', 1)
    return page.replace('</body>', f'<script src="{script_url}" data-source-path="js/nutrient-explorer.js" defer></script></body>', 1)


def article_page(row):
    id_, key, slug, title, summary, urls, scope = row
    pillar = PILLARS[int(id_[1:3]) - 1]
    body = (SOURCE / (key + '.html')).read_text(encoding='utf-8-sig').strip()
    if key == 'breakfast-fiber':
        body, restaurant_sources = breakfast_fiber(body)
        urls = list(dict.fromkeys([*urls, *restaurant_sources]))
    body = body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    links = [{'url':'/' + EXPLORER, 'label':'Compare vitamins and minerals'}] if id_.startswith('P01') else []
    if key in ('raw-milk','supplement-label'):
        links.append({'url':'/how-to-read-a-nutrition-label.html', 'label':'Read a Nutrition Facts label'})
    if key == 'caffeine':
        links.append({'url':'/articles.html#learn-coffee-drinks', 'label':'Browse coffee and drink guides'})
    if key == 'cortisol-awakening':
        links.append({'url':'/caffeine-before-bed-dose-and-timing.html', 'label':'See how timing changes the comparison in caffeine research'})
    if key == 'peptide-labels':
        links.append({'url':'/read-supplement-facts-per-serving.html', 'label':'Read a Supplement Facts panel'})
    if key == 'gua-sha':
        links.append({'url':'/editorial-policy.html', 'label':'How GetMacros evaluates evidence'})
    if key == 'breakfast-fiber':
        links.extend([{'url':'/restaurant-meal-finder.html?meal=breakfast', 'label':'Browse U.S. breakfast records'},
                      {'url':'/exact-fiber-coverage-denominator.html', 'label':'Read a missing fiber value correctly'}])
    sources = 'Source material checked November 20, 2026. ' + scope
    main = resource_main(dict(slug=slug, title=title, h1=title, description=summary,
                              category=pillar, sourceURLs=urls, sourceScope=sources, body=body, related=links))
    for url in urls:
        label = SOURCE_TITLES.get(url)
        if label:
            main = re.sub(r'(<a href="' + re.escape(escape(url, quote=True)) + r'">)[^<]+',
                          lambda match: match[1] + escape(label.strip()), main)
    main = main.replace('By GetMacros · Published October 3, 2026', 'By GetMacros · Sources checked November 20, 2026')
    # The opening paragraph answers the question. Keep the summary in metadata.
    main = main.replace(f'<p>{escape(summary)}</p>', '', 1)
    if id_.startswith(('P03','P04','P05')):
        main = re.sub(r'<span data-food-character="[^"]+"[^>]*>.*?</span>', '', main, count=1, flags=re.S)
    private = key == 'acne'
    if private:
        main = main.replace('</h1>', '</h1><p>Draft for specialist review</p>', 1)
    schema = {'@type':'Article', 'headline':title, 'description':summary,
              'author':{'@type':'Organization', 'name':'GetMacros', 'url':HOST + '/about.html'}}
    return shell(slug, title, summary, main, schema, private=private)


def breakfast_fiber(body):
    registry = json.loads((ROOT / 'js/order-registry.json').read_bytes())['records']
    rows = [row for row in registry if row['market'] == 'US' and row.get('meal') == 'breakfast']
    known = [row for row in rows if isinstance(row.get('f'), (int, float))]
    count = sum(row['f'] >= 3 for row in known)
    assert (len(rows), len(known), count) == (131, 131, 47), 'Review the breakfast snapshot before changing article counts.'
    counts = []
    for chain in sorted({row['chain'] for row in rows}):
        local = [row for row in rows if row['chain'] == chain]
        measured = [row for row in local if isinstance(row.get('f'), (int, float))]
        counts.append('<tr><th scope="row">' + escape(chain) + '</th><td>' + str(len(local)) +
                      '</td><td>' + str(len(measured)) + '</td><td>' +
                      str(sum(row['f'] >= 3 for row in measured)) + '</td></tr>')
    examples = {'Large Hash Browns': 6, '10 ct Chick-fil-A Chick-n-Minis®': 6,
                'Hash Brown Scramble Burrito w/ No Meat': 5}
    for name, amount in examples.items():
        assert any(row['name'] == name and row['f'] == amount for row in known)
    return body.replace('<!--CHAIN_ROWS-->', ''.join(counts)), sorted({row['source'] for row in rows})


def claim_library_page(script_url):
    claims = [
        ('Food safety', 'Does raw milk have a nutritional advantage?',
         'FDA and Health Canada describe the nutrient profiles of raw and pasteurized milk as similar.',
         'Different fat levels and fortification can change the figures on a carton. The nutrient panel cannot measure the risk of harmful microbes.',
         'is-raw-milk-more-nutritious.html', 'raw-milk'),
        ('Recovery', 'Is there a universal caffeine cutoff for sleep?',
         'Two controlled trials observed sleep disruption after a 400 mg dose.',
         'The smaller-dose trial used a narrow sample. Dose, bedtime and the drink’s actual caffeine are separate questions.',
         'caffeine-before-bed-dose-and-timing.html', 'caffeine'),
        ('Appearance', 'Does gua sha permanently change the jawline?',
         'A small randomized comparison measured changes in distances along the surface of the face.',
         'The study measured neither jawbone change nor persistence after the intervention. It compared two tools without a no-massage group.',
         'gua-sha-jawline-what-study-measured.html', 'gua-sha'),
        ('Supplements', 'Does a U.S. Supplement Facts panel establish FDA approval?',
         'The panel gives the declared serving and ingredient amounts under U.S. labeling rules.',
         'The FDA generally does not approve supplements for safety or effectiveness before sale. An ingredient amount and evidence for a product claim answer separate questions.',
         'read-supplement-facts-per-serving.html', 'supplement-label'),
    ]
    sources = {row[1]: row[5][0] for row in public_articles()}
    entries = ''.join(
        f'<section data-claim-example data-topic="{escape(topic, quote=True)}"><h2>{escape(question)}</h2>'
        f'<dl><dt>What the evidence supports</dt><dd>{escape(finding)}</dd>'
        f'<dt>What remains uncertain</dt><dd>{escape(limit)}</dd></dl><p>'
        f'<a href="/{slug}">Read the evidence guide</a> · <a href="{escape(sources[key], quote=True)}">Primary source</a></p></section>'
        for topic, question, finding, limit, slug, key in claims)
    summary = 'Check claims about raw milk, caffeine timing, gua sha and supplement labels against their primary sources.'
    choices = ''.join(f'<option>{escape(topic)}</option>' for topic, *_ in claims)
    main = f'''<main id="main-content" class="container"><article class="article-container release-article" data-claim-library>
<nav aria-label="Breadcrumb"><a href="/articles.html">Guides</a></nav>
<h1>Wellness Claim Evidence Library</h1><p>{summary}</p>
<form class="form-grid" hidden><div><label for="claim-query">Search claims</label> <input id="claim-query" type="search" name="claim"></div>
<div><label for="claim-topic">Topic</label> <select id="claim-topic" name="topic"><option value="">All topics</option>{choices}</select></div></form>
<p role="status"></p>{entries}<p><a href="/editorial-policy.html">GetMacros editorial and sourcing policy</a></p></article></main>'''
    page = shell(CLAIM_LIBRARY, 'Wellness Claim Evidence Library', summary, main)
    return page.replace('</body>', f'<script src="{script_url}" data-source-path="js/nutrient-explorer.js" defer></script></body>', 1)


def apply():
    for row in ARTICLES:
        parent = DOCS if row[1] == 'acne' else ROOT
        if parent == DOCS and not (SOURCE / (row[1] + '.html')).exists():
            continue
        (parent / row[2]).write_text(article_page(row), encoding='utf8', newline='\n')
    assets = ROOT / 'assets/generated'
    registry = assets / 'manifest.json'
    entries = json.loads(registry.read_bytes())
    key = 'js/nutrient-explorer.js'
    script = (ROOT / key).read_bytes().replace(b'\r\n', b'\n')
    digest = hashlib.sha256(script).hexdigest()
    url = '/assets/generated/js-nutrient-explorer-' + digest[:12] + '.js'
    (ROOT / url.lstrip('/')).write_bytes(script)
    entries[key] = dict(url=url, assetSha256=digest, sourceSha256=digest)
    registry.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf8', newline='\n')
    (ROOT / EXPLORER).write_text(explorer_page(projection(), url), encoding='utf8', newline='\n')
    (ROOT / CLAIM_LIBRARY).write_text(claim_library_page(url), encoding='utf8', newline='\n')

    # Own one crawlable discovery section. The legacy library remains available below it.
    public = public_articles()
    cards = []
    for index, pillar in enumerate(PILLARS, 1):
        items = [r for r in public if r[0].startswith(f'P{index:02d}')]
        links = ''.join(f'<li><a href="/{r[2]}">{escape(r[3])}</a></li>' for r in items)
        if index == 1:
            links += f'<li><a href="/{EXPLORER}">Explore nutrients in 18 reference foods</a></li>'
        if index == 2:
            links += '<li><a href="/high-protein-foods-list.html">High-protein foods</a></li>'
        if index == 6:
            links += '<li><a href="#learn-meal-comparisons">Restaurant meal comparisons</a></li><li><a href="#learn-portions-labels">Food labels and portion guides</a></li>'
        if links:
            cards.append(f'<section><h3>{escape(pillar)}</h3><ul>{links}</ul></section>')
    articles = ROOT / 'articles.html'
    text = articles.read_text(encoding='utf8')
    text = replace_section(text, 'wellness-publication', '')
    main = next(n for n in Document(text).nodes if n['tag'] == 'main')
    section = ('<section id="wellness-publication"><style>#wellness-publication{margin-block:2rem 3rem}'
               '#wellness-publication .wellness-topics{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr));gap:1.25rem 2rem}'
               '#wellness-publication .wellness-topics section{border-top:1px solid var(--line);padding-block-start:.85rem}'
               '#wellness-publication h3{font-size:1.1rem;margin-block:0 .65rem}'
               '#wellness-publication li{margin-block:.45rem}</style>'
               '<h2>Explore food and wellness</h2><p><a href="/' + CLAIM_LIBRARY +
               '">Check the evidence behind a wellness claim</a></p><div class="wellness-topics">' + ''.join(cards) + '</div></section>')
    # Put new topics after the existing masthead and before the guide controls.
    tree = Document(text)
    library = next((n for n in tree.nodes if 'reader-library' in n['attrs'].get('class', '').split()), None)
    features = next((n for n in tree.nodes if 'editorial-features' in n['attrs'].get('class', '').split()), None)
    at = library['start'] if library else features['end'] if features else main['close']
    articles.write_text(text[:at] + section + text[at:], encoding='utf8', newline='\n')

    search = ROOT / 'search.html'
    hits = []
    resources = [(EXPLORER, 'Nutrient Density Explorer', 'Compare vitamins, minerals, protein or fiber.'),
                 (CLAIM_LIBRARY, 'Wellness Claim Evidence Library', 'Check claims against primary evidence.')]
    for slug, title, summary in [(r[2], r[3], r[4]) for r in public] + resources:
        hits.append(f'<a class="search-hit" href="/{slug}" data-search="{escape(title + " " + summary, quote=True)}"><span class="search-hit-name">{escape(title)}</span><span class="search-hit-copy">{escape(summary)}</span></a>')
    search.write_text(replace_section(search.read_text(encoding='utf8'), 'wellness-search',
        f'<section class="search-group" data-group id="wellness-search"><h2>Food and wellness <span data-count>{len(hits)}</span></h2><div class="search-hits">{"".join(hits)}</div></section>'), encoding='utf8', newline='\n')

    density_guide = ROOT / 'fiber-per-portion-vs-density.html'
    link = ('<section id="explore-source-foods"><h2>Try it with USDA food records</h2>'
            '<p>To see how a listed portion changes a comparison, choose Fiber in the '
            f'<a href="/{EXPLORER}">Nutrient Density Explorer</a> and switch between 100 g and Listed portion.</p></section>')
    density_guide.write_text(replace_section(density_guide.read_text(encoding='utf8'),
                             'explore-source-foods', link), encoding='utf8', newline='\n')

    sitemap = ROOT / 'sitemap.xml'
    text = sitemap.read_text(encoding='utf8')
    new = []
    for route in [r[2] for r in public] + [resource[0] for resource in resources]:
        loc = f'<loc>{HOST}/{route}</loc>'
        if loc not in text:
            new.append(f'<url>{loc}<lastmod>{TODAY}</lastmod></url>')
    if new:
        sitemap.write_text(text.replace('</urlset>', ''.join(new) + '</urlset>', 1), encoding='utf8', newline='\n')


if __name__ == '__main__':
    apply()
