#!/usr/bin/env python3
"""Generates the quiz pages for GetMacros.net. Run: python3 tools/generate_quizzes.py"""
import json
from html import escape as esc_html
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_articles import ROOT, nav_html, FOOTER, HERO_STYLE, ICON_SPRITE, ADSENSE_LOADER, AD_SLOT, seo_meta, article_jsonld, breadcrumb_jsonld, AUTHOR_NAME, ASSET_VERSION  # noqa: E402

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


add(
    "biochemistry-quiz", "Biochemistry Quiz: Metabolism Revision",
    "A 10-question revision quiz on glycolysis, the Krebs cycle, the electron transport chain, and ATP yields.",
    "science", "Biochemistry Quiz", "Metabolism revision quiz",
    "10 questions on the core energy pathways — the ones exams keep coming back to.",
    [
        q("What is the NET ATP yield of glycolysis per glucose molecule?",
          ["1 ATP", "2 ATP", "4 ATP", "38 ATP"], 1,
          "Glycolysis produces 4 ATP gross but spends 2 in the investment phase, giving a net yield of 2 ATP, plus 2 NADH and 2 pyruvate.",
          "glycolysis-explained.html", "Glycolysis explained"),
        q("Which enzyme is the rate-limiting step of glycolysis?",
          ["Hexokinase", "Phosphofructokinase-1", "Pyruvate kinase", "Aldolase"], 1,
          "PFK-1 is the rate-limiting enzyme. Hexokinase catalyses the first step, which is not the same as being rate-limiting.",
          "glycolysis-explained.html", "Glycolysis explained"),
        q("Where in the cell does the Krebs cycle take place?",
          ["Cytosol", "Mitochondrial matrix", "Inner mitochondrial membrane", "Nucleus"], 1,
          "The Krebs cycle runs in the mitochondrial matrix. Glycolysis is in the cytosol; the electron transport chain is in the inner membrane.",
          "krebs-cycle-explained.html", "The Krebs cycle explained"),
        q("How many NADH are produced per single turn of the Krebs cycle?",
          ["1", "2", "3", "6"], 2,
          "Each turn yields 3 NADH, 1 FADH2, 1 GTP and 2 CO2. One glucose drives two turns, so doubles those figures.",
          "krebs-cycle-explained.html", "The Krebs cycle explained"),
        q("Why does FADH2 generate less ATP than NADH?",
          ["It carries fewer electrons", "It enters at complex II, bypassing complex I", "It is used in the cytosol", "It cannot reach ATP synthase"], 1,
          "FADH2 donates electrons at complex II, skipping complex I's proton pumping, so it contributes less to the gradient — roughly 1.5 ATP vs 2.5.",
          "electron-transport-chain-explained.html", "The electron transport chain"),
        q("What is the final electron acceptor in the electron transport chain?",
          ["NAD+", "Carbon dioxide", "Oxygen", "Pyruvate"], 2,
          "Oxygen accepts electrons at complex IV, forming water. Without it electrons back up and the whole chain — and the Krebs cycle — stalls.",
          "electron-transport-chain-explained.html", "The electron transport chain"),
        q("Under modern estimates, roughly how much ATP does one glucose molecule yield aerobically?",
          ["2 ATP", "12-15 ATP", "30-32 ATP", "100+ ATP"], 2,
          "Around 30-32 ATP. The older 36-38 figure was revised down once the cost of shuttling cytosolic NADH into the mitochondrion was accounted for.",
          "electron-transport-chain-explained.html", "The electron transport chain"),
        q("In beta-oxidation, what is the correct order of the four repeating steps?",
          ["Hydrate, oxidise, cleave, oxidise", "Oxidise, hydrate, oxidise, thiolysis", "Cleave, oxidise, hydrate, oxidise", "Oxidise, oxidise, hydrate, cleave"], 1,
          "Oxidise (FADH2), hydrate, oxidise (NADH), then thiolysis cleaves off acetyl-CoA. Mnemonic: oxidise, hydrate, oxidise, cleave.",
          "beta-oxidation-explained.html", "Beta-oxidation explained"),
        q("Which B vitamin forms the coenzyme NAD+?",
          ["B1 (thiamine)", "B2 (riboflavin)", "B3 (niacin)", "B6 (pyridoxine)"], 2,
          "Niacin (B3) forms NAD+ and NADP+. Riboflavin (B2) forms FAD and FMN — a pair frequently swapped in exams.",
          "b-vitamins-and-metabolism.html", "B vitamins as coenzymes"),
        q("What is the rate-limiting step of fatty acid oxidation?",
          ["Thiolysis", "CPT-1 (the carnitine shuttle)", "Citrate synthase", "ATP synthase"], 1,
          "CPT-1 transfers long-chain fatty acyl-CoA onto carnitine for mitochondrial entry, and is inhibited by malonyl-CoA when fat synthesis is active.",
          "beta-oxidation-explained.html", "Beta-oxidation explained"),
    ],
)

