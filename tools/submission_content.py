"""Reviewed, focused copy for pages with conflicting or repetitive legacy text."""
PAGES = {}
def page(slug, title, intro, body, sources, related):
    PAGES[slug+'.html'] = dict(title=title, intro=intro, body=body, sources=sources, related=related)

RDA = ('https://www.ncbi.nlm.nih.gov/books/NBK610205/', 'AHRQ: protein intake and reference values')
PROTEIN = ('https://pmc.ncbi.nlm.nih.gov/articles/PMC5477153/', 'ISSN: protein and exercise')
MUSCLE = ('https://pubmed.ncbi.nlm.nih.gov/28698222/', 'Protein and resistance training: systematic review')
ENERGY = ('https://www.niddk.nih.gov/bwp', 'NIDDK Body Weight Planner')
MIFFLIN = ('https://pubmed.ncbi.nlm.nih.gov/2305711/', 'The Mifflin–St Jeor resting energy equation')
LABEL = ('https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label', 'FDA: understanding the Nutrition Facts label')
RANGES = ('https://www.ncbi.nlm.nih.gov/books/NBK208874/', 'National Academies: dietary reference tables')
TIMING = ('https://pmc.ncbi.nlm.nih.gov/articles/PMC5596471/', 'ISSN: nutrient timing')

page('what-are-macros','What are macros?',
     'Macros are protein, carbohydrates and fat. They provide energy and help your body work. Here is what the numbers mean when you plan a meal.', '''
<h2>What each macro does</h2>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Macro</th><th>Calories per gram</th><th>Main roles</th></tr></thead><tbody>
<tr><th scope="row">Protein</th><td>4</td><td>Builds and repairs tissues; helps make enzymes and antibodies.</td></tr>
<tr><th scope="row">Carbohydrates</th><td>4</td><td>Provide energy. Carb-rich foods can also supply fiber.</td></tr>
<tr><th scope="row">Fat</th><td>9</td><td>Provides essential fatty acids and helps absorb vitamins A, D, E and K.</td></tr></tbody></table></div>
<p>The 4, 4 and 9 figures are useful estimates. Label rounding, fiber and other ingredients can make a food’s printed calories differ slightly from this calculation.</p>
<h2>Calories vs. macros</h2>
<p>Calories describe how much energy food provides. Macros describe where much of that energy comes from. A calorie target can help with weight planning; looking at protein, carbs and fat can help you choose satisfying meals and support training.</p>
<p>No macro tells the whole story. Fiber, sodium, vitamins, minerals, allergies, cost and the foods you enjoy still matter.</p>
<h2>How do you work out your macros?</h2>
<ol><li>Estimate your daily calories for your activity and goal.</li><li>Choose a protein amount that fits your needs.</li><li>Include enough fat, then use carbs for the remaining energy.</li></ol>
<p>The free macro calculator does this arithmetic for you. Its result is a starting estimate, not an exact measurement of your needs.</p>
<h2>A simple example</h2>
<p>A sample 2,000-calorie day with 125 g protein and 60 g fat leaves about 240 g carbohydrate: 500 protein calories + 540 fat calories + 960 carbohydrate calories = 2,000. This demonstrates the math; it is not a target for everyone.</p>
<h2>Do you need to count macros?</h2>
<p>No. You can build meals around protein foods, grains or other carbs, fruit or vegetables, and fats without logging every gram. Tracking can be useful when you have a specific question, such as whether your meals contain enough protein.</p>
<p>You do not need to hit every number exactly. Portions, labels and calorie estimates all have uncertainty. Look for a manageable pattern rather than treating small daily differences as mistakes.</p>
''',[LABEL,RANGES],['calculators.html','calories-vs-macros-what-matters-more.html','how-to-calculate-macros-by-hand.html'])

page('how-much-protein-per-day','How much protein do you need per day?',
     'Your protein needs depend on your body size, training and health. Use these ranges as a starting point, then choose foods that make the target practical.', '''
<h2>The short answer</h2>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Context</th><th>Daily protein</th><th>Example at 70 kg / 154 lb</th></tr></thead><tbody>
<tr><th scope="row">Healthy adults: RDA</th><td>0.8 g/kg</td><td>56 g</td></tr>
<tr><th scope="row">Regular exercise: ISSN range</th><td>1.4–2.0 g/kg</td><td>98–140 g</td></tr>
<tr><th scope="row">Muscle-building planning range</th><td>About 1.6–2.2 g/kg</td><td>112–154 g</td></tr></tbody></table></div>
<p>These categories overlap. They are different reference points, not three rules you must add together.</p>
<h2>What does the protein RDA mean?</h2>
<p>The adult RDA of 0.8 g/kg is designed to cover the needs of nearly all healthy adults. It is not merely the amount that prevents severe deficiency, and it was not designed as a target for maximizing muscle gain.</p>
<p>People who train regularly may benefit from more. Research on resistance training found that average gains in fat-free mass leveled off around 1.6 g/kg/day, with uncertainty around that estimate. That is why practical training ranges often extend to about 2.2 g/kg.</p>
<h2>How do you calculate your target?</h2>
<p>Multiply your weight in kilograms by the chosen grams-per-kilogram amount. To convert pounds to kilograms, divide by about 2.2. For example, 75 kg × 1.6 g/kg = 120 g protein per day.</p>
<p>If using your current weight produces an unusually large or difficult target, a registered dietitian can help choose an appropriate weight basis. A goal-weight calculation is an option in some circumstances, not an automatic rule for everyone.</p>
<h2>How much protein should you eat per meal?</h2>
<p>Split the daily total in a way that fits your routine. A 120 g example could be three meals with 40 g each, or four with 30 g each. A larger dinner is not wasted because it exceeds 30 g.</p>
<p>Start with a meal that currently has little protein. Yogurt, eggs, tofu, beans, fish or chicken can help, depending on what you like. A protein shake is convenient for some people, but it is optional.</p>
<h2>When a general range is not enough</h2>
<p>Kidney disease, pregnancy, recovery from illness and other health circumstances can change your needs. Use advice from your clinician or dietitian instead of a general training range. More protein is not automatically better.</p>
''',[RDA,PROTEIN,MUSCLE],['calculators.html#protein-calculator','high-protein-foods-list.html','how-much-protein-can-your-body-absorb.html'])

