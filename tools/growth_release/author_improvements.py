"""Prepare reviewed additions to existing pages; never rewrite root pages.

This workstream deliberately does not reconstruct the unavailable content ZIP.
The release integrator consumes editorial-improvements.json separately.
"""
from __future__ import annotations
from pathlib import Path
import sys, json, re, html
from html.parser import HTMLParser
from urllib.parse import urlencode, parse_qs, urlparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from build_restaurant_pages import parse_meals
from meal_provenance import read as read_provenance

OUT = ROOT / 'docs/growth-release-2026-10-09/editorial'
TARGETS = [
 'arbys-nutrition-guide.html', 'sonic-nutrition-guide.html',
 'qdoba-nutrition-guide.html', 'el-pollo-loco-nutrition-guide.html',
 'del-taco-nutrition-guide.html', 'noodles-and-company-nutrition-guide.html',
 'culvers-nutrition-guide.html', 'taco-johns-nutrition-guide.html',
 'in-n-out-nutrition-guide.html', 'raising-canes-nutrition-guide.html',
 'high-protein-fast-food-under-500-calories.html',
 'fast-food-breakfast-protein-comparison.html',
 'restaurant-bowl-nutrition-comparison.html',
 'fast-food-fiber-and-protein.html', 'fast-food-protein-and-sodium.html',
 'protein-density-fast-food.html', 'grilled-and-blackened-chicken-comparison.html',
 'vegetarian-fast-food-protein-comparison.html',
 'how-to-hit-protein-goal-on-budget.html', 'healthy-fast-food.html',
]

class MainReader(HTMLParser):
    def __init__(self):
        super().__init__(); self.in_main = False; self.skip = 0
        self.copy = []; self.rows = []; self.row = None; self.cell = None
    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.in_main = True
        if not self.in_main: return
        if tag in ('script','style','svg'): self.skip += 1
        if tag == 'tr': self.row = []
        if tag in ('td','th') and self.row is not None: self.cell = []
        if tag in ('p','h1','h2','h3','li','summary','caption'): self.copy.append('\n')
    def handle_endtag(self, tag):
        if tag == 'main': self.in_main = False
        if tag in ('script','style','svg') and self.skip: self.skip -= 1
        if tag in ('td','th') and self.row is not None:
            self.row.append(' '.join(''.join(self.cell or []).split())); self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None
        if tag in ('p','h1','h2','h3','li','summary','caption'): self.copy.append('\n')
    def handle_data(self, value):
        if not self.in_main or self.skip: return
        if self.cell is not None: self.cell.append(value)
        elif self.row is None: self.copy.append(value)

def audit_existing():
    OUT.mkdir(parents=True, exist_ok=True)
    meals = parse_meals(); proof = read_provenance(ROOT/'js/meal-provenance.js')
    by_key = {m['chain']+'||'+m['name']:{**m,**proof.get(m['chain']+'||'+m['name'],{})} for m in meals}
    (OUT/'baseline-records.json').write_text(json.dumps(by_key,ensure_ascii=False,indent=2),encoding='utf-8')
    audit = []
    for route in TARGETS:
        source = (ROOT/route).read_text(encoding='utf-8')
        parser = MainReader(); parser.feed(source)
        text = '\n'.join(line.strip() for line in ''.join(parser.copy).splitlines() if line.strip())
        (OUT/(route+'.txt')).write_text(text+'\n\nTABLES (all cells)\n'+json.dumps(parser.rows,ensure_ascii=False,indent=2),encoding='utf-8')
        audit.append({'route':route,'copy':text,'tableRows':parser.rows,'tableRowCount':len(parser.rows)})
    (OUT/'existing-body-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Extracted complete main copy and every table cell for {len(audit)} existing routes; {len(by_key)} unchanged records.')

def key(chain, name): return chain+'||'+name

