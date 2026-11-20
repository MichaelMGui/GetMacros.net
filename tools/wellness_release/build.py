"""Build the source-backed first wellness release and its compact food explorer."""
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))

from build_release_resources import resource_main
from normalize_calculator_layouts import Document

TODAY = '2026-11-20'
HOST = 'https://getmacros.net'
DOCS = ROOT / 'docs/wellness-expansion-2026-11-20'
SOURCE = Path(__file__).parent
DATE_LEDGER = SOURCE / 'publication-dates.json'
PUBLICATION_DATES = json.loads(DATE_LEDGER.read_bytes()) if DATE_LEDGER.is_file() else {}
EXPLORER = 'nutrient-density-explorer.html'
CLAIM_LIBRARY = 'wellness-claim-evidence.html'
STUDIO = EXPLORER + '#food-comparison-studio'
PILLARS = [
    'Nutrient Density, Vitamins & Minerals',
    'Protein, Foods, Diets & Food Comparisons',
    'Cortisol, Stress, Sleep & Recovery',
    'Appearance, Skin, Looksmaxxing & Wellness Culture',
    'Supplements, Peptides & Evidence-Based Wellness',
    'Practical Nutrition, Restaurants & Original Data Studies',
]
SECTIONS = [
    ('wellness-nutrients.html', 'Vitamins & minerals',
     'Which foods provide a nutrient, and how much is in the portion you eat? Compare reference foods and learn to read the units on food labels.',
     'broccoli', 'P01-01', EXPLORER, 'Explore nutrients in 18 reference foods'),
    ('wellness-foods-and-diets.html', 'Foods & diets',
     'Compare two foods as they are eaten. Read the source behind a viral diet claim, or find out which details to match on two packages.',
     'steak', 'P02-35', EXPLORER + '#compare-protein-and-fiber', 'Compare protein and fiber in two foods'),
    ('wellness-sleep-and-recovery.html', 'Sleep, stress & recovery',
     'See what research actually measured, from the timing of a caffeine dose to changes in soreness after exercise.',
     'egg', 'P03-01', CLAIM_LIBRARY, 'Check recovery claims'),
    ('wellness-appearance-and-culture.html', 'Appearance & online culture',
     'Unpack an unfamiliar term, check a before-and-after photo or find the evidence behind a skincare claim.',
     'strawberry', 'P04-02', CLAIM_LIBRARY, 'Check appearance claims'),
    ('wellness-supplement-evidence.html', 'Supplements & evidence',
     'Read a Supplement Facts panel, compare ingredient amounts and find out what a study actually tested.',
     'blueberry', 'P05-01', CLAIM_LIBRARY, 'Check supplement claims'),
    ('wellness-restaurant-and-diary.html', 'Restaurants & food logging',
     'Compare named restaurant portions and use the right values in your diary. Original GetMacros audits show where menu data is incomplete.',
     'chicken', 'P06-04', STUDIO, 'Compare a dish or order'),
]
SECTION_PAGES = tuple(section[0] for section in SECTIONS)
FDC_DATA = 'https://fdc.nal.usda.gov/download-datasets/'
ODS = 'https://ods.od.nih.gov/factsheets/{}-HealthProfessional/'
# Evidence about treatment stays out of the public release queue pending specialist review.
ARTICLES = [
    ('P01-01', 'magnesium', 'magnesium-foods-by-portion.html', 'Which foods have the most magnesium in a real serving?',
     'Compare pumpkin seeds, black beans and spinach by weight and on the plate, with a worked bean-bowl example.',
     [ODS.format('Magnesium'), FDC_DATA], 'USDA SR Legacy records 170557, 173735 and 168463, with NIH label guidance.'),
    ('P01-02', 'choline', 'choline-foods-eggs-soybeans-quinoa.html', 'How much choline is in an egg, soybeans or quinoa?',
     'Compare three NIH reference servings and see how much choline they contribute to a mixed bowl.',
     [ODS.format('Choline')], 'Reference food composition and U.S. label interpretation.'),
    ('P01-03', 'potassium', 'potassium-banana-potato-lentils.html', 'Do lentils or potatoes have more potassium than a banana?',
     'See how a banana, a baked potato and two sizes of cooked lentils compare using NIH food data.',
     [ODS.format('Potassium')], 'Reference food composition.'),
    ('P01-04', 'calcium-dairy-free', 'calcium-without-dairy-milk-soy-tofu.html', 'Can soymilk or tofu match the calcium in a cup of milk?',
     'Compare selected calcium-fortified soymilk, calcium-sulfate tofu and milk, with a worked example and a label check.',
     [ODS.format('Calcium'), 'https://www.healthlinkbc.ca/healthlinkbc-files/calcium-and-your-health'],
     'Reference food composition. Product ingredients, fortification and serving sizes vary.'),
    ('P01-05', 'iron-beans-beef', 'iron-in-lentils-beans-and-beef.html', 'Do lentils have more iron than beef? Compare the actual servings',
     'Use NIH reference servings to compare iron in lentils, chickpeas, trimmed beef and liver, with a worked bowl example.',
     [ODS.format('Iron')], 'Reference food composition and general explanation of bioavailability.'),
    ('P01-06', 'zinc-without-meat', 'zinc-foods-without-meat.html', 'Which foods supply zinc if you rarely eat meat?',
     'Compare zinc in pumpkin seeds, lentils, cheddar and Greek yogurt. See when a smaller topping changes the comparison.',
     [ODS.format('Zinc')], 'Reference food composition. The amounts describe zinc in food rather than the amount absorbed.'),
    ('P01-07', 'folate', 'folate-folic-acid-dfe-label.html', 'Folate vs. folic acid: what does mcg DFE mean on a label?',
     'Read folate and folic acid on the same label without double counting. Includes a worked U.S. label example.',
     [ODS.format('Folate'), 'https://www.fda.gov/food/nutrition-facts-label/folate-and-folic-acid-nutrition-and-supplement-facts-labels'],
     'U.S. label literacy. The example uses invented label amounts.'),
    ('P01-08', 'b12-without-dairy', 'vitamin-b12-foods-without-dairy.html', 'Which foods have vitamin B12 without dairy?',
     'Compare selected seafood and fortified foods for vitamin B12, then put two label amounts on the same volume basis.',
     [ODS.format('VitaminB12')], 'Reference food composition and a hypothetical label comparison.'),
    ('P01-11', 'vitamin-a-forms', 'vitamin-a-liver-vs-sweet-potato-rae.html', 'Liver vs. sweet potato: how to compare vitamin A in two different forms',
     'Compare published portions, understand retinol activity equivalents, and see which parts of the comparison need different evidence.',
     [ODS.format('VitaminA')], 'U.S. food composition and accounting conventions. No advice on frequency or supplementation.'),
    ('P01-13', 'vitamin-e-without-oils', 'vitamin-e-foods-nuts-seeds-no-oils.html', 'Which foods have vitamin E besides cooking oils?',
     'Compare the vitamin E in nuts, seeds and peanut butter, and see how a smaller seed topping changes the result.',
     [ODS.format('VitaminE')], 'U.S. reference food composition. Values represent alpha-tocopherol.'),
    ('P01-14', 'vitamin-k-greens', 'vitamin-k-spinach-kale-broccoli-servings.html', 'Spinach, kale or broccoli: how much vitamin K is in a serving?',
     'Compare raw leaves and cooked greens. A side-dish example shows why a cup measure cannot establish what cooking does.',
     [ODS.format('VitaminK')], 'Reference food composition. The table does not establish nutrient retention after cooking.'),
    ('P01-15', 'selenium-food-portions', 'selenium-foods-tuna-sardines-eggs.html', 'Which foods provide selenium in a portion you actually eat?',
     'Compare yellowfin tuna, sardines, eggs and oatmeal. A smaller fish portion changes the comparison.',
     [ODS.format('Selenium')], 'U.S. reference food composition and serving calculations.'),
    ('P01-16', 'brazil-nut-selenium-variation', 'why-brazil-nut-selenium-varies.html', 'Why does selenium vary so much in Brazil nuts?',
     'Compare two growing regions in a primary study and see why a reference amount cannot specify your bag.',
     ['https://pubmed.ncbi.nlm.nih.gov/28923728/', 'https://pubmed.ncbi.nlm.nih.gov/31426292/'],
     'Plant composition studies. No recommendation about how many nuts to eat.'),
    ('P01-18', 'iodized-salt-pinch', 'iodine-in-iodized-salt-per-pinch.html', 'How much iodine is in a pinch of iodized salt?',
     'Compare iodized table salt and noniodized sea salt by a measured portion, and see why a pinch adds uncertainty.',
     [ODS.format('Iodine')], 'U.S. food composition and kitchen measurement. Amounts are examples, not sodium or iodine intake targets.'),
    ('P01-23', 'riboflavin-no-milk', 'riboflavin-foods-without-cows-milk.html', 'Where can you find riboflavin without drinking cow’s milk?',
     'Compare fortified oats, almonds, mushrooms and other foods by serving and check whether the oat entry is fortified.',
     [ODS.format('Riboflavin')], 'U.S. reference composition. The portions are examples and do not establish overall dietary equivalence.'),
    ('P01-24', 'niacin-equivalents', 'what-are-niacin-equivalents-food-tables.html', 'What are niacin equivalents? How to read B3 in a food table',
     'Read preformed niacin and niacin equivalents on the same basis with a worked example from the NIH reference table.',
     [ODS.format('Niacin')], 'Reference-accounting example. The conversion is a convention and does not predict individual metabolism.'),
    ('P01-27', 'vitamin-d-mushrooms', 'vitamin-d-uv-mushrooms-label.html', 'Do UV-exposed mushrooms contain more vitamin D?',
     'Read the mushroom variety, treatment and serving on the package before using a vitamin D figure.',
     [ODS.format('VitaminD')], 'Reference food composition and a hypothetical U.S. label example.'),
    ('P01-37', 'vitamin-c-pepper-orange', 'vitamin-c-red-pepper-vs-orange.html', 'Does red pepper have more vitamin C than an orange?',
     'A half cup and a quarter cup can give opposite answers. Compare pepper, orange and strawberries using NIH values.',
     [ODS.format('VitaminC')], 'Reference food composition and food preparation limits.'),
    ('P02-01', 'raw-milk', 'is-raw-milk-more-nutritious.html', 'Is raw milk more nutritious than pasteurized milk?',
     'Compare the nutrition and food-safety questions separately, using FDA and Health Canada guidance.',
     ['https://www.fda.gov/food/buy-store-serve-safe-food/raw-milk-questions-answers',
      'https://www.canada.ca/en/health-canada/services/milk-infant-formula/raw-or-unpasteurized-milk.html'],
     'General food safety education from public health guidance.'),
    ('P02-02', 'grass-fed-beef', 'grass-fed-vs-grain-fed-ribeye-omega-3.html', 'Grass-fed vs. grain-fed ribeye: how much more omega-3?',
     'A North American study found a difference in ribeye fat. Compare the authors’ standardized serving model and the actual limits.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC13012854/'], 'Analytical comparison of commercial samples.'),
    ('P02-03', 'pasture-egg-cartons', 'pasture-raised-eggs-omega-3-carton.html', 'Does pasture-raised tell you how much omega-3 an egg has?',
     'A pasture study and an egg carton report different kinds of information. Compare quantities per egg and check which fatty acid the carton names.',
     ['https://www.nal.usda.gov/exhibits/ipd/frostonchickens/items/show/267', 'https://www.ams.usda.gov/publications/qa-shell-eggs'],
     'U.S. carton literacy and a primary study of a specific feeding and housing comparison.'),
    ('P02-09', 'whole-vs-skim-protein', 'whole-milk-vs-skim-protein-per-cup.html', 'Does whole milk have more protein than skim milk?',
     'Compare matching whole and skim cartons by the cup, then see why equal calories give a different result.',
     ['https://www.organicvalley.coop/products/whole-milk','https://www.organicvalley.coop/products/skim-fat-free-milk'],
     'U.S. product comparison using the manufacturer’s half-gallon labels.'),
    ('P02-10', 'lactose-free-milk-cartons', 'lactose-free-vs-regular-2-percent-milk.html', 'What changes on the label when 2% milk is lactose-free?',
     'Compare two U.S. half-gallons from the same brand and a separate high-protein lactose-free milk.',
     ['https://www.organicvalley.coop/products/2-percent-reduced-fat-milk',
      'https://www.organicvalley.coop/products/2-percent-reduced-fat-milk-lactose-free',
      'https://www.lactaid.com/products/lactaid-protein-2-percent-milk'],
     'Comparison of named U.S. labels. Formulation can vary between brands, sizes and dates.'),
    ('P02-12', 'collagen-protein-components', 'why-collagen-protein-grams-are-different.html', 'Does collagen count the same as other protein on a label?',
     'Keep the grams of protein and the amino acid composition separate when comparing collagen with another source.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC6566836/','https://pubmed.ncbi.nlm.nih.gov/31919527/'],
     'Amino acid accounting and interpretation of a protein-form comparison. No serving or supplementation advice.'),
    ('P02-20', 'tuna-drained-packing', 'tuna-oil-vs-water-drained-weight.html', 'Tuna in oil vs. water: what still differs after draining?',
     'Compare two USDA records for drained, no-added-salt light tuna at 100 g and the same 3-ounce serving.',
     [FDC_DATA], 'U.S. SR Legacy records 174227 and 171986. These are independent references, so the comparison does not isolate the packing medium.'),
    ('P02-34', 'carnivore-survey-evidence', 'carnivore-diet-survey-what-it-measured.html', 'What did the survey of 2,029 carnivore dieters actually measure?',
     'Separate respondents’ reports, the six-month eligibility rule, and questions the survey design could not answer.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC8684475/'], 'Interpretation of a self-selected survey, with no dietary prescription.'),
    ('P02-35', 'saladino-frameworks', 'paul-saladino-animal-based-vs-carnivore.html', 'What does Paul Saladino mean by “animal-based” versus “carnivore”?',
     'Read the foods and exclusions in the creator’s separate frameworks, then check which evidence applies to each.',
     ['https://www.paulsaladinomd.com/guides', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC8684475/',
      'https://www.fda.gov/food/buy-store-serve-safe-food/raw-milk-questions-answers'],
     'Primary creator materials show what is promoted. Nutrition and safety facts use independent primary sources.'),
    ('P02-37', 'santa-cruz-hydration-claim', 'santa-cruz-electrolytes-sodium-vs-hydration-evidence.html', 'Santa Cruz electrolytes: what the sodium figure tells you',
     'Compare separately listed powder formats and see what kind of research would test a hydration claim.',
     ['https://santacruzpaleo.com/products/mango-electrolyte-tub', 'https://pubmed.ncbi.nlm.nih.gov/26702122/'],
     'Observed U.S. manufacturer statements and primary trial methods. No product recommendation or mixing guidance.'),
    ('P02-38', 'blue-zones-pattern', 'blue-zones-diet-food-guide-vs-research.html', 'What is the Blue Zones diet? Separate the menu from the research',
     'Learn what the program suggests, what an Adventist cohort studied and how to compare the beans in an actual meal.',
     ['https://www.bluezones.com/wp-content/uploads/2019/12/BZL_Food-Guidelines-Printable_02.pdf',
      'https://pubmed.ncbi.nlm.nih.gov/23836264/', FDC_DATA],
     'The program guide establishes its own claims. The primary study supplies observational evidence.'),
    ('P02-39', 'blue-diet-meaning', 'blue-diet-blue-zones-vs-aquatic-food.html', 'What does “Blue Diet” mean? Two very different uses of blue',
     'Tell the Blue Zones eating program apart from aquatic blue foods in food-system research.',
     ['https://www.bluezones.com/wp-content/uploads/2019/12/BZL_Food-Guidelines-Printable_02.pdf',
      'https://www.nature.com/articles/s41586-021-03917-1'],
     'Terminology and research literacy. The examples illustrate definitions, not a recommended eating plan.'),
    ('P02-40', 'predimed-trial-reanalysis', 'predimed-mediterranean-diet-what-trial-tested.html', 'What did PREDIMED actually test about the Mediterranean diet?',
     'Read the trial groups, published event counts and the reason the investigators reanalysed the study.',
     ['https://pubmed.ncbi.nlm.nih.gov/29897866/','https://www.nejm.org/doi/full/10.1056/NEJMoa1800389'],
     'Trial interpretation. The result is specific to the studied groups and is not an individual risk prediction.'),
    ('P02-41', 'mediterranean-snack-vs-pattern', 'mediterranean-snack-vs-eating-pattern.html', 'Does a “Mediterranean” snack tell you anything about your eating pattern?',
     'Use the food label for one product and a different set of questions for a repeated eating pattern.',
     ['https://www.heart.org/en/healthy-living/healthy-eating/eat-smart/nutrition-basics/mediterranean-diet/',
      'https://professional.heart.org/en/science-news/2021-dietary-guidance-to-improve-cardiovascular-health/top-things-to-know'],
     'Food-label and pattern literacy. The snack examples are invented.'),
    ('P02-50', 'powdered-milk-portions', 'dry-milk-vs-reconstituted-serving.html', 'Is a serving of powdered milk the same as a cup after mixing?',
     'Convert a dry-milk label to the part of the prepared drink you actually pour, using the amount of powder and final batch size.',
     ['https://fns-prod.azureedge.us/sites/default/files/resource-files/MilkNonfatDry2020.pdf',
      'https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label'],
     'U.S. dry milk serving interpretation. The batch figures are illustrative and amounts vary by label.'),
    ('P03-01', 'caffeine', 'caffeine-before-bed-dose-and-timing.html', 'How late is too late for caffeine? What two trials tested',
     'Compare the dose, timing and limits of two placebo-controlled sleep studies before drawing a cutoff.',
     ['https://pubmed.ncbi.nlm.nih.gov/24235903/', 'https://pubmed.ncbi.nlm.nih.gov/39377163/'],
     'Research summary with no individualized advice or universal cutoff.'),
    ('P03-04', 'cortisol-awakening', 'cortisol-awakening-response-explained.html', 'Cortisol after waking: the time on the clock can mislead',
     'See how cortisol-awakening research distinguishes time since waking from clock time, with a worked timeline.',
     ['https://pubmed.ncbi.nlm.nih.gov/26563991/', 'https://pubmed.ncbi.nlm.nih.gov/36252387/'],
     'Research methods. Individual test interpretation and diagnosis are outside this guide.'),
    ('P03-06', 'cortisol-sample-types', 'cortisol-hair-saliva-blood-study-differences.html', 'Why cortisol studies use hair, saliva or blood',
     'Compare the time window each sample type represents and see why a one-time reading differs from repeated measurements.',
     ['https://pubmed.ncbi.nlm.nih.gov/21515299/', 'https://pubmed.ncbi.nlm.nih.gov/24513702/'],
     'Research methods. Individual testing and diagnosis are outside the article’s scope.'),
    ('P03-12', 'watch-sleep-stages', 'sleep-tracker-deep-sleep-score-accuracy.html', 'Can your sleep tracker tell how much deep sleep you got?',
     'Compare estimates of sleep versus wake with stage-by-stage agreement in two device studies.',
     ['https://pubmed.ncbi.nlm.nih.gov/33378539/','https://pubmed.ncbi.nlm.nih.gov/40303381/'],
     'Consumer-device research literacy, without recommendations for diagnosis or a current device ranking.'),
    ('P03-13', 'sleep-regularity-measure', 'sleep-regularity-versus-duration-study.html', 'What does sleep regularity measure that sleep duration misses?',
     'Two hypothetical schedules with the same sleep duration show what a sleep regularity study is comparing.',
     ['https://www.nature.com/articles/s41598-017-03171-4', 'https://pubmed.ncbi.nlm.nih.gov/37738616/'],
     'Research methods and observational study interpretation. The schedules are illustrations, not personalised sleep guidance.'),
    ('P03-16', 'decaf-caffeine', 'does-decaf-coffee-have-caffeine.html', 'Does decaf coffee have caffeine? Check the cup size',
     'Compare the FDA’s typical decaf range with measured coffee-shop samples and put different drink sizes on the same basis.',
     ['https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much', 'https://academic.oup.com/jat/article-abstract/30/8/611/714415'],
     'Beverage composition and label literacy. The historical study does not give current retailer-specific amounts.'),
    ('P03-19', 'alcohol-onset-vs-continuity', 'alcohol-sleep-onset-vs-staying-asleep.html', 'Alcohol and sleep: why the first half of the night can look different',
     'See how an alcohol sleep-lab study separated sleep onset, the first half of the night and the second half.',
     ['https://pubmed.ncbi.nlm.nih.gov/21323679/'], 'Interpretation of a supervised laboratory study. No advice on alcohol consumption.'),
    ('P03-22', 'infrared-sauna', 'infrared-sauna-recovery-soreness-study.html', 'Does infrared sauna help recovery? What a soreness study measured',
     'See how a crossover study distinguished soreness, jump performance and perceived recovery after resistance exercise.',
     ['https://pubmed.ncbi.nlm.nih.gov/37398966/',
      'https://www.cdc.gov/yellow-book/hcp/environmental-hazards-risks/heat-and-cold-illness-in-travelers.html'],
      'Evidence interpretation. No heat exposure protocol or individualized advice.'),
    ('P03-30', 'cold-water-lifting', 'cold-water-after-lifting-muscle-study.html', 'Do ice baths after lifting change training gains? What two studies found',
     'Compare how two resistance training studies measured muscle size and strength after repeated cold-water immersion.',
     ['https://pubmed.ncbi.nlm.nih.gov/26174323/', 'https://pubmed.ncbi.nlm.nih.gov/31513450/'],
     'Research interpretation. No instructions for cold-water exposure or treatment.'),
    ('P03-48', 'phone-night-shift-trial', 'does-night-shift-phone-mode-improve-sleep.html', 'Does Night Shift help you sleep? What the phone trial compared',
     'Compare a warmer display, normal display and a no-phone condition, then distinguish sleep measures from melatonin.',
     ['https://pubmed.ncbi.nlm.nih.gov/33867308/', 'https://pubmed.ncbi.nlm.nih.gov/31191118/'],
     'Research interpretation. Results apply to the devices, participants and conditions tested.'),
    ('P03-49', 'magnesium-sleep-placebo', 'why-placebo-matters-magnesium-sleep-trial.html', 'A magnesium sleep study improved in both groups. What does that mean?',
     'Compare the reported change in each study group with the difference between them, using an actual placebo-controlled trial.',
     ['https://pubmed.ncbi.nlm.nih.gov/40918053/'], 'Research interpretation of a questionnaire outcome. No treatment or dosage guidance.'),
    ('P04-01', 'acne', 'diet-and-acne-what-the-trial-tested.html', 'Can diet affect acne? What the trial changed besides sugar',
     'Read what a 12-week acne trial tested and compare its conclusions with the dermatology guideline.',
     ['https://pubmed.ncbi.nlm.nih.gov/17616769/', 'https://www.aad.org/news/updated-guidelines-acne-management'],
     'Specialist review pending.'),
    ('P04-02', 'looksmaxxing-context', 'what-is-looksmaxxing-online.html', 'What does looksmaxxing mean online, and why does the context matter?',
     'Understand the term and use a simple question to separate grooming, appearance comparisons and unsupported claims.',
     ['https://www.collinsdictionary.com/dictionary/english/looksmaxxing',
      'https://www.ofcom.org.uk/siteassets/resources/documents/research-and-data/media-literacy-research/making-sense-of-media/understanding-childrens-use-and-perceptions-of-asmr-and-self-improvement-content/report---understanding-childrens-use-and-perceptions-of-asmr-and-self-improvement-content.pdf?v=412010',
      'https://www.aad.org/member/clinical-quality/clinical-care/emerging-diseases/viral-trends/looksmaxxing'],
     'Media literacy. The examples are invented and intentionally omit unsafe practices.'),
    ('P04-04', 'mogging-meaning', 'what-does-mogging-mean-wellness-claims.html', 'What does “mogging” mean? Read the joke and the claim',
     'See how the 2026 slang word is used in jokes, appearance comparisons and online product claims.',
     ['https://www.collinsdictionary.com/dictionary/english-thesaurus/mogging',
      'https://www.collinsdictionary.com/us/woty', 'https://doi.org/10.1177/17416590251387245'],
     'Lexicography and media literacy. Examples are invented.'),
    ('P04-05', 'hypergamy-measure', 'hypergamy-meaning-research-vs-online.html', 'What does hypergamy mean in research and online?',
     'See what educational hypergamy measures, how its direction is defined, and what online posts often leave out.',
     ['https://doi.org/10.1215/00703370-10126742','https://doi.org/10.1553/populationyearbook2017s215'],
     'Social-science and media literacy. Fictional examples illustrate definitions, not advice or ratings of people.'),
    ('P04-07', 'gua-sha', 'gua-sha-jawline-what-study-measured.html', 'Can gua sha change your jawline? What researchers measured',
     'A small gua sha trial measured distances along the face. See what those measurements tell us about a permanent jawline claim.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC12121324/'],
     'Media literacy. No cosmetic technique, treatment recommendation or before-and-after claim.'),
    ('P04-09', 'appearance-photo-evidence', 'before-after-face-photos-camera-distance.html', 'Why two face photos can tell different stories about the same face',
     'Read before-and-after claims with a camera distance, lighting, pose and study-design checklist.',
     ['https://pubmed.ncbi.nlm.nih.gov/29494735/', 'https://pubmed.ncbi.nlm.nih.gov/37543968/'],
     'Research literacy. The hypothetical image comparison illustrates confounding and perspective.'),
    ('P04-11', 'cortisol-face-meaning', 'cortisol-face-what-photos-cannot-show.html', 'What does “cortisol face” mean, and can a photo show it?',
     'Separate a viral caption, an appearance observation and the clinical evidence needed to identify the cause.',
     ['https://www.niddk.nih.gov/health-information/endocrine-diseases/cushings-syndrome',
      'https://www.endocrine.org/clinical-practice-guidelines/diagnosis-of-cushing-syndrome'],
     'Health information and media literacy. No diagnosis or individualized testing advice.'),
    ('P04-14', 'skin-hydration-meaning', 'what-skin-hydration-studies-measure.html', 'What does a skin hydration study actually measure?',
     'Separate skin capacitance, elasticity and photo ratings, then check how soon a reading was taken after application.',
     ['https://pubmed.ncbi.nlm.nih.gov/11428963/'], 'Instrument and outcome literacy. No treatment or product ranking.'),
    ('P04-19', 'sleep-face-ratings', 'sleep-loss-face-photo-ratings.html', 'Does sleep change how you look in photos? What two studies rated',
     'Compare who was photographed, who rated the pictures, and why an observer’s impression does not measure skin health.',
     ['https://pubmed.ncbi.nlm.nih.gov/21156746/', 'https://pubmed.ncbi.nlm.nih.gov/28572989/'],
     'Interpretation of observer ratings from two experimental photography studies.'),
    ('P04-20', 'produce-skin-color-study', 'fruit-vegetable-skin-color-study.html', 'What did a study linking produce intake and skin color measure?',
     'Separate measured light reflectance, reported food intake and observer ratings in one frequently cited study.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC3296758/'], 'Study interpretation and media literacy. Skin color is not used as a health or beauty target.'),
    ('P04-24', 'hair-breakage-shedding', 'hair-breakage-vs-shedding-study-measures.html', 'Hair breakage and shedding: what did a study count?',
     'Distinguish a broken hair fiber from shedding. Compare two research methods before relying on a nutrition claim.',
     ['https://pubmed.ncbi.nlm.nih.gov/26207659/','https://pubmed.ncbi.nlm.nih.gov/18559765/'],
     'Research literacy. Does not diagnose the cause of a person’s hair loss.'),
    ('P04-25', 'hair-density-thickness', 'hair-density-vs-shaft-thickness-study.html', 'Hair density vs. thickness: what did the study measure?',
     'Understand counts per square centimeter and widths in micrometers with one reference study and a fictional example.',
     ['https://pubmed.ncbi.nlm.nih.gov/36407644/'], 'Interpretation of research measures and illustrative figures. No personal thresholds.'),
    ('P04-34', 'clinical-grade-labels', 'what-clinical-grade-means-skincare-label.html', 'What does “clinical grade” mean on a skincare label?',
     'Check the actual product claim, study and outcome behind a prominent skincare label phrase.',
     ['https://www.fda.gov/cosmetics/cosmetics-labeling/cosmetics-labeling-claims',
      'https://www.fda.gov/cosmetics/resources-consumers-cosmetics/cosmetics-safety-qa-personal-care-products'],
     'U.S. label and advertising literacy. The examples are fictional.'),
    ('P04-35', 'sponsored-beauty-posts', 'sponsored-beauty-posts-disclosure-evidence.html', 'What does “gifted” or “paid partnership” tell you about a beauty claim?',
     'Read the disclosure, the claim and the source separately. Three worked examples show what each label establishes.',
     ['https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers', 'https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking'],
     'U.S. endorsement guidance and fictional posts, with no individual legal or product assessment.'),
    ('P05-01', 'supplement-label', 'read-supplement-facts-per-serving.html', 'Supplement Facts: is that amount per capsule or per serving?',
     'Compare fictional Supplement Facts labels and learn what a U.S. ingredient amount or proprietary blend represents.',
     ['https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements'],
     'U.S. label literacy. No supplement dosing or product endorsements.'),
    ('P05-03', 'peptide-labels', 'collagen-peptides-vs-peptide-drugs.html', 'Collagen peptides and peptide drugs: what the labels tell you',
     'See why collagen powder, a peptide face cream and a peptide drug need different evidence and regulatory checks.',
     ['https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements',
      'https://www.fda.gov/cosmetics/cosmetics-laws-regulations/it-cosmetic-drug-or-both-or-it-soap',
      'https://www.fda.gov/drugs/human-drug-compounding/compounding-and-fda-questions-and-answers'],
     'U.S. regulatory and label literacy. No eligibility or advice for a particular product.'),
    ('P05-04', 'bpc-regulatory-context', 'bpc-157-human-evidence-and-us-policy.html', 'Is BPC-157 approved? What changed in the 2026 U.S. compounding policy',
     'Read the FDA staff review, committee vote and HHS interim policy separately. Each answers a different question about evidence or approval.',
     ['https://www.fda.gov/media/193343/download',
      'https://www.hhs.gov/sites/default/files/hhs-503a-peptide-enforcement-discretion-policy.pdf',
      'https://www.hhs.gov/sites/default/files/hhs-peptide-enforcement-discretion-appendix-b.pdf',
      'https://www.fda.gov/drugs/human-drug-compounding/compounding-and-fda-questions-and-answers'],
     'Dated U.S. agency-document explainer. No treatment, dosing, or product access advice.'),
    ('P05-08', 'supplement-quality-seals', 'what-supplement-quality-seals-verify.html', 'What does a third-party supplement seal actually verify?',
     'Check the issuer and the exact product. Quality verification and a claimed health outcome require different evidence.',
     ['https://www.usp.org/sites/default/files/usp/document/products-services/dietary-supplement-verification-summary-final.pdf',
      'https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements'],
     'U.S. supplement assurance and label literacy. No product recommendation or certification claim for a specific bottle.'),
    ('P05-12', 'vitamin-d-label-units', 'vitamin-d-mcg-to-iu-on-label.html', 'Vitamin D on labels: how to convert micrograms and IU',
     'Convert both vitamin D units and two serving sizes without mistaking equivalent amounts for separate entries.',
     [ODS.format('VitaminD'), 'https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling'],
     'U.S. label arithmetic. The example values are fictional and are not suggested doses.'),
    ('P05-17', 'fish-oil-epa-dha-label', 'fish-oil-1000-mg-vs-epa-dha.html', 'Why 1,000 mg of fish oil does not mean 1,000 mg of EPA and DHA',
     'Follow the oil, EPA and DHA lines in a real archived Supplement Facts panel and avoid adding the components twice.',
     ['https://api.ods.od.nih.gov/dsld/s3/pdf/326004.pdf'], 'Archived U.S. manufacturer label. The archive establishes the declaration for this edition.'),
    ('P05-21', 'creatine-form-trials', 'creatine-monohydrate-vs-alternative-form-studies.html', 'Do studies of creatine monohydrate apply to every creatine blend?',
     'Read the tested form and outcome in two separate comparisons of creatine products.',
     ['https://pubmed.ncbi.nlm.nih.gov/19228401/','https://pubmed.ncbi.nlm.nih.gov/22971354/'],
     'Primary trial interpretation. No dosage or individual product guidance.'),
    ('P05-22', 'creatine-hair', 'creatine-hair-loss-what-trials-measured.html', 'Does creatine cause hair loss? Two trials tested different things',
     'Compare an older DHT study with a 12-week randomized trial that measured hair directly.',
     ['https://pubmed.ncbi.nlm.nih.gov/19741313/', 'https://pubmed.ncbi.nlm.nih.gov/40265319/'],
     'Study interpretation. No dosing, supplement recommendation or clinical assessment.'),
    ('P05-26', 'magnesium-form-study', 'magnesium-citrate-oxide-absorption-study.html', 'Magnesium citrate vs. oxide: what does “better absorbed” mean?',
     'Compare elemental amounts on the label, then see what an absorption study measured and what outcomes it did not test.',
     [ODS.format('Magnesium'), 'https://pubmed.ncbi.nlm.nih.gov/2407766/'],
     'U.S. label literacy and interpretation of a small head-to-head absorption study. No supplement selection or dosing advice.'),
    ('P05-40', 'supplement-structure-function', 'what-structure-function-claims-mean.html', 'What does a “supports normal function” claim on a supplement mean?',
     'Distinguish a U.S. structure/function statement, an amount on the label and a claim to treat a disease.',
     ['https://www.fda.gov/food/information-industry-dietary-supplements/notifications-structurefunction-and-related-claims-dietary-supplement-labeling',
      'https://www.fda.gov/regulatory-information/search-fda-guidance-documents/small-entity-compliance-guide-structurefunction-claims'],
     'U.S. consumer label literacy. Examples are illustrative and do not evaluate particular products.'),
    ('P05-45', 'melatonin-label-test', 'melatonin-gummies-label-vs-lab-test.html', 'How accurate were melatonin gummy labels in a U.S. lab study?',
     'Read the 25-product test correctly, including what 347% of the label means and why it does not generalize to today’s shelf.',
     ['https://jamanetwork.com/journals/jama/fullarticle/2804077'],
     'Historical product-label audit. No dose guidance or advice about use.'),
    ('P06-01', 'breakfast-fiber', 'fast-food-breakfast-fiber-data.html', 'How much fiber do U.S. fast-food breakfasts actually list?',
     'An audit of the fiber figures in U.S. breakfast rows, with totals by chain and examples of how portion size affects comparisons.',
     ['https://getmacros.net/fast-food-nutrition-data-report.html',
      'https://www.chick-fil-a.com/nutrition-allergens', 'https://www.bk.com/nutrition-explorer'],
     'GetMacros registry snapshot. Includes counted portions, sides and named variants with a breakfast tag.'),
    ('P06-02', 'nugget-protein-ranking', 'chick-fil-a-protein-per-calorie-vs-serving.html', 'What changes when you rank Chick-fil-A nuggets by protein per calorie?',
     'The order with the largest protein total changes when you compare protein per 100 calories. Here is the math for four U.S. portions.',
     ['https://www.chick-fil-a.com/nutrition-allergens'], 'Curated U.S. portions with source values and calculated ratios.'),
    ('P06-03', 'uk-weight-coverage', 'how-many-uk-menu-items-have-serving-weights.html', 'Which UK restaurant nutrition listings can you compare by weight?',
     'An audit of UK menu rows with confirmed gram weights and calories, including why a mixed g/ml field needs a closer look.',
     ['https://getmacros.net/fast-food-nutrition-data-report.html',
      'https://www.greggs.com/nutrition', 'https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf'],
     'Snapshot of the GetMacros UK registry. Absence of a comparison field here does not establish absence from the underlying menu.'),
    ('P06-04', 'canada-sodium-coverage', 'missing-sodium-canadian-restaurant-menus.html', 'What happens to a Canadian menu comparison when sodium is missing?',
     'Count named Canadian listings with known, zero and missing sodium, and see how a missing value changes a sortable comparison.',
     ['https://getmacros.net/fast-food-nutrition-data-report.html', 'https://pizzanova.com/nutrition',
      'https://www.chick-fil-a.ca/nutrition-allergens'],
     'Snapshot of the Canadian GetMacros registry. The Pizza Nova source is the retained calories-only capture; its live page could not be rechecked.'),
    ('P06-07', 'fruit-fries-order', 'chick-fil-a-fruit-cup-vs-waffle-fries-order.html', 'What changes when you swap waffle fries for fruit at Chick-fil-A?',
     'Compare the same 8-count U.S. nuggets with small waffle fries or a small fruit cup, using the official portions.',
     ['https://www.chick-fil-a.com/nutrition-allergens'],
     'Two calculated U.S. orders using individually published portions. Sauces and drinks are excluded.'),
    ('P06-10', 'mcdonalds-japan-us-double', 'mcdonalds-double-cheeseburger-japan-vs-us.html', 'McDonald’s Double Cheeseburger calories in Japan vs. the U.S.',
     'Check two local Double Cheeseburger listings and the separate higher-calorie Japanese nighttime entry.',
     ['https://www.mcdonalds.com/us/en-us/product/double-cheeseburger.html', 'https://www.mcdonalds.co.jp/products/1360/',
      'https://www.mcdonalds.co.jp/quality/allergy_Nutrition/nutrient/'],
     'Country-specific standard burgers and a distinct Japan nighttime item. All calories refer to the listed burger alone.'),
    ('P06-13', 'mcnuggets-happy-meal-scope', 'mcdonalds-happy-meal-vs-four-nuggets-calories.html', 'Why McDonald’s lists two calorie numbers for a four-piece nugget order',
     'Compare the U.S. four-piece nuggets by themselves with the restaurant’s published Happy Meal configuration.',
     ['https://www.mcdonalds.com/us/en-us/product/chicken-mcnuggets-4-piece.html',
      'https://www.mcdonalds.com/us/en-us/meal/4-piece-chicken-mcnuggets-happy-meal.html'],
     'Published U.S. items and exact configuration. Changing the drink or sides can change the total.'),
    ('P06-21', 'diary-saved-source-values', 'what-happens-to-food-diary-when-data-changes.html', 'Does a nutrition update change an old food diary entry?',
     'Understand what GetMacros stores at the time of logging, and why the same food can show a different total later.',
     ['https://getmacros.net/back-up-and-move-food-diary.html','https://getmacros.net/food-diary.html'],
     'GetMacros diary behavior, checked against the saved-entry calculation and source information.'),
    ('P06-25', 'beans-drained-recipe', 'canned-beans-sodium-drained-vs-liquid.html', 'How much sodium is in your recipe after draining canned beans?',
     'Read the preparation basis of the bean entry, compare measured sodium across three states, and calculate a recipe subtotal.',
     ['https://www.bushbeans.com/-/media/BushsBeans/FAQ/reduced_sodium_article.pdf',
      'https://www.tandfonline.com/doi/full/10.1080/15428052.2011.582405'],
     'Published canned bean experiment and an illustrative recipe calculation. Exact brands and methods can differ.'),
    ('P06-32', 'uk-menu-salt-sodium', 'greggs-salt-to-sodium-serving-conversion.html', 'How to convert Greggs’ salt figures to sodium',
     'Convert the September 2026 UK sausage roll and four-pack salt entries without mixing portions or treating salt as sodium.',
     ['https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf', 'https://www.nidirect.gov.uk/articles/salt'],
     'Documented UK source portions and calculated sodium equivalents from rounded salt values.'),
    ('P06-33', 'week-label-rounding', 'weekly-food-log-nutrition-label-rounding.html', 'How much can food label rounding move a week of diary entries?',
     'Follow two hypothetical added-sugar numbers from the unrounded amount to the printed serving and the weekly total.',
     ['https://www.fda.gov/media/134505/download', 'https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label'],
     'U.S. label rounding example. The products and unrounded values are invented to illustrate the rule.'),
    ('P01-32', 'blackstrap-molasses-labels', 'blackstrap-molasses-iron-calcium-label-comparison.html', 'How much iron and calcium is in blackstrap molasses?',
     'Compare a labeled tablespoon with a weighed portion from a second producer, and see how a recipe divides those amounts.',
     ['https://www.swansonvitamins.com/p/swanson-organic-certified-organic-blackstrap-molasses-16-fl-oz-473-ml-liquid?expandProductReviews=t',
      'https://www.webstaurantstore.com/documents/specsheets/blackstrap_molasses_09-09-25_.pdf',
      'https://www.goldenbarrel.com/product/golden-barrel-blackstrap-molasses/'],
     'U.S. retail label and manufacturer\'s product specification. Conversions are estimates from the published units.'),
    ('P03-05', 'cortisol-detox-food', 'cortisol-detox-food-what-studies-measure.html', 'Can a food ‘detox’ cortisol? What meal studies actually show',
     'See why an hour-after-lunch hormone result and a multi-week rhythm study answer different questions.',
     ['https://pubmed.ncbi.nlm.nih.gov/24092834/',
      'https://pubmed.ncbi.nlm.nih.gov/32013045/',
      'https://www.niddk.nih.gov/health-information/endocrine-diseases/cushings-syndrome'],
     'General science education. Two meal experiments do not establish a treatment for abnormal cortisol.'),
    ('P04-03', 'softmaxxing-hardmaxxing', 'softmaxxing-vs-hardmaxxing-meaning.html', 'What do ‘softmaxxing’ and ‘hardmaxxing’ mean?',
     'Learn how people use the two labels, how they blur different risks, and how to read a claim without adopting its assumptions.',
     ['https://www.aad.org/member/clinical-quality/clinical-care/emerging-diseases/viral-trends/looksmaxxing',
      'https://www.ofcom.org.uk/siteassets/resources/documents/research-and-data/media-literacy-research/making-sense-of-media/understanding-childrens-use-and-perceptions-of-asmr-and-self-improvement-content/report---understanding-childrens-use-and-perceptions-of-asmr-and-self-improvement-content.pdf?v=412010'],
     'Online media literacy based on UK qualitative research and U.S. professional dermatology guidance.'),
    ('P05-30', 'sports-drink-ors', 'sports-drink-vs-oral-rehydration-solution.html', 'Is a sports drink the same as an oral rehydration solution?',
     'Compare the product purposes and see what one controlled study measured over four hours.',
     ['https://www.who.int/news-room/fact-sheets/detail/Diarrhoeal-disease',
      'https://pubmed.ncbi.nlm.nih.gov/26702122/',
      'https://pubmed.ncbi.nlm.nih.gov/36476514/'],
     'Product terminology and interpretation of a controlled hydration experiment. No individual treatment or electrolyte prescription.'),
    ('P06-11', 'subway-nz-breakfast', 'subway-new-zealand-breakfast-calories-and-protein.html', 'Subway New Zealand breakfast calories and protein by order',
     'Compare the official named portions for five breakfast subs and wraps, including a swap between the 6-inch subs.',
     ['https://www.subway.com/en-nz/-/media/New_Zealand/Documents/Nutritionals/NZ-Nutritional-Summary.pdf',
      'https://www.subway.com/en-nz/menunutrition/menu/breakfast/'],
     'New Zealand only. Nutrition is from Subway’s dated October 2025 guide. The menu page is a separate availability reference.'),
    ('P02-07', 'skyr-greek-yogurt', 'plain-skyr-vs-greek-yogurt-protein.html', 'Plain skyr vs. Greek yogurt: how much protein at the same weight?',
     'Compare two U.S. nonfat products per 150 g and see how the tub label changes the apparent result.',
     ['https://siggis.com/product/plain-nonfat/',
      'https://chobani.com/products/yogurt-greek-nonfat-plain-large-size-tub'],
     'Specific U.S. products and labeled portions. Matched-weight figures are calculated from rounded label values.'),
    ('P02-08', 'cottage-yogurt-sodium', 'cottage-cheese-vs-greek-yogurt-sodium.html', 'Cottage cheese vs. Greek yogurt: what changes if sodium matters?',
     'Match a 110 g spoonful from two clearly named products before comparing protein and sodium.',
     ['https://goodculture.com/product/simply-cottage-cheese-16-oz-lowfat-classic/',
      'https://chobani.com/products/yogurt-greek-nonfat-plain-large-size-tub'],
     'U.S. labels for the specific plain products. Yogurt numbers at 110 g are calculated.'),
    ('P03-14', 'sleep-time-bed-denominator', 'time-in-bed-vs-time-asleep.html', 'Time in bed vs. time asleep: what is your sleep tracker counting?',
     'Work one fictional night through two sleep-efficiency formulas and see why the percentages differ.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC4751425/',
      'https://pubmed.ncbi.nlm.nih.gov/33666165/'],
     'Measurement literacy about sleep research. The example is invented and supplies no diagnosis or target.'),
    ('P04-17', 'collagen-hydration-wrinkle-outcome', 'collagen-skin-hydration-vs-wrinkle-evidence.html', 'What a collagen skin-hydration study can tell you about wrinkles',
     'Read a specific trial’s hydration and follow-up measurements, and identify the separate outcome a wrinkle claim would need.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC12661388/',
      'https://pubmed.ncbi.nlm.nih.gov/40324552/'],
     'Research literacy based on controlled experiments and a pooled analysis. No treatment recommendation.'),
    ('P05-09', 'proprietary-blend-weights', 'supplement-proprietary-blend-what-weight-means.html', 'Can a proprietary blend label tell you how much of each ingredient is inside?',
     'Use two example formulas to see why a blend’s total weight and ingredient order cannot reveal individual doses.',
     ['https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101/subpart-C/section-101.36',
      'https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling'],
     'U.S. Supplement Facts rules. The example formulas are fictional and illustrate a labeling ambiguity.'),
    ('P05-10', 'elemental-magnesium-label', 'elemental-magnesium-on-supplement-label.html', 'What does elemental magnesium mean on the label?',
     'See why two products can list 250 mg of magnesium and use different forms and serving sizes.',
     ['https://ods.od.nih.gov/factsheets/Magnesium-HealthProfessional/',
      'https://www.naturemade.com/products/magnesium-250-mg-tablets',
      'https://www.naturemade.com/products/nature-made-magnesium-citrate-softgels-250-mg'],
     'Two named U.S. supplement labels and NIH labeling guidance. The comparison is about amount declarations.'),
    ('P06-18', 'dual-column-package', 'nutrition-label-per-serving-vs-whole-package.html', 'When should you use the whole-package column on a food label?',
     'See which figure to log when you eat a full pack, a weighed portion, or save some for later.',
     ['https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label',
      'https://www.fda.gov/media/133699/download',
      'https://www.fda.gov/media/134505/download'],
     'U.S. label guidance and a fictional 75 g package. Values illustrate rounding and partial portions.'),
    ('P01-09', 'whole-fruit-vitamin-c', 'vitamin-c-in-one-kiwi-orange-or-papaya.html', 'How much vitamin C is in one kiwi, orange or papaya?',
     'Compare four USDA fruit portions and see why the most concentrated fruit need not supply the most per piece.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://ods.od.nih.gov/factsheets/VitaminC-HealthProfessional/'],
     'U.S. USDA SR Legacy reference values and edible portion weights. Individual fruit size and variety vary.'),
    ('P02-14', 'edamame-mature-soybeans', 'edamame-vs-mature-soybeans-protein-by-portion.html', 'Edamame vs. mature soybeans: how much protein per cup?',
     'Compare two cooked, shelled USDA portions, then separate the effect of concentration from the grams in the cup.',
     [FDC_DATA],
     'USDA SR Legacy records 168411 and 174271, covering prepared edamame and boiled mature beans.'),
    ('P03-08', 'exercise-cortisol-time', 'why-exercise-timing-changes-cortisol-readings.html', 'Why does exercise timing matter for a cortisol reading?',
     'See how sampling, exercise intensity, and changes in plasma volume affect comparisons across three experiments.',
     ['https://pubmed.ncbi.nlm.nih.gov/18787373/',
      'https://pubmed.ncbi.nlm.nih.gov/18642761/',
      'https://pubmed.ncbi.nlm.nih.gov/11991783/'],
     'Method interpretation for healthy adult studies. Clinical questions about test timing require a care team.'),
    ('P04-15', 'water-skin-baseline', 'drinking-water-skin-hydration-baseline-intake.html', 'Does drinking more water improve skin hydration if you already drink enough?',
     'Read what a four-week study found after separating higher and lower habitual fluid intake.',
     ['https://pubmed.ncbi.nlm.nih.gov/38816975/',
      'https://pmc.ncbi.nlm.nih.gov/articles/PMC4529263/'],
     'Study interpretation for healthy adults. The trial’s intake groups are research categories and do not diagnose dehydration.'),
    ('P05-13', 'vitamin-d2-d3-trial-matched', 'vitamin-d2-vs-d3-matched-trial.html', 'Vitamin D2 vs. D3: what did a matched-dose trial measure?',
     'Compare D2 and D3 in the same fortified food, and distinguish the dose on a label from the outcome in blood.',
     ['https://pubmed.ncbi.nlm.nih.gov/28679555/',
      'https://pubmed.ncbi.nlm.nih.gov/22623396/',
      'https://ods.od.nih.gov/factsheets/Vitamind-HealthProfessional/'],
     'Research literacy from UK fortification studies and NIH definitions. No recommendation about individual supplements.'),
    ('P06-22', 'calories-only-diary-backup', 'what-a-calories-only-diary-backup-keeps.html', 'Can you restore a food diary entry that has calories but no macros?',
     'Learn which calories-only snapshots GetMacros can restore and why a calorie total cannot reconstruct missing macros.',
     ['https://github.com/MichaelMGui/GetMacros.net/blob/6200a51eb94ce479117b9754a6865f2266a4af4f/js/food-core.js',
      'https://getmacros.net/back-up-and-move-food-diary.html'],
     'GetMacros schema 1 importer and source snapshots. Example values are fictional.'),
    ('P01-10', 'broccoli-frozen-versus-fresh', 'frozen-vs-fresh-cooked-broccoli-vitamin-c.html', 'Does cooked frozen broccoli have less vitamin C than fresh?',
     'Compare two cooked USDA servings, then read what a broccoli retention study can and cannot explain.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://pubmed.ncbi.nlm.nih.gov/17995854/',
      'https://pubmed.ncbi.nlm.nih.gov/30153746/'],
     'Screening of USDA SR Legacy records and a separate broccoli processing study. These reference figures are not a paired experiment.'),
    ('P01-31', 'leafy-greens-cooked-folate', 'folate-in-cooked-spinach-turnip-greens-and-collards.html', 'How much folate is in cooked spinach, turnip greens and collards?',
     'Match boiled greens by weight and by a half-cup, then calculate the folate in a mixed side.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://ods.od.nih.gov/factsheets/Folate-HealthProfessional/'],
     'USDA SR Legacy. Boiled, drained and unsalted entries. Values refer to naturally occurring folate.'),
    ('P01-36', 'apple-peel-fiber', 'apple-fiber-with-peel-vs-peeled.html', 'How much apple fiber is left after peeling?',
     'Compare two raw USDA reference apples and separate the effect of a lower edible weight from a lower fiber concentration.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label'],
     'U.S. reference comparison. The two records are independent entries and do not trace a specific apple through peeling.'),
    ('P01-40', 'peaches-syrup-drained', 'fresh-peaches-vs-canned-in-heavy-syrup.html', 'Fresh peaches vs. canned peaches: how much does the syrup change?',
     'Compare fresh peach slices, heavy-syrup peaches and drained pieces at the same weight.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label'],
     'Specific U.S. USDA SR Legacy records. Added sugars are a separate label value and cannot be computed from these total sugars.'),
    ('P01-44', 'pumpkin-sunflower-kernels', 'pumpkin-seeds-vs-sunflower-seeds-magnesium-folate-selenium.html', 'Pumpkin or sunflower seeds? The answer changes with the nutrient',
     'Compare unsalted edible kernels by the ounce for magnesium, selenium and folate.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://ods.od.nih.gov/factsheets/Magnesium-HealthProfessional/',
      'https://ods.od.nih.gov/factsheets/Selenium-HealthProfessional/'],
     'U.S. USDA SR Legacy nutrient reference estimates. The comparison holds kernel weight constant.'),
    ('P02-13', 'tempeh-tofu-matched', 'tofu-vs-tempeh-protein-at-equal-weight.html', 'Tofu vs. tempeh: how much of each gives 20 g of protein?',
     'Compare equal weights first, then work backwards from the same protein amount to a portion.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'USDA SR Legacy reference entries for raw firm calcium-set tofu and cooked tempeh. The preparation states differ.'),
    ('P02-16', 'white-beans-chickpeas-soup', 'white-beans-vs-chickpeas-protein-in-soup.html', 'Do white beans and chickpeas add the same protein to a soup?',
     'Calculate the protein added per bowl using either a measured cup or the same weighed amount of beans.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'U.S. USDA SR Legacy prepared bean references. The soup example estimates only the bean contribution.'),
    ('P05-38', 'informed-sport-lot', 'informed-sport-check-a-supplement-batch.html', 'How do you check whether an Informed Sport supplement batch was tested?',
     'Match the lot, flavor and formulation, and see what a banned-substance screen establishes.',
     ['https://sport.wetestyoutrust.com/about/certification-process',
      'https://sport.wetestyoutrust.com/education/athletes',
      'https://www.sportintegrity.gov.au/what-we-do/anti-doping/substances/supplements-sport'],
     'Scope of the named certification program and public anti-doping guidance. Testing lowers risk but does not guarantee safety.'),
    ('P05-39', 'fda-supplement-adverse-report', 'report-a-supplement-reaction-to-fda.html', 'How does reporting a suspected supplement reaction to the FDA work?',
     'Find the reporting route and see why the reports cannot tell you how common a reaction is.',
     ['https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements',
      'https://www.fda.gov/food/compliance-enforcement-food/human-foods-complaint-system-hfcs',
      'https://open.fda.gov/apis/food/event/understanding-the-api-results/'],
     'U.S. regulatory reporting information, using an invented example and the FDA’s explanation of its public data limitations.'),
    ('P05-41', 'canada-npn-label', 'canada-npn-vs-us-supplement-facts.html', 'What does a Canadian NPN actually tell you about a supplement?',
     'Look up an actual natural health product number and compare it with the information on a U.S. supplement label.',
     ['https://health-products.canada.ca/lnhpd-bdpsnh/?lang=eng',
      'https://health-products.canada.ca/lnhpd-bdpsnh/info?lang=eng&licence=80005581',
      'https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements'],
     'Canadian and U.S. regulatory labeling literacy. Uses one actual licensed record without making a product recommendation.'),
    ('P05-42', 'australia-artg-supplement', 'australia-supplement-artg-aust-number.html', 'How do you check a supplement’s AUST number in Australia?',
     'Find a named example in the ARTG and distinguish the three prefixes on medicine labels.',
     ['https://www.tga.gov.au/resources/artg',
      'https://www.tga.gov.au/products/medicines/labelling-and-advertising/medicines-and-biologicals-labelling-and-packaging/aust-numbers-medicine-labels',
      'https://www.tga.gov.au/resources/artg/318912',
      'https://www.tga.gov.au/resources/artg/136142'],
     'Australian regulatory literacy. Some products are regulated as foods rather than as medicines.'),
    ('P03-07', 'caffeine-cortisol-trial', 'caffeine-and-cortisol-what-the-trial-measured.html', 'Does caffeine raise cortisol after you get used to it?',
     'Read a crossover study that separated prior caffeine exposure, morning response and later samples.',
     ['https://pmc.ncbi.nlm.nih.gov/articles/PMC2257922/',
      'https://pubmed.ncbi.nlm.nih.gov/16204431/'],
     'Controlled capsule study in healthy adults. Results describe a biochemical outcome, not a prescribed intake.'),
    ('P03-09', 'sleep-loss-evening-cortisol', 'one-night-sleep-loss-next-evening-cortisol.html', 'When did cortisol change after one night of lost sleep?',
     'Compare a normal night, a curtailed night and no sleep in the actual window the experiment measured.',
     ['https://pubmed.ncbi.nlm.nih.gov/9415946/'],
     'One controlled lab protocol in young men. Estimates are comparisons between two measurement days.'),
    ('P03-15', 'ten-thirty-minute-nap', 'ten-vs-thirty-minute-nap-study.html', '10-minute vs. 30-minute naps: why the timing of the test matters',
     'Compare the first hour after two naps and see what a study lasting across nights measured differently.',
     ['https://pubmed.ncbi.nlm.nih.gov/11322712/',
      'https://pubmed.ncbi.nlm.nih.gov/28934525/'],
     'Short-term performance research in small adult samples. Results do not establish individual sleep needs.'),
    ('P03-17', 'coffee-energy-caffeine-container', 'coffee-vs-energy-drink-caffeine-per-container.html', 'Does an energy drink have more caffeine than coffee? Check the container',
     'Compare U.S. drink ranges and the published amounts in three actual sizes of one energy drink.',
     ['https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much',
      'https://www.redbull.com/us-en/energydrink/questions/how-much-caffeine-is-in-a-can-of-red-bull-sugarfree'],
     'U.S. FDA ranges and Red Bull manufacturer figures for the named Sugarfree sizes. No personal caffeine recommendation.'),
    ('P03-43', 'presleep-protein-outcomes', 'protein-before-sleep-what-recovery-studies-measure.html', 'Protein before sleep: what does ‘recovery’ mean in these trials?',
     'Take a closer look at three trials that measured different rates during a single night after exercise.',
     ['https://pubmed.ncbi.nlm.nih.gov/22330017/',
      'https://pubmed.ncbi.nlm.nih.gov/28536184/',
      'https://pubmed.ncbi.nlm.nih.gov/36857005/'],
     'Interpretation of acute adult exercise experiments. The measured synthesis rates do not establish long-term effects or individual intake needs.'),
    ('P04-33', 'blinded-skin-grading', 'what-blinded-skin-assessment-means.html', 'What does a blinded skin assessment actually hide?',
     'Read how one Australian study separated treatment allocation from the graders who assessed skin texture.',
     ['https://pubmed.ncbi.nlm.nih.gov/23732711/'],
     'Evidence literacy using a published Australian factorial experiment. No treatment advice.'),
    ('P04-47', 'nofilter-tag-evidence', 'does-nofilter-prove-a-beauty-result.html', 'Does #NoFilter prove a beauty result is real?',
     'See what a UK advertising ruling evaluated and why an unfiltered image can still leave the cause untested.',
     ['https://www.asa.org.uk/advice-online/cosmetics-the-use-of-production-techniques.html',
      'https://www.asa.org.uk/rulings/charlotte-dawson-g22-1160111-charlotte-dawson.html'],
     'Media literacy using a named advertising ruling. The label is not a conclusion about any unreviewed post.'),
    ('P06-23', 'rice-volume-weight-log', 'cooked-rice-cup-vs-gram-food-diary.html', 'How many grams are in a cup of cooked rice for your food diary?',
     'Use the USDA’s reference cup and compare it with weighed scoops on the same cooked basis.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label'],
     'U.S. USDA SR Legacy reference for cooked long-grain white rice. The two home scoop weights are illustrative.'),
    ('P06-27', 'weigh-food-from-package', 'weigh-what-you-ate-from-the-package.html', 'How to weigh food you ate straight from the package',
     'Calculate what you removed by weighing the same package twice, then match the printed serving size.',
     ['https://www.fda.gov/files/food/published/Food-Labeling-Guide-(PDF).pdf',
      'https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label'],
     'Kitchen measurement using a fictional package and U.S. label serving principles.'),
    ('P06-29', 'package-as-prepared-dinner', 'as-packaged-vs-as-prepared-food-label.html', 'As packaged or as prepared? Which number belongs in your diary?',
     'Use a real boxed dinner example to identify ingredients already counted and ingredients added at home.',
     ['https://www.fda.gov/files/food/published/Food-Labeling-Guide-(PDF).pdf',
      'https://www.kraftheinz.com/kraft-mac-and-cheese/products/00021000658831-original-mac-cheese-macaroni-and-',
      'https://www.kraftheinz.com/kraft-mac-and-cheese/recipes/525138-kraft-macaroni-cheese-dinner'],
     'U.S. label terms, using a named manufacturer recipe and a separate illustrative nutrition calculation.'),
    ('P06-36', 'restaurant-meal-photo-evidence', 'restaurant-nutrition-from-photo-what-is-missing.html', 'Can you work out restaurant calories from a photo and ingredients list?',
     'See which exact portion, sauce and preparation facts a photo leaves out, using a published menu example.',
     ['https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/menu-labeling-requirements',
      'https://www.chick-fil-a.com/nutrition-allergens'],
     'U.S. published portions and FDA menu-labeling scope. The hypothetical photo has no inferred nutrition.'),
    ('P06-48', 'sauce-packet-grams', 'chick-fil-a-sauce-packets-calories-per-gram.html', 'Chick-fil-A sauces by packet and gram: which comparison answers your question?',
     'Read three different U.S. serving weights and compare what happens when you use one 12 g portion.',
     ['https://www.chick-fil-a.com/nutrition-allergens'],
     'Chick-fil-A U.S. published sauce portions. Equal-weight values are calculated estimates from rounded figures.'),
    ('P03-11', 'stress-cortisol-disagreement', 'why-stress-rating-and-cortisol-can-disagree.html', 'Why can a stress rating and cortisol reading disagree?',
     'Compare a participant’s reported experience with timed cortisol samples before and after a lab task.',
     ['https://pubmed.ncbi.nlm.nih.gov/23246327/'],
     'Research literacy from a timed lab experiment. The measures are not substitutes for a clinical assessment.'),
    ('P04-08', 'facial-roller-blood-flow', 'facial-roller-blood-flow-what-studies-measure.html', 'What does a facial roller study measure besides appearance?',
     'Compare the short-lived blood flow finding with a separate test of response to warmth after weeks of use.',
     ['https://pubmed.ncbi.nlm.nih.gov/30477852/'],
     'Two measured outcomes from one small Japanese study. No claim about permanent structure or treatment effect.'),
    ('P04-29', 'milk-acne-questionnaires', 'milk-and-acne-questionnaire-study-meaning.html', 'What can milk-and-acne questionnaires actually tell you?',
     'Read two large cohort comparisons with the same skim-milk result and check what they measured separately.',
     ['https://pubmed.ncbi.nlm.nih.gov/18194824/',
      'https://pubmed.ncbi.nlm.nih.gov/17083856/'],
     'Interpretation of two observational adolescent cohorts. No personal diet, treatment or diagnosis guidance.'),
    ('P04-30', 'whey-acne-trial-designs', 'whey-and-acne-why-two-studies-differ.html', 'Whey and acne: why a survey and a trial can give different answers',
     'Compare how two 2024 studies chose participants and what each design could learn.',
     ['https://pubmed.ncbi.nlm.nih.gov/38291989/',
      'https://pubmed.ncbi.nlm.nih.gov/38633058/'],
     'Study interpretation only. The compared products, participant groups and outcomes do not establish individual recommendations.'),
]
# The source IDs refer to the already retained USDA reference shards.
FOODS = {
    'Fruit & vegetables': {171688:'Raw apple with skin', 173944:'Raw banana', 169097:'Raw orange',
      170457:'Raw tomato', 169967:'Boiled broccoli, drained, no salt',
      168463:'Boiled spinach, drained, no salt', 170033:'Baked potato flesh, no salt'},
    'Legumes & grains': {173735:'Boiled black beans, no salt', 172421:'Boiled lentils, no salt',
      172475:'Firm tofu, calcium sulfate', 173904:'Dry oats, unfortified',
      173905:'Oats cooked in water, no salt'},
    'Nuts & seeds': {170158:'Dry roasted almonds, no salt', 170557:'Roasted pumpkin seed kernels, no salt'},
    'Dairy, eggs, meat & fish': {170886:'Plain low-fat yogurt', 173424:'Hard-boiled egg',
      171477:'Roasted chicken breast, meat only', 175139:'Atlantic sardines, oil-packed, drained with bones'},
}
NUTRIENTS = ('magnesium', 'potassium', 'calcium', 'iron', 'zinc', 'selenium', 'vitaminC',
             'vitaminB12', 'vitaminA', 'vitaminD', 'vitaminE', 'vitaminK', 'folate', 'p', 'f')