page('protein','What does protein do in your body?',
     'Protein helps build and repair tissues, including muscle. Your body also uses it to make enzymes, hormones and antibodies.', '''
<h2>What is protein made of?</h2>
<p>Proteins are made from amino acids. Nine are called essential because your body cannot make enough of them; you get them from food. Digestion breaks food proteins into smaller parts that your body can use.</p>
<h2>Does eating protein build muscle?</h2>
<p>Protein supplies material for muscle repair and growth. Resistance training provides the stimulus. Eating extra protein without suitable training does not have the same effect as combining both.</p>
<p>Your overall daily intake matters more than finding one perfect post-workout food. Meals before and after training can both contribute.</p>
<h2>How much do you need?</h2>
<p>The adult RDA is 0.8 g per kilogram of body weight per day, an amount intended to meet the needs of nearly all healthy adults. Regular exercisers often use a higher range; the ISSN recommends 1.4–2.0 g/kg/day for most exercising individuals.</p>
<p>For a 70 kg adult, those figures are 56 g at the RDA and 98–140 g in the exercise range. They answer different questions. Our daily protein guide explains how to choose a starting point.</p>
<h2>Which foods contain protein?</h2>
<p>Meat, fish, eggs, milk, yogurt, tofu, tempeh, beans and lentils all contribute. Animal proteins and some plant foods, including soy, supply all nine essential amino acids in useful proportions. A varied plant-based diet can also meet protein needs; you do not have to combine particular foods at every meal.</p>
<ul><li>Breakfast: eggs, yogurt or tofu alongside the foods you already enjoy.</li><li>Lunch: beans, fish, chicken or tempeh in a sandwich, salad or bowl.</li><li>Dinner: a protein food with grains or potatoes and vegetables.</li></ul>
<h2>What if you are not getting enough?</h2>
<p>Long-term inadequate protein and energy intake can affect health, recovery and muscle maintenance. Tiredness, hair changes or poor recovery alone do not diagnose protein deficiency; they have many possible causes.</p>
<p>If you are losing weight unexpectedly, have persistent symptoms or struggle to eat enough, ask a qualified clinician or dietitian. Do not use a symptom checklist to diagnose yourself.</p>
''',[RDA,PROTEIN,('https://www.myplate.gov/eat-healthy/protein-foods','USDA MyPlate: protein foods')],['how-much-protein-per-day.html','high-protein-foods-list.html'])

page('carbs','What do carbs do in your body?',
     'Carbohydrates provide energy. Foods such as oats, rice, potatoes, fruit and beans can also bring fiber, vitamins and minerals to your meals.', '''
<h2>What counts as a carbohydrate?</h2>
<p>Carbohydrates include sugars, starches and fiber. Your body digests most sugars and starches into simple sugars, including glucose. Fiber behaves differently: it is not fully digested in the small intestine, and some types are fermented by gut bacteria.</p>
<h2>How do carbs help with exercise?</h2>
<p>Your muscles and liver store carbohydrate as glycogen. Muscle glycogen helps fuel exercise; liver glycogen helps maintain blood glucose between meals. Carb needs tend to rise with longer or more demanding training.</p>
<p>A short gym session does not require the same carb strategy as an endurance event. A familiar meal with rice, potatoes, bread, oats or fruit is often a practical starting point.</p>
<h2>Does your brain need carbs?</h2>
<p>The brain normally uses glucose for much of its energy. During prolonged fasting or a very-low-carbohydrate diet, it can also use ketones. The body can make glucose, so eating fewer carbs does not mean the brain stops receiving fuel.</p>
<p>That does not make a very-low-carb diet necessary or suitable for everyone. Your preferences, training, digestion and any medical advice matter.</p>
<h2>How many carbs should you eat?</h2>
<p>The adult reference range is 45–65% of calories. At 2,000 calories, that works out to about 225–325 g carbohydrate. This is a broad reference, not a requirement to match the same percentage every day.</p>
<p>A macro calculator may set protein and fat first, then assign the remaining calories to carbs. That can produce a different split. Use the approach that fits your needs, especially if you have been given a medical nutrition plan.</p>
<h2>Choose carbs you enjoy</h2>
<ul><li>Whole grains: oats, whole-wheat bread, brown rice or barley.</li><li>Beans and lentils: carbohydrate, fiber and protein in the same food.</li><li>Fruit and vegetables: fresh, frozen and canned options can all work.</li><li>Potatoes, pasta and rice: useful meal bases; portions and additions change the meal.</li></ul>
<p>On a U.S. food label, total carbohydrate already includes fiber and sugars. Do not add those lines again when calculating your portion.</p>
''',[RANGES,TIMING,LABEL,('https://pmc.ncbi.nlm.nih.gov/articles/PMC3900881/','Review: glucose and brain function')],['how-much-fiber-per-day.html','carbohydrate-label-portion-tool.html','what-to-eat-before-a-workout.html'])