# Original analysis of existing records, not drafts recreated from a missing ZIP.
# Field assertions intentionally stop a rebuild if a reviewed value has changed.
DECISIONS = [
 dict(route=TARGETS[0], heading='Crispy Chicken or Buffalo Chicken: check sodium',
 keys=[key('Arby’s','Crispy Chicken'), key('Arby’s','Buffalo Chicken')], fields=['cal','p','na'],
 paragraphs=[
 'These two named sandwiches each list 530 calories and 24 g protein, but they are not interchangeable on sodium: Crispy Chicken has 1,410 mg and Buffalo Chicken has 2,100 mg. That is a 690 mg difference even though the headline calorie and protein numbers match.',
 'If you are choosing between these flavors, compare the standard sandwiches first. The table does not isolate the nutrition of a buffalo-sauce portion, because the complete builds and serving weights differ. It cannot tell you what an unlisted sauce substitution would do.',
 'Both rows exclude extra sides, sauce packets and drinks. Their source is the U.S. document effective June 2026, retained from the October 4 inspection. Check your local recipe before reusing the figures.'],
 overlap='The existing guide compares its lowest-calorie and highest-protein recorded options; it never analyzes the two same-calorie chicken sandwiches.',
 contribution='Adds a flavor decision where calorie/protein equality conceals 690 mg sodium; distinguishes whole-build evidence from an invented sauce subtraction.',
 assertions=[['A.cal',530],['B.cal',530],['A.p',24],['B.p',24],['B.na-A.na',690]]),
 dict(route=TARGETS[1], heading='Three tenders or a crispy-chicken wrap?',
 keys=[key('SONIC','Crispy Tenders (3 Pc.)'), key('SONIC','Cheesy Baja Crispy Tender Wrap')], fields=['cal','p','c','na'],
 paragraphs=[
 'The three-piece tenders have 21 g protein in 260 calories. The Cheesy Baja wrap has 12 g protein in 290 calories. Here, choosing a wrap does not add protein simply because it sounds like a more complete package: it is a different recipe and chicken portion.',
 'Choose the format you want to eat, then include your extras. The tenders row does not include a dipping sauce; the wrap row describes its named build. You cannot turn the wrap into a tender count by subtracting an assumed tortilla value.',
 'The recorded sodium totals are 730 mg and 810 mg. These U.S. brochure entries were inspected October 4; the file name and printed season do not establish one precise menu date. Drinks, sides and later local changes remain separate.'],
 overlap='The guide gives the complete table and a corn-dog/double-burger contrast, but does not help someone decide between two chicken formats.',
 contribution='Adds a practical 3-piece portion-versus-wrap choice with carbohydrate and sodium context and no guessed customization.',
 assertions=[['A.cal',260],['B.cal',290],['A.p-B.p',9],['B.na-A.na',80]]),
 dict(route=TARGETS[2], heading='Chicken or steak in the named Keto Bowl?',
 keys=[key('QDOBA','Keto Bowl - Chicken'), key('QDOBA','Keto Bowl - Steak')], fields=['cal','p','fat','na'],
 paragraphs=[
 'Both published Keto Bowl portions are 340 g. The chicken version lists 400 calories and 33 g protein; the steak version lists 490 calories and 25 g protein. Similar serving weight makes this a useful menu choice, but it does not prove that every other ingredient is identical.',
 'Their sodium difference goes the other way: steak is 940 mg, compared with chicken at 990 mg. Decide which difference matters to your own order rather than letting a product name choose for you. “Keto” here is QDOBA’s menu wording, not a recommendation or a GetMacros diet assessment.',
 'These are whole named U.S. builds from the document inspected October 4. Rice, toppings or sauce changes need their own supported calculation. Compare the rows below before changing the standard recipe.'],
 overlap='The guide contrasts Brisket Birria with a large Double Protein Steak Bowl and warns about named builds, but never compares the two equal-weight Keto Bowl entries.',
 contribution='Adds a same-published-weight chicken/steak decision, including the inverse calorie/protein versus sodium trade-off without a health rating.',
 assertions=[['A.cal',400],['B.cal',490],['A.p-B.p',8],['A.na-B.na',50]]),
 dict(route=TARGETS[3], heading='Two chicken quesadillas with the same protein',
 keys=[key('El Pollo Loco','Salsa Verde Chicken Quesadilla'), key('El Pollo Loco','Chipotle Chicken Quesadilla')], fields=['cal','p','fat','na'],
 paragraphs=[
 'The Salsa Verde and Chipotle Chicken Quesadillas each use a published 11.6 oz serving and each contain 51 g protein. Their other totals differ: Salsa Verde is 810 calories and 44 g fat; Chipotle is 930 calories and 57 g fat.',
 'For this specific choice, the extra 120 calories do not bring extra protein. The sodium difference is 150 mg, with Salsa Verde at 1,570 mg and Chipotle at 1,720 mg. That is an observation about these two finished recipes, not a general rule about salsa flavors or a measurement of a sauce add-on.',
 'Keep chips and drinks outside this comparison until you add their actual portions. The figures come from the September 2026 U.S. guide inspected October 4; the recipe you order locally may later change.'],
 overlap='The existing guide explains excluded salad dressings and chicken-meal sides; its preview compares a taco with a large double-chicken bowl.',
 contribution='Adds a matched-published-size quesadilla comparison with equal protein and explicit calorie/fat/sodium deltas.',
 assertions=[['A.p',51],['B.p',51],['B.cal-A.cal',120],['B.fat-A.fat',13],['B.na-A.na',150]]),
 dict(route=TARGETS[4], heading='Original, Ranch or Chipotle Chicken Cheddar Roller?',
 keys=[key('Del Taco','Chicken Cheddar Roller (Original)'),key('Del Taco','Chicken Cheddar Roller (Ranch)'),key('Del Taco','Chicken Cheddar Roller (Chipotle)')], fields=['cal','p','fat','na'],
 paragraphs=[
 'All three recorded Chicken Cheddar Rollers contain 13 g protein. The Original lists 250 calories, Ranch 270 and Chipotle 280. If you are deciding by protein, their different flavor names do not change that total.',
 'The Original has less recorded fat, at 9 g rather than 12 g, but slightly more sodium: 750 mg versus 730 mg for each flavored version. None wins every column. The Original portion is 118 g; Ranch and Chipotle are 111 g each, so these are the listed products rather than an equal-weight ingredient experiment.',
 'One roller means one roller, not a meal with fries. Keep your actual count and extras visible. These figures use Del Taco’s February 2026 U.S. table, inspected October 4, and do not establish current prices or local availability.'],
 overlap='The guide contains the roller rows without a flavor decision; its highlighted comparison is a single street taco against a large burrito.',
 contribution='Adds a compact three-flavor choice with equal protein, portion weights and the reverse sodium relationship.',
 assertions=[['A.p',13],['B.p',13],['C.p',13],['B.cal-A.cal',20],['C.cal-A.cal',30],['A.na-B.na',20]]),
 dict(route=TARGETS[5], heading='Two regular chicken pastas: compare fiber, too',
 keys=[key('Noodles & Company','Rigatoni Rosa with Parmesan Chicken, regular'),key('Noodles & Company','Chicken Parmesan, regular')], fields=['cal','p','f','na'],
 paragraphs=[
 'The regular Rigatoni Rosa with Parmesan Chicken lists 45 g protein and 13 g fiber in 890 calories. The regular Chicken Parmesan lists 51 g protein and 8 g fiber in 940 calories. The extra 6 g protein therefore comes with 50 more calories and 5 g less fiber in these finished dishes.',
 'Sodium is 1,640 mg for Rigatoni Rosa and 1,840 mg for Chicken Parmesan. Start with the dish you want, then check the limits that matter to you; a protein-only ranking leaves out that difference.',
 'The named chicken is already included. Do not add an extra chicken entry unless that is an additional portion you actually order. Both rows use the regular column in the official document inspected October 4, not small or Duos values.'],
 overlap='The guide contrasts soup with Buffalo Chicken Ranch Mac and explains REG versus SM; it does not compare these two chicken-containing pastas.',
 contribution='Adds a realistic regular pasta decision that balances protein/fiber/sodium and prevents double-counting the named chicken.',
 assertions=[['B.p-A.p',6],['B.cal-A.cal',50],['A.f-B.f',5],['B.na-A.na',200]]),
 dict(route=TARGETS[6], heading='Single Cheese or Single Deluxe?',
 keys=[key('Culver’s','ButterBurger® Cheese, Single'),key('Culver’s',"The Culver's® Deluxe, Single")], fields=['cal','p','fat','na'],
 paragraphs=[
 'The single ButterBurger Cheese and single Deluxe each list 24 g protein in this source edition. Deluxe has 580 calories, compared with 460 for Cheese. Choosing the more elaborate named recipe adds 120 calories here without adding protein.',
 'Fat rises from 23 g to 34 g and sodium from 700 mg to 920 mg. Those differences belong to the complete standard burgers. They are not nutrition quotes for removing mayonnaise, lettuce or another individual ingredient; use a supported custom build for that narrower question.',
 'Both are single-patty adult-menu entries, with fries and drinks excluded. The dataset uses the July 2025 official guide retrieved October 4, 2026. Its later retrieval does not make the recipe edition current, so confirm later changes with Culver’s before ordering.'],
 overlap='The guide contains both burger rows but currently spotlights cod dinner versus Buffalo tenders; dinner inclusion notes do not answer this burger choice.',
 contribution='Adds an adult-menu single-patty comparison, exposing equal protein across two different standard burger recipes and retaining the older edition limit.',
 assertions=[['A.p',24],['B.p',24],['B.cal-A.cal',120],['B.fat-A.fat',11],['B.na-A.na',220]]),
 dict(route=TARGETS[7], heading='Fiesta Rice Bowl or Boss Bowl with chicken?',
 keys=[key('Taco John’s','Fiesta Rice Bowl, Chicken'),key('Taco John’s','Boss Bowl, Chicken')], fields=['cal','p','f','na'],
 paragraphs=[
 'These two chicken bowls are close in the recorded numbers: each has 38 g protein and 9 g fiber. The Fiesta Rice Bowl lists 630 calories and 1,760 mg sodium; the Boss Bowl lists 650 calories and 1,730 mg sodium.',
 'That 20-calorie difference is small next to the fact that you are choosing different named recipes. There is no numerical reason here to assume Boss means more protein. The 30 mg sodium difference also does not establish that the bowls taste the same or use equal ingredient portions.',
 'Pick the recipe you want and preserve its full published name in your notes. Extra Potato Olés, sauces and a drink are separate. These U.S. rows were inspected October 4; the printed source did not establish an exact edition date or current local availability.'],
 overlap='The original guide previews a bean taco and a chipotle-shredded-chicken Fiesta Bowl and lists the large menu; no direct standard-chicken bowl analysis exists.',
 contribution='Adds a near-equal macro comparison between two practical chicken bowls instead of ranking a taco against a bowl.',
 assertions=[['A.p',38],['B.p',38],['A.f',9],['B.f',9],['B.cal-A.cal',20],['A.na-B.na',30]]),
 dict(route=TARGETS[8], heading='Two different ways to order a Double-Double',
 keys=[key('In-N-Out','Double-Double with onion, mustard and ketchup instead of spread'),key('In-N-Out','Double-Double with onion, Protein Style (lettuce instead of bun)')], fields=['cal','p','c','fat'],
 paragraphs=[
 'Mustard and ketchup instead of spread and Protein Style are different published changes. The first version keeps a bun and lists 550 calories, 34 g protein and 41 g carbohydrate. The lettuce-wrap version lists 460 calories, 30 g protein and 12 g carbohydrate.',
 'Protein Style is the menu’s name for replacing the bun, not a claim that it contains more protein. The recorded amount is 4 g lower here. Its fat total is also higher than the mustard-and-ketchup version, at 32 g versus 27 g, so the alternatives are not one simple ranking.',
 'Use the exact version you will order. Neither row combines both modifications. Fries, drinks and extra spread packets are excluded. These numbers use the linked January 2026 U.S. PDF retained from October 4, rather than mixing PDF and HTML-page values.'],
 overlap='The guide names the alternative builds but compares a lettuce-wrap hamburger with a standard Double-Double; it never contrasts these two Double-Double alternatives.',
 contribution='Clarifies that two supported modifications are different builds, debunks an intuitive but unsupported higher-protein interpretation of Protein Style, and preserves source consistency.',
 assertions=[['A.cal-B.cal',90],['A.p-B.p',4],['A.c-B.c',29],['B.fat-A.fat',5]]),
 dict(route=TARGETS[9], heading='The extras around three chicken fingers',
 keys=[key('Raising Cane’s','3 fingers with Texas Toast and coleslaw (individual portions)'),key('Raising Cane’s','3 fingers with fries, sauce and Texas Toast (individual portions)')], fields=['cal','p','fat','f','na'],
 paragraphs=[
 'Both calculated orders use three individual chicken fingers and one Texas Toast. One adds coleslaw; the other adds fries and sauce. Their recorded totals are 630 and 1,150 calories, despite having the same chicken-finger count.',
 'The fries-and-sauce build adds 520 calories, 4 g protein and 580 mg sodium compared with the coleslaw build. That is a comparison of two explicitly assembled orders, not a promise that the restaurant’s named combos have these totals. The source’s published combo rows and individual-portion sums do not reconcile.',
 'Exact fiber remains unknown in both assembled orders because a component is listed below 1 g. No drink is counted. This section uses the existing August 2026 source snapshot inspected October 4; a fresh October 9 PDF retrieval was unsuccessful, so availability and later recipe changes remain unverified.'],
 overlap='The guide compares the coleslaw build with the sandwich and states combo limitations, but does not quantify what changes between its two three-finger assemblies.',
 contribution='Adds a complete-order contrast where finger count is held fixed, using only the two existing calculated builds and preserving unknown fiber.',
 assertions=[['B.cal-A.cal',520],['B.p-A.p',4],['B.na-A.na',580],['A.f',None],['B.f',None]]),
 dict(route=TARGETS[10], heading='Three more named entrées below the same limit',
 keys=[key('QDOBA','Keto Bowl - Chicken'),key('Culver’s','Grilled Chicken Sandwich'),key('El Pollo Loco','Classic Chicken Burrito')], fields=['cal','p','f','na'],
 paragraphs=[
 'The wider dataset also records QDOBA’s Keto Bowl - Chicken, Culver’s Grilled Chicken Sandwich and El Pollo Loco’s Classic Chicken Burrito below 500 calories with at least 25 g protein. These are a named bowl, sandwich and burrito, rather than three bare chicken portions.',
 'At 480 calories each, the Culver’s sandwich and El Pollo Loco burrito still differ: 36 g versus 25 g protein, and 2 g versus 5 g fiber. QDOBA’s bowl has 33 g protein at 400 calories. Matching a calorie limit is the start of the comparison; it does not make their recipes equivalent.',
 'Each row keeps its own U.S. serving and source edition. Extra food and drinks are excluded, and the Culver’s July 2025 guide is older than the other documents. Use the exact-order comparison to keep those boundaries visible.'],
 overlap='The existing shortlist uses the earlier source-inspected collection and omits these three additional-chain records.',
 contribution='Expands an important existing collection with three genuinely different documented entrée formats and same-calorie protein/fiber analysis, not a new keyword-variant page.',
 assertions=[['A.cal',400],['A.p',33],['B.cal',480],['C.cal',480],['B.p-C.p',11],['C.f-B.f',3]]),
 dict(route=TARGETS[11], heading='Two breakfast burritos with 25 g protein',
 keys=[key('SONIC','Breakfast Burrito Bacon'),key('Del Taco','Breakfast Burrito (Carne Asada Steak, Egg & Cheese)')], fields=['cal','p','c','na'],
 paragraphs=[
 'SONIC’s Bacon Breakfast Burrito and Del Taco’s Carne Asada Steak, Egg & Cheese Breakfast Burrito each list 25 g protein. Their recorded calories are 470 and 450, so the protein headline is similar even though the recipes differ.',
 'Sodium is 1,540 mg for the SONIC burrito and 1,290 mg for Del Taco’s. The 250 mg difference does not come from an isolated bacon-to-steak substitution: these are two restaurants’ whole products, with different serving definitions and ingredients. Del Taco specifies a 237 g portion; SONIC’s row identifies one listed burrito without a gram weight.',
 'Coffee, juice, hash browns and extra sauce are outside this food-only comparison. The rows were inspected October 4 from different U.S. documents. Confirm breakfast availability and the exact local recipe before using them as an ordering quote.'],
 overlap='The original four-food breakfast comparison covers Chick-fil-A and Starbucks; it has no burrito pair or explicit no-gram-weight contrast.',
 contribution='Adds a concise breakfast format comparison across two documented chains with equal protein and explicit portion/region limits.',
 assertions=[['A.p',25],['B.p',25],['A.cal-B.cal',20],['A.na-B.na',250]]),
 dict(route=TARGETS[12], heading='At QDOBA, two chicken bowls tell different stories',
 keys=[key('QDOBA','Keto Bowl - Chicken'),key('QDOBA','Cholula® Hot & Sweet Chicken Bowl')], fields=['cal','p','f','na'],
 paragraphs=[
 'A larger named bowl does not necessarily contain more protein. QDOBA’s 340 g Keto Bowl - Chicken has 33 g protein; the 418 g Cholula Hot & Sweet Chicken Bowl has 31 g. The Cholula build also has more recorded calories, at 610 rather than 400.',
 'Fiber moves in the opposite direction to protein: 15 g in the Cholula bowl versus 7 g in the Keto Chicken bowl. Sodium is 1,500 mg versus 990 mg. If fiber is your priority, that may change which comparison you want to make; neither product is a universal winner.',
 'These are published U.S. named builds from the QDOBA document inspected October 4. We have not treated one as the other with a sauce added. A custom rice, bean or topping change needs its own supported values.'],
 overlap='The existing bowl reference covers Chipotle, CAVA and Sweetgreen, with no QDOBA entries or this larger-serving/lower-protein pattern.',
 contribution='Extends the existing bowl reference with a new two-build decision and explicit protein/fiber/size trade-off.',
 assertions=[['B.cal-A.cal',210],['A.p-B.p',2],['B.f-A.f',8],['B.na-A.na',510]]),
 dict(route=TARGETS[13], heading='More fiber can still miss your protein filter',
 keys=[key('Del Taco','Bean & Cheese Burrito (Green)'),key('QDOBA','Fajita Vegan Bowl')], fields=['cal','p','f','na'],
 paragraphs=[
 'Del Taco’s Green Bean & Cheese Burrito records 24 g protein and 15 g fiber. QDOBA’s Fajita Vegan Bowl has more fiber, at 22 g, but less protein, at 17 g. A “most fiber” sort and a “20 g protein minimum” filter answer different questions.',
 'Under this page’s 20 g protein and 7 g fiber collection rule, the burrito qualifies and the bowl does not. That does not make the bowl a poor choice; it means you asked the tool for two simultaneous conditions. Lowering your chosen protein minimum is different from guessing an unrecorded add-on.',
 'Compare the listed portions, 280 g and 482 g, rather than interpreting the gap as one ingredient’s effect. These U.S. source rows were inspected October 4. Product names do not provide allergy assurances, and prices and extra items are not included.'],
 overlap='The original collection defines two cutoffs and discusses beans but never shows a high-fiber order that fails the protein condition beside a qualifying order.',
 contribution='Adds a real edge case explaining two simultaneous nutrient filters with supported records, without moral labels or invented substitutions.',
 assertions=[['A.p',24],['A.f',15],['B.p',17],['B.f',22],['B.f-A.f',7]]),
 dict(route=TARGETS[14], heading='Soup is not automatically the lower-sodium choice',
 keys=[key('Noodles & Company','Chicken Noodle Soup, regular'),key('Culver’s','Beef Pot Roast Sandwich')], fields=['cal','p','f','na'],
 paragraphs=[
 'The regular Noodles Chicken Noodle Soup records 30 g protein and 2,320 mg sodium. Culver’s Beef Pot Roast Sandwich records 31 g protein and 740 mg sodium. Their protein totals are close, but the sodium totals differ by 1,580 mg.',
 'This does not establish a rule about soups or sandwiches generally. It gives you two specific recorded choices, with 360 and 410 calories respectively. A broth-based description alone would not reveal the sodium difference; you need the exact item and serving.',
 'The soup is the regular dish, not the smaller side. The sandwich excludes sides and a drink. Both are U.S. records inspected October 4, with Culver’s figures retained from its July 2025 edition. For a medically prescribed limit, use advice from your clinician and confirm the current restaurant information.'],
 overlap='The existing comparison contains neither the Noodles soup nor the Culver’s pot-roast sandwich; it otherwise focuses on chicken portions and bowls.',
 contribution='Adds a practical equal-protein comparison that defeats an unreliable soup-format sodium assumption while keeping medical boundaries and editions explicit.',
 assertions=[['A.p',30],['B.p',31],['A.na-B.na',1580],['B.cal-A.cal',50]]),
 dict(route=TARGETS[15], heading='Use the ratio after choosing your serving',
 keys=[key('Arby’s','Classic Roast Beef'),key('Arby’s','Ham & Swiss Melt')], fields=['cal','p','na','density'],
 paragraphs=[
 'Arby’s Classic Roast Beef gives 23 g protein in 360 calories, or 6.4 g per 100 calories when rounded. The Ham & Swiss Melt gives 26 g in 380 calories, or 6.8 g per 100 calories. This is a close ratio comparison, not the wide gap between a bare chicken portion and a complete bowl.',
 'If your own minimum is 25 g protein, only the melt passes it at these listed portions. If you are also comparing sodium, the roast-beef sandwich is lower: 970 mg versus 1,370 mg. A slightly higher protein ratio does not cancel that other difference.',
 'The ratio uses the whole order’s published totals, not meat weight. These individual U.S. sandwiches exclude extras and use the June 2026 effective document inspected October 4. No local price is assumed.'],
 overlap='The existing reference explains ratios with high-density chicken portions; it has no close everyday-sandwich pair or concrete 25 g cutoff application.',
 contribution='Adds a low-gap density example with independent protein and sodium constraints instead of extending a top-ratio ranking.',
 assertions=[['A.p',23],['A.cal',360],['B.p',26],['B.cal',380],['B.na-A.na',400]]),
 dict(route=TARGETS[16], heading='Compare a chicken sandwich with another sandwich',
 keys=[key('Culver’s','Grilled Chicken Sandwich'),key('Culver’s','Crispy Chicken Sandwich')], fields=['cal','p','fat','na'],
 paragraphs=[
 'To choose a sandwich, use sandwich totals rather than comparing it with a bare nugget or tender portion. In the retained Culver’s guide, Grilled Chicken Sandwich lists 480 calories and 36 g protein; Crispy Chicken Sandwich lists 690 calories and 28 g protein.',
 'The crispy build therefore has 210 more calories but 8 g less protein at its standard serving. Fat is 35 g versus 19 g, and sodium 1,590 mg versus 1,340 mg. These whole-product differences cannot be attributed exclusively to cooking method: the records do not measure a controlled identical-chicken experiment.',
 'Both figures exclude an added side or drink. They come from the July 2025 U.S. edition retrieved October 4, 2026, so confirm later recipe changes. Compare the full order once you choose the extras you actually want.'],
 overlap='The existing article compares five chicken-only portions and warns about extras; it has no within-chain standard sandwich comparison.',
 contribution='Adds the matching sandwich-format decision and explicitly prevents a causal preparation claim from non-controlled menu data.',
 assertions=[['B.cal-A.cal',210],['A.p-B.p',8],['B.fat-A.fat',16],['B.na-A.na',250]]),
 dict(route=TARGETS[17], heading='A vegan bowl name and a veggie burger name',
 keys=[key('QDOBA','Fajita Vegan Bowl'),key('Culver’s','Harvest Veggie Burger')], fields=['cal','p','f','na'],
 paragraphs=[
 'The official menu names also include QDOBA’s Fajita Vegan Bowl and Culver’s Harvest Veggie Burger. Their recorded protein totals are 17 g and 19 g respectively. The bowl has 22 g fiber at 530 calories; the burger has 5 g at 610 calories. Those are two different complete products, not equivalent servings of vegetables.',
 'These additional records do not yet have dietary classifications assigned in GetMacros. The exact-order link can compare their nutrition, but they are not automatically included as verified matches by the site’s meat-free or plant-based filter. A menu name alone cannot fill that missing classification.',
 'Check current ingredients and preparation with the restaurant for your own restrictions. The U.S. source snapshots were inspected October 4; Culver’s uses an older July 2025 edition. Extra sides, sauces and drinks remain separate.'],
 overlap='The original article covers previously classified meat-free builds but does not explain the additional unclassified menu-named records or why they may be absent from its filter.',
 contribution='Adds a supported bowl/burger comparison and explains a real classification gap without inventing diet or allergen safety.',
 assertions=[['A.p',17],['B.p',19],['A.f-B.f',17],['B.cal-A.cal',80]]),
 dict(route=TARGETS[18], heading='Take a restaurant comparison to your receipt',
 keys=[key('Arby’s','Classic Roast Beef'),key('Arby’s','Ham & Swiss Melt')], fields=['cal','p','na'],
 paragraphs=[
 'For a restaurant order, use the amount you actually paid and the protein in that exact item. Arby’s Classic Roast Beef records 23 g protein; its Ham & Swiss Melt records 26 g. The melt can cost about 13% more before its cost per gram exceeds the roast-beef sandwich’s: 26 ÷ 23 is about 1.13.',
 'For arithmetic only, if the first sandwich cost 10 currency units, the equal-value price for the melt would be about 11.30 units. These are invented prices to show the break-even method, not menu-price claims. Enter your receipt, quantity and currency in the protein-value tool instead of using those example amounts.',
 'Protein value still does not rank taste, fiber or sodium. The sandwich nutrient records use the U.S. June 2026 effective source inspected October 4; sides, drinks and extra sauce are excluded. Keep fees consistent between the two prices.'],
 overlap='The existing guide explains package-price arithmetic and shopping staples, but has no exact restaurant item break-even worked comparison.',
 contribution='Adds a practical receipt-based restaurant protein-value decision with actual nutrient inputs and explicitly invented price units.',
 assertions=[['A.p',23],['B.p',26],['B.p/A.p',26/23]]),
 dict(route=TARGETS[19], heading='Count the food, not just the menu row',
 keys=[key('Del Taco','Grilled Chicken Street Taco'),key('El Pollo Loco','Classic Chicken Burrito')], fields=['cal','p','c','na'],
 paragraphs=[
 'A single Del Taco Grilled Chicken Street Taco records 110 calories and 9 g protein. If you actually order three identical listed portions, the calculated amount is 330 calories and 27 g protein. That is your three-taco calculation, not a newly published restaurant combo.',
 'Compare it with the food you would otherwise buy: El Pollo Loco’s Classic Chicken Burrito records 480 calories and 25 g protein at its 10.4 oz portion. The lower-calorie taco row does not by itself tell you which full order you want. Count comes before sorting.',
 'These U.S. records retain the February and September 2026 source editions inspected October 4. A drink, dipping sauce or side needs another supported portion. Use the exact records below, then change quantities in the order builder; missing component values must remain unknown.'],
 overlap='The hub includes a single-taco low-calorie list and says extras are separate, but has no worked count comparison; its restaurant directory also omits ten existing chains.',
 contribution='Adds an actual three-portion arithmetic example plus a current-data 25-chain directory reconciliation instruction, improving scope and ordering usefulness.',
 assertions=[['A.cal*3',330],['A.p*3',27],['A.c*3',39],['A.na*3',900],['B.cal',480],['B.p',25]])
]

