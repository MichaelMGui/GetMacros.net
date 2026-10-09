"""Replace repetitive restaurant ranking cards with explicit, data-backed decisions.

Run after the publication build. Existing reviewed nutrient records are the source;
this does not refresh restaurant verification dates or invent missing values.
"""
from pathlib import Path
from html import escape
import json, re
from urllib.parse import urlencode
from build_restaurant_pages import parse_meals
from normalize_calculator_layouts import Document

ROOT = Path(__file__).resolve().parents[1]
# Each comparison addresses a different real ordering decision. Pair names must
# match source records exactly, so renamed/deleted records fail the build.
CHOICES = {
 'Chipotle': ('Bowl or salad: what changes?', 'High Protein-High Fiber Bowl', 'High Protein-Low Calorie Salad',
  'The bowl includes light brown rice and black beans; the salad uses Supergreens and guacamole. These are two complete builds, not the same bowl with rice removed. The bowl has more protein and fiber, while the salad has fewer calories. Choose the build you want to eat rather than treating the word salad as a nutrition rating.',
  'Changing rice, beans, guacamole or the protein changes this comparison. Use the ingredient list below to recreate the listed build, then check custom changes in Chipotle’s calculator.'),
 'Chick-fil-A': ('Nuggets or a sandwich?', 'Grilled Nuggets, 8 count', 'Grilled Chicken Sandwich',
  'The eight-count nuggets are a smaller protein portion. The sandwich includes a bun and supplies more total food energy, with only a small increase in protein. Neither number includes an extra side or a drink. A nugget serving and a sandwich answer different appetite needs; the smaller number is not automatically a better lunch.',
  'Check which sauce packets you use. If you add fries, fruit or another side, compare that complete order instead of using the nugget-only total.'),
 'Sweetgreen': ('Similar protein, different bowl sizes', 'Chicken Pesto Parm', 'Harvest Bowl',
  'These recorded bowls are close in protein but differ substantially in calories. The Harvest Bowl has more fiber and less sodium in our records, so choosing only by calorie count would miss part of the comparison. Both figures describe the standard bowl, including its listed dressing.',
  'Removing dressing or changing grains creates a different build. Do not subtract an assumed dressing amount: check the specific dressing portion in Sweetgreen’s nutrition information.'),
 'CAVA': ('Greens or rice as the starting point?', 'Greek Salad bowl', 'Chicken + Rice bowl',
  'The Chicken + Rice bowl has more calories and slightly more protein than the Greek Salad bowl. Their recorded sodium totals are the same. Choosing greens is therefore not a reliable way to lower every nutrient at once; compare the whole standard bowl, including its dips and toppings.',
  'These are named standard bowls, not interchangeable bases in a custom order. Bread, extra dips and substitutions need a separate nutrition check.'),
 'Subway': ('Six-inch or footlong?', '6-inch Grilled Chicken & Fresh Avocado', 'Footlong Grilled Chicken & Fresh Avocado',
  'For this recorded recipe, the footlong doubles the six-inch calories, protein, fiber and sodium. That makes size a straightforward decision: compare the amount you plan to eat, not just the sandwich name. If you eat half of this exact footlong, the six-inch record is the matching portion.',
  'This relationship applies to the listed Fresh Avocado recipe. Different bread, cheese, sauces or a different chicken sandwich cannot be substituted without checking the numbers.'),
 'Panera': ('Check the portion before comparing salads', 'Green Goddess Cobb Salad with Chicken, half', 'Caesar with Chicken Salad, whole',
  'The smaller calorie total belongs to a half salad; the Caesar record is a whole salad. This is not an equal-size recipe comparison. Use these figures when those are the portions you would actually order, and do not conclude that the entire difference comes from the dressing or recipe.',
  'A cup of soup, bread or a side adds to the order. You Pick Two combinations must use the correct half or cup portions rather than whole-item figures.'),
 'Starbucks': ('Egg bites or a breakfast wrap?', 'Egg White & Roasted Red Pepper Egg Bites', 'Spinach, Feta & Egg White Wrap',
  'The wrap supplies more protein, fiber and calories than the egg bites in these records. The bites are the smaller breakfast option, but the wrap may better match a larger appetite. These are food-only comparisons: a latte, syrup or other drink is not included.',
  'Check the portion count for egg bites and the drink size separately. A protein-box label also does not guarantee more protein than a wrap; use the menu table above to compare grams.'),
 'McDonald’s': ('Two burgers with different protein totals', 'Double Cheeseburger', 'Quarter Pounder with Cheese',
  'The Quarter Pounder with Cheese adds calories and protein compared with the Double Cheeseburger, while the recorded sodium totals are close. If your priority is a lower-sodium order, changing between these two burgers makes much less difference than the calorie totals might suggest.',
  'These are individual burgers. Fries, drinks and a second sandwich are not included. Removing ingredients also requires a new check rather than using the standard burger total.'),
 'Wendy’s': ('A wrap and sandwich with the same protein', 'Grilled Chicken Ranch Wrap', 'Classic Chicken Sandwich',
  'Both recorded items contain the same amount of protein. The wrap has fewer calories and less sodium, while the sandwich has more fiber. That is a useful comparison when protein is your first filter: more calories here do not buy more protein.',
  'The wrap figure includes its standard recipe, including ranch. Extra sauce and meal-deal sides are separate from the values shown.'),
 'Taco Bell': ('What we can compare—and what is missing', 'Cantina Chicken Bowl', 'Veggie Bowl',
  'We can compare the recorded calorie totals for these two bowls. We cannot make a complete protein, fiber or sodium comparison because some values are unverified in our records. A dash is missing information, not a zero and not evidence that the veggie bowl has no protein.',
  'The finder requires known calories, protein, carbs and fat by default. You can include incomplete records, but a nutrient filter still requires that nutrient to be known. Check Taco Bell’s current item information before relying on a missing value.'),
 'Panda Express': ('Chicken alone or with a full greens base?', 'Grilled Teriyaki Chicken', 'Grilled Teriyaki Chicken with Super Greens',
  'The second record adds a full 10 oz Super Greens base to the 6.1 oz chicken entree: 180 calories, 8 g protein, 8 g fiber and 660 mg sodium more. The smaller 3.5 oz Super Greens entree entry is a different source portion and is not used for this combination.',
  'Rice, chow mein or a half-side serving makes a different calculation. Extra sauce packets are separate; the source lists teriyaki sauce as its own portion.'),
 'KFC': ('One piece of chicken or a listed combination?', 'Kentucky Grilled Chicken Breast', 'Grilled Breast with green beans and corn',
  'The combination adds green beans and corn to the grilled breast. It contains more calories and fiber than the chicken piece alone. These are recorded portions, not a promise that grilled chicken or these sides are available at every KFC.',
  'Check your location first. If it offers only a different recipe or side size, the figures here do not transfer to that replacement.'),
 'Popeyes': ('More tenders or a side with your chicken?', '5 Blackened Tenders', '3 Blackened Tenders with regular red beans and rice',
  'Five tenders provide more protein; three tenders with red beans and rice provide more calories and fiber. Their recorded sodium totals are close. This is a choice between a larger chicken portion and a mixed order, not a comparison where one option wins every category.',
  'The side is a regular portion. A larger side, biscuit, dipping sauce or drink changes the total and should be added separately.'),
 'Jersey Mike’s': ('A bowl is not automatically smaller than a sub', 'Turkey and Provolone Bowl, Mike’s Way', 'Mini Turkey and Provolone, Mike’s Way',
  'These two recorded orders have similar calories, even though one has no bread. The bowl has more protein and slightly less fiber. Removing bread from the name does not establish a lower-calorie order when the complete portions differ.',
  'Both records are Mike’s Way. A regular sub, wrap or different toppings are separate orders; do not reuse the mini-sub numbers for them.'),
 'Dunkin’': ('Small wrap or English muffin?', 'Egg & Cheese Wake-Up Wrap', 'Egg & Cheese English Muffin',
  'The English muffin contains twice the recorded protein of the small wrap, along with more calories. If one wrap is too little food, compare the actual number you order: two standard wraps would double the wrap figures, rather than remain a 180-calorie breakfast.',
  'Coffee additions and specialty drinks are separate. Use the listed sandwich recipe; adding meat or changing cheese needs its own check.'),
}

