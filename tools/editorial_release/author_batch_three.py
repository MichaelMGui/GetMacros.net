"""Original analyses of inspected U.S. restaurant rows, not menu marketing copy."""
from author_batch_two import *
PAYLOAD=json.loads((D.parent/'restaurant_release/expansion-payload.json').read_text(encoding='utf-8'))
RECORDS=PAYLOAD['records']
for chain in PAYLOAD['chains']:
 u=chain['source']['url']
 source_info[u]=(chain['chain']+' official U.S. nutrition information','Exact published order values and portion definitions; source edition '+str(chain['sourceDate'] or 'not established')+'. Retrieved October 4, 2026.')

CONVERT='https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9'
source_info[CONVERT]=('NIST: unit conversion factors','Avoirdupois ounce and pound conversion factors and thermochemical calorie-to-joule conversion; rounded factors are identified as approximations.')
for r in rows:
 if r['slug'] in ['per-ounce-vs-per-100g-food.html','calculator-pound-kilogram-entry.html']:
  r['sources'].append({'url':CONVERT,'label':source_info[CONVERT][0],'supports':source_info[CONVERT][1]})

def order_table(indices):
 return table('Published U.S. portions; drinks and extra sides are excluded unless the order explicitly includes them.', ['Restaurant / exact order','Serving','kcal','Protein (g)','Carbs (g)','Fat (g)','Fiber (g)','Sodium (mg)'], [[r['meal']['chain']+' — '+r['meal']['name'],r['provenance']['serving'],r['values']['cal'],r['values']['p'],r['values']['c'],r['values']['fat'],r['values']['f'] if r['values']['f'] is not None else 'Not exact / see source',r['values']['na']] for r in [RECORDS[i] for i in indices]])

def analysis(slug,title,desc,intent,indices,body,category='Restaurant comparisons',checks=()):
 selected=[RECORDS[i] for i in indices]
 urls=list(dict.fromkeys(r['provenance']['source'] for r in selected))
 add(slug,title,desc,category,intent,'Original source-defined comparison, fully labeled table and decision limits.',body+'\n\n'+order_table(indices),src=urls,tool='restaurant-meal-finder.html',tool_label='Compare the tracked U.S. meals',scope='These are specific U.S. source-defined orders, not personalised recommendations or worldwide menus. Published values are estimates of standard portions. Extra items, unrecorded substitutions, prices and allergen safety are not inferred. Source retrieval is October 4, 2026; an older printed edition remains an older edition.',checks=list(checks))
 rows[-1]['tableFacts']=[{'recordKey':r['recordKey'],'values':r['values'],'serving':r['provenance']['serving'],'sourcePage':r['sourcePage'],'sourceRow':r['sourceRow']} for r in selected]

analysis('arbys-roast-beef-cheddar-french-dip','Arby’s roast beef, Beef ’n Cheddar or French Dip?','Three sandwiches show why equal protein does not mean equal sodium.','Choose among three roast-beef sandwich builds without treating au jus as an extra unknown.',[10,9,11],'''The Classic Roast Beef and Classic Beef ’n Cheddar each list 23 g protein, but they are not nutritionally interchangeable. The French Dip & Swiss/Au Jus lists more protein and substantially more sodium. Choose the published sandwich that meets the limits you actually care about.

## Compare the complete named builds

The Classic Roast Beef is 360 kcal and 970 mg sodium. Beef ’n Cheddar is 450 kcal and 1,280 mg. Moving between those two adds 90 kcal and 310 mg sodium while the listed protein stays at 23 g. The difference belongs to the complete builds; it is not a verified nutrition value for cheese alone.

French Dip & Swiss/Au Jus is 530 kcal, 34 g protein and 2,540 mg sodium. Au jus is explicitly in that source entry. Do not add a second serving of dipping liquid to the recorded total simply because it arrives separately.

## Use the right filter order

With an illustrative sodium ceiling of 1,500 mg, the first two orders qualify and the French Dip does not. With protein at least 30 g, only the French Dip of this trio qualifies. Combining those two limits leaves no match. That is a useful trade-off, not a failed search.

## Before ordering

Check local availability and the source serving. The table shows sandwiches rather than combinations with fries or a drink. A more filling purchased order may have a different total, and none of these differences measures how much you will enjoy it.''',checks=[['450-360',90],['1280-970',310]])

