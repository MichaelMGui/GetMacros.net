"""Final distinct worked decisions: source reading, budget constraints and meal arithmetic."""
from author_batch_four import *
PREFIX='https://www.nist.gov/pml/owm/metric-si-prefixes'
source_info[PREFIX]=('NIST: metric prefixes','Milli and micro represent powers of ten; supports the conversion between milligrams and micrograms.')

analysis('menu-pdf-filename-not-edition-date','A menu PDF filename is not its verified edition date','Read the printed source instead of turning a download name into a review date.','Distinguish actual printed edition from file naming and retrieval using Arby’s and SONIC.',[10,117],'''A nutrition PDF’s filename can suggest a date without establishing the date printed inside it. Arby’s linked file contains JULY_2026 in its name while the inspected edition is June 2026. SONIC’s download name contains September material while its extracted cover says Summer 2026. Keep that disagreement visible.

## Three dates have different jobs

A printed edition describes what the document claims about itself. A retrieval date records when GetMacros obtained it. A filename is a storage label. None proves when every restaurant changed a recipe or last verified a kitchen portion.

The example rows below show the exact values retained from the inspected sources. Their presence does not mean the filename supplies a stronger nutrient claim than the body of the document.

## What an honest source note looks like

Record the official URL, the portion, the printed date where established and the retrieval date separately. If the edition cannot be resolved confidently, mark it unavailable instead of choosing a convenient month. October 4, 2026 is a retrieval date here, not a claim that every record was freshly reformulated that day.

## When the discrepancy matters

If two official documents give different values, match the market, item and portion before deciding which applies. A later-looking filename alone cannot settle it. Use the current restaurant guidance for an actual changed order and report the conflict through corrections when necessary. Source transparency is more useful than a reassuring date that the evidence does not support.''',category='Sources and methods')

snapshot('burger-variants-not-nine-base-burgers','Nine In-N-Out rows do not mean nine base burgers','Standard, sauce and lettuce-wrap variations change the count.','Explain how documented variants expand record counts without inflating distinct base menu products.', '''The In-N-Out part of the expansion has nine records, arranged around three base burger names. Each base has its standard-with-onion row, a published mustard-and-ketchup variation and a published Protein Style variation. Nine documented choices do not mean nine unrelated base burgers.

## The variations deserve their own values

They are separate records because calories, macros, sodium or serving weight change. A finder must not merge them and keep a single convenient nutrient total. Equally, a coverage claim should not describe the nine rows as nine completely different burger products.

## Count the unit you actually mean

“Source-defined orders” includes variations with their exact portion assumptions. “Base burger names” groups those variations. “Restaurants” counts chains, not the number of local outlets. A statistic becomes misleading when its label changes while the denominator stays the same.

## What this means for browsing

Seeing several versions can help you choose an explicitly supported build. It does not imply that every off-menu alteration has been calculated or that all options are available everywhere. Fries, drinks and additional packets are outside these nine burger rows.

The table shows the three-by-three structure in the January 2026 source. This is a classification of the inspected records, not a menu sales analysis or a claim about the popularity of lettuce wraps. A modest count with a precise label is more useful than a larger number that hides repeated base names.''',{'type':'inNOutVariants'},['Base name','Standard','Sauce variation','Protein Style'],[['Hamburger',1,1,1],['Cheeseburger',1,1,1],['Double-Double',1,1,1]])

analysis('saved-meal-source-version-check','A saved meal is a bookmark, not a frozen restaurant promise','Recheck the build when a menu or official source changes.','Use saved meal state responsibly when source-defined recipes may change.',[305,306],'''Saving an order keeps it easy to find again. It should not imply that the restaurant will keep the same recipe, serving, price or availability indefinitely. A useful saved record retains enough identity to compare it with the current source later.

## Keep more than the title

QDOBA’s Chicken Queso Bowl and Burrito share a name family but list different totals: 750 versus 1,050 kcal and 43 versus 51 g protein. A saved note saying only “chicken queso” loses the most important distinction. Keep restaurant, exact format, serving scope and source together.

## What to recheck before using it

Confirm that the current official entry still describes the same market and build. If you added extra protein or removed an ingredient, the standard saved row may not describe your modification. A source retrieval date records an inspection, not a guarantee about the next order.

## Sharing needs the same context

A link or screenshot is more useful when it shows the exact meal and included items. Do not send a calorie figure with its portion label cropped away. Someone choosing a different format or local menu version may otherwise log a wrong total with complete confidence.

## If a figure changes

Use the updated matching source rather than averaging old and new values. Report a discrepancy when its basis is unclear. The table below is a concrete reminder that a closely named pair can differ before any menu update happens; saving the correct identity is essential.''',category='Using GetMacros',checks=[['1050-750',300]])

