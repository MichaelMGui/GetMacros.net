"""Additional original worked cases, authored separately from the shared shell."""
from author_batch_one import *

add('protein-cost-currency-comparison','Protein prices only compare when the currencies match','A lower-looking price can be more expensive after a unit or currency mismatch.','Food costs','Compare protein costs within a single currency and compatible tax scope.','Price ledger with per-protein-unit arithmetic and currency exclusion.', '''Use the same currency for both foods before comparing cost per gram of protein. A bare “$” is not enough to tell you whether two prices belong to the same market. Keep tax, discounts and the amount purchased explicit too.

## Compare one consistent example

Imagine two local products priced in the same fictional currency units. A costs 4.80 and provides 60 g package protein. B costs 5.40 and provides 90 g. A costs 0.08 per gram; B costs 0.06. B is more expensive at the checkout but cheaper per documented gram of protein.

## Do not compare across currencies blindly

If A is priced in one currency and B in another, those ratios are not directly comparable. A current exchange rate is needed, and a converted retail price may still describe different tax or delivery assumptions. GetMacros does not supply current exchange rates or guaranteed local prices.

## Keep the purchase decision wider than the ratio

The lower ratio does not account for taste, usable shelf life or whether you will use the whole pack. It also does not rank all nutrients. Package protein must come from matching edible weight and label values; container or discarded-food mass should not inflate it.

The example prices are invented. FDA’s serving explanation supports the protein basis; the cost divisions are original arithmetic. The protein-cost calculator can compare inputs you provide, but it cannot validate a store price, currency or promotion for you. Write those assumptions beside your result.''',src=(SERVE,),tool='protein-value-calculator.html',tool_label='Compare protein costs',checks=[['4.8/60',0.08],['5.4/90',0.06]])

add('two-for-one-protein-promotion','Does a two-for-one offer change the protein value?','Calculate the usable total and the actual checkout price.','Food costs','Evaluate a multi-pack promotion without treating free units as usable by default.','Promotion math with complete and partial-use cases.', '''A two-for-one offer can reduce cost per gram of protein if both packs are usable and the advertised checkout price is the one you actually pay. It does not double the protein in one portion. It doubles the purchased amount.

## Count both packs once

Suppose a fictional pack costs 6 currency units and contains 50 g total protein. One pack costs 0.12 per gram. Two identical packs for the same 6 units contain 100 g, giving 0.06 per gram if both are used. Do not divide the price by two and also double the denominator: that would apply the offer twice.

## What if only one pack gets used?

If the second pack is discarded, the usable protein remains 50 g. The effective price per used gram returns to 0.12. A discount can improve purchased-unit value without improving the value of what you actually eat.

## Read the offer conditions

Check eligible pack sizes, whether a loyalty price applies, and the actual checkout total. A buy-one-get-one offer is different from two smaller packs sold together. The label basis must also match both packs; a reformulated or different-flavor product may have another protein quantity.

All prices and label values in this example are fictional. FDA’s serving guide supports determining protein for the purchased edible amount. The calculator can compare your actual inputs, while the offer decision needs your current store conditions and realistic use plan. A low calculated ratio is not a reason to buy food you will not use.''',src=(SERVE,),tool='protein-value-calculator.html',tool_label='Check an offer with your own inputs',checks=[['6/50',0.12],['6/100',0.06]])

add('protein-value-after-fixed-delivery-fee','Delivery fees can reverse a protein-cost comparison','Include the costs that actually belong to the purchase.','Food costs','Compare two purchases when one has an unavoidable fixed fee.','Original fee-inclusive ranking reversal with a break-even calculation.', '''If delivery is necessary for one purchase, its cost belongs in that purchase comparison. Comparing only the food’s sticker price can produce the wrong ranking. If the fee is shared with other shopping, state how you allocate it rather than pretending the allocation is objective.

## A ranking that reverses

Imagine a local product costing 8 units for 80 g package protein. Its ratio is 0.10 per gram. An online product costs 7 for 100 g, or 0.07 before delivery. Add an unavoidable 5-unit delivery fee and the online purchase becomes 12 ÷ 100 = 0.12 per gram. The local option is now cheaper on that defined basis.

## Find the fee boundary

For the online ratio to equal 0.10, its total cost would be 10 units. Since the food costs 7, a fee of 3 gives a tie. Fees below 3 favor the online example; fees above 3 favor the local one, assuming all protein is used.

## Keep the scope practical

Tax, minimum-order requirements and subscriptions can add other costs. Do not count an entire delivery fee against one item without explaining that choice, and do not assume a subscription is free because you already pay for it.

These are invented shopping conditions, not current offers or a claim about any retailer. The protein amount must still come from compatible label portions. This original calculation extends the serving-based method into a transparent purchase decision. It is a comparison of specified costs, not an overall health score or a guarantee of value.''',src=(SERVE,),tool='protein-value-calculator.html',tool_label='Compare a defined total price',checks=[['8/80',0.1],['7/100',0.07],['12/100',0.12],['100*0.1-7',3]])