analysis('arbys-breakfast-bread-format','Arby’s bacon breakfast: biscuit, croissant, wrap or sourdough?','The bread format changes the complete breakfast, not just its shape.','Compare four bacon breakfast formats with printed mass and sodium.',[32,33,34,35],'''Bread choice changes the listed breakfast enough to be worth checking. Arby’s Bacon, Egg & Cheese versions range from 410 to 470 kcal in these four records, but their sodium range is wider than the calorie difference might suggest.

## A calorie tie can hide other differences

The biscuit and sourdough entries both list 470 kcal. The sourdough has 23 g protein and 1,260 mg sodium; the biscuit has 18 g and 1,720 mg. Equal calories therefore do not mean equal protein, sodium or serving weight.

The croissant is 430 kcal, 18 g protein and 1,010 mg sodium. The wrap is 410 kcal, 18 g and 1,330 mg. The lower-calorie wrap is not the lower-sodium choice in this pair. Choosing solely by the bread’s familiar appearance would miss that distinction.

## These are whole-order differences

The printed weights range from 132 g for the croissant to 166 g for the biscuit. Different bread, recipe and portion can all affect the full order. Subtracting one breakfast from another does not isolate the nutrient value of a bread replacement you can make at every location.

## A practical breakfast decision

Start with whichever breakfast formats the location actually offers, then compare the complete rows. Add any ordered potato side, spread or drink separately using its own source portion. Breakfast availability is location-dependent; this comparison records published builds rather than promising all four will be offered where you are.''',category='Breakfast decisions',checks=[['1720-1260',460],['1330-1010',320]])

analysis('del-taco-two-street-tacos-vs-burrito','Two Del Taco street tacos or one chicken burrito?','Count the tacos before comparing them with a whole burrito.','Compare a clearly calculated two-taco order with a standard single burrito.',[59,76],'''Two Grilled Chicken Street Tacos and one Del Classic Chicken Burrito are different-sized orders. Two tacos total 220 kcal and 18 g protein; the burrito lists 560 kcal and 24 g. This comparison helps you count what is actually on the tray, without pretending the portions are equivalent.

## Double every taco value

The official street-taco row is one 90 g taco: 110 kcal, 9 g protein, 13 g carbs, 3.5 g fat and 300 mg sodium. Two identical published portions total 180 g, 220 kcal, 18 g protein, 26 g carbs, 7 g fat and 600 mg sodium. Fiber is published as 0 g per taco; that is a reported value, not an analysis of every tortilla batch.

## Put the burrito beside the actual order

The Del Classic Chicken Burrito is one 251 g portion with 1,200 mg sodium. Compared with the calculated pair of tacos, it has 340 more kcal, 6 g more protein and 600 mg more sodium. The table below retains the one-taco source row so the multiplication is reproducible.

## Avoid turning the comparison into a promise

The pair may or may not be enough food for your meal. The numbers cannot answer hunger or preference for you. No combo discount, salsa packet, side or beverage is included, and local prices are not known. If you want a larger order, calculate the exact extra items rather than silently treating two tacos as a complete restaurant combo.''',checks=[['2*110',220],['2*9',18],['2*300',600],['560-220',340]])

analysis('del-taco-bean-burrito-vs-veggie-burrito','Del Taco bean-and-cheese or Eight Layer Veggie Burrito?','A vegetable-focused name does not predict the fiber number.','Compare named bean and veggie burritos rather than inferring fiber from branding.',[70,71,69],'''The Bean & Cheese Burritos list more fiber than the Eight Layer Veggie Burrito in this source. That does not make one a universally better meal. It shows why the nutrient row is more useful than guessing from the word “veggie.”

## Start with the actual portions

Both Bean & Cheese versions list 15 g fiber and 24 g protein at 280 g. The green-sauce version is 500 kcal and the red-sauce version is 520 kcal. The Eight Layer Veggie Burrito is a larger 342 g portion, 540 kcal, 9 g fiber and 18 g protein.

The 6 g fiber difference belongs to the full published orders. You cannot assign all of it to one ingredient without compatible ingredient records. “More layers” also does not automatically mean more of every nutrient.

## The sauce versions are not identical

The green-sauce row lists 1,360 mg sodium and the red-sauce row 1,330 mg. Their 30 mg difference is small relative to the complete orders and published values are rounded estimates. Do not promise that every actual red-sauce burrito will have precisely 30 mg less.

## Keep classification separate

This is a comparison of named menu entries, not an allergen or vegan certification. Consult the restaurant’s ingredient and allergen information for those questions. If fiber and protein are your priorities, use their reported amounts alongside calories, sodium and the portion you plan to eat; a plant-related title is not a substitute for those numbers.''',category='Fiber and plant foods',checks=[['15-9',6],['342-280',62]])