SOURCE_TITLES = {
    FDC_DATA: 'USDA FoodData Central: SR Legacy reference dataset downloads',
    ODS.format('Magnesium'): 'NIH Office of Dietary Supplements: Magnesium, selected foods and U.S. label rules',
    ODS.format('Choline'): 'NIH Office of Dietary Supplements: Choline, Table 2',
    ODS.format('Potassium'): 'NIH Office of Dietary Supplements: Potassium, Table 2',
    ODS.format('Folate'): 'NIH Office of Dietary Supplements: Folate, folic acid and dietary folate equivalents',
    ODS.format('Zinc'): 'NIH Office of Dietary Supplements: Zinc sources, Table 2 and absorption',
    ODS.format('VitaminK'): 'NIH Office of Dietary Supplements: Vitamin K in foods, Table 2 and medication interactions',
    ODS.format('VitaminD'): 'NIH Office of Dietary Supplements: Vitamin D in foods and fortified products, Table 3',
    'https://www.fda.gov/consumers/consumer-updates/spilling-beans-how-much-caffeine-too-much': 'FDA: Caffeine in common beverages and decaffeinated coffee',
    'https://academic.oup.com/jat/article-abstract/30/8/611/714415': 'McCusker et al. (2006): Caffeine content of decaffeinated coffee',
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC12121324/': 'Ahn et al. (2025): Facial roller versus gua sha randomized trial',
    'https://pubmed.ncbi.nlm.nih.gov/24235903/': 'Drake et al. (2013): Caffeine at bedtime or 3 or 6 hours earlier',
    'https://pubmed.ncbi.nlm.nih.gov/39377163/': 'Gardiner et al. (2025): Caffeine dose and timing crossover trial',
    'https://pubmed.ncbi.nlm.nih.gov/17616769/': 'Smith et al. (2007): Low-glycemic-load diet and acne trial',
    'https://www.aad.org/news/updated-guidelines-acne-management': 'American Academy of Dermatology: Evidence in the updated acne guidelines',
    'https://www.fda.gov/food/buy-store-serve-safe-food/raw-milk-questions-answers': 'FDA: Raw milk and pasteurization questions and answers',
    'https://www.canada.ca/en/health-canada/services/milk-infant-formula/raw-or-unpasteurized-milk.html': 'Health Canada: Raw or unpasteurized milk ',
    'https://www.fda.gov/food/information-consumers-using-dietary-supplements/questions-and-answers-dietary-supplements': 'FDA: U.S. supplement labels, blend disclosures and regulation',
}