add('protein-value-usable-yield-break-even','How much usable food makes a cheaper pack worthwhile?','Find the yield where the price advantage disappears.','Food costs','Calculate break-even usable yield against another product.','Original algebraic yield threshold distinct from a generic food-waste comparison.', '''A lower purchase price per kilogram can stop being cheaper when the usable yield is lower. A break-even calculation tells you how much edible material you need to use for the comparison to hold. It does not establish that a particular food has that yield.

## Set a reference cost

Imagine Product A costs 10 units and provides 100 g usable protein. Its ratio is 0.10 per gram. Product B costs 8 and has 100 g protein before losses. To match A’s ratio, B needs 8 ÷ 0.10 = 80 g usable protein.

## Interpret the boundary

If B retains more than 80% of that assumed protein total, it is cheaper per used gram. At exactly 80%, the ratios tie. Below 80%, the lower checkout price no longer wins. This assumes losses have the same protein concentration as the portion being retained; selective discard can change that.

## Measure the right material

Bones, liquid, trimming and leftovers need compatible source definitions. A gross weight cannot be turned into edible protein with an unsupported percentage. Use an actual edible yield or label boundary when you have it, and keep uncertain yield as a sensitivity estimate.

The figures here are invented. NIST supports mass measurements and USDA’s documentation explains edible material descriptions. The algebra is original. Use it to identify what you need to know before buying, rather than presenting a hypothetical yield as a verified fact about the product. The protein-cost tool’s result is only as sound as those usable-amount inputs.''',src=(MASS,FOUND),tool='protein-value-calculator.html',tool_label='Compare protein with an explicit edible amount',checks=[['10/100',0.1],['8/0.1',80],['80/100*100',80]])

add('protein-cost-pack-size-minimum-spend','Cheaper protein per gram can require a larger cash outlay','Separate checkout affordability from unit value.','Food costs','Compare unit value under a fixed purchase budget.','Feasible-purchase ledger with an explicit budget constraint.', '''Cost per gram and the amount you can spend today are different constraints. A bulk pack can be cheaper per protein gram while costing more than your available budget. Neither result invalidates the other.

## Two invented options

A small pack costs 4 units for 40 g protein: 0.10 per gram. A bulk pack costs 18 for 240 g: 0.075 per gram. If your example checkout budget is 10 units, the bulk pack is unavailable within that constraint even though its unit ratio is lower.

## Do not call a fractional bulk pack purchasable

Dividing the bulk price by its serving count does not mean the retailer sells a single serving at that price. You must pay the pack total unless individual units are actually available. A tool can display a unit cost without guaranteeing a purchase option.

## Compare realistic alternatives

Two small packs cost 8 and provide 80 g protein in this example. That is a feasible purchase under the 10-unit constraint. Whether it is useful also depends on how much you need, storage and the food’s other qualities; buying the maximum possible amount is not the goal.

All prices and nutrition figures are invented. The FDA serving source supports converting the label basis into a package quantity. This guide’s original comparison separates two questions that a single cheapest-per-gram ranking can blur. Keep the pack total and unit ratio visible together so the result can inform a real shopping decision.''',src=(SERVE,),tool='protein-value-calculator.html',tool_label='Compare unit cost and pack totals',checks=[['4/40',0.1],['18/240',0.075],['4*2',8],['40*2',80]])

add('restaurant-protein-value-no-price-data','Can you rank restaurant protein value without prices?','Nutrition alone cannot establish cost per gram.','Food costs','Explain the evidence needed for a restaurant protein-value ranking.','Example showing identical nutrition but opposite price rankings under two price assumptions.', '''No. Protein grams and calories do not tell you what the order costs. A value ranking needs current, market-specific prices for the exact order, with a clear treatment of taxes and fees. Without that evidence, a nutrition ranking should stay a nutrition ranking.

## Why the missing price matters

Imagine two fictional orders with 30 g and 40 g protein. If both cost 10 units, their protein costs are about 0.33 and 0.25 per gram. If the second costs 16 instead, its ratio becomes 0.40. More protein wins in the first price scenario and loses in the second.

## Use the exact order

The source price must include the items whose nutrition you are counting. A standalone entrée’s price cannot represent a bowl plus paid add-ons. Delivery and local promotion prices may also differ from the restaurant counter price.

## Label a sensitivity example honestly

You can explore fictional prices to show how the arithmetic works, as above. Clearly separate those assumptions from a claimed restaurant offer. Do not publish the result as “best value” unless the underlying price coverage and comparison scope support that statement.

FDA’s menu-labeling resource explains the nutrition context; it does not provide prices. GetMacros’ protein-cost calculator accepts prices you supply. The finder’s nutrient records should never be treated as a verified price database. When a value question cannot be answered from the available evidence, the useful next step is to obtain the missing price, not to turn calories into a proxy for cost.''',src=(MENU,),tool='protein-value-calculator.html',tool_label='Calculate with a current price you supply',checks=[['10/30',0.3333333333333333],['10/40',0.25],['16/40',0.4]])

add('recipe-fixed-seasoning-scale','Scaling a recipe when one ingredient stays fixed','A double batch is not exactly double if the ingredient list changes.','Recipe arithmetic','Calculate a nonuniformly scaled recipe with a fixed component.','Original recipe ledger distinguishing variable and fixed components.', '''Double only the ingredients that actually double. If a fixed component stays at its original amount, the new recipe total is not simply twice the old total. Record the changed ingredient list first, then sum it.

## A fixed-component example

Imagine the main ingredients in a fictional recipe contribute 900 calories and a fixed seasoning mixture contributes 60. The original total is 960. A new batch uses double the main ingredients but the same seasoning amount, giving 1,800 + 60 = 1,860 calories. Multiplying the old total by two would give 1,920 and overstate this example by 60.

## Portion count is a separate step

If the new batch is divided into six uniform portions, each has 310 calories under the stated assumptions. The number of portions should describe the new batch, not automatically retain the original recipe’s serving count.

## Apply the method to every known nutrient

The fixed seasoning may contribute sodium, carbohydrate or other supported nutrients. Keep those component figures and multipliers separate too. A missing ingredient value remains missing; it does not become known because the rest of the recipe scales cleanly.

This is invented arithmetic, not a kitchen-tested recipe or a recommendation to double food intake. FDA supports the serving-based ingredient inputs and NIST supports measured amounts. The recipe tool can divide a supported batch total once you have built that total correctly. It cannot infer an ingredient-specific exception from a single “double recipe” instruction.''',src=(SERVE,KITCHEN),tool='recipe-macro-scaler.html',tool_label='Divide a documented batch total',checks=[['900+60',960],['900*2+60',1860],['960*2-1860',60],['1860/6',310]])

