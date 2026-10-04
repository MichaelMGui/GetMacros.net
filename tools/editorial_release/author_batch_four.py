"""Cross-restaurant decisions and original, reproducible dataset questions."""
from author_batch_three import *

analysis('cross-chain-melt-sandwich-orders','Reuben or sourdough melt: compare the whole sandwich','Three different melt-style orders show why the name is not a serving standard.','Compare melt sandwich constructions across chains with source age kept visible.',[19,180,163],'''A melt-style sandwich is a menu description, not a standard portion. Arby’s Reuben, Culver’s Grilled Reuben Melt and Culver’s Single Sourdough Melt have different recipes and totals. Compare the order you would actually buy rather than treating “melt” as a nutrition category.

## Keep like names distinct

Arby’s Reuben lists 680 kcal, 37 g protein and 2,420 mg sodium. Culver’s Grilled Reuben Melt lists 660 kcal, 37 g protein and 1,840 mg. Those two tie on published protein while sodium differs by 580 mg. The 20 kcal difference does not settle that sodium question.

Culver’s Single Sourdough Melt lists 490 kcal, 26 g protein and 600 mg sodium. It is not another Reuben recipe and should not be described as the same sandwich with one ingredient removed.

## A practical shortlist

If your example search requires at least 30 g protein, the two Reubens qualify and Sourdough Melt does not. If sodium must also stay at or below 2,000 mg, only the Culver’s Reuben of this trio remains. These demonstration limits explain the decision; they are not a recommendation for your day.

## Different sources have different dates

The Culver’s figures come from its linked July 2025 guide, while the Arby’s source carries a June 2026 edition. Both were retrieved in October 2026. A comparison does not make their edition dates equal or certify local availability. Sides, drinks and extra dressing remain outside these sandwich rows.''',checks=[['2420-1840',580],['680-660',20]])

analysis('three-count-tacos-not-three-equal-meals','Three tacos across Del Taco and QDOBA: define the count','A three-taco named order and three single tacos need different arithmetic.','Compare a source-defined three-taco build with a calculated three-street-taco order.',[59,317,318],'''Three tacos is a count, not an equal recipe or food weight. QDOBA publishes complete three-flour-taco builds; Del Taco publishes a single Grilled Chicken Street Taco. Multiply the latter before comparing it with the former.

## Build the calculated order

Three Del Taco Grilled Chicken Street Tacos total 330 kcal, 27 g protein, 39 g carbs, 10.5 g fat and 900 mg sodium. Their combined listed mass is 270 g. The table keeps the individual 90 g source row so the calculation can be checked.

QDOBA’s Street Style Chicken three-taco build is 550 kcal and 29 g protein at 311 g. Its Street Style Pork Carnitas three-taco build is 370 kcal and 23 g protein at 238 g. These are different fillings and recipes; do not infer which difference belongs to the tortilla alone.

## Similar protein does not imply similar totals

The calculated Del Taco chicken order has 2 g less protein than QDOBA’s chicken build, alongside 220 fewer kcal and 790 mg less sodium. Their count is the same, yet their standard servings and other components differ.

## Ordering still needs context

None of these totals includes every sauce packet, drink or side you might choose. Prices are not supplied, so the table cannot rank value. If your location serves a different tortilla or assembly, use the correct official entry instead of keeping a convenient old number. Treat a three-taco total as an explicitly defined selection, never as a universal serving size.''',checks=[['110*3',330],['9*3',27],['300*3',900],['1690-900',790],['550-330',220]])

analysis('protein-chicken-sandwich-size-cross-chain','Three chicken sandwiches with different portion boundaries','Cane’s, Culver’s and SONIC sandwich rows are complete builds.','Choose among source-defined chicken sandwiches without assuming grilled and fried meat quantities are matched.',[377,170,132],'''Raising Cane’s Chicken Sandwich, Culver’s Grilled Chicken Sandwich and SONIC’s Crispy Chicken Sandwich are all sandwiches, but their protein portions and construction are not matched. Read their complete totals before using a preparation label to choose lunch.

## Compare the actual entries

Cane’s lists 810 kcal, 45 g protein and 1,650 mg sodium. Culver’s grilled sandwich lists 480 kcal, 36 g protein and 1,340 mg. SONIC’s crispy sandwich lists 520 kcal, 24 g protein and 1,470 mg. The highest protein amount is not in the lowest-calorie entry.

Between Culver’s and SONIC, the published difference is 40 kcal and 12 g protein. This does not establish the effect of grilling versus frying identical chicken: the restaurants, recipes and portions differ. Do not turn the comparison into a universal cooking-method claim.

## Match the question to the order

If you want a sandwich with at least 35 g protein, both Cane’s and Culver’s meet that example condition. Adding a 600 kcal maximum leaves Culver’s in this three-order comparison. Another person may value taste, serving size or availability instead.

## Preserve the source limitations

The Cane’s entry gives a 297 g sandwich portion. The other rows do not justify inventing matching weights. Culver’s source is its older July 2025 guide retrieved in October 2026; use newer official information if it changes. Fries, drinks and additional sauce portions are not automatically included in any sandwich total.''',checks=[['520-480',40],['36-24',12]])