CURRENT_SOURCE_REVIEW = {
 'Arby’s': {'method':'Official PDF extracted rows inspected with web.open/find; chicken sandwich, roast beef and melt rows matched the retained dataset.','sourceEdition':'Effective June 2026; filename July 2026.'},
 'SONIC': {'method':'Official PDF extracted page 4 rows inspected with web.open/find; tender, wrap and breakfast-burrito values matched the retained dataset.','sourceEdition':'Filename September 2026; printed season ambiguity retained.'},
 'QDOBA': {'method':'Official PDF extracted rows inspected with web.open/find; Keto Chicken/Steak, Cholula and Fajita Vegan rows matched the retained dataset.','sourceEdition':'Printed Nutrition Facts 2026; filename September 1, 2026.'},
 'El Pollo Loco': {'method':'Official PDF extracted rows inspected with web.open/find; both quesadillas and Classic Chicken Burrito matched the retained dataset.','sourceEdition':'Retained September 2026 edition.'},
 'Del Taco': {'method':'Official PDF extracted rows inspected with web.open/find; roller flavors, bean-and-cheese, taco and breakfast-burrito values matched the retained dataset.','sourceEdition':'Printed February 2026.'},
 'Noodles & Company': {'method':'Official PDF extracted regular-column rows inspected with web.open; pasta and regular soup values matched the retained dataset.','sourceEdition':'Printed NTR.0126, exact formal publication date remains unstated in stored metadata.'},
 'Culver’s': {'method':'Official PDF extracted adult-menu rows inspected with web.open; burger, sandwich and veggie-burger rows matched the retained dataset. Adult menu is kept separate from differing kids à-la-carte values.','sourceEdition':'Retained July 2025 edition; not represented as a newly issued 2026 menu.'},
 'Taco John’s': {'method':'Official PDF extracted bowl rows inspected with web.open/find; the two standard chicken bowls matched the retained dataset.','sourceEdition':'Exact printed edition date remains unstated.'},
 'In-N-Out': {'method':'Official linked PDF extracted rows and printed January 2026 date inspected with web.open/find; Double-Double versions matched the retained dataset.','sourceEdition':'Printed January 2026.'},
 'Raising Cane’s': {'method':'Fresh official-PDF web retrieval returned an internal error. Existing inspected snapshot only; no fresh source verification claimed.','sourceEdition':'Retained August 2026 edition.'},
}

