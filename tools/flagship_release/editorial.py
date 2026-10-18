"""Four authored, source-backed resources. Import/export only; never edits public pages.

Call export() to write review artifacts in this workstream's documentation folder.
The main release integrator owns HTML rendering, sitemap/search and publication.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlencode
from decimal import Decimal
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/flagship-release-2026-10-18/editorial'
DATE = '2026-10-18'
FIELDS = ('cal', 'p', 'c', 'fat', 'f', 'na', 'sugar')


def e(value):
    return escape(str(value), quote=True)


def number(value):
    if value is None:
        return 'Not reported'
    return format(Decimal(str(value)).normalize(), 'f')


def load(name):
    return json.loads((ROOT / 'tools/flagship_release' / name).read_text(encoding='utf-8'))['records']


UK = load('uk_records.json')
MARKETS = load('markets_records.json')
EVIDENCE = {}


def item(rows, market, chain, name):
    matches = [r for r in rows if r['market'] == market and r['chain'] == chain and r['name'] == name]
    assert len(matches) == 1, (market, chain, name, len(matches))
    row = matches[0]
    assert row.get('verificationStatus') in ('official-table-reviewed', 'official-page-reviewed', 'calculated-from-official-components'), row.get('verificationStatus')
    EVIDENCE[row['id']] = {k: row.get(k) for k in ('id', 'market', 'chain', 'name', 'serving', 'nativeNutrients', 'source', 'sourceDate', 'checked', 'verificationStatus', 'components', 'conversions') + FIELDS}
    return row


def sum_rows(name, rows):
    assert len({r['market'] for r in rows}) == 1
    result = dict(name=name, market=rows[0]['market'], serving=' + '.join(r['serving'] for r in rows), calculated=True)
    for field in FIELDS:
        result[field] = None if any(r.get(field) is None for r in rows) else float(sum(Decimal(str(r[field])) for r in rows))
    salts = [r.get('nativeNutrients', {}).get('salt') for r in rows]
    result['salt'] = None if any(x is None for x in salts) else float(sum(Decimal(str(x)) for x in salts))
    return result


def table(rows, caption, fields=('cal', 'p', 'c', 'fat'), serving=True):
    headings = {'cal': 'Energy (kcal)', 'p': 'Protein (g)', 'c': 'Carbs (g)', 'fat': 'Fat (g)', 'f': 'Fibre (g)', 'na': 'Sodium (mg)', 'salt': 'Salt (g)', 'sugar': 'Total sugars (g)'}
    cells = []
    for r in rows:
        portion = '<span class="table-portion">' + e(r['serving']) + '</span>' if serving else ''
        values = []
        for f in fields:
            value = r.get('salt', r.get('nativeNutrients', {}).get('salt')) if f == 'salt' else r.get(f)
            values.append('<td>' + number(value) + '</td>')
        cells.append('<tr><th scope="row">' + e(r['name']) + portion + '</th>' + ''.join(values) + '</tr>')
    return '<div class="table-wrap" role="region" tabindex="0" aria-label="' + e(caption) + '"><table><caption>' + e(caption) + '</caption><thead><tr><th scope="col">Food and portion</th>' + ''.join('<th scope="col">' + headings[f] + '</th>' for f in fields) + '</tr></thead><tbody>' + ''.join(cells) + '</tbody></table></div>'


def compare(rows, label):
    query = [('item', 'order:' + r['market'] + ':' + r['id']) for r in rows] + [('basis', 'portions')]
    return '<p><a href="/compare-foods.html?' + e(urlencode(query)) + '">' + e(label) + '</a></p>'


def sources(urls, edition):
    return '<section class="resource-sources"><h2>Sources and portions</h2><p>' + edition + '</p><ul>' + ''.join('<li><a href="' + e(url) + '">' + e(label) + '</a></li>' for url, label in urls) + '</ul><p>Food is prepared to order; portions and recipes can vary. Ingredient preferences are not an allergy check. Use the restaurant’s current ingredient and allergen information when ordering.</p></section>'


def article(route, title, description, market, body, rows, urls, intent, overlap, query):
    return dict(route=route, title=title, description=description, market=market, body=body, sourceUrls=[u for u, _ in urls], sourceIds=[r['id'] for r in rows], preparedAt=DATE, sourceCheckedAt=DATE, datePublished=None, dateModified=None, status='authored-and-source-checked; awaiting release integration and browser verification', intent=intent, existingOverlap=overlap, observedQuery=query)


def build_articles():
    result = []
    sausage = item(UK, 'GB', 'LEON', 'Sausage & Egg Muffin')
    bacon = item(UK, 'GB', 'LEON', 'Bacon & Egg Muffin')
    pot = item(UK, 'GB', 'LEON', 'Smoked Salmon & Avocado Egg Pot')
    sando = item(UK, 'GB', 'LEON', 'Halloumi, Egg & Avo Sando')
    rows = [pot, bacon, sausage, sando]
    urls = [(r.get('productUrl') or r['source'], r['name'] + ' · official LEON UK page') for r in rows] + [('https://leon.co/menu/', 'LEON UK menu and breakfast categories')]
    body = '''<p class="article-lead">LEON’s UK Sausage &amp; Egg Muffin lists 454 kcal and 25 g protein. The Smoked Salmon &amp; Avocado Egg Pot lists 211 kcal and 13 g protein. The pot is a smaller, different recipe; it is not the same breakfast with the bread removed.</p>
<h2>Compare the whole breakfast</h2><p>Use one named portion when deciding what to order. The egg pot weighs 145 g in the source, the two savoury muffins 217–224 g, and the halloumi sando 271 g. A lower number per portion can partly reflect a smaller amount of food.</p>''' + table(rows, 'LEON UK breakfast: one published portion of each recipe') + '''
<h2>Two muffins, a small calorie difference</h2><p>The Bacon &amp; Egg Muffin has 431 kcal and 24 g protein. The Sausage &amp; Egg Muffin has 23 kcal more and 1 g more protein. Those differences are small compared with the change from either muffin to the egg pot or the larger sando.</p><p>Salt is a separate comparison: LEON lists 3.7 g for the bacon muffin and 2.1 g for the sausage muffin. The lower-calorie muffin therefore does not have the lower salt figure. Neither recipe is a universal winner; compare the fields you actually care about.</p>''' + compare([bacon, sausage], 'Compare the two muffins by their published portions') + '''
<h2>What changes with an egg pot?</h2><p>The salmon and avocado pot has 243 fewer kcal and 12 g less protein than the sausage-and-egg muffin. It also lists 2.5 g carbohydrate and 16 g fat. This is useful if you want a smaller breakfast, but it does not tell us how full you will feel or what else you should eat.</p><p>The recipes contain different ingredients and amounts. Do not subtract the pot’s values from a muffin to estimate the nutrition of bread, sauce or an egg. Log the named item that you actually ordered; add a coffee, side or extra separately using its own serving.</p>
<h2>When you want the larger option</h2><p>The Halloumi, Egg &amp; Avo Sando lists 610 kcal and 31 g protein, with 41 g carbohydrate and 35 g fat. Compared with the sausage muffin, that is 156 more kcal for 6 g more protein. Its 271 g serving and different filling are part of the choice, not an unexplained upgrade.</p><p>LEON’s menu groups these items under breakfast, shown as until 11 am in the source read on 18 October 2026. Check your branch: a source-listed breakfast is not a promise that every restaurant stocks it or serves it at every hour.</p><p><a href="/restaurant-meal-finder.html?market=GB">Find another UK meal</a> · <a href="/food-diary.html?market=GB">Log your actual breakfast</a></p>''' + sources(urls, 'UK per-portion menu and individual product information read on 18 October 2026. LEON does not state an edition date on these menu records. Salt figures above are the restaurant’s published grams, not sodium milligrams.')
    result.append(article('leon-uk-breakfast-muffin-egg-pot-nutrition.html', 'LEON UK breakfast: muffins, egg pot and sando compared', 'Compare LEON UK breakfast portions, calories, protein and salt: two egg muffins, the salmon egg pot and halloumi sando.', 'GB', body, rows, urls, 'Choose among different LEON UK breakfast formats without treating portions as equivalent.', 'No existing LEON article found. General breakfast comparisons focus on other restaurants or U.S. records; this guide is specific to current UK recipes.', 'LEON breakfast calories protein egg pot muffin UK official nutrition'))

    base = item(UK, 'GB', 'Nando’s', '1/4 Chicken')
    rice = item(UK, 'GB', 'Nando’s', 'Spicy Rice · Regular')
    chips = item(UK, 'GB', 'Nando’s', 'PERi-Salted Chips · Regular')
    corn = item(UK, 'GB', 'Nando’s', 'Corn on the Cob · Regular')
    rows = [base, rice, chips, corn]
    plates = [sum_rows('1/4 Chicken + regular Spicy Rice', [base, rice]), sum_rows('1/4 Chicken + regular PERi-Salted Chips', [base, chips]), sum_rows('1/4 Chicken + regular Corn on the Cob', [base, corn])]
    urls = [('https://www.nandos.co.uk/food/menu/', 'Nando’s official UK menu, side sizes and regional entries'), (base['source'], 'Official Nando’s menu nutrition snapshot used for the calculations')]
    body = '''<p class="article-lead">Using Nando’s standard UK menu portions, 1/4 Chicken plus regular Spicy Rice totals 535 kcal and 43.1 g protein. Keep the same chicken and choose regular PERi-Salted Chips instead: the listed food total becomes 787 kcal and 44 g protein.</p><p>These are sums of the named chicken and one named side. They do not include an extra sauce, dessert, drink or a second side, and they are not a restaurant-published combo total.</p>
<h2>Start with the exact portions</h2>''' + table(rows, 'Official standard-menu portions before combining', ('cal', 'p', 'c', 'fat')) + '''
<p>For example, the rice order is 289 + 246 = 535 kcal and 39.3 + 3.8 = 43.1 g protein. Each item is counted once. Do not add a chicken-and-sides bundle total on top of these components.</p>
<h2>Same chicken, three different sides</h2>''' + table(plates, 'GetMacros-calculated chicken-and-one-side totals', ('cal', 'p', 'f', 'salt'), serving=False) + '''
<p>Switching from the regular chips to the regular rice changes this order by 252 kcal, 0.9 g protein and 4 g fibre. The chips add more fibre in these particular published portions: 7.9 g versus 3.9 g in the rice. A single label such as “lighter side” would hide that trade-off.</p><p>The corn order totals 431 kcal and 42.8 g protein. Nando’s describes the regular Corn on the Cob as served with butter; do not log it as plain, unbuttered corn or silently remove butter from the published recipe.</p>''' + compare([rice, chips], 'Compare the two regular side portions') + '''
<h2>Regular, large and Nandino are different entries</h2><p>Choose the regular side shown here. The menu also has large sides intended for sharing and separate Nandino portions. A regular side is not automatically half of every large side, and a child’s side is not interchangeable with the adult entry.</p><p>No gram weight is supplied for these source portions, so this comparison uses named servings. If you divide a shared side, log the fraction you ate as an estimate rather than claiming that it was weighed.</p>
<h2>Check Northern Ireland and your sauce choice</h2><p>The official UK menu lists a separate Northern Ireland Spicy Rice recipe starting at 197 kcal, rather than the standard 246 kcal used above. The 535 kcal rice total therefore must not be presented as the Northern Ireland order. Use that branch’s matching local entry instead.</p><p>The calculations use the named base recipes without adding optional spice adjustments, bottled sauces or extras. Check the current restaurant information for the recipe you choose. Salt is shown in grams here; where GetMacros displays sodium, the conversion is salt in grams × 1,000 ÷ 2.5, not a separate laboratory sodium measurement.</p><p><a href="/restaurant-meal-finder.html?market=GB">Browse UK meals</a> · <a href="/compare-complete-restaurant-orders.html?market=GB">Build a precisely listed order</a></p>''' + sources(urls, 'Standard UK menu recipes read on 18 October 2026; no fixed source edition date is stated. The separate Northern Ireland recipe and Gatwick-specific entries are not silently substituted into this table. Totals are GetMacros calculations from published portions; no menu price or nationwide availability is claimed.')
    result.append(article('nandos-uk-quarter-chicken-rice-chips-corn.html', 'Nando’s UK: 1/4 Chicken with rice, chips or corn', 'Compare calculated Nando’s chicken-and-side totals using exact regular UK portions, including the Northern Ireland rice distinction.', 'GB', body, rows, urls, 'Keep a Nando’s main fixed and compare the real impact of the chosen side and source portion.', 'No existing chicken-and-side Nando’s article found. Existing country directories are restaurant coverage, not this exact order calculation.', "Nando's UK chicken butterfly spicy rice chips nutrition calories"))

    egg = item(UK, 'GB', 'Wendy’s', 'Classic Egg & Cheese Muffin')
    sausage = item(UK, 'GB', 'Wendy’s', 'Classic Sausage & Cheese Muffin')
    bacon = item(UK, 'GB', 'Wendy’s', 'Classic Bacon & Cheese Muffin')
    wrap = item(UK, 'GB', 'Wendy’s', 'Breakfast Wrap Egg & Cheese w/ Brown Sauce')
    rows = [wrap, egg, bacon, sausage]
    urls = [(egg['source'], 'Wendy’s UK national nutrition information · 25 March 2026'), ('https://www.wendys.com/en-gb/breakfast-wraps', 'Wendy’s UK breakfast wraps and branch-availability notice')]
    body = '''<p class="article-lead">Wendy’s UK lists its Classic Egg &amp; Cheese Muffin at 319 kcal and 14 g protein. The Egg &amp; Cheese Breakfast Wrap with brown sauce is 290 kcal and 13 g protein. These are individual breakfast foods, with no potato side or drink added.</p>
<h2>A wrap is not automatically a bigger breakfast</h2><p>In this comparison, the egg-and-cheese wrap has 29 fewer kcal and 1 g less protein than the egg-and-cheese muffin. The wrap’s named brown-sauce recipe is 137 g; the muffin is 130 g. The difference is about their actual recipes, not a rule that wraps contain less energy than bread.</p>''' + table(rows, 'Wendy’s UK breakfast: one named item, not a combo') + compare([wrap, egg], 'Compare the egg-and-cheese wrap and muffin') + '''
<h2>What do bacon and sausage change?</h2><p>The Classic Bacon &amp; Cheese Muffin lists 384 kcal and 19 g protein. The Classic Sausage &amp; Cheese Muffin lists 477 kcal and 23 g protein. Moving from the egg-and-cheese muffin to the sausage-and-cheese one is a 158 kcal difference alongside 9 g more protein.</p><p>Those are separate menu recipes. This is not a calculation of what happens when a sausage is added to the egg muffin; the table does not establish which ingredients or amounts are held constant. Choose the exact name when logging rather than combining two complete sandwiches as if one were an add-on.</p>
<h2>Keep salt separate from calories</h2>''' + table(rows, 'Published fibre and salt in the same breakfast portions', ('f', 'salt')) + '''
<p>The egg-and-cheese wrap has 1.2 g salt in the named brown-sauce version; the egg-and-cheese muffin has 1 g. The lower-calorie choice is therefore not the lower-salt one. Similarly, the bacon-and-cheese muffin lists 1.7 g salt and the sausage-and-cheese muffin 1.4 g.</p><p>Use the published grams of salt when comparing this UK chart. A tool showing sodium will use different units; salt and sodium numbers cannot be placed in the same column without conversion.</p>
<h2>Order, then log the whole breakfast</h2><ol><li>Check that your Wendy’s branch serves breakfast. The official UK page says breakfast is not available at every location.</li><li>Match the exact filling and sauce. A red-sauce wrap has its own source entry, even where the energy figure happens to match.</li><li>Add any potato side, coffee, milk, sugar or other extra as its own supported portion. A sandwich value is not the total for a priced breakfast meal.</li></ol><p>The nutrition chart is the UK edition dated 25 March 2026, read on 18 October 2026. Later product changes and branch availability are separate checks; a newer retrieval date does not turn the chart into a new recipe edition.</p><p><a href="/restaurant-meal-finder.html?market=GB">Find a UK breakfast</a> · <a href="/food-diary.html?market=GB">Log the breakfast you ordered</a></p>''' + sources(urls, 'Values are per named serving from Wendy’s UK chart, dated 25 March 2026. The live official breakfast-wrap page was also inspected for current calorie labels and its location-availability warning. This is not a U.S. Wendy’s comparison. Salt is the chart’s original gram value.')
    result.append(article('wendys-uk-breakfast-muffin-wrap-calories-protein.html', 'Wendy’s UK breakfast: muffins versus the egg-and-cheese wrap', 'Compare Wendy’s UK breakfast calories, protein, portions, fibre and salt, with clear sauce and combo assumptions.', 'GB', body, rows, urls, 'Choose the exact UK Wendy’s breakfast recipe and avoid confusing single-item and combo nutrition.', 'The existing Wendy’s guide is U.S.-focused. No existing UK breakfast-format comparison was found; general breakfast pages do not answer these recipe/portion questions.', "Wendy's UK breakfast muffin wrap calories nutrition"))

    sandwich = item(MARKETS, 'CA', 'Chick-fil-A', 'Grilled Chicken Sandwich')
    fries = item(MARKETS, 'CA', 'Chick-fil-A', 'Small Chick-fil-A Waffle Potato Fries®')
    medium = item(MARKETS, 'CA', 'Chick-fil-A', 'Medium Chick-fil-A Waffle Potato Fries®')
    large = item(MARKETS, 'CA', 'Chick-fil-A', 'Large Chick-fil-A Waffle Potato Fries®')
    tea = item(MARKETS, 'CA', 'Chick-fil-A', 'Small Freshly-Brewed Unsweetened Iced Tea')
    fries_order = item(MARKETS, 'CA', 'Chick-fil-A', 'Grilled sandwich, small waffle fries & small unsweet tea')
    calculated = sum_rows('check', [sandwich, fries, tea])
    assert all(Decimal(str(fries_order[f])) == Decimal(str(calculated[f])) for f in FIELDS)
    plates = [sum_rows('Grilled sandwich + small fries + small unsweetened tea', [sandwich, fries, tea]), sum_rows('Grilled sandwich + medium fries + small unsweetened tea', [sandwich, medium, tea]), sum_rows('Grilled sandwich + large fries + small unsweetened tea', [sandwich, large, tea])]
    rows = [sandwich, fries, medium, large, tea, fries_order]
    urls = [('https://www.chick-fil-a.ca/nutrition-allergens', 'Chick-fil-A Canada official nutrition and allergen table'), ('https://www.chick-fil-a.ca/menu/sides', 'Official Canadian side menu'), ('https://www.chick-fil-a.ca/menu/entrees/grilled-chicken-sandwich', 'Official Canadian grilled sandwich')]
    body = '''<p class="article-lead">A Canadian Grilled Chicken Sandwich with small waffle fries and a small unsweetened iced tea totals 700 kcal and 32.1 g protein. Keep the same sandwich and tea, and change to medium fries: the calculated total is 800 kcal. Large fries bring it to 980 kcal.</p><p>The choice changes the side portion, not the sandwich recipe. These sums use Canadian menu values and three specifically named fry sizes.</p>
<h2>What is in the order?</h2><ul><li><strong>Same main:</strong> one Canadian Grilled Chicken Sandwich, the published 205 g build: 380 kcal and 28.1 g protein.</li><li><strong>Same drink:</strong> one Small Freshly-Brewed Unsweetened Iced Tea, listed as a 451 g serving, with 0 kcal explicitly reported. This is not sweet tea, lemonade or a milkshake.</li><li><strong>One side:</strong> small fries at 96 g, medium at 125 g, or large at 179 g. No extra dipping sauce is included.</li></ul>''' + table(plates, 'GetMacros-calculated Canadian orders: same sandwich and small unsweetened tea', serving=False) + '''
<h2>Small, medium and large are not equal steps</h2>''' + table([fries, medium, large], 'Official Canadian waffle-fry portions before adding the sandwich or drink', ('cal', 'p', 'f', 'na')) + '''
<p>Small to medium adds 29 g of fries and 100 kcal. Medium to large adds 54 g and 180 kcal. The size names do not describe equal increments, so do not infer a missing portion simply by averaging two labels.</p><p>From small to large, the listed order gains 280 kcal, 3 g protein, 30 g carbohydrate and 16 g fat. Fibre rises by 3 g and sodium by 150 mg. These changes belong to the larger fry portion; it is the same main and drink throughout.</p>''' + compare([fries, medium], 'Compare small and medium Canadian fries directly') + '''
<h2>Log what you ate, once</h2><p>Choose Canada first, then the matching fry size. Log the sandwich, fries and tea separately, or use the composed small-fries order once. Do not log a complete order and add its components again.</p><p>If you finish the sandwich but eat half the fries, adjust only that side. Half a small source serving is a calculated 48 g reference and 160 kcal, not a claim that your actual leftovers were weighed. Use an actual food weight when you have one, or keep the portion estimate visible.</p>
<h2>Keep the rest of the order fixed</h2><p>A change to the main is another order: the Canadian Grilled Chicken Club, cheese variants and breaded sandwich have their own values. A different drink is not calorie-free because this tea is. The tea’s source weight is preserved as 451 g rather than relabeled as a guessed millilitre size.</p><p>These totals are GetMacros arithmetic from Canadian component portions, not a restaurant-published combo or a price offer. No sauce packet, unlisted extra or U.S. nutrient value is included. Add an exact supported sauce or drink record if you order one; if its information is missing, the expanded order total is partial rather than complete.</p><p><a href="/ca/en/restaurants/chick-fil-a/">See Canadian Chick-fil-A portions</a> · <a href="/food-diary.html?market=CA">Log your order</a> · <a href="/compare-complete-restaurant-orders.html?market=CA">Build another complete order</a></p>''' + sources(urls, 'Canadian official serving information read on 18 October 2026; no source edition date is stated. Calculated totals: 380 + 320 + 0 = 700 kcal; 380 + 420 + 0 = 800 kcal; 380 + 600 + 0 = 980 kcal. All nutrient totals retain unknowns if a component is missing; the zero-calorie tea values in this source are explicitly reported.')
    result.append(article('chick-fil-a-canada-grilled-sandwich-fries-sizes.html', 'Chick-fil-A Canada: small, medium or large fries with a grilled sandwich', 'Compare three exact Canadian orders: grilled sandwich, small unsweet tea and 96 g, 125 g or 179 g waffle fries.', 'CA', body, rows, urls, 'Choose a Canadian fry portion, see the whole order total, and avoid equal-size-step assumptions.', 'Existing Chick-fil-A guide and cross-chain chicken comparison are U.S.-focused. The New York Fries worked example concerns another chain; no current Canadian Chick-fil-A size-specific order comparison was found.', 'Chick-fil-A Canada waffle fries small medium calories chicken sandwich nutrition'))
    return result


ARTICLES = build_articles()


def export():
    OUT.mkdir(parents=True, exist_ok=True)
    evidence = dict(preparedAt=DATE, articleCount=len(ARTICLES), newArticles=len(ARTICLES), improvedExistingPages=0, publicPagesWritten=0, publication='Not performed by this module; release integrator owns publication', articles=ARTICLES, records=EVIDENCE)
    (OUT / 'articles.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for article in ARTICLES:
        # Review fragments are documentation only and cannot be confused with published pages.
        (OUT / (article['route'] + '.fragment.txt')).write_text(article['body'] + '\n', encoding='utf-8')
    report = dict(checkedAt=DATE, articles=len(ARTICLES), distinctRoutes=len({r['route'] for r in ARTICLES}), sourceRecords=len(EVIDENCE), checks=['Exact country/chain/name uniqueness', 'Official reviewed source status', 'Decimal component sums for all Canadian order fields', 'No missing values converted to zero', 'All original UK salt values retained', 'UK plate arithmetic and prose differences', 'No automatic publication dates'], wordCounts={r['route']: len(re.sub('<[^>]+>', ' ', r['body']).split()) for r in ARTICLES})
    assert report['distinctRoutes'] == len(ARTICLES)
    assert sum_rows('missing', [dict(market='GB', serving='1', cal=None), dict(market='GB', serving='1', cal=0)])['cal'] is None
    lookup = {(r['market'], r['chain'], r['name']): r for r in EVIDENCE.values()}
    quarter = lookup['GB', 'Nando’s', '1/4 Chicken']
    for side, cal, protein in [('Spicy Rice · Regular', 535, 43.1), ('PERi-Salted Chips · Regular', 787, 44), ('Corn on the Cob · Regular', 431, 42.8)]:
        plate = sum_rows('check', [quarter, lookup['GB', 'Nando’s', side]])
        assert plate['cal'] == cal and plate['p'] == protein
    for r in EVIDENCE.values():
        if r['market'] == 'GB':
            assert Decimal(str(r['nativeNutrients']['salt'])) * 400 == Decimal(str(r['na']))
    assert Decimal(str(lookup['GB', 'LEON', 'Sausage & Egg Muffin']['cal'])) - Decimal(str(lookup['GB', 'LEON', 'Smoked Salmon & Avocado Egg Pot']['cal'])) == 243
    assert lookup['GB', 'Wendy’s', 'Classic Sausage & Cheese Muffin']['cal'] - lookup['GB', 'Wendy’s', 'Classic Egg & Cheese Muffin']['cal'] == 158
    (OUT / 'editorial-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return ARTICLES


if __name__ == '__main__':
    export()