analysis('sonic-small-burgers-not-same-order','SONIC’s smaller burgers: read beyond “Jr”','Three small burger names still describe different nutrition profiles.','Resolve small burger portion choices without assuming the junior name guarantees lower sodium.',[123,124,117,116],'''“Jr” describes a menu format, not a fixed nutrient profile. In these SONIC records, the Jr Double Cheeseburger has more protein and less sodium than the Jr Bacon Cheeseburger, even though their calories are close.

## Compare the four named orders

The Jr Burger lists 270 kcal and 11 g protein; the Jr Cheeseburger lists 290 kcal and 13 g. The Jr Double Cheeseburger is 390 kcal with 21 g protein and 870 mg sodium. The Jr Bacon Cheeseburger is 400 kcal with 17 g protein and 1,440 mg sodium.

Between the last two, the published calorie difference is only 10 kcal. Protein differs by 4 g and sodium by 570 mg. Do not assume a lower patty count creates a lower-sodium complete recipe when its other ingredients differ.

## What the differences do not tell you

These rows do not supply the nutrient values of bacon, cheese or patties in isolation. Removing an ingredient is not automatically the same as ordering a different menu entry. Use an explicitly published variation if one is available rather than subtracting an invented topping number.

## Build the tray deliberately

Each table entry is the burger only. Tots, fries, a drink and sauce packets can change the purchased order. Choose an available burger first, then add the exact extras you want. The shortlist does not recommend eating less food or equate a smaller name with a healthier decision; it makes the printed choices easier to compare.''',checks=[['1440-870',570],['21-17',4],['400-390',10]])

analysis('sonic-hot-dog-sodium-toppings','SONIC hot dogs: similar calories, different sodium','The Chicago, New York and Regular Hot Dog builds are not interchangeable.','Show how source-defined hot dog builds can tie on calories but differ in sodium.',[137,140,141,136],'''SONIC’s Chicago Hot Dog and New York Hot Dog both list 400 kcal in this brochure. Their sodium figures are 2,030 mg and 1,110 mg respectively. A calorie tie therefore leaves a meaningful ordering question unanswered.

## Compare recipes, not just hot-dog size

The Regular Hot Dog lists 360 kcal, 12 g protein and 800 mg sodium. The All-American Hot Dog lists 410 kcal, 13 g protein and 1,150 mg. These are named builds with different nutrient totals; the table does not turn the extra sodium into an exact value for relish, mustard or another individual topping.

The Chicago versus New York difference is 920 mg sodium while listed protein differs by 2 g. If you use an illustrative 1,200 mg sodium ceiling, the Chicago row fails it while the other three qualify. That ceiling is an example search setting, not a personal recommendation.

## Check the availability marks

Some of these entries carry a symbol in the source for optional availability. A record in a nationwide brochure does not promise that every location offers it. Confirm the named build rather than ordering a similarly described item and copying the figure.

## Add the rest separately

Drinks and side portions are absent from this table. A hot dog and a full combination meal are different comparisons. Use the recorded hot dog as one component and add documented extras if they are part of your plan. Sodium here is reported in milligrams, not grams of salt.''',checks=[['2030-1110',920]])