analysis('salad-burger-calories-no-category-rule','Can a burger have fewer calories than a salad?','The exact restaurant recipe matters more than the category name.','Test the salad-versus-burger assumption against named source-defined entries without universal claims.',[160,365,324],'''Yes, a particular burger can list fewer calories than a particular salad. Culver’s Single ButterBurger lists 390 kcal; Noodles & Company’s Chicken Caesar Salad lists 670 kcal. This example does not rank every burger or salad, and calories alone do not measure overall usefulness.

## Look at the rest of the record

The ButterBurger lists 20 g protein and 480 mg sodium. Chicken Caesar Salad lists 42 g protein and 1,510 mg sodium. The salad supplies more recorded protein as well as more energy and sodium. Neither description contains enough information to predict those totals.

El Pollo Loco’s Mexican Caesar Salad lists 420 kcal and 52 g protein, but its starred source row excludes dressing. That serving boundary must stay visible beside the other two complete named entries; a dressed salad would need the chosen dressing added separately.

## Avoid a misleading category winner

You cannot average these three items and conclude that burgers or salads generally have a particular energy value. Their recipes, chains and included ingredients differ. Nor does a lower calorie number make an order appropriate for everyone or establish ingredient quality.

## Use categories for discovery, numbers for comparison

Choose the kind of food you want, then inspect the exact documented build and relevant nutrients. A salad can be a useful meal without fitting a particular calorie ceiling. A burger can be a useful choice without receiving a health label. Keep extra sides and drinks outside the comparison until their portions are documented.''',checks=[['670-390',280]])

analysis('cross-chain-bean-burritos-serving-proof','Two bean burritos: Del Taco and El Pollo Loco','The shared word “bean” does not create equivalent portions.','Compare bean-based burrito builds by exact serving while avoiding dietary certification.',[70,343],'''Del Taco’s Bean & Cheese Burrito with green sauce and El Pollo Loco’s Original BRC Burrito are both bean-containing named orders. They are not identical recipes or portions. Their fiber and protein figures are useful precisely because the serving definitions stay attached.

## Read each full order

Del Taco lists 500 kcal, 24 g protein, 80 g carbs, 10 g fat, 15 g fiber and 1,360 mg sodium for 280 g. Original BRC lists 410 kcal, 13 g protein, 63 g carbs, 11 g fat, 4 g fiber and 1,020 mg sodium for the published 7.6 oz serving.

The Del Taco entry has 11 g more listed protein and 11 g more fiber. It also has 90 more kcal and 340 mg more sodium. The differences cannot identify what a spoonful of beans contributes because cheese, rice, tortilla and their amounts may differ between recipes.

## Do not make a classification from the name

Bean-containing does not independently prove vegan status, dairy absence or allergen safety. The named cheese ingredient is one reason to read ingredient information, but this nutrient table is not an allergen certification for either order.

## A practical comparison

If fiber is your chosen priority, these exact rows point to different amounts. If the planned calorie ceiling matters more, compare that line as well. This is a two-order decision, not a ranking of all bean burritos or restaurant markets. Drinks, sides and unrecorded modifications remain separate.''',category='Fiber and plant foods',checks=[['24-13',11],['15-4',11],['1360-1020',340]])

