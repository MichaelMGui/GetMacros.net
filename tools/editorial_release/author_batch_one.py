"""Individually authored practical articles. Examples are invented, not food data."""
import json, re
from pathlib import Path
from html import escape
D=Path(__file__).resolve().parent
FDA='https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label'
SERVE='https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label'
DV='https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels'
SUGAR='https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label'
SODIUM='https://www.fda.gov/food/nutrition-education-resources-materials/sodium-your-diet'
MENU='https://www.fda.gov/food/food-labeling-nutrition/menu-labeling-requirements'
MASS='https://www.nist.gov/pml/owm/si-units-mass'
VOL='https://www.nist.gov/pml/owm/si-units-volume'
KITCHEN='https://www.nist.gov/pml/owm/metric-si/metric-kitchen'
FDC='https://fdc.nal.usda.gov/data-documentation/'
FOUND='https://fdc.nal.usda.gov/Foundation_Foods_Documentation/'
ALLERGY='https://www.fda.gov/food/buy-store-serve-safe-food/food-allergies-what-you-need-know'
CAL='https://www.fda.gov/food/nutrition-facts-label/calories-nutrition-facts-label'
source_info={FDA:('FDA: using a Nutrition Facts label','Label quantities refer to the stated serving; nutrients are not interchangeable.'),SERVE:('FDA: serving information','Serving sizes and household/metric units on U.S. labels.'),DV:('FDA: Daily Values','Percent Daily Value is a reference comparison, not a personalised target.'),SUGAR:('FDA: added sugars','Added sugars are part of total sugars, not an additional amount to add.'),SODIUM:('FDA: sodium','Sodium units and the distinction between sodium and salt.'),MENU:('FDA: menu labeling','Written nutrition information and menu-labeling scope.'),MASS:('NIST: units of mass','Gram, milligram and kilogram relationships.'),VOL:('NIST: units of volume','Volume quantities and their distinction from mass.'),KITCHEN:('NIST: Metric Kitchen','Using appropriate kitchen measurements.'),FDC:('USDA: FoodData Central documentation','Food-data types have different sources and purposes.'),FOUND:('USDA: Foundation Foods documentation','Food descriptions, portions, missing nutrients and sample variation.'),ALLERGY:('FDA: food allergies','Ingredient/allergen information requires attention beyond nutrient totals.'),CAL:('FDA: calories on the label','Calories describe energy for the listed amount.')}
rows=[]
def table(caption,heads,values):
 return '<div class="table-wrap"><table><caption>'+escape(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+escape(str(x))+'</th>' for x in heads)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+escape(str(x))+'</td>' for x in r)+'</tr>' for r in values)+'</tbody></table></div>'
def prose(value):
 out=[]
 for block in value.strip().split('\n\n'):
  if block.startswith('## '):out.append('<h2>'+escape(block[3:].strip())+'</h2>')
  elif block.startswith('<'):out.append(block)
  else:out.append('<p>'+escape(block.strip())+'</p>')
 return ''.join(out)
def add(slug,title,desc,cat,intent,utility,body,src=(FDA,),tool='nutrition-label-comparison-tool.html',tool_label='Compare food labels',scope=None,checks=None):
 rows.append({'slug':slug+'.html','title':title,'description':desc,'category':cat,'intent':intent,'utility':utility,'body':prose(body),'sources':[{'url':u,'label':source_info[u][0],'supports':source_info[u][1]} for u in src],'related':[{'url':tool,'label':tool_label},{'url':'articles.html','label':'Explore the reading table'}],'scope':scope or 'All food figures and prices in the worked example are invented to explain the method. They are not restaurant nutrition, tested recipes, shopping prices or personal dietary advice. Use the current label for the product you actually have.','status':'checked','arithmeticChecks':checks or []})

add('sugar-lines-do-not-add','Do I add total sugars and added sugars together?','Read the indented sugar lines correctly, then compare two portions without counting sugar twice.','Food labels','Avoid double-counting an indented nutrient on a U.S. label.','Original subtraction and portion-scaling example with an accounting check.', '''No. Added sugars already sit inside the total-sugars figure. Treating the two lines as separate ingredients overcounts the amount in your food. The indentation matters: “includes” identifies a part of the total.

## Read the relationship first

Imagine a yogurt label showing 18 g total sugars, including 6 g added sugars, per 150 g pot. That means the example has 12 g of sugars outside the added-sugars category: 18 − 6 = 12. It does not contain 24 g total sugars. This calculation describes the printed categories; it does not identify individual ingredients or how each sugar was produced.

## What changes with half a pot?

For a uniform product, half the labeled amount gives 9 g total sugars and 3 g added sugars. Both lines scale together. The portion still has 9 g total, not 12 g. If you compare it with another yogurt, put the same chosen portion beside both total and added amounts.

## Keep the useful question separate

If you want to compare added sugars, compare that line directly. If you want total carbohydrate, use the total-carbohydrate line instead of adding carbohydrate and sugar. More detail does not create more food. A missing added-sugars figure on a restaurant table is unknown; subtracting it from total sugars cannot recover it.

Before saving your notes, check that the parts do not exceed their total. The FDA explanation linked below supports the label relationship. The invented numbers here let you practise it without implying that a particular yogurt has this composition.''',src=(SUGAR,),checks=[['18-6',12],['18/2',9],['6/2',3]])

add('nutrient-grams-not-food-weight','Why do nutrient grams not add up to the food’s weight?','A 200 g portion is not 200 g of protein, carbs and fat. Learn what that leaves out.','Nutrition numbers','Understand why food mass differs from summed listed macronutrients.','Mass-accounting example distinguishes unlisted water and components from a missing-food error.', '''A food’s weight and its nutrient totals answer different questions. The weight describes the entire portion. Protein, carbohydrate and fat describe selected parts of it. You should not expect those three lines to reconstruct every gram on the plate.

## A 200 g example

Suppose a label for a 200 g food lists 12 g protein, 20 g carbohydrate and 8 g fat. The three numbers sum to 40 g. The other 160 g is not automatically a mistake or a hidden 160 g of carbohydrate. Water and other constituents can contribute to food mass, and the listed values have their own measurement and reporting limits.

You cannot calculate the precise water content simply by subtracting these three label lines. A full composition measurement would need compatible definitions and more information. USDA’s food documentation explains why a nutrient profile and a food description contain more than a few macro fields.

## Do not subtract fiber a second time

On the U.S. Nutrition Facts format, fiber sits within total carbohydrate. Adding it as a fourth independent mass category can count it twice. The same caution applies to sugars. Use the total lines for your accounting rather than every indented line in the panel.

## What to record instead

Write down the edible food weight, the actual serving basis and each listed nutrient separately. If you ate 100 g of this uniform 200 g example, you would scale the listed macro amounts by one-half. You would not divide the portion by the 40 g macro sum. This preserves a useful estimate while avoiding a false promise that label arithmetic measures every constituent.''',src=(FOUND,FDA),checks=[['12+20+8',40],['200-40',160]])