add(
    "physiology-quiz", "Physiology Quiz: Homeostasis and Organs",
    "A 10-question revision quiz on homeostasis, hormones, kidney function, and muscle contraction.",
    "science", "Physiology Quiz", "Physiology revision quiz",
    "10 questions on feedback loops, hormones, the nephron, and how muscle actually contracts.",
    [
        q("In a negative feedback loop, the response to a stimulus:",
          ["Amplifies the stimulus", "Opposes the stimulus", "Has no effect", "Permanently changes the set point"], 1,
          "Negative feedback opposes the original change, returning the variable toward its set point. Positive feedback amplifies it instead.",
          "homeostasis-explained.html", "Homeostasis explained"),
        q("Which of these is an example of POSITIVE feedback?",
          ["Sweating when hot", "Insulin release after a meal", "Oxytocin during childbirth", "Vasoconstriction when cold"], 2,
          "Oxytocin strengthens contractions, which triggers more oxytocin — an amplifying loop. The others all oppose their stimulus.",
          "homeostasis-explained.html", "Homeostasis explained"),
        q("Which pancreatic cells secrete insulin?",
          ["Alpha cells", "Beta cells", "Delta cells", "Acinar cells"], 1,
          "Beta cells secrete insulin when blood glucose is high; alpha cells secrete glucagon when it is low.",
          "insulin-and-glucagon.html", "Insulin and glucagon"),
        q("Why can't muscle glycogen raise blood glucose for the rest of the body?",
          ["Muscle stores too little", "Muscle lacks glucose-6-phosphatase", "Muscle glycogen is a different molecule", "It can — this is a myth"], 1,
          "Without glucose-6-phosphatase, muscle cannot release free glucose into the blood. Only the liver can do that.",
          "insulin-and-glucagon.html", "Insulin and glucagon"),
        q("Roughly what percentage of kidney filtrate is reabsorbed?",
          ["About 25%", "About 50%", "About 75%", "Over 99%"], 3,
          "Around 180 litres are filtered daily but only 1-2 litres leave as urine — over 99% is reabsorbed.",
          "kidney-function-explained.html", "Kidney function explained"),
        q("What does ADH (vasopressin) do?",
          ["Increases sodium reabsorption", "Increases water reabsorption in the collecting duct", "Increases filtration rate", "Triggers glucose reabsorption"], 1,
          "ADH inserts aquaporins into the collecting duct, increasing water reabsorption and concentrating urine. Aldosterone is the sodium hormone.",
          "kidney-function-explained.html", "Kidney function explained"),
        q("During muscle contraction, which sarcomere band does NOT change length?",
          ["I band", "H zone", "A band", "All of them shorten"], 2,
          "The A band matches the full myosin filament length, and myosin doesn't shorten — actin just slides further over it. The I band and H zone shorten.",
          "muscle-contraction-explained.html", "Muscle contraction explained"),
        q("What is the direct role of calcium in muscle contraction?",
          ["It powers the power stroke", "It binds troponin, moving tropomyosin off actin", "It detaches myosin from actin", "It re-cocks the myosin head"], 1,
          "Calcium binds troponin, shifting tropomyosin away from the myosin-binding sites. ATP handles detachment and re-cocking.",
          "muscle-contraction-explained.html", "Muscle contraction explained"),
        q("Why does rigor mortis occur after death?",
          ["Calcium is depleted", "No ATP is available to detach myosin from actin", "Muscles denature immediately", "Lactic acid accumulates"], 1,
          "ATP binding is what causes myosin to release actin. With no ATP after death, cross-bridges stay attached and the muscle locks.",
          "muscle-contraction-explained.html", "Muscle contraction explained"),
        q("Which energy system dominates during a maximal 8-second sprint?",
          ["Oxidative", "Glycolytic", "Phosphagen (ATP-PC)", "Beta-oxidation"], 2,
          "The phosphagen system uses stored ATP and creatine phosphate for the highest power output, sustainable for roughly 10 seconds.",
          "energy-systems-explained.html", "The three energy systems"),
    ],
)