add('recipe-one-ingredient-substitution','Recalculate a recipe after changing one ingredient','Subtract the old component and add the new one.','Recipe arithmetic','Update batch nutrition for one documented ingredient replacement.','Original subtraction/addition ledger with equal amount and different basis cautions.', '''For a documented replacement, start with the original batch total, subtract the old ingredient’s contribution and add the new one’s. Changing a name in the recipe without changing the numbers leaves the original ingredient in the calculation.

## Update an invented batch

Suppose a fictional batch totals 1,500 calories and 75 g protein. Its original ingredient contributes 300 calories and 10 g protein. The replacement, at the actual included amount, contributes 220 calories and 18 g protein. The new batch is 1,420 calories and 83 g protein.

## Recompute the portion

If it is still divided into five uniform portions, each has 284 calories and 16.6 g protein. If the replacement changes the total cooked weight, an old per-gram density no longer applies. Use the new measured batch mass for weight-based portions.

## A substitution needs evidence

The replacement’s nutrition must come from its own matching label or database entry. Equal ingredient weights do not imply equal nutrients. A restaurant substitution also needs official support; this method does not certify that the restaurant offers it or that a generic ingredient profile matches it.

FDA’s serving explanation and USDA’s food-identity documentation support the inputs. The values here are invented. The calculation is an original worked example, not a tested recipe. Record the original component, replacement amount and source basis so another person can audit precisely what changed.''',src=(SERVE,FOUND),tool='recipe-macro-scaler.html',tool_label='Scale the updated recipe total',checks=[['1500-300+220',1420],['75-10+18',83],['1420/5',284],['83/5',16.6]])

add('recipe-sauce-on-side-two-totals','Recipe with sauce on the side: keep two totals','A separate sauce is useful only if its portion stays visible.','Recipe arithmetic','Calculate optional sauce separately from a base recipe.','Base/sauce ledger avoids assuming all or none of an optional addition.', '''Keep the base recipe and optional sauce as separate quantities. Then the portion calculation can reflect how much sauce is actually added. A single combined batch total assumes the whole sauce amount is included and distributed with the base.

## A two-part example

Imagine a fictional four-portion base containing 1,200 calories and 80 g protein. Each base portion has 300 calories and 20 g protein. A separate 100 g sauce batch contributes 200 calories. Adding 15 g of that uniform sauce contributes 30 calories, giving 330 for that particular plate.

## Protein needs its own sauce value

The sauce’s calories do not establish its protein content. If protein is unavailable, keep the final plate’s complete protein amount unknown while showing the base’s 20 g subtotal. If the source supplies 0 g protein, that documented figure can be used.

## Do not reuse a sauce volume as mass

A tablespoon or milliliter amount does not automatically weigh 15 g. Use the product’s stated mass conversion or a measured mass. A separate sauce can make a recipe easier to portion, but it does not remove the need for compatible units.

FDA and NIST support the serving and unit distinctions. These are invented figures, not a tested recipe or a restaurant dressing instruction. The practical result is a base total you can reuse and an addition that stays explicit, instead of treating every plate as though it received exactly one-quarter of the whole sauce batch.''',src=(SERVE,VOL),tool='recipe-macro-scaler.html',tool_label='Calculate the base portions',checks=[['1200/4',300],['80/4',20],['15/100*200',30],['300+30',330]])

add('recipe-evaporation-weight-density','When water evaporates, recipe calories per gram can change','Batch totals and batch density are different quantities.','Recipe arithmetic','Understand a changed cooked yield without inventing nutrient loss.', 'Original fixed-nutrient-total model distinguishes mass loss from measured composition change.', '''A smaller final weight can make the same assumed nutrient total more concentrated per gram. That does not prove that cooking created calories. It means your portion calculation needs the final measured batch weight, with the model’s limitations stated.

## Hold one assumption constant

Imagine a fictional batch with a calculated total of 1,200 calories. Before a water-only loss it weighs 1,000 g; afterward it weighs 800 g. Under the explicit assumption that the counted nutrients remain in the batch, density changes from 1.2 to 1.5 calories per gram.

## A 200 g portion changes meaning

At 1,000 g yield, a 200 g portion is one-fifth of the batch and calculates to 240 calories. At 800 g yield, it is one-quarter and calculates to 300. The portion mass stayed the same, but its fraction of the batch changed.

## Do not overextend the water-only model

Draining fat, discarding cooking liquid or leaving food on the pan may remove more than water. Ingredient totals then may not represent the retained cooked batch exactly. A yield measurement by itself cannot identify which nutrients were lost.

USDA’s food-description documentation and NIST’s measurement resources support using compatible food states and measured amounts. The original numbers here illustrate a fixed-total model; they are not cooking-loss data for a real recipe. State that assumption if you use the method, and avoid presenting the result as laboratory-verified nutrition.''',src=(FOUND,KITCHEN),tool='recipe-macro-scaler.html',tool_label='Divide the final batch by portion',checks=[['1200/1000',1.2],['1200/800',1.5],['1200*200/1000',240],['1200*200/800',300]])

