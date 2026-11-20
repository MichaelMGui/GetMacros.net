"""Build the source-backed first wellness release and its compact food explorer."""
import argparse
import hashlib
import json
import re
import sys
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
EXPLORER = 'nutrient-density-explorer.html'
CLAIM_LIBRARY = 'wellness-claim-evidence.html'
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
     'chicken', 'P06-04', 'restaurant-meal-finder.html', 'Browse restaurant meals'),
]
SECTION_PAGES = tuple(section[0] for section in SECTIONS)
FDC = 'https://fdc.nal.usda.gov/food-details/{}/nutrients'
ODS = 'https://ods.od.nih.gov/factsheets/{}-HealthProfessional/'
# Evidence about treatment stays out of the public release queue pending specialist review.
ARTICLES = [
    ('P01-01', 'magnesium', 'magnesium-foods-by-portion.html', 'Which foods have the most magnesium in a real serving?',
     'Compare pumpkin seeds, black beans and spinach by weight and on the plate, with a worked bean-bowl example.',
     [ODS.format('Magnesium'), *[FDC.format(i) for i in (170557, 173735, 168463)]], 'Reference food composition.'),
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
    ('P01-14', 'vitamin-k-greens', 'vitamin-k-spinach-kale-broccoli-servings.html', 'Spinach, kale or broccoli: how much vitamin K is in a serving?',
     'Compare raw leaves and cooked greens. A side-dish example shows why a cup measure cannot establish what cooking does.',
     [ODS.format('VitaminK')], 'Reference food composition. The table does not establish nutrient retention after cooking.'),
    ('P01-15', 'selenium-food-portions', 'selenium-foods-tuna-sardines-eggs.html', 'Which foods provide selenium in a portion you actually eat?',
     'Compare yellowfin tuna, sardines, eggs and oatmeal. A smaller fish portion changes the comparison.',
     [ODS.format('Selenium')], 'U.S. reference food composition and serving calculations.'),
    ('P01-18', 'iodized-salt-pinch', 'iodine-in-iodized-salt-per-pinch.html', 'How much iodine is in a pinch of iodized salt?',
     'Compare iodized table salt and noniodized sea salt by a measured portion, and see why a pinch adds uncertainty.',
     [ODS.format('Iodine')], 'U.S. food composition and kitchen measurement. Amounts are examples, not sodium or iodine intake targets.'),
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
    ('P02-20', 'tuna-drained-packing', 'tuna-oil-vs-water-drained-weight.html', 'Tuna in oil vs. water: what still differs after draining?',
     'Compare two USDA records for drained, no-added-salt light tuna at 100 g and the same 3-ounce serving.',
     [FDC.format(174227), FDC.format(171986)], 'U.S. SR Legacy reference comparison. It does not isolate the effect of the packing medium in one experiment.'),
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
      'https://pubmed.ncbi.nlm.nih.gov/23836264/', FDC.format(173735)],
     'The program guide establishes its own claims. The primary study supplies observational evidence.'),
    ('P02-39', 'blue-diet-meaning', 'blue-diet-blue-zones-vs-aquatic-food.html', 'What does “Blue Diet” mean? Two very different uses of blue',
     'Tell the Blue Zones eating program apart from aquatic blue foods in food-system research.',
     ['https://www.bluezones.com/wp-content/uploads/2019/12/BZL_Food-Guidelines-Printable_02.pdf',
      'https://www.nature.com/articles/s41586-021-03917-1'],
     'Terminology and research literacy. The examples illustrate definitions, not a recommended eating plan.'),
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
    ('P04-14', 'skin-hydration-meaning', 'what-skin-hydration-studies-measure.html', 'What does a skin hydration study actually measure?',
     'Separate skin capacitance, elasticity and photo ratings, then check how soon a reading was taken after application.',
     ['https://pubmed.ncbi.nlm.nih.gov/11428963/'], 'Instrument and outcome literacy. No treatment or product ranking.'),
    ('P04-19', 'sleep-face-ratings', 'sleep-loss-face-photo-ratings.html', 'Does sleep change how you look in photos? What two studies rated',
     'Compare who was photographed, who rated the pictures, and why an observer’s impression does not measure skin health.',
     ['https://pubmed.ncbi.nlm.nih.gov/21156746/', 'https://pubmed.ncbi.nlm.nih.gov/28572989/'],
     'Interpretation of observer ratings from two experimental photography studies.'),
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
    ('P05-12', 'vitamin-d-label-units', 'vitamin-d-mcg-to-iu-on-label.html', 'Vitamin D on labels: how to convert micrograms and IU',
     'Convert both vitamin D units and two serving sizes without mistaking equivalent amounts for separate entries.',
     [ODS.format('VitaminD'), 'https://www.fda.gov/food/dietary-supplements-guidance-documents-regulatory-information/dietary-supplement-labeling-guide-chapter-iv-nutrition-labeling'],
     'U.S. label arithmetic. The example values are fictional and are not suggested doses.'),
    ('P05-17', 'fish-oil-epa-dha-label', 'fish-oil-1000-mg-vs-epa-dha.html', 'Why 1,000 mg of fish oil does not mean 1,000 mg of EPA and DHA',
     'Follow the oil, EPA and DHA lines in a real archived Supplement Facts panel and avoid adding the components twice.',
     ['https://api.ods.od.nih.gov/dsld/s3/pdf/326004.pdf'], 'Archived U.S. manufacturer label. The archive establishes the declaration for this edition.'),
    ('P05-22', 'creatine-hair', 'creatine-hair-loss-what-trials-measured.html', 'Does creatine cause hair loss? Two trials tested different things',
     'Compare an older DHT study with a 12-week randomized trial that measured hair directly.',
     ['https://pubmed.ncbi.nlm.nih.gov/19741313/', 'https://pubmed.ncbi.nlm.nih.gov/40265319/'],
     'Study interpretation. No dosing, supplement recommendation or clinical assessment.'),
    ('P05-26', 'magnesium-form-study', 'magnesium-citrate-oxide-absorption-study.html', 'Magnesium citrate vs. oxide: what does “better absorbed” mean?',
     'Compare elemental amounts on the label, then see what an absorption study measured and what outcomes it did not test.',
     [ODS.format('Magnesium'), 'https://pubmed.ncbi.nlm.nih.gov/2407766/'],
     'U.S. label literacy and interpretation of a small head-to-head absorption study. No supplement selection or dosing advice.'),
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
    ('P06-32', 'uk-menu-salt-sodium', 'greggs-salt-to-sodium-serving-conversion.html', 'How to convert Greggs’ salt figures to sodium',
     'Convert the September 2026 UK sausage roll and four-pack salt entries without mixing portions or treating salt as sodium.',
     ['https://a.storyblok.com/f/94904/x/7dd8489dab/nutritional-information.pdf', 'https://www.nidirect.gov.uk/articles/salt'],
     'Documented UK source portions and calculated sodium equivalents from rounded salt values.'),
    ('P06-33', 'week-label-rounding', 'weekly-food-log-nutrition-label-rounding.html', 'How much can food label rounding move a week of diary entries?',
     'Follow two hypothetical added-sugar numbers from the unrounded amount to the printed serving and the weekly total.',
     ['https://www.fda.gov/media/134505/download', 'https://www.fda.gov/food/nutrition-facts-label/added-sugars-nutrition-facts-label'],
     'U.S. label rounding example. The products and unrounded values are invented to illustrate the rule.'),
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
                             values={key: record['nutrients'].get(key) for key in (*NUTRIENTS, 'cal')}))
    return dict(rows=rows, nutrients={key: fields[key] for key in NUTRIENTS})


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