def fmt(v): return 'Not verified' if v is None else f'{v:,.1f}'.rstrip('0').rstrip('.') if isinstance(v,float) else f'{v:,}'

def numeric_table(records, fields):
    labels={'cal':'Calories (kcal)','p':'Protein (g)','c':'Carbs (g)','fat':'Fat (g)','f':'Fiber (g)','na':'Sodium (mg)','density':'Protein per 100 kcal (g)'}
    rows=[]
    for r in records:
        name=html.escape(r['chain']+' · '+r['name'])
        portion=html.escape(r['serving'])
        vals=[]
        for f in fields:
            v=round(r['p']/r['cal']*100,1) if f=='density' else r.get(f)
            vals.append('<td>'+fmt(v)+'</td>')
        rows.append('<tr><th scope="row">'+name+'<p class="table-portion">'+portion+' · '+html.escape(r['region'])+'</p></th>'+''.join(vals)+'</tr>')
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="Exact listed orders compared; scroll horizontally if needed"><table class="comparison-table"><caption>Per listed order. Extra items excluded unless named. Unknown is not zero.</caption><thead><tr><th scope="col">Order and portion</th>'+''.join('<th scope="col">'+labels[f]+'</th>' for f in fields)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'

def build_improvements():
    OUT.mkdir(parents=True,exist_ok=True)
    baseline=json.loads((OUT/'baseline-records.json').read_text(encoding='utf-8'))
    audit=json.loads((OUT/'existing-body-audit.json').read_text(encoding='utf-8'))
    audit_by_route={v['route']:v for v in audit}
    current_proof=read_provenance(ROOT/'js/meal-provenance.js')
    current={key(m['chain'],m['name']):{**m,**current_proof.get(key(m['chain'],m['name']),{})} for m in parse_meals()}
    payload=[]; checks=0; duplicates=[]; seen_paragraphs={}; current_checks=0
    for i,d in enumerate(DECISIONS):
        records=[baseline[k] for k in d['keys']]
        for record_key,record in zip(d['keys'],records):
            assert record_key in current,('Reviewed order removed',record_key)
            for field in ('cal','p','c','fat','f','na','checked','sourceDate','region','serving','source'):
                assert current[record_key].get(field)==record.get(field),('Reviewed source snapshot changed; editorial review required',record_key,field,record.get(field),current[record_key].get(field))
                current_checks+=1
        ctx={chr(65+j):type('Record',(),r)() for j,r in enumerate(records)}
        for expression,expected in d['assertions']:
            observed=eval(expression,{'__builtins__':{}},ctx)
            assert observed==expected,(d['route'],expression,expected,observed)
            checks+=1
        assert all(r['region']=='U.S.' and r.get('source') and r.get('serving') for r in records)
        assert len(d['keys'])<=3
        for p in d['paragraphs']:
            assert p not in audit_by_route[d['route']]['copy'],(d['route'],'paragraph repeats existing copy')
            norm=' '.join(p.lower().split())
            assert norm not in seen_paragraphs,(d['route'],'duplicate authored paragraph')
            seen_paragraphs[norm]=d['route']
        href='restaurant-meal-finder.html?'+urlencode([('compare',k) for k in d['keys']])
        assert parse_qs(urlparse(href).query)['compare']==d['keys']
        body='<p>'+html.escape(d['paragraphs'][0])+'</p>'+numeric_table(records,d['fields'])+''.join('<p>'+html.escape(p)+'</p>' for p in d['paragraphs'][1:])
        body+='<p><a class="text-action" href="'+html.escape(href,quote=True)+'">Compare these exact orders</a>'
        if d['route']==TARGETS[18]: body+=' · <a href="protein-value-calculator.html">Use your receipt prices</a>'
        if d['route']==TARGETS[19]: body+=' · <a href="compare-complete-restaurant-orders.html#order-builder">Build your full order</a>'
        body+='</p>'
        source_refs=[]
        for r in records:
            source_refs.append({'key':key(r['chain'],r['name']),'url':r['source'],'recordInspectionDate':r['checked'],'sourceEdition':r.get('sourceDate'),'method':r['verificationStatus'],'newSourceInspection':CURRENT_SOURCE_REVIEW[r['chain']]['method'],'currentSourceReviewDate':'2026-10-09','portion':r['serving'],'region':r['region']})
        source_rows={ (r['source'],r['checked'],r.get('sourceDate')):r for r in records }
        links='<details><summary>Source editions for this comparison</summary><ul>'+''.join('<li><a href="'+html.escape(r['source'],quote=True)+'">'+html.escape(r['chain']+' official source')+'</a> · recorded inspection '+html.escape(r['checked'])+' · edition '+html.escape(r.get('sourceDate') or 'not established')+'</li>' for r in source_rows.values())+'</ul></details>'
        body+=links
        guide=i<10
        anchor='<section class="chain-menu-section" id="menu-comparison">' if guide else '<h2 id="resource-section-4">Sources and date boundaries</h2>' if i<18 else '<section class="guide-sources">' if i==18 else '<section class="hub-notes container">'
        source=(ROOT/d['route']).read_text(encoding='utf-8')
        assert anchor in source,(d['route'],'missing stable insertion anchor')
        slug='growth-'+d['route'].removesuffix('.html')
        wrapper='<section class="'+('container ' if guide or i==19 else '')+'growth-ordering-note" id="'+slug+'"><h2>'+html.escape(d['heading'])+'</h2>'+body+'</section>'
        obj={'route':d['route'],'insertBefore':anchor,'insertionOccurrence':1,'heading':d['heading'],'bodyHTML':body,'sectionHTML':wrapper,'contribution':d['contribution'],'existingPageOverlap':d['overlap'],'baselineBodyRead':'Complete main copy and all table cells extracted, then inspected; audit at docs/growth-release-2026-10-09/editorial/existing-body-audit.json','sourceRefs':source_refs,'comparedKeys':d['keys'],'comparatorHref':href,'substantiveUpdateDate':'2026-10-09','status':'checked','checks':{'arithmeticAssertions':d['assertions'],'sourceRecordAssertions':[{k:r.get(k) for k in ('chain','name','cal','p','c','fat','f','na','checked','sourceDate','region','serving','source')} for r in records],'zeroAsUnknown':False,'newIndexableRoute':False,'medicalReview':'No new physiological or disease-management claims; no expert review claimed.'},'integrationInstructions':'Insert section idempotently before the exact anchor; include heading in local article contents where present. Update substantive dateModified and sitemap lastmod only for this changed route. Preserve original published/review dates and all record inspection dates.'}
        if guide:
            obj['removeLegacyComparisonSelector']='section.chain-picks-section'
            obj['integrationInstructions']+=' Replace the prior lowest-calorie/highest-protein comparison section, rather than stacking two tables of unrelated picks; retain the full menu table and source disclosure.'
        if i==19:
            counts=Counter(r['chain'] for r in baseline.values())
            routes={r['chain']:r['url'] for r in baseline.values()}
            obj['directoryCorrection']={'currentProblem':'The live-generation baseline labels and links 15 chains despite 463 records across 25 chains.','heading':'Browse all '+str(len(counts))+' restaurants','entries':[{'chain':chain,'route':routes[chain],'recordCount':counts[chain]} for chain in sorted(counts)],'instruction':'Replace the legacy 15-chain list with actual current-data chain counts and routes during integration; if the dataset expands, recompute from the complete canonical meal list.'}
        payload.append(obj)
    for a in DECISIONS:
        for b in DECISIONS:
            if a['route']>=b['route']:continue
            ratio=SequenceMatcher(None,' '.join(a['paragraphs']),' '.join(b['paragraphs'])).ratio()
            if ratio>.65: duplicates.append({'a':a['route'],'b':b['route'],'ratio':ratio})
    assert not duplicates,duplicates
    result={'release':'2026-10-09','missingPackage':'GetMacros_Content_Release_2026-10-08.zip is unavailable; no packaged drafts or new articles reconstructed.','counts':{'existingPagesSubstantiallyImproved':len(payload),'newArticles':0,'newMenuRecords':0,'numericAssertions':checks},'sourcePolicy':'Current official extracted rows were spot-checked for the selected values; this is not a complete menu reinspection or a replacement for record provenance. Cane’s current retrieval failed. All stored dates remain unchanged.','improvements':payload}
    (ROOT/'tools/growth_release/editorial-improvements.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'source-review.json').write_text(json.dumps({'reviewDate':'2026-10-09','methodLimit':'Web extracted rows; no claim that every PDF visual column or complete current local menu was newly verified. Existing source-audited records are preserved.','chains':CURRENT_SOURCE_REVIEW},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    review={'routes':[v['route'] for v in payload],'completeBodyReads':len(audit),'sourceRecordChecks':sum(len(v['comparedKeys']) for v in payload),'currentDatasetFieldComparisons':current_checks,'arithmeticAssertions':checks,'duplicateAuthoredParagraphs':0,'highSimilarityAdditionPairs':duplicates,'comparatorQueryRoundTrips':len(payload),'missingPackageRecreated':False,'rootHTMLModifiedByThisAuthor':False,'pending':'Root integration and browser/production checks required; these prepared additions are not claimed published.'}
    (OUT/'review-checks.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(review,ensure_ascii=False))

if __name__=='__main__':
    if '--audit' in sys.argv: audit_existing()
    else: build_improvements()