add('protein-label-blank-daily-value','Why can a protein label have grams but no % Daily Value?','A blank percentage is different from zero protein. Use the grams and the portion.','Protein questions','Interpret protein grams with an absent percentage field.','Explains absent versus zero fields with a concrete two-product comparison.', '''A blank protein percentage does not mean the food has no protein. Start with the grams shown for the serving. The U.S. labeling rules described by FDA do not require a protein % Daily Value in every situation.

## Compare the information you have

Picture two example snacks: one lists 10 g protein without a percentage, while the other lists 8 g protein and a percentage. The blank field does not erase the first product’s 10 g. Nor does a printed percentage prove that the second product has more grams. Compare the actual quantities for the portions you will eat.

If the servings differ, fix that first. A 40 g portion with 10 g protein and a 20 g portion with 8 g protein answer different portion questions. At equal 40 g food weights, the second example would provide 16 g protein if the product is uniform. At one labeled serving each, it provides 8 g.

## Why not calculate the percentage yourself?

The label percentage is not always just an informal gram target divided into the listed grams. Protein-label requirements have additional conditions. A calculator that invents a missing official percentage can make the result appear more authoritative than it is. Keep your personal gram comparison separate from the manufacturer’s regulated panel.

## A blank is a data boundary

If a restaurant has not published protein grams, the absence of a percentage cannot rescue the calculation either. Record what is known, mark what is unavailable and use another complete source where possible. GetMacros’ food comparison works with gram quantities; it does not certify protein claims or fill in missing label percentages.''',src=(FDA,),checks=[['8*40/20',16]])

add('percent-daily-value-not-vertical-total','Why % Daily Value does not add up to 100%','Each nutrient has its own reference amount. Adding the column creates a number with no useful meaning.','Food labels','Interpret the vertical Daily Value column as separate reference ratios.','Original independent-denominator example and table.', '''Do not add the % Daily Value column from top to bottom. Sodium, fiber and other nutrients use different reference amounts. Their percentages describe separate comparisons, not slices of one nutrition pie.

## Three percentages, three questions

Suppose an example portion shows 10% DV sodium, 20% DV fiber and 15% DV calcium. Adding them gives 45%, but that does not mean the meal covers 45% of your nutrition needs. The sodium percentage asks how the sodium amount compares with its reference. Fiber and calcium use their own denominators.

## Portion changes do not join the categories

Eating two identical portions would approximately double each displayed amount before rounding: 20% sodium, 40% fiber and 30% calcium in this example. These still remain three separate statements. There is no meaningful 90% total across them.

## Use the column horizontally

The practical comparison is the same nutrient across foods. Put sodium beside sodium for equivalent portions, or fiber beside fiber. A percentage can make unlike nutrient units easier to interpret, but it does not turn an entire label into one score. If you are following a personal target from a clinician, that target may differ from the label reference.

When entering a calculator, use the nutrient amount in its stated unit, such as grams or milligrams. Never enter “20” from a percentage field into a grams field merely because the numbers look similar. The FDA Daily Value guide explains the reference system; the arithmetic above is an original example of why summing the column loses the meaning of each line.''',src=(DV,),checks=[['10+20+15',45]])

add('sodium-milligrams-to-grams','Sodium in mg and g: stop the thousand-fold mistake','Convert the unit before comparing a label with a nutrient target.','Nutrition numbers','Convert sodium units without confusing nutrient amount with food weight.','Unit ledger with a thousand-fold input-error demonstration.', '''A milligram is one-thousandth of a gram. If a label says 800 mg sodium, that is 0.8 g sodium—not 800 g. Keeping the unit beside the number prevents one of the largest possible comparison errors.

## Work through the conversion

To move from milligrams to grams, divide by 1,000. To move from grams to milligrams, multiply by 1,000. An example sauce with 0.3 g sodium per portion therefore has 300 mg. Compared with an example soup containing 800 mg, the sauce has 500 mg less for those particular listed portions.

## The food weight is another quantity

A 300 g bowl with 800 mg sodium contains a 300 g food portion and 0.8 g of the listed sodium. The two “300” values in the sauce and bowl examples do not mean anything alike. One is a nutrient amount in milligrams; the other is an entire food mass in grams.

## Enter the calculator’s unit

The sodium tool asks for milligrams. Enter 300 for the example sauce, not 0.3. If your source uses grams, convert first and note that conversion. Check whether the nutrition is per portion or per 100 g before scaling; unit conversion alone does not fix a serving-size mismatch.

Finally, sodium and table salt are not interchangeable names. This guide converts sodium units only. It does not convert a salt figure into sodium or set a personal daily limit. NIST supports the mass-unit relationship, and FDA explains the distinction between sodium and salt. Both checks matter before a comparison can be trusted.''',src=(MASS,SODIUM),tool='sodium-label-comparison-tool.html',tool_label='Compare sodium portions',checks=[['800/1000',0.8],['0.3*1000',300],['800-300',500]])

add('per-ounce-vs-per-100g-food','How to compare food listed per ounce and per 100 g','Convert the portion basis first, keeping fluid ounces separate.','Food labels','Compare mass ounces and metric mass label bases.','Original per-ounce normalization with explicit fluid-ounce exclusion.', '''A food weight in ounces can be compared with a weight in grams once you use the same mass unit. A fluid ounce is a volume measurement and needs a different treatment. Look for “fl oz” before converting anything.

## Put both foods on one basis

For ordinary avoirdupois mass, one ounce is about 28.35 g. Imagine Food A lists 7 g protein per 1 oz, while Food B lists 20 g per 100 g. Food A’s approximate amount per 100 g is 7 × 100 ÷ 28.35 = 24.7 g. That is higher than Food B on an equal-weight basis, even though its printed serving number is smaller.

## Keep the original portion useful

Equal weight is useful for comparing concentration. It is not necessarily the amount you will eat. If you eat one ounce of A and 100 g of B, the actual portions give 7 g and 20 g protein respectively. Keep both answers in your notes rather than letting normalization erase the order size.

## Do not borrow the calculation for a drink

A bottle listed in fluid ounces describes volume. You cannot turn that into grams with the 28.35 conversion. Use the product’s own metric volume or an explicit product-specific mass measurement. A unit abbreviation can change the entire calculation.

Keep a sensible number of decimal places. The converted protein density is an estimate based on rounded printed inputs, not a laboratory result to four decimal places. NIST’s unit references support the distinction between mass and volume. This worked comparison is invented so it can illustrate the two competing questions clearly.''',src=(MASS,VOL),checks=[['7*100/28.35',24.691358024691358]])