analysis('cross-chain-breakfast-ham-formats','Ham breakfasts at Arby’s and SONIC: choose the format','A wrap, croissant and burrito are different breakfasts.','Compare named ham breakfast formats across two chains with availability limits.',[41,43,146,155],'''A ham breakfast can take several forms, and the name of the filling does not predict the whole order. Arby’s croissant and wrap and SONIC’s burrito and Croissonic have different protein and sodium totals. Check the format you actually want to eat.

## The near-calorie cluster

Arby’s Ham, Egg & Cheese Croissant lists 410 kcal and 21 g protein. Its wrap lists 400 kcal and 20 g. SONIC’s Breakfast Burrito Ham lists 440 kcal and 27 g protein; Croissonic Sandwich Ham lists 430 kcal and 22 g.

These figures sit within a 40 kcal range, but sodium runs from 1,040 mg in the Arby’s croissant to 2,000 mg in SONIC’s Croissonic. That 960 mg spread is more informative for a sodium-focused choice than calling all four similar-calorie breakfasts.

## The filling is not isolated

Subtracting the rows does not measure ham nutrition. Each complete recipe contains different bread or tortilla, egg, cheese and quantities. The source weights supplied for the Arby’s orders do not establish weights for SONIC’s entries.

## Check the morning menu

Breakfast and marked regional items depend on the location. Confirm availability before relying on a shortlist. Coffee, a potato side or added sauce is outside these food totals. If you are recording the whole purchased breakfast, add the documented extras rather than assuming they arrived inside the sandwich or burrito row. This comparison is specific to U.S. published builds, not a global breakfast standard.''',category='Breakfast decisions',checks=[['440-400',40],['2000-1040',960]])

analysis('cross-chain-chicken-soup-no-sodium-assumption','Chicken soup at El Pollo Loco and Noodles & Company','A soup label does not guarantee a lower-sodium lunch.','Compare two exact soup servings without pretending bowls and ounce weights match.',[342,367],'''El Pollo Loco’s Chicken Tortilla Soup and Noodles & Company’s regular Chicken Noodle Soup have different serving definitions. Both contain published protein, calories and sodium worth reading. “Soup” alone does not mean low sodium or a complete lunch.

## The two documented portions

Chicken Tortilla Soup lists 240 kcal, 23 g protein, 19 g carbs, 9 g fat, 3 g fiber and 1,260 mg sodium for 13.7 oz. Chicken Noodle Soup lists 360 kcal, 30 g protein, 41 g carbs, 10 g fat, 2 g fiber and 2,320 mg sodium for its regular serving.

The second recorded order has 120 more kcal, 7 g more protein and 1,060 mg more sodium. Because the portion descriptions differ, this is an order comparison rather than a per-ounce ingredient comparison.

## Add the pairing deliberately

Bread, crackers or another side could change the meal, but they are not included by guesswork here. If you choose a soup-and-sandwich combination, count both source-defined portions. A restaurant’s half or small soup option should use its own row rather than an assumed half of this total.

## Keep the question modest

These two soups do not establish which restaurant makes healthier soup in general or how much liquid you should eat. They show what the recorded portions contribute. Sodium is in milligrams, and protein is in grams; neither figure should be compared without its unit. Check the official information if the recipe or serving changes.''',checks=[['2320-1260',1060],['360-240',120]])

analysis('burrito-wrap-cross-chain-no-size-standard','A wrap is not a burrito serving standard','Small wraps and large named burritos should not share one assumed portion.','Compare named wrap sizes across chains to challenge a shape-based serving assumption.',[26,27,307,308],'''Wrapped food does not have a standard size across restaurants. Arby’s chicken wraps and QDOBA’s Cholula Hot & Sweet Chicken Burrito have different portion weights, recipes and totals. An identical-looking handheld shape cannot tell you how much food or protein is inside.

## Weight changes the comparison

Arby’s Ranch Chicken Wrap and Honey Mustard Chicken Wrap each list a 139 g serving. Their calories are 400 and 380, with 16 and 15 g protein respectively. QDOBA’s named burrito is 520 g, 910 kcal and 39 g protein. Its corresponding bowl is a separate 418 g, 610 kcal build.

The QDOBA burrito is more than three times the listed mass of either Arby’s wrap. That does not make a precise three-wrap equivalence: recipes differ and each complete order has its own nutrient density.

## Use count and mass for different jobs

“One” is useful for ordering the menu item. Grams explain the published portion when available. Calories and protein explain selected nutrients. None of these fields can replace the others, especially when comparing a snack-sized handheld with a substantial burrito.

## A fair decision

Compare the whole items if those are the orders you are considering. Do not silently normalize all of them to 100 g and then present that normalized amount as an available menu portion. Extra sides and drinks remain outside the table, and no unrecorded tortilla removal or filling change is assigned a nutrition total.''')