page('fats','What does fat do in your body?',
     'Fat provides energy, essential fatty acids and help absorbing vitamins A, D, E and K. Both the type and amount matter.', '''
<h2>Why do you need fat?</h2>
<p>Fat is part of cell membranes and provides a concentrated source of energy: about 9 calories per gram. Your body needs essential fatty acids from food because it cannot make them itself.</p>
<p>Some fat with meals helps absorb fat-soluble vitamins. You do not need to add oil to every vegetable dish if the meal already contains fat from other foods.</p>
<h2>Which fats should you choose?</h2>
<p>Unsaturated fats are found in olive oil, nuts, seeds, avocado and fish. Replacing some saturated fat with unsaturated fat can improve blood cholesterol. Adding extra oil without replacing anything also adds calories.</p>
<p>Saturated fat is found in foods including butter, fatty meats, cheese and coconut oil. Industrial trans fat is a separate category and should be avoided. A food’s overall role in your diet matters more than a single “good” or “bad” label.</p>
<h2>How much fat should you eat?</h2>
<p>The adult reference range is 20–35% of daily calories. At 2,000 calories, that is about 44–78 g fat. Divide calories from fat by 9 to convert them to grams.</p>
<p>This range is a planning reference, not a diagnostic cutoff. Eating outside it on one day does not mean you have a deficiency or a hormone problem.</p>
<h2>Does dietary fat affect hormones?</h2>
<p>The body uses cholesterol to make steroid hormones and can produce cholesterol itself. This does not mean that eating more fat or cholesterol will reliably raise testosterone or improve muscle growth.</p>
<p>Research comparing low- and higher-fat diets has reported differences in testosterone, but the studies do not establish one ideal fat intake for everyone. Total energy intake and health also matter. Persistent symptoms need clinical assessment, not a higher-fat target based on a website.</p>
<h2>Easy ways to include fat</h2>
<ul><li>Add nuts or seeds to yogurt or oats.</li><li>Use olive oil or another unsaturated oil in cooking.</li><li>Include fish if you eat it, or plant foods such as walnuts and flaxseed.</li><li>Count dressings and sauces when comparing restaurant meals.</li></ul>
<p>Fat adds flavor and energy, so a modest portion can make a meal more satisfying. There is no need to remove it just because you are managing calories.</p>
''',[RANGES,('https://nutritionsource.hsph.harvard.edu/what-should-you-eat/fats-and-cholesterol/','Harvard Nutrition Source: fats and cholesterol'),('https://ods.od.nih.gov/factsheets/Omega3FattyAcids-HealthProfessional/','NIH: omega-3 fatty acids'),('https://pubmed.ncbi.nlm.nih.gov/33741447/','Low-fat diets and testosterone: systematic review')],['calculators.html#fat-calculator','how-to-read-a-nutrition-label.html'])

page('macros-for-weight-loss','How to set your macros for weight loss',
     'Start with a manageable calorie target, include enough protein, and choose a balance of carbs and fat you can keep eating comfortably.', '''
<h2>Start with calories</h2>
<p>Weight loss requires an energy deficit over time: using more energy than you take in. Estimate your maintenance calories first. The calculator’s weight-loss option reduces that estimate; it cannot predict your exact rate of loss.</p>
<p>A larger deficit is not automatically better. If you are persistently exhausted, hungry, struggling to recover or becoming distressed about food, reassess the plan.</p>
<h2>Keep protein in the plan</h2>
<p>Adequate protein and resistance training can help preserve muscle during weight loss. People who train often use about 1.6–2.2 g/kg/day as a starting range, but needs vary with body size, health and the size of the deficit.</p>
<p>Use a realistic target, then include protein foods in meals you already eat. A very high target that crowds out other foods is not automatically more effective.</p>
<h2>Choose your carbs and fat</h2>
<p>There is no single best macro percentage for weight loss. Carbs can support training and supply fiber; fats provide essential fatty acids and help with vitamin absorption. Choose amounts that leave room for both.</p>
<p>The adult fat reference range is 20–35% of calories. After choosing protein and fat, you can assign the remaining calories to carbs. This is one planning method, not the only way to eat well.</p>
<h2>One worked example</h2>
<p>At an illustrative 1,800 calories, 130 g protein provides 520 calories. Choosing 60 g fat provides 540 calories. The remaining 740 calories provide 185 g carbohydrate. These numbers show the calculation; they are not a universal weight-loss plan.</p>
<h2>What if your weight is not changing?</h2>
<p>Compare several weeks under similar conditions before changing your intake. Water, digestion and menstrual-cycle changes can hide a trend. Check whether portions, drinks, sauces or your activity have changed, rather than assuming your metabolism is broken.</p>
<p>Weight is only one check. Energy, recovery, hunger and whether you can live comfortably with the plan matter too. A qualified clinician or dietitian can help if your situation needs more than a general estimate.</p>
<h2>Do carbs have to be low?</h2>
<p>No. Lower-carb and lower-fat approaches can both support weight loss. The useful question is which meals help you maintain an appropriate intake while meeting your nutritional needs.</p>
''',[ENERGY,PROTEIN,RANGES],['calculators.html','how-much-protein-per-day.html','restaurant-meal-finder.html'])

page('macros-for-muscle-gain','How to set your macros for muscle gain',
     'Muscle gain depends on training, enough food and recovery. A useful macro plan supports those things without turning every meal into a calculation.', '''
<h2>Do you need a calorie surplus?</h2>
<p>A modest surplus can help support muscle gain, especially for experienced lifters. It is not an absolute requirement: some beginners, returning lifters and people with more stored body fat can gain muscle while maintaining or losing weight.</p>
<p>Start with a maintenance estimate. If you choose a surplus, increase food modestly and watch your training, recovery and weight trend. Eating much more does not make muscle grow at the same pace as the scale.</p>
<h2>How much protein helps?</h2>
<p>About 1.6–2.2 g/kg/day is a common muscle-building planning range. Research found an average benefit leveling off near 1.6 g/kg, with uncertainty around the estimate. More protein is not guaranteed to produce more muscle.</p>
<p>For a 75 kg person, that planning range is about 120–165 g/day. Split it across meals in whatever pattern is comfortable and practical.</p>
<h2>Keep room for carbs and fat</h2>
<p>Carbs help fuel demanding training. Rice, oats, potatoes, bread, pasta, beans and fruit are all options. There is no need to treat them as food you must earn.</p>
<p>Fat adds energy and essential fatty acids. The adult reference range is 20–35% of calories. After setting protein and fat, the remaining energy can come from carbs.</p>
<h2>A sample calculation</h2>
<p>An illustrative 2,400-calorie target with 150 g protein and 80 g fat leaves 270 g carbs: 600 + 720 + 1,080 = 2,400 calories. It demonstrates a split, not a target for every lifter.</p>
<h2>How do you know whether it is working?</h2>
<p>Look at several weeks of training performance, recovery, measurements and weight together. Strength can improve without a matching increase in muscle size, and early weight gain may include water and food in the digestive system.</p>
<p>Muscle-growth rates vary widely. Avoid treating a fixed number of kilograms per month as a promise. If weight is rising faster than intended without useful progress, review the surplus instead of automatically adding more food.</p>
<h2>Do you need supplements?</h2>
<p>No. Protein powder can make a target easier to reach, but ordinary foods can do the same job. Consistent training and enough total food matter more than a perfectly timed shake.</p>
''',[MUSCLE,PROTEIN,TIMING,('https://pubmed.ncbi.nlm.nih.gov/34623696/','Energy deficiency and resistance-training gains: meta-analysis')],['calculators.html','body-recomposition-explained.html','what-to-eat-after-a-workout.html'])