add('half-serving-percent-daily-value','Does half a serving mean half the % Daily Value?','Scale the underlying amount, then allow for the label’s rounding.','Food labels','Use percentage reference amounts when eating a fractional serving.','A sodium percentage calculation distinguishes exact arithmetic from rounded panel display.', '''For the same uniform food, half the portion gives half the underlying nutrient amount. The displayed percentage may not halve perfectly because the original label is rounded. Use this as a practical estimate rather than demanding exact agreement between printed integers.

## Start with the amount in the panel

Imagine a label listing 460 mg sodium per serving. Half gives 230 mg. Against the FDA sodium Daily Value of 2,300 mg, that is 230 ÷ 2,300 × 100 = 10%. If the full serving was displayed as 20% DV, the two views line up neatly in this example.

## A less tidy label

Now imagine 500 mg sodium per serving. Half is 250 mg, or about 10.9% of that reference. A full-serving panel may show a rounded integer percentage. Halving that printed integer can introduce another small rounding difference. The food did not change; the representations did.

## Keep the denominator fixed

Eating half a portion changes the numerator, not the reference amount. Do not halve both the sodium and the Daily Value: that would leave the percentage unchanged. The same reasoning applies to other nutrient references, each with its own denominator.

Use the stated mass portion when you can. “Half” of a layered snack that separates unevenly may not contain half of every component. For a mixed product, portioning assumptions belong beside the calculation. The FDA Daily Value source supports the reference denominator; these invented amounts demonstrate the portion arithmetic, not a recommended sodium allocation.''',src=(DV,SODIUM),tool='sodium-label-comparison-tool.html',tool_label='Scale a sodium portion',checks=[['460/2',230],['230/2300*100',10],['250/2300*100',10.869565217391305]])

add('added-sugar-percentage-from-grams','Calculate added-sugars % Daily Value from grams','Use the U.S. label reference without turning it into a personal sugar prescription.','Food labels','Reconcile added-sugar grams and the label reference percentage.','Worked examples for single and multiple portions with total-sugar boundary.', '''On a U.S. label using the standard 50 g added-sugars Daily Value, divide the added-sugar grams by 50 and multiply by 100. This checks the label reference. It does not determine your individual dietary needs.

## A small arithmetic check

An invented drink with 8 g added sugars per bottle contributes 8 ÷ 50 × 100 = 16% DV for the full bottle. If you drink half of that same uniform product, 4 g contributes 8%. Two bottles would have 16 g and 32% before display rounding.

## Choose the correct sugar line

If the drink also lists 11 g total sugars, do not use 11 g in an added-sugar calculation. The example’s remaining 3 g sits outside the added-sugars category. A total-sugars figure alone is insufficient to work out added sugars because it does not reveal how that total is divided.

## The percentage is a comparison tool

Put the gram amount and portion beside the percentage. A tiny serving may appear modest as a percentage while several servings add up. Conversely, one larger bottle may have fewer servings than a container of another size. Compare the amount you actually intend to drink rather than matching package graphics.

The FDA source linked below explains the added-sugar reference and label category. The example arithmetic is original. If the restaurant source does not publish added sugars, keep that field unavailable instead of filling it with total sugars. A neat percentage is not worth creating unsupported data.''',src=(SUGAR,),checks=[['8/50*100',16],['4/50*100',8],['16/50*100',32],['11-8',3]])

add('calorie-range-menu-reading','What does a calorie range on a restaurant menu mean?','A range does not tell you the total for your exact order. Check the included choices.','Eating out','Interpret menu calorie ranges for variable menu combinations.','A decision checklist and invented combo arithmetic distinguish endpoints from an exact order.', '''A calorie range signals that the menu entry can cover different choices. The midpoint is not automatically your order. Identify the size, sides, drink and available options before treating the range as a number you can compare.

## Ask what produces the endpoints

An example combo marked 600–1,000 calories may include several side and drink options. Taking the average gives 800, but your selection might not correspond to any 800-calorie combination. Without the included choices, the average is just a mathematical midpoint.

## Build the order instead

Imagine the selected entrée is 420 calories, the listed side is 180 and the selected drink is 120. That exact example sums to 720. Choosing an example drink listed at 0 would change the total to 600. The calculation needs the actual component figures, not a guess about which combination sits near the middle.

## What if the detail is unavailable?

Keep the displayed range and its assumptions visible, or choose a record with a defined serving. Do not enter the lower endpoint as though it applies to every version. U.S. menu-labeling requirements have a particular scope; a menu page is not a universal guarantee that every restaurant or every country publishes the same detail.

For a useful comparison, name the complete order and excluded extras. “Entrée, small side and drink” is more informative than the combo’s marketing title. The FDA menu-labeling source provides the regulatory context; all figures here are fictional. GetMacros works best with defined orders, so its results should not pretend that a variable menu range is one measured meal.''',src=(MENU,),tool='restaurant-meal-finder.html',tool_label='Browse defined restaurant orders',checks=[['(600+1000)/2',800],['420+180+120',720],['420+180',600]])

add('restaurant-menu-serving-weight','When restaurant serving weights help—and when they do not','Use a gram weight to understand the source portion, not to promise an exact tray weight.','Eating out','Interpret listed restaurant serving mass without overclaiming portion precision.','A mass-to-density example and a distinction between published and served quantities.', '''A listed serving weight identifies the portion behind the nutrition table. It helps you see whether a record describes one sandwich, a full bowl or one component. It does not guarantee that every order assembled in a restaurant has exactly that mass.

## Read the weight beside the item

Suppose an invented menu entry gives one 250 g sandwich at 500 calories. The listed density is 500 ÷ 250 = 2 calories per gram. A different 150 g side at 300 calories has the same arithmetic density, but it is a different food and a different order. Density alone does not establish that they are equivalent meals.

## Avoid an unsupported scaling shortcut

If your sandwich weighs 270 g, multiplying by 2 gives 540 calories only under an assumption that the whole sandwich’s composition scales uniformly. An extra 20 g of sauce, chicken or bread would not necessarily have the average composition. Label that method as an estimate rather than a correction to the restaurant’s published number.

## Serving names still matter

A weight should never replace the order description. Check whether dressing, buns, toppings and sides are included. Ingredient weights and a completed order’s weight may be drawn from different source records, and rounded figures may not sum exactly.

Use a restaurant’s own published nutrition for the defined standard order, with its caveats, then request official customization information if the order changes. The FDA menu-labeling guidance supplies the context for declared menu information. This example demonstrates why a gram figure is useful evidence but not a guarantee of individually weighed or laboratory-tested food.''',src=(MENU,FOUND),tool='restaurant-meal-finder.html',tool_label='Inspect order portions',checks=[['500/250',2],['300/150',2],['270*2',540]])