analysis('equal-calories-different-macros-menu','Same calories, different macros: three real menu ties','A tied calorie total can still leave very different protein and fat choices.','Demonstrate exact energy ties across food families without using a macro-calorie recalculation.',[13,14,153,156],'''Equal printed calories do not make restaurant orders nutritionally identical. Four specific source rows below all list 530 kcal, yet protein, carbohydrate, fat and sodium differ. The calorie tie is a starting point for comparison, not a reason to collapse the meals into one option.

## Two lunch orders and two breakfasts

Arby’s Crispy Chicken and Buffalo Chicken each list 24 g protein, 59 g carbs and 22 g fat. Their sodium differs: 1,410 versus 2,100 mg. SONIC’s Brioche Sandwich Sausage lists 22 g protein, 38 g carbs and 33 g fat; its Croissonic Sandwich Sausage lists 19 g protein, 29 g carbs and 37 g fat.

Their identical energy line does not mean the same amount of food or the same distribution of nutrients. The breakfast and main-meal categories also need to stay visible so a shortlist makes practical sense.

## Do not force the macros to solve the tie

Published nutrient values are rounded estimates. Reconstructing calories with a few gram totals is not a reliable way to declare one restaurant’s table wrong or choose an order. Use the official calorie row and retain each macro line separately.

## Use a second decision criterion

If calories are equal, compare the supported nutrient that matters to you, the meal format and current availability. Sodium breaks the Arby’s tie clearly in the published records. Preference can still decide the order. The table excludes additional sides, sauce packets and drinks and does not promise every standard kitchen portion is exact.''',category='Macro fundamentals',checks=[['2100-1410',690]])

analysis('protein-sort-vs-portion-mass','More food weight does not guarantee more protein','Source portions let you separate quantity of food from protein grams.','Compare known gram portions where order weight and protein ranking reverse.',[0,10,11,305,311],'''Sorting food by serving weight would not produce the same order as sorting by protein. Arby’s Pecan Chicken Salad Sandwich is a 322 g portion with 28 g protein; its 324 g French Dip & Swiss/Au Jus lists 34 g. Nearly equal weight leaves a 6 g protein difference.

## A second reversal in bowls

QDOBA’s Fajita Vegan Bowl is 482 g with 17 g protein. Chicken Queso Bowl is lighter at 468 g but lists 43 g protein. The heavier bowl does not automatically have more of this nutrient because food mass includes water and every other component.

## What weight is good for

The serving weight helps identify a published portion and compare an actually measured amount with a compatible record. It is not a measure of satiety, quality or personal fit. A soup’s liquid or a bowl’s vegetables can add mass without matching another recipe’s protein concentration.

The Arby’s Pecan Chicken Salad Sandwich is marked limited-time in the source. Its presence here is not a promise of availability. The source’s au jus scope is also retained for French Dip.

## Use the intended sort

If your question is total protein per available order, sort by the protein field with portion names visible. If you want protein per 100 g, calculate and label that separately instead of replacing the available order with an imagined 100 g purchase. No mass normalization can repair an unknown serving definition.''',category='Practical protein',checks=[['34-28',6],['43-17',26]])

analysis('fat-and-carb-two-energy-profiles','Similar energy, different fat and carbohydrate profiles','Two 950–960 kcal orders show why calories cannot fill missing macro lines.','Compare higher-carbohydrate noodles with a higher-fat potato bowl at similar energy.',[355,196],'''Noodles & Company’s Spicy Korean Steak and Taco John’s Loaded Potato Olés Bowl, Chicken sit close in printed energy: 960 and 950 kcal. Their fat and carbohydrate totals are very different. Knowing calories cannot tell you the missing macro profile.

## Read the two distributions

Spicy Korean Steak lists 150 g carbs and 25 g fat, with 31 g protein. Loaded Potato Olés Bowl, Chicken lists 73 g carbs and 61 g fat, with 27 g protein. The carbohydrate difference is 77 g and the fat difference 36 g, despite a 10 kcal difference in their source energy lines.

These are complete named dishes, not equal ingredient portions. The noodle meal and potato bowl also list different fiber and sodium values: 3 versus 12 g fiber, and 3,400 versus 2,690 mg sodium.

## Do not reconstruct an unknown record

If a restaurant entry supplies calories and protein but lacks fat, borrowing fat from a similar-calorie dish would create false data. Even a familiar meal shape or meat name cannot supply the missing amount. Keep the unknown field unavailable until a matching official source provides it.

## Compare without moral labels

This table does not classify carbs or fat as good or bad, or predict how either order will feel for you. It explains why the separate lines matter. Neither dish includes every extra side or beverage you might buy. If a numeric filter uses an unavailable nutrient, the interface should explain that limit instead of treating the missing figure as zero.''',category='Macro fundamentals',checks=[['150-73',77],['61-25',36],['960-950',10]])

