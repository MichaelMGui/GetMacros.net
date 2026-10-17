"""Generate source-linked, arithmetic-checked editorial briefs from staged facts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants'
batch=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-records.json').read_text(encoding='utf-8'))
rows=batch['records']+batch['updates']
def row(market,name):return next(r for r in rows if r['market']==market and r['name']==name)
briefs=[]
def brief(market,slug,title,names,paragraphs,calculations=()):
 selected=[row(market,name) for name in names]
 briefs.append({'market':market,'slug':slug,'title':title,'reviewedAt':'2026-10-17','scope':'Source-backed editorial brief; not published HTML. Exact named servings, not a diet prescription.','paragraphs':paragraphs,'comparisonRows':[{k:r.get(k) for k in ('id','name','serving','servingGrams','cal','p','c','fat','f','na','sugar','sat','ingredientDescription','source','sourceDate','sourcePage','checked')} for r in selected],'calculations':list(calculations),'sources':sorted({r['source'] for r in selected}),'recordIds':[r['id'] for r in selected]})
brief('CA','kfc-canada-original-recipe-pieces-and-two-piece-log','KFC Canada: log the named chicken piece',
 ['Original Recipe® Chicken — Drumstick','Original Recipe® Chicken — Rib','Famous Chicken Sandwich'],[
 'The Canadian table gives separate Original Recipe values for keel, rib, drumstick, wing and thigh. A generic entry called one piece of KFC chicken cannot describe all five. Start with the piece actually eaten, then add separately listed sides and drinks.',
 'One drumstick is 140 kcal, 15 g protein, 2 g carbohydrate and 8 g fat. One rib is 270 kcal, 29 g protein, 6 g carbohydrate and 15 g fat. Two documented drumstick portions total 280 kcal and 30 g protein; that arithmetic is different from choosing an unspecified two-piece combo.',
 'The Famous Chicken Sandwich is its own complete sandwich serving at 690 kcal and 35 g protein. It includes a different published build, so subtracting a chicken piece from the sandwich total would not isolate bread or sauce.',
 'These facts come from the English Canadian sheet updated November 17, 2025 and reviewed October 17, 2026. They are a dated local source selection. Two macaroni-salad rows were withheld because their calories and macros disagree substantially; no replacement numbers were guessed.'
 ],[{'expression':'2 × drumstick','cal':280,'p':30,'c':4,'fat':16,'na':300,'basis':'Two published one-piece portions; no side or drink included.'}])
brief('GB','kfc-uk-fillet-burger-and-ranch-rice-bowl','KFC UK: Fillet Burger or Original Ranch Rice Bowl',
 ['Fillet Burger','Original Ranch Rice Bowl'],[
 'The September 2026 UK&I table gives the Fillet Burger and Original Ranch Rice Bowl the same 28.8 g protein. The rest of their nutrition differs, so a bowl name alone does not establish a lower-calorie choice.',
 'The burger is 463 kcal with 43 g carbohydrate and 18.7 g fat. The bowl is 558 kcal with 62.8 g carbohydrate and 19.7 g fat. For these exact named servings, the bowl adds 95 kcal, 19.8 g carbohydrate and 1 g fat while published protein stays the same.',
 'The source reports salt rather than sodium: 2.2 g for the burger and 2.9 g for the bowl. Converting salt grams to sodium milligrams with salt × 1000 ÷ 2.5 gives 880 mg and 1,160 mg. Those are calculated sodium equivalents; fibre is absent from the table.',
 'The comparison covers one listed item. Chips, dipping sauces and drinks need their own entries. Ireland-only markers and selected-restaurant markers still matter when using this shared source.'
 ],[{'expression':'rice bowl minus burger','cal':95,'p':0,'c':19.8,'fat':1,'na':280}])
brief('IE','kfc-ireland-fillet-roll-and-fillet-burger','KFC Ireland: the Fillet Roll has its own serving',
 ['Original Recipe Chicken Fillet Roll #','Zinger Fillet Roll #','Fillet Burger'],[
 'The official September 2026 shared UK&I sheet marks both Fillet Rolls with #, meaning Ireland-only. Their local entries are preserved for Ireland and excluded from Great Britain coverage.',
 'The Original Recipe Chicken Fillet Roll is 662 kcal, 28.6 g protein, 78.7 g carbohydrate and 24.5 g fat. The Fillet Burger is 463 kcal, 28.8 g protein, 43 g carbohydrate and 18.7 g fat. The roll adds 199 kcal and 35.7 g carbohydrate while the published protein totals remain close.',
 'The Zinger Fillet Roll is another named recipe at 751 kcal, 23 g protein, 81 g carbohydrate and 36 g fat. Its values are not obtained by swapping a chicken number inside the Original Recipe roll.',
 'The three servings exclude an invented meal deal. Use the source name and its Ireland availability marker, then log any actual sides or drinks separately. Sodium is a conversion from source salt, and gram weights and fibre are not supplied.'
 ],[{'expression':'Original Recipe roll minus Fillet Burger','cal':199,'p':-0.2,'c':35.7,'fat':5.8,'na':400}])
brief('AU','gyg-australia-mini-bowl-and-mini-burrito','GYG Australia: Mini Bowl versus Mini Burrito',
 ['Mini Bowl — Mild Grilled Chicken','Mini Burrito — Mild Grilled Chicken'],[
 'The March 9, 2026 Australian guide publishes separate mild grilled chicken Mini Bowl and Mini Burrito recipes. Their names share a filling, but each row is a complete named build with its own source serving.',
 'The 264 g Mini Bowl is 409 kcal with 24.2 g protein, 48.6 g carbohydrate and 12.8 g fat. The 260 g Mini Burrito is 453 kcal with 26.5 g protein, 53.1 g carbohydrate and 14.6 g fat. The burrito adds 44 kcal and 2.3 g protein in these source recipes.',
 'Published sodium is 992 mg for the bowl and 1,090 mg for the burrito. The serving weights are close, but equal food mass would not make their ingredient composition or nutrition identical.',
 'These rows use the standard mild recipe. Spicy deltas, rice swaps, extra toppings and sauces are not automatically applied. The extended menu collection also keeps mini, regular and Little G’s servings separate; restricted-store item names retain the listed store limitation.'
 ],[{'expression':'Mini Burrito minus Mini Bowl','cal':44,'p':2.3,'c':4.5,'fat':1.8,'na':98}])
brief('NZ','subway-nz-regular-and-large-teriyaki-salad','Subway New Zealand: regular and large teriyaki salads',
 ['Regular Salad — Sweet Onion Chicken Teriyaki','Large Salad — Sweet Onion Chicken Teriyaki'],[
 'The May 2026 New Zealand guide gives separate recipes for regular and large salads. The large Sweet Onion Chicken Teriyaki salad is a published 500 g portion, while the regular is 300 g. A large entry is not created by doubling the regular numbers.',
 'The regular salad is 208 kcal with 20.1 g protein, 20.2 g carbohydrate and 5.4 g fat. The large is 402 kcal with 39.3 g protein, 38.6 g carbohydrate and 10.6 g fat. Doubling the regular calories would give 416 kcal, which is not the published 402 kcal large serving.',
 'Both source salad definitions include lettuce, spinach, tomato, cucumber, capsicum, onion, carrot and olives. The named recipe also lists chicken strips in teriyaki glaze, mozzarella and sweet onion sauce. These recipe components describe the standard build, not a full additive or allergen formulation.',
 'The large adds 194 kcal, 19.2 g protein and 640 mg sodium relative to the regular. Log the exact size and sauce actually ordered; ingredient changes need separate support. Two contradictory source food rows were withheld rather than repaired by assumption.'
 ],[{'expression':'large minus regular','cal':194,'p':19.2,'c':18.4,'fat':5.2,'na':640},{'expression':'2 × regular calories','cal':416,'isPublishedLargeServing':False}])
brief('JP','mos-japan-mos-burger-and-teriyaki-chicken','MOS Japan: MOS Burger and Teriyaki Chicken Burger',
 ['モスバーガー','テリヤキチキンバーガー'],[
 'MOS Japan’s October 14, 2026 table reports each named item with a source weight. The MOS Burger is 211.2 g; the Teriyaki Chicken Burger is 148.9 g. The comparison is between those actual local recipes and portions.',
 'The MOS Burger is 372 kcal with 15.2 g protein, 40 g carbohydrate and 17 g fat. The Teriyaki Chicken Burger is 303 kcal with 20.1 g protein, 32.4 g carbohydrate and 10.3 g fat. For these named servings, the chicken burger has 69 fewer calories and 4.9 g more protein.',
 'The source provides sodium directly: 906 mg and 842 mg. It also provides rounded salt equivalents, so the direct sodium values are retained instead of recalculating them from rounded salt. Sugar and saturated fat are unavailable and remain blank.',
 'Japanese names are preserved to help match the local item. MOS Cafe drinks and foods retain their own recipes, separately listed sauces are not silently included, and the source says cold drink weights exclude ice. Item names and these nutrient totals are not full ingredient lists.'
 ],[{'expression':'Teriyaki Chicken Burger minus MOS Burger','cal':-69,'p':4.9,'c':-7.6,'fat':-6.7,'na':-64}])
brief('MX','subway-mexico-gran-pastor-and-gringo-pastor','Subway Mexico: Gran Pastor versus Gringo Pastor',
 ['Pastor — Gran Pastor','Pastor — Gringo Pastor'],[
 'The August 2026 Mexican source names Gran Pastor and Gringo Pastor as separate local builds. Both English and Spanish official sheets agree on the selected macro values. Their portions are the named sandwiches; no six-inch or footlong size is inferred.',
 'Gran Pastor is a 257 g serving at 470 kcal, 31 g protein, 43 g carbohydrate and 20 g fat. Gringo Pastor is 215 g at 420 kcal, 31 g protein, 40 g carbohydrate and 15 g fat. The published protein is equal, while Gran Pastor adds 50 kcal and 5 g fat.',
 'Gran Pastor also has 5 g fibre and 1,510 mg sodium, versus 2 g fibre and 1,360 mg sodium for Gringo Pastor. The extra 3 g fibre therefore comes with a different overall serving, not an isolated ingredient comparison.',
 'This selected expansion adds seven named Golazo/Pastor builds. Two other new builds were withheld because same-date English and Spanish nutrition values conflict. The rest of the older Mexican snapshot is not relabelled as August 2026. Additional sauces, cheese, sides and drinks must be logged separately when actually added.'
 ],[{'expression':'Gran Pastor minus Gringo Pastor','cal':50,'p':0,'c':3,'fat':5,'f':3,'na':150}])
brief('US','panda-express-mushroom-and-orange-chicken-portions','Panda Express: Mushroom Chicken and Orange Chicken portions',
 ['Chicken — Mushroom Chicken','Chicken — The Original Orange Chicken®'],[
 'The official U.S. live nutrition table lists Mushroom Chicken at a 5.7 oz portion and The Original Orange Chicken at 6.2 oz. Each is one published entree portion; neither number is a bowl, plate or family tray.',
 'Mushroom Chicken is 180 kcal with 13 g protein, 12 g carbohydrate and 9 g fat. Orange Chicken is 560 kcal with 19 g protein, 63 g carbohydrate and 25 g fat. Orange Chicken adds 380 kcal and 6 g protein when comparing these exact source portions.',
 'Published sodium is 820 mg for Mushroom Chicken and 1,000 mg for Orange Chicken. A lower-calorie entree can still contribute substantial sodium, so use both displayed values if those are the nutrients you track.',
 'A complete order needs its actual side and every entree portion. The dataset preserves separately published side versus entree versions of Super Greens and does not invent Cub Meal totals from an incomplete capture. The live page supplies no publication date: October 17, 2026 is the review date, not a source-edition date. Restaurant preparation and actual portions can vary.'
 ],[{'expression':'Orange Chicken minus Mushroom Chicken','cal':380,'p':6,'c':51,'fat':16,'na':180}])
brief('NZ','subway-nz-roast-beef-sub-and-wrap-recipes','Subway New Zealand: roast beef bread and dressing differ by format',
 ['6-Inch Sub — Roast Beef','Wrap — Roast Beef'],[
 'The May 2026 New Zealand recipes give the roast beef sub and wrap different standard dressings. The sub lists processed cheddar, lettuce, spinach, tomato, onion and mayonnaise on roasted garlic bread. The wrap lists the same named vegetables and cheese with honey mustard on white flour wrap.',
 'The 222 g sub is 356 kcal with 19.3 g protein, 48.3 g carbohydrate and 8.2 g fat. The 220 g wrap is 329 kcal with 18.5 g protein, 42.9 g carbohydrate and 9.5 g fat. In this source pair, the wrap is 27 kcal lower and 1.3 g fat higher.',
 'Those differences describe two complete published recipes. They do not measure the isolated effect of replacing bread with a wrap or mayonnaise with honey mustard; more than one component changes.',
 'Use the recipe description to check the actual order before logging. A custom sauce or bread choice needs its own documented ingredient amount. These standard-build descriptions are useful menu components, but they do not replace a full ingredient or allergen document.'
 ],[{'expression':'wrap minus sub','cal':-27,'p':-0.8,'c':-5.4,'fat':1.3,'na':-576}])
for b in briefs:
 for calc in b['calculations']:
  if 'minus' not in calc['expression'] or len(b['comparisonRows'])!=2:continue
  a,z=b['comparisonRows']
  if b['market']=='JP':first,second=a,z
  elif b['slug']=='subway-nz-roast-beef-sub-and-wrap-recipes':first,second=a,z
  elif b['market']=='MX':first,second=z,a
  else:first,second=a,z
  for k in ('cal','p','c','fat','f','na'):
   if k in calc:assert abs((second[k]-first[k])-calc[k])<1e-8,(b['slug'],k)
(D/'guide-briefs.json').write_text(json.dumps({'reviewedAt':'2026-10-17','briefs':briefs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceBackedBriefs':len(briefs),'marketCounts':{m:sum(b['market']==m for b in briefs) for m in sorted({b['market'] for b in briefs})}}))