page('cutting-bulking-maintenance-explained','Cutting, bulking or maintenance: what do they mean?',
     'Cutting means eating for weight loss. Bulking means eating to support weight gain and muscle building. Maintenance means keeping weight broadly steady.', '''
<h2>Three goals, explained simply</h2>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Goal</th><th>Calorie approach</th><th>What to watch</th></tr></thead><tbody>
<tr><th scope="row">Cutting / weight loss</th><td>A manageable deficit</td><td>Weight trend, strength, hunger and recovery</td></tr>
<tr><th scope="row">Maintenance</th><td>Near your average energy needs</td><td>Broadly stable weight and a sustainable routine</td></tr>
<tr><th scope="row">Bulking / muscle gain</th><td>Often a modest surplus</td><td>Training progress and the pace of weight gain</td></tr></tbody></table></div>
<p>You do not have to cycle through these phases. Maintaining your weight while improving fitness and meal habits is a valid long-term goal.</p>
<h2>What changes in your meals?</h2>
<p>Much of the food can stay the same. For weight loss, portions or calorie-dense extras may be smaller. For weight gain, larger portions or an extra snack may help. Keep protein foods, produce and other useful nutrients in both plans.</p>
<p>Resistance training and adequate protein support muscle retention during weight loss and muscle growth when that is your goal. Neither outcome follows from a calorie number alone.</p>
<h2>Should you cut or bulk first?</h2>
<p>Start with the outcome you want and whether changing weight is appropriate for you. There is no body-fat percentage that makes the decision for everyone.</p>
<p>If you want to improve strength without changing weight, start around maintenance. If your priority is weight loss, use a manageable deficit. If you are training consistently and want to gain, consider a modest surplus.</p>
<h2>Can you build muscle and lose fat together?</h2>
<p>Sometimes. This is called body recomposition. It can be more achievable for newer or returning lifters, but results vary. A large deficit generally makes muscle gain harder.</p>
<h2>How long should a phase last?</h2>
<p>There is no universal deadline. Review your energy, recovery, weight trend and relationship with food. You can spend time at maintenance when that better supports your health or routine; it is not a failed diet.</p>
<p>Use the free macro calculator for a starting estimate, then review what actually happens over several weeks. Get personal advice if pregnancy, illness, eating-disorder recovery or another health circumstance affects the plan.</p>
''',[ENERGY,PROTEIN,('https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/','ISSN: diets and body composition')],['calculators.html','macros-for-weight-loss.html','macros-for-muscle-gain.html'])

page('body-recomposition-explained','Body recomposition: can you lose fat and build muscle?',
     'Body recomposition means losing body fat while gaining muscle. It can happen, but progress is gradual and the scale may not show the full change.', '''
<h2>Who is most likely to make progress?</h2>
<p>Newer lifters, people returning after time away and people with more stored body fat may have more room for simultaneous changes. Experienced lifters can sometimes do it too, but there is no guarantee based on a category or body-fat percentage.</p>
<p>Studies have shown lean-mass gains during weight loss under specific training and nutrition conditions. Those results do not mean everyone should copy a study’s aggressive diet or training schedule.</p>
<h2>What should you focus on?</h2>
<ol><li><strong>Resistance training:</strong> follow a suitable program and make progress over time.</li><li><strong>Enough protein:</strong> choose a daily target that fits your size and training.</li><li><strong>Enough food:</strong> maintenance or a modest deficit may fit the goal better than a large cut.</li><li><strong>Recovery:</strong> allow time for sleep, rest and consistent meals.</li></ol>
<p>The calculator’s “Lose fat + build muscle” option gives an estimate with a smaller deficit. It cannot predict whether you personally will gain muscle at that intake.</p>
<h2>How do you track recomposition?</h2>
<p>Look at several measures together: how clothes fit, waist measurements taken consistently, training performance and weight trends. Photos are optional, not a requirement.</p>
<p>A smaller waist and improving strength may suggest progress, but they do not precisely measure muscle gain. Strength also changes with skill and practice. Home body-fat scales are estimates too.</p>
<h2>How long does it take?</h2>
<p>Think in months rather than days. The pace depends on training history, starting point, nutrition and recovery. Stable weight can coexist with changing body composition, but stable weight alone does not prove recomposition.</p>
<h2>When should you change the plan?</h2>
<p>If recovery is poor or the routine is hard to maintain, review the deficit and training demands. If maximum muscle gain or faster weight loss becomes your priority, a more focused approach may be easier to assess.</p>
<p>Choose the approach that fits your health and daily life. You do not need to pursue both goals at once to make worthwhile progress.</p>
''',[PROTEIN,('https://pubmed.ncbi.nlm.nih.gov/26817506/','Higher protein during an energy deficit: randomized trial'),('https://pubmed.ncbi.nlm.nih.gov/34623696/','Energy deficiency and resistance-training gains: meta-analysis')],['can-you-build-muscle-in-a-calorie-deficit.html','calculators.html'])