add('net-carbs-total-carbohydrate','Can I put “net carbs” into a total-carbohydrate filter?','Use the same definition on both sides of a comparison.','Food labels','Avoid mixing a marketing net-carb value with total-carbohydrate data.','Worked difference with explicit definition assumptions and missing-data boundary.', '''Not without changing the meaning of the filter. A total-carbohydrate control expects the total-carbohydrate figure. A “net carbs” figure uses a different calculation, which may vary with the product’s stated method.

## The two numbers answer different questions

Imagine a food showing 30 g total carbohydrate and 6 g fiber. If a stated example method subtracts only fiber, the result is 24 g. Entering 24 into a tool that expects total carbohydrate undercounts its total by 6 g. Calling both entries “carbs” hides the mismatch.

Some products also refer to sugar alcohols or other adjustments. Do not assume a subtraction rule from the front of the package. Read the full panel and the product’s explanation. This guide does not endorse a net-carb definition or claim that subtracting a nutrient predicts an individual response to the food.

## Keep a small data dictionary

Record the label name, quantity, serving and method. For a restaurant source, “carbohydrate” should retain the definition used by that source. If fiber is missing, subtracting an assumed amount does not make the missing value known.

## Use the supported field

GetMacros’ carbohydrate tool scales total-carbohydrate grams. Its restaurant carbohydrate filter should be interpreted using the recorded source definition, not a homemade net calculation. If you want to track another definition, keep it in a separate note with the calculation stated. FDA’s label guidance supports the relationship of carbohydrate and its indented lines; the numerical example is invented and is not medical advice about blood glucose or carbohydrate management.''',src=(FDA,),tool='carbohydrate-label-portion-tool.html',tool_label='Scale total carbohydrate',checks=[['30-6',24]])

add('choose-fooddata-central-entry','Which FoodData Central entry should I choose?','Match food identity and preparation before choosing a nutrient number.','Kitchen calculations','Select a USDA data type and food description for a real measurement.','Entry-selection decision matrix with a practical identification checklist.', '''Choose the entry that describes what you actually have. A matching word is not enough: the food’s state, brand, preparation and serving basis can change the meaning of the result. More digits do not make a mismatched entry accurate.

## Start with the food, not the nutrient

If you have a packaged product, read its current label and compare its identity with a branded database entry. For an ordinary ingredient, examine the detailed description of a suitable basic-food entry. For a prepared dish, inspect how the entry describes that dish rather than borrowing a raw ingredient profile.

## Data types are not interchangeable badges

FoodData Central’s documentation distinguishes several data types. Foundation Foods and Branded Foods do not obtain every value in the same way. The former provides analytical and descriptive information; the latter includes industry-supplied label information. Neither category means that your exact portion was personally tested by GetMacros.

## Save the identification trail

Keep the FDC identifier, description, preparation state, unit and date you consulted it. If an app presents only “chicken,” the omitted details make it difficult to audit the estimate later. Check whether a nutrient is unavailable rather than assuming that an absent field means zero.

Before using an entry for a recipe, confirm that your measured amount has the same edible basis. Bone-in purchased weight and edible meat weight differ; raw and cooked weights can also describe different material states. This is a selection workflow, not a promise of perfect home-meal measurement. The official USDA documentation linked below explains the database categories and why their metadata deserve attention.''',src=(FDC,FOUND),tool='recipe-macro-scaler.html',tool_label='Scale a documented recipe',scope='No nutrient values for a specific USDA food are quoted here. This article explains how to choose and document an entry; the database remains the source for the selected food.')

add('nutrition-data-mean-not-every-portion','A food database average is not every individual portion','Understand what an average can support without inventing precision.','Nutrition data','Interpret variability in sampled nutrient data.','An original three-sample arithmetic example separates mean, range and individual measurement.', '''An average is useful for describing a set of measurements. It is not proof that every individual portion contains precisely that amount. USDA’s Foundation Foods documentation makes sample information and variation part of the data context.

## A simple sample example

Imagine three invented measurements for the same stated nutrient basis: 8, 10 and 12 g. Their mean is (8 + 10 + 12) ÷ 3 = 10 g. The range is 8–12 g. If you report only 10, you communicate the centre of those examples but hide the variation.

## Do not turn a range into a personal reading

You cannot know which sample your lunch resembles merely by choosing the average. Nor can you treat the highest or lowest sample as the guaranteed content of your order. A measured portion, a recipe calculation and a published mean are different evidence types.

## Preserve the basis and method

An average per 100 g should stay attached to that food description and preparation state. Multiplying it by a weighed amount can give a useful estimate, but extra decimal places do not remove the underlying variation. A 137 g portion calculated from 10 g per 100 g gives 13.7 g under that simple assumption; it is not a direct laboratory measurement of your plate.

For everyday use, a documented estimate is often more honest than false exactness. When a published source gives sample counts or variability, keep them rather than rewriting the number as a universal property of the food. The figures above are fictional and explain statistics only; they are not measurements of any ingredient in GetMacros.''',src=(FOUND,),tool='sources.html',tool_label='Read how GetMacros handles data',checks=[['(8+10+12)/3',10],['137*10/100',13.7]])

add('nutrition-blank-vs-not-detected','Blank, zero and “not detected” are different nutrition entries','A missing field is a boundary, not an invitation to create a number.','Nutrition data','Separate missing, measured/rounded zero and detection-limited fields.','Original status ledger demonstrates why calculations must propagate unknowns.', '''A blank means the source has not supplied a usable value in that field. Zero is a supplied numerical value, subject to its source’s measurement and labeling conventions. “Not detected” describes an analytical result and may depend on the method’s detection limit. These labels should not be silently treated as the same thing.

## A sum with one missing ingredient

Imagine a bowl with 600 mg documented sodium from its known ingredients, plus a sauce whose sodium is unavailable. The complete bowl is not known to have 600 mg. You have a documented subtotal and an unknown addition. Naming it “at least the known subtotal” can communicate the boundary, but a strict maximum filter cannot certify the final order from it.

## A genuine zero has a different role

If the sauce source supplies 0 mg, the numerical calculation can use that published figure while retaining the source convention. Do not claim laboratory absence merely because a rounded label displays zero. Equally, do not discard every zero as missing.

## Preserve the status in your notes

Use a number plus a source status where needed. A spreadsheet that automatically fills blanks with zero may create attractive totals while corrupting their meaning. USDA’s documentation describes analytical data and unavailable nutrients; the FDA label guide explains the context of displayed nutrition amounts.

For GetMacros, an unknown should stay unknown in a meal, comparison and filter. If an important limit depends on that unknown, choose a fully documented order or consult the official source. The invented bowl example illustrates data handling, not a claim about any sauce or restaurant.''',src=(FOUND,FDA),tool='missing-restaurant-nutrition.html',tool_label='Read about unavailable meal data',checks=[])

