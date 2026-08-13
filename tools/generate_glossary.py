#!/usr/bin/env python3
"""Generates glossary.html — an A-Z nutrition terms reference for students."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_articles import ROOT, nav_html, FOOTER, ICON_SPRITE, ADSENSE_LOADER, AD_SLOT, seo_meta, article_jsonld, AUTHOR_NAME  # noqa: E402

TERMS = [
    ("Acceptable Macronutrient Distribution Range (AMDR)", "The range of intake for a macronutrient associated with reduced risk of chronic disease while providing adequate intake of essential nutrients — 10-35% of calories from protein, 20-35% from fat, 45-65% from carbohydrate.", "how-many-carbs-per-day.html"),
    ("Amino acid", "The building block of protein. 20 exist in the human body; 9 are essential and must come from food.", "complete-vs-incomplete-protein.html"),
    ("Anabolism", "The metabolic process of building larger molecules from smaller ones, such as building muscle protein from amino acids. The opposite of catabolism.", "body-recomposition-explained.html"),
    ("Basal Metabolic Rate (BMR)", "The number of calories your body burns at complete rest just to maintain basic functions like breathing and circulation.", "tdee-vs-bmr.html"),
    ("Bulking", "A deliberate phase of eating in a calorie surplus to support muscle growth.", "macros-for-muscle-gain.html"),
    ("Calorie", "A unit of energy. In nutrition, \"Calorie\" (capital C) technically refers to a kilocalorie, the energy needed to raise 1kg of water by 1°C.", "tdee-vs-bmr.html"),
    ("Carbohydrate", "One of the three macronutrients; broken down into glucose for energy and stored as glycogen.", "carbs.html"),
    ("Catabolism", "The metabolic process of breaking larger molecules into smaller ones for energy, such as breaking down muscle protein into amino acids. The opposite of anabolism.", "low-carb-diet-effects.html"),
    ("Cholesterol", "A waxy lipid used to build cell membranes and steroid hormones; found in food and also produced by the liver.", "cholesterol-explained.html"),
    ("Complete protein", "A protein source that supplies all 9 essential amino acids in sufficient amounts.", "complete-vs-incomplete-protein.html"),
    ("Cutting", "A deliberate phase of eating in a calorie deficit to lose body fat while trying to preserve muscle.", "macros-for-weight-loss.html"),
    ("Deficit (calorie)", "Eating fewer calories than your body burns (TDEE), causing weight loss over time.", "macros-for-weight-loss.html"),
    ("Dietary Reference Intakes (DRI)", "A set of nutrient reference values (including RDA and AMDR) published by the U.S. National Academies used to plan and assess diets.", "how-much-protein-per-day.html"),
    ("Disaccharide", "A carbohydrate made of two linked sugar units, such as sucrose (table sugar) or lactose (milk sugar).", "simple-vs-complex-carbs.html"),
    ("Essential amino acid", "One of 9 amino acids the body cannot synthesize on its own and must obtain from food.", "complete-vs-incomplete-protein.html"),
    ("Essential fatty acid (EFA)", "A fat the body cannot make itself — omega-3 and omega-6 fatty acids — and must get from food.", "omega-3-vs-omega-6.html"),
    ("Fiber", "A type of carbohydrate the body can't fully digest; supports digestion, blood sugar control, and gut health.", "fiber-benefits.html"),
    ("Glucose", "The simple sugar cells use directly for energy; the main breakdown product of dietary carbohydrate.", "carbs.html"),
    ("Gluconeogenesis", "The process of making new glucose from non-carbohydrate sources, including amino acids from protein — increases when carbohydrate and glycogen are low.", "low-carb-diet-effects.html"),
    ("Glycemic index (GI)", "A ranking of how quickly a carbohydrate food raises blood sugar compared to pure glucose.", "glycemic-index-explained.html"),
    ("Glycogen", "The storage form of glucose, held mainly in muscle and liver tissue and used as an energy reserve.", "what-is-glycogen.html"),
    ("Hydrogenation", "An industrial process that adds hydrogen to liquid vegetable oil to make it more solid; partial hydrogenation is the main source of artificial trans fat.", "trans-fat-explained.html"),
    ("IIFYM", "\"If It Fits Your Macros\" — a flexible dieting approach where food choices are unrestricted as long as daily macro targets are met.", "iifym-flexible-dieting.html"),
    ("Insulin", "A hormone that lowers blood sugar by helping cells absorb glucose from the bloodstream.", "glycemic-index-explained.html"),
    ("Joule", "The SI unit of energy; 1 dietary Calorie (kilocalorie) equals about 4,184 joules. Used alongside Calories on some nutrition labels outside the US.", "tdee-vs-bmr.html"),
    ("Ketosis", "A metabolic state where the body burns fat and produces ketones for fuel instead of relying primarily on glucose, typically triggered by very low carbohydrate intake.", "ketogenic-diet-explained.html"),
    ("Kwashiorkor", "A severe form of malnutrition caused by inadequate protein intake, causing swelling, a swollen liver, and impaired growth.", "protein-deficiency-symptoms.html"),
    ("Lipid", "The broader scientific term for fats and fat-like substances, including triglycerides and cholesterol.", "fats.html"),
    ("Macronutrient", "A nutrient the body needs in large amounts for energy: protein, fat, or carbohydrate.", "micronutrients-vs-macronutrients.html"),
    ("Maintenance calories", "The number of calories that keeps body weight stable — roughly equal to TDEE.", "tdee-vs-bmr.html"),
    ("Metabolism", "The sum of all chemical processes that convert food into energy and building blocks for the body.", "meal-frequency-and-metabolism.html"),
    ("Micronutrient", "A nutrient needed in small amounts, such as a vitamin or mineral; doesn't provide calories.", "micronutrients-vs-macronutrients.html"),
    ("Monounsaturated fat", "An unsaturated fat with one double bond in its chemical structure; liquid at room temperature. Found in olive oil and avocado.", "saturated-vs-unsaturated-fat.html"),
    ("Muscle protein synthesis (MPS)", "The biological process of building new muscle protein, stimulated by both resistance exercise and protein intake.", "protein-for-muscle-growth.html"),
    ("Nitrogen balance", "A measure comparing nitrogen (protein) intake to nitrogen loss, used to assess whether the body is gaining, maintaining, or losing protein/muscle mass overall.", "protein.html"),
    ("Omega-3 fatty acid", "An essential polyunsaturated fat found in fatty fish, walnuts, and flaxseed; involved in reducing inflammation.", "omega-3-vs-omega-6.html"),
    ("Omega-6 fatty acid", "An essential polyunsaturated fat abundant in vegetable oils; needed in balance with omega-3.", "omega-3-vs-omega-6.html"),
    ("Physical Activity Level (PAL)", "A multiplier applied to BMR to estimate total daily energy expenditure based on activity level.", "tdee-vs-bmr.html"),
    ("Polysaccharide", "A carbohydrate made of long chains of sugar units, such as starch or glycogen.", "simple-vs-complex-carbs.html"),
    ("Polyunsaturated fat", "An unsaturated fat with two or more double bonds; includes essential omega-3 and omega-6 fats.", "saturated-vs-unsaturated-fat.html"),
    ("Protein", "One of the three macronutrients, made of amino acids; used to build and repair tissue, enzymes, hormones, and antibodies.", "protein.html"),
    ("Recommended Dietary Allowance (RDA)", "The average daily intake level sufficient to meet the nutrient needs of nearly all healthy people in a group.", "how-much-protein-per-day.html"),
    ("Saturated fat", "A fat with no double bonds in its chemical structure, allowing it to pack tightly and stay solid at room temperature. Found in butter and fatty meat.", "saturated-vs-unsaturated-fat.html"),
    ("Sarcopenia", "The age- or inactivity-related loss of muscle mass and strength.", "protein-deficiency-symptoms.html"),
    ("Satiety", "The feeling of fullness that suppresses hunger after eating; protein and fiber are especially satiating.", "fiber-benefits.html"),
    ("Simple carbohydrate", "A carbohydrate made of one or two sugar units, digested and absorbed quickly.", "simple-vs-complex-carbs.html"),
    ("Starch", "A complex carbohydrate (polysaccharide) made of many linked glucose units; found in grains, potatoes, and legumes.", "sugar-vs-starch.html"),
    ("Surplus (calorie)", "Eating more calories than your body burns (TDEE), supporting weight and muscle gain over time.", "macros-for-muscle-gain.html"),
    ("Total Daily Energy Expenditure (TDEE)", "The total number of calories burned in a day, including BMR, digestion, and all activity.", "tdee-vs-bmr.html"),
    ("Thermic Effect of Food (TEF)", "The energy your body uses to digest, absorb, and metabolize food — protein has the highest TEF of the three macronutrients.", "tdee-vs-bmr.html"),
    ("Trans fat", "An unsaturated fat that has been chemically altered (usually via partial hydrogenation) to behave more like a saturated fat; linked to negative cardiovascular effects.", "trans-fat-explained.html"),
    ("Triglyceride", "The main form of fat stored in the body and found in food — three fatty acid chains attached to a glycerol backbone.", "fats.html"),
    ("Unsaturated fat", "A fat containing one or more double bonds in its structure, keeping it liquid at room temperature. Found in oils, nuts, and fish.", "saturated-vs-unsaturated-fat.html"),
    ("Vegan diet", "An eating pattern that excludes all animal products, including meat, dairy, eggs, and honey; requires deliberate planning to combine plant proteins for a complete amino acid profile.", "vegan-macros-guide.html"),
    ("Visceral fat", "Body fat stored deep around the abdominal organs, as opposed to just under the skin; elevated levels are linked to greater metabolic and cardiovascular risk.", "water-weight-vs-fat-loss.html"),
    ("VLDL (Very-Low-Density Lipoprotein)", "A lipoprotein made by the liver that carries triglycerides through the bloodstream to tissues; elevated VLDL is associated with higher cardiovascular risk.", "cholesterol-explained.html"),
    ("Whey protein", "A fast-digesting, complete protein derived from milk during cheesemaking; a common protein supplement.", "protein-powder-101.html"),
    ("Yo-yo dieting", "A repeating cycle of weight loss followed by weight regain, often from unsustainable calorie deficits; also called weight cycling.", "cutting-bulking-maintenance-explained.html"),
    ("Zone diet", "A dieting approach that targets a fixed 40/30/30 percent split of calories from carbohydrate, protein, and fat at every meal.", "how-to-calculate-macros-by-hand.html"),
]


def build():
    by_letter = {}
    for term, definition, link in TERMS:
        letter = term[0].upper()
        by_letter.setdefault(letter, []).append((term, definition, link))
    letters = sorted(by_letter.keys())

    jump = "\n".join(f'<a href="#letter-{l}">{l}</a>' for l in letters)

    sections = ""
    for l in letters:
        items = "\n".join(
            f'''        <div class="glossary-term"><dt>{term}</dt><dd>{definition} <a href="{link}">Read more →</a></dd></div>'''
            for term, definition, link in by_letter[l]
        )
        sections += f'''  <section class="tight">
    <div class="container">
      <h2 class="glossary-letter" id="letter-{l}">{l}</h2>
      <dl>
{items}
      </dl>
    </div>
  </section>
'''

    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>Nutrition Glossary: A-Z Terms for Students | GetMacros.net</title>
<meta name="description" content="An A-Z glossary of macronutrient and nutrition science terms — amino acids, glycogen, AMDR, ketosis, TDEE, and more — built for nutrition students.">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/glossary.html">
{seo_meta("Nutrition Glossary: A-Z Terms for Students", "An A-Z glossary of macronutrient and nutrition science terms — amino acids, glycogen, AMDR, ketosis, TDEE, and more — built for nutrition students.", "https://getmacros.net/glossary.html", og_type="website")}
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{nav_html("glossary")}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-book"/></svg> For students</p>
      <h1>Nutrition glossary</h1>
      <p>{len(TERMS)} terms every nutrition student should know, from amino acids to TDEE — each one links to the full article for more depth.</p>
    </div>
  </section>

  <section class="tight">
    <div class="container">
      <div class="glossary-jump">
{jump}
      </div>
    </div>
  </section>

{sections}
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js"></script>
<script src="js/reveal.js"></script>
<script src="js/ads-config.js"></script>
<script src="js/ads.js"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "glossary.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path, f"({len(TERMS)} terms)")


if __name__ == "__main__":
    build()
