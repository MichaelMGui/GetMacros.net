#!/usr/bin/env python3
"""Generates the quiz pages for GetMacros.net. Run: python3 tools/generate_quizzes.py"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_articles import ROOT, nav_html, FOOTER, HERO_STYLE, ICON_SPRITE, ADSENSE_LOADER, AD_SLOT, seo_meta, article_jsonld, breadcrumb_jsonld, AUTHOR_NAME  # noqa: E402

QUIZZES = []


def add(slug, title, meta, category, eyebrow, h1, intro, questions, tiers=None):
    QUIZZES.append(dict(slug=slug, title=title, meta=meta, category=category,
                         eyebrow=eyebrow, h1=h1, intro=intro, questions=questions, tiers=tiers))


def q(question, options, correct, explain, link_href, link_label):
    return {"q": question, "options": options, "correct": correct, "explain": explain,
            "link": {"href": link_href, "label": link_label}}


add(
    "protein-quiz", "Protein Quiz: Test Your Knowledge",
    "An 8-question quiz testing what you know about protein, muscle building, and deficiency.",
    "protein", "Protein Quiz", "How much do you really know about protein?",
    "8 questions, straight from the articles on this site.",
    [
        q("What's the RDA (baseline) protein intake for a sedentary adult?",
          ["0.4 g/kg body weight", "0.8 g/kg body weight", "1.6 g/kg body weight", "2.2 g/kg body weight"], 1,
          "0.8 g/kg is the minimum intake shown to prevent deficiency in a sedentary adult — not an optimal target for anyone who trains.",
          "how-much-protein-per-day.html", "How much protein do you need?"),
        q("How long can muscle protein synthesis stay elevated after a resistance training session?",
          ["About 30 minutes", "About 2 hours", "Up to 48 hours", "About a week"], 2,
          "MPS can stay elevated for up to 48 hours as your body remodels and repairs the trained muscle.",
          "protein-for-muscle-growth.html", "Protein for muscle growth"),
        q("Which of these is a naturally \"complete\" plant protein?",
          ["White rice", "Quinoa", "Kidney beans alone", "Wheat bread"], 1,
          "Quinoa (along with soy and buckwheat) is a rare plant food that supplies all 9 essential amino acids on its own.",
          "complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"),
        q("Severe, prolonged protein deficiency is called:",
          ["Ketosis", "Kwashiorkor", "Sarcopenia", "Rhabdomyolysis"], 1,
          "Kwashiorkor causes swelling, a swollen liver, and impaired growth — most seen in regions with significant food insecurity.",
          "protein-deficiency-symptoms.html", "Signs of protein deficiency"),
        q("About how much protein does 100g of cooked chicken breast provide?",
          ["~10 g", "~20 g", "~31 g", "~50 g"], 2,
          "Chicken breast is roughly 31g of protein per 100g cooked — one of the most protein-dense common foods.",
          "high-protein-foods-list.html", "High-protein foods list"),
        q("The \"anabolic window\" myth claims you must eat protein within:",
          ["24 hours of training", "30-60 minutes post-workout", "One week of training", "It doesn't matter at all"], 1,
          "Since MPS stays elevated for up to 48 hours, the strict 30-60 minute \"window\" is largely overstated.",
          "protein-timing.html", "Does protein timing matter?"),
        q("How many amino acids are considered \"essential\" (must come from food)?",
          ["5", "9", "12", "20"], 1,
          "9 of the 20 amino acids are essential — your body can't synthesize them on its own.",
          "complete-vs-incomplete-protein.html", "Complete vs. incomplete protein"),
        q("For muscle building, sports nutrition research (ISSN) suggests protein intake around:",
          ["0.5-0.8 g/kg", "1.4-2.0 g/kg", "3.0-4.0 g/kg", "It doesn't matter"], 1,
          "1.4-2.0 g/kg/day maximizes muscle protein balance for most people who train regularly.",
          "protein.html", "What protein actually does"),
    ],
)

add(
    "fat-quiz", "Fat Quiz: Test Your Knowledge",
    "An 8-question quiz testing what you know about dietary fat, hormones, and essential fatty acids.",
    "fat", "Fat Quiz", "How much do you really know about dietary fat?",
    "8 questions, straight from the articles on this site.",
    [
        q("How many calories are in one gram of fat?",
          ["4", "7", "9", "11"], 2,
          "Fat provides 9 calories per gram — more than double protein or carbs (4 each).",
          "fats.html", "What fat actually does"),
        q("The recommended range (AMDR) for fat intake is:",
          ["5-15% of calories", "20-35% of calories", "40-50% of calories", "60-70% of calories"], 1,
          "20-35% of total calories is the Acceptable Macronutrient Distribution Range for fat.",
          "how-much-fat-per-day.html", "How much fat per day"),
        q("Steroid hormones like testosterone and estrogen are synthesized from:",
          ["Glucose", "Cholesterol", "Amino acids", "Fiber"], 1,
          "Cholesterol, partly from diet and partly made by your body using fat as a building block, is the raw material for steroid hormones.",
          "low-fat-diet-risks.html", "Risks of very low-fat diets"),
        q("Which vitamins require dietary fat for proper absorption?",
          ["B vitamins and C", "Vitamins A, D, E, and K", "Only vitamin C", "None — all vitamins absorb the same way"], 1,
          "Vitamins A, D, E, and K are fat-soluble and need dietary fat to be absorbed and transported.",
          "fats.html", "What fat actually does"),
        q("Which fat type stays liquid at room temperature due to double bonds in its structure?",
          ["Saturated fat", "Unsaturated fat", "Trans fat", "All fats behave the same"], 1,
          "Double bonds kink the fat molecule's chain, keeping unsaturated fats like olive oil liquid at room temperature.",
          "saturated-vs-unsaturated-fat.html", "Saturated vs. unsaturated fat"),
        q("Most modern diets tend to have an imbalance of:",
          ["Too much omega-3, too little omega-6", "Too much omega-6, too little omega-3", "Equal omega-3 and omega-6", "No omega fats at all"], 1,
          "Vegetable oils used widely in processed food are rich in omega-6, while omega-3 sources are less common in the typical diet.",
          "omega-3-vs-omega-6.html", "Omega-3 vs. omega-6"),
        q("Artificial trans fat is mainly created through:",
          ["Freezing", "Partial hydrogenation", "Fermentation", "Pasteurization"], 1,
          "Partial hydrogenation pumps hydrogen into liquid oil to make it more solid and shelf-stable, changing its molecular shape.",
          "trans-fat-explained.html", "What is trans fat?"),
        q("Roughly how much fat is in one tablespoon of olive oil?",
          ["~2 g", "~7 g", "~14 g", "~25 g"], 2,
          "A tablespoon of olive oil is essentially pure fat — about 14 grams.",
          "healthy-high-fat-foods.html", "Healthy high-fat foods"),
    ],
)

add(
    "carbs-quiz", "Carbs Quiz: Test Your Knowledge",
    "An 8-question quiz testing what you know about carbohydrates, glycogen, and fiber.",
    "carbs", "Carbs Quiz", "How much do you really know about carbohydrates?",
    "8 questions, straight from the articles on this site.",
    [
        q("Carbohydrates are broken down during digestion mainly into:",
          ["Amino acids", "Fatty acids", "Glucose", "Cholesterol"], 2,
          "Most carbs become glucose, which cells throughout your body use directly for energy.",
          "carbs.html", "What carbohydrates actually do"),
        q("Glycogen is mainly stored in:",
          ["Skin and hair", "Muscle and liver", "Blood plasma", "Bone marrow"], 1,
          "Muscle glycogen fuels the muscle it's stored in; liver glycogen keeps blood sugar stable, including for the brain.",
          "what-is-glycogen.html", "What is glycogen?"),
        q("The recommended range (AMDR) for carbohydrate intake is:",
          ["10-20% of calories", "45-65% of calories", "70-90% of calories", "There is no recommended range"], 1,
          "45-65% of total calories is the Acceptable Macronutrient Distribution Range for carbohydrates.",
          "how-many-carbs-per-day.html", "How many carbs per day"),
        q("\"Keto flu\" symptoms are mainly caused by:",
          ["Eating too much sugar", "Rapid glycogen depletion during low-carb adaptation", "Eating too much fiber", "Drinking too much water"], 1,
          "As glycogen empties out and your body adapts to burning fat and ketones, fatigue and headaches are common early on.",
          "low-carb-diet-effects.html", "What happens on a low-carb diet"),
        q("Which tissue relies on glucose as its primary, obligate fuel source?",
          ["Skeletal muscle", "The brain", "The liver", "Skin"], 1,
          "The brain can't efficiently use circulating fat for energy, making it heavily dependent on a steady glucose supply.",
          "carbs.html", "What carbohydrates actually do"),
        q("Fiber is a type of carbohydrate that:",
          ["Digests faster than sugar", "Your body can't fully digest", "Contains 9 calories per gram", "Is only found in meat"], 1,
          "Fiber passes through digestion largely intact, adding bulk and feeding beneficial gut bacteria along the way.",
          "fiber-benefits.html", "Why fiber matters"),
        q("\"Carb loading\" before an endurance event typically means eating roughly:",
          ["1-2 g/kg of carbs", "8-12 g/kg of carbs", "20-30 g/kg of carbs", "No carbs at all"], 1,
          "8-12 g/kg per day for 1-3 days beforehand is the modern carb-loading approach to maximize glycogen stores.",
          "carb-loading-for-athletes.html", "Carb loading for athletes"),
        q("Complex carbohydrates are made of:",
          ["A single sugar molecule", "Two linked sugar molecules", "Long chains of sugar molecules", "No sugar at all"], 2,
          "Polysaccharides — long chains of sugar units — take longer to digest than simple sugars, generally producing a slower blood sugar rise.",
          "simple-vs-complex-carbs.html", "Simple vs. complex carbs"),
    ],
)

add(
    "macro-master-quiz", "Macro Master Quiz: The Hardest One",
    "A 10-question mixed quiz covering protein, fat, carbs, and calculator concepts — for people who've read most of the site.",
    "general", "Master Quiz", "The Macro Master Quiz",
    "10 mixed, harder questions pulling from every corner of the site. Good luck.",
    [
        q("Which macronutrient provides the most calories per gram?",
          ["Protein", "Fat", "Carbohydrates", "They're all equal"], 1,
          "Fat provides 9 calories per gram, versus 4 for protein and carbs.",
          "fats.html", "What fat actually does"),
        q("BMR measures:",
          ["Calories burned during exercise", "Calories burned at complete rest", "Calories from digestion only", "Total daily calories including activity"], 1,
          "Basal Metabolic Rate is what your body burns just to stay alive at complete rest — TDEE adds activity on top.",
          "tdee-vs-bmr.html", "BMR vs. TDEE"),
        q("The Mifflin-St Jeor equation estimates:",
          ["Body fat percentage", "Basal Metabolic Rate", "VO2 max", "Glycogen storage capacity"], 1,
          "It's a widely used, research-validated formula for estimating BMR from weight, height, age, and sex.",
          "tdee-vs-bmr.html", "BMR vs. TDEE"),
        q("During a fat-loss phase, sports nutrition guidance suggests you should generally:",
          ["Lower protein intake", "Raise protein intake", "Eliminate carbs completely", "Eliminate fat completely"], 1,
          "Higher protein (around 1.8 g/kg) helps preserve muscle while you're in a calorie deficit.",
          "macros-for-weight-loss.html", "Macros for fat loss"),
        q("Roughly how much water does each gram of stored glycogen hold alongside it?",
          ["None at all", "~1 gram", "~3 grams", "~10 grams"], 2,
          "That's why cutting carbs sharply causes a fast multi-pound drop that's mostly water, not fat.",
          "water-weight-vs-fat-loss.html", "Water weight vs. fat loss"),
        q("IIFYM stands for:",
          ["\"It Is Fine, You're Missing it\"", "\"If It Fits Your Macros\"", "\"Improve If Following Your Meals\"", "It's not a real acronym"], 1,
          "IIFYM is the idea that as long as you hit your macro targets, specific food choices are flexible.",
          "iifym-flexible-dieting.html", "IIFYM explained"),
        q("Alcohol provides roughly how many calories per gram?",
          ["0", "4", "7", "9"], 2,
          "Alcohol provides about 7 calories per gram — between carbs/protein (4) and fat (9) — despite not being a macronutrient.",
          "alcohol-and-macros.html", "Alcohol and macros"),
        q("A standard ketogenic diet typically limits carbs to roughly:",
          ["Under 50g/day", "100-150g/day", "200-250g/day", "300g/day or more"], 0,
          "Standard keto usually keeps carbs under about 50g/day to maintain ketosis.",
          "ketogenic-diet-explained.html", "The ketogenic diet explained"),
        q("Body recomposition (building muscle and losing fat at once) works best for:",
          ["Advanced lifters only", "Beginners, or people returning after a break", "Only endurance athletes", "It never actually works"], 1,
          "New lifters and people regaining lost muscle have a rare window where both can happen simultaneously.",
          "body-recomposition-explained.html", "Body recomposition explained"),
        q("Which of these is NOT one of the three macronutrients?",
          ["Protein", "Fiber", "Fat", "Carbohydrate"], 1,
          "Fiber is a subtype of carbohydrate, not a fourth macronutrient — protein, fat, and carbs are the three.",
          "micronutrients-vs-macronutrients.html", "Micronutrients vs. macronutrients"),
    ],
    tiers=[
        {"min": 90, "msg": "Macro Master — you could write these articles yourself."},
        {"min": 70, "msg": "Very strong. A couple of edge cases tripped you up."},
        {"min": 40, "msg": "Decent foundation — worth another lap through the site."},
        {"min": 0, "msg": "Tough quiz on purpose. Start with the pillar pages and come back."},
    ],
)

add(
    "athlete-diets-quiz", "Athlete Diets Quiz: Fact or Fiction?",
    "An 8-question quiz on real athlete and World Cup team nutrition stories — Messi, Ronaldo, Phelps, Bolt, Djokovic, Biles, and more, fact-checked.",
    "athletes", "Athletes Quiz", "Athlete diets: fact or fiction?",
    "8 questions on real, sourced athlete and team nutrition stories — see how many myths you can spot.",
    [
        q("Roughly how much food did Norway's team fly in from home for the 2026 World Cup?",
          ["About 10 kg", "About 100 kg", "Over 1,000 kg", "It was all sourced locally"], 2,
          "Norway transported over 1,000kg of food, including salmon, white fish, brunost cheese, and about 6,000 oranges.",
          "world-cup-2026-team-nutrition.html", "What World Cup 2026 teams are actually eating"),
        q("What did Argentina bring roughly 500kg of to the 2026 World Cup?",
          ["Beef", "Pasta", "Olive oil", "Mate tea"], 0,
          "Argentina brought nearly 500kg of beef, prepared in part for the team's traditional post-win asado.",
          "world-cup-2026-team-nutrition.html", "What World Cup 2026 teams are actually eating"),
        q("Did Michael Phelps really eat 12,000 calories a day, as widely reported?",
          ["Yes, confirmed by his coach", "No — it was closer to 8,000-10,000 on his heaviest days", "No, he ate a normal 2,500 calories", "The claim was about a different swimmer"], 1,
          "The 12,000-calorie figure came from exaggerated reporter math; Phelps himself said the real number was 8,000-10,000 on intense days.",
          "famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"),
        q("What did Usain Bolt reportedly eat almost exclusively during the 2008 Beijing Olympics?",
          ["Rice and fish", "Chicken nuggets", "Protein shakes only", "Local Chinese cuisine"], 1,
          "Bolt ate roughly 100 McDonald's chicken nuggets a day for 10 days after a local meal upset his stomach — and still broke 3 world records.",
          "famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"),
        q("What kind of diet does Novak Djokovic follow?",
          ["High-carb, dairy-heavy", "Gluten-free and plant-based", "Ketogenic", "Carnivore"], 1,
          "Djokovic went gluten-free in 2010 and later moved to a fully plant-based diet.",
          "famous-athlete-diets-fact-checked.html", "6 famous athlete diets, fact-checked"),
        q("What does controlled research find when non-celiac athletes try a gluten-free diet?",
          ["Large performance gains", "No measurable performance change", "Immediate weight gain", "Increased injury risk"], 1,
          "Controlled trials find no measurable difference in performance or GI symptoms in non-celiac athletes on a gluten-free diet.",
          "do-elimination-diets-improve-performance.html", "Do elimination diets improve performance?"),
        q("According to research, what actually explains the old \"30-minute anabolic window\" studies?",
          ["The window is real and exact", "Groups eating sooner also ate more total protein per day", "Muscle stops growing after 10 minutes", "It only applies to beginners"], 1,
          "A meta-analysis found the timing groups simply ate ~25% more total daily protein — once matched, the timing effect disappeared.",
          "post-workout-anabolic-window.html", "The post-workout anabolic window"),
        q("Per ACSM guidance, when do carbohydrate-electrolyte sports drinks start to help more than plain water?",
          ["Any workout, even 10 minutes", "Past about 60-90 minutes of exercise", "Only during weightlifting", "Never — water is always enough"], 1,
          "Under about an hour, plain water is enough for most people; past 60-90 minutes, a carb-electrolyte drink helps maintain performance.",
          "sports-drinks-vs-water.html", "Sports drinks vs. water"),
    ],
)

add(
    "diets-quiz", "Diets Quiz: Animal-Based, Vegan, Paleo & More",
    "An 8-question quiz testing what you know about animal-based, plant-based, vegan, paleo, carnivore, vegetarian, and pescatarian diets.",
    "diets", "Diets Quiz", "How well do you know the major diets?",
    "8 questions on what each major diet actually restricts — and what the evidence says about each one.",
    [
        q("What's the key difference between a vegan diet and a plant-based diet?",
          ["They're identical", "Vegan excludes all animal products; plant-based just emphasizes plants", "Plant-based excludes more foods than vegan", "Plant-based always includes meat"], 1,
          "Vegan is a strict zero-animal-product rule. Plant-based is a spectrum — mostly plants, but not necessarily zero animal products.",
          "plant-based-vs-vegan-diet.html", "Plant-based vs. vegan: what's actually the difference?"),
        q("What foods does an animal-based diet typically still allow, unlike strict carnivore?",
          ["Grains and legumes", "Fruit and honey", "Refined sugar", "Nothing — they're the same diet"], 1,
          "Animal-based diets allow some low-\"antinutrient\" plant foods like fruit and honey, unlike strict carnivore, which excludes all plant foods.",
          "animal-based-diet-explained.html", "The animal-based diet explained"),
        q("What is the paleo diet's typical macronutrient split?",
          ["Very high carb, low protein", "High protein, moderate fat, relatively low carb", "Zero fat", "Identical to a standard diet"], 1,
          "Paleo typically runs 19-35% protein, 28-58% fat, and 22-40% carbohydrate — higher protein and lower carb than a standard diet.",
          "paleo-diet-explained.html", "The paleo diet explained"),
        q("What nutrient deficiencies do clinicians most often flag with long-term carnivore diets?",
          ["Protein and fat", "Vitamin C, magnesium, and calcium", "Sodium only", "None — carnivore has no risks"], 1,
          "Removing all plant foods removes common sources of vitamin C, magnesium, and calcium, which clinicians flag as a real long-term risk.",
          "carnivore-diet-explained.html", "The carnivore diet explained"),
        q("What does a vegetarian diet typically still include that makes protein easier than vegan?",
          ["Meat", "Eggs and dairy", "Fish", "Nothing — it's identical to vegan"], 1,
          "Vegetarian excludes meat, poultry, and fish, but usually keeps eggs and dairy — both complete proteins.",
          "macros-for-vegetarians.html", "Macros for vegetarians"),
        q("A pescatarian diet is often described as:",
          ["Vegan plus dairy", "Vegetarian plus fish", "Carnivore plus vegetables", "Paleo plus grains"], 1,
          "Pescatarian excludes meat and poultry but includes fish and seafood alongside eggs, dairy, and plant foods.",
          "pescatarian-diet-explained.html", "The pescatarian diet explained"),
        q("Regular seafood intake (about 8oz/week) is linked to roughly how much lower risk of cardiovascular death, per one widely cited analysis?",
          ["No measurable difference", "~10%", "~36%", "~90%"], 2,
          "One widely cited analysis found roughly a 36% lower risk of death from heart disease associated with eating about 8oz of seafood per week.",
          "pescatarian-diet-explained.html", "The pescatarian diet explained"),
        q("Across paleo, carnivore, vegan, and every other diet, what does the evidence say matters most for health outcomes?",
          ["The specific diet label you use", "Total calories, protein adequacy, and overall diet quality", "Eating only foods from before 10,000 BC", "Avoiding all carbohydrates"], 1,
          "No diet pattern is universally optimal — total calories, protein adequacy, and whole-food quality matter more than which specific label you follow.",
          "diets-explained.html", "Diets explained: every major pattern"),
    ],
)


def page(slug, title, meta, category, eyebrow, h1, intro, questions, moreHref, tiers=None):
    hero_class = "hero page-hero" if category != "general" else "page-hero"
    tiers_js = ("tiers: " + json.dumps(tiers) + ",\n        ") if tiers else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
{seo_meta(title, meta, f"https://getmacros.net/{slug}.html", category=category)}
{article_jsonld(title, meta, f"https://getmacros.net/{slug}.html", kind="Quiz", category=category)}
{breadcrumb_jsonld(title, f"https://getmacros.net/{slug}.html", hub_name="Quiz", hub_url="https://getmacros.net/quiz.html")}
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{nav_html("quiz")}

<main>
  <section class="{hero_class}" style="{HERO_STYLE[category]}">
    <div class="container">
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p>{intro}</p>
    </div>
  </section>

  <section>
    <div class="container">
      <div id="quiz-root" style="max-width:640px;margin:0 auto;"></div>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js"></script>
<script src="js/confetti.js"></script>
<script src="js/quiz.js"></script>
<script>
  renderQuiz('quiz-root', {json.dumps(questions)}, {{
    title: {json.dumps(title.split(":")[0])},
    {tiers_js}moreHref: 'quiz.html'
  }});
</script>
<script src="js/ads-config.js"></script>
<script src="js/ads.js"></script>
</body>
</html>
'''


def main():
    for qz in QUIZZES:
        html = page(qz["slug"], qz["title"], qz["meta"], qz["category"], qz["eyebrow"],
                    qz["h1"], qz["intro"], qz["questions"], "quiz.html", qz["tiers"])
        path = os.path.join(ROOT, f'{qz["slug"]}.html')
        with open(path, "w") as f:
            f.write(html)
        print("wrote", path)
    print(f"\n{len(QUIZZES)} quizzes generated.")
    return QUIZZES


if __name__ == "__main__":
    main()