page('how-to-read-a-nutrition-label','How to read a nutrition label',
     'Start with the serving size, then check the nutrients in the amount you will eat. This guide follows the U.S. Nutrition Facts label.', '''
<h2>1. Check the serving and the package</h2>
<p>A serving size describes an amount people typically consume; it is not advice about how much you should eat. Check servings per container too. Some labels show both a per-serving column and a whole-package column.</p>
<p>If one serving is 40 g and you eat 60 g, multiply the per-serving numbers by 1.5. For example, 160 calories per serving becomes 240 calories in your portion.</p>
<h2>2. Read the nutrients you care about</h2>
<p>Calories tell you about energy. Protein, fiber, saturated fat, sodium and added sugar help you understand other parts of the food. There is no single line that decides whether a food belongs in your meals.</p>
<ul><li>Total carbohydrate already includes fiber and sugars. Do not add them again.</li><li>Total fat already includes saturated and trans fat.</li><li>Added sugars are part of total sugars, not an extra amount on top.</li><li>Use protein grams when comparing protein; many labels do not show a protein %DV.</li></ul>
<h2>3. Use % Daily Value as a quick guide</h2>
<p>The FDA’s rule of thumb is 5% DV or less is low and 20% DV or more is high for a nutrient in one serving. Daily Values are general reference amounts, not your personal targets.</p>
<p>The 2,000-calorie statement provides general nutrition context. It does not mean everyone needs 2,000 calories, or that every Daily Value scales directly with your own calorie intake.</p>
<h2>4. Compare the same amount</h2>
<p>Two products may use different serving sizes. Comparing equal weights helps when the foods serve a similar purpose. Comparing the portions you actually eat may be more useful for planning a meal.</p>
<p>Our food comparison tool offers per-serving, per-100-g and per-100-calorie views. These answer different questions; none is an overall health score.</p>
<h2>5. Check ingredients and allergens</h2>
<p>Ingredients are generally listed from greatest to least weight. Their order does not reveal exact percentages, and a long list is not automatically worse than a short one.</p>
<p>Read the allergen statement and ingredient list if you have an allergy. Do not assume that a missing precautionary warning rules out cross-contact.</p>
<h2>Why don’t the numbers always add up?</h2>
<p>Nutrition labels use rounding rules. Fiber, sugar alcohols and other ingredients can also affect calorie calculations. Small differences between printed calories and a calculation using 4 calories per gram of protein or carbs and 9 per gram of fat are not automatically errors.</p>
''',[LABEL,('https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label','FDA: serving sizes'),('https://www.fda.gov/food/food-labeling-nutrition/food-allergies-what-you-need-know','FDA: food allergies')],['nutrition-label-comparison-tool.html','serving-size-vs-portion-size.html'])

page('how-to-eat-out-without-wrecking-your-goal','How to eat out while working toward your goals',
     'You can enjoy a restaurant meal while working on weight loss, muscle gain or everyday nutrition. Start with the whole order and a goal that matters to you.', '''
<h2>Choose what you want from the meal</h2>
<p>Are you looking for more protein, a smaller meal, a plant-based option or simply something you enjoy? You do not need to optimize every nutrient at once. A celebration and a quick lunch can involve different choices.</p>
<h2>Compare the whole order</h2>
<p>Count the sides, sauces, dressing and drink you expect to have. An entrée’s nutrition is not necessarily the total for its combo meal. Check the named portion and whether dressing is included.</p>
<p>The meal finder compares selected U.S. menu options. It does not cover every item or customization. Use the restaurant’s own menu to confirm current availability, ingredients and nutrition.</p>
<h2>Swaps that can help</h2>
<ul><li>Compare grilled and fried versions when both are available.</li><li>Ask for a sauce or dressing separately if you want to control the amount.</li><li>Choose a drink that fits your preference and meal.</li><li>Order a smaller side, share one, or take leftovers home if that suits your appetite.</li><li>Add beans or vegetables when you want more fiber.</li></ul>
<p>The size of each difference depends on the restaurant. A salad is not automatically lower in calories, and a sandwich is not automatically a poor choice.</p>
<h2>What if the restaurant has no nutrition information?</h2>
<p>Choose familiar foods and a portion that feels appropriate. If you track, use a comparable food entry as a rough estimate and accept that it may be off. A palm-sized serving does not always contain the same grams of protein.</p>
<p>You do not need to deliberately overestimate or compensate later. One uncertain meal is not a reason to skip the next one or abandon your routine.</p>
<h2>For weight loss or muscle gain</h2>
<p>For weight loss, compare portions and calorie-dense additions while keeping the meal satisfying. For muscle gain, check protein and whether the meal supplies enough overall food. A very large order is optional, not a requirement for building muscle.</p>
<p>After eating, return to your usual routine. Judge a plan by the pattern over time, alongside energy, recovery and enjoyment—not by whether one meal matched a calculator exactly.</p>
''',[LABEL,ENERGY,('restaurant-meal-guides.html','Official restaurant nutrition links')],['restaurant-meal-finder.html','healthy-fast-food.html','serving-size-vs-portion-size.html'])

page('how-many-calories-should-i-eat-a-day','How many calories should I eat a day?',
     'There is no single calorie target for everyone. Your body size, age, activity and goal help estimate a starting point.', '''
<h2>Start with your maintenance calories</h2>
<p>Maintenance is the average intake that keeps your weight broadly stable. It includes energy used at rest, daily movement, exercise and digestion. The free macro calculator estimates it from your details.</p>
<p>The calculator uses the Mifflin–St Jeor equation for resting energy needs, then applies an activity factor. It estimates energy use; it does not measure your metabolism.</p>
<h2>Choose an activity level</h2>
<p>Think about the whole day, including your job and time spent walking or sitting. Workout frequency is only a rough guide. Two people who both train three days a week may move very differently the rest of the time.</p>
<h2>Adjust for your goal</h2>
<ul><li><strong>Maintain weight:</strong> start near the maintenance estimate.</li><li><strong>Lose weight:</strong> choose a manageable reduction that still supports nutrition and daily life.</li><li><strong>Gain weight or muscle:</strong> a modest increase may help; training matters if muscle gain is the goal.</li></ul>
<p>For example, reducing an illustrative maintenance estimate of 2,200 calories by 10% gives 1,980. This shows the math, not a recommendation for every reader.</p>
<h2>How do you know if the estimate is right?</h2>
<p>If tracking suits you, compare your intake and weight trend over several weeks under similar conditions. Consider energy, hunger and recovery too. Water retention and menstrual-cycle changes can obscure the trend for longer than two weeks.</p>
<p>If the pattern consistently differs from your goal, review portions and activity before making a modest adjustment. More decimal places will not make an uncertain estimate more accurate.</p>
<h2>Is 1,200 calories enough?</h2>
<p>It is not a suitable default for everyone. A low target can make it hard to meet nutritional needs, especially for active or larger adults. Do not use a round number from the internet as a personal prescription.</p>
<h2>Should you add exercise calories back?</h2>
<p>An activity-based estimate already includes some exercise. Automatically adding a watch’s exercise estimate again can double-count it. If your activity changes substantially, review the overall target instead.</p>
<p>Use personal clinical advice during pregnancy, illness, eating-disorder recovery or other circumstances that change your needs. The site’s weight-planning calculator is designed for adults.</p>
''',[MIFFLIN,ENERGY],['calculators.html','how-to-calculate-maintenance-calories.html','restaurant-meal-finder.html'])