add(
    "cell-biology-quiz", "Cell Biology Quiz: Transport and Enzymes",
    "A 10-question revision quiz on membrane transport, osmosis, enzyme function, and protein structure.",
    "science", "Cell Biology Quiz", "Cell biology revision quiz",
    "10 questions on how things cross membranes and how enzymes and proteins are built.",
    [
        q("Is facilitated diffusion active or passive transport?",
          ["Active — it uses a protein", "Passive — it needs no ATP", "Active — it moves against gradients", "Neither"], 1,
          "It's passive. Using a transport protein doesn't make it active; moving against a gradient using energy does.",
          "cell-membrane-transport.html", "Cell membrane transport"),
        q("The sodium-potassium pump moves which ions, per ATP?",
          ["2 Na+ out, 3 K+ in", "3 Na+ out, 2 K+ in", "3 Na+ in, 3 K+ out", "1 Na+ out, 1 K+ in"], 1,
          "Three sodium ions out, two potassium in, per ATP — primary active transport against both gradients.",
          "cell-membrane-transport.html", "Cell membrane transport"),
        q("An animal cell placed in a hypotonic solution will:",
          ["Shrink", "Swell and possibly burst", "Stay the same", "Become hypertonic"], 1,
          "Solute is lower outside, so water moves in. The cell swells and may lyse — which is why IV fluids must be isotonic.",
          "cell-membrane-transport.html", "Cell membrane transport"),
        q("How do enzymes speed up reactions?",
          ["They raise the temperature", "They lower activation energy", "They shift the equilibrium position", "They add energy to reactants"], 1,
          "Enzymes lower activation energy. They don't change the equilibrium or the overall free energy change — only how fast equilibrium is reached.",
          "enzymes-explained.html", "Enzymes explained"),
        q("A competitive inhibitor has what effect on Km and Vmax?",
          ["Km increases, Vmax unchanged", "Km unchanged, Vmax decreases", "Both increase", "Both decrease"], 0,
          "Competitive inhibitors can be outcompeted with more substrate, so Vmax is still reachable — but it takes more substrate, raising Km.",
          "enzyme-kinetics-explained.html", "Enzyme kinetics explained"),
        q("A LOW Km value indicates:",
          ["Low affinity for substrate", "High affinity for substrate", "A fast enzyme", "A denatured enzyme"], 1,
          "Km is the substrate concentration giving half Vmax. A low Km means little substrate is needed — high affinity. The inversion catches people out.",
          "enzyme-kinetics-explained.html", "Enzyme kinetics explained"),
        q("Which bonds hold the PRIMARY structure of a protein together?",
          ["Hydrogen bonds", "Peptide bonds", "Disulfide bridges", "Ionic bonds"], 1,
          "Primary structure is the amino acid sequence, linked by covalent peptide bonds. Hydrogen bonds hold secondary structure.",
          "protein-structure-levels.html", "Levels of protein structure"),
        q("What survives denaturation of a protein?",
          ["Quaternary structure", "Tertiary structure", "Primary structure", "Nothing"], 2,
          "Denaturation breaks the weak interactions holding higher-order structure, but peptide bonds are covalent — the sequence survives.",
          "protein-structure-levels.html", "Levels of protein structure"),
        q("Coenzymes are most often derived from:",
          ["Minerals", "B vitamins", "Fatty acids", "Nucleic acids"], 1,
          "NAD+ from niacin, FAD from riboflavin, coenzyme A from pantothenic acid — which is why B-vitamin deficiencies have such broad effects.",
          "b-vitamins-and-metabolism.html", "B vitamins as coenzymes"),
        q("Which protein does NOT have quaternary structure?",
          ["Haemoglobin", "Myoglobin", "Antibodies", "Collagen"], 1,
          "Myoglobin is a single polypeptide, so it has no quaternary structure. Haemoglobin's four subunits give it quaternary structure.",
          "protein-structure-levels.html", "Levels of protein structure"),
    ],
)