add('tare-bowl-before-weighing-food','How to tare a bowl before weighing food','Measure the food rather than the bowl, and keep the unit visible.','Kitchen calculations','Use container subtraction to obtain the measured food mass.','Tare and manual-subtraction workflows with a diagnostic example.', '''Taring sets the container reading aside so the next reading represents the added material. If you forget, the bowl’s mass can make your recorded food amount much larger than it is. You can still recover the food weight when both readings are available.

## Two ways to get the same answer

Imagine an empty bowl weighing 240 g. Bowl plus food reads 415 g. Without using tare, subtract: 415 − 240 = 175 g food. If you place the empty bowl on the scale and tare it before adding the food, the displayed added mass should be 175 g in this example.

## Keep your sequence consistent

Choose grams on the scale. Place the stable empty container on it, tare, then add the food. If you reset between ingredients, write down each ingredient before resetting. Otherwise a later reading can tell you only what was added since the latest tare, not the whole recipe.

## Check what the label describes

The measured edible mass still needs a matching source. A tared 175 g raw ingredient is not automatically 175 g of a cooked database entry. A layered bowl also cannot be divided into ingredient nutrition merely from its total weight.

If the scale drifts, changes unit or was reset at the wrong time, repeat the measurement instead of adjusting the result to a number you expected. NIST’s Metric Kitchen supports careful kitchen measurement and appropriate tools. This workflow improves the mass input; it does not make a home nutrition estimate equivalent to laboratory analysis.''',src=(KITCHEN,MASS),tool='recipe-macro-scaler.html',tool_label='Calculate a recipe portion',checks=[['415-240',175]])

add('weigh-food-by-container-difference','Weigh a spoonful by the change in container weight','An alternative when putting the ingredient directly on the scale is awkward.','Kitchen calculations','Estimate transferred mass by before/after container readings.','Difference method with residue and separate-ingredient boundaries.', '''Weighing the source container before and after serving can tell you how much mass left it. This is useful for a sticky spread when a spoon or plate is difficult to weigh. It estimates the transfer, not necessarily the exact amount ultimately eaten.

## Follow the disappearing mass

Suppose an invented jar weighs 510 g before you take out a spoonful and 492 g afterward. The difference is 18 g. If the spread’s label gives 90 calories per 15 g, that transfer corresponds to 18 ÷ 15 × 90 = 108 calories under the label-scaling assumption.

## Account for what stayed on the spoon

If some spread remains on the utensil or was spilled, the mass leaving the jar is larger than the mass eaten. Do not describe the 18 g as an exact intake measurement unless you know the transfer was complete. A second measurement of leftovers may help, but it has its own measurement limits.

## Avoid a changing-container mistake

Use the same lid and container arrangement before and after. Removing a lid for the second reading subtracts the lid too. Keep the scale unit fixed and the container stable. Differences can magnify small reading errors when the portion is tiny.

This method is an alternative mass input for a documented portion calculation. It should not replace the source label or convert an ingredient into a restaurant customization. NIST’s kitchen-measurement resources and FDA’s serving-basis explanation support the workflow. All food values above are invented for the arithmetic, so they do not describe a real spread.''',src=(KITCHEN,SERVE),tool='nutrition-label-comparison-tool.html',tool_label='Scale the measured amount',checks=[['510-492',18],['18/15*90',108]])

add('portion-ratio-vs-percent-change','A portion multiplier is different from a percentage increase','Two servings are twice the amount, but that is a 100% increase—not 200%.','Nutrition numbers','Distinguish final ratio from change percentage in nutrition comparisons.','Side-by-side multiplier and percentage-change example.', '''“Twice as much” describes the final ratio. “Increased by” describes the extra amount relative to the starting value. Confusing them can turn a simple meal comparison into an exaggerated claim.

## Use the starting amount as the denominator

Imagine a listed portion with 200 calories, then a double portion with 400. The multiplier is 400 ÷ 200 = 2. The increase is (400 − 200) ÷ 200 × 100 = 100%. The double portion is 200% of the original amount, but it increased by 100%.

## A smaller change

Moving from 200 to 250 calories gives a 1.25 multiplier and a 25% increase. The additional 50 calories are the difference; 250 is the final amount. A sentence that says “adds 250 calories” would be wrong for this example even though 250 appears in the table.

## Reverse comparisons use another starting point

Going from 400 back to 200 is a 50% decrease, not a 100% decrease. The denominator is now 400. State the direction whenever you use percentages: “compared with the original portion” is enough to make the claim auditable.

This arithmetic can compare calories, protein or another supported quantity, but it does not by itself judge the meal’s suitability. Keep the portions and units visible. A percentage for a tiny baseline can sound dramatic while the gram difference is small. FDA’s serving guidance supports scaling like-for-like portions; the fictional examples here explain how to describe the resulting difference accurately.''',src=(SERVE,),checks=[['400/200',2],['(400-200)/200*100',100],['(250-200)/200*100',25],['(400-200)/400*100',50]])

add('percentage-points-vs-percent-food-labels','Percentage points and percent: read a label comparison correctly','A move from 10% DV to 15% DV is five points, not a 5% increase.','Nutrition numbers','Describe differences between nutrient reference percentages accurately.','Original three-way comparison of amount, point difference and relative change.', '''A percentage-point difference subtracts two percentages directly. A relative percentage change divides that difference by the starting percentage. Both can be valid, but they communicate different things.

## A clear example

Imagine two equal portions listed at 10% DV and 15% DV for the same nutrient. The difference is 5 percentage points. Relative to the 10% starting value, 15% is 50% higher: (15 − 10) ÷ 10 × 100. Calling it a “5% increase” mixes the two methods.

## Check the comparison basis

The two percentages must refer to the same nutrient reference and compatible portions. Comparing sodium %DV from one product with fiber %DV from another is not a point difference with a useful dietary meaning. Changing the portion can also change the conclusion.

## Prefer the quantity when it is clearer

If both panels give gram or milligram amounts, put those beside the percentages. “An additional 2 g fiber for this portion” can be easier to use than a relative increase. A percentage reference adds context, but it should not conceal how much food or nutrient is involved.

Rounded percentages can make small differences imprecise. If you have the underlying amounts, calculate from those before writing a comparison, then round the result sensibly. FDA’s Daily Value guidance explains what the label percentages refer to. This article’s invented percentage pair is a language and arithmetic example, not a claim about any product or a personalised nutrient target.''',src=(DV,),checks=[['15-10',5],['(15-10)/10*100',50]])

add('grams-per-serving-vs-protein-percentage','Protein grams are different from the percentage of a food’s weight','A protein percentage needs an explicit denominator.','Protein questions','Interpret protein gram content as mass share rather than calorie share or Daily Value.','One invented food described on three denominator bases.', '''“Twenty grams of protein” is an amount. “Twenty percent protein” is incomplete until you know what the percentage refers to. It might mean a share of food weight, energy or a separate reference. Those are not interchangeable.

## Describe the food-weight calculation

Imagine a 100 g food portion containing 20 g protein. Protein represents 20 ÷ 100 × 100 = 20% of the food’s mass under that description. A 50 g portion of the same uniform food contains 10 g protein, but its mass proportion remains 20%.

## Keep food weight and energy separate

You cannot infer the percentage of calories from protein solely from that 20% mass share. You would need the relevant energy calculation and the food’s total energy on a compatible basis. Likewise, a mass share is not the label’s protein % Daily Value.

## Use ordinary grams for meal decisions

For two actual meals, total protein grams and included portions are usually the useful starting points. A small concentrated snack may have a higher mass share while providing fewer grams than a larger order. Do not let a percentage erase that trade-off.

When reading a package or app, look for the denominator in the caption. If it is absent, ask what the number means rather than guessing. USDA’s food-data documentation distinguishes quantities and calculation factors; FDA explains label amounts and reference percentages. The simple 100 g example above is invented and does not certify a product as “high protein” or set a meal target.''',src=(FOUND,FDA),tool='protein-value-calculator.html',tool_label='Compare protein amounts and cost',checks=[['20/100*100',20],['50*20/100',10]])