analysis('fiber-count-menu-not-plant-score','Where fiber appears in a varied menu sample','Beans, bowls, noodles and sandwiches all need their actual rows.','Use disparate published examples to explain why a vegetable-name shortcut cannot classify fiber.',[69,70,311,353,181],'''Fiber is a reported nutrient, not a score attached to how green a menu name sounds. The selected orders below include a veggie burrito, bean-and-cheese burrito, vegan bowl, chicken pasta and veggie burger. Their recorded fiber spans 5 to 22 g per defined order.

## The named builds differ

Del Taco’s Eight Layer Veggie Burrito lists 9 g fiber; its Bean & Cheese green-sauce burrito lists 15 g. QDOBA’s Fajita Vegan Bowl lists 22 g. Noodles & Company’s Rigatoni Rosa with Parmesan Chicken lists 13 g, while Culver’s Harvest Veggie Burger lists 5 g.

The chicken-containing pasta does not become a plant-only meal because it has fiber. Equally, the veggie burger name does not guarantee a larger fiber total than every dish with meat. Nutrient content and ingredient classification answer separate questions.

## Preserve the portions

These are not matched calorie or gram portions. The table deliberately shows complete available builds, so it answers an ordering question. A per-100-kcal analysis would be another calculation requiring a clearly labeled denominator, not a replacement menu serving.

## Avoid a broad restaurant ranking

Five selected orders do not represent the whole menus or establish which chain has the most fiber overall. The Culver’s guide is an older linked edition, and availability can differ. Use the official source for additional dishes, ingredient questions or a changed recipe. A fiber-focused filter should use known values and keep non-exact entries out of confident minimum claims.''',category='Fiber and plant foods')

# Eight reproducible dataset questions use the complete expansion snapshot.
def snapshot(slug,title,desc,intent,body,calculation,headers,values):
 add(slug,title,desc,'Dataset field notes',intent,'Original calculation over the 380-record expansion with denominator, source scope and reproducible selection.',body+'\n\n'+table('October 4, 2026 expansion snapshot only; not a nationwide menu census.',headers,values),src=tuple(c['source']['url'] for c in PAYLOAD['chains']),tool='sources.html',tool_label='See source and dataset methods',scope='Analysis is limited to the frozen 380-row October 4, 2026 expansion, not all current GetMacros records, every restaurant menu or actual customer purchases. Rows are source-defined orders and variants. Retrieval dates do not replace printed edition dates. No market-wide statistics, prices or dietary classifications are inferred.')
 rows[-1]['datasetCalculation']=calculation

counts={c['chain']:c['records'] for c in PAYLOAD['chains']}
snapshot('menu-average-chain-weighting','Why a pooled menu average can misrepresent the chains','Unequal record counts can make one restaurant dominate a dataset average.','Understand record-weighted versus chain-weighted summaries in the actual expansion.', '''A pooled average gives every tracked row equal weight. It does not give every restaurant equal influence. In the expansion snapshot, Taco John’s contributes 122 rows while Raising Cane’s contributes three; a combined nutrient average therefore reflects much more of the first selected menu.

## Count the denominator before trusting the result

There are 380 source-defined records across ten chains in this expansion. Taco John’s is 122 ÷ 380, approximately 32.1% of those rows. Raising Cane’s is 3 ÷ 380, approximately 0.8%. These shares describe database coverage, not sales, popularity or the proportion of menu items sold nationally.

## Two different averages answer different questions

A row-weighted calculation describes the average recorded order in this particular collection. A chain-weighted calculation first averages each chain and then gives those ten means equal weight. Neither automatically represents what a person orders, especially when menus contain multiple variations of similar items.

## Use the data for a better task

The finder can compare exact meals without inventing a broad chain health score. When evaluating a dataset summary, look for its scope, count and weighting method. More records can mean more documented variants rather than better or worse food. The table makes the imbalance visible so a single average cannot hide it.''',{'type':'countsByChain'},['Chain','Tracked expansion rows'],list(counts.items()))