analysis('culvers-chicken-grilled-crispy-spicy','Culver’s grilled, crispy or spicy chicken sandwich?','Protein, calories and sodium all change with the published build.','Compare chicken sandwich preparations using the older officially linked source without claiming a fresh menu update.',[170,169,171],'''In Culver’s linked July 2025 guide, the Grilled Chicken Sandwich is the lowest-calorie and highest-protein option of these three. The crispy and spicy sandwiches have their own trade-offs; the result is specific to these published recipes, not a rule about all grilled food.

## Read the full sandwich rows

Grilled lists 480 kcal, 36 g protein and 1,340 mg sodium. Crispy lists 690 kcal, 28 g protein and 1,590 mg sodium. Spicy Crispy lists 680 kcal, 32 g protein and 1,680 mg sodium. Switching from Crispy to Grilled changes the recorded total by 210 kcal and increases protein by 8 g.

Spicy Crispy has 10 fewer kcal than Crispy but 90 mg more sodium. A small calorie difference should not obscure the rest of the profile. The two sandwiches also differ in reported fiber and fat.

## Be precise about the source date

We retrieved the restaurant’s linked guide on October 4, 2026, but the printed edition remains July 2025. Retrieval does not turn it into a verified 2026 menu. Confirm current local availability and use updated official figures if the restaurant replaces them.

## Complete your own comparison

These are sandwiches without extra sides or beverages. The difference is between complete recipes, not a tested effect of removing breading from your order. Ingredient and allergen questions require the restaurant’s own guidance; a protein or calorie comparison cannot settle them.''',checks=[['690-480',210],['36-28',8],['1680-1590',90]])

analysis('culvers-dinner-name-side-footnote','What does a Culver’s dinner nutrition row include?','The word “dinner” does not mean every side is in the number.','Explain the official dinner footnote through shrimp, cod and roast portions.',[173,175,176],'''Culver’s dinner figures need their footnote. The linked guide’s dinner entries include the specified protein, lemon wedge, dinner roll and butter; they do not include every side you may receive or choose. A dinner name alone is not a complete accounting boundary.

## Three examples with their scope visible

The six-piece Butterfly Jumbo Shrimp Dinner lists 470 kcal and 13 g protein. The one-piece North Atlantic Cod Dinner lists 350 kcal and 16 g. The Beef Pot Roast Dinner lists 500 kcal and 32 g. Each has its source-defined components and excludes extra sides in the table below.

Do not add a dinner roll and butter again if you are logging one of these rows unchanged. Equally, do not assume fries, coleslaw or a drink are already counted just because the purchase is called a dinner.

## Why piece counts matter

The six-piece shrimp dinner cannot be compared with a ten-piece shrimp protein portion as if the only difference were sides. Protein quantity and included components both change. Preserve the exact piece count before subtracting totals or making a portion choice.

## Keep the edition honest

This is the officially linked July 2025 guide retrieved in October 2026. It supports the recorded definitions, not a claim that we checked a kitchen or all current local combinations. When an included item or standard recipe changes, the old total may no longer describe your order. Use the source footnotes to decide what still needs its own line.''')

analysis('taco-johns-bowl-base-tradeoff','Taco John’s rice bowl or Loaded Potato Olés bowl?','The base changes the whole chicken bowl, not only its carbohydrate line.','Compare two named chicken bowl types without inventing a customizable potato-to-rice swap.',[192,196],'''The Fiesta Rice Bowl, Chicken and Loaded Potato Olés Bowl, Chicken are different published builds. The rice bowl lists less energy and more protein; the potato bowl lists more fiber. This is a menu comparison, not an instruction to swap a base while keeping an old total.

## Read the differences together

Fiesta Rice Bowl, Chicken is 630 kcal, 38 g protein, 74 g carbs, 19 g fat, 9 g fiber and 1,760 mg sodium. Loaded Potato Olés Bowl, Chicken is 950 kcal, 27 g protein, 73 g carbs, 61 g fat, 12 g fiber and 2,690 mg sodium.

The carbohydrate totals are nearly equal, differing by just 1 g. Calories differ by 320 kcal and fat by 42 g. A “rice versus potatoes” comparison based only on carbohydrate would miss much of the difference between these actual recipes.

## Fiber and protein point different ways

The potato bowl has 3 g more listed fiber but 11 g less protein. There is no single winner unless you identify your priorities first. Neither row is a judgment about the ingredients themselves or a personal daily target.

## Check availability and extras

The source marks these bowls as location-dependent. Drinks, additional sides and sauce packets are not silently added here. If the restaurant offers a customization, get its documented component quantities before assigning it a new nutrient total. These two complete entries do not establish an isolated nutrition value for the base alone.''',checks=[['950-630',320],['61-19',42],['38-27',11]])