def public_articles():
    return [row for row in ARTICLES if row[1] != 'acne']


def replace_section(text, section_id, replacement):
    node = next((node for node in Document(text).nodes if node['attrs'].get('id') == section_id), None)
    if node:
        return text[:node['start']] + replacement + text[node['end']:]
    main = next(node for node in Document(text).nodes if node['tag'] == 'main')
    return text[:main['close']] + replacement + text[main['close']:]


def projection():
    library = ROOT / 'data/food-library'
    fields = json.loads((library / 'manifest.json').read_bytes())['fields']
    index = {row['id']: row for row in json.loads((library / 'index.json').read_bytes())}
    rows = []
    for group, foods in FOODS.items():
        for source_id, label in foods.items():
            id_ = f'fdc:{source_id}'
            shard = index[id_]['shard']
            data = json.loads((library / 'records' / f'{shard}.json').read_bytes())
            record = next(row for row in data if row['id'] == id_)
            assert record['basis'] == {'amount': 100, 'unit': 'g'} and record['market'] == 'US-reference'
            portions = record.get('portions', [])
            portion = next((p for p in portions if p['label'] == '1 oz' and p['grams'] > 0),
                           next((p for p in portions if p['grams'] > 0), None))
            rows.append(dict(id=source_id, label=label, name=record['name'], group=group, portion=portion,
                             values={key: record['nutrients'].get(key) for key in (*NUTRIENTS, 'cal', 'na')}))
    return dict(rows=rows, nutrients={key: fields[key] for key in NUTRIENTS}, source=FDC_DATA)


