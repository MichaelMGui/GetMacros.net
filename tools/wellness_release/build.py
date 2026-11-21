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
from wellness_release.followup import RECORDS as FOLLOWUP, SOURCE_DATE as FOLLOWUP_DATE, render_body

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
REVIEW_DRAFT = ('P04-01', 'acne', 'diet-and-acne-what-the-trial-tested.html',
                'Can diet affect acne? What the trial changed besides sugar',
                'Read what a 12-week acne trial tested and compare its conclusions with the dermatology guideline.',
                ['https://pubmed.ncbi.nlm.nih.gov/17616769/', 'https://www.aad.org/news/updated-guidelines-acne-management'],
                'Specialist review pending.')
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
    ('P04-01', 'acne-counts-vs-grades', 'acne-study-lesion-count-vs-severity-grade.html',
     'Why do acne studies count spots and also grade overall severity?',
     'Compare three ways of describing a skin outcome and see what a percentage can hide.',
     ['https://www.fda.gov/regulatory-information/search-fda-guidance-documents/acne-vulgaris-establishing-effectiveness-drugs-intended-treatment',
      'https://www.fda.gov/media/71152/download'],
     'U.S. FDA guidance and fictional figures for reading study endpoints. No personal treatment recommendation.'),
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
    ('P03-21', 'postexercise-soreness', 'what-soreness-means-for-muscle-recovery.html', 'Does soreness tell you your muscles have recovered?',
     'Compare reported soreness with strength and lab measures after an unfamiliar exercise bout.',
     ['https://pubmed.ncbi.nlm.nih.gov/27116346/',
      'https://pubmed.ncbi.nlm.nih.gov/27219125/'],
     'Interpretation of exercise recovery measurements. The group results do not diagnose injury or determine an individual’s readiness.'),
    ('P03-32', 'contrast-water-comparator', 'contrast-water-recovery-how-to-read-the-control.html', 'Is it the hot water, the cold or the contrast? What recovery studies can isolate',
     'Compare cold-only, contrast and control conditions before attributing a recovery effect to alternating temperatures.',
     ['https://pubmed.ncbi.nlm.nih.gov/21132438/',
      'https://pubmed.ncbi.nlm.nih.gov/29299318/',
      'https://pubmed.ncbi.nlm.nih.gov/42713556/'],
     'Study-method comparison in trained adults. The article does not provide a home immersion protocol.'),
    ('P03-38', 'urine-colour-sport-research', 'urine-color-hydration-what-it-measures.html', 'What can urine color actually tell you about hydration?',
     'Read how scientists compared color with urinary concentration and why one sample cannot summarize your fluid balance.',
     ['https://pubmed.ncbi.nlm.nih.gov/36034925/'],
     'Research literacy about samples and instruments. No clinical threshold, diagnosis or intake target.'),
    ('P04-18', 'sun-measurement-skin', 'how-skin-studies-measure-sun-exposure.html', 'How do skin studies separate a nutrition result from sun exposure?',
     'Compare questionnaire, diary and badge methods and see why equal time outside can mean different exposure.',
     ['https://pubmed.ncbi.nlm.nih.gov/29421857/',
      'https://pubmed.ncbi.nlm.nih.gov/27419038/',
      'https://pubmed.ncbi.nlm.nih.gov/23732711/'],
     'Methods used in sun-exposure validation studies and a randomized skin-outcome study. No sun exposure recommendation.'),
    ('P05-06', 'compounding-fda-distinction', 'compounded-medicine-vs-fda-approved.html', 'Does ‘compounded’ mean a medicine is FDA-approved?',
     'Distinguish FDA approval of a finished medicine from pharmacy compounding and facility registration.',
     ['https://www.fda.gov/drugs/human-drug-compounding/compounding-and-fda-questions-and-answers',
      'https://www.fda.gov/drugs/human-drug-compounding/questions-and-answers-outsourcing-facility-registration',
      'https://www.fda.gov/drugs/human-drug-compounding/compounding-laws-and-policies'],
     'U.S. FDA regulatory definitions. No advice about choosing a medication or obtaining a compounded product.'),
    ('P05-31', 'probiotic-strain-label', 'what-a-probiotic-strain-code-means.html', 'How to read a probiotic strain code on the label',
     'Match a strain code across a study and a bottle even when the genus name has changed.',
     ['https://ods.od.nih.gov/factsheets/Probiotics-HealthProfessional/',
      'https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling'],
     'NIH strain nomenclature and U.S. label literacy. Published examples are about identity rather than disease-specific effectiveness.'),
    ('P01-22', 'thiamin-enriched-flour', 'thiamin-enriched-vs-unenriched-flour.html', 'How much thiamin does flour enrichment add to a recipe?',
     'Compare two all-purpose flour records at the same weight and calculate the ingredient contribution per roll.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://ods.od.nih.gov/factsheets/Thiamin-HealthProfessional/',
      'https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-137/subpart-B/section-137.165'],
     'U.S. SR Legacy flour references and U.S. enriched flour rules. The per-roll math is for the unbaked ingredient.'),
    ('P01-35', 'two-boiled-eggs-nutrients', 'two-boiled-eggs-nutrients-beyond-protein.html', 'What do two hard-boiled eggs provide besides protein?',
     'See the B12, selenium, vitamin D and other values for two large eggs and compare a side’s contribution.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'U.S. USDA SR Legacy egg and spinach references. Use edible cooked weights without the shell.'),
    ('P01-43', 'lentils-chickpeas-folate-iron', 'lentils-vs-chickpeas-iron-folate-per-serving.html', 'Lentils vs. chickpeas for iron and folate in a half-cup',
     'Compare the same cooked weight and the same volume, then calculate a mix of both.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://ods.od.nih.gov/factsheets/Folate-HealthProfessional/'],
     'USDA SR Legacy cooked, unsalted legume entries. Total iron in the table is not a measure of absorption.'),
    ('P02-04', 'ground-beef-cooked-lean', '80-20-vs-90-10-ground-beef-cooked.html', '80/20 vs. 90/10 ground beef after cooking: how different is an 85 g patty?',
     'Compare two broiled patties at the same cooked weight and see why the raw label does not scale directly.',
     ['https://fdc.nal.usda.gov/download-datasets/',
      'https://www.ars.usda.gov/ARSUserFiles/80400535/Data/retn/retn06.pdf'],
     'USDA SR Legacy values for two broiled beef patty records. No additions included.'),
    ('P02-05', 'turkey-beef-saturated-fat', 'ground-turkey-vs-ground-beef-saturated-fat.html', 'Can ground turkey have more saturated fat than ground beef?',
     'Compare three broiled USDA patties with different starting fat percentages.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'USDA SR Legacy broiled plain patties. The results depend on the exact blend and preparation.'),
    ('P02-15', 'lentils-replace-ground-beef', 'replace-ground-beef-with-lentils-protein-and-fiber.html', 'What changes if you swap half the ground beef for cooked lentils?',
     'Keep the cooked weight unchanged and see how calories, protein and fiber shift together.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'USDA SR Legacy boiled lentils and cooked ground beef. Sauce, oil and other ingredients are excluded.'),
    ('P02-24', 'egg-whites-vs-whole', 'egg-whites-vs-whole-eggs-real-portions.html', 'How do four egg whites compare with two whole eggs?',
     'Compare real ingredient amounts, then see why equal weight answers a different question.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'USDA SR Legacy raw egg ingredients measured before cooking. This is a recipe comparison.'),
    ('P02-44', 'chicken-tofu-chickpea-bowl', 'tofu-chickpea-bowl-vs-chicken-bowl-protein.html', 'Can a tofu and chickpea bowl match a chicken bowl for protein?',
     'Use two worked recipes with the same cooked rice and see which portions get both bowls to about 29 g protein.',
     ['https://fdc.nal.usda.gov/download-datasets/'],
     'Calculated portions based on USDA SR Legacy entries. No dressing, oil or seasoning added.'),
    ("P01-29", "boiled-broccoli-vitamin-c", "broccoli-vitamin-c-boiled-retention.html", "How much vitamin C stays in broccoli after boiling?",
     "Compare the same broccoli before and after cooking and see why concentration alone can give a different answer.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC6049644/"],
     "A laboratory comparison of specified cooking conditions. Results vary with time, water, preparation and the starting broccoli."),
    ("P01-33", "tofu-calcium-label", "calcium-in-tofu-firm-vs-regular.html", "Can two types of calcium-set tofu list very different amounts of calcium?",
     "Compare two calcium-sulfate reference entries at the same weight, then see where to look on a package.",
     ["https://fdc.nal.usda.gov/download-datasets/",
      "https://www.ams.usda.gov/sites/default/files/media/Calcium%20Sulfate%202%20TR.pdf"],
     "The quantities are historical USDA SR Legacy reference values for two preparations, not estimates for any package on sale."),
    ("P02-47", "oatmilk-enzymes-sugar", "why-oat-milk-has-added-sugar-without-sugar-ingredient.html",
     "Why does some oat milk have added sugar with no sugar in the ingredients?",
     "Read the FDA’s explanation and compare two U.S. Oatly cartons at the same volume.",
     ["https://www.fda.gov/media/117402/download",
      "https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-full-fat-64-oz",
      "https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-unsweetened-64-oz"],
     "FDA guidance and official labels for two named U.S. products. Cartons in other markets can differ."),
    ("P04-38", "skin-hydration-probes", "skin-hydration-meters-compare-readings.html", "Why can two skin hydration meters disagree on the same patch?",
     "Compare what capacitance and conductance measure and what belongs next to a published change in hydration.",
     ["https://pubmed.ncbi.nlm.nih.gov/14731246/",
      "https://pubmed.ncbi.nlm.nih.gov/35980652/"],
     "Instrument-comparison research in defined test groups. This is a reading guide to evidence, not a skin assessment."),
    ("P05-14", "b12-form-vs-dose", "vitamin-b12-form-vs-dose-absorption.html", "Does a different form of vitamin B12 guarantee higher absorption?",
     "Separate the chemical form on a label from the dose and the fraction that was absorbed.",
     ["https://ods.od.nih.gov/factsheets/VitaminB12-HealthProfessional/"],
     "NIH Office of Dietary Supplements reference estimates for oral supplements. The worked arithmetic has no dosing recommendation."),
    ("P05-32", "probiotic-cfu-expiry", "probiotic-cfu-at-manufacture-vs-expiration.html", "When does a probiotic’s advertised CFU count apply?",
     "Compare two example labels and find out how serving units, expiration and storage affect the meaning of the number.",
     ["https://ods.od.nih.gov/factsheets/Probiotics-HealthProfessional/"],
     "U.S. Supplement Facts context. Package examples are fictional and illustrate label reading."),
    ("P06-44", "fiber-serving-rank-reversal", "which-food-has-more-fiber-serving-vs-calorie.html", "Why does spinach rank above beans for fiber per calorie, but below them per serving?",
     "Compare boiled spinach, black beans, lentils and a tomato using the actual weight needed for each serving basis.",
     ["https://fdc.nal.usda.gov/download-datasets/"],
     "USDA SR Legacy for the four specified preparations. No salt, sauce or toppings added in the examples."),
    ("P06-12", "uk-restaurant-alias-ranking", "uk-protein-ranking-location-duplicate-records.html", "How duplicate location listings change a UK protein ranking",
     "See what happened to a ten-item protein list when exact airport duplicates were grouped and unique dishes were kept.",
     ["https://www.nandos.co.uk/food/menu/",
      "https://www.nandos.co.uk/allergens/allergy-information-gatwick",
      "https://www.wendys.com/sites/default/files/2026-04/United-Kingdom-National-Nutrition-Information---3.25.2026-(002).pdf",
      "https://pepes.co.uk/nutrition-allergens-uk/"],
     "Historical GetMacros UK source snapshot. Current official pages are supplied for recipe and menu context, and values can change."),
    ("P03-23", "sauna-steam-humidity", "steam-room-dry-sauna-humidity-study.html", "Why can a cooler steam room feel harder than a hot dry sauna?",
     "Read a crossover comparison of humidity, body mass and heat strain alongside a controlled humidity experiment.",
     ["https://pubmed.ncbi.nlm.nih.gov/24899780/",
      "https://pubmed.ncbi.nlm.nih.gov/24597154/"],
     "Laboratory studies in small groups of healthy men. No personal heat exposure plan or safety threshold is inferred."),
    ("P03-25", "water-vs-air-heat", "hot-bath-study-vs-steam-room-evidence.html", "Why doesn’t a hot bath study tell you what happens in a steam room?",
     "Compare an actual water-immersion trial with the separate design a steam-room claim would need.",
     ["https://pubmed.ncbi.nlm.nih.gov/40332494/",
      "https://pubmed.ncbi.nlm.nih.gov/24899780/"],
     "Protocols in healthy adult samples. Acute measurements describe the trial conditions and are not instructions for home heat exposure."),
    ("P03-33", "sports-drink-sodium-bottle", "sports-drink-sodium-per-bottle-serving.html", "How much sodium is in the whole sports drink bottle?",
     "Convert a 12-ounce comparison to what you actually drink without mistaking a scaled amount for the package label.",
     ["https://www.gatorade.com/sports-drinks/gatorade-thirst-quencher/lemon-lime",
      "https://performancepartner.gatorade.com/content/resources/pdfs/foods-fluids-for-explosive-power-sports-2026.pdf"],
     "U.S. manufacturer figures for named beverages. Derived volumes are labeled as estimates and do not prescribe intake."),
    ("P03-36", "exercise-weight-change", "before-after-exercise-weight-sweat-loss.html", "Does the change on a scale show how much you sweated?",
     "Work through an example in which net weight and estimated sweat loss give different numbers.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC5634236/",
      "https://www.tandfonline.com/doi/full/10.1080/02640414.2019.1633159"],
     "A numerical example of a sports science method. No personal fluid target or body composition estimate is inferred."),
    ("P03-46", "sleep-diary-observations", "sleep-diary-without-a-sleep-score.html", "How to keep a sleep diary without turning it into a score",
     "Use a few observations and a worked night to pair subjective sleep quality with estimated timing.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC3250369/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC8314633/"],
     "The Consensus Sleep Diary and a comparison study inform the example. It is not a sleep diagnosis."),
    ("P05-15", "elemental-zinc-label", "elemental-zinc-on-supplement-facts.html", "What does “zinc 15 mg as zinc gluconate” mean on a label?",
     "Read the elemental zinc line, source ingredient and serving size separately.",
     ["https://ods.od.nih.gov/factsheets/Zinc-HealthProfessional/"],
     "U.S. Supplement Facts context. The numbers on the illustrated label are fictional."),
    ("P05-18", "epa-dha-softgels-normalized", "compare-epa-dha-per-softgel.html", "Which fish oil has more EPA and DHA once you compare one capsule?",
     "Normalize two named softgel products to the same capsule count and see how the result changes.",
     ["https://www.naturemade.com/products/fish-oil-1200-mg-softgels-burp-less-one-per-day",
      "https://www.nordic.com/products/ultimate-omega/",
      "https://www.nordic.com/cofa-results/?LotNumber=252648"],
     "Manufacturer declarations and one stated specification for a Nordic Naturals lot. This is a serving-math comparison, not product dosing advice."),
    ("P05-36", "daily-value-upper-limit", "daily-value-vs-upper-intake-limit.html", "Does a supplement’s % Daily Value tell you its upper limit?",
     "Read two different reference numbers and calculate what a big percentage on the label actually compares.",
     ["https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels",
      "https://ods.od.nih.gov/factsheets/VitaminC-Consumer/"],
     "U.S. general label Daily Value and adult U.S. upper limit example. Suggested or personal intakes are outside scope."),
    ("P06-45", "diary-export-unknown", "what-null-means-on-a-food-diary-export.html", "What does a null nutrient mean in a GetMacros diary export?",
     "Learn what a blank value says about the source and how to read an exported sum without counting unknown amounts as zero.",
     ["https://getmacros.net/food-diary.html",
      "https://getmacros.net/privacy.html"],
     "GetMacros diary JSON behavior. Example records are fictional, and exports remain private."),
    ("P01-12", "retinol-activity-equivalents", "why-vitamin-a-and-beta-carotene-use-different-units.html", "Why are vitamin A and beta-carotene listed in different units?",
     "Convert food beta-carotene to retinol activity equivalents and avoid counting an ingredient twice.",
     ["https://ods.od.nih.gov/factsheets/VitaminA-HealthProfessional/"],
     "U.S. reference conversion for vitamin A. The worked values are examples of unit conversion, not supplement doses."),
    ("P01-17", "iodine-without-seafood", "iodine-foods-without-seafood.html", "Which common foods contain iodine if you skip seafood?",
     "Compare eggs, cheese and iodized salt using measured portions, and check the exact ingredient that matters in bread.",
     ["https://ods.od.nih.gov/factsheets/Iodine-HealthProfessional/"],
     "U.S. iodine reference examples. Brand, region, dairy production and formulation can change the amounts."),
    ("P01-21", "manganese-grain-bowl", "manganese-brown-rice-white-rice-oats.html", "How much manganese changes when you swap white rice for brown rice?",
     "Use matched cooked portions to compare the same chickpea bowl and see where oats fit.",
     ["https://ods.od.nih.gov/factsheets/Manganese-HealthProfessional/"],
     "NIH reference table uses cooked medium-grain brown rice and long-grain white rice. The example swaps both the grain type and the stated reference preparation."),
    ("P01-25", "vitamin-b6-plate", "vitamin-b6-foods-chickpeas-chicken-banana.html", "Which everyday servings give you vitamin B6?",
     "Compare canned chickpeas, roast chicken and a banana, then calculate two smaller mixed servings.",
     ["https://ods.od.nih.gov/factsheets/VitaminB6-HealthProfessional/"],
     "NIH reference foods and portions. The worked meal subtotal uses rounded published values."),
    ("P03-10", "night-shift-relative-sleep", "why-night-shift-sleep-studies-use-biological-time.html", "Why can night-shift sleepers get the same hours but different amounts of REM sleep?",
     "Read the study’s shared sleep window and see what scientists measured to distinguish clock time from biological timing.",
     ["https://pubmed.ncbi.nlm.nih.gov/37914630/",
      "https://pubmed.ncbi.nlm.nih.gov/39078935/"],
     "Laboratory studies with specified night shifts. Results depend on the schedule, testing measures and people studied."),
    ("P03-18", "dinner-hours-before-sleep", "late-dinner-before-bed-what-sleep-studies-measure.html", "Does dinner an hour before bed change sleep in the same way every time?",
     "Compare two trials with similar dinner gaps and different testing schedules.",
     ["https://pubmed.ncbi.nlm.nih.gov/32525525/",
      "https://pubmed.ncbi.nlm.nih.gov/41975458/"],
     "Two randomized crossover studies in small healthy adult samples. This comparison describes studied meals and measurements."),
    ("P03-28", "soreness-ice-bath-trials", "ice-baths-and-soreness-24-48-hour-trials.html", "Why did two ice-bath trials disagree about soreness the next day?",
     "Compare the exercise, control condition and soreness tasks in two randomized studies.",
     ["https://pubmed.ncbi.nlm.nih.gov/17654228/",
      "https://pubmed.ncbi.nlm.nih.gov/17261562/"],
     "Two controlled studies in specific research samples. Experimental exposures are reported for comparison and are not home instructions."),
    ("P04-21", "vitamin-c-skin-observational", "vitamin-c-in-food-vs-wrinkle-claim-evidence.html", "What can a high-vitamin-C food tell you about a wrinkle claim?",
     "Separate a nutrient measurement from a survey association and from an intervention.",
     ["https://ods.od.nih.gov/factsheets/VitaminC-HealthProfessional/",
      "https://pubmed.ncbi.nlm.nih.gov/17921406/"],
     "Food reference values and an observational U.S. study. The article explains evidence types without endorsing a treatment."),
    ("P04-22", "carotenoids-vs-tanning-reflectance", "carotenoid-skin-color-vs-uv-tanning.html", "Can a study tell carotenoid-related color from a tan?",
     "Read the reflected-light measurements behind a randomized smoothie study, and see what an ordinary photo cannot resolve.",
     ["https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133445",
      "https://pubmed.ncbi.nlm.nih.gov/22412966/"],
     "Optical research on specific study groups and foods. Color values are measurements, with no beauty standard or nutrition diagnosis inferred."),
    ("P01-28", "canned-fish-bones-calcium", "calcium-canned-sardines-pink-salmon-bones.html", "How much does leaving the bones in change canned-fish calcium?",
     "Compare three equal drained portions of fish, with the bone and skin instructions kept visible.",
     ["https://fdc.nal.usda.gov/download-datasets/"],
     "Three U.S. SR Legacy food entries. The two pink-salmon preparations differ in both bones and skin."),
    ("P01-30", "apricot-drying-portion", "dried-vs-fresh-apricot-vitamin-c-fiber.html", "Why do dried apricots have more fiber but less vitamin C per 100 g?",
     "Compare fresh and dried reference apricots by weight and by the portions you actually see.",
     ["https://fdc.nal.usda.gov/download-datasets/"],
     "U.S. SR Legacy fresh and dried sulfured apricots. The records are separate reference foods, so they do not measure the exact change in a batch."),
    ("P01-39", "orange-grapefruit-matched-grams", "orange-vs-grapefruit-vitamin-c-same-weight.html", "Does an orange have more vitamin C than grapefruit at the same weight?",
     "Separate vitamin C concentration from the size of an orange, half grapefruit or measured cup.",
     ["https://fdc.nal.usda.gov/download-datasets/",
      "https://www.fda.gov/consumers/consumer-updates/grapefruit-juice-and-some-drugs-dont-mix"],
     "U.S. SR Legacy raw orange and pink or red grapefruit references. The FDA separately describes medication interactions for grapefruit."),
    ("P02-06", "chicken-thigh-edible-yield", "bone-in-chicken-thigh-cooked-edible-protein.html", "How much edible meat is in a bone-in chicken thigh?",
     "Translate USDA’s purchase yield into a kitchen example, then calculate protein for cooked meat without bone or skin.",
     ["https://foodbuyingguide.fns.usda.gov/files/Reports/USDA_FBG_Section1_MeatsAndMeatAlternatesYieldTable.pdf",
      "https://fdc.nal.usda.gov/download-datasets/"],
     "USDA Food Buying Guide yield for small skin-on bone-in thighs without backs, and a separate SR Legacy roasted thigh reference."),
    ("P02-17", "powdered-peanut-vs-spread", "powdered-peanut-butter-vs-spread-protein.html", "How does powdered peanut butter compare with a regular spread for protein?",
     "A tablespoon label can hide a large weight difference. Compare the listed amounts and then match grams of protein.",
     ["https://pb2.com/products/pb2-original-powdered-peanut-butter-peanut-butter-powder",
      "https://www.jif.com/products/simply/simply-creamy-sweetened"],
     "Named U.S. product labels for the dry powder and the spread. The comparison excludes added liquid or other ingredients."),
    ("P06-28", "banana-edible-weight", "banana-edible-weight-without-peel-food-log.html", "Should you weigh a banana with or without its peel for a food log?",
     "Use actual edible weight when available and learn what a USDA purchase yield can estimate.",
     ["https://foodbuyingguide.fns.usda.gov/files/Reports/USDA_FBG_Section3_FruitsYieldTable.pdf",
      "https://fdc.nal.usda.gov/download-datasets/"],
     "U.S. institutional buying yield and USDA SR Legacy raw banana composition. Actual peel and fruit weights vary."),
    ("P06-05", "menu-data-vs-local-order", "chain-nutrition-page-vs-local-menu-availability.html", "Does a chain’s nutrition page mean a nearby store serves that item?",
     "Use one real ordering example to separate a documented recipe from a location’s current menu.",
     ["https://www.tacobell.com/food/deals-and-combos/cravings-box",
      "https://www.tacobell.com/food/new/cravings-box?store=032077",
      "https://www.tacobell.com/locations"],
     "U.S. Taco Bell ordering pages, which can change with store, date and session. This guide does not claim a specific location currently serves the item."),
    ("P06-06", "taco-bell-box-drink", "taco-bell-cravings-box-calories-include-drink.html", "Does a Taco Bell Cravings Box already include the drink?",
     "Follow the meal’s scope and choose which number to log for a store-specific box.",
     ["https://www.tacobell.com/food/new/cravings-box?store=032077",
      "https://www.tacobell.com/food/online-exclusives/build-your-own-cravings-box?store=025493",
      "https://www.tacobell.com/nutrition/calculator"],
     "Examples are from U.S. store-context pages. Box contents, posted ranges and availability may vary."),
    ("P06-09", "subway-uk-ireland-chicken-salad", "subway-chicken-breast-salad-uk-vs-ireland.html", "Subway Chicken Breast Salad: the UK and Irish pages give different numbers",
     "Compare the portions by order and per 100 g without guessing which ingredients changed.",
     ["https://www.subway.com/en-ie/menunutrition/menu/category/salads/product/chicken-breast",
      "https://www.subway.com/en-gb/menunutrition/menu/category/salads/product/chicken-breast"],
     "Two official market-specific Subway salad pages. The figures are for the stated listings, not every customized salad."),
    ("P06-14", "pizza-pizza-same-slice-different-pie", "pizza-pizza-small-medium-same-slice-calories.html", "How can two Pizza Pizza sizes both have 210 calories per pepperoni slice?",
     "Multiply by the chain’s actual slice count and compare two slices, half a pizza and the whole pie.",
     ["https://www.pizzapizza.ca/about-us/nutrition/small-pizza/",
      "https://www.pizzapizza.ca/about-us/nutrition/medium-pizza/"],
     "Canadian Pizza Pizza pepperoni rows updated March 12, 2026. Whole-pizza and half-pizza estimates multiply rounded slice values."),
    ("P06-46", "taco-johns-limited-menu-count", "taco-johns-limited-time-menu-coverage-count.html", "How many Taco John’s nutrition listings are marked limited time?",
     "See which entries a GetMacros snapshot found and how to count them without claiming permanent availability.",
     ["https://tacojohns.com/wp-content/uploads/2026/09/TAC-26-P5_NUTRITION-GUIDE_ED_V3.pdf",
      "https://tacojohns.com/nutrition-information/"],
     "Historical U.S. GetMacros Taco John’s nutrition snapshot for the cited source. This is a count of imported entries, not an inventory of current sales."),
    ("P06-47", "greggs-pizza-rounding", "greggs-pizza-box-serving-rounding.html", "Why don’t two Greggs pizza slices add up to every number on the box label?",
     "Compare published single- and double-portion figures and test whether rounding could explain a mismatch.",
     ["https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf"],
     "Greggs UK nutrition PDF. Rounding bounds are illustrative tests, not a statement of the company’s actual calculation process."),
    ("P03-20", "oura-readiness-vs-strength", "does-oura-readiness-score-measure-muscle-recovery.html", "What does an Oura Readiness Score tell you about muscle recovery?",
     "Read the device’s actual inputs and compare them with a study that tested muscle strength directly.",
     ["https://support.ouraring.com/hc/en-us/articles/360057791533-Readiness-Contributors",
      "https://pubmed.ncbi.nlm.nih.gov/17654228/"],
     "The Oura score description applies to its documented product. The study measures a different outcome."),
    ("P03-41", "tart-cherry-outcomes", "tart-cherry-juice-soreness-vs-strength-studies.html", "Did tart cherry juice studies find less soreness or faster strength recovery?",
     "Compare two running-trial questions, then see why a newer pooled estimate treats their outcomes separately.",
     ["https://pubmed.ncbi.nlm.nih.gov/19883392/",
      "https://pubmed.ncbi.nlm.nih.gov/20459662/",
      "https://pubmed.ncbi.nlm.nih.gov/41945263/"],
     "Exercise recovery research with different interventions and population samples. No product use or treatment instructions."),
    ("P03-50", "melatonin-phase-outcome", "melatonin-circadian-shift-vs-sleep-onset-study.html", "Why can a melatonin study shift the body clock without proving faster sleep onset?",
     "Compare two types of timing outcome and see how a study uses the rise of melatonin under dim light.",
     ["https://pubmed.ncbi.nlm.nih.gov/18006583/",
      "https://pubmed.ncbi.nlm.nih.gov/23001190/",
      "https://pubmed.ncbi.nlm.nih.gov/38888087/"],
     "Chronobiology and sleep research interpretation. No personal schedule or amount is recommended."),
    ("P04-31", "acne-age-definition", "why-acne-study-age-bands-and-denominators-matter.html", "Why do acne prevalence numbers change when the study changes the age bracket?",
     "Compare age cutoffs and who entered the denominator in two research designs.",
     ["https://pubmed.ncbi.nlm.nih.gov/39422854/",
      "https://pubmed.ncbi.nlm.nih.gov/10495379/",
      "https://www.fda.gov/media/71152/download"],
     "Population and methods comparison only. The studies described came from different periods and answer different questions."),
    ("P05-16", "zinc-copper-duration", "why-high-zinc-studies-check-copper-over-time.html", "Why do studies of repeated high zinc intake check copper too?",
     "Read the duration and outcome behind the NIH’s zinc and copper summary.",
     ["https://ods.od.nih.gov/factsheets/Zinc-HealthProfessional/",
      "https://ods.od.nih.gov/factsheets/Copper-HealthProfessional/"],
     "Summary of public NIH reference material. No advice on treating a deficiency or combining supplements."),
    ("P05-33", "prebiotic-fiber-label", "prebiotic-fiber-vs-dietary-fiber-on-label.html", "Does “prebiotic fiber” mean all the fiber on the label is prebiotic?",
     "Read the dietary fiber total and the named ingredient separately, using FDA guidance and a scientific consensus definition.",
     ["https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/questions-and-answers-dietary-fiber",
      "https://pubmed.ncbi.nlm.nih.gov/28611480/"],
     "U.S. fiber declaration context and an international scientific consensus. The package example is fictional."),
    ("P05-49", "d3-gummy-softgel-matched", "vitamin-d3-one-gummy-vs-one-softgel.html", "Can one gummy have the same vitamin D3 as a softgel with half the number on the front?",
     "Normalize two named labels by serving count and record the equivalent unit just once.",
     ["https://www.naturemade.com/products/nature-made-vitamin-d3-gummies",
      "https://www.naturemade.com/products/vitamin-d3-25-mcg-1000-iu-softgels?variant=17609447571527"],
     "U.S. manufacturer pages for exact Nature Made products. The calculation compares stated amounts and does not recommend use."),
    ("P06-49", "selenium-ranking-coverage", "selenium-ranking-what-missing-sardines-changes.html", "What happens to a selenium ranking if one food is missing?",
     "Reproduce a ranking change in a small GetMacros reference set and see why the denominator matters.",
     ["https://fdc.nal.usda.gov/download-datasets/",
      "https://getmacros.net/nutrient-density-explorer.html"],
     "Fixed GetMacros explorer set of 18 selected U.S. reference foods. The missing row is an explicitly simulated scenario."),
    ("P02-11", "whey-soy-isolate-equal-weight", "now-whey-vs-soy-protein-powder-same-weight.html", "How do NOW whey and soy protein isolates compare at the same weight?",
     "Compare two scoops as labeled, then normalize both to 25 g of dry powder.",
     ["https://www.nowfoods.com/products/sports-nutrition/whey-protein-isolate-unflavored-powder",
      "https://www.nowfoods.com/products/sports-nutrition/soy-protein-isolate-unflavored-powder"],
     "Named unflavored U.S. NOW Sports powders. The label values describe dry powder and can differ for other variants."),
    ("P02-23", "impossible-plant-ground-sodium", "impossible-ground-beef-vs-lite-sodium-protein-canada.html", "How much does sodium change between two Impossible ground products in Canada?",
     "Compare classic and Lite at four ounces and at roughly matched protein.",
     ["https://impossiblefoods.com/ca/nutrition-disclaimers"],
     "Impossible Foods’ Canada reference page for two product formulations. Calculation excludes seasonings and additions."),
    ("P02-31", "fage-plain-vs-strawberry-split", "fage-plain-vs-strawberry-split-cup-nutrition.html", "What changes on the label of FAGE plain yogurt versus a strawberry split cup?",
     "Compare two 150 g cups at the same stated milk-fat category, and see what the split package leaves unknown.",
     ["https://usa.fage/products/yogurt/fage-total-2",
      "https://usa.fage/products/yogurt/fage-total-2-split-cup/fage-total-2-strawberry-53-oz"],
     "Two labeled FAGE U.S. products. The split-cup label covers both compartments together."),
    ("P02-46", "protein-bar-mass-share", "protein-bar-percent-protein-by-weight.html", "Which protein bar has a bigger share of its weight as protein?",
     "Two chocolate-chip examples switch order when you compare grams per bar with protein as a share of weight.",
     ["https://www.questnutrition.com/products/chocolate-chip-cookie-dough-protein-bar",
      "https://www.pureprotein.com/collections/protein-bars/products/chewy-chocolate-chip-protein-bar",
      "https://www.pureprotein.ca/product/bars-chewy-chocolate-chip/"],
     "Specific sources for two package sizes and flavors. Formula, flavor and market can affect the printed values."),
    ("P04-41", "post-workout-size-photos", "post-workout-photo-vs-muscle-growth.html",
     "Can a post-workout photo separate muscle swelling from growth?",
     "Compare immediate and six-week ultrasound results and use the timing to read a before-and-after claim.",
     ["https://pubmed.ncbi.nlm.nih.gov/31904714/",
      "https://pubmed.ncbi.nlm.nih.gov/26280652/"],
     "Two specific ultrasound studies in untrained men. The measurements apply to their tested muscles, timing and methods."),
    ("P04-46", "hair-shine-optical-conditions", "hair-shine-lighting-oil-vs-nutrition-evidence.html", "Can shinier hair in a photo prove a nutrition change?",
     "Compare what controlled hair-fiber studies measure with what a beauty post actually shows.",
     ["https://pubmed.ncbi.nlm.nih.gov/14528387/",
      "https://pubmed.ncbi.nlm.nih.gov/15037922/"],
     "Laboratory optical measurements of hair samples. No dietary treatment or personal nutrient assessment."),
    ("P05-11", "magnesium-sleep-study-enrolment", "magnesium-sleep-trials-who-was-studied.html", "Who took part in the magnesium sleep studies you see online?",
     "Compare eligibility, duration and outcomes before applying one study to a different reader.",
     ["https://pubmed.ncbi.nlm.nih.gov/40918053/",
      "https://pubmed.ncbi.nlm.nih.gov/23853635/"],
     "Two specific human trials. This is a comparison of study enrolment and measurement, not guidance on treating sleep problems."),
    ("P05-20", "collagen-study-funding-replication", "collagen-skin-studies-funding-and-replication.html", "Why does a funded collagen study still need an independent repeat?",
     "Read a real funding subgroup result and see what it can and cannot establish.",
     ["https://pubmed.ncbi.nlm.nih.gov/40324552/",
      "https://pubmed.ncbi.nlm.nih.gov/42342959/"],
     "Evidence synthesis and review methods. No claim about an individual product’s efficacy or treatment."),
    ("P03-24", "sauna-cohort-absolute-counts", "sauna-longevity-study-absolute-numbers.html", "What did the Finnish sauna longevity study actually count?",
     "Read the event counts alongside weekly habits and distinguish an observed association from a scheduled intervention.",
     ["https://pubmed.ncbi.nlm.nih.gov/25705824/",
      "https://pubmed.ncbi.nlm.nih.gov/29551418/"],
     "Historical Finnish cohort evidence with a defined sample and observed habits. It does not prescribe heat exposure."),
    ("P04-27", "hair-supplement-generalization", "hair-supplement-trials-self-perceived-thinning.html", "Who was actually studied in the hair supplement research behind an ad?",
     "Compare participant criteria and controls across two studies used in claims about commercial products.",
     ["https://pubmed.ncbi.nlm.nih.gov/26903744/",
      "https://pubmed.ncbi.nlm.nih.gov/41171588/"],
     "Interpretation of selected commercial-product studies. The evidence does not establish an individual diagnosis or treatment."),
    ("P04-39", "hair-width-vs-growth-rate", "hair-shaft-width-vs-growth-rate-measurements.html", "Does a wider hair shaft mean hair grew faster?",
     "Read what a one-image method measures and what requires repeated images of the same site.",
     ["https://pubmed.ncbi.nlm.nih.gov/42719743/",
      "https://pubmed.ncbi.nlm.nih.gov/8003326/"],
     "Measurement-method studies. Their results do not establish an individual growth rate or response to a treatment."),
    ("P04-40", "head-position-chin-photo", "head-position-chin-length-profile-photo.html", "Can a small head tilt change how long the chin looks in a photo?",
     "Use a controlled photography study to measure the effect of posture on apparent facial dimensions.",
     ["https://pubmed.ncbi.nlm.nih.gov/21146481/"],
     "Facial photography method study. The reported changes apply to the tested pose and measures."),
    ("P04-45", "small-sample-appearance-percent", "skin-study-small-sample-percent-confidence-interval.html", "Why does “80% saw an improvement” mean less when only five people were studied?",
     "Compare two fictional responder counts using the same percentage and a transparent uncertainty calculation.",
     ["https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm"],
     "Fictional examples using approximate 95% Wilson confidence intervals for a proportion. No product effectiveness claim."),
    ("P05-19", "collagen-trial-comparator-mass", "collagen-trial-maltodextrin-placebo-meaning.html", "What does a maltodextrin placebo let a collagen trial test?",
     "Read the actual amounts and ingredients in a trial’s comparator, then identify the question it leaves open.",
     ["https://pubmed.ncbi.nlm.nih.gov/39336856/",
      "https://pubmed.ncbi.nlm.nih.gov/39021368/"],
     "Two named skin-related product trials. This guide compares study designs and offers no treatment or dosing advice."),
    ("P05-48", "protein-placebo-vs-food-control", "protein-supplement-trial-placebo-vs-food-comparison.html", "Why does a protein trial’s control food change what the result means?",
     "Compare an isocaloric carbohydrate control with a matched amount of protein from whole foods.",
     ["https://pubmed.ncbi.nlm.nih.gov/27466602/",
      "https://pubmed.ncbi.nlm.nih.gov/41643855/"],
     "Research interpretation of specific protein comparisons. The studies measured different time frames and outcomes."),
    ("P06-08", "burrito-sauce-scope", "burrito-included-sauce-vs-side-packet.html", "When should you log burrito sauce separately?",
     "Compare where a Taco Bell sauce and a Chick-fil-A salsa appear in the chains’ ordering descriptions.",
     ["https://www.tacobell.com/food/burritos/bean-burrito?store=024328",
      "https://www.chick-fil-a.com/stories/high-protein-meals",
      "https://www.chick-fil-a.com/customer-support/our-food/nutrition-and-allergens/do-the-calories-displayed-for-each-menu-item-include-toppings-or-the-dressing-that-goes-with-it"],
     "Examples from U.S. chain pages. Use the actual build as ordered and verify the scope of the sauce or salsa."),
    ("P06-15", "dominos-ca-two-stuffed-slices", "dominos-canada-parmesan-stuffed-crust-two-slices.html", "What do two slices of Domino’s Canada stuffed-crust pizza add up to?",
     "Compare the same number of slices even when one published row covers only one slice.",
     ["https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf"],
     "Domino’s Canada August 2026 guide for medium Parmesan Stuffed Crust Feast pizzas. The calculated two-slice row uses the rounded listed value."),
    ("P06-20", "ramen-broth-solids-scope", "can-you-log-ramen-without-the-broth.html", "Can you use the full ramen nutrition label if you leave the broth?",
     "Read evidence that broth consumption changes salt intake and identify the portions an exact calculation needs.",
     ["https://pubmed.ncbi.nlm.nih.gov/42395312/",
      "https://foodbuyingguide.fns.usda.gov/Home/About"],
     "One cafeteria study on ramen and a general discussion of measured servings. Its salt values do not transfer to other recipes."),
    ("P06-26", "portion-batch-before-cooking", "divide-oats-before-cooking-recipe-portions.html", "How should you log oats that you divided before cooking?",
     "Follow the weighed dry portion into the diary even when two bowls absorb different amounts of water.",
     ["https://fdc.nal.usda.gov/download-datasets/",
      "https://foodbuyingguide.fns.usda.gov/Appendix/ResourceAppendixB"],
     "USDA dry oats record 173904 and a Food Buying Guide yield example. Bowl weights here illustrate measurement, with no additions."),
    ("P06-34", "repeat-entry-fraction-duplicate", "food-diary-double-count-recipe-fraction.html", "Did you log one part of a meal twice?",
     "Work through a whole-recipe entry and its separate components to find the overlap.",
     ["https://getmacros.net/food-diary.html",
      "https://getmacros.net/what-happens-to-food-diary-when-data-changes.html"],
     "Fictional meal and calculations explaining how to read saved GetMacros portions."),
    ("P06-38", "dominos-component-scope", "why-pizza-sauce-is-listed-as-a-component.html", "Why is a 5-calorie pizza sauce entry missing from a meal search?",
     "Read the Domino’s serving basis and see what a component can contribute to a built pizza.",
     ["https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf",
      "https://getmacros.net/ca/en/restaurants/domino-s/"],
     "August 2026 Domino’s Canada ingredient guide and the corresponding GetMacros guide. Values describe parts of a specific size and crust."),
    ("P06-43", "starkist-can-drained-size", "starkist-tuna-can-drained-vs-net-weight.html", "Why does the five-ounce tuna can use 113 g for its nutrition label?",
     "Compare the package weight and drained serving, then match sodium on two exact StarKist cans.",
     ["https://starkist.com/product/chunk-light-tuna-in-water-can/",
      "https://starkist.com/product/chunk-light-tuna-in-water-25-percent-less-sodium-can/"],
     "U.S. StarKist can labels for two different formulas, using their drained serving sizes."),
    ("P01-19", "phosphorus-ingredients-quantity", "why-phosphorus-missing-on-nutrition-facts.html", "Why can a food contain phosphorus without listing how much?",
     "Compare a carton that lists milligrams with a cola ingredient list that leaves the amount unknown.",
     ["https://ods.od.nih.gov/factsheets/Phosphorus-HealthProfessional/",
      "https://horizon.com/organic-dairy-products/organic-milk/organic-whole-milk/",
      "https://www.coca-cola.com/us/en/brands/coca-cola/products/original"],
     "U.S. labeling context and the two manufacturer product pages. No individual limit or medical advice."),
    ("P01-20", "copper-cashews-sunflower-portion", "copper-cashews-vs-sunflower-seed-portions.html", "Do a handful of cashews and a sprinkle of sunflower seeds provide the same copper?",
     "Compare an ounce and a quarter cup as listed, then rescale to smaller toppings.",
     ["https://ods.od.nih.gov/factsheets/Copper-HealthProfessional/"],
     "NIH food reference values for specific preparation and serving sizes. Tablespoon values scale the same listed quarter cup."),
    ("P01-26", "vitamin-d-fish-egg-servings", "natural-vitamin-d-trout-salmon-eggs.html", "How much vitamin D is naturally present in trout, salmon and eggs?",
     "Compare named fish and egg servings and calculate what a smaller portion contributes.",
     ["https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/"],
     "NIH Table 3 reference portions. Values exclude separately added food ingredients and vary with exact species and production."),
    ("P01-34", "oat-soy-calcium-coffee", "fortified-oat-vs-soy-milk-calcium-coffee-portion.html", "How much calcium does a splash of fortified oat or soy drink add?",
     "Compare two 240 mL labels, then scale each to the part poured into your coffee.",
     ["https://www.silk.com/plant-based-products/soymilk/unsweet-soymilk",
      "https://www.oatly.com/en-us/products/chilled-oatmilk/chilled-oatmilk-unsweetened-64-oz"],
     "Named U.S. Silk and Oatly products. The calculation applies only to the drink poured, excluding coffee and other ingredients."),
    ("P01-38", "meal-iron-content-vs-absorption", "nonheme-iron-meal-content-vs-absorption.html", "Why doesn’t twice the iron in a meal mean twice as much is absorbed?",
     "Compare a study’s measured iron content and absorbed amount, then see what a food table can track.",
     ["https://ods.od.nih.gov/factsheets/Iron-HealthProfessional/",
      "https://pubmed.ncbi.nlm.nih.gov/7134832/",
      "https://pubmed.ncbi.nlm.nih.gov/11124756/"],
     "Food composition and human absorption study interpretation. No individual absorption estimate or treatment advice."),
    ("P01-41", "shellfish-edible-selenium", "clam-mussel-selenium-edible-cooked-portion.html", "How do you compare selenium in clams and mussels when the shells are discarded?",
     "Use the same cooked edible weight and check how a counted serving changes the result.",
     ["https://fdc.nal.usda.gov/download-datasets/"],
     "USDA SR Legacy clam and blue mussel records for moist-heat cooking. Portions refer to edible food."),
    ("P01-46", "micronutrient-zero-vs-unknown", "vitamin-k-zero-vs-missing-nutrient-table.html", "What makes a reported zero different from a blank vitamin K value?",
     "Read three actual USDA entries and see what happens to a subtotal when data is missing.",
     ["https://fdc.nal.usda.gov/download-datasets/",
      "https://getmacros.net/nutrient-density-explorer.html"],
     "The data states in three retained U.S. SR Legacy records. A displayed zero is the source value for the preparation."),
    ("P01-48", "chicken-thigh-skin-micronutrients", "roasted-chicken-thigh-skin-vs-meat-micronutrients.html", "What changes in a chicken thigh’s nutrition when you log meat with the skin?",
     "Compare equal edible weights of roasted thigh reference foods, then calculate a smaller serving.",
     ["https://fdc.nal.usda.gov/download-datasets/"],
     "USDA SR Legacy roasted thigh records for edible meat with skin and meat only. These are separate reference entries."),
    ("P01-42", "lentil-folate-uk-records", "green-red-lentils-folate-cooked-uk.html", "Why do cooked green and red lentils have such different folate entries?",
     "Compare the UK food database’s four dry and cooked lentil records, then see why a canned lentil soup entry cannot settle the question.",
     ["https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid"],
     "CoFID 2021, worksheet 1.5 Vitamins, folate in micrograms per 100 g and food codes 13-089, 13-661, 13-657, 13-658, 17-698 and 17-808."),
    ("P01-45", "vitamin-e-cooking-oil-volume", "vitamin-e-cooking-oils-teaspoon-tablespoon.html", "How much vitamin E is in a teaspoon of sunflower, safflower or wheat germ oil?",
     "Compare three NIH oil servings and scale the values from a tablespoon to one teaspoon or one part of a shared dressing.",
     ["https://ods.od.nih.gov/factsheets/VitaminE-HealthProfessional/"],
     "NIH Office of Dietary Supplements vitamin E fact sheet, food table 2, alpha-tocopherol per listed U.S. tablespoon."),
    ("P02-26", "diaas-weakest-ratio", "protein-digestibility-diaas-worked-example.html", "What does a protein digestibility score actually measure?",
     "Walk through the amino-acid ratios behind DIAAS and see why a score of 80 cannot be used to convert your food label to absorbed grams.",
     ["https://www.fao.org/4/i3124e/i3124e.pdf"],
     "FAO Food and Nutrition Paper 92, Chapter 4, sections 4.1 and 4.2. Table is explicitly hypothetical."),
    ("P02-42", "ultra-processed-offered-vs-eaten", "ultra-processed-food-trial-offered-vs-eaten.html", "What did the NIH ultra-processed food trial actually compare?",
     "Separate foods offered from foods eaten in the NIH crossover study and see how to interpret its findings when you’re looking at one grocery item.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/7946062/",
      "https://clinical.nih.gov/news/2019/summer/story-01",
      "https://pubmed.ncbi.nlm.nih.gov/30744710/"],
     "Hall et al. 2019 inpatient randomized crossover study with 20 adults and the original NOVA authors’ explanation of how to classify foods."),
    ("P05-23", "creatine-water-scale", "creatine-weight-gain-water-vs-muscle-study.html", "Does early scale weight during creatine use measure new muscle?",
     "See how a 28-day study separated body weight, total body water and muscle creatine, and what a bathroom scale can tell you on its own.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC155510/"],
     "Powers et al. 2003 resistance-trained adults, randomized placebo comparison with measurements at baseline, day 7 and day 28."),
    ("P05-24", "creatine-saturation-study-phase", "creatine-loading-vs-gradual-muscle-creatine-study.html", "What’s the difference between creatine loading and a longer trial?",
     "Compare the time points in an original muscle-creatine experiment and see why six-day and four-week results answer different questions.",
     ["https://pubmed.ncbi.nlm.nih.gov/8828669/",
      "https://hero.epa.gov/reference/5426616/"],
     "Hultman et al. 1996 study of 31 men, total muscle creatine, with short, gradual, maintenance and cessation observations."),
    ("P06-50", "rice-dry-to-cooked-recipe-yield", "rice-dry-cup-to-cooked-yield-brown-white.html", "How much cooked rice does one dry cup make? Two USDA examples",
     "Work out how many half-cup portions come from a dry cup of two different rice types, and learn how to record the yield of your own batch.",
     ["https://foodbuyingguide.fns.usda.gov/AltText/AppendixB_Example9_Cereal_Rice",
      "https://foodbuyingguide.fns.usda.gov/files/Reports/USDA_FBG_Section4_GrainsYieldTable.pdf"],
     "USDA Food Buying Guide entries for long-grain brown parboiled rice and enriched long-grain white parboiled rice. USDA conversions are approximate food-service estimates."),
    ("P01-47", "canada-calcium-dv-vs-rda", "canada-calcium-daily-value-vs-personal-target.html", "Does 20% Daily Value on a Canadian label mean 20% of your calcium target?",
     "Work through a 260 mg calcium example using Canada’s label denominator and three published reference groups.",
     ["https://www.canada.ca/en/health-canada/services/technical-documents-labelling-requirements/table-daily-values/nutrition-labelling.html",
      "https://www.canada.ca/en/health-canada/services/food-nutrition/healthy-eating/dietary-reference-intakes/tables/reference-values-elements.html"],
     "Canadian general-food label values and selected Health Canada calcium RDAs. The example is a hypothetical portion."),
    ("P01-49", "banana-cnf-usda-provenance", "raw-banana-nutrition-usda-vs-canada-cnf.html", "Why do the U.S. and Canadian raw banana entries have different fiber numbers?",
     "Compare matched edible weights in two official datasets and look up the Canadian source code for each nutrient.",
     ["https://fdc.nal.usda.gov/food-details/173944/nutrients",
      "https://open.canada.ca/data/en/dataset/1b6139bd-ed7e-4043-bc28-ff00e10f3109",
      "https://aliments-nutrition.canada.ca/cnf-fce/source?lang=eng&wbdisable=true"],
     "USDA SR Legacy FDC 173944, USDA NDB 09040, and Canadian Nutrient File 2026 food code 1704. All results use 100 g of raw edible banana."),
    ("P03-02", "cortisol-clock-vs-waking", "morning-cortisol-waking-vs-body-clock.html", "Does waking up make cortisol rise, or is it already rising?",
     "Compare a circadian laboratory experiment with a study that sampled across sleep and waking, and learn why the two measurements answer different questions.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC9669756/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC11732391/"],
     "Bowles et al. forced-desynchrony cortisol study and 2025 study of cortisol sampling before and after waking. General explanation of group research, without test interpretation for individuals."),
    ("P03-03", "one-saliva-sample-stress-claim", "single-saliva-cortisol-test-stress.html", "Can one saliva cortisol reading tell you how stressed you are?",
     "See how researchers interpret the sampling time and compare two hypothetical collection schedules for the same morning.",
     ["https://pubmed.ncbi.nlm.nih.gov/26563991/",
      "https://pubmed.ncbi.nlm.nih.gov/15763075/"],
     "Original expert consensus for the cortisol awakening response and electronic monitoring study of cortisol sampling compliance. Example times illustrate design only and do not interpret a personal test."),
    ("P04-37", "skin-redness-and-texture-endpoints", "skin-redness-vs-texture-study-measurement.html", "Why can a skin redness study and a skin texture study both report a change?",
     "Compare what the instruments measured in two published studies before treating both findings as the same kind of result.",
     ["https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133445",
      "https://www.mdpi.com/2077-0383/13/18/5370"],
     "Tan et al. 2015 reflectance measurements and the 2024 CollaSel Pro trial’s skin-imaging roughness endpoint. No head-to-head comparison."),
    ("P04-42", "chewing-force-vs-jaw-shape", "chewing-gum-jaw-shape-trial.html", "Does a stronger bite mean chewing gum changed someone’s jaw shape?",
     "Read the separate force, muscle and shape outcomes in a six-month randomized chewing trial before interpreting a jawline claim.",
     ["https://pubmed.ncbi.nlm.nih.gov/39215439/",
      "https://doi.org/10.1111/joor.13830"],
     "2024 randomized controlled trial with six months of gum chewing training. Describes study endpoints without prescribing exercise or treatment."),
    ("P02-49", "fairlife-filter-and-lactase", "ultra-filtered-milk-protein-and-lactose-label.html", "Where does the extra protein come from in ultra-filtered milk?",
     "Read the U.S. fairlife 2% milk ingredients and cup comparison to separate filtration, lactase and fortification.",
     ["https://fairlife.com/ultra-filtered-milk/reduced-fat-2-percent-milk/",
      "https://fairlife.com/news/whats-in-a-glass-of-milk/"],
     "U.S. fairlife 2% reduced-fat ultra-filtered milk product label and manufacturer comparison with regular 2% milk. The comparison is market- and formulation-specific."),
    ("P03-26", "heat-conditions-and-fluid-balance", "exercise-heat-humidity-hydration-study-conditions.html", "What should an exercise hydration claim tell you about the heat?",
     "Read temperature, humidity and workload together before applying a fluid-balance experiment to a different setting.",
     ["https://pubmed.ncbi.nlm.nih.gov/42831410/",
      "https://www.cdc.gov/heat-health/about/index.html",
      "https://pubmed.ncbi.nlm.nih.gov/33513989/"],
     "An occupational hot-dry vs. warm-humid fluid-balance experiment, soccer heat and intensity study, and CDC heat-risk guidance. No personalized fluid recommendations."),
    ("P03-27", "cold-immersion-temperature-time-depth", "cold-water-immersion-temperature-vs-exposure.html", "Why doesn’t ice-bath temperature describe the whole exposure?",
     "See what to record beside water temperature when comparing studies that measured cooling after cold immersion.",
     ["https://pubmed.ncbi.nlm.nih.gov/31203599/",
      "https://rnli.org/water-safety/know-the-risks/cold-water-shock"],
     "Cold-immersion muscle cooling research and RNLI public water-safety context. No exposure prescription or safety threshold for an individual."),
    ("P03-31", "rnli-cold-water-shock-reading", "cold-water-shock-vs-cooling-water-safety.html", "What’s the difference between cold-water shock and gradual cooling?",
     "Use RNLI water-safety guidance to separate the risks that happen on entry, during swimming and across longer exposure.",
     ["https://rnli.org/water-safety/know-the-risks/cold-water-shock",
      "https://rnli.org/safety/float"],
     "Royal National Lifeboat Institution guidance for UK and Irish waters. The article distinguishes the timing of risks and refers to the official instructions."),
    ("P03-35", "elite-soccer-sweat-study-context", "elite-soccer-sweat-data-ordinary-workout.html", "Can an elite soccer sweat study tell you what you’ll lose at the gym?",
     "Read a study of elite players by training intensity and heat, then see why total sweat sodium and concentration are separate numbers.",
     ["https://pubmed.ncbi.nlm.nih.gov/33513989/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5634236/"],
     "Elite male soccer training study by intensity and environment, with the original NATA fluid-replacement position statement for measurement framing. Arithmetic examples are hypothetical."),
    ("P03-40", "tart-cherry-product-matching", "tart-cherry-marathon-study-vs-store-juice.html", "Does a tart cherry marathon study apply to the juice at your grocery store?",
     "Match the study beverage, timing and outcome before treating a carton of cherry juice as equivalent to the original trial.",
     ["https://researchportal.northumbria.ac.uk/en/publications/influence-of-tart-cherry-juice-on-indices-of-recovery-following-m/",
      "https://pubmed.ncbi.nlm.nih.gov/19883392/"],
     "Original Howatson et al. marathon trial and institutional archive. This guide audits product equivalence, not an individual intake schedule."),
    ("P03-37", "thirst-fluid-measures-diverge", "thirst-vs-hydration-measures-after-exercise.html", "Can thirst go away before you’ve replaced all the fluid you lost?",
     "Read an exercise study that compared when people stopped drinking with blood, urine and fluid-balance measures.",
     ["https://pubmed.ncbi.nlm.nih.gov/36235840/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5634236/"],
     "Original post-exercise drinking study and NATA fluid-replacement position statement. No guidance on personal fluid amounts."),
    ("P03-42", "race-vs-short-recovery-carbohydrate", "carbohydrate-timing-one-race-vs-two-sessions.html", "Why does carbohydrate timing matter differently when you exercise again soon?",
     "Compare the design of a muscle glycogen study with a repeat-exercise study and ask how much recovery time was available.",
     ["https://pubmed.ncbi.nlm.nih.gov/3132449/",
      "https://pubmed.ncbi.nlm.nih.gov/14767257/"],
     "Ivy et al. glycogen resynthesis experiment and original endurance-run study of carbohydrate feeding frequency during recovery."),
    ("P03-47", "caffeine-sleep-trial-rules", "caffeine-sleep-trial-usual-intake-and-timing.html", "What should a caffeine-and-sleep study say about participants’ usual coffee?",
     "Read two crossover-style sleep experiments by assigned dose, comparison conditions and what they measured after bedtime.",
     ["https://pubmed.ncbi.nlm.nih.gov/24235903/",
      "https://pubmed.ncbi.nlm.nih.gov/39377163/"],
     "Drake et al. placebo timing study and original dose-and-timing randomized crossover trial. The study settings are not individual intake instructions."),
    ("P04-26", "ferritin-hair-observation-treatment", "hair-shedding-ferritin-association-vs-treatment.html", "Does low ferritin in a hair-shedding study show that iron will help everyone?",
     "Follow the difference between an observational ferritin measurement and a trial that would measure a change in shedding.",
     ["https://pubmed.ncbi.nlm.nih.gov/20021982/",
      "https://pubmed.ncbi.nlm.nih.gov/32792884/"],
     "Two human observational studies of lab values in people with diffuse hair loss. Educational methods comparison without diagnosis thresholds, treatment or supplementation advice."),
    ("P05-25", "creatine-repeated-sprint-readouts", "creatine-repeated-short-sprints-peak-vs-mean-power.html", "What does a creatine study mean by better repeated sprints?",
     "Distinguish peak power, mean power and changes between repetitions using two original sprint protocols.",
     ["https://pubmed.ncbi.nlm.nih.gov/8599745/",
      "https://pubmed.ncbi.nlm.nih.gov/35334797/"],
     "Original cycling single- and repeated-sprint trial and original repeated treadmill-sprinting trial. No supplement regimen or cross-study effect estimate."),
    ("P05-28", "ashwagandha-human-trial-outcomes", "adaptogen-stress-study-scores-vs-hormone.html", "What does an “adaptogen” trial actually measure?",
     "Use an original ashwagandha extract trial to distinguish stress questionnaires from hormone measures and a broad marketing claim.",
     ["https://pubmed.ncbi.nlm.nih.gov/31517876/",
      "https://pubmed.ncbi.nlm.nih.gov/23439798/"],
     "Two original randomized placebo-controlled studies of specific ashwagandha extracts. Describes measured outcomes without dosing, eligibility advice or product endorsement."),
    ("P05-46", "cosmos-aging-clock-disagreement", "supplement-epigenetic-age-clock-cosmos-trial.html", "Can a supplement trial really tell you that you became biologically younger?",
     "Read why the COSMOS substudy tested multiple blood-based epigenetic clocks and what the measurements can establish.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC13696102/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC10148951/"],
     "Original COSMOS multivitamin and cocoa factorial trial substudy of epigenetic clocks, with original CALERIE clock and pace analysis as a methodological contrast."),
    ("P06-31", "core-power-total-added-sugars", "zero-added-sugar-five-grams-total-shake-label.html", "How can a protein shake have 5 g total sugar and zero added sugar?",
     "Use the U.S. Core Power chocolate label to see which line to record and what happens if you drink half the bottle.",
     ["https://fairlife.com/core-power/chocolate-protein-shake/",
      "https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label"],
     "U.S. fairlife Core Power chocolate, 26 g protein, one 14 fl oz labeled bottle, and FDA Nutrition Facts labeling guidance."),
    ("P06-17", "protein-value-allocation-split-receipt", "protein-per-dollar-two-meals-split-discount.html", "How should you split a discount when comparing the protein value of two meals?",
     "Work a two-item receipt under a percentage coupon and a targeted discount, then keep the protein totals separate from the price assumptions.",
     ["https://www.chick-fil-a.com/nutrition-allergens"],
     "Protein inputs from the official U.S. Chick-fil-A nutrition listings for the chicken sandwich and grilled chicken sandwich. Prices and discount terms are explicitly hypothetical."),
    ("P06-37", "raw-package-cooked-batch-portion", "raw-nutrition-label-weigh-cooked-batch.html", "How do you log a cooked portion using a label for raw weight?",
     "Work a package-to-cooked-weight example and see when discarded fat or liquid makes the shortcut less reliable.",
     ["https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label",
      "https://www.ars.usda.gov/ARSUserFiles/80400525/Data/retn/retn06.pdf"],
     "FDA serving-size guidance and USDA nutrient retention factors documentation. A hypothetical raw label and cooked-batch weights illustrate the arithmetic."),
    ("P06-19", "leftovers-uneven-components-diary", "log-uneven-restaurant-leftovers-components.html", "Can you log half an order when the leftovers aren’t evenly mixed?",
     "Use a component checklist to decide when half the weight represents half the order and when it doesn’t.",
     ["https://www.chipotle.com/nutrition-calculator"],
     "Official U.S. Chipotle customizable ingredient calculator as an example of distinct restaurant components. Leftover portions in the article are hypothetical."),
    ("P01-50", "fortified-oatmilk-poured-volume", "oatmilk-vitamin-d-full-carton-vs-one-serving.html", "How much vitamin D is in one cup versus a full carton of fortified oat milk?",
     "Compare the U.S. 32 fl oz and 8 fl oz Oatly Original labels and calculate the vitamin D for the volume you actually pour.",
     ["https://www.oatly.com/en-us/products/oatmilk/oatmilk-32-oz",
      "https://www.oatly.com/en-us/products/oatmilk/oatmilk-original-8-oz",
      "https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label"],
     "Manufacturer U.S. package listings for shelf-stable Oatly Original 32 fl oz and the 8 fl oz single package. Large-carton estimates inherit the label’s approximate count and rounding."),
    ("P02-21", "sardine-tin-salmon-fillet", "sardine-drained-tin-vs-salmon-fillet-protein.html", "Does a drained tin of sardines have more protein than a salmon fillet?",
     "Compare one USDA drained tin with two listed cooked salmon portions and see where the answer changes.",
     ["https://fdc.nal.usda.gov/food-details/175139/nutrients",
      "https://fdc.nal.usda.gov/food-details/175168/nutrients"],
     "USDA SR Legacy FDC 175139 drained Atlantic sardines in oil, with bones, and 175168 Atlantic farmed salmon, cooked with dry heat."),
    ("P02-22", "rotisserie-meat-yield-portions", "rotisserie-chicken-protein-breast-thigh-edible-weight.html", "How much protein is in the meat you pull from a rotisserie chicken?",
     "Calculate protein separately for weighed breast and thigh meat, leaving bones and discarded skin out of the estimate.",
     ["https://fdc.nal.usda.gov/food-details/171518/nutrients",
      "https://fdc.nal.usda.gov/food-details/171120/nutrients"],
     "USDA SR Legacy original-seasoning cooked rotisserie breast meat only and thigh meat only. Example portions are hypothetical edible weights."),
    ("P02-29", "deli-sliced-sodium-named-preparations", "deli-chicken-vs-roast-chicken-sodium-60g.html", "How much more sodium is in deli chicken than plain roasted chicken?",
     "Compare three USDA chicken breast entries at a 60 g sandwich serving and see why the preparation name matters.",
     ["https://fdc.nal.usda.gov/food-details/173874/nutrients",
      "https://fdc.nal.usda.gov/food-details/171518/nutrients",
      "https://fdc.nal.usda.gov/food-details/171477/nutrients"],
     "USDA SR Legacy prepackaged sliced deli chicken 173874, roast rotisserie breast 171518, and plain roasted breast 171477."),
    ("P02-30", "romaine-additions-protein-fiber", "salad-protein-add-ins-breast-chickpeas-feta.html", "What do chicken, chickpeas or feta add to a simple romaine salad?",
     "Build three versions of the same base with common portions and compare the protein and fiber added by each topping.",
     ["https://fdc.nal.usda.gov/food-details/169247/nutrients",
      "https://fdc.nal.usda.gov/food-details/171477/nutrients",
      "https://fdc.nal.usda.gov/food-details/173757/nutrients",
      "https://fdc.nal.usda.gov/food-details/173420/nutrients"],
     "USDA SR Legacy raw romaine, roasted chicken breast meat, boiled unsalted chickpeas, and feta. Dressings and other toppings excluded."),
    ("P02-32", "liver-vs-steak-matched-serving", "beef-liver-vs-steak-macros-why-separate-entries.html", "Why does beef liver need a different food entry from steak?",
     "Compare equal amounts of cooked beef liver and top-round steak, then see which dietary fields a steak substitute would misstate.",
     ["https://fdc.nal.usda.gov/food-details/168627/nutrients",
      "https://fdc.nal.usda.gov/food-details/171808/nutrients"],
     "USDA SR Legacy pan-fried beef liver (168627) and broiled lean select top-round steak (171808). Independent reference foods and preparations."),
    ("P02-33", "preformed-vitamin-a-liver-portion", "beef-liver-retinol-portion-and-vitamin-a-upper-limit.html", "Why does portion size matter so much for the vitamin A in liver?",
     "Use a named beef liver reference to calculate preformed vitamin A for two portions and interpret the upper limit accurately.",
     ["https://fdc.nal.usda.gov/food-details/168627/nutrients",
      "https://ods.od.nih.gov/factsheets/VitaminA-HealthProfessional/"],
     "USDA SR Legacy pan-fried beef liver retinol values and NIH discussion of the U.S. adult tolerable upper intake level for preformed vitamin A. No personal intake target or schedule."),
    ("P02-45", "bison-vs-beef-matched-round", "bison-vs-beef-top-round-ground-cut-comparison.html", "Is bison always leaner than beef? Start with the cut and preparation",
     "Compare cooked top-round references first, and see how the answer shifts when a ground bison entry is used instead.",
     ["https://fdc.nal.usda.gov/food-details/171808/nutrients",
      "https://fdc.nal.usda.gov/food-details/172600/nutrients",
      "https://fdc.nal.usda.gov/food-details/174422/nutrients"],
     "USDA SR Legacy broiled lean top-round bison and select beef, plus pan-broiled ground bison. Values are per 100 g cooked edible food."),
    ("P03-29", "cold-water-short-vs-training", "cold-water-immersion-soreness-vs-strength-training.html", "Can an ice bath feel helpful now and still change training gains later?",
     "Compare how two different cold-water studies measure recovery after one workout or adaptations after repeated strength sessions.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC4594298/",
      "https://pubmed.ncbi.nlm.nih.gov/30026562/"],
     "Roberts et al. resistance-training cold-water experiment and an original separate randomized trial of post-exercise markers and function. No immersion schedule or individualized advice."),
    ("P03-34", "electrolyte-water-composition", "what-electrolytes-add-to-water-sodium-potassium.html", "What do electrolytes add that plain water may not contain?",
     "Read the sodium, potassium and carbohydrate lines separately and see how water and electrolyte amounts answer different questions.",
     ["https://ods.od.nih.gov/factsheets/Potassium-HealthProfessional/",
      "https://www.gatorade.com/sports-drinks/gatorade-thirst-quencher/lemon-lime",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC5634236/"],
     "NIH potassium fact sheet, sports-fluid position statement, and U.S. Lemon Lime Gatorade as a product label example. Tap and bottled water composition can differ."),
    ("P03-39", "marathon-recovery-time-series", "marathon-recovery-soreness-and-blood-marker-timeline.html", "How do researchers tell when people recover after a marathon?",
     "Read a marathon study’s measurements over time and see how soreness, muscle tightness and a blood marker can create different recovery timelines.",
     ["https://pubmed.ncbi.nlm.nih.gov/25665742/",
      "https://pubmed.ncbi.nlm.nih.gov/32351588/"],
     "Two original human full-marathon observational analyses of soreness and indirect markers. No clearance for activity or clinical interpretation of laboratory results."),
    ("P03-44", "workload-match-recovery-trials", "recovery-supplement-compare-training-volume.html", "Is a recovery supplement trial relevant to your workout? Check the workload",
     "Compare two lower-body contexts and check why repetition counts, loading and concurrent exercise affect how useful the result is.",
     ["https://pubmed.ncbi.nlm.nih.gov/26578852/",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC4594298/"],
     "Original powdered tart cherry trial with a strenuous lower-body strength bout, and original repeated lower-body training research as a contrasting workload design."),
    ("P03-45", "regularity-vs-duration-sleep-routine", "sleepmaxxing-regularity-vs-sleep-duration.html", "Which part of a sleepmaxxing routine can you actually measure?",
     "Separate regular timing from total sleep duration using two example schedules and a study that measured sleep regularity.",
     ["https://pubmed.ncbi.nlm.nih.gov/28607474/",
      "https://pubmed.ncbi.nlm.nih.gov/40378648/"],
     "Original university-student sleep regularity and bedtime planning studies. Fictional schedules are measurement examples, with no personal sleep advice."),
    ("P04-06", "looksmaxxing-ordinal-rank-rules", "looksmaxxing-rankings-who-defines-the-scale.html", "What gets lost when a looksmaxxing chart ranks people’s faces?",
     "Check who defined the scale, whether raters agree, and what differences a ranking chart cannot establish.",
     ["https://www.ofcom.org.uk/online-safety/protecting-children/experiences-of-engaging-with-the-manosphere",
      "https://pubmed.ncbi.nlm.nih.gov/33690945/"],
     "Ofcom qualitative research about engaging with manosphere material and original validation of a specific clinical photonumeric scale. Does not reproduce rankings or provide personal ratings."),
    ("P04-10", "clinical-drainage-cosmetic-claim", "facial-lymphatic-drainage-cosmetic-vs-clinical.html", "What does facial lymphatic drainage mean in a spa claim versus clinical care?",
     "Identify who and what are being treated in a clinical program, and see why a photograph alone cannot show what fluid did.",
     ["https://www.cancer.gov/about-cancer/treatment/side-effects/lymphedema",
      "https://pubmed.ncbi.nlm.nih.gov/39487245/"],
     "NCI lymphedema information and indexed clinical literature as context. General distinction only, without technique, treatment or individual evaluation."),
    ("P04-16", "skin-rating-vs-elastic-test", "skin-aging-photo-grades-vs-elasticity-measurement.html", "Do visible skin-aging grades measure the same thing as elasticity?",
     "Compare a validated visual skin scale with a device-based elasticity measurement and see how their results can differ.",
     ["https://pubmed.ncbi.nlm.nih.gov/33690945/",
      "https://www.mdpi.com/2077-0383/13/18/5370"],
     "Original photonumeric scale validation and CollaSel Pro human trial measuring multiple test properties. Explains endpoints without product endorsement."),
    ("P02-18", "pasta-protein-smaller-portion", "high-protein-pasta-dry-label-vs-cooked-plate.html", "Can a smaller high-protein pasta serving have less protein than regular pasta?",
     "Use the Barilla red lentil serving and a USDA regular dry pasta reference to see what a high-protein headline leaves out.",
     ["https://www.barilla.com/en-us/products/pasta/legume/red-lentil-penne",
      "https://fdc.nal.usda.gov/food-details/169736/nutrients"],
     "U.S. Barilla red lentil penne manufacturer claim per 3.5 oz dry and USDA enriched dry pasta 169736. Calculations use uncooked portion weights."),
    ("P02-19", "pasta-boiling-sodium-reference", "pasta-cooked-with-salt-vs-without-sodium.html", "Does boiling pasta in salted water change what you should log?",
     "Compare two USDA cooked enriched pasta entries at bowl size and see which nutrient changes while protein stays the same.",
     ["https://fdc.nal.usda.gov/food-details/169737/nutrients",
      "https://fdc.nal.usda.gov/food-details/169751/nutrients"],
     "USDA SR Legacy enriched cooked pasta without added salt (169737) and with added salt (169751), compared at equal cooked weights. No estimate for an individual pot."),
    ("P02-25", "rice-lentil-amino-amounts", "rice-lentils-protein-mixed-meal-lysine-methionine.html", "What does “complete protein” leave out when you make a rice and lentil bowl?",
     "Read the protein, lysine and methionine amounts in two USDA cooked portions and see why the totals are separate from digestibility.",
     ["https://fdc.nal.usda.gov/food-details/169753/nutrients",
      "https://fdc.nal.usda.gov/food-details/172421/nutrients",
      "https://www.fao.org/4/i3124e/i3124e.pdf"],
     "USDA cooked enriched long-grain rice and boiled unsalted lentils, plus FAO Food and Nutrition Paper 92. Amino acid amounts are total reported contents, without adjustment for digestibility."),
    ("P02-27", "amino-acid-missing-label-profiles", "protein-compare-missing-amino-acid-entry.html", "Can you compare protein quality when the label leaves out the amino acids?",
     "Make the ordinary serving comparison you can support and leave the amino-acid comparison open when the required fields are absent.",
     ["https://www.fao.org/4/i3124e/i3124e.pdf",
      "https://www.accessdata.fda.gov/scripts/InteractiveNutritionFactsLabel/assets/InteractiveNFL_Protein_October2021.pdf"],
     "FDA Nutrition Facts explanation and FAO amino-acid scoring methods. Example entries are hypothetical, with missing states explicitly modeled."),
    ("P02-28", "restaurant-price-protein-calorie-ranks", "protein-per-calorie-vs-restaurant-cost.html", "Can the restaurant item with more protein per calorie cost more per gram?",
     "Use the two published Chick-fil-A U.S. sandwich records and an example price pair to calculate where the cost ranking flips.",
     ["https://www.chick-fil-a.com/menu/entrees/chick-fil-a-chicken-sandwich",
      "https://www.chick-fil-a.com/menu/entrees/grilled-chicken-sandwich"],
     "Official U.S. sandwich energy and protein portions. Prices are hypothetical and do not represent restaurant price claims."),
    ("P02-36", "animal-based-two-plates-fiber", "fiber-animal-based-plates-beans-vs-extra-chicken.html", "How much fiber changes when the side is beans instead of more chicken?",
     "Build two explicit plates from USDA cooked records and see how a side swap changes fiber, protein and energy.",
     ["https://fdc.nal.usda.gov/food-details/171477/nutrients",
      "https://fdc.nal.usda.gov/food-details/173735/nutrients"],
     "USDA roasted chicken breast meat and boiled unsalted black beans. Example plates are hypothetical and exclude added fat and sauces."),
    ("P02-43", "canned-fish-drained-sauce", "canned-sardines-tomato-sauce-drained-vs-whole-tin.html", "Can you use drained sardine nutrition for a whole tin with tomato sauce?",
     "Compare two USDA drained-fish descriptions and see when the sauce needs its own place in the calculation.",
     ["https://fdc.nal.usda.gov/food-details/175140/nutrients",
      "https://fdc.nal.usda.gov/food-details/175139/nutrients"],
     "USDA SR Legacy Pacific sardines in tomato sauce and Atlantic sardines in oil, both drained solids with bones. Different species and preparations, so the comparison does not isolate a sauce effect."),
    ("P02-48", "yogurt-package-usable-protein-value", "greek-yogurt-tub-vs-cup-protein-value.html", "Is a big Greek yogurt tub better value if you won’t finish it?",
     "Compare two U.S. yogurt packages with hypothetical prices, then recalculate the cost when only part of the tub is eaten.",
     ["https://chobani.com/products/yogurt-greek-nonfat-plain-large-size-tub",
      "https://shop.oikosyogurt.com/social/6967ec8a3b305cdbf5a92ee8"],
     "U.S. 32 oz plain nonfat Chobani at 16 g per listed serving and 5.3 oz Oikos Triple Zero Vanilla at 15 g per cup. Prices and consumed portions are explicitly hypothetical."),
    ("P04-23", "skin-glow-outcome-definitions", "skin-glow-claims-gloss-brightness-perception.html", "What does a “glow” claim actually measure?",
     "Separate measured gloss, measured color and people’s appearance ratings before comparing the results of skin studies.",
     ["https://pubmed.ncbi.nlm.nih.gov/40793458/",
      "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0133445"],
     "Original skin gloss measurement research in Japanese women and an original human skin-color study. Demonstrates outcome definitions, not a cosmetic outcome prediction."),
    ("P04-32", "comedogenicity-vs-diet-evidence", "noncomedogenic-claim-vs-diet-acne-evidence.html", "What does a noncomedogenic label tell you about food and acne?",
     "Identify whether the evidence tested direct contact with a product or a food exposure, and check the measured outcomes separately.",
     ["https://pubmed.ncbi.nlm.nih.gov/6229554/",
      "https://pubmed.ncbi.nlm.nih.gov/2940978/",
      "https://www.fda.gov/industry/fda-basics-industry/how-can-i-tell-if-my-product-cosmetic-drug-or-both"],
     "Historical product-screening and human assay examples, with FDA distinctions by intended use. No product or dietary recommendation."),
    ("P04-48", "before-after-controlled-white-balance", "before-after-skin-photo-control-light-distance.html", "What should match in a before-and-after skin photo?",
     "Use a controlled camera study to check distance, angle and lighting before deciding whether two images show a change.",
     ["https://onlinelibrary.wiley.com/doi/10.1002/jbio.202200381",
      "https://pubmed.ncbi.nlm.nih.gov/28197993/"],
     "Original smartphone camera experiment using skin-tone-based standards and original standardized clinical photography methods. This guide describes image measurement controls."),
    ("P05-02", "peptide-sequence-claim-identity", "what-is-a-peptide-sequence-and-product-claim.html", "What does the word “peptide” tell you about a product?",
     "Read a peptide description by sequence, final formulation and route before treating two products as equivalent.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC13137480/",
      "https://www.ncbi.nlm.nih.gov/books/NBK26883/"],
     "Original ChEBI peptide ontology research and molecular biology reference hosted by NCBI. General chemistry context without engineering, preparation or administration instructions."),
    ("P05-05", "copper-peptide-route-boundary", "ghk-cu-topical-evidence-vs-injectable-fda.html", "Does a skin study of GHK-Cu tell you anything about an injectable version?",
     "Check what the topical study tested and read the FDA’s separate safety statement for injectable compounding.",
     ["https://pubmed.ncbi.nlm.nih.gov/23744835/",
      "https://www.fda.gov/drugs/human-drug-compounding/certain-bulk-drug-substances-use-compounding-may-present-significant-safety-risks"],
     "Original topical copper tripeptide research in an irradiated rat wound model and current FDA statement on compounded injectable GHK-Cu. No instructions to obtain, make or use the substance."),
    ("P05-07", "human-trial-registry-vs-animal", "peptide-claim-human-trial-vs-animal-study.html", "How can you tell if a peptide claim actually has human trial results?",
     "Follow the source from an animal methods section or human registration to the exact population and posted results.",
     ["https://pubmed.ncbi.nlm.nih.gov/23744835/",
      "https://clinicaltrials.gov/study/NCT07614698",
      "https://clinicaltrials.gov/study-basics/how-to-read-study-record"],
     "Original copper tripeptide animal study and ClinicalTrials.gov human peptide-cream study record used for a source-reading exercise. The records need not study the same peptide or outcome."),
    ("P04-12", "salty-dinner-morning-photo-evidence", "salty-dinner-morning-puffiness-evidence.html", "Does a salty dinner explain a puffy face the next morning?",
     "Check what controlled sodium studies measured and why a morning photo cannot identify sodium as the cause.",
     ["https://pmc.ncbi.nlm.nih.gov/articles/PMC5409798/",
      "https://pubmed.ncbi.nlm.nih.gov/29206647/"],
     "Controlled sodium and water-balance studies. Neither source establishes a next-morning facial appearance effect from a particular dinner."),
    ("P04-13", "appearance-vs-hydration-composition", "puffiness-vs-body-fat-measurement.html", "Can a change in puffiness tell you that your body fat changed?",
     "Compare appearance, recorded body mass and an estimated composition measure in research on changed hydration.",
     ["https://pubmed.ncbi.nlm.nih.gov/19536161/",
      "https://pubmed.ncbi.nlm.nih.gov/28204901/"],
     "Two original hydration-related body-composition measurement studies, one using impedance and one using DXA. General measurement context, without estimating individual composition."),
    ("P04-28", "elimination-photo-multiple-changes", "changed-food-routine-photo-why-cause-unclear.html", "If your skin looks different after a food change, what did you actually test?",
     "Use a worked timeline to distinguish a single change from a bundle of changes and see what a comparison can establish.",
     ["https://www.bmj.com/content/389/bmj-2024-081124",
      "https://onlinelibrary.wiley.com/doi/10.1002/jbio.202200381"],
     "CONSORT 2025 explanation of trial design and original standardized camera experiment. The timeline is hypothetical and does not recommend eliminating any food."),
    ("P04-36", "cells-to-visible-skin-claim", "cell-study-vs-visible-skin-product-result.html", "Why doesn’t a skin-cell result prove that a product changes how skin looks?",
     "Use an original fibroblast study to separate its measured signal from a visible result in a person using a finished product.",
     ["https://pubmed.ncbi.nlm.nih.gov/25745767/",
      "https://www.bmj.com/content/389/bmj-2024-081124"],
     "Original study of GHK and its copper complex with normal human dermal fibroblasts, and CONSORT 2025 reporting guidance. No usage, production or formulation instructions."),
    ("P04-43", "bloating-distension-appearance-claims", "debloat-claims-bloating-vs-distension.html", "Do “debloat” food lists mean a symptom, a measurement or a photo?",
     "Use NIDDK definitions to separate feeling bloated, measured abdominal enlargement and appearance-only marketing.",
     ["https://www.niddk.nih.gov/health-information/digestive-diseases/gas-digestive-tract/symptoms-causes"],
     "NIDDK digestive symptom terminology. Educational comparison of outcomes and claims without elimination instructions, diagnosis or treatment."),
    ("P04-44", "influencer-diary-recall-and-time-order", "meal-diary-clear-skin-cause-claims.html", "Can an influencer’s meal diary explain why their skin cleared?",
     "Check timing, baseline and selective reporting with an example drawn from the limits of diet and acne questionnaires.",
     ["https://pubmed.ncbi.nlm.nih.gov/15692464/",
      "https://www.bmj.com/content/389/bmj-2024-081124"],
     "Published diet and acne recall-based observational research and CONSORT 2025 reporting guidance. The timeline is hypothetical and does not assign a dietary cause."),
    ("P04-49", "appearance-challenge-missing-outcomes", "appearance-challenge-progress-posts-selection.html", "What do appearance challenges leave out of their progress posts?",
     "Check who appears in the final montage, what counted as success, and how missing outcomes can change the story.",
     ["https://www.ofcom.org.uk/online-safety/protecting-children/experiences-of-engaging-with-the-manosphere",
      "https://www.bmj.com/content/389/bmj-2024-081124"],
     "Ofcom qualitative research about engaging with online appearance and self-improvement material, with CONSORT follow-up guidance used for an evidence comparison. Example is hypothetical."),
    ("P04-50", "visible-skin-supplement-prespecified", "skin-supplement-evidence-primary-visible-outcome.html", "What would count as evidence that a supplement changes how skin looks?",
     "Use an original collagen study and trial-reporting guidance to check which visible outcome was planned, measured and reported.",
     ["https://www.mdpi.com/2077-0383/13/18/5370",
      "https://www.bmj.com/content/389/bmj-2024-081124"],
     "Original human placebo-controlled collagen trial, with CONSORT 2025 guidance on reporting prespecified outcomes. This guide evaluates evidence design without recommending a product."),
    ("P05-27", "ashwagandha-pooled-extracts", "ashwagandha-meta-analysis-different-extracts.html", "Can an ashwagandha meta-analysis tell you which extract works best?",
     "Read the pooled result alongside two actual product trials and see what’s missing from an extract-versus-extract comparison.",
     ["https://pubmed.ncbi.nlm.nih.gov/36017529/",
      "https://pubmed.ncbi.nlm.nih.gov/31517876/",
      "https://pubmed.ncbi.nlm.nih.gov/23439798/"],
     "Akhgarjand et al. 2022 quantitative synthesis and two original placebo-controlled trials with specific formulations. No product, dose or treatment recommendation."),
    ("P05-29", "electrolyte-label-sodium-sugar-serving", "electrolyte-powder-label-lmnt-liquid-iv-sodium-sugar.html", "How do you compare sodium and sugar in electrolyte powder packets?",
     "Read two U.S. manufacturer labels per packet and scale the result when only part of a well-mixed drink is consumed.",
     ["https://drinklmnt.com/pages/ingredients",
      "https://drugwholesale.liquid-iv.com/products/liquid-i-v-hydration-multiplier-lemon-lime"],
     "U.S. LMNT powder and Liquid I.V. original Lemon Lime manufacturer data, ordinary single sticks. Compares label quantities without individual use advice."),
    ("P05-34", "antioxidant-claim-label-vs-outcome", "what-contains-antioxidants-food-label-actually-means.html", "Does “contains antioxidants” tell you what the product does for your health?",
     "Read the U.S. nutrient-content rule and distinguish an amount on a label from a measured biological or health outcome.",
     ["https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101/subpart-D/section-101.54",
      "https://ods.od.nih.gov/factsheets/VitaminC-HealthProfessional/"],
     "U.S. 21 CFR 101.54(g) nutrient-content labeling and NIH vitamin C fact sheet. Does not evaluate a specific advertisement’s legality or make a health claim."),
    ("P05-35", "antioxidant-biomarker-baseline-context", "antioxidant-study-marker-baseline-vs-health-outcomes.html", "What does it mean when an antioxidant study changes a blood marker?",
     "Read a randomized vitamin C and E trial by baseline values and the actual blood marker it measured.",
     ["https://pubmed.ncbi.nlm.nih.gov/18455517/",
      "https://pubmed.ncbi.nlm.nih.gov/21990298/"],
     "Original two-month randomized oxidative-stress marker study and original SELECT clinical-endpoint follow-up for a distinct context. No supplementation recommendation."),
    ("P05-37", "supplement-overlap-amounts-and-units", "supplement-stack-overlapping-ingredients-units.html", "How do you spot the same nutrient in two supplement labels?",
     "Work through a labeled-amount example for vitamin D and magnesium without adding percentages or the weight of a whole blend.",
     ["https://ods.od.nih.gov/factsheets/MVMS-HealthProfessional/",
      "https://ods.od.nih.gov/factsheets/VitaminD-HealthProfessional/",
      "https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling"],
     "NIH multivitamin and vitamin D fact sheets and FDA Supplement Facts labeling guide. The product amounts below are hypothetical."),
    ("P05-43", "powder-packet-bottle-normalization", "packet-vs-bottle-electrolyte-sodium-per-100ml.html", "Why can one electrolyte packet look stronger or weaker than a bottle?",
     "Use a single packet’s published sodium value to compare two example mixing volumes and a partial bottle.",
     ["https://drugwholesale.liquid-iv.com/products/liquid-i-v-hydration-multiplier-lemon-lime",
      "https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label"],
     "Liquid I.V. original U.S. Lemon Lime hydration multiplier packet with 500 mg labeled sodium, scaled in hypothetical container volumes. No mixing recommendation."),
    ("P05-44", "preworkout-caffeine-label-declared-serving", "preworkout-caffeine-serving-and-blend-label.html", "Where should you look for the caffeine amount on a pre-workout label?",
     "Distinguish a named caffeine amount from the weight of a blend and check one manufacturer’s current U.S. product example.",
     ["https://cellucor.com/products/c4-ultimate",
      "https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling"],
     "U.S. Cellucor C4 Ultimate manufacturer listing and FDA Supplement Facts guidance. Does not offer a dose or regimen."),
    ("P05-47", "caco2-iron-vs-human-outcome", "iron-bioavailability-cell-model-vs-human-absorption.html", "What does an in vitro iron bioavailability test tell you about people?",
     "Use a paired food study to distinguish an intestinal-cell prediction, human iron absorption and a longer-term health outcome.",
     ["https://pubmed.ncbi.nlm.nih.gov/17684210/",
      "https://pubmed.ncbi.nlm.nih.gov/28754026/"],
     "Original maize/bean study comparing Caco-2 estimates with human measures, and original human biofortified-bean analysis. No request for laboratory protocols or personal nutrition advice."),
    ("P05-50", "funded-study-who-rated-endpoints", "supplement-study-funded-who-rated-appearance.html", "What matters besides who paid for a skin supplement trial?",
     "Read a trial with disclosed product-company involvement and check who measured the outcomes and who was masked.",
     ["https://pubmed.ncbi.nlm.nih.gov/39021368/",
      "https://www.bmj.com/content/389/bmj-2024-081124"],
     "Original hydrolysed-collagen-supplement trial and original CONSORT 2025 reporting guidance. The paper’s disclosures distinguish product provision and employment from an assumption about other study roles."),
    ("P06-16", "local-menu-price-pair-record", "compare-restaurant-prices-same-location-channel.html", "What makes two restaurant prices fair to compare on the same day?",
     "Use a practical receipt checklist to match store, ordering channel, fees and portion before calculating a food value ranking.",
     ["https://www.chick-fil-a.com/customer-support/ordering-and-payment/digital-ordering-and-payment/where-can-i-find-the-prices-for-menu-items-at-my-restaurant",
      "https://www.chick-fil-a.com/customer-support/ordering-and-payment/digital-ordering-and-payment/i-selected-a-different-location-and-the-prices-changed",
      "https://www.chick-fil-a.com/customer-support/ordering-and-payment/delivery/how-much-does-chick-fil-a-delivery-cost"],
     "Chick-fil-A U.S. support pages on location-specific prices and delivery pricing. Reusable comparison checklist, not a live price collection."),
    ("P06-24", "powder-servings-scoop-weight", "compare-powder-scoop-sizes-by-grams.html", "What if two powders call one scoop a serving but the scoops are different?",
     "Use weight to compare two example powder labels and see why transferring a spoon between packages can misstate the portion.",
     ["https://www.metamucil.com/en-us/faqs/metamucil-faqs",
      "https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling"],
     "Manufacturer Metamucil FAQ on variation in serving volumes by formulation and FDA serving-label context. Weights and quantities in the comparison are explicitly hypothetical."),
    ("P06-30", "fiber-chia-topping-vs-bean-side", "fiber-chia-seed-topping-vs-black-beans-serving.html", "Does a spoonful of chia have more fiber than a side of black beans?",
     "Scale two USDA references to the amount actually served, then find the seed portion that matches the beans’ fiber.",
     ["https://fdc.nal.usda.gov/food-details/170554/nutrients",
      "https://fdc.nal.usda.gov/food-details/173735/nutrients"],
     "USDA SR Legacy dried chia seeds (170554) and unsalted boiled black beans (173735). Serving weights are explicit food amounts."),
    ("P06-35", "calculator-daily-to-one-meal", "daily-macro-calculator-set-one-meal-limit.html", "How do you turn a daily calorie estimate into one restaurant meal limit?",
     "Follow the GetMacros calculator handoff and compare a quarter-day shortcut, a third-day shortcut and an explicit one-meal limit.",
     ["https://getmacros.net/calculators.html",
      "https://getmacros.net/restaurant-meal-finder.html"],
     "GetMacros calculator result flow and finder handoff. Daily estimate and example limits are illustrative, not personal targets."),
    ("P06-39", "recipe-protein-fiber-rank-changes", "protein-vs-fiber-ranking-mixed-oat-bowls.html", "Can adding yogurt or chia change how two oatmeal bowls rank?",
     "Start with the same cooked oats and compute how a yogurt topping and a chia topping change the meal’s protein and fiber.",
     ["https://fdc.nal.usda.gov/food-details/173905/nutrients",
      "https://fdc.nal.usda.gov/food-details/170886/nutrients",
      "https://fdc.nal.usda.gov/food-details/170554/nutrients"],
     "Three USDA SR Legacy reference entries: oats cooked in water, plain low-fat yogurt, dried chia. Recipes and weighed amounts are explicit examples."),
    ("P06-40", "restaurant-source-edition-reproducibility", "restaurant-nutrition-source-edition-saved-comparison.html", "How do you check which menu edition a saved restaurant comparison used?",
     "Build a source note for a published Domino’s Canada example so the calculation can be reconstructed after a menu update.",
     ["https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf",
      "https://getmacros.net/dominos-canada-parmesan-stuffed-crust-two-slices.html"],
     "Domino’s Canada August 2026 nutrition guide and a GetMacros two-slice computation. The worked note describes the cited edition and need to recheck when using later data."),
    ("P06-41", "same-edition-strips-complete-order", "chick-fil-a-strips-kale-tea-sauce-complete-order.html", "What’s in a Chick-fil-A strips order with kale, tea and one sauce?",
     "Rebuild two U.S. orders from one nutrition guide using the same side, tea and sauce and changing only the strip count.",
     ["https://www.chick-fil-a.com/nutrition-allergens",
      "https://www.chick-fil-a.com/menu/entrees/chick-n-strips",
      "https://www.chick-fil-a.com/menu/sides/kale-crunch-side"],
     "Same retrieved U.S. Chick-fil-A nutrition guide for 2- and 3-count strips, regular 112 g kale, medium 604 g unsweet tea and one 12 g Honey Roasted BBQ packet. Composed totals are calculations."),
    ("P06-42", "equal-calories-realistic-edible-weights", "equal-calorie-food-comparison-check-serving-weight.html", "How much food is actually in an equal-calorie comparison?",
     "Convert a 400-calorie comparison into weights and then check the energy in examples you might actually serve.",
     ["https://fdc.nal.usda.gov/food-details/169247/nutrients",
      "https://fdc.nal.usda.gov/food-details/173735/nutrients",
      "https://fdc.nal.usda.gov/food-details/171477/nutrients"],
     "USDA SR Legacy raw romaine, boiled unsalted black beans and broiler breast meat roasted. All displays use edible food weight and the actual named reference."),
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
# These labels identify measured portions in the retained source records.
LISTED_PORTIONS = {
    171688: '1 medium (3" dia)',
    173944: '1 medium (7" to 7-7/8" long)',
    169097: '1 fruit (2-5/8" dia)',
    170457: '1 medium whole (2-3/5" dia)',
    169967: '0.5 cup, chopped',
    173904: '0.33 cup',
    173905: '1 cup',
    170158: '1 oz (22 whole kernels)',
    170886: '1 container (6 oz)',
    173424: '1 large',
    175139: '1 can (3.75 oz)',
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
    return [*ARTICLES, *(record['article'] for record in FOLLOWUP.values())]


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
            usable = [p for p in portions if p['grams'] > 0]
            preferred = LISTED_PORTIONS.get(source_id, '1 oz')
            portion = next((p for p in usable if p['label'] == preferred), None)
            if source_id in LISTED_PORTIONS:
                assert portion, f'Check the listed portion for USDA record {source_id}.'
            if not portion:
                portion = next(iter(usable), None)
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
    followup = FOLLOWUP.get(key)
    body = render_body(followup) if followup else (SOURCE / (key + '.html')).read_text(encoding='utf-8-sig').strip()
    if key == 'breakfast-fiber':
        body, restaurant_sources = breakfast_fiber(body)
        urls = list(dict.fromkeys([*urls, *restaurant_sources]))
    if key == 'uk-weight-coverage':
        body = uk_weight_coverage(body)
    if key == 'canada-sodium-coverage':
        body = canada_sodium_coverage(body)
    if key == 'uk-restaurant-alias-ranking':
        verify_uk_alias_ranking()
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
    source_date = FOLLOWUP_DATE if followup else 'November 20, 2026'
    sources = f'Source material checked {source_date}. ' + scope
    main = resource_main(dict(slug=slug, title=title, h1=title, description=summary,
                              category=pillar, sourceURLs=urls, sourceScope=sources, body=body, related=links))
    for url in urls:
        label = SOURCE_TITLES.get(url)
        if label:
            main = re.sub(r'(<a href="' + re.escape(escape(url, quote=True)) + r'">)[^<]+',
                          lambda match: match[1] + escape(label.strip()), main)
    byline = f'By GetMacros · Sources checked {source_date}'
    main = main.replace('By GetMacros · Published October 3, 2026', byline)
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
        main = main.replace(f'{byline}</p>',
                            f'{byline}</p>'
                            f'<p>Published <time datetime="{published}">{display_date}</time></p>', 1)
    return shell(slug, title, summary, main, schema, private=private)


def registry_market(market):
    return [row for row in json.loads((ROOT / 'js/order-registry.json').read_bytes())['records']
            if row['market'] == market]


def verify_uk_alias_ranking():
    rows = sorted(
        (row for row in registry_market('GB')
         if row.get('category') == 'entree' and isinstance(row.get('cal'), (int, float))
         and 0 < row['cal'] <= 650 and isinstance(row.get('p'), (int, float)) and row['p'] >= 20),
        key=lambda row: (-row['p'], row['cal'], row['name']))
    grouped = {}
    for row in rows:
        name = row['name'].removesuffix(' · Exclusive to Gatwick')
        fields = ('cal', 'p', 'c', 'fat', 'f', 'na', 'serving', 'source')
        grouped.setdefault((row['chain'], name, *(row.get(field) for field in fields)), row)
    distinct = list(grouped.values())
    assert (len(rows), len(distinct), len({row['chain'] for row in rows})) == (350, 333, 17)
    for chain, raw_count, distinct_count in (('Nando’s', 8, 7), ('Pepe’s', 1, 1), ('Wendy’s', 1, 2)):
        assert (sum(row['chain'] == chain for row in rows[:10]),
                sum(row['chain'] == chain for row in distinct[:10])) == (raw_count, distinct_count)
    assert all((row['cal'], row['p']) == (579, 78.7) for row in rows[:2])
    assert distinct[9]['name'].startswith('Chicken Benedict') and (distinct[9]['cal'], distinct[9]['p']) == (619, 50)


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
    followup = FOLLOWUP.get(row[1])
    if followup:
        return followup['topic']
    id_, key, *_ = row
    pillar = int(id_[1:3])
    if pillar == 1:
        if key in ('folate', 'niacin-equivalents', 'retinol-activity-equivalents'):
            return 'Reading nutrient values'
        if key.startswith(('vitamin-', 'b12-')) or key in ('boiled-broccoli-vitamin-c', 'apricot-drying-portion',
                                                           'orange-grapefruit-matched-grams', 'lentils-chickpeas-folate-iron'):
            return 'Vitamins in food'
        return 'Minerals and choline'
    if pillar == 2:
        if key in ('carnivore-survey-evidence', 'saladino-frameworks', 'blue-zones-pattern', 'blue-diet-meaning',
                   'santa-cruz-hydration-claim', 'predimed-trial-reanalysis', 'mediterranean-snack-vs-pattern'):
            return 'Diet and product claims'
        return 'Food comparisons'
    if pillar == 3:
        if 'cortisol-' in key or key.endswith('-cortisol'):
            return 'Stress measurements'
        if key in ('sports-drink-sodium-bottle', 'exercise-weight-change', 'urine-colour-sport-research'):
            return 'Hydration measurements'
        if key in ('infrared-sauna', 'cold-water-lifting', 'sauna-steam-humidity', 'water-vs-air-heat',
                   'contrast-water-comparator', 'soreness-ice-bath-trials', 'postexercise-soreness',
                   'oura-readiness-vs-strength', 'tart-cherry-outcomes'):
            return 'Exercise recovery'
        return 'Sleep and timing'
    if pillar == 4:
        if key in ('looksmaxxing-context', 'mogging-meaning', 'hypergamy-measure', 'softmaxxing-hardmaxxing'):
            return 'Online terms'
        return 'Marketing claims' if key in ('sponsored-beauty-posts', 'clinical-grade-labels') else 'Appearance research'
    if pillar == 5:
        if key in ('peptide-labels', 'bpc-regulatory-context'):
            return 'Peptides and policy'
        return 'Ingredient studies' if key in ('creatine-hair', 'magnesium-form-study') else 'Reading supplement labels'
    if key in ('breakfast-fiber', 'uk-weight-coverage', 'canada-sodium-coverage', 'uk-restaurant-alias-ranking',
               'taco-johns-limited-menu-count', 'selenium-ranking-coverage'):
        return 'GetMacros data studies'
    if key in ('uk-menu-salt-sodium', 'banana-edible-weight', 'diary-export-unknown', 'diary-saved-source-values',
               'calories-only-diary-backup', 'rice-volume-weight-log', 'weigh-food-from-package',
               'package-as-prepared-dinner', 'dual-column-package', 'beans-drained-recipe', 'week-label-rounding'):
        return 'Diary calculations'
    if key == 'fiber-serving-rank-reversal':
        return 'Food comparisons'
    return 'Restaurant comparisons'


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
    for row in public_articles():
        (ROOT / row[2]).write_text(article_page(row), encoding='utf8', newline='\n')
    if (SOURCE / (REVIEW_DRAFT[1] + '.html')).is_file():
        (DOCS / REVIEW_DRAFT[2]).write_text(article_page(REVIEW_DRAFT), encoding='utf8', newline='\n')
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