def run():
 meals=parse_meals()
 provenance=__import__('meal_provenance').read(ROOT/'js/meal-provenance.js')
 for chain,(title,first,second,meaning,check) in CHOICES.items():
  pair=[next(m for m in meals if m['chain']==chain and m['name']==name) for name in (first,second)]
  rows=[]; orders=[]
  for m in pair:
   vals=['—' if m.get(k) is None else f'{m[k]:,g}'+unit for k,unit in [('cal',''),('p',' g'),('f',' g'),('na',' mg')]]
   rows.append('<tr><th scope="row">'+escape(m['name'])+'</th>'+''.join('<td>'+v+'</td>' for v in vals)+'</tr>')
   r=provenance.get(chain+'||'+m['name'],{})
   source=r.get('source') or m.get('source')
   if not source: raise ValueError('Missing source: '+m['name'])
   orders.append('<li><strong>'+escape(m['name'])+'</strong><p>'+escape(m['why'])+'</p><a href="'+escape(source,quote=True)+'" target="_blank" rel="noopener">Restaurant nutrition source</a></li>')
  fragment='<section class="chain-picks-section" id="ordering-comparison"><div class="container"><h2>'+escape(title)+'</h2><p>'+escape(meaning)+'</p><p>Recorded U.S. portions; extra items excluded. A dash means unverified.</p><p class="table-scroll-note">Scroll the table sideways to compare all nutrients.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Two recorded orders compared"><table class="comparison-table"><thead><tr><th scope="col">Order and portion</th><th scope="col">Calories</th><th scope="col">Protein</th><th scope="col">Fiber</th><th scope="col">Sodium</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div><h3>Before you order</h3><p>'+escape(check)+'</p><details><summary>Included items and sources</summary><ul>'+''.join(orders)+'</ul><p>Figures use the recorded source dates. Confirm current portions and local availability before ordering.</p></details><p><a class="btn" href="restaurant-meal-finder.html?'+escape(urlencode({'chain':chain, **({'complete':'0'} if any(m.get(k) is None for m in pair for k in ('cal','p','c','fat')) else {})}),quote=True)+'">Filter '+escape(chain)+' orders</a></p></div></section>'
  path=ROOT/pair[0]['url'];text=path.read_text(encoding='utf-8');doc=Document(text)
  node=next(n for n in doc.nodes if 'chain-picks-section' in n['attrs'].get('class','').split())
  text=text[:node['start']]+fragment+text[node['end']:]
  path.write_text(text,encoding='utf-8')
 sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
 changed={m['url'] for m in meals}|{'body-recomposition-explained.html','sources.html'}
 for name in changed:
  sitemap=re.sub(r'(<loc>https://getmacros\.net/'+re.escape(name)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-09-28',sitemap)
 (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
 print('Updated 15 restaurant comparisons; nutrient records and source dates unchanged.')

if __name__=='__main__':run()