add('protein-target-gap-not-automatic-extra','A protein gap is arithmetic, not an instruction to add another order','Compare the difference with portions you actually want to eat.','Protein questions','Interpret a user-chosen protein target difference without automatic supplementation advice.','Hypothetical gap comparison across portion options and uncertainty.', '''If you choose a protein amount for a meal, subtracting the recorded meal’s amount tells you the gap. It does not tell you that you must order extra food, take a supplement or reach the number at all costs. Appetite, the rest of your day and personal advice remain separate considerations.

## Calculate the difference

Imagine a self-chosen example target of 30 g and an order recorded at 24 g. The numerical gap is 6 g. A hypothetical extra portion with 12 g protein would raise the total to 36 g, which is 6 g above that example target. Half of that uniform portion would add 6 g only if half-portions are supported and the food is divided appropriately.

## Consider the whole addition

The extra portion also has its own calories, fat, carbohydrate and sodium. It is not pure protein simply because you selected it for protein. Add all known component values if you want to compare the complete order. Keep any unavailable nutrient as unknown.

## Do not invent a customization

An arithmetic half-portion is not evidence that a restaurant sells one. Use a listed serving or an official customization tool, and name the included items. If you are not hungry for the addition, choosing a different complete order can be simpler than building around a precise gap.

These numbers teach subtraction and addition. They do not establish an appropriate protein target for you. FDA’s label guidance supports the serving-based quantities used in the method. The finder lets you compare supported gram amounts while leaving the actual decision in your hands.''',src=(FDA,),tool='restaurant-meal-finder.html',tool_label='Compare complete meals',checks=[['30-24',6],['24+12',36],['36-30',6]])

add('protein-serving-count-day-not-prescription','Add protein from different portions without inventing a meal plan','Keep the quantities and serving assumptions in a simple ledger.','Protein questions','Sum recorded protein across distinct eating occasions without prescribing intake.','A four-entry example with an omitted-item correction.', '''Add the protein amounts for the portions you actually recorded. The calculation is a ledger, not a recommendation to eat those foods or to achieve that particular total. A useful record tells you where every amount came from.

## Make each row auditable

Imagine four invented portions providing 16 g, 28 g, 9 g and 22 g protein. Their total is 75 g. If the 9 g snack was not eaten, the corrected total is 66 g. Keep the correction attached to the record rather than leaving the food name in place while changing only the day’s total.

## Watch for mixed serving bases

One row might describe a whole sandwich while another describes 100 g of yogurt. Both can be added if the amounts have already been scaled to what was eaten. Adding unscaled panel values does not produce a meaningful day total. Double-check powders, drinks and recipe portions where the entered amount may differ from one label serving.

## Unknown is not a convenient zero

If a portion has no reliable protein figure, the ledger’s complete total is unavailable. You can report the known subtotal and name the missing portion. Do not quietly leave the item out and call the remaining number the full day.

The FDA serving explanation supports the source basis, not the invented meal pattern. This method is for understanding recorded amounts. It does not decide how much protein you need or replace individualized advice. If tracking becomes stressful or you need a medical nutrition plan, a numerical ledger alone cannot answer that wider question.''',src=(SERVE,),tool='how-much-protein-per-day.html',tool_label='Understand protein estimates',checks=[['16+28+9+22',75],['75-9',66]])

add('protein-per-package-not-scoop-count','How much protein is in a pack when serving weights differ?','Use weight and the label basis to compare the whole pack.','Protein questions','Compare total protein in packages whose serving count and size differ.','Two-pack example distinguishes package content, portion content and cost.', '''The protein in a full pack depends on its food weight and labeled protein basis. Counting printed servings alone is not enough when two products use different serving sizes. Keep package amount and the portion you intend to eat separate.

## Compare two invented packs

Pack A weighs 400 g and lists 10 g protein per 100 g. Its calculated package total is 40 g. Pack B weighs 300 g and lists 8 g protein per 60 g serving. It contains five such servings, for 40 g protein in the pack. Different package sizes and serving figures can produce the same package protein total.

## That does not make the foods identical

One 100 g portion of A supplies 10 g; the same 100 g weight of B supplies about 13.3 g under the uniform-product assumption. The package total answers how much protein is available across the whole pack, while equal-weight density answers another question.

## Useful for a cost comparison

If you use the entire pack, price divided by package protein gives a cost per gram. If part is discarded or inedible, the usable total may differ. Do not include packaging mass or turn drained and undrained weights into interchangeable amounts.

FDA’s serving guidance supports scaling the recorded quantity. The example is invented, and the figures should not be attached to real products. Use the protein-cost tool only after entering matching edible weight and label basis. A pack with more total protein can still be a less practical purchase if the amount exceeds what you will use.''',src=(SERVE,),tool='protein-value-calculator.html',tool_label='Compare protein cost',checks=[['400*10/100',40],['300/60*8',40],['8*100/60',13.333333333333334]])

add('fiber-per-portion-vs-density','More fiber per 100 g can still mean less fiber on your plate','Compare concentration and actual portion as separate questions.','Fiber and plant foods','Distinguish fiber density from fiber delivered by a chosen portion.','A reversible ranking example using two different real-life measurement questions.', '''The higher fiber figure per 100 g does not always mean more fiber in the portion you eat. Weight-normalized data describe concentration. Your plate’s total also depends on how much of the food is included.

## Watch the ranking change

Imagine Food A supplies 8 g fiber per 100 g and Food B supplies 5 g. A is more concentrated. But a 30 g portion of A gives 2.4 g fiber, while a 150 g portion of B gives 7.5 g. B’s larger chosen portion provides more total fiber in this example.

## Use the question you actually have

If you are comparing labels for equal weights, density is useful. If you are choosing between a small topping and a substantial side, the listed portions may matter more. Neither comparison proves that one food is universally better or that the larger amount is the portion you should eat.

## Keep fiber inside total carbohydrate

On a U.S. label, dietary fiber is part of the carbohydrate presentation. Do not add fiber grams to total carbohydrate when calculating the meal. Use each field for its own purpose and retain the serving basis.

The FDA label guide supports how the fields are read; the original arithmetic demonstrates the ranking reversal. When using restaurant data, compare only supported fiber amounts. A blank fiber field should not receive a value inferred from an ingredient’s name. The finder can help you compare complete documented orders, but a filter threshold is not a personal fiber recommendation.''',src=(FDA,),tool='restaurant-meal-finder.html?goal=fibre',tool_label='Explore recorded fiber amounts',checks=[['8*30/100',2.4],['5*150/100',7.5]])