analysis('taco-johns-small-fiber-bound','Taco John’s “less than 1 g” fiber is not zero','A source bound changes what you can total and filter honestly.','Show a real published less-than bound and contrast it with exact zero and a known fiber value.',[199,200,202,203],'''Some Taco John’s taco rows publish fiber as less than 1 g. GetMacros retains that as a bound rather than turning it into exactly 0 g. This matters when you add several tacos or apply a minimum-fiber filter.

## What the source actually gives you

The Crispy Taco, Chicken is 130 kcal and 12 g protein, with fiber printed as less than 1 g. Crispy Taco, Steak is 140 kcal and 10 g protein with the same fiber bound. Crispy Taco, Beef lists 1 g fiber, while Refried Beans lists 4 g. The table preserves the difference between a numeric value and a non-exact entry.

## Two tacos do not create an exact figure

Two identical chicken tacos total 260 kcal and 24 g protein from the published values. Their fiber remains non-exact: two portions each below 1 g give a combined upper bound below 2 g. That does not establish 0 g, 1 g or any other precise number.

## Filtering needs a defined rule

A minimum-fiber search should not silently treat missing exact data as a successful match. If you want at least 4 g per recorded order, the one-taco Refried Beans row supplies that amount; the bounded chicken row does not verify it. This is an evidence distinction, not an allergen or dietary classification.

## Practical takeaway

Read the original table when a number is marked non-exact. Less-than notation is useful information; replacing it with a confident zero makes the interface easier to draw but less trustworthy.''',category='Food labels',checks=[['130*2',260],['12*2',24]])

analysis('qdoba-burrito-bowl-published-pair','QDOBA Chicken Queso: bowl or burrito?','Compare the actual published pair before assuming what the tortilla adds.','Show the two official Chicken Queso builds and avoid treating subtraction as ingredient verification.',[305,306],'''QDOBA’s Chicken Queso Bowl and Chicken Queso Burrito have the same named theme, but each is a separately published order. The burrito has more calories, protein, carbohydrate, fiber and sodium. The difference is useful, yet it is not automatically a verified tortilla-only measurement.

## The complete-order difference

The bowl is a 468 g portion at 750 kcal, 43 g protein, 74 g carbs and 1,820 mg sodium. The burrito is 569 g at 1,050 kcal, 51 g protein, 126 g carbs and 2,580 mg sodium. That is 300 additional kcal, 8 g protein, 52 g carbohydrate and 760 mg sodium in the published burrito build.

The portion-weight difference is 101 g. That does not prove which ingredients account for every gram. A reliable ingredient-level claim would require compatible component data and a matching standard assembly.

## Use the pair for a real decision

If you are choosing between these exact named orders, the total difference is enough to compare them. With an illustrative calorie ceiling of 900, the bowl qualifies and the burrito does not. If you require 50 g protein as well, neither meets both example limits.

## Keep extras outside the pair

Chips, a drink and any unrecorded substitutions are separate. The figures do not describe every build-your-own bowl with chicken and queso. Choose the exact source row, then check what the restaurant actually includes in the order you plan to purchase.''',checks=[['1050-750',300],['126-74',52],['2580-1820',760],['569-468',101]])

analysis('qdoba-vegan-bowl-fiber-tradeoff','QDOBA Fajita Vegan Bowl: fiber, protein and the full portion','A named vegan bowl provides useful numbers without becoming a diet score.','Compare a vegan named build with Chicken Queso on supported nutrients while keeping classification source-specific.',[311,305],'''QDOBA’s named Fajita Vegan Bowl lists 22 g fiber and 17 g protein. Chicken Queso Bowl lists 16 g fiber and 43 g protein. Their strengths differ, so the useful question is which recorded portion fits the nutrients you want to compare today.

## A larger weight does not mean more calories

Fajita Vegan Bowl is 482 g and 530 kcal. Chicken Queso Bowl is 468 g and 750 kcal. The vegan build is 14 g heavier while its published energy is 220 kcal lower. Weight reflects the complete food and cannot substitute for the calorie line.

The vegan bowl also lists 1,380 mg sodium versus 1,820 mg. Those are complete standard-build totals, not a claim about all plant-based restaurant dishes or a guarantee about an actual customized portion.

## Let priorities stay explicit

For a hypothetical fiber minimum of 20 g, only the Fajita Vegan Bowl of this pair verifies the requirement. For a protein minimum of 30 g, only Chicken Queso does. Combining both requirements leaves no match. That tells you to reconsider the constraints or compare other documented orders, not to relabel one as perfect.

## The name has a limited job

“Vegan” is retained as the restaurant’s named build, not an independently certified allergen claim. Check ingredient and cross-contact information separately. No price, modification or extra side is supplied by these totals; changing the build requires new evidence.''',category='Fiber and plant foods',checks=[['482-468',14],['750-530',220],['1820-1380',440]])