add('recipe-left-in-pan-residual','Food left in the pan: what can you subtract from the recipe?','A leftover weight needs a composition assumption before it becomes a nutrient subtraction.','Recipe arithmetic','Handle retained residue without equating any lost gram with the average recipe.', 'Original residual example distinguishes uniform leftovers from separated oil or solids.', '''You can subtract a measured leftover portion proportionally only when its composition is reasonably represented by the batch average. Residue that is mostly oil, sauce or a particular ingredient may not have that average composition.

## The uniform-leftover model

Imagine a fictional fully mixed batch weighing 1,000 g with 1,500 calculated calories. If 100 g of the same uniform mixture remains uneaten, that portion represents 150 calories under the model. The remaining 900 g accounts for 1,350.

## When the model fails

A pan with mostly separated cooking oil is not the same mixture as the completed food. Multiplying its weight by average batch density can misstate what was removed. You need a supported component amount or a clearly stated uncertainty, not a guess justified by a convenient total.

## Keep served and eaten records distinct

The batch recipe total describes what was prepared under its ingredient assumptions. The served total describes what was portioned onto plates. The eaten amount may differ again. For a household recipe, do not claim all three were directly measured if only ingredient weights were recorded.

The example is original arithmetic with invented quantities. FDA supports the portion basis and USDA supports matching material descriptions. A transparent estimate can be useful without claiming exact intake. If the residue composition is unknown, preserve that limitation instead of forcing the numbers to reconcile to a falsely precise consumed total.''',src=(FOUND,SERVE),tool='recipe-macro-scaler.html',tool_label='Work with a supported recipe total',checks=[['1500/1000*100',150],['1500-150',1350]])

add('recipe-uniform-vs-component-serving','A stew and a plated meal need different portion calculations','Uniform batch division cannot replace separate component amounts.','Recipe arithmetic','Choose uniform-batch or separate-component portion methods.','Worked plate decomposition contrasts proportional division with measured components.', '''Use batch division for a genuinely mixed recipe when the portion assumption is appropriate. For a plate assembled from separate foods, calculate each component at its own amount. Equal plate weights can conceal very different compositions.

## Compare two methods

Imagine a fictional mixed batch with 1,600 calories across 800 g. A 200 g uniform portion gives 400 calories. Now imagine a separate plate with 120 g Component A at 1.5 calories per gram and 80 g Component B at 3. The plate also weighs 200 g, but its calculated total is 180 + 240 = 420 calories.

## The same weight is not the same meal

Borrowing the mixed batch’s 2-calorie-per-gram average for the separate plate would produce 400 and miss the defined component calculation. Another distribution of A and B could produce another total while retaining the same plate weight.

## Record what you can actually identify

A single total plate weight does not reveal its ingredient split. Measure components or use a supported complete-dish source. For a restaurant order, rely on the restaurant’s defined standard build where available rather than estimating its composition from a photo.

NIST supports compatible kitchen measurements and USDA documents the importance of food descriptions. All figures above are invented. The distinction is a calculation choice, not a judgment about which meal is preferable. Choose the method that matches the food and evidence, then keep its assumptions beside the result.''',src=(FOUND,KITCHEN),tool='recipe-macro-scaler.html',tool_label='Divide a mixed recipe',checks=[['1600/800*200',400],['120*1.5',180],['80*3',240],['180+240',420]])

add('recipe-discrete-pieces-count-or-weight','Counted pieces or gram portions: choose one clear recipe basis','A piece count works only when the pieces are sufficiently comparable.','Recipe arithmetic','Allocate recipe nutrition among countable pieces with unequal size boundaries.','Original muffin-style yield calculation contrasted with weighed piece calculation.', '''A recipe’s “per piece” figure divides the batch by its piece count. It is an average when the pieces differ in size. A weighed portion uses a different assumption: that nutrient distribution follows the measured mass.

## An invented twelve-piece batch

Suppose a fictional batch totals 2,400 calories and produces twelve pieces. Its average is 200 calories per piece. If the finished batch weighs 900 g, its calculated average density is about 2.67 calories per gram. A 90 g piece calculates to 240 under a uniform-composition model.

## Why the numbers differ

Twelve pieces need not each weigh 75 g. The larger 90 g piece exceeds the average mass, so its proportional estimate is larger than the count average. That does not establish an exact laboratory amount in that piece; uneven fillings or toppings can change the composition.

## Keep the recipe description honest

Write “average per piece, twelve pieces” for count division. Write “estimated 90 g piece from the measured batch” for proportional division. Do not publish the count-based average as though each individually shaped piece has identical nutrition.

This example has not been kitchen-tested and does not describe a real muffin or food product. FDA’s portion guidance and NIST’s measurement references support the two inputs. The recipe tool can divide a documented batch into an entered count, but it cannot make irregular pieces equal by labeling them servings.''',src=(SERVE,KITCHEN),tool='recipe-macro-scaler.html',tool_label='Calculate a count-based average',checks=[['2400/12',200],['2400/900*90',240]])

add('recipe-quarter-batch-not-quarter-ingredient','A quarter of the batch is not a quarter of one ingredient','Keep the portion fraction attached to the correct total.','Recipe arithmetic','Avoid applying a recipe portion fraction to only one component.','Three-ingredient batch example with a diagnostic incorrect calculation.', '''The fraction of a complete mixed batch applies to the complete batch total. Multiplying only one ingredient by that fraction omits the others. First build the recipe, then divide the recipe.

## Sum before splitting

Imagine three fictional ingredients contributing 400, 600 and 200 calories. The complete batch is 1,200. One-quarter of a uniform batch gives 300 calories. One-quarter of the 600-calorie ingredient gives 150, but that represents only its contribution to that portion—not the whole portion.

## Keep a component check

The quarter-batch contributions are 100, 150 and 50 calories. Their sum is 300, which matches quartering the full batch. This provides a useful audit: if your component method and total method disagree, check the included amounts and multipliers.

## When separate portions matter

If the foods are plated separately or distributed unevenly, the quarter-batch assumption may not fit. In that case, calculate the actual component amounts on the plate instead. The simple fraction is not permission to assume an even distribution that did not occur.

All values above are invented. FDA supports scaling documented serving quantities, while the calculation is original arithmetic. The recipe tool expects a batch total, not one highlighted ingredient’s value. Keep that input label clear in your notes so an attractive per-serving result does not hide an incomplete recipe.''',src=(SERVE,),tool='recipe-macro-scaler.html',tool_label='Divide the complete batch',checks=[['400+600+200',1200],['1200/4',300],['600/4',150],['100+150+50',300]])