def shell(slug, title, summary, main, schema=None, *, private=False):
    # Reuse the retained shared header, theme, footer and reading styles.
    template = (ROOT / 'how-to-read-a-nutrition-label.html').read_text(encoding='utf8')
    doc = Document(template)
    node = next(n for n in doc.nodes if n['tag'] == 'main')
    page = template[:node['start']] + main + template[node['end']:]
    # The source guide has a save-to-shelf control inside its main content.
    # That control is not part of the wellness article or tool template.
    unused_assets = []
    for asset in Document(page).nodes:
        attributes = asset['attrs']
        path = attributes.get('data-source-path') or attributes.get('href') or attributes.get('src') or ''
        if asset['tag'] in ('link', 'script') and path.split('?', 1)[0].lstrip('/') in ('css/food-shelf.css', 'js/food-shelf.js'):
            unused_assets.append(asset)
    for asset in reversed(unused_assets):
        page = page[:asset['start']] + page[asset['end']:]
    url = HOST + '/' + slug
    full_title = title + ' | GetMacros'
    page = re.sub(r'<title>.*?</title>', lambda _: '<title>' + escape(full_title) + '</title>', page, count=1, flags=re.S)
    page = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{url}">', page)
    page = re.sub(r'<link\b[^>]*hreflang="[^"]*"[^>]*>', '', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>', '', page, flags=re.S)
    for field, value in {'description':summary, 'og:description':summary, 'twitter:description':summary,
                        'og:title':full_title, 'twitter:title':full_title, 'og:url':url}.items():
        page = re.sub(r'(<meta (?:name|property)="' + re.escape(field) + r'" content=")[^"]*',
                      lambda match: match[1] + escape(value, quote=True), page)
    if private:
        page = re.sub(r'(<meta name="robots" content=")[^"]*', r'\1noindex, nofollow', page)
    if schema and not private:
        breadcrumb = {'@type':'BreadcrumbList', 'itemListElement':[
            {'@type':'ListItem', 'position':1, 'name':'Guides', 'item':HOST + '/articles.html'},
            {'@type':'ListItem', 'position':2, 'name':title, 'item':url}]}
        data = {'@context':'https://schema.org', '@graph':[schema | {'url':url}, breadcrumb]}
        page = page.replace('</head>', '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=True) +
                            '</script></head>', 1)
    return page


STUDIO_FIELDS = [('cal', 'Energy', 'kcal'), ('p', 'Protein', 'g'),
                 ('f', 'Fiber', 'g'), ('na', 'Sodium', 'mg')]


def studio_pairs(data):
    us = {row['id']: row for row in registry_market('US') if 'id' in row}
    ca = {row['id']: row for row in registry_market('CA') if 'id' in row}
    foods = {row['id']: row for row in data['rows']}
    nutrients = [key for key, *_ in STUDIO_FIELDS]

    def order(label, portion, *parts):
        reference_ids = [part['referenceId'] for part in parts if 'referenceId' in part]
        return dict(label=label, portion=portion,
                    values={key: sum(part[key] for part in parts)
                            if all(part.get(key) is not None for part in parts) else None
                            for key in nutrients},
                    grams=sum(part['servingGrams'] for part in parts)
                          if all(part.get('servingGrams') for part in parts) else None,
                    sources=list(dict.fromkeys(part['source'] for part in parts)),
                    referenceIds=reference_ids)

    def portion(food_id, grams):
        row = foods[food_id]
        return dict({key: row['values'][key] * grams / 100 if key in row['values'] and row['values'][key] is not None else None
                     for key in nutrients},
                    servingGrams=grams, source=FDC_DATA, referenceId=food_id)

    nuggets = us['cfa-us-10318-d9cc8c5b']
    fruit = us['cfa-us-10209-577b0041']
    fries = us['cfa-us-10338-29c625a3']
    oats = portion(173905, 150)
    yogurt = portion(170886, 100)
    pizza = ca['CA|pizza-nova|136e7ef92aa95020']
    return [
        dict(name='Chick-fil-A · Fruit vs. fries',
             guide='/chick-fil-a-fruit-cup-vs-waffle-fries-order.html',
             note='Calculated from published U.S. portions. Both orders have 8 nuggets. Sauces and drinks are separate.',
             sides=[order('Nuggets and fruit', '8 nuggets and a small fruit cup', nuggets, fruit),
                    order('Nuggets and fries', '8 nuggets and small waffle fries', nuggets, fries)]),
        dict(name='At home · Oats and yogurt',
             guide='/food-diary.html',
             note='Recipe example using USDA reference values. The second bowl adds plain low-fat yogurt to the same amount of cooked oats.',
             sides=[order('Cooked oats', '150 g oats cooked in water', oats),
                    order('Oats with yogurt', '150 g cooked oats and 100 g yogurt', oats, yogurt)]),
        dict(name='Pizza Nova · One or two slices',
             guide='/ca/en/restaurants/pizza-nova/',
             note='This Canadian in-store Doppio Pepperoni slice listing has calories only. The two-slice result doubles the listed portion.',
             sides=[order('One slice', '1 in-store slice', pizza),
                    order('Two slices', '2 in-store slices', pizza, pizza)]),
    ]


def studio_section(data):
    pairs = studio_pairs(data)
    options = ''.join(f'<option value="{index}">{escape(pair["name"])}</option>' for index, pair in enumerate(pairs))
    payload = json.dumps(dict(pairs=pairs, fields=STUDIO_FIELDS), ensure_ascii=True,
                         separators=(',', ':')).replace('<', '\\u003c')
    return f'''<section id="food-comparison-studio" data-food-studio aria-labelledby="food-studio-title">
<h2 id="food-studio-title">Food Comparison Studio</h2>
<p>Swap a restaurant side, add an ingredient to breakfast, or compare two portions of the same item.</p>
<form class="form-grid" hidden>
<div><label for="food-studio-example">Comparison</label><select id="food-studio-example" name="example">{options}</select></div>
<div><label for="food-studio-basis">Compare by</label><select id="food-studio-basis" name="basis"><option value="portion">Listed amount</option><option value="100g">100 g</option><option value="100kcal">100 kcal</option></select></div>
</form>
<noscript><p>Enable JavaScript for the interactive table, or read <a href="/chick-fil-a-fruit-cup-vs-waffle-fries-order.html">the full side comparison</a>.</p></noscript>
<p data-studio-note role="status"></p>
<div class="table-wrap" role="region" aria-label="Food comparison results" tabindex="0" hidden><table>
<caption>Amounts for both choices</caption>
<thead><tr><th scope="col">Measure</th><th scope="col" data-studio-food></th><th scope="col" data-studio-food></th></tr></thead>
<tbody></tbody></table></div>
<p><a data-studio-guide hidden>Open the related guide or tool</a></p>
<script type="application/json">{payload}</script></section>'''


def explorer_page(data, script_url):
    def options(values, selected=None):
        return ''.join(f'<option value="{escape(key, quote=True)}"{" selected" if key == selected else ""}>{escape(label)}</option>'
                       for key, label in values)
    rows = sorted(data['rows'], key=lambda row: row['values']['magnesium'] if row['values']['magnesium'] is not None else -1, reverse=True)
    initial = ''.join('<tr><th scope="row">' + escape(row['label']) + '</th><td>100 g</td><td>' +
                      (str(row['values']['magnesium']) + ' mg' if row['values']['magnesium'] is not None else 'Unknown') +
                      f'</td><td><a href="{FDC_DATA}">USDA data ({row["id"]})</a></td></tr>' for row in rows)
    summary = f'Compare {len(rows)} USDA reference foods by vitamins, minerals, protein or fiber per 100 g, per portion or per 100 calories.'
    nutrient_options = options((key, value['label']) for key, value in data['nutrients'].items())
    category_options = options((name, name) for name in FOODS)
    food_options = sorted(((str(row['id']),row['label']) for row in data['rows']), key=lambda row: row[1].casefold())
    payload = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    main = f'''<main id="main-content" class="container"><article class="article-container release-article">
<nav aria-label="Breadcrumb"><a href="/articles.html">Guides</a></nav>
<h1>Nutrient Density Explorer</h1><p>{escape(summary)}</p>
<p><a href="#compare-protein-and-fiber" data-macro-pair-link hidden>Compare protein and fiber side by side</a> · <a href="#food-comparison-studio">Compare a dish or order</a></p>
<section data-nutrient-explorer aria-label="Food nutrient comparison">
<form class="form-grid" hidden>
<div><label for="explorer-nutrient">Nutrient</label> <select id="explorer-nutrient" name="nutrient">{nutrient_options}</select></div>
<div><label for="explorer-basis">Compare by</label> <select id="explorer-basis" name="basis"><option value="100g">100 g</option><option value="portion">Listed portion</option><option value="100kcal">100 kcal</option></select></div>
<div><label for="explorer-category">Food category</label> <select id="explorer-category" name="category"><option value="">All categories</option>{category_options}</select></div>
<div><label for="explorer-food">Find a food</label> <input id="explorer-food" type="search" name="food" placeholder="e.g. black beans"></div>
<label><input type="checkbox" name="unknown" checked> Include unknown values</label>
</form>
<p role="status"></p><noscript><p>Magnesium per 100 g is shown below. Enable JavaScript to change nutrients and portions.</p></noscript>
<div class="table-wrap" role="region" aria-label="Food nutrient values" tabindex="0"><table>
<caption>Selected USDA SR Legacy reference foods</caption>
<thead><tr><th scope="col">Food</th><th scope="col">Amount of food</th><th scope="col" data-amount-label>Magnesium per 100 g</th><th scope="col">Source</th></tr></thead>
<tbody>{initial}</tbody></table></div>
<section id="compare-protein-and-fiber" data-macro-pair hidden aria-labelledby="macro-pair-title">
<h2 id="macro-pair-title">Compare protein and fiber in two foods</h2>
<form class="form-grid">
<div><label for="macro-pair-first">First food</label><select id="macro-pair-first" name="first">{options(food_options, '173735')}</select></div>
<div><label for="macro-pair-second">Second food</label><select id="macro-pair-second" name="second">{options(food_options, '173905')}</select></div>
<div><label for="macro-pair-basis">Protein and fiber basis</label><select id="macro-pair-basis" name="basis"><option value="100g">100 g</option><option value="portion">Listed portion</option><option value="100kcal">100 kcal</option></select></div>
</form>
<div class="table-wrap" role="region" aria-label="Protein and fiber comparison" tabindex="0"><table>
<caption>Protein and fiber in the selected foods</caption><thead><tr><th scope="col">Food and amount</th><th scope="col">Protein</th><th scope="col">Fiber</th></tr></thead>
<tbody aria-live="polite"></tbody></table></div></section>
<script type="application/json">{payload}</script></section>
{studio_section(data)}
<h2>How the amounts are calculated</h2>
<p>A listed portion uses a measure with a weight in the source. For 100 calories, the tool divides by the source energy per 100 g and multiplies by 100. A missing amount or unavailable conversion stays unknown. The results show total nutrient content, which can differ from the amount absorbed.</p>
<p>These are selected U.S. reference foods. Use the exact preparation and source when comparing your own meal. For choline examples, see the separate <a href="/choline-foods-eggs-soybeans-quinoa.html">egg, soybeans and quinoa comparison</a>.</p>
<p>The USDA source column gives the record ID and links to the SR Legacy download.</p>
<p><a href="/food-library.html">Search a larger set of reference and packaged foods</a> or <a href="/compare-foods.html">review exact portions side by side</a>.</p></article></main>'''
    page = shell(EXPLORER, 'Nutrient Density Explorer', summary, main)
    page = page.replace('data-family="article"', 'data-family="tool"', 1)
    page = page.replace('data-analytics-page="public"', 'data-analytics-page="off"', 1)
    page = page.replace('</head>', '''<style>
:is([data-nutrient-explorer],[data-food-studio]) form:not([hidden]){display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem 1rem;align-items:start}
:is([data-nutrient-explorer],[data-food-studio]) form>div{min-width:0}
:is([data-nutrient-explorer],[data-food-studio]) form>div>label{display:block;margin-bottom:.25rem}
:is([data-nutrient-explorer],[data-food-studio]) form :is(select,input[type="search"]){width:100%;min-inline-size:0;min-block-size:44px}
[data-nutrient-explorer] form>label{grid-column:1/-1}
:is([data-macro-pair],[data-food-studio]) table{min-width:0;width:100%}
:is([data-macro-pair],[data-food-studio]) th :is(small,a){display:block;font-weight:400}
[data-macro-pair] td{white-space:nowrap;font-variant-numeric:tabular-nums}
[data-food-studio] td{font-variant-numeric:tabular-nums}
@media(max-width:480px){:is([data-macro-pair],[data-food-studio]) form:not([hidden]){grid-template-columns:1fr}}
@media(max-width:350px){[data-nutrient-explorer] form:not([hidden]){grid-template-columns:1fr}}
</style></head>''', 1)
    return page.replace('</body>', f'<script src="{script_url}" data-source-path="js/nutrient-explorer.js" defer></script></body>', 1)


def article_page(row):
    id_, key, slug, title, summary, urls, scope = row
    pillar = PILLARS[int(id_[1:3]) - 1]
    body = (SOURCE / (key + '.html')).read_text(encoding='utf-8-sig').strip()
    if key == 'breakfast-fiber':
        body, restaurant_sources = breakfast_fiber(body)
        urls = list(dict.fromkeys([*urls, *restaurant_sources]))
    if key == 'uk-weight-coverage':
        body = uk_weight_coverage(body)
    if key == 'canada-sodium-coverage':
        body = canada_sodium_coverage(body)
    body = body.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    links = [{'url':'/' + EXPLORER, 'label':'Compare vitamins and minerals'}] if id_.startswith('P01') else []
    if key in ('raw-milk','supplement-label'):
        links.append({'url':'/how-to-read-a-nutrition-label.html', 'label':'Read a Nutrition Facts label'})
    if key == 'caffeine':
        links.append({'url':'/articles.html#learn-coffee-drinks', 'label':'Browse coffee and drink guides'})
    if key == 'cortisol-awakening':
        links.append({'url':'/caffeine-before-bed-dose-and-timing.html', 'label':'See how timing changes the comparison in caffeine research'})
    if key == 'peptide-labels':
        links.append({'url':'/read-supplement-facts-per-serving.html', 'label':'Read a Supplement Facts panel'})
    if key == 'gua-sha':
        links.append({'url':'/editorial-policy.html', 'label':'How GetMacros evaluates evidence'})
    if key in ('mogging-meaning','appearance-photo-evidence'):
        links.append({'url':'/gua-sha-jawline-what-study-measured.html', 'label':'See what a facial contour study measured'})
    if key == 'blue-zones-pattern':
        links.append({'url':'/' + EXPLORER + '#compare-protein-and-fiber', 'label':'Compare fiber in two reference foods'})
    if key in ('fruit-fries-order', 'beans-drained-recipe', 'canada-sodium-coverage', 'subway-nz-breakfast'):
        links.append({'url':'/' + STUDIO, 'label':'Compare a dish or order in the Food Comparison Studio'})
    if key == 'breakfast-fiber':
        links.extend([{'url':'/restaurant-meal-finder.html?meal=breakfast', 'label':'Browse U.S. breakfast records'},
                      {'url':'/exact-fiber-coverage-denominator.html', 'label':'Read a missing fiber value correctly'}])
    section_page, section_label, *_ = SECTIONS[int(id_[1:3]) - 1]
    links.append({'url':'/' + section_page, 'label':section_label})
    sources = 'Source material checked November 20, 2026. ' + scope
    main = resource_main(dict(slug=slug, title=title, h1=title, description=summary,
                              category=pillar, sourceURLs=urls, sourceScope=sources, body=body, related=links))
    for url in urls:
        label = SOURCE_TITLES.get(url)
        if label:
            main = re.sub(r'(<a href="' + re.escape(escape(url, quote=True)) + r'">)[^<]+',
                          lambda match: match[1] + escape(label.strip()), main)
    main = main.replace('By GetMacros · Published October 3, 2026', 'By GetMacros · Sources checked November 20, 2026')
    # The opening paragraph answers the question. Keep the summary in metadata.
    main = main.replace(f'<p>{escape(summary)}</p>', '', 1)
    if id_.startswith(('P03','P04','P05')):
        main = re.sub(r'<span data-food-character="[^"]+"[^>]*>.*?</span>', '', main, count=1, flags=re.S)
    private = key == 'acne'
    if private:
        main = main.replace('</h1>', '</h1><p>Draft for specialist review</p>', 1)
    schema = {'@type':'Article', 'headline':title, 'description':summary,
              'author':{'@type':'Organization', 'name':'GetMacros', 'url':HOST + '/about.html'}}
    if not private and id_ in PUBLICATION_DATES:
        published = date.fromisoformat(PUBLICATION_DATES[id_])
        display_date = f'{published:%B} {published.day}, {published.year}'
        schema['datePublished'] = published.isoformat()
        main = main.replace('By GetMacros · Sources checked November 20, 2026</p>',
                            'By GetMacros · Sources checked November 20, 2026</p>'
                            f'<p>Published <time datetime="{published}">{display_date}</time></p>', 1)
    return shell(slug, title, summary, main, schema, private=private)


def registry_market(market):
    return [row for row in json.loads((ROOT / 'js/order-registry.json').read_bytes())['records']
            if row['market'] == market]


def breakfast_fiber(body):
    rows = [row for row in registry_market('US') if row.get('meal') == 'breakfast']
    known = [row for row in rows if isinstance(row.get('f'), (int, float))]
    count = sum(row['f'] >= 3 for row in known)
    assert (len(rows), len(known), count) == (131, 131, 47), 'Review the breakfast snapshot before changing article counts.'
    counts = []
    for chain in sorted({row['chain'] for row in rows}):
        local = [row for row in rows if row['chain'] == chain]
        measured = [row for row in local if isinstance(row.get('f'), (int, float))]
        counts.append('<tr><th scope="row">' + escape(chain) + '</th><td>' + str(len(local)) +
                      '</td><td>' + str(len(measured)) + '</td><td>' +
                      str(sum(row['f'] >= 3 for row in measured)) + '</td></tr>')
    examples = {'Large Hash Browns': 6, '10 ct Chick-fil-A Chick-n-Minis®': 6,
                'Hash Brown Scramble Burrito w/ No Meat': 5}
    for name, amount in examples.items():
        assert any(row['name'] == name and row['f'] == amount for row in known)
    return body.replace('<!--CHAIN_ROWS-->', ''.join(counts)), sorted({row['source'] for row in rows})


def coverage_row(name, *counts):
    return f'<tr><th scope="row">{escape(name)}</th>' + ''.join(f'<td>{count:,}</td>' for count in counts) + '</tr>'


def uk_weight_coverage(body):
    rows = registry_market('GB')
    counts = []
    eligible = 0
    for chain in sorted({row['chain'] for row in rows}):
        local = [row for row in rows if row['chain'] == chain]
        mass = [row for row in local if isinstance(row.get('servingGrams'), (int, float)) and row['servingGrams'] > 0]
        calories = sum(isinstance(row.get('cal'), (int, float)) for row in mass)
        counts.append(coverage_row(chain, len(local), len(mass), calories))
        eligible += calories
    assert rows and 0 < eligible < len(rows)
    return (body.replace('<!--CHAIN_ROWS-->', ''.join(counts))
            .replace('<!--ELIGIBLE-->', f'{eligible:,}').replace('<!--TOTAL-->', f'{len(rows):,}')
            .replace('<!--SHARE-->', f'{eligible / len(rows):.1%}'))


def canada_sodium_coverage(body):
    rows = registry_market('CA')
    counts = []
    missing = 0
    for chain in sorted({row['chain'] for row in rows}):
        local = [row for row in rows if row['chain'] == chain]
        known = [row for row in local if isinstance(row.get('na'), (int, float))]
        zero = sum(row['na'] == 0 for row in known)
        blank = len(local) - len(known)
        counts.append(coverage_row(chain, len(local), len(known), zero, blank))
        missing += blank
    assert rows and 0 < missing < len(rows)
    return (body.replace('<!--CHAIN_ROWS-->', ''.join(counts))
            .replace('<!--MISSING-->', f'{missing:,}').replace('<!--TOTAL-->', f'{len(rows):,}'))


def claim_library_page(script_url):
    claims = [
        ('Food safety', 'Does raw milk have a nutritional advantage?',
         'FDA and Health Canada describe the nutrient profiles of raw and pasteurized milk as similar.',
         'Different fat levels and fortification can change the figures on a carton. The nutrient panel cannot measure the risk of harmful microbes.',
         'is-raw-milk-more-nutritious.html', 'raw-milk'),
        ('Recovery', 'Is there a universal caffeine cutoff for sleep?',
         'Two controlled trials observed sleep disruption after a 400 mg dose.',
         'The smaller-dose trial used a narrow sample. Dose, bedtime and the drink’s actual caffeine are separate questions.',
         'caffeine-before-bed-dose-and-timing.html', 'caffeine'),
        ('Appearance', 'Does gua sha permanently change the jawline?',
         'A small randomized comparison measured changes in distances along the surface of the face.',
         'The study measured neither jawbone change nor persistence after the intervention. It compared two tools without a no-massage group.',
         'gua-sha-jawline-what-study-measured.html', 'gua-sha'),
        ('Supplements', 'Does a U.S. Supplement Facts panel establish FDA approval?',
         'The panel gives the declared serving and ingredient amounts under U.S. labeling rules.',
         'The FDA generally does not approve supplements for safety or effectiveness before sale. An ingredient amount and evidence for a product claim answer separate questions.',
         'read-supplement-facts-per-serving.html', 'supplement-label'),
        ('Recovery', 'Can a food detox cortisol?',
         'Controlled meal studies can measure short-term cortisol changes. One measured a post-meal increase.',
         'An immediate result does not establish a lasting effect or treatment for a hormone disorder.',
         'cortisol-detox-food-what-studies-measure.html', 'cortisol-detox-food'),
        ('Supplements', 'Does “peptide” tell you whether a product works?',
         'The term describes a group of molecules. A food ingredient and a drug can both contain peptides.',
         'Evidence applies to the named product, preparation and outcome. Do not transfer a drug’s results to a supplement or experimental product.',
         'collagen-peptides-vs-peptide-drugs.html', 'peptide-labels'),
    ]
    sources = {row[1]: row[5][0] for row in public_articles()}
    entries = ''.join(
        f'<section data-claim-example data-topic="{escape(topic, quote=True)}"><h2>{escape(question)}</h2>'
        f'<dl><dt>What the evidence supports</dt><dd>{escape(finding)}</dd>'
        f'<dt>What remains uncertain</dt><dd>{escape(limit)}</dd></dl><p>'
        f'<a href="/{slug}">Read the evidence guide</a> · <a href="{escape(sources[key], quote=True)}">Primary source</a></p></section>'
        for topic, question, finding, limit, slug, key in claims)
    summary = 'Check claims about food, cortisol, skincare and supplements against their primary sources.'
    choices = ''.join(f'<option>{escape(topic)}</option>' for topic in dict.fromkeys(entry[0] for entry in claims))
    main = f'''<main id="main-content" class="container"><article class="article-container release-article" data-claim-library>
<nav aria-label="Breadcrumb"><a href="/articles.html">Guides</a></nav>
<h1>Wellness Claim Evidence Library</h1><p>{summary}</p>
<form class="form-grid" hidden><div><label for="claim-query">Search claims</label> <input id="claim-query" type="search" name="claim"></div>
<div><label for="claim-topic">Topic</label> <select id="claim-topic" name="topic"><option value="">All topics</option>{choices}</select></div></form>
<p role="status"></p>{entries}<p><a href="/editorial-policy.html">GetMacros editorial and sourcing policy</a></p></article></main>'''
    page = shell(CLAIM_LIBRARY, 'Wellness Claim Evidence Library', summary, main)
    return page.replace('</body>', f'<script src="{script_url}" data-source-path="js/nutrient-explorer.js" defer></script></body>', 1)


def guide_topic(row):
    id_, key, *_ = row
    pillar = int(id_[1:3])
    if pillar == 1:
        if key in ('folate', 'niacin-equivalents'):
            return 'Reading nutrient values'
        return 'Vitamins in food' if key.startswith(('vitamin-', 'b12-')) else 'Minerals and choline'
    if pillar == 2:
        if key in ('carnivore-survey-evidence', 'saladino-frameworks', 'blue-zones-pattern', 'blue-diet-meaning',
                   'santa-cruz-hydration-claim', 'predimed-trial-reanalysis', 'mediterranean-snack-vs-pattern'):
            return 'Diet and product claims'
        return 'Food comparisons'
    if pillar == 3:
        if 'cortisol-' in key:
            return 'Stress measurements'
        return 'Exercise recovery' if key in ('infrared-sauna', 'cold-water-lifting') else 'Sleep and timing'
    if pillar == 4:
        if key in ('looksmaxxing-context', 'mogging-meaning', 'hypergamy-measure', 'softmaxxing-hardmaxxing'):
            return 'Online terms'
        return 'Marketing claims' if key in ('sponsored-beauty-posts', 'clinical-grade-labels') else 'Appearance research'
    if pillar == 5:
        if key in ('peptide-labels', 'bpc-regulatory-context'):
            return 'Peptides and policy'
        return 'Ingredient studies' if key in ('creatine-hair', 'magnesium-form-study') else 'Reading supplement labels'
    if key in ('breakfast-fiber', 'uk-weight-coverage', 'canada-sodium-coverage'):
        return 'GetMacros data studies'
    return 'Diary calculations' if 'rounding' in key or key == 'uk-menu-salt-sodium' else 'Restaurant comparisons'


def section_page(index, items, script_url):
    slug, label, intro, character, feature, tool_link, tool_label = SECTIONS[index]
    featured = next((row for row in items if row[0] == feature), items[0])
    topics = sorted({guide_topic(row) for row in items})
    choices = ''.join(f'<option>{escape(topic)}</option>' for topic in topics)
    guides = ''.join(f'<li data-guide-topic="{escape(guide_topic(row), quote=True)}">'
                     f'<a href="/{row[2]}">{escape(row[3])}</a><p>{escape(row[4])}</p></li>' for row in items)
    section_links = ''.join(f'<li><a href="/{route}">{escape(name)}</a></li>'
                            for route,name,*_ in SECTIONS if route != slug)
    related = '<p><a href="/high-protein-foods-list.html">See the high-protein foods list</a></p>' if index == 1 else ''
    main = f'''<main id="main-content" class="container"><article class="article-container release-article">
<nav aria-label="Breadcrumb"><a href="/articles.html#wellness-publication">Guides</a></nav>
<div class="wellness-pillar-intro"><div><h1>{escape(PILLARS[index])}</h1><p>{escape(intro)}</p></div>
<svg viewBox="0 0 160 160" aria-hidden="true" focusable="false"><use href="/images/food-characters.svg#food-{character}"></use></svg></div>
<section class="wellness-pillar-feature"><h2>Start here</h2><a href="/{featured[2]}">{escape(featured[3])}</a>
<p>{escape(featured[4])}</p><a href="/{tool_link}">{escape(tool_label)}</a>{related}</section>
<section data-pillar-guides><h2>Browse {escape(label.lower())}</h2>
<form hidden class="wellness-pillar-filters"><div><label for="pillar-query">Search this collection</label><input type="search" id="pillar-query" name="query"></div>
<div><label for="pillar-topic">Topic</label><select id="pillar-topic" name="topic"><option value="">All topics</option>{choices}</select></div></form>
<p role="status"></p><ul class="wellness-pillar-guides">{guides}</ul></section>
<nav aria-label="Other guide collections"><h2>More collections</h2><ul>{section_links}</ul></nav>
</article></main>'''
    page = shell(slug, PILLARS[index], intro, main, {'@type':'CollectionPage','name':PILLARS[index],'description':intro})
    page = page.replace('</head>', '''<style>
.wellness-pillar-intro{display:grid;grid-template-columns:minmax(0,1fr) clamp(4rem,15vw,8rem);gap:1rem;align-items:center}
.wellness-pillar-intro svg{width:100%;height:auto}
.wellness-pillar-feature{margin-block:1.5rem;padding:1.25rem;border-inline-start:.25rem solid var(--green);background:var(--surface);border-radius:.6rem}
.wellness-pillar-filters:not([hidden]){display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:1rem}
.wellness-pillar-filters label{display:block;margin-block-end:.35rem;font-weight:600}
.wellness-pillar-filters :is(input,select){width:100%;min-inline-size:0;min-block-size:44px}
.wellness-pillar-guides{list-style:none;padding:0}
.wellness-pillar-guides li{padding:1rem 0;border-block-end:1px solid var(--line)}
.wellness-pillar-guides li p{margin:.35rem 0 0}
@media(max-width:480px){.wellness-pillar-filters:not([hidden]){grid-template-columns:1fr}.wellness-pillar-intro{grid-template-columns:1fr}.wellness-pillar-intro svg{display:none}}
</style></head>''', 1)
    return page.replace('</body>', f'<script src="{script_url}" data-source-path="js/nutrient-explorer.js" defer></script></body>', 1)


def apply():
    for row in ARTICLES:
        parent = DOCS if row[1] == 'acne' else ROOT
        if parent == DOCS and not (SOURCE / (row[1] + '.html')).exists():
            continue
        (parent / row[2]).write_text(article_page(row), encoding='utf8', newline='\n')
    assets = ROOT / 'assets/generated'
    registry = assets / 'manifest.json'
    entries = json.loads(registry.read_bytes())
    key = 'js/nutrient-explorer.js'
    script = (ROOT / key).read_bytes().replace(b'\r\n', b'\n')
    digest = hashlib.sha256(script).hexdigest()
    url = '/assets/generated/js-nutrient-explorer-' + digest[:12] + '.js'
    (ROOT / url.lstrip('/')).write_bytes(script)
    entries[key] = dict(url=url, assetSha256=digest, sourceSha256=digest)
    registry.write_text(json.dumps(entries, indent=2) + '\n', encoding='utf8', newline='\n')
    (ROOT / EXPLORER).write_text(explorer_page(projection(), url), encoding='utf8', newline='\n')
    (ROOT / CLAIM_LIBRARY).write_text(claim_library_page(url), encoding='utf8', newline='\n')

    # Own one crawlable discovery section. The legacy library remains available below it.
    public = public_articles()
    cards = []
    for index, pillar in enumerate(PILLARS, 1):
        items = [r for r in public if r[0].startswith(f'P{index:02d}')]
        route, label, intro, _, feature, *_ = SECTIONS[index - 1]
        (ROOT / route).write_text(section_page(index - 1, items, url), encoding='utf8', newline='\n')
        featured = next((row for row in items if row[0] == feature), items[0])
        cards.append(f'<section><h3><a href="/{route}">{escape(label)}</a></h3><p>{escape(intro)}</p>'
                     f'<a href="/{featured[2]}">{escape(featured[3])}</a></section>')
    articles = ROOT / 'articles.html'
    text = articles.read_text(encoding='utf8')
    text = replace_section(text, 'wellness-publication', '')
    main = next(n for n in Document(text).nodes if n['tag'] == 'main')
    section = ('<section id="wellness-publication"><style>#wellness-publication{margin-block:2rem 3rem}'
               '#wellness-publication .wellness-topics{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr));gap:1.25rem 2rem}'
               '#wellness-publication .wellness-topics section{border-top:1px solid var(--line);padding-block-start:.85rem}'
               '#wellness-publication h3{font-size:1.1rem;margin-block:0 .65rem}'
               '#wellness-publication li{margin-block:.45rem}</style>'
               '<h2>Explore food and wellness</h2><p><a href="/' + CLAIM_LIBRARY +
               '">Check the evidence behind a wellness claim</a> · <a href="/' + EXPLORER +
               '">Explore nutrients in 18 reference foods</a></p><div class="wellness-topics">' + ''.join(cards) + '</div></section>')
    # Put new topics after the existing masthead and before the guide controls.
    tree = Document(text)
    library = next((n for n in tree.nodes if 'reader-library' in n['attrs'].get('class', '').split()), None)
    features = next((n for n in tree.nodes if 'editorial-features' in n['attrs'].get('class', '').split()), None)
    at = library['start'] if library else features['end'] if features else main['close']
    articles.write_text(text[:at] + section + text[at:], encoding='utf8', newline='\n')

    search = ROOT / 'search.html'
    hits = []
    resources = [(EXPLORER, 'Nutrient Density Explorer', 'Compare vitamins, minerals, protein or fiber.'),
                 (CLAIM_LIBRARY, 'Wellness Claim Evidence Library', 'Check claims against primary evidence.')]
    resources.extend((route, PILLARS[index], intro) for index,(route, _, intro,*_) in enumerate(SECTIONS))
    for slug, title, summary in [(r[2], r[3], r[4]) for r in public] + resources:
        hits.append(f'<a class="search-hit" href="/{slug}" data-search="{escape(title + " " + summary, quote=True)}"><span class="search-hit-name">{escape(title)}</span><span class="search-hit-copy">{escape(summary)}</span></a>')
    search.write_text(replace_section(search.read_text(encoding='utf8'), 'wellness-search',
        f'<section class="search-group" data-group id="wellness-search"><h2>Food and wellness <span data-count>{len(hits)}</span></h2><div class="search-hits">{"".join(hits)}</div></section>'), encoding='utf8', newline='\n')

    density_guide = ROOT / 'fiber-per-portion-vs-density.html'
    link = ('<section id="explore-source-foods"><h2>Try it with USDA food records</h2>'
            '<p>To see how a listed portion changes a comparison, choose Fiber in the '
            f'<a href="/{EXPLORER}">Nutrient Density Explorer</a> and switch between 100 g and Listed portion.</p></section>')
    density_guide.write_text(replace_section(density_guide.read_text(encoding='utf8'),
                             'explore-source-foods', link), encoding='utf8', newline='\n')

    sitemap = ROOT / 'sitemap.xml'
    text = sitemap.read_text(encoding='utf8')
    new = []
    for route in [r[2] for r in public] + [resource[0] for resource in resources]:
        loc = f'<loc>{HOST}/{route}</loc>'
        if loc not in text:
            new.append(f'<url>{loc}<lastmod>{TODAY}</lastmod></url>')
    if new:
        sitemap.write_text(text.replace('</urlset>', ''.join(new) + '</urlset>', 1), encoding='utf8', newline='\n')


if __name__ == '__main__':
    apply()