add('fiber-daily-value-portion-example','What does 7 g fiber mean on a U.S. label?','Translate a gram amount into the label reference while keeping the portion visible.','Fiber and plant foods','Interpret a fiber quantity against the current FDA Daily Value basis.','Original fraction-of-reference example with two portion sizes.', '''For the standard U.S. label fiber Daily Value of 28 g, a portion containing 7 g supplies 25% of that reference. It does not mean that the food is 25% fiber by weight or that everyone needs the same amount each day.

## Keep the arithmetic transparent

Divide 7 by 28, then multiply by 100. If you eat half of the same uniform portion, 3.5 g corresponds to 12.5% before label rounding. Two full portions give 14 g, or 50%. These are reference comparisons, not instructions for distributing fiber across meals.

## Avoid a misleading visual score

A ring filled one-quarter of the way could communicate this particular reference calculation, but it would not be a score for the meal’s overall quality. It does not include other nutrients, portion suitability or your circumstances. A plain “7 g fiber in this portion” can be more useful.

## Check what was actually measured

If a restaurant gives no fiber figure, a meal name containing beans or vegetables cannot supply a precise value. Use the official source or retain the unknown. If a published figure is per component rather than per complete meal, sum only supported included components and state the method.

FDA’s Daily Value source supports the 28 g denominator. The example portion is fictional. For individual needs or gastrointestinal concerns, a label reference is not a treatment plan. Use it to understand published quantities and compare compatible portions, not to certify that one meal completes a personal dietary requirement.''',src=(DV,),tool='how-much-fiber-per-day.html',tool_label='Read about fiber reference amounts',checks=[['7/28*100',25],['3.5/28*100',12.5],['14/28*100',50]])

add('two-fiber-sources-one-bowl','Two fiber sources in one bowl: add the portions, not the percentages','Keep both ingredients and their labeled amounts in the calculation.','Fiber and plant foods','Sum supported fiber contributions in a mixed example without assuming uniform distributions.','Original two-ingredient calculation and a missing-topping boundary.', '''A mixed bowl can include fiber from several foods. Add each documented ingredient amount after scaling it to the included portion. The ingredient names alone are not enough to determine the total.

## Build the example from its labels

Imagine Ingredient A gives 6 g fiber per 100 g and Ingredient B gives 4 g per 80 g. The bowl includes 150 g of A and 40 g of B. A contributes 9 g and B contributes 2 g, for 11 g fiber from those two ingredients.

## Keep other additions visible

If an added sauce has unavailable fiber, the complete bowl’s value remains unknown. The 11 g is the documented subtotal, not an excuse to pretend the sauce has zero. If the source supplies a genuine zero, retain it with its source convention.

## Dividing the bowl takes an assumption

If you split a fully mixed, uniform bowl into two equal portions, each has half the calculated total. If beans stay mostly in one container and another ingredient in the other, equal container weight does not guarantee equal fiber. Weighing the mixed whole cannot reveal each ingredient’s distribution.

This is original arithmetic using invented ingredient values. FDA supports the serving-based label interpretation and USDA documents why food identification matters. The result is not a verified recipe or a restaurant customization. Save the ingredient weights and source basis alongside the total so another person can reproduce the calculation and see what is missing.''',src=(SERVE,FOUND),tool='recipe-macro-scaler.html',tool_label='Calculate portions of a documented recipe',checks=[['6*150/100',9],['4*40/80',2],['9+2',11]])

add('plant-name-not-fiber-number','A plant ingredient’s name cannot tell you its fiber grams','Check the actual food, preparation and portion before assigning a number.','Fiber and plant foods','Avoid fabricating fiber from plant names and unspecified mixtures.','Decision workflow distinguishes descriptive ingredients from numerical evidence.', '''“Contains vegetables” is descriptive information. It is not a measured fiber amount. To calculate grams, you need a source for the actual food and preparation, plus the amount included. A menu photograph or ingredient list without quantities cannot do that work.

## Identify the missing piece

For a named plain ingredient, a compatible database entry may provide a basis. For an unspecified vegetable mixture, the proportions and preparation remain uncertain. For a restaurant order, a complete published nutrition figure is generally more directly applicable than an estimate built from generic foods.

## Do not award an invented bonus

Imagine two bowls, both described as “with greens.” One has 5 g documented fiber and the other has no fiber figure. They are not tied at 5 g, and the missing one is not zero. A ranking that fills its blank with an attractive guessed number would invent precision and could change the order of results.

## Quantities make a recipe calculation possible

If a recipe actually states ingredient weights and has appropriate source entries, you can scale and sum their values while recording assumptions. Keep cooked and raw bases compatible. That calculation is different from reading a restaurant’s declared complete order and should be labeled accordingly.

USDA’s documentation describes food identity and data types; FDA explains serving-based panel values. This guide supplies a practical evidence checklist, not a catalog of fiber claims. GetMacros should offer a transparent unavailable state where the data are missing rather than treating a friendly plant-food description as a numerical verification.''',src=(FOUND,FDA),tool='missing-restaurant-nutrition.html',tool_label='Understand missing restaurant values',scope='No fiber values are claimed for a real food or restaurant. The two bowls are invented data-status examples.')

add('vegetarian-label-not-allergen-safety','Vegetarian is not an allergen-safety guarantee','Dietary descriptions and allergen information answer different questions.','Eating out','Distinguish dietary preference labels from confirmed allergy suitability.','Ordering checklist separating ingredient preference, allergen declaration and preparation.', '''A vegetarian description does not mean an order is free of allergens. Ingredient preferences and allergy safety are different questions. Do not use a vegetarian filter, food character or nutrient comparison as permission to order food that you need to avoid.

## Read more than the menu category

An order can fit a vegetarian preference while containing ingredients relevant to a food allergy. A nutrient panel also does not identify all ingredients or how a kitchen handles them. The FDA allergen source explains why the food source named in the ingredient declaration matters.

## Ask about the actual order

Use the restaurant’s current allergen information for your market and discuss the exact order with the restaurant. Check substitutions and preparation rather than assuming that removing one visible ingredient resolves everything. GetMacros does not have the kitchen’s real-time handling information.

## Keep two decisions separate

First, decide whether the listed ingredients match a preference using supported information. Separately, obtain the allergy-related information you need from the appropriate source. If that information is unavailable, a low calorie amount or a high protein number does not make the unknown safer.

This article does not certify an order as allergen-free or provide an allergy treatment plan. Its practical purpose is to stop one kind of label from being mistaken for another. The official FDA resource linked below provides further information on food allergens. For a known food allergy, follow the plan from your health professional and use restaurant-specific information; an independent nutrition finder cannot guarantee safety.''',src=(ALLERGY,),tool='sources.html',tool_label='Read dataset boundaries',scope='This is a scope explanation, not allergen certification, medical diagnosis or a claim about a named restaurant.')