page('how-to-calculate-macros-by-hand','How to calculate your macros by hand',
     'Estimate daily calories first, then convert protein, fat and carbs into grams. This worked example explains the arithmetic behind a macro plan.', '''
<h2>1. Estimate resting energy</h2>
<p>The Mifflin–St Jeor equation uses weight in kilograms, height in centimeters and age in years. It estimates resting energy expenditure.</p>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Equation</th><th>Calculation</th></tr></thead><tbody><tr><th scope="row">Male</th><td>10 × kg + 6.25 × cm − 5 × age + 5</td></tr><tr><th scope="row">Female</th><td>10 × kg + 6.25 × cm − 5 × age − 161</td></tr></tbody></table></div>
<p>For a 32-year-old woman weighing 68 kg at 165 cm, the estimate is 1,390.25 calories per day at rest.</p>
<h2>2. Account for activity and your goal</h2>
<p>Multiply resting energy by an activity factor. The site offers factors from 1.2 to 1.9. These are rough categories, not measurements; include activity outside the gym.</p>
<p>Using 1.55 in this example gives about 2,155 calories for maintenance. An illustrative 20% reduction gives about 1,724 calories. The factor and reduction are assumptions for this example, not instructions for everyone.</p>
<h2>3. Set protein</h2>
<p>Protein provides about 4 calories per gram. If this example uses 136 g protein, it accounts for 544 calories. Choose your own amount using your needs and the daily protein guide.</p>
<h2>4. Set fat</h2>
<p>Fat provides about 9 calories per gram. Choosing 28% of the example’s calories gives about 483 calories from fat, or roughly 54 g. The adult fat reference range is 20–35% of total energy.</p>
<h2>5. Work out the remaining carbs</h2>
<p>Subtract protein and fat calories from the total, then divide by 4. Here, (1,724 − 544 − 483) ÷ 4 gives about 174 g carbohydrate.</p>
<p>The rounded example is 1,724 calories, 136 g protein, 54 g fat and 174 g carbs. Rounded grams may add back to a slightly different calorie total. Keep extra precision during calculation, then round the final display.</p>
<h2>What if the numbers do not fit?</h2>
<p>If protein and fat use more than the whole calorie target, review your assumptions. Do not force negative carbs or an impractically low calorie intake to make a formula work.</p>
<p>Your result is a starting estimate. Compare it with your routine and progress over time; it is not a precise measurement or a promise of a particular outcome.</p>
''',[MIFFLIN,RANGES,PROTEIN],['calculators.html','how-much-protein-per-day.html','what-are-macros.html'])

page('how-much-fiber-per-day','How much fiber do you need per day?',
     'Fiber helps with digestion and can support heart health. Beans, whole grains, fruit, vegetables, nuts and seeds are practical ways to get more.', '''
<h2>How much should you aim for?</h2>
<p>Needs vary with age, sex and energy intake. The National Academies’ adequate intakes include 25 g/day for women and 38 g/day for men aged 19–50, and 21 g and 30 g respectively after age 50. Pregnancy and breastfeeding have separate reference amounts.</p>
<p>Another planning reference is about 14 g per 1,000 calories. The U.S. label Daily Value is 28 g. These figures come from different reference contexts, so they are not interchangeable personal prescriptions.</p>
<h2>Which foods make it easier?</h2>
<ul><li>Add beans or lentils to a bowl, soup or pasta dish.</li><li>Choose oats or a whole-grain cereal you enjoy.</li><li>Include fruit and vegetables across meals.</li><li>Use nuts or seeds as a topping or snack.</li></ul>
<p>For an exact product, check its label. The same food can have different fiber amounts depending on portion, brand and preparation.</p>
<h2>Does the type of fiber matter?</h2>
<p>Different fibers have different effects. Some help with stool bulk; some form gels or are fermented by gut bacteria. A mix of plant foods is a practical starting point without tracking individual fiber types.</p>
<p>If a clinician has recommended a particular fiber or supplement for a condition, follow that advice rather than a general food list.</p>
<h2>How can you get more fiber when eating out?</h2>
<p>Look for beans, lentils, whole grains and vegetables, then compare the published fiber for the complete order. A salad is not automatically the highest-fiber option, and added fiber can also contribute to a packaged wrap’s total.</p>
<p>Our meal finder includes a higher-fiber preference. A missing restaurant value means unknown, not zero. Higher fiber does not automatically mean lower calories or sodium.</p>
<h2>Increase it gradually</h2>
<p>Try one manageable change at a time and drink enough fluid. A sudden large increase can cause gas or discomfort. You do not need to force a fixed weekly increase if your digestion responds differently.</p>
<p>Digestive conditions can change what is appropriate. Seek individual advice if symptoms persist or you have been told to limit certain foods.</p>
''',[RANGES,LABEL,('https://www.niddk.nih.gov/health-information/digestive-diseases/constipation/eating-diet-nutrition','NIDDK: fiber, food and fluids')],['restaurant-meal-finder.html','carbs.html','how-to-read-a-nutrition-label.html'])

