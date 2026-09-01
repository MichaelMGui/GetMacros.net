#!/usr/bin/env python3
"""Build focused, evidence-led guides for the practical nutrition library."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from focus_components import SITE, breadcrumbs, footer, head, nav
from site_scope import GUIDE_GROUPS

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "2026-08-31"
UPDATED_HUMAN = "August 31, 2026"

ARTICLES = [
    {
        "path": "what-to-eat-before-a-workout.html",
        "title": "What to Eat Before a Workout | GetMacros",
        "h1": "What to eat before a workout",
        "desc": "What to eat before a workout, from a full meal to a quick snack. Choose carbs, protein and portion size based on timing and stomach comfort.",
        "dek": "A useful pre-workout meal gives you fuel without making the session feel like digestion practice.",
        "read": "8 min read",
        "quick": "Start with food you already tolerate. As the workout gets closer, make the meal smaller and easier to digest. Carbohydrate usually does most of the immediate fueling; a moderate protein serving can help you cover your daily target.",
        "body": r'''
<h2>The simple answer</h2>
<p>If you have two to four hours, eat a normal meal built around carbohydrate, a useful protein source and a portion size you know sits well. If you have less than an hour, a smaller, lower-fat snack is usually easier to tolerate. The “best” choice depends on the workout, the time available and your own gut—not a universal list of approved foods.</p>
<div class="guide-decision-table" role="region" aria-label="Pre-workout food ideas by timing" tabindex="0"><table><thead><tr><th>Time before training</th><th>What to prioritize</th><th>Practical examples</th></tr></thead><tbody>
<tr><td>2–4 hours</td><td>A familiar meal with carbs, protein and fluids</td><td>Rice with chicken and vegetables; oatmeal, yogurt and fruit; a turkey sandwich with fruit</td></tr>
<tr><td>60–120 minutes</td><td>A smaller mixed snack or light meal</td><td>Greek yogurt and a banana; cereal and milk; toast with eggs</td></tr>
<tr><td>Under 60 minutes</td><td>Easy-to-digest carbohydrate if you need it</td><td>A banana, applesauce, toast, pretzels or a small sports drink</td></tr>
</tbody></table></div>
<p>Those are templates, not prescriptions. A large bowl of oatmeal may feel great three hours before lifting and terrible 25 minutes before running. Your previous experience is useful evidence.</p>

<h2>Carbs, protein and fat play different roles</h2>
<h3>Carbohydrate is the most direct training fuel</h3>
<p>Hard or long exercise draws heavily on carbohydrate stored as glycogen. The International Society of Sports Nutrition notes that carbohydrate timing matters most when sessions are long, intense or close together. For an ordinary one-hour gym session, you do not need an elaborate loading protocol; arriving generally well-fed is usually enough.</p>
<h3>Protein supports the day, not a magic window</h3>
<p>A pre-workout protein serving can make it easier to distribute protein across the day. It does not need to be swallowed at an exact minute. A 2017 position stand concludes that total daily protein and reasonably spaced servings matter more than treating the workout as a narrow countdown.</p>
<h3>Fat and fiber are useful—but can slow the meal down</h3>
<p>Fat and fiber belong in a healthy eating pattern. Close to training, however, a very fatty or very fibrous meal can feel heavy for some people. Reduce them only as much as your comfort and timing require. There is no prize for making every pre-workout meal bland.</p>

<h2>Match the food to the session</h2>
<ul>
<li><strong>Strength training:</strong> a normal meal in the previous few hours often works. Add a small carb snack if you trained after a long gap and feel flat.</li>
<li><strong>Long endurance work:</strong> carbohydrate availability matters more as duration and intensity rise. Practice your strategy before an important event.</li>
<li><strong>Early-morning training:</strong> you can train after breakfast or with little food if the session is short and you feel good. If performance drops, test a small carb source rather than forcing a large meal.</li>
<li><strong>Training while cutting:</strong> place some of the calories you already planned near the workout instead of automatically adding more.</li>
<li><strong>Training while bulking:</strong> the pre-workout meal can help meet a higher calorie target, but leave enough time to digest a larger portion.</li>
</ul>

<h2>A repeatable way to choose</h2>
<ol>
<li>Check how long the session will be and how hard you expect to work.</li>
<li>Count backward from training time.</li>
<li>Choose one familiar carbohydrate and one protein source.</li>
<li>Make the portion smaller as the time window shrinks.</li>
<li>Write down how your energy and stomach felt, then adjust one variable next time.</li>
</ol>
<p>If you routinely feel dizzy, faint, unusually weak or unwell during exercise, stop and seek advice from a qualified clinician. A meal guide cannot diagnose the cause.</p>
''',
        "sources": [
            ("International Society of Sports Nutrition position stand: nutrient timing", "https://pubmed.ncbi.nlm.nih.gov/28919842/"),
            ("Nutrition and Athletic Performance — Academy of Nutrition and Dietetics, Dietitians of Canada and ACSM", "https://pubmed.ncbi.nlm.nih.gov/26920240/"),
        ],
        "related": [("What to eat after a workout", "what-to-eat-after-a-workout.html"), ("Free macro calculator", "calculators.html"), ("How much protein do I need?", "how-much-protein-per-day.html")],
    },
    {
        "path": "what-to-eat-after-a-workout.html",
        "title": "What to Eat After a Workout | GetMacros",
        "h1": "What to eat after a workout",
        "desc": "Build a practical post-workout meal with protein, carbs and fluids. Learn when recovery timing matters and when your next normal meal is enough.",
        "dek": "Recovery food should fit the work you did and the next thing your body has to do.",
        "read": "8 min read",
        "quick": "Eat a useful protein serving and include carbohydrate in proportion to the work you did. If another hard session is only a few hours away, timing becomes more important. Otherwise, a normal meal soon after training is usually a sensible plan.",
        "body": r'''
<h2>Build the meal around the recovery job</h2>
<p>Post-workout nutrition has three practical jobs: help repair tissue, replace the fuel you used and restore fluid. The size and urgency of each job changes. A casual 40-minute lift followed by a rest day does not require the same recovery plan as a tournament, a long run or two training sessions in one day.</p>
<div class="guide-formula"><span>Protein source</span><b>+</b><span>Carbohydrate matched to the session</span><b>+</b><span>Fluids and a normal meal</span></div>

<h2>How soon do you need to eat?</h2>
<p>The often-repeated “30-minute anabolic window” is too rigid. The ISSN position stand describes a wider practical window and emphasizes the importance of total daily protein. If you ate a mixed meal before training, you have even less reason to panic on the walk back to the car.</p>
<p>Timing deserves more attention when recovery time is short. If you must perform hard again within roughly four hours, rapid carbohydrate replacement becomes useful. The ISSN review discusses aggressive carbohydrate intake for this specific situation. That is an athlete-with-another-session problem, not a rule everyone needs after every workout.</p>

<h2>What belongs on the plate?</h2>
<h3>Protein</h3>
<p>Choose a serving that meaningfully contributes to your daily protein target: poultry, fish, lean meat, eggs, dairy, tofu, tempeh, beans or a convenient protein shake. The exact amount depends on body size and the rest of your diet. For most people, consistently reaching an appropriate daily target matters more than chasing a perfect post-workout number.</p>
<h3>Carbohydrate</h3>
<p>Use more when the workout was long, glycogen-demanding or followed by another session soon. Rice, potatoes, oats, pasta, bread, fruit, cereal and beans are all workable. A short easy session does not automatically require a large sugar-heavy recovery snack.</p>
<h3>Fluids and sodium</h3>
<p>Drink according to thirst and the amount you sweated. A normal meal often supplies sodium. People with very high sweat losses, long sessions or repeated work in heat may need a more deliberate plan; the <a href="sweat-rate-calculator.html">sweat-rate calculator</a> can help estimate fluid loss, but it is not a medical hydration prescription.</p>

<h2>Six meals that make the idea concrete</h2>
<div class="guide-example-grid">
<article><h3>Fast breakfast</h3><p>Greek yogurt, oats, berries and milk.</p></article>
<article><h3>Full lunch</h3><p>Chicken or tofu, rice, vegetables and a sauce you enjoy.</p></article>
<article><h3>Plant-based</h3><p>Lentil pasta with tomato sauce and roasted vegetables.</p></article>
<article><h3>No-cook</h3><p>Turkey or hummus sandwich, fruit and yogurt.</p></article>
<article><h3>Higher-calorie</h3><p>A burrito bowl with rice, beans, meat or sofritas, salsa and guacamole.</p></article>
<article><h3>Small appetite</h3><p>A smoothie with milk or soy drink, fruit, oats and protein.</p></article>
</div>

<h2>Recovery mistakes worth avoiding</h2>
<ul>
<li><strong>Rewarding every workout with unplanned calories.</strong> A recovery meal can be part of your target rather than a bonus added on top.</li>
<li><strong>Eating only protein.</strong> Carbohydrate has a clear role, especially after demanding endurance or high-volume work.</li>
<li><strong>Using supplements when food would be easier.</strong> Shakes are convenient, not mandatory.</li>
<li><strong>Ignoring the full day.</strong> One polished meal cannot rescue chronically inadequate energy, protein or sleep.</li>
</ul>
<p>Use the meal you can repeat. Recovery is a pattern, not a single photograph of a “perfect” plate.</p>
''',
        "sources": [
            ("International Society of Sports Nutrition position stand: nutrient timing", "https://pubmed.ncbi.nlm.nih.gov/28919842/"),
            ("ISSN position stand: protein and exercise", "https://pubmed.ncbi.nlm.nih.gov/28642676/"),
            ("Nutrition and Athletic Performance", "https://pubmed.ncbi.nlm.nih.gov/26920240/"),
        ],
        "related": [("What to eat before a workout", "what-to-eat-before-a-workout.html"), ("Macros for muscle gain", "macros-for-muscle-gain.html"), ("How much protein can your body absorb?", "how-much-protein-can-your-body-absorb.html")],
    },
    {
        "path": "why-did-i-gain-weight-overnight.html",
        "title": "Why Did I Gain Weight Overnight? | GetMacros",
        "h1": "Why did I gain weight overnight?",
        "desc": "An overnight scale increase is usually not a sudden change in body fat. Learn how food mass, fluid, sodium, carbs and digestion move daily weight.",
        "dek": "The scale can change quickly because it measures everything in your body—not only fat.",
        "read": "7 min read",
        "quick": "A one-day increase usually reflects a mixture of fluid, food and waste in the digestive system, carbohydrate storage and normal measurement noise. Look at a trend under similar conditions before changing your plan.",
        "body": r'''
<h2>The scale measures more than body fat</h2>
<p>Your scale reports total mass at one moment. That includes body tissue, water, glycogen, food moving through your digestive tract and waste. Several of those can change within hours. Body-fat change is much slower than the dramatic overnight jumps that make people want to rewrite an entire diet.</p>

<h2>Five common reasons the number moved</h2>
<div class="guide-example-grid">
<article><h3>More food in transit</h3><p>A later or larger meal has physical mass while it is being digested. The scale sees it even before absorption matters.</p></article>
<article><h3>More sodium</h3><p>A salty restaurant day can change thirst and fluid balance. A kidney review describes short-term body-weight increases after abrupt increases in sodium intake.</p></article>
<article><h3>More carbohydrate</h3><p>Carbohydrate is stored as glycogen. Glycogen status and body water are related, although the exact relationship is more complicated than a fixed water-per-gram rule.</p></article>
<article><h3>Training stress</h3><p>Hard or unfamiliar exercise can temporarily shift fluid as tissue responds and recovers.</p></article>
<article><h3>Bathroom timing</h3><p>Different bowel and bladder timing can move the number without saying anything useful about fat loss.</p></article>
<article><h3>Hormonal variation</h3><p>Menstrual-cycle-related fluid changes can affect scale weight. Individual patterns vary.</p></article>
</div>

<h2>What to do the morning after</h2>
<ol>
<li><strong>Do not compensate with an extreme restriction day.</strong> Return to your normal plan.</li>
<li><strong>Use the same measuring conditions.</strong> A common approach is morning, after using the bathroom and before eating, with similar clothing.</li>
<li><strong>Watch a rolling trend.</strong> Compare several weeks, not one Tuesday with one Wednesday.</li>
<li><strong>Add context.</strong> Note unusually salty meals, travel, hard training, menstrual-cycle timing or a late dinner.</li>
<li><strong>Adjust only when the trend supports it.</strong> If the average is moving away from your goal for multiple weeks, then review intake, activity and adherence.</li>
</ol>

<h2>A worked example</h2>
<p>Imagine your morning weights are 172.1, 171.8, 172.4, 171.9, 174.0, 172.6 and 172.2 pounds. The 174-pound reading looks dramatic by itself. In the context of the week, it looks like a brief spike that returned toward the established range. That pattern calls for observation, not punishment.</p>
<p>Weekly averages are not magic either. They simply reduce the power of a noisy reading. Compare averages taken with the same method and pay attention to the direction over enough time to matter.</p>

<h2>When an increase deserves medical attention</h2>
<p>Rapid weight gain accompanied by swelling, shortness of breath, chest symptoms or a new medical concern should not be treated as a routine diet fluctuation. Contact a qualified clinician promptly. Certain heart, kidney, liver, hormonal and medication-related issues can affect fluid balance, and a website cannot sort those out safely.</p>

<h2>Keep the response proportional</h2>
<p>If your plan is designed for fat loss, one higher restaurant meal does not erase it. If your plan is designed for muscle gain, a lower morning reading does not prove the bulk failed. Use the <a href="weight-goal-timeline-calculator.html">weight-goal timeline calculator</a> for a broad planning estimate, then judge real progress by the trend and by outcomes you care about—training, measurements, energy and consistency.</p>
''',
        "sources": [
            ("Relationship between sodium intake and water intake: review", "https://pubmed.ncbi.nlm.nih.gov/28614828/"),
            ("Muscle glycogen assessment and body hydration: narrative review", "https://pubmed.ncbi.nlm.nih.gov/36615811/"),
        ],
        "related": [("Weight-goal timeline calculator", "weight-goal-timeline-calculator.html"), ("Macros for weight loss", "macros-for-weight-loss.html"), ("Cutting, bulking and maintenance", "cutting-bulking-maintenance-explained.html")],
    },
    {
        "path": "how-to-hit-protein-goal-on-budget.html",
        "title": "How to Hit Your Protein Goal on a Budget | GetMacros",
        "h1": "How to hit your protein goal on a budget",
        "desc": "Reach your protein goal on a budget by comparing cost per gram, choosing flexible staples and planning meals that use the whole package.",
        "dek": "The cheapest package is not always the cheapest protein—and the best bargain is food you will actually finish.",
        "read": "9 min read",
        "quick": "Choose two or three affordable protein anchors, compare them by usable servings or cost per gram of protein, and build repeatable meals around them. Prices vary too much by store and week for one universal cheapest-food ranking.",
        "body": r'''
<h2>Start with your target, not a shopping list</h2>
<p>A budget plan works better when you know the size of the job. Estimate a reasonable protein target with the <a href="calculators.html">free macro calculator</a> or read <a href="how-much-protein-per-day.html">how much protein you need per day</a>. More is not automatically better, and an inflated target makes every grocery bill harder.</p>
<p>Next, split the target across meals you already eat. Someone aiming for 120 grams could think in four meals of roughly 30 grams, but there is no requirement to make every meal identical. The point is to turn one intimidating daily number into a few shopping decisions.</p>

<h2>Use cost per gram without letting it run the whole diet</h2>
<p>Package price hides serving size and protein density. Our <a href="protein-value-calculator.html">protein cost per gram calculator</a> uses a simple comparison:</p>
<div class="guide-formula"><span>Package price</span><b>÷</b><span>Total grams of protein in the package</span><b>=</b><span>Cost per gram of protein</span></div>
<p>This is useful for comparing two tubs of yogurt, sizes of chicken, cans of fish or powders. It is not a nutrition score. Beans may contribute fiber and carbohydrate; fish may contribute omega-3 fats; dairy may contribute calcium. Cost is one lens.</p>

<h2>Build a flexible protein bench</h2>
<div class="guide-decision-table" role="region" aria-label="Budget protein roles" tabindex="0"><table><thead><tr><th>Role</th><th>Foods to compare locally</th><th>Why it helps</th></tr></thead><tbody>
<tr><td>Low-prep staple</td><td>Eggs, Greek yogurt, cottage cheese, canned tuna, tofu</td><td>Reduces the cost of last-minute takeout</td></tr>
<tr><td>Batch-cook anchor</td><td>Dry lentils, beans, chicken thighs, ground turkey, textured vegetable protein</td><td>Works across bowls, soups, wraps and pasta</td></tr>
<tr><td>Freezer backup</td><td>Frozen fish, edamame, cooked beans, portioned meat</td><td>Extends shelf life and cuts waste</td></tr>
<tr><td>Convenience option</td><td>Milk, soy drink, canned chicken, protein powder when competitively priced</td><td>Fills gaps without cooking another meal</td></tr>
</tbody></table></div>
<p>USDA resources list beans, lentils, eggs, peanut butter, canned tuna and several frozen or canned meats among practical protein foods. USDA budget guidance also suggests comparing forms and using lower-cost options such as beans, peas and eggs. Local prices still decide the winner.</p>

<h2>A shopping method that survives price changes</h2>
<ol>
<li><strong>Check unit price and servings.</strong> Compare the shelf label, package weight and edible yield.</li>
<li><strong>Calculate protein value for the close contenders.</strong> Do not do this for every food in the building.</li>
<li><strong>Choose foods with multiple uses.</strong> A large package is not a deal if half spoils.</li>
<li><strong>Plan the leftovers before buying.</strong> Tonight’s chicken can become tomorrow’s wrap; lentils can move from soup to pasta sauce.</li>
<li><strong>Keep one emergency meal.</strong> Eggs and toast, tuna pasta, lentil curry or tofu stir-fry can protect both budget and protein target.</li>
</ol>

<h2>Three no-nonsense meal templates</h2>
<ul>
<li><strong>Bean-and-meat bowl:</strong> combine a smaller portion of meat with beans, rice and vegetables. You get protein from more than one ingredient and stretch the costlier item.</li>
<li><strong>High-protein breakfast:</strong> eggs plus yogurt or milk, with oats or toast and fruit.</li>
<li><strong>Pantry pasta:</strong> lentil or regular pasta with canned tuna, chicken, beans or textured vegetable protein and tomato sauce.</li>
</ul>

<h2>Where budget advice goes wrong</h2>
<p>Fixed “cheapest protein” lists age quickly. Sales, region, dietary restrictions, cooking equipment and package waste all matter. Supplements are not automatically cheaper or more expensive; calculate the actual product. And do not make the entire diet a protein-efficiency contest. Vegetables, fruit, grains and fats still have jobs.</p>
''',
        "sources": [
            ("USDA Foods product information sheets: proteins", "https://www.fns.usda.gov/usda-foods/household-product-information-sheets/proteins"),
            ("USDA MyPlate: Healthy Eating on a Budget", "https://www.myplate.gov/web/eat-healthy/healthy-eating-budget"),
            ("Protein foods and affordability analysis", "https://pubmed.ncbi.nlm.nih.gov/31706353/"),
        ],
        "related": [("Protein cost per gram calculator", "protein-value-calculator.html"), ("High-protein foods list", "high-protein-foods-list.html"), ("Budget meal builder", "budget-meal-builder.html")],
    },
    {
        "path": "calories-on-rest-days.html",
        "title": "Should You Eat the Same Calories on Rest Days? | GetMacros",
        "h1": "Should you eat the same calories on rest days?",
        "desc": "You can keep calories the same on rest days or cycle them around training. Compare both approaches while keeping recovery and your weekly goal in view.",
        "dek": "A rest day is still a recovery day. Your calorie pattern can change, but the weekly plan still has to add up.",
        "read": "8 min read",
        "quick": "Keeping calories similar every day is simple and works well for many people. Eating somewhat more on hard training days and less on rest days can also work if it improves performance or adherence. Keep protein consistent and avoid turning rest days into severe restriction.",
        "body": r'''
<h2>Both approaches can work</h2>
<p>Your body does not reset its energy accounting at midnight. Training, recovery, spontaneous movement and appetite vary across the week. That means daily calories do not have to be identical—but changing them is optional, not automatically more advanced.</p>
<div class="guide-decision-table" role="region" aria-label="Same calories versus calorie cycling" tabindex="0"><table><thead><tr><th>Approach</th><th>Best feature</th><th>Watch for</th></tr></thead><tbody>
<tr><td>Same target each day</td><td>Simple shopping, meal prep and tracking</td><td>May feel inflexible around unusually hard sessions</td></tr>
<tr><td>More on training days</td><td>Places more carbohydrate and energy near demanding work</td><td>Rest days can become needlessly low</td></tr>
<tr><td>Flexible range</td><td>Allows appetite and schedule to vary while preserving the weekly direction</td><td>A wide range can become inconsistent without a plan</td></tr>
</tbody></table></div>

<h2>Why rest days still need food</h2>
<p>Exercise creates a recovery demand that continues after the session. Muscle remodeling, glycogen restoration and the rest of daily life do not stop because the calendar says “rest.” Research in endurance-trained men has even found that protein requirements may remain substantial on recovery days. That single study does not set everyone’s target, but it is a useful reminder not to treat recovery as inactivity.</p>

<h2>Keep these anchors steady</h2>
<h3>Protein</h3>
<p>Keep your daily protein target broadly consistent unless a qualified professional has given you a different plan. Recovery continues between workouts, and a predictable protein pattern is easier to execute.</p>
<h3>Total weekly direction</h3>
<p>For fat loss, the overall deficit needs to be tolerable and sustained. For muscle gain, the surplus should support training without turning every rest day into an uncontrolled refeed. Maintenance leaves the most room to follow hunger and routine.</p>
<h3>Food quality and enjoyment</h3>
<p>Do not remove vegetables, fruit or satisfying meals to force an arbitrary low-day number. A plan that makes rest days miserable often creates a rebound later.</p>

<h2>When calorie cycling may be useful</h2>
<ul>
<li>You have long or high-volume sessions that clearly feel better with more carbohydrate.</li>
<li>Your appetite is reliably higher on training days and lower on rest days.</li>
<li>You prefer a larger pre- and post-workout food budget.</li>
<li>Your weekly target remains clear and the pattern does not trigger restrict-and-overeat behavior.</li>
</ul>

<h2>When the same target may be better</h2>
<ul>
<li>You value predictable meal prep and grocery shopping.</li>
<li>Your training-day and rest-day activity are not dramatically different.</li>
<li>Frequent target changes make tracking harder.</li>
<li>You notice that “low days” worsen mood, recovery or your relationship with food.</li>
</ul>

<h2>A simple way to set the week</h2>
<p>Start with the daily estimate from the <a href="calculators.html">free macro calculator</a>. Keep it consistent for two or three weeks while watching body-weight trend, training quality, hunger and adherence. Only add calorie cycling when you can name the problem it solves.</p>
<p>If you do cycle, move a modest amount rather than inventing two completely different diets. Many people shift mostly carbohydrate because it directly supports demanding training, while protein stays similar. The weekly average should still reflect cutting, maintenance or gaining.</p>

<h2>The decision in one sentence</h2>
<p>Eat the same calories on rest days if consistency helps you; vary them if the variation has a clear purpose. Neither pattern compensates for a weekly intake that does not match the goal.</p>
''',
        "sources": [
            ("Protein requirements on training and rest days in endurance-trained males", "https://pubmed.ncbi.nlm.nih.gov/38603808/"),
            ("ISSN position stand: diets and body composition", "https://pubmed.ncbi.nlm.nih.gov/28630601/"),
            ("ISSN position stand: nutrient timing", "https://pubmed.ncbi.nlm.nih.gov/28919842/"),
        ],
        "related": [("Free macro calculator", "calculators.html"), ("Cutting, bulking and maintenance", "cutting-bulking-maintenance-explained.html"), ("Macros for muscle gain", "macros-for-muscle-gain.html")],
    },
]

ARTICLES.extend([
    {
        "path": "how-to-calculate-maintenance-calories.html",
        "title": "How to Calculate Maintenance Calories | GetMacros",
        "h1": "How to calculate maintenance calories",
        "desc": "Calculate maintenance calories with a clear starting estimate, then use your weight trend to find the intake that actually maintains your weight.",
        "dek": "A formula gives you a starting point. Your own consistent data turns it into a useful target.",
        "read": "8 min read",
        "quick": "Estimate resting energy needs with a validated equation, account for activity, then hold the estimate steady long enough to compare average intake with your body-weight trend. Maintenance is a working range, not one permanently exact number.",
        "body": r'''
<h2>Maintenance calories are an average</h2>
<p>Your maintenance calories are the average intake that keeps body weight broadly stable over time. They are often called total daily energy expenditure, or TDEE. The total includes resting metabolism, movement, training and the energy used to digest food. None of those components is perfectly identical every day.</p>
<p>That is why maintenance is better treated as a range. A restaurant day, a long walk and a quiet workday can all have different totals while the weekly pattern remains stable.</p>

<h2>Method 1: start with an equation</h2>
<p>The GetMacros calculator uses the Mifflin–St Jeor equation to estimate resting energy expenditure from weight, height, age and equation sex. The original study derived the equation from 498 healthy adults. An activity factor then converts that resting estimate into an estimated daily total.</p>
<div class="guide-formula"><span>Estimated resting needs</span><b>×</b><span>Activity factor</span><b>=</b><span>Starting maintenance estimate</span></div>
<p>Activity is the least precise input. “Moderately active” can mean different things to two people, and planned exercise is only part of daily movement. Use the result as a first estimate—not proof that your body burns that exact number.</p>

<h2>Method 2: use your own trend</h2>
<ol>
<li>Choose the calculator estimate or your current average intake as a starting point.</li>
<li>Keep intake reasonably consistent for two to three weeks.</li>
<li>Weigh under similar conditions and compare weekly averages, not isolated days.</li>
<li>If the average is stable, your average intake is near maintenance.</li>
<li>If the trend moves consistently, make a modest adjustment and observe again.</li>
</ol>
<p>Food tracking and scale weight both contain noise. Restaurant portions vary, labels round values and body water changes quickly. More decimal places do not fix uncertain inputs.</p>

<h2>When should the estimate change?</h2>
<p>Recheck after a meaningful weight change, a major shift in training or daily movement, or several weeks in which the trend no longer matches the plan. Energy expenditure changes with body size and composition, and it can also adapt during prolonged underfeeding. Do not react to one high or low morning.</p>

<h2>A practical example</h2>
<p>Suppose the calculator estimates 2,450 calories. You average about 2,400 for three weeks and your weekly weight averages are 176.2, 176.0 and 176.3 pounds. That intake is probably close enough to maintenance for planning. Calling it exactly 2,413 would suggest precision the data cannot support.</p>
<p>Start with the <a href="calculators.html">free macro calculator</a>. If your goal changes, read <a href="cutting-bulking-maintenance-explained.html">cutting, bulking and maintenance</a> before changing the number.</p>
''',
        "sources": [
            ("Mifflin–St Jeor resting energy equation", "https://pubmed.ncbi.nlm.nih.gov/2305711/"),
            ("NIDDK Body Weight Planner", "https://www.niddk.nih.gov/bwp"),
            ("Control of energy expenditure in humans", "https://pubmed.ncbi.nlm.nih.gov/25905198/"),
        ],
        "related": [("Free macro calculator", "calculators.html"), ("What is a calorie deficit?", "what-is-a-calorie-deficit.html"), ("When to recalculate macros", "when-to-recalculate-calories-and-macros.html")],
    },
    {
        "path": "what-is-a-calorie-deficit.html",
        "title": "What Is a Calorie Deficit? | GetMacros",
        "h1": "What is a calorie deficit?",
        "desc": "A calorie deficit means taking in less energy than you use over time. Learn how to estimate one, why weight loss slows and what to monitor.",
        "dek": "A deficit describes an energy gap. It does not tell you which foods to eat or how aggressive the plan should be.",
        "read": "8 min read",
        "quick": "A calorie deficit occurs when average energy intake is below average energy expenditure. It can produce weight loss over time, but the relationship is dynamic: expenditure, body weight, appetite and adherence can change as the plan continues.",
        "body": r'''
<h2>The plain-language definition</h2>
<p>Your body uses energy at rest, during movement and exercise, and while processing food. When average intake stays below average expenditure, stored energy helps cover the difference. That is a calorie deficit.</p>
<p>The important word is <em>average</em>. One meal does not create or erase a long-term result. A higher restaurant day can exist inside an overall deficit, just as one low-calorie day cannot guarantee weight loss.</p>

<h2>How to estimate a starting deficit</h2>
<ol>
<li>Estimate your <a href="how-to-calculate-maintenance-calories.html">maintenance calories</a>.</li>
<li>Choose a moderate starting reduction rather than the largest number you can tolerate for a few days.</li>
<li>Keep protein, produce and satisfying meals in the plan.</li>
<li>Track the trend for several weeks under similar conditions.</li>
<li>Adjust only when the trend and adherence both justify it.</li>
</ol>
<p>The CDC emphasizes gradual, steady weight loss and a broader lifestyle that includes eating patterns, activity, sleep and stress management. A calorie target is one tool inside that process, not the whole process.</p>

<h2>Why the simple 3,500-calorie rule falls short</h2>
<p>The familiar rule assumes a fixed energy gap produces the same rate forever. Human weight change is not linear. A smaller body generally requires less energy, movement can change, and the body can adapt to prolonged restriction. The NIH Body Weight Planner uses a dynamic model for that reason.</p>
<p>This does not mean a deficit “stops working.” It means the original estimate may no longer describe the current situation.</p>

<h2>Signs the plan may be too aggressive</h2>
<ul>
<li>Training performance and recovery decline persistently.</li>
<li>Hunger or fatigue makes the plan difficult to sustain.</li>
<li>Food rules become increasingly rigid or distressing.</li>
<li>The rate of loss is much faster than intended.</li>
</ul>
<p>Pregnancy, growth, eating-disorder recovery and many medical conditions require individualized care. Speak with a qualified clinician or registered dietitian rather than using a general calculator.</p>

<h2>Judge the plan by more than the scale</h2>
<p>Use weekly weight trends, but also monitor strength, energy, hunger, sleep and your ability to eat normally around other people. A mathematically larger deficit is not automatically a better plan.</p>
''',
        "sources": [
            ("CDC: Steps for Losing Weight", "https://www.cdc.gov/healthy-weight-growth/losing-weight/index.html"),
            ("NIDDK Body Weight Planner", "https://www.niddk.nih.gov/bwp"),
            ("Dynamic mathematical model of body-weight change", "https://pubmed.ncbi.nlm.nih.gov/21872751/"),
        ],
        "related": [("Maintenance calories", "how-to-calculate-maintenance-calories.html"), ("Macros for weight loss", "macros-for-weight-loss.html"), ("Weight-goal timeline", "weight-goal-timeline-calculator.html")],
    },
    {
        "path": "can-you-build-muscle-in-a-calorie-deficit.html",
        "title": "Can You Build Muscle in a Calorie Deficit? | GetMacros",
        "h1": "Can you build muscle in a calorie deficit?",
        "desc": "Muscle gain in a calorie deficit is possible for some people, but energy deficiency makes it harder. See who is most likely to progress and what matters.",
        "dek": "Possible does not mean equally likely for everyone—or optimal for maximizing muscle gain.",
        "read": "9 min read",
        "quick": "Some people can gain lean mass while losing fat, especially newer or returning lifters and people with more body fat. Resistance training and adequate protein matter, but larger energy deficits generally make lean-mass gains harder.",
        "body": r'''
<h2>The honest answer is “sometimes”</h2>
<p>Building muscle requires a training signal, amino acids and enough recovery. Stored body energy can help cover an intake deficit, so fat loss and lean-mass gain are not biologically incompatible. But an energy deficit makes the environment less favorable for maximizing growth.</p>
<p>A meta-analysis found that energy deficiency impaired lean-mass gains from resistance training even when strength gains remained possible. It also found a relationship between larger deficits and poorer lean-mass outcomes. That is a reason to avoid treating an extreme cut as a muscle-building shortcut.</p>

<h2>Who has the best chance?</h2>
<ul>
<li><strong>New lifters:</strong> the training stimulus is novel, leaving more room for early adaptation.</li>
<li><strong>People returning after time off:</strong> previously built muscle may return more readily than entirely new tissue is gained.</li>
<li><strong>People with more stored body fat:</strong> more stored energy is available while training creates a reason to retain or build lean tissue.</li>
<li><strong>People using a modest deficit:</strong> recovery is generally easier than during severe restriction.</li>
</ul>
<p>Advanced, already-lean lifters usually have less room for simultaneous progress. If maximum muscle gain is the priority, maintenance or a modest surplus is often the more predictable route.</p>

<h2>What the strongest experiment can—and cannot—show</h2>
<p>In a four-week randomized trial, young men completed intense resistance and interval training during a large energy deficit. The higher-protein group gained more lean mass and lost more fat than the lower-protein group. That shows recomposition can occur under tightly controlled, demanding conditions.</p>
<p>It does not prove everyone should copy the trial’s aggressive deficit, protein intake or six-day training schedule. The intervention was short, supervised and specific.</p>

<h2>Build the plan around four priorities</h2>
<ol>
<li><strong>Progressive resistance training:</strong> give the body a clear reason to adapt.</li>
<li><strong>Adequate daily protein:</strong> use a sensible range based on body size and training, not an unlimited target.</li>
<li><strong>A manageable deficit:</strong> faster weight loss can compete with recovery and lean-mass gain.</li>
<li><strong>Sleep and time:</strong> judge several weeks of strength, measurements and weight trends together.</li>
</ol>
<p>Use the <a href="calculators.html">macro calculator</a> as a starting estimate, then read <a href="body-recomposition-explained.html">body recomposition explained</a> for a longer-term view.</p>
''',
        "sources": [
            ("Higher protein during energy deficit and intense exercise: randomized trial", "https://pubmed.ncbi.nlm.nih.gov/26817506/"),
            ("Energy deficiency and resistance-training gains: meta-analysis", "https://pubmed.ncbi.nlm.nih.gov/34623696/"),
            ("ISSN position stand: protein and exercise", "https://pubmed.ncbi.nlm.nih.gov/28642676/"),
        ],
        "related": [("Body recomposition", "body-recomposition-explained.html"), ("Macros for muscle gain", "macros-for-muscle-gain.html"), ("Protein per day", "how-much-protein-per-day.html")],
    },
    {
        "path": "when-to-recalculate-calories-and-macros.html",
        "title": "When Should You Recalculate Calories and Macros? | GetMacros",
        "h1": "When should you recalculate calories and macros?",
        "desc": "Recalculate calories and macros after meaningful changes—not every scale fluctuation. Use weight trends, activity and performance to decide when.",
        "dek": "Update the target when the inputs or the trend have changed enough to matter.",
        "read": "7 min read",
        "quick": "Recalculate after a meaningful weight change, a sustained change in activity or training, a new goal, or several consistent weeks in which progress differs from the plan. Do not recalculate because of one meal or one weigh-in.",
        "body": r'''
<h2>Your target was always an estimate</h2>
<p>Calorie equations use current inputs such as weight, height, age and activity. Macro targets then divide that energy estimate according to the goal. If those inputs change, the old result can become less useful.</p>

<h2>Five good reasons to recalculate</h2>
<div class="guide-decision-table" role="region" aria-label="Reasons to recalculate calories and macros" tabindex="0"><table><thead><tr><th>Change</th><th>Why it matters</th></tr></thead><tbody>
<tr><td>Meaningful weight change</td><td>Body size and composition influence energy expenditure.</td></tr>
<tr><td>New activity pattern</td><td>A new job, step count or training schedule can change daily expenditure.</td></tr>
<tr><td>New goal</td><td>Maintenance, cutting and gaining require different energy directions.</td></tr>
<tr><td>Several weeks off-plan</td><td>A consistent trend can show that the starting estimate needs adjustment.</td></tr>
<tr><td>Major recovery change</td><td>Illness, injury or a return to training can change needs and priorities.</td></tr>
</tbody></table></div>

<h2>What does not justify a new target?</h2>
<ul>
<li>One high restaurant meal.</li>
<li>One unexpectedly high or low weigh-in.</li>
<li>A few days of soreness or appetite change.</li>
<li>A calculator giving a slightly different answer after rounding.</li>
</ul>
<p>Changing the target too often makes it impossible to learn from the plan. Hold a reasonable target steady long enough to see a trend.</p>

<h2>A simple review schedule</h2>
<ol>
<li>Compare weekly weight averages for at least two to three weeks.</li>
<li>Check training performance, hunger, energy and adherence.</li>
<li>Confirm that activity has not changed accidentally.</li>
<li>If the trend is consistently wrong for the goal, adjust modestly.</li>
<li>Run the <a href="calculators.html">calculator</a> again after a meaningful change in body weight or routine.</li>
</ol>

<h2>Why needs can fall during weight loss</h2>
<p>A smaller body generally uses less energy, and research also describes adaptive reductions in energy expenditure during prolonged restriction and weight loss. The size of that adaptation varies. It should not be used to declare a metabolism “broken,” but it is another reason an old maintenance estimate may stop matching current data.</p>
<p>Keep protein relatively stable unless body size, training or clinical advice changes the target. Most routine adjustments can come from carbohydrate and fat according to preference and training needs.</p>
''',
        "sources": [
            ("Changes in energy expenditure with weight gain and loss", "https://pubmed.ncbi.nlm.nih.gov/27739007/"),
            ("Body composition and adaptive thermogenesis during weight loss", "https://pubmed.ncbi.nlm.nih.gov/36863769/"),
            ("NIDDK Body Weight Planner", "https://www.niddk.nih.gov/bwp"),
        ],
        "related": [("Maintenance calories", "how-to-calculate-maintenance-calories.html"), ("Why weight jumped overnight", "why-did-i-gain-weight-overnight.html"), ("Cutting, bulking and maintenance", "cutting-bulking-maintenance-explained.html")],
    },
    {
        "path": "how-to-build-a-balanced-meal-with-macros.html",
        "title": "How to Build a Balanced Meal With Macros | GetMacros",
        "h1": "How to build a balanced meal with macros",
        "desc": "Build a balanced meal with protein, carbohydrate, produce and satisfying fat—then adjust portions for cutting, maintenance or bulking.",
        "dek": "Use macros to shape the meal, not to turn dinner into an accounting exercise.",
        "read": "9 min read",
        "quick": "Start with a useful protein source, add a carbohydrate that fits the meal, include fruit or vegetables, and use fats and flavor deliberately. Change portion sizes for your goal instead of inventing separate ‘diet foods.’",
        "body": r'''
<h2>A four-part meal template</h2>
<div class="guide-formula"><span>Protein</span><b>+</b><span>Carbohydrate</span><b>+</b><span>Produce</span><b>+</b><span>Fat and flavor</span></div>
<p>This is a flexible assembly method, not a rule that every plate must look identical. A bean burrito, salmon rice bowl, lentil curry and yogurt-oat breakfast can all satisfy it in different ways.</p>

<h2>1. Choose a protein anchor</h2>
<p>Pick a serving that makes a meaningful contribution to your daily target: poultry, fish, eggs, dairy, tofu, tempeh, beans, lentils or another food you enjoy. USDA MyPlate emphasizes variety because different protein foods bring different nutrients.</p>

<h2>2. Add carbohydrate for energy and satisfaction</h2>
<p>Rice, potatoes, oats, bread, pasta, fruit, corn, beans and other carbohydrate foods can support training and make a meal satisfying. The amount can rise on higher-energy days and shrink on lower-energy days without labeling the food itself good or bad.</p>

<h2>3. Add produce for volume, fiber and variety</h2>
<p>Use vegetables or fruit that fit the meal rather than forcing a plain side salad everywhere. Frozen, canned and fresh options can all work. Sauces and preparation affect calories and sodium, so include them in the meal rather than pretending they do not count.</p>

<h2>4. Use fat and flavor on purpose</h2>
<p>Oil, nuts, seeds, avocado, cheese and sauces can add flavor and energy. They are especially useful when appetite is low or calories are high. During a cut, measure calorie-dense additions often enough to understand the portion—but do not strip every meal of flavor.</p>

<h2>Adjust the same meal for three goals</h2>
<div class="guide-decision-table" role="region" aria-label="Balanced meal adjustments by goal" tabindex="0"><table><thead><tr><th>Goal</th><th>Practical adjustment</th></tr></thead><tbody>
<tr><td>Cutting</td><td>Keep the protein anchor, use plenty of produce and reduce the most calorie-dense extras first.</td></tr>
<tr><td>Maintenance</td><td>Use portions that leave energy, hunger and weight trend broadly stable.</td></tr>
<tr><td>Bulking</td><td>Add carbohydrate, a larger protein portion when needed, and convenient energy from fats or drinks.</td></tr>
</tbody></table></div>

<h2>Five meals built from the template</h2>
<ul>
<li>Chicken or tofu, rice, roasted vegetables and tahini sauce.</li>
<li>Eggs, toast, fruit and yogurt.</li>
<li>Lentil pasta, tomato sauce, vegetables and parmesan or nutritional yeast.</li>
<li>Salmon, potatoes, green beans and olive-oil dressing.</li>
<li>A burrito bowl with beans, rice, meat or sofritas, salsa and guacamole.</li>
</ul>
<p>When eating out, use the same logic: identify the protein, carbohydrate, produce and calorie-dense extras, then compare the published numbers in <a href="restaurant-meal-finder.html">Healthy Order Match</a>.</p>
''',
        "sources": [
            ("USDA MyPlate", "https://www.myplate.gov/"),
            ("USDA MyPlate: Protein Foods Group", "https://www.myplate.gov/web/eat-healthy/protein-foods"),
            ("Dietary Guidelines for Americans, 2025–2030", "https://cdn.realfood.gov/DGA_508.pdf"),
        ],
        "related": [("Free macro calculator", "calculators.html"), ("High-protein foods", "high-protein-foods-list.html"), ("Healthy Order Match", "restaurant-meal-finder.html")],
    },
])


def article_schema(item: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["h1"],
        "description": item["desc"],
        "datePublished": UPDATED,
        "dateModified": UPDATED,
        "mainEntityOfPage": f'{SITE}/{item["path"]}',
        "author": {"@type": "Organization", "name": "The GetMacros.net editorial team"},
        "publisher": {"@type": "Organization", "name": "GetMacros.net", "url": SITE},
    }


def build_article(item: dict) -> str:
    sources = "".join(
        f'<li><a href="{html.escape(url, quote=True)}" rel="noopener">{html.escape(label)}</a></li>'
        for label, url in item["sources"]
    )
    related = "".join(
        f'<a href="{html.escape(url, quote=True)}"><span>Keep going</span><b>{html.escape(label)}</b><i aria-hidden="true">→</i></a>'
        for label, url in item["related"]
    )
    return f'''{head(item["path"], item["title"], item["desc"], schema=article_schema(item))}<body class="site-v3 article-page focused-guide">
{nav("guides")}<main id="main-content">{breadcrumbs([("Home", "index.html"), ("Nutrition guides", "articles.html"), (item["h1"], None)])}
<article>
<header class="focused-guide-hero liquid-surface" id="guide-top"><div class="container"><div class="focused-guide-kicker"><span>Practical nutrition guide</span><span>{item["read"]}</span></div><h1 data-reveal-title>{html.escape(item["h1"])}</h1><p>{html.escape(item["dek"])}</p><div class="focused-guide-byline"><span>By the GetMacros editorial team</span><span>Reviewed and updated {UPDATED_HUMAN}</span></div></div></header>
<div class="container focused-guide-layout"><div class="focused-guide-body">
<aside class="guide-quick-answer"><span>Short answer</span><p>{html.escape(item["quick"])}</p></aside>
{item["body"]}
<section class="guide-sources"><h2>Sources and evidence</h2><p>GetMacros uses primary research, position stands and official resources where possible. These sources support the guide; they do not make it individualized medical advice.</p><ol>{sources}</ol></section>
</div><aside class="focused-guide-side"><div><span>On this page</span><a href="#guide-top">Back to the top</a><a href="articles.html">All nutrition guides</a><a href="editorial-policy.html">How we review content</a></div></aside></div>
<nav class="guide-related" aria-label="Related guides"><div class="container">{related}</div></nav>
</article></main>{footer()}</body></html>'''


def refresh_hub() -> None:
    hub_path = ROOT / "articles.html"
    text = hub_path.read_text(encoding="utf-8")
    text = re.sub(r'<section class="gm6-library-controls">.*?</section>', "", text, flags=re.S)
    groups = []
    for group, paths in GUIDE_GROUPS.items():
        cards = []
        for path in paths:
            page = (ROOT / path).read_text(encoding="utf-8")
            title = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
            desc = re.search(r'<meta name="description" content="([^"]+)">', page, re.S)
            label = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else path.removesuffix('.html').replace('-', ' ')
            summary = html.unescape(desc.group(1)).strip() if desc else "Read this focused GetMacros guide."
            cards.append(f'<a class="guide-card" href="{path}"><h3>{html.escape(html.unescape(label))}</h3><p>{html.escape(summary)}</p></a>')
        section_id = {
            "Macros and goals": "macros-and-goals",
            "Eating out": "eating-out",
            "Labels and recipes": "labels-and-recipes",
        }.get(group)
        id_attr = f' id="{section_id}"' if section_id else ""
        groups.append(f'<section class="guide-group data-section"{id_attr}><div class="container"><div class="section-head"><h2>{html.escape(group)}</h2></div><div class="guide-grid">{"".join(cards)}</div></div></section>')
    text = re.sub(r'<section class="guide-group[^>]*>.*?(?=<div class="ad-auto-anchor")', "".join(groups), text, count=1, flags=re.S)
    count = sum(len(paths) for paths in GUIDE_GROUPS.values())
    text = re.sub(r'("numberOfItems"\s*:\s*)\d+', rf'\g<1>{count}', text)
    hub_path.write_text(text, encoding="utf-8", newline="\n")


for article in ARTICLES:
    (ROOT / article["path"]).write_text(build_article(article), encoding="utf-8", newline="\n")
refresh_hub()
print(f"Built {len(ARTICLES)} focused guides and refreshed articles.html.")
