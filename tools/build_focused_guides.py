#!/usr/bin/env python3
"""Build the five focused, evidence-led guides added in August 2026."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from focus_components import SITE, breadcrumbs, footer, head, nav
from site_scope import GUIDE_GROUPS

ROOT = Path(__file__).resolve().parents[1]
UPDATED = "2026-08-30"

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
<header class="focused-guide-hero liquid-surface" id="guide-top"><div class="container"><div class="focused-guide-kicker"><span>Practical nutrition guide</span><span>{item["read"]}</span></div><h1 data-reveal-title>{html.escape(item["h1"])}</h1><p>{html.escape(item["dek"])}</p><div class="focused-guide-byline"><span>By the GetMacros editorial team</span><span>Reviewed and updated August 30, 2026</span></div></div></header>
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
        groups.append(f'<section class="guide-group data-section"><div class="container"><div class="section-head"><h2>{html.escape(group)}</h2></div><div class="guide-grid">{"".join(cards)}</div></div></section>')
    text = re.sub(r'<section class="guide-group[^>]*>.*?(?=<div class="ad-auto-anchor")', "".join(groups), text, count=1, flags=re.S)
    count = sum(len(paths) for paths in GUIDE_GROUPS.values())
    text = re.sub(r'("numberOfItems"\s*:\s*)\d+', rf'\g<1>{count}', text)
    hub_path.write_text(text, encoding="utf-8", newline="\n")


for article in ARTICLES:
    (ROOT / article["path"]).write_text(build_article(article), encoding="utf-8", newline="\n")
refresh_hub()
print(f"Built {len(ARTICLES)} focused guides and refreshed articles.html.")