analysis('nutrition-totals-not-ingredient-recipe','Can nutrition totals reveal a restaurant recipe?','Six nutrient numbers cannot tell you every ingredient quantity.','Explain why record totals cannot reverse-engineer a meal or undocumented customization.',[305,311,353],'''No. Calories, protein, carbs, fat, fiber and sodium do not uniquely reveal a restaurant’s recipe. Many ingredient combinations can produce similar totals. A precise-looking row cannot recover missing ingredient weights or prove which component should be removed.

## The unknowns outnumber the totals

A bowl might contain several ingredients, sauces and preparation steps. The table supplies selected nutrient totals, not every ingredient quantity or cooking loss. QDOBA’s named bowls and Noodles & Company’s chicken pasta retain their full identities; none is an ingredient-level recipe in GetMacros.

## A matching value is not a matching build

If two meals both list 43 g protein, they still might have different food weights, ingredients and other nutrients. Solving one line does not verify the rest. Treating a missing sauce quantity as whatever makes calories balance would invent data rather than extract it.

## What subtraction can establish

Subtracting two complete rows gives a difference between those recorded orders. It isolates an ingredient only when the source explicitly establishes compatible builds that differ in that ingredient and its amount. Otherwise multiple changes may be hidden inside the recipe names.

## A better path

Look for official component information, a documented customization or a clearly defined standard variation. When it is absent, keep the modified total unknown. The complete-order records below remain useful for choosing between published builds; they simply do not become recipes or independent ingredient measurements because a calculator can subtract them.''',category='Macro fundamentals')

analysis('restaurant-protein-cost-receipt-prices','Use your receipt to compare restaurant protein value','Official protein can be paired with your actual paid price, with extras kept separate.','Worked price-per-protein comparison uses verified protein and explicitly invented receipt amounts.',[160,170],'''Restaurant nutrition data does not supply your local checkout price. If you want a protein-cost comparison, pair the verified order’s protein with an actual current price for that same order. The example prices here are invented to explain the method.

## A receipt example with real protein inputs

Culver’s Single ButterBurger lists 20 g protein and Grilled Chicken Sandwich lists 36 g in the linked guide. Suppose their food-only prices are $5 and $8 in the same currency. The ratios are $5 ÷ 20 = $0.25 per protein gram and $8 ÷ 36 ≈ $0.22 per gram.

The sandwich has the better ratio in this example, but buying it still requires $3 more. A budget decision needs both the ratio and the money you must actually spend. The prices are not advertised or verified Culver’s prices.

## Keep the receipt boundary compatible

Do not use a combo price with a sandwich-only protein total unless you explicitly explain that mismatch. If fries or a drink are included in the paid amount, their documented nutrients belong in the complete order calculation as well.

## What the result leaves out

Protein value does not rank flavor, hunger satisfaction or every nutrient. The older Culver’s guide also needs its source date retained. Taxes, delivery charges and tips may change your outlay; name what the price includes. A ratio is useful only when its numerator and denominator refer to the same actual purchase.''',category='Budget and value',checks=[['5/20',.25],['8/36',8/36],['8-5',3]])

analysis('two-person-restaurant-budget-constraints','Choose two orders within one budget','A lower price per protein gram may still exceed the money available.','Solve a two-person menu-selection budget using real nutrient rows and invented prices.',[160,170],'''For two people, the useful question may be “Which two orders fit our budget?” rather than “Which single item has the best protein ratio?” A small combination table can make the spending decision clear without pretending that nutrition alone chooses the meal.

## Set transparent example prices

Use Culver’s Single ButterBurger at an invented $5 and Grilled Chicken Sandwich at an invented $8, in the same currency. With a $12 food-only budget, two burgers cost $10, a mixed pair costs $13 and two chicken sandwiches cost $16. Only the two-burger pair fits that example ceiling.

Its combined published protein is 40 g and energy 780 kcal, across two orders. These are totals for the pair, not a recommendation that one person should eat both or that each person needs an equal nutrient amount.

## Show the unavailable option honestly

The mixed pair would supply 56 g protein, but it exceeds the example budget by $1. Saying it has better protein value does not remove that cash constraint. A real offer or local price could change the decision, so recalculate from current prices rather than treating the invented figures as a menu.

## Count the complete purchase

Extras, tax and fees are excluded from this teaching budget. If they apply, subtract them from the available money before choosing food or include them explicitly in each option. Prices do not come from the nutrition guide; only the stated standard-order nutrient inputs do.''',category='Budget and value',checks=[['2*5',10],['5+8',13],['2*8',16],['20*2',40],['390*2',780],['20+36',56]])