page('how-much-sodium-per-day','How much sodium should you have per day?',
     'Packaged foods and restaurant meals can contain a lot of sodium. Check the whole portion, then compare options that fit the meal you want.', '''
<h2>What are the general limits?</h2>
<p>The U.S. Daily Value is less than 2,300 mg sodium per day. WHO recommends less than 2,000 mg per day for adults. These are general limits, not amounts you need to reach.</p>
<p>Use an individual target if your clinician has given you one. Some medical conditions and situations involving prolonged heavy sweating need more specific guidance.</p>
<h2>Is sodium the same as salt?</h2>
<p>No. Table salt contains sodium and chloride. About 5 g salt contains 2,000 mg sodium. Food labels in different countries may show sodium or salt, so check the label before comparing.</p>
<h2>How do you read sodium on a label?</h2>
<p>Find sodium in milligrams and check the serving size. A soup with 700 mg per serving contains 1,400 mg if you eat two servings. The sodium portion calculator handles that multiplication for two foods.</p>
<p>% Daily Value offers a quick comparison: the FDA describes 5% DV or less as low and 20% or more as high per serving. It is a label reference, not a personal meal allowance.</p>
<h2>How do you choose a lower-sodium restaurant meal?</h2>
<ul><li>Compare similar portions instead of a small side with a full meal.</li><li>Include sauces, dressings and sides in the total.</li><li>Check cured meats, cheese, soups and seasoned entrées.</li><li>Ask about a sauce separately when the restaurant can accommodate it.</li></ul>
<p>Changes are not always reflected in a standard menu total. The restaurant is the best source for what can be changed and whether updated nutrition is available. Our lower-sodium filter means lower within the selected options, not suitable for every medical diet.</p>
<h2>Does water cancel out a salty meal?</h2>
<p>No. Drinking water does not remove the sodium from the food you ate. Return to your normal routine and use the pattern across your meals to guide future choices.</p>
<p>A meal cooked at home is not automatically low in sodium either. Ingredients, portions and the rest of the day still count. If you have a prescribed sodium limit, follow it rather than using this general guide.</p>
''',[('https://www.fda.gov/food/nutrition-education-resources-materials/sodium-your-diet','FDA: sodium in your diet'),('https://www.who.int/news-room/fact-sheets/detail/sodium-reduction','WHO: sodium reduction'),LABEL],['sodium-label-comparison-tool.html','restaurant-meal-finder.html','how-to-read-a-nutrition-label.html'])

page('editorial-policy','How we write and check our content',
     'GetMacros explains nutrition and helps you compare meals. Here is how we choose sources, describe the evidence and correct mistakes.', '''
<h2>Who publishes GetMacros?</h2>
<p>Pages are published under the GetMacros name. This is the site’s publishing identity, not a claim that a registered dietitian or doctor wrote or medically reviewed each page.</p>
<p>We use software and AI tools to help draft, organize and check content and code. The publisher remains responsible for what appears here. A citation does not mean its author endorses this site.</p>
<h2>Where do the facts come from?</h2>
<p>Restaurant pages link to official menu information. Nutrition guides use research papers, reviews and accountable sources such as the NIH, FDA and USDA. Calculators explain their formulas and assumptions.</p>
<p>We distinguish a study’s findings from what it cannot show. A short experiment in one group does not establish what happens to everyone over years. Missing menu data is not treated as zero.</p>
<h2>What makes a page worth keeping?</h2>
<p>It should answer a clear question, explain how to use a tool or help someone compare real options. We remove repeated explanations, unsupported claims and wording that makes a simple decision harder.</p>
<p>There is no fixed word-count target. A working calculator needs clear instructions; a research question may need more explanation and sources.</p>
<h2>Updates and corrections</h2>
<p>Dates change when content is meaningfully revised. Important factual or calculation corrections appear in the public corrections log. Routine spelling, layout and link repairs do not each need an entry.</p>
<p>If something looks wrong, send the page link and the sentence or result to check. A supporting source is helpful. We assess the evidence before changing a claim.</p>
<h2>What this site cannot do</h2>
<p>GetMacros provides general education and estimates. It does not diagnose conditions or replace individual advice from a qualified clinician or dietitian. Medical nutrition needs can differ from the general examples here.</p>
''',[],['about.html','sources.html','corrections.html','contact.html'])

page('corrections','Corrections and updates',
     'Found a wrong number, unclear explanation or broken tool? Send the page link and what needs checking.', '''
<h2>How to report a problem</h2>
<p>Email <a href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a>. Include the wording or result, what you expected and a supporting source if you have one. Please do not send private medical records.</p>
<p>We check the report against the page, calculation and relevant sources. Corrections that change a factual meaning or result are recorded below. Small wording, design and link fixes may be made without a separate entry.</p>
<h2>September 9, 2026 — nutrition explanations</h2>
<p>Earlier protein guides described the RDA as only a deficiency-prevention minimum and gave overlapping, inconsistent ranges. The revised guides explain that the RDA is designed to cover nearly all healthy adults and distinguish it from training-oriented ranges.</p>
<p>We also removed unsupported guarantees about muscle gain, strict macro tolerances and the time needed for scale fluctuations to settle. Worked macro examples were checked and replaced with consistent arithmetic. Label guidance now accounts for per-package columns and explains Daily Values without treating them as personal targets.</p>
<h2>September 9, 2026 — restaurant meals</h2>
<p>We checked the 83 tracked orders against official menu information, corrected outdated figures and replaced older items with options in the linked menus. Meal descriptions now clarify standard toppings, dressings and sides. We removed incorrect dietary labels, including the vegetarian label on Popeyes red beans and rice and the plant-based label on CAVA’s Falafel Crunch bowl.</p>
<p>Some current Taco Bell nutrient values could not be confirmed. Those values are now blank, and meals with missing data do not qualify for filters that need that number.</p>
<h2>September 9, 2026 — protein food comparisons</h2>
<p>We corrected entries that mixed nutrition values from different food preparations, including firm tofu, shelled pumpkin seeds and cooked salmon. All 25 foods now link to a specific reference, with protein per portion calculated from the same underlying values.</p>
<h2 id="recipe-correction">September 7, 2026 — recipe and comparison tools</h2>
<p>The recipe tool mixed up dividing the same batch into more portions with making a larger batch. It now separates those actions. The protein-cost tool was corrected to recognize equal costs, and the macro calculator’s unit buttons convert the entered weight or height.</p>
''',[],['editorial-policy.html','contact.html'])