add('breakfast-two-items-not-one-entry','A breakfast order with two items needs two nutrition entries','Count the actual food and drink instead of borrowing a single-item menu total.','Breakfast decisions','Document a breakfast assembled from separate source servings.','Original breakfast ledger with exclusions and total correction.', '''If your breakfast has two separately listed foods, one item’s nutrition cannot represent both. Build the order from the exact portions and any drink or spread you include. A menu photo of a breakfast arrangement does not establish the included nutrition.

## Write the order before adding

Imagine a fictional sandwich listed at 310 calories and 18 g protein, plus a yogurt listed at 120 calories and 9 g protein. Those two portions sum to 430 calories and 27 g protein. A separately listed 80-calorie drink raises energy to 510 without changing the known protein unless its own source supplies a protein amount.

## Keep unavailable fields unavailable

If the drink’s protein is unknown, 27 g is the food-only subtotal, not a verified complete-order protein total. Do not infer its grams from the drink name. If the source lists 0 g, you can use that documented value instead.

## A breakfast name is not a serving definition

Check whether the sandwich listing includes a spread, sauce or cheese. Check whether the yogurt is the whole container or a smaller serving. GetMacros records should keep exclusions visible so a standalone breakfast item is not mistaken for a combo.

The FDA serving and menu resources support reading the basis and seeking the written information. All figures here are invented. They explain how to assemble a ledger, not what to eat at breakfast. Compare complete defined orders in the finder or consult the restaurant’s own information when your combination differs from a tracked entry.''',src=(SERVE,MENU),tool='restaurant-meal-finder.html?meal=breakfast',tool_label='Compare recorded breakfast orders',checks=[['310+120',430],['18+9',27],['430+80',510]])

add('breakfast-yogurt-topping-layer','Calculate yogurt with a topping without treating it as one label','Separate the pot, topping and portion you actually use.','Breakfast decisions','Estimate breakfast assembled from separately packaged yogurt and topping.','Original two-label calculation with partial-topping example.', '''A yogurt pot’s label may or may not include a separately packaged topping. Read the serving definition before adding granola, nuts or another addition. Counting the topping twice is as easy as leaving it out.

## Establish what the panel includes

For this invented example, the yogurt-only portion has 140 calories and 12 g protein. A separately labeled 30 g topping has 150 calories and 3 g protein. Using the full topping gives 290 calories and 15 g protein, assuming those panels really describe separate components.

## Using part of the topping

If you add 12 g of that uniform topping, the multiplier is 12 ÷ 30 = 0.4. It contributes 60 calories and 1.2 g protein. Combined with the whole yogurt, the example gives 200 calories and 13.2 g protein. Retain enough precision while calculating, then avoid presenting the final estimate as more exact than its rounded labels.

## Stop if the packaging basis is unclear

If the label already describes yogurt plus topping, adding the topping’s panel again overcounts. Look for an explicit serving description or manufacturer information. A front-of-pack number without that basis cannot resolve the ambiguity.

This worked breakfast is arithmetic practice, not a tested recipe or a real brand comparison. FDA’s serving explanation supports the relationship between the panel and its described portion. Keep the yogurt weight, topping weight and source descriptions in your notes if you want the result to be reproducible later.''',src=(SERVE,),tool='nutrition-label-comparison-tool.html',tool_label='Scale the topping portion',checks=[['140+150',290],['12+3',15],['12/30',0.4],['150*0.4',60],['140+60',200],['12+3*0.4',13.2]])

add('breakfast-sandwich-half-not-half-protein','Half a sandwich may not be half of every nutrient','Dividing a mixed food requires a composition assumption, not just a knife.','Breakfast decisions','Explain when fractional mixed-food nutrition is an estimate.','Original unequal-filling example and a clear documentation workflow.', '''Half the weight of a mixed sandwich is not guaranteed to contain half its protein, fat and carbohydrate. The simple half-serving calculation assumes a reasonably even distribution of the components. A filling concentrated on one side can break that assumption.

## What the simple calculation means

Imagine a whole fictional sandwich listed at 400 calories and 24 g protein. Dividing both by two gives 200 calories and 12 g protein for an assumed uniform half. That is a reasonable arithmetic model of an evenly split item—not a measurement of each cut piece.

## What can make the halves differ?

Uneven filling, a sauce placed on one side or removing part of the bread changes the composition. Weighing both halves and finding equal masses does not prove equal nutrient content. Two different ingredients can weigh the same and contain different nutrient amounts.

## Choose the level of precision you can support

For everyday notes, label the result “estimated half of the standard sandwich.” If you need component-level calculation, obtain the supported component values and amounts instead. Do not invent a filling split from the photograph.

FDA’s serving guidance explains scaling a portion; USDA’s food-description documentation helps show why identifying the material matters. This example illustrates the limits of a fractional calculation. It does not recommend eating half a meal or suggest that the smallest portion is preferable. Your portion decision and the estimate of its nutrition are separate tasks.''',src=(SERVE,FOUND),tool='serving-size-vs-portion-size.html',tool_label='Understand serving and portion definitions',checks=[['400/2',200],['24/2',12]])

add('breakfast-food-vs-combo-menu','Breakfast item or breakfast combo: compare the same thing','Separate the food-only entry from its optional side and drink.','Breakfast decisions','Avoid comparing a breakfast combo with a standalone entrée.','Complete-vs-food-only example with explicit comparative arithmetic.', '''A food-only menu entry and a combo are not interchangeable servings. Before comparing calories or protein, identify whether the side and drink belong to each number. A lower printed total may simply describe fewer included items.

## Make the comparison explicit

Imagine Breakfast A is one fictional sandwich at 330 calories and 20 g protein. Breakfast B is a different sandwich plus a side at 510 calories and 23 g protein. Comparing 330 with 510 answers a complete-order question only if those are the orders you plan to buy. It does not isolate the sandwich difference.

## Separate the side when the source allows

If B’s official component table says its sandwich is 360 calories and 21 g protein, the side accounts for 150 calories and 2 g protein in this example. You can then compare sandwiches at 330 versus 360 and complete listed orders at 330 versus 510. Label both views clearly.

## Keep the beverage in scope

If the combo includes a choice of drink, a single food-and-side total still may not be the full purchased order. Add the chosen documented beverage or state that it is excluded. Do not assign a default drink without telling the reader.

FDA’s menu-labeling and serving information supports checking the published scope. These are invented values. Use them to learn the accounting method, then use actual source-defined portions for a restaurant decision. GetMacros should compare clearly named orders rather than letting a marketing combo name hide what the recorded figure contains.''',src=(MENU,SERVE),tool='restaurant-meal-finder.html?meal=breakfast',tool_label='Browse breakfast with portions visible',checks=[['510-360',150],['23-21',2],['360-330',30]])

def write():
 D.mkdir(exist_ok=True)
 (D/'articles.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
 sources=[{'url':u,'label':v[0],'status':'inspected','researchDate':'2026-10-04','locale':'U.S. nutrition labels; SI measurements','notes':v[1],'method':'Opened current official source with web tool; body inspected; no fabricated expert review.'} for u,v in source_info.items()]
 (D/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Authored',len(rows),'distinct articles')
if __name__=='__main__':write()