analysis('equal-tax-protein-value-ranking','Does the same percentage tax change protein-value rankings?','A shared percentage multiplies every ratio equally; fixed charges behave differently.','Prove a shared proportional price multiplier preserves ranking using exact source protein and invented costs.',[160,170],'''The same percentage added to every food price does not change their order by cost per protein gram. It multiplies each ratio by the same factor. This is arithmetic, not tax guidance or a claim about the rates at a particular restaurant.

## Work the example

Suppose a 20 g-protein Culver’s Single ButterBurger costs an invented $5 and a 36 g-protein Grilled Chicken Sandwich costs $8. Their food-only ratios are $0.25 and about $0.22 per gram. An invented 10% addition makes the prices $5.50 and $8.80, giving $0.275 and about $0.244 per gram.

The same order remains lower per gram because both original ratios were multiplied by 1.10. The overall amount spent has increased, even though the comparison ranking has not changed.

## Check whether the percentage is really shared

Different discounts, taxed item categories or fees can break that simple assumption. A fixed delivery fee per order also behaves differently from a proportional addition. Describe the charge basis before using a calculator rather than putting every checkout cost into one mysterious percentage.

## Keep nutrition and price aligned

The protein figures come from named standard orders in the older linked guide. The prices and percentage are invented. If your receipt covers a combo, include compatible combo nutrients or separate its components first. This calculation tells you how the example ratios respond to a common multiplier; it does not tell you which order is best overall.''',category='Budget and value',checks=[['5*1.1',5.5],['8*1.1',8.8],['5.5/20',.275],['8.8/36',8.8/36]])

analysis('restaurant-value-your-nutrient-not-protein','Value per fiber gram asks a different question','The nutrient in the denominator changes what a price comparison means.','Compare fiber cost with protein cost for actual burrito data using transparent hypothetical prices.',[69,70],'''Protein per dollar is only one possible value calculation. If fiber is the nutrient you want to compare, use fiber in the denominator instead. Keep the calculation’s name specific; changing the denominator changes the question.

## Two burritos and invented prices

Del Taco’s Eight Layer Veggie Burrito lists 9 g fiber and 18 g protein. Its Bean & Cheese green-sauce burrito lists 15 g fiber and 24 g protein. Suppose they cost an invented $6 and $5 respectively, in one currency.

Fiber cost is $6 ÷ 9 ≈ $0.67 per gram for the veggie burrito and $5 ÷ 15 ≈ $0.33 for bean-and-cheese. Protein cost is about $0.33 and $0.21 per gram respectively. These prices are teaching assumptions, not verified local menu prices or a promotion.

## Name the trade-off outside the ratio

The complete orders differ in calories, sodium, serving mass and ingredients. A lower cost per fiber gram cannot certify allergen safety, determine hunger or decide dietary preferences. Neither calculation measures every reason to choose lunch.

## Do not divide by an unknown

An exact nutrient ratio requires a supported numeric amount. A less-than fiber value or missing price cannot be replaced with zero to produce a confident ranking. When your actual receipt and current source are available, use those matching inputs. The table below supplies the exact published standard-food nutrient quantities while leaving local prices outside the official data.''',category='Budget and value',checks=[['6/9',6/9],['5/15',5/15],['6/18',6/18],['5/24',5/24]])

analysis('breakfast-bacon-format-sodium-cross-chain','A bacon breakfast comparison needs its bread format','Arby’s and SONIC have similar-calorie choices with different sodium.','Choose bacon morning formats across chains without treating meat type as the decisive nutrient variable.',[33,151,154,145],'''Bacon alone does not define the breakfast. Arby’s Bacon, Egg & Cheese Croissant and SONIC’s brioche, Croissonic and burrito formats fall between 430 and 470 kcal in these source rows, yet their sodium and protein are not equal.

## Read the cluster rather than choosing by the filling

Arby’s croissant is 430 kcal, 18 g protein and 1,010 mg sodium. SONIC’s Brioche Sandwich Bacon is 440 kcal, 20 g and 1,820 mg. Its Croissonic Bacon is 430 kcal, 18 g and 1,540 mg; Breakfast Burrito Bacon is 470 kcal, 25 g and 1,540 mg.

The two 430 kcal croissant-style entries tie on listed protein but differ by 530 mg sodium. The comparison does not prove that either restaurant uses identical bacon, eggs, cheese or bread.

## Avoid attributing everything to one ingredient

A full breakfast difference can include portion, recipe and bread changes. It is not an isolated bacon experiment. Removing bacon from one order is not equivalent to substituting another published order with a convenient lower number.

## Make the order practical

Confirm breakfast and regional availability before selecting a recorded format. A coffee, side of potatoes or extra sauce is separate from these food rows. The meaningful choice is an available complete breakfast with its documented portion, not a claim that one bread or meat is always better. The calorie range here is a description of four selected entries, not a recommendation for how much breakfast to eat.''',category='Breakfast decisions',checks=[['1540-1010',530],['470-430',40]])