page('accessibility','Accessibility at GetMacros',
     'We want the site to be comfortable to read and use on phones, larger screens and with a keyboard. Tell us when something gets in the way.', '''
<h2>Features you can use</h2>
<ul><li>A “Skip to main content” link for keyboard navigation.</li><li>Visible focus outlines and labeled calculator inputs.</li><li>A mobile menu that reports whether it is open and closes with Escape.</li><li>Light and dark themes, plus a motion pause control in the footer.</li><li>Support for your device’s reduced-motion setting.</li><li>Text results and error messages rather than color alone.</li></ul>
<h2>Small screens and larger text</h2>
<p>Layouts are checked at phone, tablet and desktop widths. Some comparison tables scroll horizontally so their columns remain readable. Increasing text size may require more scrolling.</p>
<h2>What still has limits?</h2>
<p>Calculations and interactive filters need JavaScript. Core reading content and navigation remain available without it. External websites, PDFs and advertising are outside our direct control.</p>
<p>We use WCAG 2.2 AA as a reference and test keyboard behavior, contrast and layouts. These checks do not amount to a complete independent accessibility certification or guarantee compatibility with every assistive technology.</p>
<h2>Report a barrier</h2>
<p>Send the page link, what you were trying to do and what happened. If you are comfortable sharing it, include your browser, device or assistive technology. You do not need to share health information.</p>
''',[],['contact.html'])

# Restaurant examples share the finder's records so values cannot drift between pages.
from build_restaurant_pages import parse_meals
import html as _html
_meals=parse_meals()
def _meal(chain,name):
    return next(m for m in _meals if m['chain']==chain and m['name']==name)
_comparisons=[
 ('High protein in a small portion','Chick-fil-A','Grilled Nuggets, 12 count','This is a protein portion, not necessarily enough food for lunch. Add a side if you want more energy or fiber. Dipping sauce is separate.'),
 ('A bowl you can customize','Chipotle','High Protein-High Fiber Bowl','This named build includes chicken, light brown rice, black beans, vegetables and salsas. Use Chipotle’s calculator when you change ingredients.'),
 ('A sandwich with a clear portion size','Subway','6-inch Grilled Chicken & Fresh Avocado','The Fresh Fit recipe includes multigrain bread, a deluxe chicken portion, avocado and vegetables. A footlong doubles these published six-inch values.'),
 ('A warm meal with fiber','Panera','Hearty Fireside Chili, bowl','One bowl provides beans and other ingredients in a hot meal. Bread and separate sides are not included. Check the seasonal menu before ordering.'),
 ('A plant-based bowl','Sweetgreen','Shroomami','Tofu, mushrooms, rice and vegetables with miso sesame ginger dressing. This is a full bowl, so compare it with another meal rather than a tiny side.'),
 ('A larger chicken-and-rice order','Panda Express','Bigger Plate: fried rice + 3 grilled teriyaki chicken entrées','This very large order combines fried rice and three chicken entrées. It may suit a large appetite, but has more than a day’s 2,300 mg sodium reference before extra sauce.')
]
_rows=[];_sections=[];_sources=[]
for heading,chain,name,note in _comparisons:
    m=_meal(chain,name)
    _rows.append('<tr><th scope="row">'+_html.escape(chain+' — '+name)+'</th><td>'+str(m['cal'])+'</td><td>'+str(m['p'])+' g</td><td>'+str(m['f'])+' g</td><td>'+f"{m['na']:,}"+' mg</td></tr>')
    _sections.append('<h2>'+heading+'</h2><p><strong>'+_html.escape(chain+': '+name)+'.</strong> '+note+'</p><p><a class="btn" href="'+m['url']+'">Compare '+_html.escape(chain)+' meals</a></p>')
    _sources.append(('https://getmacros.net/'+m['url'],chain+' figures and official source links'))
page('best-fast-food-restaurants-for-your-goals','Healthy fast food: which restaurant fits your goal?',
 'Compare real orders for protein, calories, fiber and portion size. The best choice depends on what you want from your next meal.',
 '''<h2>Start with the meal, not the restaurant’s reputation</h2>
<p>A chain with a useful grilled-chicken option may also sell meals that do not fit your needs. A salad can contain more calories than a sandwich once you include its dressing. Compare the exact order you want to eat.</p>
<p>These six examples answer different questions. They are not a ranking of every restaurant, and the smallest calorie number is not automatically the best meal.</p>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Order</th><th>Calories</th><th>Protein</th><th>Fiber</th><th>Sodium</th></tr></thead><tbody>'''+''.join(_rows)+'''</tbody></table></div>'''+''.join(_sections)+'''
<h2>What about Taco Bell?</h2>
<p>The current Cantina Chicken Bowl is listed at 520 calories and 25 g protein. Its rice, beans, vegetables and toppings make it a different order from a single taco. The standard Veggie Bowl is 410 calories and includes dairy and egg ingredients. Extra sauces and custom changes need their own check.</p>
<p>We have removed older Power Menu Bowl examples. Where we could not confirm a current nutrient value, the finder shows a dash and excludes that item from filters that require the missing number.</p>
<h2>How to choose quickly</h2>
<ol><li>Decide whether you want a snack, regular meal or larger portion.</li><li>Pick one or two priorities, such as protein and calories.</li><li>Include the dressing, sauce, sides and drink you will actually have.</li><li>Check the restaurant’s current menu for your exact order.</li></ol>
<p>For weight loss, a meal that fits your calorie needs and keeps you satisfied is more useful than the smallest item. For weight gain, a larger portion can help, but you still have choices about sodium, fiber and how much food feels comfortable.</p>
<h2>About these comparisons</h2>
<p>These are selected U.S. menu orders from the GetMacros meal finder. Restaurant portions, recipes and availability change. The restaurant guides link to the official nutrition sources and explain the build being compared. GetMacros is independent of these restaurants.</p>
''',_sources+[('https://www.tacobell.com/food/bowls','Taco Bell: current bowls')],['restaurant-meal-finder.html','calculators.html'])