analysis('el-pollo-loco-salad-dressing-boundary','El Pollo Loco salads: check whether dressing is included','A starred salad total is an incomplete dressed-salad total.','Make the dressing-excluded footnote operational for salad ordering and comparison.',[324,330,329],'''The starred El Pollo Loco salad rows used here exclude dressing. Their calories and protein describe the published salad build without that extra component. Adding a dressing creates a different total; the missing amount is not zero.

## Read three distinct salad bases

Mexican Caesar Salad lists 420 kcal and 52 g protein. Street Corn Salad lists 390 kcal and 52 g. Classic Chicken Tostada lists 820 kcal and 42 g. Each row carries the dressing boundary in the serving description below.

The tostada is not simply a larger serving of the Caesar. Its named construction and nutrient profile differ. A salad title cannot establish either a lower calorie total or an equal amount of chicken.

## Add only the dressing actually chosen

Suppose a separate dressing label states 80 kcal for the quantity you use. That hypothetical add-on would bring Mexican Caesar to 500 kcal. The 80 is a teaching example, not an El Pollo Loco dressing value. Use the actual official dressing entry and its serving size for your order.

## Do not reverse-engineer the missing component

The difference between two salad totals does not reveal either dressing’s nutrition because both salad recipes differ and exclude it. Nor can the source’s salad figure prove that the restaurant serves your packet on the side. Confirm the order construction locally.

This comparison retains U.S. September 2026 source definitions. Extra chips, a beverage and any additional toppings remain separate. A useful salad comparison starts by making those boundaries visible, rather than relying on the appearance of vegetables.''',checks=[['420+80',500]])

analysis('el-pollo-loco-tortilla-complete-chicken-meal','El Pollo Loco chicken meal: corn or flour tortillas?','An explicit two-piece meal pair includes beans and rice.','Compare officially named complete chicken-meal variants with sides fixed in the source.',[327,328],'''This El Pollo Loco pair is a useful comparison because both published names include a two-piece breast-and-wing meal, pinto beans and rice. The tortilla format differs. Preserve that exact construction rather than comparing a bare chicken portion with a full meal.

## What the published pair says

The corn-tortilla entry is 660 kcal, 58 g protein, 77 g carbs, 14 g fat, 8 g fiber and 2,070 mg sodium. The flour-tortilla entry is 740 kcal, 59 g protein, 85 g carbs, 18 g fat, 8 g fiber and 2,490 mg sodium.

The full flour-version total is 80 kcal and 420 mg sodium higher. Protein differs by just 1 g and reported fiber is the same. These complete rows are stronger evidence than assuming that every tortilla type has a universal calorie or fiber value.

## Keep the included sides counted once

Pinto beans and rice belong to both named records. Adding their standard portions again would double-count them. If you select another side or different pieces of chicken, neither original row automatically becomes accurate for the revised meal.

## Use the difference honestly

The source-defined pair supports a menu decision between these builds, not an allergen verdict or a claim that one tortilla is always better. It also does not include every sauce packet or drink. Check the published portion and current local assembly before logging or sharing the total.''',checks=[['740-660',80],['2490-2070',420],['85-77',8]])

analysis('noodles-regular-noodle-orders-not-addons','Noodles & Company: which noodle rows already include chicken?','A named chicken dish and a base pasta need different accounting.','Distinguish regular dishes with included protein from plain base dishes before adding extras.',[349,353,356],'''Some Noodles & Company dishes already include a named chicken component, while others are pasta builds without that named addition. Read the complete dish name before adding a separate protein entry. Otherwise your comparison can count chicken twice.

## Three regular-size records

Buttery Parmesan Noodles lists 760 kcal and 22 g protein. Rigatoni Rosa with Parmesan Chicken lists 890 kcal and 45 g. Chicken Parmesan lists 940 kcal and 51 g. Their protein difference reflects complete recipes, not simply a single chicken serving layered over the same noodles.

The Rigatoni Rosa record is 130 kcal above Buttery Parmesan and 23 g higher in protein. It also lists 13 g fiber versus 4 g. Those differences cannot be assigned solely to chicken because pasta, sauce and other components are not identical.

## Choose the correct size first

These are regular-size entries. Small servings and Duos are different source rows and cannot be estimated by dividing every regular total in half unless their documented quantities support that calculation. The dish name and size work together to identify a record.

## Then account for your actual order

If your ordered named dish already includes Parmesan Chicken, do not add that protein again merely because the receipt lists an ingredient. An extra ordered protein is another component and requires its published portion. Drinks and extra sides are not included in this table. This guide records source-defined builds rather than a promise about every customization available at a location.''',checks=[['890-760',130],['45-22',23]])