analysis('sonic-ultimate-breakfast-not-extra-protein-rule','SONIC’s Ultimate breakfast burrito: what changes?','A bigger name adds more than just protein.','Compare bacon, SuperSONIC and Ultimate breakfast burritos as three distinct builds.',[145,158,159],'''SONIC’s Ultimate Meat & Cheese Breakfast Burrito lists more protein than the Bacon Breakfast Burrito, but the difference is not only protein. Its full recipe has more calories, fat and sodium. The SuperSONIC Breakfast Burrito is a third named build rather than an intermediate serving of the same recipe.

## Read the complete totals

Bacon Breakfast Burrito is 470 kcal and 25 g protein. SuperSONIC Breakfast Burrito is 590 kcal and 24 g. Ultimate Meat & Cheese is 820 kcal and 29 g. Moving from Bacon to Ultimate adds 350 kcal but only 4 g listed protein.

Ultimate also lists 56 g fat versus Bacon’s 25 g, and 2,190 versus 1,540 mg sodium. Those differences belong to whole-order recipes. They do not establish the nutrition of an extra bacon strip or cheese slice in isolation.

## The middle name does not predict the middle nutrient

SuperSONIC has fewer grams of protein than the Bacon entry despite its larger calorie total. Its 3 g fiber is above the other two recorded values. Different nutrients can point to different choices, so a premium-sounding title cannot rank every line.

## Use the build you actually order

Do not log Ultimate under the ordinary bacon row because the names overlap. Keep the exact title and count, then add any drink or side separately. These comparisons do not decide your energy needs or rate the foods morally. They show what changes between three published U.S. breakfast orders.''',category='Breakfast decisions',checks=[['820-470',350],['29-25',4],['56-25',31],['2190-1540',650]])

analysis('taco-johns-breakfast-taco-vs-burrito','Taco John’s breakfast taco or Meat & Potato Burrito?','The same bacon theme does not make these equivalent portions.','Compare compact breakfast taco and larger meat-and-potato breakfast format without component subtraction.',[288,295,290,297],'''Taco John’s breakfast taco and Meat & Potato Breakfast Burrito are different formats. Comparing their whole rows can help you choose an order, but it cannot measure the potato component by subtraction. Other ingredients and amounts may change too.

## Start with the bacon pair

Breakfast Taco, Bacon lists 340 kcal, 12 g protein, 28 g carbs, 19 g fat, 2 g fiber and 800 mg sodium. Meat & Potato Breakfast Burrito, Bacon lists 530 kcal, 18 g protein, 51 g carbs, 27 g fat, 4 g fiber and 1,310 mg sodium.

The burrito is 190 kcal and 6 g protein higher. Its sodium is 510 mg higher and its listed fiber doubles from 2 to 4 g. This describes the two recipes, not the nutrition of a stand-alone potato portion.

## Steak is a separate comparison

The steak taco lists 340 kcal and 14 g protein; the steak burrito 540 kcal and 21 g. Do not copy the bacon difference to that pair as a universal format adjustment. Use the source rows rather than inventing a common breakfast multiplier.

## Keep breakfast scope clear

Additional Potato Olés, a drink or a sauce packet is outside these rows. The burrito name includes its own meat-and-potato build; an extra side is still extra. Check availability at the location and keep the named order visible when saving the total. This guide does not prescribe a breakfast size or a personal nutrient target.''',category='Breakfast decisions',checks=[['530-340',190],['18-12',6],['1310-800',510]])

analysis('noodles-mac-protein-not-simple-add-on','Noodles & Company mac dishes: compare named builds','A chicken or pork mac is not plain mac plus an assumed meat value.','Compare three complete macaroni builds without converting their differences into ingredient claims.',[361,362,363],'''Noodles & Company publishes separate regular-size Creamy Cheddar Mac, Buffalo Chicken Ranch Mac and Pulled Pork BBQ Mac totals. Use those named rows if you are choosing among them. They are not verified equations for plain mac plus a standard meat portion.

## Three recipes with different profiles

Creamy Cheddar Mac lists 1,050 kcal and 46 g protein. Buffalo Chicken Ranch Mac lists 1,380 kcal and 70 g. Pulled Pork BBQ Mac lists 1,240 kcal and 63 g. Their carbohydrate and fat totals differ too, as the table shows.

Buffalo Chicken Ranch is 330 kcal and 24 g protein above Creamy Cheddar. Its sodium is 3,450 versus 1,910 mg: a 1,540 mg difference. That gap cannot be assigned entirely to chicken because ranch, sauce and the rest of the assembly are part of the named build.

## An addition is not automatically a substitution

Ordering extra protein on a base dish creates another calculation requiring the exact extra portion. It does not automatically create one of these named recipes. Similarly, removing a topping cannot be calculated from unrelated complete-dish differences.

## Compare the relevant whole order

If a minimum protein amount is your filter, check it alongside the full energy and sodium rather than assuming the largest protein number settles the choice. These are regular servings, not small or Duo entries, and extra sides or drinks remain separate. The table describes three selected recipes rather than all ways to order macaroni.''',category='Lunch and dinner',checks=[['1380-1050',330],['70-46',24],['3450-1910',1540]])