add('recipe-added-water-not-new-nutrients','Adding water changes recipe weight, not the counted ingredient totals','Recalculate portion density after measuring the new yield.','Recipe arithmetic','Model added water in a fixed-nutrient recipe without misusing an old density.', 'Original water-addition model and equal-weight portion comparison.', '''In a model where only water is added and no counted ingredients are lost, the calculated batch nutrient totals stay the same while its mass increases. A gram portion then represents a smaller fraction of the batch. Keep the water-only assumption explicit.

## A diluted-batch example

Imagine a fictional sauce with 600 calculated calories in 300 g. Adding 200 g water makes 500 g total, assuming complete mixing and no loss. The modeled density changes from 2 to 1.2 calories per gram. The batch still totals 600.

## Compare a chosen mass

A 50 g portion of the original calculates to 100 calories. A 50 g portion of the diluted batch calculates to 60. Those portions do not contain the same amount of the original mixture. A 50 g original-equivalent amount would require about 83.3 g of the new mixture under this model.

## Check what was actually added

Milk, stock or another liquid may carry nutrients. They cannot automatically use the water-only assumption. Add their documented contributions, then measure the new batch. Likewise, if some sauce stays in the blender, an exact no-loss model may not describe the retained mixture.

The numbers are invented and the sauce was not kitchen-tested. NIST supports mass measurements; FDA supports serving-based ingredient calculations. The original worked example explains why an old per-gram estimate should not be copied after dilution. It does not imply that diluting food is a required dietary strategy.''',src=(MASS,SERVE),tool='recipe-macro-scaler.html',tool_label='Scale the measured final batch',checks=[['600/300',2],['600/500',1.2],['50*2',100],['50*1.2',60],['100/1.2',83.33333333333334]])

add('recipe-freezing-portion-count','Freezing a batch does not decide its serving count','Use measured containers and a consistent recipe basis.','Recipe arithmetic','Organize frozen recipe portions without treating container count as equal weight.','Original container ledger with unequal fills and known batch fractions.', '''The number of containers tells you how many containers you filled. It does not prove that they contain equal food amounts. For a uniform mixed batch, measured portions can produce a more transparent estimate than assuming every container is identical.

## A four-container example

Imagine a fictional uniform batch weighing 1,200 g with 1,800 calculated calories. Four equal 300 g portions would each calculate to 450. If the actual fills are 250, 300, 300 and 350 g, the modeled totals are 375, 450, 450 and 525. They still sum to 1,800.

## Label the basis before storage

Write the portion mass and the batch reference rather than just “one serving.” If you later combine two portions or leave some uneaten, the original container count should not dictate the new amount. Container mass itself must be excluded from the food weight.

## Keep food handling separate

This arithmetic does not establish how long a particular dish can be safely frozen or how it should be reheated. Follow appropriate food-safety guidance for the actual food. A neat nutrition label on a container is not a safety verification.

NIST supports the measurement method and FDA supports using the portion basis consistently. These figures are invented and no recipe or storage procedure was tested. The recipe tool can give an average serving estimate, while a weighed portion ledger makes unequal fills visible instead of hiding them behind an equal-container assumption.''',src=(KITCHEN,SERVE),tool='recipe-macro-scaler.html',tool_label='Work out the batch’s average portion',checks=[['1800/1200*250',375],['1800/1200*300',450],['1800/1200*350',525],['375+450+450+525',1800]])

add('calculator-positive-inputs-zero-nutrition','A zero nutrient value is different from a zero serving weight','Some zeros are valid data; others make a calculation undefined.','Calculator notes','Distinguish zero nutrient inputs from invalid denominator inputs.','Boundary-case examples using sodium, label scaling and protein-value division.', '''A label can legitimately supply zero for a nutrient under its reporting convention. A serving weight of zero cannot provide a useful denominator for portion scaling. Validate what the field represents, not merely whether the entered number is zero.

## A valid zero

If a source lists 0 mg sodium per 100 g, scaling that published value to 50 g still gives a published-value calculation of 0. The source’s rounding or measurement limits remain relevant. Do not turn the zero into missing data just because other values are positive.

## An invalid denominator

An entered label basis of 0 g would require dividing by zero. The calculator should ask for a positive serving amount instead of returning infinity or silently substituting 100 g. Similarly, a protein-cost ratio with 0 g total protein has no finite cost per protein gram.

## Missing data is a third state

A blank field is not zero. If the sodium figure is unavailable, the portion’s sodium result should stay unavailable. Filling the blank with zero may produce a tidy output while changing the meaning of the source.

FDA’s serving guidance and USDA’s data documentation support these distinctions. The examples above explain validation behavior, not a claim that any named food is nutrient-free. In a good tool, the error appears beside the relevant field and explains what to enter. Correct numerical boundaries are part of the user experience, not an obstacle to a prettier result.''',src=(SERVE,FOUND),tool='nutrition-label-comparison-tool.html',tool_label='Try a supported label comparison',scope='No real food is assigned zero. This article explains calculator boundary cases and source-status handling.')