add(
    "digestion-quiz", "Digestion Quiz: Enzymes and Absorption",
    "A 10-question revision quiz on digestive anatomy, enzymes, absorption sites, and accessory organs.",
    "science", "Digestion Quiz", "Digestion revision quiz",
    "10 questions on which enzyme does what, and where each nutrient is actually absorbed.",
    [
        q("Where does carbohydrate digestion begin?",
          ["Stomach", "Mouth", "Small intestine", "Large intestine"], 1,
          "Salivary amylase begins starch digestion in the mouth. It's then inactivated by stomach acid and resumes via pancreatic amylase.",
          "how-digestion-works.html", "How digestion works"),
        q("Which enzyme begins protein digestion in the stomach?",
          ["Amylase", "Pepsin", "Lipase", "Trypsin"], 1,
          "Pepsin, activated from pepsinogen by stomach acid, starts protein digestion. Trypsin acts later, in the small intestine.",
          "how-digestion-works.html", "How digestion works"),
        q("What is the main role of bile?",
          ["Digesting protein", "Emulsifying fat", "Breaking down starch", "Neutralising enzymes"], 1,
          "Bile emulsifies fat into smaller droplets, increasing surface area for lipase. It's a detergent, not an enzyme — it doesn't chemically digest fat.",
          "how-digestion-works.html", "How digestion works"),
        q("Where is bile produced and where is it stored?",
          ["Produced in gallbladder, stored in liver", "Produced in liver, stored in gallbladder", "Both in the pancreas", "Both in the liver"], 1,
          "The liver produces bile; the gallbladder concentrates and stores it, releasing it when fat enters the small intestine.",
          "how-digestion-works.html", "How digestion works"),
        q("Most nutrient absorption occurs in the:",
          ["Stomach", "Small intestine", "Large intestine", "Oesophagus"], 1,
          "The small intestine, whose villi and microvilli give it an enormous surface area. The large intestine mainly reclaims water and electrolytes.",
          "how-digestion-works.html", "How digestion works"),
        q("Glucose absorption from the intestine uses which mechanism?",
          ["Simple diffusion", "Secondary active transport with sodium", "Osmosis", "Endocytosis"], 1,
          "SGLT1 co-transports glucose with sodium, riding the gradient built by the sodium-potassium pump — secondary active transport.",
          "cell-membrane-transport.html", "Cell membrane transport"),
        q("What does stomach acid do to dietary protein before enzymes act?",
          ["Breaks peptide bonds", "Denatures it, unfolding the structure", "Converts it to glucose", "Nothing"], 1,
          "Acid denatures protein, unfolding it so proteases can reach the peptide bonds. The primary structure stays intact until enzymes act.",
          "protein-structure-levels.html", "Levels of protein structure"),
        q("Which nutrient is fermented by bacteria in the large intestine?",
          ["Protein", "Fat", "Fiber", "Simple sugars"], 2,
          "Gut bacteria ferment fermentable fiber into short-chain fatty acids like butyrate, the preferred fuel of colon cells.",
          "fiber-and-gut-microbiome.html", "Fiber and your gut microbiome"),
        q("Which organ produces the enzymes amylase, lipase, and trypsin?",
          ["Liver", "Pancreas", "Gallbladder", "Stomach"], 1,
          "The pancreas secretes these into the small intestine, along with bicarbonate to neutralise stomach acid.",
          "how-digestion-works.html", "How digestion works"),
        q("Fat slows digestion of a meal because it:",
          ["Is absorbed in the stomach", "Delays gastric emptying", "Blocks enzymes", "Requires no bile"], 1,
          "Fat slows gastric emptying, which is why mixed meals containing fat produce a more gradual, sustained release of energy.",
          "how-digestion-works.html", "How digestion works"),
    ],
)