analysis('el-pollo-loco-bowls-protein-bigger-build','El Pollo Loco bowls: Original, Grande or Double Chicken?','More protein arrives with a different complete bowl.','Compare three bowl tiers while refusing to infer doubling chicken from complete recipe differences.',[325,331,323],'''El Pollo Loco’s Original Pollo Bowl, Grande Avocado Chicken Bowl and Double Chicken Bowl are separate published builds. The last has the most listed protein of these three, but its total cannot be treated as simply twice the Original’s chicken.

## Keep names and serving sizes together

Original Pollo Bowl is 18.2 oz, 580 kcal and 41 g protein. Grande Avocado Chicken Bowl is 22.2 oz, 790 kcal and 49 g. Double Chicken Bowl is 24.2 oz, 930 kcal and 74 g. Their complete ingredient quantities are not established by the name alone.

Double Chicken is 350 kcal and 33 g protein above Original. It also lists 2,670 mg sodium compared with 2,030 mg. The Original-to-Grande step adds 210 kcal and 8 g protein, a different relationship. There is no common size multiplier that reproduces every nutrient.

## Do not use a menu tier as a formula

“Double” names an offered build; it does not mean every macro or the entire bowl’s weight doubles. A standard bowl with extra chicken would need exact official component information to calculate independently.

## Choose the actual meal

Compare available named portions alongside your relevant limits and preferences. This table does not claim a personal protein requirement or that a larger bowl is better. Drinks, extra sides and unrecorded changes are excluded. The source is the U.S. September 2026 guide; use the current matching row if a local standard build changes.''',category='Lunch and dinner',checks=[['930-580',350],['74-41',33],['2670-2030',640],['790-580',210]])

add('recipe-combined-batches-not-average-serving','Combine two batches without averaging the wrong servings','Add whole-batch totals before dividing by the final serving count.','Recipe portions','Combine differently sized batches with weighted serving arithmetic.','Original two-batch sum with incorrect averaging explained.', '''When two batches have different serving counts, average serving values only after accounting for their sizes. A simple average of the two printed per-serving numbers can give the wrong result for the combined food.

## A worked batch example

Suppose batch A totals 1,200 kcal across four equal servings, while batch B totals 900 kcal across three. Together they provide 2,100 kcal in seven servings at 300 kcal each. Here both original portions happen to be 300 kcal, so their average looks harmless.

Now suppose B has only two equal servings instead. Its portions are 450 kcal; the combined six portions still sum to 2,100 kcal, averaging 350. The simple average of 300 and 450 is 375, which is wrong because the batches contribute different numbers of portions.

## Use the whole quantities

Add whole-batch protein, carbs and fat separately, then divide by the number of equal portions actually made. If you mix by weight and serve unequal amounts, weigh the finished combined batch and calculate each portion’s fraction instead of assuming the old serving counts survive.

## Keep the input basis compatible

These are invented figures, not a tested recipe. Actual batches need the amounts used, correct raw or prepared label basis and a clear final yield. Do not combine a per-serving entry with a whole-batch entry without converting it first. The useful rule is to add compatible totals before calculating a new portion, rather than averaging attractive-looking labels.''',src=(SERVE,FDC),tool='recipe-macro-scaler.html',tool_label='Calculate a combined batch',checks=[['1200+900',2100],['2100/7',300],['900/2',450],['2100/6',350],['(300+450)/2',375]])