add('calculator-round-at-end','Why a calculator should round at the end','Small intermediate changes can add up across several portions.','Calculator notes','Avoid compounded rounding error during portion calculations.','Original repeating-decimal example with exact total reconciliation.', '''Keep working precision through the calculation and round the final display. Rounding every intermediate value can create a total that differs from the same calculation performed directly. More digits should still not imply that the source nutrition is exact.

## A repeating-decimal example

Imagine a fictional 900-calorie batch split into seven equal portions. The calculated value is about 128.571 calories each. Rounding each to 129 and then multiplying by seven gives 903. That does not mean the batch gained three calories.

## Separate display from arithmetic

The interface can display approximately 129 calories per portion while retaining the unrounded division internally. If it reports the whole batch, it should use the original 900 rather than adding rounded display values. The same principle applies to protein, price ratios and unit conversions.

## Know the input’s limits

The source label may already be rounded, and the recipe may have uneven nutrient distribution. Carrying more digits through arithmetic prevents an additional calculation error; it does not remove those uncertainties. A sensible display can use “about” where a rounded estimate is being presented.

The FDA serving and label guidance supplies the input context. The seven-portion example is invented arithmetic. When two displayed totals do not reconcile exactly, first check intermediate rounding and serving definitions before assuming the source is wrong. A reliable calculator preserves the difference between a clean display and the quantities used to calculate it.''',src=(FDA,),tool='recipe-macro-scaler.html',tool_label='Calculate a batch serving',checks=[['900/7',128.57142857142858],['129*7',903]])

add('calculator-activity-choice-sensitivity','Activity choices can change an estimate more than decimal places','Use the activity description honestly instead of chasing a precise-looking result.','Calculator notes','Interpret sensitivity to activity-factor inputs without prescribing intake.','Abstract factor comparison separates input assumptions from apparent precision.', '''An activity selection is an assumption in a daily energy estimate. A precise-looking output does not make that assumption exact. Choose the description that best fits the tool’s intended use and interpret the result as an estimate.

## Isolate one input

Imagine an abstract base value of 1,500 energy units. Applying example factors of 1.3 and 1.5 gives 1,950 and 2,250. The 300-unit difference comes entirely from the chosen factor. Reporting either result to two decimal places would not resolve which factor is appropriate.

## Avoid counting the same activity twice

If a tool’s factor already includes regular activity, adding another independent exercise estimate may overlap with it. Read the calculator’s method before combining outputs from different tools. Two estimates are not automatically complementary simply because they use different interfaces.

## Observe rather than overpromise

An equation-based result is a starting estimate, not a guarantee of a particular outcome. Changing body measurements, recording habits and the model’s limitations can affect interpretation. This guide does not instruct you to select a particular factor or set a personal calorie target.

FDA’s calories guide notes that energy needs vary; the arithmetic here is a deliberately abstract sensitivity example, not a worked prescription. Use the calculator’s existing explained method and leave personal inputs out of shared links. A useful explanation of uncertainty is more trustworthy than a result displayed with needless precision.''',src=(CAL,),tool='calculators.html',tool_label='Read the macro calculator’s inputs',checks=[['1500*1.3',1950],['1500*1.5',2250],['2250-1950',300]])

add('calculator-pound-kilogram-entry','Pounds and kilograms: change the unit, not just the number','A wrong unit selection can overwhelm the rest of a calculator’s inputs.','Calculator notes','Check body-mass unit consistency before a nutrition estimate.','Unit-conversion audit with no personal calorie prescription.', '''A number needs its unit. Entering a pounds figure into a kilograms field does not convert it. The calculator then interprets a very different mass, even if the remaining inputs are correct.

## Check the order of operations

Select the unit first, then enter the amount. If the tool converts an existing value when you switch units, read the new displayed number instead of replacing it with the old one. The same physical mass should stay represented after a unit change.

## A simple test case

Using the conversion factor 2.2046226218 pounds per kilogram, an example 70 kg mass is approximately 154.32 lb. The unit switch should preserve that relationship within the tool’s display precision. Entering 154.32 as kilograms would be a separate input, not another way of writing 70 kg.

## Look for a clear validation message

A tool should display its selected unit beside the field and use reasonable validation. It cannot always tell whether a plausible-looking number was copied from the wrong unit system. You remain responsible for checking the source measurement.

NIST’s mass resources support consistent unit treatment; this is a numerical test example, not a statement about a person or a recommended body mass. Correct conversion preserves the underlying calculator’s method. It does not establish that an energy estimate is individually exact or that a particular body target is appropriate.''',src=(MASS,),tool='calculators.html',tool_label='Check the calculator’s unit selector',checks=[['70*2.2046226218',154.323583526]])

add('calculator-estimate-not-shared-personal-input','Share a meal choice without sharing personal calculator inputs','The useful result and the inputs that produced it can stay separate.','Calculator notes','Understand privacy boundaries when moving from a personal calculation to a meal search.','A practical sharing checklist with explicit exclusion of personal fields.', '''A meal-search link can describe restaurant preferences and supported nutrient filters without exposing the personal measurements used in a daily calculator. Those are separate parts of the product. Sharing the useful next step does not require sharing every preceding input.

## Decide what the recipient needs

For a lunch comparison, the useful information is the exact order, portions, nutrient figures and the selected search constraints. Age, body mass, height and other calculator inputs do not help another person verify that restaurant order’s published nutrition.

## Inspect a share link before sending

Look for restaurant and filter parameters. Do not copy private form values into a URL, caption or screenshot without intending to share them. A screenshot can reveal more than the share control if the calculator form remains visible.

## Keep estimates in context

If you mention a daily estimate, describe it as an estimate rather than a recommendation for the recipient. Their circumstances can differ. A meal finder filter is also a user preference, not a medical prescription.

FDA’s calories source supports the fact that calorie needs vary. The privacy guidance here is a product-use workflow, not a new legal promise about external platforms. Read GetMacros’ privacy page for the site’s actual storage and integration behavior. A well-designed handoff retains the meal decision and its evidence while leaving unrelated personal inputs out of the shared state.''',src=(CAL,),tool='privacy.html',tool_label='Read GetMacros privacy information',scope='This article explains a sharing workflow. It does not assert privacy guarantees for third-party services or change the site privacy policy.')