add(
    "exercise-physiology-quiz", "Exercise Physiology Quiz: Energy and Fuel",
    "A 10-question revision quiz on energy systems, fuel use, lactate, VO2 max concepts, and training adaptations.",
    "science", "Exercise Physiology Quiz", "Exercise physiology revision quiz",
    "10 questions on how the body fuels movement — and the myths that keep appearing in textbooks.",
    [
        q("Which energy system has the HIGHEST power output but shortest duration?",
          ["Oxidative", "Glycolytic", "Phosphagen (ATP-PC)", "Beta-oxidation"], 2,
          "The phosphagen system regenerates ATP almost instantly from creatine phosphate — highest power, but exhausted in roughly 10 seconds.",
          "energy-systems-explained.html", "The three energy systems"),
        q("Does lactate cause delayed-onset muscle soreness (DOMS)?",
          ["Yes, it's the main cause", "No — lactate clears within about an hour", "Only in untrained people", "Only during eccentric work"], 1,
          "Lactate clears within about an hour; DOMS peaks 24-48 hours later. DOMS is linked to mechanical damage and inflammation.",
          "energy-systems-explained.html", "The three energy systems"),
        q("Why can't fat fuel maximal-intensity sprinting?",
          ["Fat contains no energy", "Oxidising fat needs more oxygen per ATP and more steps", "Fat can't enter mitochondria", "It can — carbs are irrelevant"], 1,
          "Fat is energy-dense but slow to oxidise, requiring more oxygen per unit ATP. It can't supply ATP fast enough for maximal effort.",
          "energy-systems-explained.html", "The three energy systems"),
        q("Which muscle fibre type is most reliant on oxidative metabolism?",
          ["Type I (slow-twitch)", "Type IIa", "Type IIx (fast-twitch)", "All equally"], 0,
          "Type I fibres are fatigue-resistant and rely heavily on oxidative metabolism, with more mitochondria and capillaries.",
          "muscle-fiber-types-and-nutrition.html", "Muscle fibre types"),
        q("At roughly what level of fluid loss does endurance performance start to decline measurably?",
          ["0.5% of body mass", "2% of body mass", "8% of body mass", "It never does"], 1,
          "Meaningful decrements generally appear beyond about 2% of body mass — roughly 1.5 kg for a 75 kg athlete.",
          "hydration-and-performance.html", "Hydration and performance"),
        q("What dose of caffeine does the ISSN position stand associate with improved performance?",
          ["0.5-1 mg/kg", "3-6 mg/kg", "10-15 mg/kg", "Any dose works equally"], 1,
          "3-6 mg/kg about 60 minutes before exercise. Higher doses don't reliably help further and increase side effects.",
          "caffeine-and-athletic-performance.html", "Caffeine and performance"),
        q("Carb loading works primarily by:",
          ["Increasing muscle mass", "Maximising muscle and liver glycogen stores", "Raising testosterone", "Reducing sweat rate"], 1,
          "It supercompensates glycogen stores, extending the duration of high-intensity endurance work before depletion.",
          "carb-loading-for-athletes.html", "Carb loading for athletes"),
        q("During prolonged low-carbohydrate conditions, the liver converts excess acetyl-CoA into:",
          ["Glucose", "Ketone bodies", "Lactate", "Glycogen"], 1,
          "With oxaloacetate diverted to gluconeogenesis, acetyl-CoA is converted to ketone bodies, which the brain and other tissues can use.",
          "beta-oxidation-explained.html", "Beta-oxidation explained"),
        q("Fasted cardio, compared with fed cardio at matched calories and protein, produces:",
          ["Substantially more fat loss", "No significant difference in fat loss over time", "Less fat loss", "More muscle gain"], 1,
          "It burns more fat during the session, but the body compensates across the day. Trials find no significant difference in fat loss over time.",
          "fasted-cardio-fat-loss.html", "Fasted cardio and fat loss"),
        q("Drinking far more fluid than sweat losses during a long event risks:",
          ["Nothing — more is always better", "Hyponatremia from diluted blood sodium", "Immediate dehydration", "Glycogen depletion"], 1,
          "Overdrinking can dilute blood sodium, causing exercise-associated hyponatremia — a genuinely dangerous condition.",
          "hydration-and-performance.html", "Hydration and performance"),
    ],
)


def page(slug, title, meta, category, eyebrow, h1, intro, questions, moreHref, tiers=None):
    hero_class = "hero page-hero" if category != "general" else "page-hero"
    tiers_js = ("tiers: " + json.dumps(tiers) + ",\n        ") if tiers else ""
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com https://*.adtrafficquality.google https://*.gstatic.com https://*.googleapis.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com https://*.adtrafficquality.google; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google https://*.googleapis.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.adtrafficquality.google; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<title>{esc_html(title)} | GetMacros.net</title>
<meta name="description" content="{esc_html(meta)}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
{seo_meta(title, meta, f"https://getmacros.net/{slug}.html", category=category)}
{article_jsonld(title, meta, f"https://getmacros.net/{slug}.html", kind="Quiz", category=category)}
{breadcrumb_jsonld(title, f"https://getmacros.net/{slug}.html", hub_name="Quiz", hub_url="https://getmacros.net/quiz.html")}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<link rel="stylesheet" href="css/site-v3.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body class="site-v3 article-page">
<a class="skip-link" href="#main-content">Skip to main content</a>
{ICON_SPRITE}
{nav_html("quiz")}

<main id="main-content">
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
{AD_SLOT}</main>

{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/lang.js?v={ASSET_VERSION}"></script>
<script src="js/confetti.js?v={ASSET_VERSION}"></script>
<script src="js/quiz.js?v={ASSET_VERSION}"></script>
<script>
  renderQuiz('quiz-root', {json.dumps(questions)}, {{
    title: {json.dumps(title.split(":")[0])},
    {tiers_js}moreHref: 'quiz.html'
  }});
</script>
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