add('recipe-repeated-ingredient-two-label-bases','The same ingredient listed twice can use two label bases','Convert each quantity before combining it.','Recipe portions','Resolve repeated ingredient quantities that use different portion labels.','Two-stage sum checks that prevent adding serving numbers before unit conversion.', '''A recipe may use the same ingredient in more than one step. Keep each amount aligned with its label basis before adding nutrition. Two lines saying “one serving” can refer to different amounts if you copied them from different entries.

## An invented two-step example

Suppose a label gives 100 kcal per 50 g. You use 75 g in a filling and 25 g in a topping. The filling contributes 150 kcal and the topping 50, totaling 200 kcal from 100 g. Counting both amounts as one serving would happen to produce the same energy here, but hide the wrong reasoning.

If the topping were 40 g instead, it would contribute 80 kcal and the ingredient total would be 230. The final quantity is 115 g, or 2.3 label servings. A list with two recipe steps still does not mean two label servings.

## Consolidate after conversion

You can add the compatible gram quantities first and scale once, or calculate each step and then add. Both methods should agree. Use that agreement as a check before dividing the whole recipe into portions.

## Do not consolidate incompatible forms

Raw and cooked entries, drained and undrained foods, or different product labels may need separate treatment. A repeated ingredient name alone does not prove identical nutrition per gram. This article’s figures are invented to demonstrate bookkeeping, not kitchen testing. Keep the current product label and actual amounts attached to the recipe so a later change can be recalculated.''',src=(SERVE,FOUND),tool='recipe-macro-scaler.html',tool_label='Scale the actual recipe quantities',checks=[['75/50*100',150],['25/50*100',50],['40/50*100',80],['150+80',230],['115/50',2.3]])

add('recipe-sauce-made-vs-sauce-used','Made 300 g of sauce but used only 80 g?','The main dish needs the amount transferred, not the whole sauce batch.','Recipe portions','Allocate a separately prepared sauce batch to another dish by actual transferred mass.','Two-recipe calculation with leftovers reconciliation.', '''A sauce prepared separately has its own batch total. If only part enters the main dish, include only that part in the dish calculation. The remainder stays with the sauce batch rather than disappearing or being counted twice.

## Follow the transferred amount

Suppose an invented sauce batch weighs 300 g and contains 600 kcal and 12 g protein. You stir 80 g into a dish. That is 80 ÷ 300 of the sauce, adding 160 kcal and 3.2 g protein to the dish. The remaining 220 g retains the corresponding 440 kcal and 8.8 g protein under the same uniform-mixture assumption.

## Check that the totals reconcile

The dish’s sauce contribution plus the remainder should return the whole sauce batch: 160 + 440 = 600 kcal. If you also enter the full 600 kcal into the main recipe, you count sauce that was never transferred. If you count the used 80 g again when eating the dish, you duplicate it.

## Use the finished sauce basis

Weigh after its final preparation and account for the ingredients actually retained. Separating oil, uneven solids or residue can make a simple mass fraction inaccurate. Uniformity is an assumption, not a laboratory result.

The numbers here are invented and the method does not certify a recipe’s shelf life or safety. It is a way to connect two recipe calculations cleanly: sauce batch first, transferred portion second, finished main-dish servings last.''',src=(SERVE,FDC),tool='recipe-macro-scaler.html',tool_label='Calculate the transferred portion',checks=[['80/300*600',160],['80/300*12',3.2],['300-80',220],['220/300*600',440],['220/300*12',8.8]])

add('recipe-target-batch-portions-integer','A batch can yield six portions plus a smaller remainder','Do not round the serving count and lose the leftover food.','Recipe portions','Handle an integer portion count and remainder without invented full-serving totals.','Mass-conservation example with separate leftover serving.', '''A batch does not always divide into a whole number of your chosen portion size. Keep the smaller remainder visible rather than rounding it into a full serving or pretending it is absent.

## Divide the finished weight

Imagine a uniform 1,000 g batch containing 2,000 kcal and 100 g protein. At 150 g per portion, you can make six full portions totaling 900 g, plus a 100 g remainder. Each full portion contains 300 kcal and 15 g protein. The remainder contains 200 kcal and 10 g protein.

Rounding 1,000 ÷ 150 up to seven identical portions would claim 1,050 g of food. Rounding down to six and discarding the remainder from your records would omit 200 kcal if you later eat it.

## Reconcile the batch

Six full portions plus the remainder return 2,000 kcal and 100 g protein. That check helps reveal a mistaken portion count before the recipe is saved. The smaller container can be labeled with its actual amount instead of the standard 150 g value.

## When equal weight is not enough

This method assumes an evenly mixed batch. Separate chicken pieces, toppings or uneven sauce may require component-level portioning. The invented example is arithmetic, not a kitchen-tested recipe or advice to eat a particular portion. Use your actual final yield and compatible ingredient records, and follow appropriate storage guidance independently of the nutrient calculation.''',src=(SERVE,FDC),tool='recipe-macro-scaler.html',tool_label='Calculate full portions and the remainder',checks=[['150*6',900],['1000-900',100],['150/1000*2000',300],['100/1000*2000',200],['6*300+200',2000]])