breakfast=[r for r in RECORDS if r['meal']['meal']=='breakfast']
snapshot('breakfast-dataset-not-opening-hours','Breakfast records do not establish restaurant opening hours','The breakfast field describes food, not whether your nearby location serves it now.','Use actual breakfast coverage without treating dataset classification as live availability.',f'''The expansion includes {len(breakfast)} breakfast-labeled records. That count identifies documented food builds, not locations, hours or a live menu. A breakfast result should help you find an order while still making availability a local question.

## What the classification means

The meal field separates explicitly identified breakfast entries from main-meal records. It does not decide when every sandwich may be eaten or guarantee a location serves breakfast all day. Arby’s regional breakfast formats and SONIC’s marked optional entries need their source limits preserved.

## Why a breakfast search can look narrower

The collection is intentionally based on verified rows, not every product a chain sells. A restaurant with no breakfast record in this expansion is not proven to have no breakfast menu. Nor does a chain with many documented bread formats necessarily have more locations or broader opening hours.

## Build a useful shortlist

Choose a recorded breakfast, check the source-defined portion, and confirm local availability. Add a drink or side separately if you order one. Do not count a breakfast combo’s beverage unless its type and serving are established.

The table below groups the snapshot by chain. It is an inventory aid for food discovery, not a promise about current service. Keeping those two jobs separate prevents a nutrition tool from presenting itself as a restaurant-hours directory.''',{'type':'breakfastByChain'},['Chain','Breakfast rows'],[[chain,sum(r['meal']['meal']=='breakfast' and r['meal']['chain']==chain for r in RECORDS)] for chain in counts])

bounded=[r for r in RECORDS if r['values']['f'] is None]
snapshot('exact-fiber-coverage-denominator','Which expansion records have an exact fiber figure?','A missing exact value belongs outside an exact-fiber average.','Calculate fiber completeness over real expansion rows and explain why bounds change the denominator.',f'''The expansion has {len(RECORDS)-len(bounded)} rows with a numeric fiber value and {len(bounded)} without an exact one. A reported less-than value can be useful evidence while still failing to supply a single number for a mean or minimum filter.

## Define the denominator

An exact-fiber average should use only compatible numeric entries and disclose how many rows it omits. Replacing a non-exact row with zero changes both the numerator and the meaning of the result. It converts uncertainty into a confident low-fiber measurement.

## The source bound still matters

Several Taco John’s entries publish fiber as less than 1 g. Some Raising Cane’s constructed orders combine components whose exact fiber is not established. The records keep those limits rather than inventing a total. A number can be unavailable for one operation while calories or protein remain fully usable.

## What the finder should do

For a minimum-fiber requirement, a row must actually verify the threshold. A non-exact value should not appear as a match just because another nutrient qualifies. If the interface lets you inspect a bounded item, it should show why an exact total is missing.

This snapshot is a completeness analysis, not a study of how much fiber people consume. It covers tracked orders rather than every ingredient or current menu option. The table names the affected chains so the limitation can be examined at its source.''',{'type':'fiberExactness'},['Chain','Numeric fiber','No exact fiber'],[[chain,sum(r['meal']['chain']==chain and r['values']['f'] is not None for r in RECORDS),sum(r['meal']['chain']==chain and r['values']['f'] is None for r in RECORDS)] for chain in counts])

snapshot('published-vs-calculated-restaurant-rows','Published and calculated orders need different labels','Two constructed Cane’s trays use a different verification route from published menu rows.','Audit published and component-calculated record methods with actual expansion counts.', '''A nutrition figure can come directly from a restaurant’s complete-order row or from adding its documented individual components. Both methods can be useful, but they are not the same evidence. The expansion identifies the method instead of presenting every total as restaurant-published.

## The calculated entries have explicit boundaries

Two Raising Cane’s selections add inspected individual portions. One is three fingers, fries, sauce and toast; the other is three fingers, toast and coleslaw. Neither includes a drink, and neither is claimed as the chain’s named combo total. The separate Chicken Sandwich is a published complete-order entry.

## A total inherits its weakest input

Calories and protein can be summed when every component has those fields. If fiber is published only as a bound for a relevant component, the constructed tray cannot acquire an exact fiber number. A complete calorie sum does not verify every other nutrient automatically.

## Why the label helps you

When you change an order, the calculation should name what changed and use compatible portion values. A source-defined combo with a drink choice is not interchangeable with a drink-free component sum. This transparency makes it possible to reproduce the total and notice missing pieces.

The table separates the two methods in the frozen expansion. It does not claim restaurant endorsement of our calculated selections or independent laboratory testing. Published values remain estimates of standard portions, and calculations remain dependent on them.''',{'type':'methods'},['Method','Rows'],[['Direct published orders',378],['Explicit component-calculated orders',2]])

if __name__=='__main__':write()