analysis('noodles-two-chicken-salads','Noodles & Company chicken salads: Caesar or Mediterranean?','Lower calories and lower sodium do not point to the same salad.','Compare two salad builds where sodium reverses the calorie ordering.',[365,366],'''The Mediterranean Salad with Chicken has fewer calories than Chicken Caesar Salad in the regular-size source rows. It also has more sodium. Neither salad wins every comparison, and the restaurant’s names do not replace the nutrient values.

## The published totals

Chicken Caesar Salad is 670 kcal, 42 g protein, 18 g carbs, 49 g fat, 3 g fiber and 1,510 mg sodium. Mediterranean Salad with Chicken is 430 kcal, 36 g protein, 34 g carbs, 17 g fat, 3 g fiber and 1,700 mg sodium.

The Mediterranean row is 240 kcal lower, but 190 mg sodium higher. It has 6 g less protein and 16 g more carbohydrate. The identical 3 g fiber figure does not make their ingredients or portions interchangeable.

## Set the question before ranking

With an illustrative 500 kcal ceiling, only the Mediterranean entry qualifies. With sodium capped at 1,600 mg, only Caesar qualifies. Combining those two example limits produces no match from this pair. A truthful comparison can show that conflict rather than inventing a combined health score.

## Preserve the recipe boundary

Use the exact named regular-size salad record. Removing a dressing or ingredient requires compatible official component information; it is not safe to borrow a calorie subtraction from another chain’s salad. The table does not certify allergen safety, price, local availability or an actual weighed serving. Extra bread, a drink or additional protein remains outside the listed order.''',checks=[['670-430',240],['1700-1510',190],['42-36',6]])

analysis('in-n-out-three-published-hamburger-versions','In-N-Out Hamburger: standard, sauce swap or Protein Style?','The restaurant publishes three exact builds worth keeping separate.','Compare standard Hamburger variants without extrapolating unlisted secret-menu modifications.',[368,369,370],'''In-N-Out publishes specific Hamburger variations: with onion, mustard-and-ketchup instead of spread, and Protein Style with onion. Use those complete rows rather than guessing what a removed bun or sauce contributes.

## Three builds, three totals

Hamburger with onion is 360 kcal, 16 g protein, 38 g carbs and 670 mg sodium. The mustard-and-ketchup version is 300 kcal with the same listed protein and carbs, at 610 mg sodium. Protein Style is 210 kcal, 12 g protein, 9 g carbs and 390 mg sodium.

The source-defined sauce version is 60 kcal lower than standard. Protein Style is 150 kcal lower, but also lists 4 g less protein. A lettuce-wrap name does not mean all nutrients except carbohydrate stay unchanged.

## The portion weight is revealing

The source weights are 209 g, 202 g and 211 g respectively. Protein Style is slightly heavier than standard despite its lower energy. Total mass is therefore not a useful shortcut for either calorie or protein content.

## Stay inside the published choices

This is not a calculator for every off-menu combination. No extra patty, cheese, fries, drink or spread packet is inferred. If you choose a different customization, find an exact official entry or keep its nutrition uncertainty visible. The January 2026 U.S. sheet was consulted in October; that retrieval date is not a claim about an individual kitchen’s portions.''',checks=[['360-300',60],['360-210',150],['16-12',4]])