add('recipe-recalculate-new-product-label','Changing brands means updating the ingredient record','An equal spoonful can carry a different label value.','Recipe portions','Recalculate a stored recipe after one branded input label changes.','Difference method versus full rebuild cross-check with explicit portion basis.', '''A saved recipe should use the label for the product actually added. Switching brands while keeping the amount can change nutrition, even when the ingredient name is the same. Update the input before reusing the old portion total.

## Calculate the replacement difference

Suppose an invented recipe includes 60 g of a product labeled 90 kcal per 30 g. That input contributes 180 kcal. A replacement label gives 70 kcal per 25 g, so the same 60 g contributes 168 kcal. The recipe’s whole-batch energy decreases by 12 kcal.

If the old batch total was 1,200 kcal, the updated total becomes 1,188. For four equal portions, that is 297 kcal instead of 300. Do not compare the labels’ 90 and 70 directly: their stated portions differ.

## Update every supported nutrient

Protein, carbs, fat and other fields may change independently. A 12 kcal difference does not reveal their new values. Replace the ingredient’s compatible nutrient inputs separately, then rebuild the recipe and preserve missing data where necessary.

## Keep the version useful

Note the product and label basis beside the quantity so the saved recipe can be understood later. This is an invented arithmetic case rather than a tested recipe or a claim about any current brand. A brand substitution can also change ingredients or allergens, which the macro totals do not certify. Use the new packaging for those questions rather than relying on an old saved label.''',src=(SERVE,ALLERGY),tool='recipe-macro-scaler.html',tool_label='Recalculate after a label change',checks=[['60/30*90',180],['60/25*70',168],['1200-180+168',1188],['1188/4',297]])

add('milligram-microgram-mineral-label','Milligrams and micrograms: a thousand-fold label difference','Check the unit before moving a nutrient into your notes.','Macro fundamentals','Prevent a unit-prefix error when recording micronutrient labels.','Original microgram-to-milligram example clearly separated from nutrition targets.', '''A milligram and a microgram are different amounts. One milligram is 1,000 micrograms. If you copy a nutrient value into a table without its unit, a harmless-looking decimal can become a thousand-fold recording error.

## Keep the prefix with the number

An invented label listing 20 micrograms records 0.020 milligrams, not 20 milligrams. Conversely, 2 milligrams is 2,000 micrograms. The arithmetic converts the unit; it does not change the amount of the nutrient in the food.

## Different nutrients need different units

Protein is commonly shown in grams, sodium in milligrams and some vitamins in micrograms. Adding or comparing the raw numbers without identifying the nutrient and unit is meaningless. Twenty micrograms of one vitamin is not automatically more or less useful than 2 milligrams of another.

## Daily Values are another field

A unit conversion is not a Daily Value calculation. To calculate a percentage, you need the reference amount for that exact nutrient in the same unit. Do not use a sodium denominator for a vitamin or guess a vitamin target from the size of its number.

## A simple recording check

Write the nutrient name, numeric amount, unit and serving together. When converting, show the original and converted amount side by side, then verify that multiplying back returns the starting value. NIST supports the metric-prefix relationships and FDA supports label serving context. The examples here introduce no supplement dose, medical advice or personal nutrient target.''',src=(PREFIX,DV),checks=[['20/1000',.02],['2*1000',2000],['.02*1000',20]])

add('calorie-units-kcal-kilojoules','Calories, kcal and kilojoules: compare energy units first','An energy number needs its unit before it can be compared.','Macro fundamentals','Convert displayed energy units without confusing kilojoules with food grams.','Invented energy conversion and inverse check with explicit thermochemical factor.', '''Food energy may be displayed as Calories, kcal or kilojoules. In nutrition use, a food Calorie denotes a kilocalorie. A kilojoule is another energy unit, so a larger printed kilojoule number does not automatically mean more energy than a smaller kcal number.

## Use a named conversion

NIST lists the thermochemical calorie relationship. Using 1 kcal = 4.184 kJ, an invented 250 kcal portion corresponds to 1,046 kJ. Converting back, 1,046 ÷ 4.184 returns 250 kcal. Rounding displayed figures may make a real label’s reverse conversion differ slightly.

## Compare the same serving too

Converting the unit does not align portions. A 250 kcal per-serving entry cannot be compared with kJ per 100 g until both the energy unit and amount of food match. Keep the serving description attached throughout the calculation.

## Energy is not food weight

Neither kcal nor kJ is a gram amount. You cannot divide a dish’s calories by its protein grams and call the result the weight of its ingredients. Macro quantities and energy describe different properties of the same food.

## A useful cross-check

If an imported value looks several times larger than expected, check whether the unit changed before assuming the recipe did. Retain the official source’s published energy for the exact order, and label any conversion clearly. The example does not prescribe daily calorie needs, reconstruct a restaurant’s missing values or turn a rounded label into a laboratory measurement.''',src=(CONVERT,CAL),checks=[['250*4.184',1046],['1046/4.184',250]])