add('calculator-input-basis-checklist','Before calculating: five checks on the nutrition input','A correct formula cannot repair a mismatched source.','Calculator notes','Audit label basis, material state, unit, included amount and status before calculation.','A five-part troubleshooting sequence applied to one concrete input scenario.', '''Before trusting a result, check what went into the formula. A calculation can be mathematically correct and still answer the wrong food question. The most useful checks concern identity and measurement rather than how attractive the output looks.

## Start with the source basis

Imagine you weighed 75 g of a food, but the label lists values per 50 g. The multiplier is 1.5. Confirm that 75 is the edible food amount, not container-plus-food weight. Confirm that the weighed food is in the preparation state described by the source.

## Read every unit

Calories, protein grams and sodium milligrams belong in different fields. A per-100-mL liquid panel cannot be scaled from a gram reading without a product-specific relationship. A percentage is not a gram amount.

## Check what is included

A base recipe and optional sauce may have separate totals. A restaurant entry may exclude a side or drink. Make your intended calculation match those boundaries rather than filling a gap with a guessed component.

## Keep source status visible

A blank is unavailable. A source-supplied zero has a different meaning. Use current product information and retain the source date where available. FDA’s serving guidance, NIST’s unit references and USDA’s food descriptions support these checks. The 75 g example is invented. If the input basis fails a check, correct that before rerunning the tool; changing the formula cannot turn mismatched evidence into a reliable meal estimate.''',src=(SERVE,MASS,FOUND),checks=[['75/50',1.5]])

add('calorie-tool-output-reverse-check','Reverse-check a portion calculator before trusting its output','A simple inverse calculation can reveal a wrong multiplier.','Calculator notes','Verify a scaled nutrition result using the original input basis.','Original forward/inverse arithmetic and error diagnosis.', '''After scaling a label, work backward once. If the displayed result cannot recover the original value under the same assumptions, check the serving basis, units and rounding. This is a calculation audit, not independent verification of the label.

## A forward calculation

Imagine a fictional product with 180 calories per 60 g. You enter a 90 g portion. The multiplier is 1.5, so the expected result is 270 calories. Reverse-check by dividing 270 by 1.5: it returns 180.

## Find a common mistake

If the tool result is 162, someone may have multiplied by 90 ÷ 100 instead of 90 ÷ 60. The 100 g basis was never in the source. A familiar-looking per-100 figure is not a substitute for reading the actual panel.

## Allow for display precision

A result rounded to whole calories may not reverse exactly. Inspect the unrounded operation rather than rejecting a sound method over a tiny display difference. Conversely, a large difference should not be dismissed as rounding.

FDA’s serving source supports using the stated label amount. All figures here are invented. The inverse check verifies that a chosen transformation is internally consistent; it cannot prove that the original product label is current or that a mixed portion was uniform. Save the source basis alongside the output so the calculation remains auditable.''',src=(SERVE,),checks=[['180/60*90',270],['270/1.5',180],['180*90/100',162]])

add('restaurant-compare-tradeoff-not-single-score','Two meals can trade places when your priority changes','Calories and protein do not produce one universal winner.','Lunch and dinner','Explain multidimensional ranking without a fabricated fit score.','Original two-order trade-off analysis retaining both coordinates.', '''A meal comparison does not need one overall score. Put the values that matter beside each other and identify the trade-off. A higher protein amount and a lower calorie amount can point toward different orders.

## Two invented choices

Order A has 450 calories and 25 g protein. Order B has 600 calories and 40 g protein. A has 150 fewer calories; B has 15 g more protein. Neither dominates the other on both quantities. The choice depends on the question you are asking and the portion you want.

## A ratio does not erase the trade-off

Protein per 100 calories is about 5.6 g for A and 6.7 g for B. B leads that ratio, yet it still has more total calories. A ratio is another view, not a verdict that the meal is best for everyone.

## Keep the complete order attached

Compare the included sides, sauces and drinks as well as the headline values. A ranking based on a standalone entrée should not be presented as a complete combo comparison. Keep unavailable nutrients visible rather than giving the incompletely documented order a falsely low total.

FDA’s serving and menu resources support checking the declared basis. The figures here are fictional and do not establish a personal target. GetMacros can sort real supported records by a chosen quantity. It should not convert those simple rankings into a made-up percentage of perfection or a promise about an individual health outcome.''',src=(MENU,SERVE),tool='restaurant-meal-finder.html',tool_label='Compare meals by your selected priority',checks=[['600-450',150],['40-25',15],['25/450*100',5.555555555555555],['40/600*100',6.666666666666667]])