analysis('in-n-out-double-vs-two-hamburgers','In-N-Out Double-Double or two Hamburgers?','More pieces do not necessarily mean a similar protein total.','Compare one double burger with a transparently calculated two-standard-burger order.',[368,374],'''A Double-Double with onion and two Hamburgers with onion are distinct orders. The Double-Double lists 610 kcal and 34 g protein. Two standard Hamburgers total 720 kcal and 32 g protein using the restaurant’s per-burger values.

## Count the complete order

One Hamburger lists 360 kcal, 16 g protein, 38 g carbs, 16 g fat, 2 g fiber and 670 mg sodium. Two identical portions therefore give 76 g carbs, 32 g fat, 4 g fiber and 1,340 mg sodium alongside their 720 kcal and 32 g protein.

The Double-Double lists 42 g carbs, 34 g fat, 2 g fiber and 1,670 mg sodium. Compared with the pair of Hamburgers, it has 110 fewer kcal and 2 g more protein, but 330 mg more sodium. “One versus two” is not a complete nutritional rule.

## Do not erase the serving difference

The source gives 287 g for Double-Double versus 418 g when two 209 g Hamburgers are combined. This is not an equal-mass comparison and the items have different recipes. It answers which actual order you might purchase, not which ingredient is nutritionally superior.

## Keep calculations identifiable

The two-Hamburger total is calculated here from two published portions; it is not a named restaurant combination row. Fries, drinks and extra sauce are excluded. Use the exact standard versions in the table, because substituting Protein Style or another sauce changes the inputs.''',checks=[['360*2',720],['16*2',32],['670*2',1340],['720-610',110],['1670-1340',330]])

analysis('raising-canes-build-order-not-combo-name','Raising Cane’s: build an order without inventing a combo total','Listed individual portions can be added transparently; a combo name is not enough.','Compare two explicitly calculated individual-item orders while preserving unknown exact fiber.',[378,379,377],'''The two calculated Raising Cane’s orders here are not claimed as published named combos. They add specific individual portions from the official guide. This distinction makes the arithmetic useful without implying that a drink choice or every default combo component has been verified.

## Two orders with three fingers each

Three chicken fingers, fries, Cane’s Sauce and Texas Toast total 1,150 kcal and 45 g protein. Three fingers, Texas Toast and coleslaw total 630 kcal and 41 g protein. Both exclude a beverage; the latter has neither the fries nor sauce from the former.

The difference is 520 kcal and 580 mg sodium. It involves multiple components, so it is not a verified “remove the fries” calculation. The second order changes fries, sauce and coleslaw together. Exact fiber totals remain unavailable because the source has less-than values in relevant components.

## A sandwich is another complete entry

The separately published Chicken Sandwich is 810 kcal and 45 g protein. Do not add the three-finger count again if the sandwich’s recipe already includes its own chicken. Its 297 g source portion differs from either constructed tray.

## How to use the method

Write every selected component and serving count before calculating. Identify which totals are published and which are sums. If the order includes a beverage, add its documented size and type separately. Missing exact fiber does not prevent a calorie sum, but it prevents a confident exact fiber total. The table preserves that limitation rather than replacing it with zero.''',checks=[['1150-630',520],['1880-1300',580],['45-41',4]])

analysis('arbys-sliders-count-whole-tray','Arby’s sliders: one row is one slider','A slider comparison needs the number on your tray.','Compare three recorded slider builds and demonstrate a three-slider order with no invented combo.',[22,23,24],'''Arby’s slider rows describe one slider each. If you plan to eat three, compare the complete three-item order rather than a single small figure. The roast-beef, chicken and ham builds have the same listed protein per slider but different energy and sodium.

## One of each has a clear total

Roast Beef Slider is 180 kcal, Chicken Slider 230 kcal and Ham Slider 170 kcal. Each lists 11 g protein. One of each therefore totals 580 kcal and 33 g protein. Sodium adds to 1,740 mg: 520 + 620 + 600.

This tray contains three distinct recipes and 233 g using the published 77 g, 79 g and 77 g weights. It is a calculated selection, not a named promotional combo. A price deal or available quantity cannot be inferred from these rows.

## Protein alone cannot pick the slider

Equal 11 g protein leaves calories, carbohydrate, fat, sodium and preference as possible decision factors. The ham row lists 0 g fiber while the other two list 1 g. These reported small values should not be turned into sweeping statements about the bread or meat in every actual portion.

## Count extras once

The table is for sliders without extra sides, sauce packets or drinks. If you choose three identical sliders, multiply that exact row by three instead of using the mixed-tray total above. Check the item name and count before saving or sharing an order; a clear serving definition is more useful than a small-looking per-item calorie number.''',checks=[['180+230+170',580],['11*3',33],['520+620+600',1740],['77+79+77',233]])

if __name__=='__main__':write()