add('meal-calculation-two-serving-units','Two servings of food do not mean two servings of every topping','Different components need their own quantity multipliers.','Lunch and dinner','Calculate a doubled food base with a single topping portion instead of doubling the entire tray.','Original mixed-count nutrition table and arithmetic reconciliation.', '''Doubling the food base does not automatically double every item in your meal. A topping, sauce or drink can keep its original quantity. Apply a separate multiplier to each component before adding the total.

## Work the actual counts

Imagine a food base with 250 kcal and 12 g protein per portion, plus a topping with 60 kcal and 2 g protein. Two base portions with one topping contain 560 kcal and 26 g protein. Doubling the combined single-serving meal would give 620 kcal and 28 g, counting a second topping you did not use.

## Keep the component list short and precise

Write “base × 2; topping × 1” rather than “meal × 2.” If you add half a topping later, calculate that amount from its own source portion. A recipe step, serving count and purchase count are not interchangeable measurement units.

## Check the complete result

The base contributes 500 kcal and the topping 60. Their sum should equal the final 560. Perform the same calculation for each nutrient you actually have. Missing sodium or fiber cannot be reconstructed from a calorie total.

The numbers are invented and describe no named restaurant or tested recipe. With real food, use the correct standard portion, product label and preparation basis for each entry. This method is especially useful when a meal includes several amounts but only one component changes; it prevents a convenient “double” button from silently multiplying the wrong items.''',src=(SERVE,FDA),tool='nutrition-label-comparison-tool.html',tool_label='Compare the component portions',checks=[['250*2+60',560],['12*2+2',26],['(250+60)*2',620],['(12+2)*2',28]])

add('two-meal-total-not-day-recommendation','Two restaurant meals are a subtotal, not a daily diet','A sum can be accurate while still leaving the rest of the day unknown.','Lunch and dinner','Add two exact meal records while avoiding a daily adequacy claim.','Source-backed two-order sum with explicit limits on daily interpretation.', '''Adding two restaurant orders can give a useful subtotal. It does not tell you whether your whole day meets your needs, and it does not include unrecorded breakfast, snacks, beverages or extras.

## An example with documented meals

Culver’s Single ButterBurger lists 390 kcal and 20 g protein in its linked guide. QDOBA’s Chicken Queso Bowl lists 750 kcal and 43 g. Together those two standard orders total 1,140 kcal and 63 g protein. Their published sodium totals add to 2,300 mg.

## Keep the subtotal labeled

That is the sum of two selected U.S. orders, not a meal plan or a prescription for a person. A daily energy estimate depends on other information; protein and sodium need their own context. Matching one familiar reference number does not verify the rest of the day or imply that no more food should be eaten.

## Account for what was actually ordered

The burger record excludes extra sides and a drink. The bowl is the named standard build, not every customizable chicken bowl. Add documented extras separately and do not repeat included components. The Culver’s source remains its older July 2025 edition despite October retrieval.

## Use the numbers for one clear job

A subtotal can help you see what has been counted and what remains unknown. It cannot establish medical suitability, ingredient variety, hunger or adequacy from two rows. Save the exact orders and units so the arithmetic can be checked, rather than attaching a reassuring label to an incomplete day.''',src=(RECORDS[160]['provenance']['source'],RECORDS[305]['provenance']['source'],CAL),tool='restaurant-meal-finder.html',tool_label='Compare exact recorded meals',scope='The two real source-defined orders are an arithmetic example, not a prescribed daily intake. Extra items and the rest of the day are not included.',checks=[['390+750',1140],['20+43',63],['480+1820',2300]])
rows[-1]['tableFacts']=[{'recordKey':RECORDS[i]['recordKey'],'values':RECORDS[i]['values'],'serving':RECORDS[i]['provenance']['serving'],'sourcePage':RECORDS[i]['sourcePage'],'sourceRow':RECORDS[i]['sourceRow']} for i in [160,305]]

# Registry method notes distinguish current web reads from locally inspected official PDFs.
original_write=write
def write():
 original_write()
 p=D/'sources.json';registry=json.loads(p.read_text(encoding='utf-8'))
 for source in registry:
  if source['url'] in [c['source']['url'] for c in PAYLOAD['chains']]:
   source['locale']='U.S. official restaurant orders'
   source['method']='Official PDF downloaded by data verifier; relevant source rows and table headings inspected locally by editorial. Published fields cross-checked against the versioned record payload; no laboratory or expert review claimed.'
   if 'in-n-out.com' in source['url']:source['method']='Current official PDF opened with web tool; all nine burger rows, headings and January 2026 edition inspected. Local snapshot not claimed.'
 p.write_text(json.dumps(registry,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':write()