add('restaurant-dominated-choice-still-context','When one order beats another on two numbers','A numerical advantage is useful—but it still has a defined scope.','Lunch and dinner','Interpret Pareto dominance on supported meal attributes without a health ranking.','Three-order example explains dominance versus a remaining trade-off.', '''If one order has no more calories and no less protein than another, it has a numerical advantage on those two chosen dimensions. That can simplify a comparison. It does not establish an overall health ranking, allergy suitability or personal preference.

## An invented comparison

Order A has 500 calories and 30 g protein. B has 550 and 25 g. A has 50 fewer calories and 5 g more protein, so it leads on both stated measures. C has 650 and 45 g: it trades more calories for more protein, so it does not fit the same simple dominance relationship with A.

## Define the measures before ranking

This analysis applies only if lower calories and higher protein are the chosen criteria. If your priority is a larger meal, flavor, price or sodium, the comparison needs different evidence. Do not describe the lower-calorie option as inherently better.

## Missing attributes remain relevant

If sodium is unavailable for A, the two-number comparison does not answer a sodium-limit question. A stronger-looking protein and calorie pair cannot certify a missing nutrient. Likewise, an ingredient description cannot establish dietary or allergen suitability.

The FDA menu and serving sources support compatible portion evidence. These fictional orders provide an original decision model. For actual restaurant use, keep the exact order and serving assumptions beside the numerical comparison. Removing an option from a particular two-attribute shortlist is different from judging whether someone should eat it.''',src=(MENU,SERVE),tool='restaurant-meal-finder.html',tool_label='Inspect supported order attributes',checks=[['550-500',50],['30-25',5]])

add('meal-filters-intersection-not-extra-options','Why adding a filter can reduce your meal matches','Every explicit condition must be satisfied by the same order.','Lunch and dinner','Explain intersection of strict supported constraints with an original example.','Three-order truth table with an empty-intersection explanation.', '''Adding a strict filter keeps only meals that satisfy the new condition as well as the existing ones. It does not add a second pool of options. One meal must meet all the explicit limits together.

## A three-order example

Imagine A has 450 calories and 20 g protein; B has 600 and 35 g; C has 520 and 28 g. A maximum of 550 calories keeps A and C. A minimum of 25 g protein keeps B and C. Applying both conditions together keeps only C.

## Why a no-match state is legitimate

If you reduce the calorie maximum to 500 while retaining that protein minimum, none of these examples matches. Silently ignoring one condition would make the page seem helpful while violating the search you asked for.

## Change one condition deliberately

Review the active filter summary. Clear or edit a limit explicitly, then compare the new count. A useful interface should show which controls are active and offer a clear reset without modifying them on your behalf.

FDA’s menu and serving guidance supports the nutrition inputs, while the filtering logic is original product arithmetic. The fictional thresholds are not recommendations for your lunch. GetMacros should preserve explicit preferences through a quiz, direct browsing and shared link, with unknown required values kept out of strict-limit certification rather than treated as zero.''',src=(MENU,SERVE),tool='restaurant-meal-finder.html',tool_label='Try supported meal filters',checks=[])

add('restaurant-search-result-count-scope','A result count is coverage, not the whole restaurant menu','Know what the database includes before interpreting a shortlist.','Nutrition data','Interpret meal-finder counts as dataset-limited matches, not menu exhaustiveness.','Scope checklist distinguishes tracked, eligible, matching and displayed counts.', '''A meal finder counts records it can search, not every order a restaurant could prepare. The result count is useful when its scope is clear. “No matches” in a tracked dataset does not prove that no suitable meal exists anywhere on the current menu.

## Four counts can differ

The tracked count describes records in the dataset. The eligible count may exclude entries missing essential filter data. The matching count applies your active choices. The displayed count may show only the first page or batch. A “show more” action should change the display without inventing additional matches.

## A simple example

Imagine a dataset of 20 records, two lacking the necessary protein data. Eighteen are eligible for a supported protein search. Five satisfy your active limits, but the first display shows three. The useful label is “5 matches” with three currently visible—not “20 meals for you.”

## Coverage limits deserve a real next step

If your chosen chain has few tracked orders, use its official nutrition information for other menu options. Do not relax your limits automatically just to increase the count, and do not describe missing entries as unavailable to purchase.

FDA’s menu information supplies the source context; the example counts are invented. GetMacros should report actual dataset-derived counts and keep pagination separate from match logic. A modest, clearly scoped collection is more trustworthy than a large-looking number that confuses ingredients, duplicate portions and complete orders.''',src=(MENU,),tool='sources.html',tool_label='Read dataset coverage and limitations',checks=[['20-2',18]])

add('same-restaurant-name-different-market-data','The same restaurant name does not mean the same nutrition worldwide','Use the market attached to the source record.','Eating out','Avoid transferring U.S. nutrient values to another market by brand name.','Evidence checklist for market, standard build and source date.', '''Use the nutrition information for the market where you are ordering. A familiar restaurant name does not make portion sizes, standard ingredients or nutrient figures globally interchangeable. GetMacros’ U.S. records should remain labeled as U.S. data.

## Match the record before comparing

Look for the country or region, the exact item name, serving size and included components. A similar menu title in another country may describe another build. Copying its calories into the U.S. record would hide that difference rather than resolve it.

## Source dates matter too

A newer page from another market is not automatically a better source for the old market. Check that the menu version and geographic scope both match. If a source does not state a publication date, keep that date unavailable and record when you consulted it separately.

## What to do when the market is unsupported

Use the restaurant’s local official information for your order. You can compare those documented values yourself, but do not assume a GetMacros shortlist certifies the local meal. A shared filter link should retain its underlying dataset scope rather than suggesting worldwide coverage.

FDA’s menu-labeling guidance is U.S.-specific context, not a global menu standard. This article introduces no cross-market nutrition claims and quotes no restaurant values. The practical rule is to keep brand, market and serving together whenever a number travels from a source to a result.''',src=(MENU,),tool='restaurant-meal-guides.html',tool_label='Browse the supported U.S. restaurant guides',scope='GetMacros currently labels this dataset as U.S. restaurant information. This article does not claim coverage or equivalence in other markets.')

if __name__=='__main__':write()