def explorer_page(data, script_url):
    def options(values, selected=None):
        return ''.join(f'<option value="{escape(key, quote=True)}"{" selected" if key == selected else ""}>{escape(label)}</option>'
                       for key, label in values)
    rows = sorted(data['rows'], key=lambda row: row['values']['magnesium'] if row['values']['magnesium'] is not None else -1, reverse=True)
    initial = ''.join('<tr><th scope="row">' + escape(row['label']) + '</th><td>100 g</td><td>' +
                      (str(row['values']['magnesium']) + ' mg' if row['values']['magnesium'] is not None else 'Unknown') +
                      f'</td><td><a href="{FDC.format(row["id"])}">USDA record {row["id"]}</a></td></tr>' for row in rows)
    summary = f'Compare {len(rows)} USDA reference foods by vitamins, minerals, protein or fiber per 100 g, per portion or per 100 calories.'
    nutrient_options = options((key, value['label']) for key, value in data['nutrients'].items())
    category_options = options((name, name) for name in FOODS)
    food_options = sorted(((str(row['id']),row['label']) for row in data['rows']), key=lambda row: row[1].casefold())
    payload = json.dumps(data, ensure_ascii=True, separators=(',', ':')).replace('<', '\\u003c')
    main = f'''<main id="main-content" class="container"><article class="article-container release-article">
<nav aria-label="Breadcrumb"><a href="/articles.html">Guides</a></nav>
<h1>Nutrient Density Explorer</h1><p>{escape(summary)}</p>
<p><a href="#compare-protein-and-fiber" data-macro-pair-link hidden>Compare protein and fiber side by side</a></p>
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
<h2>How the amounts are calculated</h2>
<p>A listed portion uses a measure with a weight in the source. For 100 calories, the tool divides by the source energy per 100 g and multiplies by 100. A missing amount or unavailable conversion stays unknown. The results show total nutrient content, which can differ from the amount absorbed.</p>
<p>These are selected U.S. reference foods. Use the exact preparation and source when comparing your own meal. For choline examples, see the separate <a href="/choline-foods-eggs-soybeans-quinoa.html">egg, soybeans and quinoa comparison</a>.</p>
<p><a href="/food-library.html">Search a larger set of reference and packaged foods</a> or <a href="/compare-foods.html">review exact portions side by side</a>.</p></article></main>'''
    page = shell(EXPLORER, 'Nutrient Density Explorer', summary, main)
    page = page.replace('data-family="article"', 'data-family="tool"', 1)
    page = page.replace('data-analytics-page="public"', 'data-analytics-page="off"', 1)
    page = page.replace('</head>', '''<style>
[data-nutrient-explorer] form:not([hidden]){display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem 1rem;align-items:start}
[data-nutrient-explorer] form>div{min-width:0}
[data-nutrient-explorer] form>div>label{display:block;margin-bottom:.25rem}
[data-nutrient-explorer] form :is(select,input[type="search"]){width:100%;min-inline-size:0;min-block-size:44px}
[data-nutrient-explorer] form>label{grid-column:1/-1}
[data-macro-pair] table{min-width:0;width:100%}
[data-macro-pair] th small,[data-macro-pair] th a{display:block;font-weight:400}
[data-macro-pair] td{white-space:nowrap;font-variant-numeric:tabular-nums}
@media(max-width:480px){[data-macro-pair] form:not([hidden]){grid-template-columns:1fr}}
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
    ]
    sources = {row[1]: row[5][0] for row in public_articles()}
    entries = ''.join(
        f'<section data-claim-example data-topic="{escape(topic, quote=True)}"><h2>{escape(question)}</h2>'
        f'<dl><dt>What the evidence supports</dt><dd>{escape(finding)}</dd>'
        f'<dt>What remains uncertain</dt><dd>{escape(limit)}</dd></dl><p>'
        f'<a href="/{slug}">Read the evidence guide</a> · <a href="{escape(sources[key], quote=True)}">Primary source</a></p></section>'
        for topic, question, finding, limit, slug, key in claims)
    summary = 'Check claims about raw milk, caffeine timing, gua sha and supplement labels against their primary sources.'
    choices = ''.join(f'<option>{escape(topic)}</option>' for topic, *_ in claims)
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
        if key in ('carnivore-survey-evidence', 'saladino-frameworks', 'blue-zones-pattern', 'blue-diet-meaning', 'santa-cruz-hydration-claim'):
            return 'Diet and product claims'
        return 'Food comparisons'
    if pillar == 3:
        if 'cortisol-' in key:
            return 'Stress measurements'
        return 'Exercise recovery' if key in ('infrared-sauna', 'cold-water-lifting') else 'Sleep and timing'
    if pillar == 4:
        if key in ('looksmaxxing-context', 'mogging-meaning', 'hypergamy-measure'):
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
