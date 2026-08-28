# -*- coding: utf-8 -*-
"""Expansion content, keyed by page slug.

Each entry adds information the page was missing: the number behind a claim,
a worked example, or the condition under which the usual advice stops holding.
"""

T = '<div class="table-scroll"><table class="data-table">%s</table></div>'


def rows(head, body):
    h = "<thead><tr>" + "".join(f'<th scope="col">{c}</th>' for c in head) + "</tr></thead>"
    b = "<tbody>" + "".join(
        "<tr>" + f'<th scope="row">{r[0]}</th>' +
        "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in body) + "</tbody>"
    return T % (h + b)


EXPANSIONS = {

"how-much-protein-per-day": [
 ("What the research actually recommends",
  "<p>The 0.8 g per kilogram figure on most nutrition labels is the RDA, and the RDA is "
  "a floor: the amount that prevents deficiency in 97.5% of healthy adults. It was never "
  "meant to describe the intake that best supports training, ageing or fat loss. Those "
  "sit considerably higher.</p>" +
  rows(["Situation", "Grams per kg", "For a 70 kg / 154 lb adult"], [
   ["Sedentary adult, RDA floor", "0.8", "56 g"],
   ["Generally active", "1.0&ndash;1.4", "70&ndash;98 g"],
   ["Training to build muscle", "1.6&ndash;2.2", "112&ndash;154 g"],
   ["Fat loss while training", "1.8&ndash;2.4", "126&ndash;168 g"],
   ["Adults over 65", "1.0&ndash;1.5", "70&ndash;105 g"],
  ]) +
  "<p>The range for muscle gain comes from a well-known meta-analysis of resistance-training "
  "studies, which found benefits levelling off around 1.6 g/kg, with the confidence interval "
  "reaching 2.2. Above that, added protein has not been shown to add muscle. It is not "
  "harmful in healthy people, but it is not doing the job it is being bought for.</p>"
  "<p>The fat-loss range is higher than the muscle-gain range for a reason that surprises "
  "people: in a calorie deficit protein protects lean mass, and there is less total energy "
  "coming in, so the proportion has to rise to hold the same absolute intake.</p>"),
 ("Why per-kilogram, and what to do if you carry excess fat",
  "<p>Protein needs scale with lean tissue, not total weight. For someone at a typical body "
  "composition, body weight is a close enough proxy. For someone carrying substantial excess "
  "fat, it is not: the formula will produce a number far above what the body can use, because "
  "fat mass has almost no protein requirement.</p>"
  "<p>The usual adjustment is to calculate against a goal weight or an estimate of lean mass "
  "rather than current weight. A 120 kg person targeting 2.0 g/kg would land at 240 g a day, "
  "which is impractical and unnecessary; calculating against an 85 kg goal weight gives 170 g, "
  "which is both achievable and sufficient.</p>"),
 ("Spreading it across the day",
  "<p>Total daily protein matters most. Distribution matters second, and the effect is real "
  "but smaller than the internet suggests. Muscle protein synthesis responds to a meal "
  "containing roughly 0.4 g/kg of protein, which is about 25&ndash;30 g for most adults, and "
  "the response lasts a few hours before returning to baseline.</p>"
  "<p>The practical consequence is that three or four meals each clearing that threshold beat "
  "one enormous dinner and two token meals, even at identical daily totals. Most people who "
  "miss their target are not short at dinner; they are eating 8 g at breakfast.</p>"
  "<p>There is no upper limit on how much protein the body can absorb from one meal. Absorption "
  "and use are different questions: a 60 g serving is absorbed, the surplus simply goes toward "
  "energy or other tissues rather than extra muscle.</p>"),
 ("When to get a target from a clinician instead",
  "<p>Higher protein intakes are well tolerated in healthy people; the concern about protein "
  "harming healthy kidneys has not held up in controlled trials. That finding does not extend "
  "to people who already have reduced kidney function, where protein intake is a clinical "
  "decision and often a restricted one.</p>"
  "<p>Get a target from your own clinician rather than a general guide if you have chronic "
  "kidney disease or reduced kidney function, liver disease, are pregnant or breastfeeding, or "
  "are recovering from an eating disorder, where numeric targets can do more harm than good.</p>"),
],

"protein-for-muscle-growth": [
 ("How much of a difference protein actually makes",
  "<p>Protein is necessary for muscle growth and is not sufficient for it. The training "
  "stimulus decides whether growth happens at all; protein decides whether the raw material "
  "is there when it does. Someone eating 2.2 g/kg without a progressive training program "
  "will not build meaningful muscle, and the failure will not be nutritional.</p>"
  "<p>Within a training program, the dose response is steep at first and flattens quickly:</p>" +
  rows(["Daily protein", "Effect on muscle gain"], [
   ["Below 1.2 g/kg", "Growth is limited by protein availability"],
   ["1.2&ndash;1.6 g/kg", "Most of the available benefit is captured here"],
   ["1.6&ndash;2.2 g/kg", "Small additional benefit, well supported"],
   ["Above 2.2 g/kg", "No demonstrated additional muscle"],
  ]) +
  "<p>Going from 0.8 to 1.6 g/kg is a meaningful change. Going from 1.8 to 2.6 is buying very "
  "little at considerable cost and appetite pressure.</p>"),
 ("Leucine, and why the source matters less than the total",
  "<p>The amino acid leucine acts as the trigger for muscle protein synthesis, and a meal needs "
  "roughly 2&ndash;3 g of it to hit the threshold. That is one reason 25&ndash;30 g of a "
  "complete protein is the usual per-meal recommendation: it reliably clears the leucine bar.</p>"
  "<p>Animal proteins hit it in smaller servings because they carry more leucine per gram. Plant "
  "proteins get there too, but the serving has to be larger, and the practical fix is volume "
  "plus variety rather than any single ingredient. Someone eating entirely plant-based is "
  "usually advised to aim near the top of the range, around 1.8&ndash;2.0 g/kg, to compensate.</p>"),
 ("The mistakes that actually cost people muscle",
  "<ul>"
  "<li><strong>Undereating overall.</strong> In a deficit, muscle gain is slow at best. Protein "
  "cannot substitute for the energy the process requires.</li>"
  "<li><strong>Breakfast and snacks at near-zero protein.</strong> The most common cause of "
  "missing a daily target, and the easiest to fix.</li>"
  "<li><strong>Counting protein from foods that barely contain it.</strong> A cup of rice "
  "contributes 4 g, not a meaningful share of a 140 g target.</li>"
  "<li><strong>Chasing timing while missing the total.</strong> Whether the shake lands 20 or "
  "90 minutes after training is a rounding error next to whether the day reached 1.6 g/kg.</li>"
  "</ul>"),
],

"protein-before-bed": [
 ("What the overnight studies found",
  "<p>The research most often cited comes from a group in Maastricht, which fed 40 g of casein "
  "before sleep and measured overnight muscle protein synthesis. It rose meaningfully compared "
  "with a placebo. Later training studies found modest additional gains in muscle size and "
  "strength when a pre-sleep protein dose was added to a resistance-training program.</p>"
  "<p>The size of the effect is the part usually lost in the retelling. It is a real but small "
  "addition, and in most of those trials the pre-sleep dose also raised total daily protein. "
  "When total protein is matched, the specific advantage of the bedtime timing shrinks "
  "considerably. It is likelier that the extra protein did most of the work.</p>"),
 ("Casein, and whether the type matters",
  "<p>Casein digests slowly, releasing amino acids over several hours rather than spiking and "
  "clearing like whey. That is the mechanistic argument for using it overnight, and it is a "
  "reasonable one. In practice, whole foods with a similar profile do the same job: Greek "
  "yogurt, cottage cheese and milk are all casein-dominant.</p>" +
  rows(["Option", "Protein", "Notes"], [
   ["Casein powder, 40 g", "~32 g", "The dose used in the research"],
   ["Cottage cheese, 1 cup", "~25 g", "Casein-dominant whole food"],
   ["Greek yogurt, 200 g", "~20 g", "Add more if the target needs it"],
   ["Milk, 500 ml", "~17 g", "Roughly 80% casein"],
  ]) +
  "<p>Around 30&ndash;40 g is the range that has been tested. Smaller amounts have not been "
  "shown to produce the same overnight response.</p>"),
 ("Whether it is worth doing",
  "<p>It is worth doing if it helps you reach a daily protein target you would otherwise miss, "
  "which for many people it does &mdash; the evening is when there is appetite and time. It is "
  "not worth losing sleep over, in either sense. If eating before bed disrupts your sleep or "
  "causes reflux, the small synthesis advantage does not compensate for worse recovery.</p>"
  "<p>It also does not cause fat gain by virtue of being late. Total daily energy decides that. "
  "The idea that calories eaten after a particular hour are stored differently has been tested "
  "repeatedly and has not held up.</p>"),
],

"how-to-calculate-macros-by-hand": [
 ("A full worked example",
  "<p>The arithmetic below is the whole method, run start to finish for one person: a 32-year-old "
  "woman, 68 kg, 165 cm, training four times a week, aiming for gradual fat loss.</p>"
  "<p><strong>Step 1 &mdash; resting energy (Mifflin-St Jeor).</strong><br>"
  "For women: (10 &times; kg) + (6.25 &times; cm) &minus; (5 &times; age) &minus; 161<br>"
  "(10 &times; 68) + (6.25 &times; 165) &minus; (5 &times; 32) &minus; 161 = 680 + 1031 &minus; 160 &minus; 161 = "
  "<strong>1,390 kcal</strong></p>"
  "<p><strong>Step 2 &mdash; daily burn.</strong> Multiply by an activity factor. Four sessions a "
  "week is 1.55.<br>1,390 &times; 1.55 = <strong>2,155 kcal</strong></p>"
  "<p><strong>Step 3 &mdash; adjust for the goal.</strong> A 15&ndash;20% deficit is the usual "
  "range for fat loss without excessive muscle loss.<br>2,155 &times; 0.8 = <strong>1,724 kcal</strong></p>"
  "<p><strong>Step 4 &mdash; set protein first.</strong> Fat loss while training: 1.8&ndash;2.4 g/kg. "
  "Take 2.0.<br>68 &times; 2.0 = <strong>136 g protein</strong> = 136 &times; 4 = 544 kcal</p>"
  "<p><strong>Step 5 &mdash; set fat.</strong> 25&ndash;30% of calories, with about 0.5 g/kg as a "
  "floor for hormone function.<br>1,724 &times; 0.28 = 483 kcal &divide; 9 = <strong>54 g fat</strong></p>"
  "<p><strong>Step 6 &mdash; carbohydrate takes the remainder.</strong><br>"
  "1,724 &minus; 544 &minus; 483 = 697 kcal &divide; 4 = <strong>174 g carbohydrate</strong></p>"
  "<p><strong>Result:</strong> 1,724 kcal, 136 g protein, 54 g fat, 174 g carbohydrate.</p>"),
 ("The numbers you need to remember",
  rows(["Quantity", "Value"], [
   ["Protein", "4 kcal per gram"],
   ["Carbohydrate", "4 kcal per gram"],
   ["Fat", "9 kcal per gram"],
   ["Alcohol", "7 kcal per gram"],
   ["1 kg body weight", "2.2 lb"],
   ["1 inch", "2.54 cm"],
  ]) +
  "<p>Activity multipliers: 1.2 mostly sitting, 1.375 light activity one to three days a week, "
  "1.55 moderate three to five days, 1.725 hard six to seven days, 1.9 very hard or a physical "
  "job. Most people overestimate here, and the error compounds through every later step.</p>"),
 ("Why the answer is an estimate, not a measurement",
  "<p>Mifflin-St Jeor predicts resting energy expenditure to within about 10% for most people, "
  "which on a 2,000 kcal target is a 200 kcal band. The activity multiplier is cruder still: it "
  "compresses everything from job type to fidgeting into five options.</p>"
  "<p>Treat the output as a starting point to test rather than a fact about your body. Hold it "
  "for two to three weeks, track weight trend rather than single mornings, and adjust by "
  "10&ndash;15% if the trend is not going where you intended. The number that survives that "
  "process is worth more than any equation's first guess.</p>"),
],
}


EXPANSIONS.update({

"creatine-explained": [
 ("Dosing: two routes to the same place",
  "<p>Creatine works by topping up phosphocreatine in muscle, which regenerates ATP during "
  "short, hard efforts. Saturation is the goal, and there are two ways to reach it.</p>" +
  rows(["Protocol", "Dose", "Time to saturation"], [
   ["Loading then maintenance", "20 g/day (4 &times; 5 g) for 5&ndash;7 days, then 3&ndash;5 g", "About 1 week"],
   ["Maintenance only", "3&ndash;5 g/day from the start", "About 3&ndash;4 weeks"],
  ]) +
  "<p>Both arrive at the same muscle creatine content. Loading is faster and more likely to "
  "cause stomach upset; splitting the 20 g into four doses reduces that. There is no benefit "
  "to exceeding 5 g a day once saturated &mdash; the surplus is excreted.</p>"
  "<p>Timing is close to irrelevant. Saturation is a stock, not a flow, so what matters is "
  "taking it consistently rather than taking it at a particular hour.</p>"),
 ("What it does and does not do",
  "<p>Creatine monohydrate is among the most studied supplements in sports nutrition, and the "
  "effects are consistent for high-intensity, short-duration work: a few extra repetitions, "
  "slightly better sprint repeatability, and over months of training, more accumulated volume "
  "and therefore more muscle. Typical strength gains in trials run a few percent above training "
  "alone, which is meaningful but not transformative.</p>"
  "<p>It does not help endurance performance in any reliable way. Roughly 20&ndash;30% of people "
  "are non-responders, usually those whose muscle creatine is already high from a meat-heavy "
  "diet. Vegetarians tend to respond most, having the least to begin with.</p>"),
 ("Water weight, safety and the forms worth paying for",
  "<p>The 1&ndash;2 kg gained in the first weeks is intracellular water drawn into muscle, not "
  "fat and not bloating. It is a sign the supplement is doing what it does.</p>"
  "<p>Long-term studies in healthy adults have not found kidney or liver harm at standard doses. "
  "Creatine does raise serum creatinine, a marker used to estimate kidney function, which can "
  "produce an alarming blood test result in a healthy person &mdash; worth mentioning to a "
  "clinician before testing. People with existing kidney disease should ask first.</p>"
  "<p>Monohydrate is the form used in nearly all the research and the cheapest on the shelf. "
  "Hydrochloride, buffered and liquid versions cost more without evidence of an advantage.</p>"),
],

"caffeine-and-athletic-performance": [
 ("The dose that has actually been tested",
  "<p>Performance trials cluster around 3&ndash;6 mg per kilogram of body weight, taken about "
  "60 minutes before exercise. For a 70 kg person that is 210&ndash;420 mg.</p>" +
  rows(["Source", "Typical caffeine"], [
   ["Brewed coffee, 240 ml", "80&ndash;120 mg"],
   ["Espresso, single", "60&ndash;80 mg"],
   ["Energy drink, 250 ml", "80&ndash;150 mg"],
   ["Pre-workout serving", "150&ndash;300 mg"],
   ["Caffeine tablet", "100&ndash;200 mg"],
   ["Black tea, 240 ml", "40&ndash;70 mg"],
  ]) +
  "<p>Above roughly 6 mg/kg the performance benefit stops increasing while jitteriness, raised "
  "heart rate and disrupted sleep continue to. More is not better past that point; it is "
  "simply worse.</p>"),
 ("What it improves, and by how much",
  "<p>The effect is best established for endurance: time-trial performance improves by roughly "
  "2&ndash;4% in trained cyclists and runners, which is a large margin in competitive terms. "
  "Perceived effort drops at the same workload, which is likely much of the mechanism.</p>"
  "<p>For strength and power the picture is smaller and less consistent &mdash; a modest "
  "improvement in repetitions to failure and in repeated sprints, less reliable for a one-rep "
  "maximum.</p>"
  "<p>Habitual coffee drinkers still get a benefit. Tolerance develops to some effects, but "
  "trials that control for habitual intake generally still find a performance response.</p>"),
 ("The cost side of the ledger",
  "<p>Caffeine has a half-life of around five hours in most adults, meaning a 200 mg dose at "
  "4 pm still has roughly 100 mg circulating at 9 pm. Its effect on sleep is the most reliable "
  "downside, and lost sleep costs more athletically than the caffeine gains. A cut-off eight "
  "hours before bed is a defensible default.</p>"
  "<p>Genetics matter more here than for most supplements: variation in the CYP1A2 enzyme means "
  "some people clear caffeine in half the time others do. If it keeps you awake for an entire "
  "night, that is a physiological difference, not a lack of discipline.</p>"),
],

"protein-timing": [
 ("The anabolic window, tested",
  "<p>The idea that muscle protein synthesis requires protein within 30&ndash;60 minutes of "
  "training came from early studies that mostly compared a post-workout dose against nothing at "
  "all. When later work controlled for total daily protein, the timing advantage largely "
  "disappeared.</p>"
  "<p>A widely cited meta-analysis found that the apparent benefit of post-exercise timing was "
  "explained by the higher total protein intake in the timed groups. Once totals matched, the "
  "window stopped mattering much. The practical window is measured in hours, not minutes.</p>"),
 ("What the evidence does support",
  "<ul>"
  "<li><strong>Total daily protein</strong> is the dominant variable, by a wide margin.</li>"
  "<li><strong>Distribution across three to four meals</strong>, each around 0.4 g/kg, produces "
  "a slightly better response than the same total taken unevenly.</li>"
  "<li><strong>Training fasted</strong> is the one case where a nearby dose matters more, "
  "because the previous meal is many hours behind.</li>"
  "<li><strong>Pre-sleep protein</strong> has modest support, mostly because it raises the daily "
  "total.</li>"
  "</ul>"
  "<p>If you ate a protein-containing meal within a few hours of training, the post-workout "
  "shake is convenience rather than physiology.</p>"),
],

"complete-vs-incomplete-protein": [
 ("What complete actually means",
  "<p>Nine amino acids are essential: histidine, isoleucine, leucine, lysine, methionine, "
  "phenylalanine, threonine, tryptophan and valine. The body cannot make them, so they must "
  "come from food. A complete protein supplies all nine in proportions that meet human "
  "requirements.</p>"
  "<p>Most animal proteins are complete. Most single plant proteins are not, though the label "
  "overstates the problem: they are rarely missing an amino acid outright, they are low in one "
  "relative to need. That shortfall is the limiting amino acid.</p>" +
  rows(["Food group", "Usually limiting in"], [
   ["Grains (rice, wheat, oats)", "Lysine"],
   ["Legumes (beans, lentils)", "Methionine"],
   ["Nuts and seeds", "Lysine"],
   ["Soy, quinoa, buckwheat", "Nothing &mdash; complete"],
  ])),
 ("Why combining at every meal is not required",
  "<p>The older advice to pair rice with beans in the same sitting came from a 1970s "
  "popularization, and the author later withdrew it. The body maintains a free amino acid pool "
  "that buffers across meals, so complementary proteins eaten across a day work as well as "
  "those eaten together.</p>"
  "<p>What does still matter is variety and total quantity. A plant-based diet drawing on "
  "grains, legumes, soy, nuts and seeds across the day covers the requirement. A plant-based "
  "diet built almost entirely on one food group can genuinely run short.</p>"
  "<p>Because plant proteins are generally less digestible and lower in leucine, a common "
  "recommendation for people eating entirely plant-based is to target the upper end of the "
  "protein range &mdash; nearer 1.8&ndash;2.0 g/kg when training &mdash; rather than treating "
  "the totals as interchangeable.</p>"),
],

"net-carbs-vs-total-carbs": [
 ("The arithmetic, and where it goes wrong",
  "<p>Net carbohydrate is a calculation, not a regulated term. In the United States the usual "
  "form is:</p>"
  "<p><strong>Net carbs = total carbohydrate &minus; fiber &minus; sugar alcohols</strong></p>"
  "<p>The logic is that fiber is not digested to glucose and most sugar alcohols are absorbed "
  "poorly, so neither raises blood glucose the way starch or sugar does. As far as it goes, "
  "that is sound.</p>"
  "<p>Where it breaks down is in the subtraction of sugar alcohols. They are not equivalent:</p>" +
  rows(["Sugar alcohol", "Roughly how much affects blood glucose"], [
   ["Erythritol", "Almost none &mdash; largely excreted unchanged"],
   ["Xylitol", "Partial"],
   ["Maltitol","Substantial &mdash; roughly half that of sugar"],
   ["Sorbitol", "Partial"],
  ]) +
  "<p>Subtracting maltitol in full, as many products do, understates the real glycemic load. A "
  "bar claiming 2 g net carbs on 20 g of maltitol is not behaving like a 2 g food.</p>"),
 ("Which number to use",
  "<p>For most people, total carbohydrate is the more honest figure and the one worth tracking. "
  "Net carbs are useful in two narrower cases: following a ketogenic diet, where the point is "
  "specifically to limit glucose-raising carbohydrate, and carbohydrate counting for insulin "
  "dosing, where the practice varies and should follow a clinician's guidance rather than a "
  "package.</p>"
  "<p>Outside those, the label serves marketing more than the eater. A product engineered to "
  "show a low net-carb number often carries the same calories as the food it replaces.</p>"),
],
})


EXPANSIONS.update({

"saturated-vs-unsaturated-fat": [
 ("The structural difference, and why it matters",
  "<p>Saturated fatty acids have no double bonds in their carbon chain &mdash; every position "
  "is saturated with hydrogen. That lets the molecules pack tightly, which is why butter, lard "
  "and coconut oil are solid at room temperature. Unsaturated fats carry one double bond "
  "(monounsaturated) or several (polyunsaturated); each bend prevents tight packing, so olive "
  "oil and sunflower oil pour.</p>" +
  rows(["Type", "Main sources", "Typical effect on LDL cholesterol"], [
   ["Saturated", "Butter, fatty meat, cheese, coconut and palm oil", "Raises it"],
   ["Monounsaturated", "Olive oil, avocado, almonds, cashews", "Neutral to lowering"],
   ["Polyunsaturated omega-6", "Sunflower, soybean, corn oil, walnuts", "Lowers it"],
   ["Polyunsaturated omega-3", "Oily fish, flax, chia, walnuts", "Mainly lowers triglycerides"],
   ["Industrial trans", "Partially hydrogenated oils", "Raises LDL, lowers HDL"],
  ])),
 ("What the replacement evidence shows",
  "<p>The most useful way to read the research is as a substitution question: not whether "
  "saturated fat is bad in isolation, but what happens when it is replaced with something "
  "else.</p>"
  "<p>Replacing saturated fat with polyunsaturated fat consistently lowers cardiovascular risk "
  "in controlled trials and cohort studies. Replacing it with monounsaturated fat looks "
  "favorable too. Replacing it with refined carbohydrate shows little or no benefit, which is "
  "why the low-fat era did not deliver what it promised.</p>"
  "<p>That nuance is the reason blanket statements in both directions are wrong. Saturated fat "
  "is not inert, and it is also not uniquely dangerous regardless of what replaces it.</p>"),
 ("Practical targets",
  "<p>Major guidelines put saturated fat under about 10% of daily calories, and cardiology "
  "bodies often suggest under 7% for people at elevated risk. On a 2,000 kcal diet, 10% is "
  "roughly 22 g.</p>"
  "<p>Industrial trans fat is the one category with no safe intake; it has been largely removed "
  "from the food supply in many countries. On a label, 'partially hydrogenated oil' in the "
  "ingredients is the tell, since rounding rules allow a product with under 0.5 g per serving "
  "to print 0 g.</p>"),
],

"simple-vs-complex-carbs": [
 ("Why the simple/complex split is a weak guide",
  "<p>The distinction is structural: simple carbohydrates are one or two sugar units, complex "
  "ones are long chains of glucose. The implication usually drawn &mdash; that simple means "
  "fast and complex means slow &mdash; does not survive contact with real foods.</p>" +
  rows(["Food", "Type", "Glycemic index (approx.)"], [
   ["White bread", "Complex (starch)", "~75 &mdash; high"],
   ["Baked potato", "Complex (starch)", "~85 &mdash; high"],
   ["Apple", "Simple (fructose, sucrose)", "~36 &mdash; low"],
   ["Milk", "Simple (lactose)", "~31 &mdash; low"],
   ["Lentils", "Complex (starch + fiber)", "~29 &mdash; low"],
  ]) +
  "<p>A baked potato raises blood glucose faster than an apple, despite being the complex one. "
  "Starch made of glucose chains is broken to glucose quickly; fructose in fruit is metabolized "
  "differently and arrives slowly, with fiber slowing it further.</p>"),
 ("What actually determines the response",
  "<ul>"
  "<li><strong>Fiber content.</strong> Slows gastric emptying and glucose absorption.</li>"
  "<li><strong>Fat and protein in the same meal.</strong> Both blunt the rise substantially.</li>"
  "<li><strong>Processing.</strong> Milling and grinding increase surface area; whole oats and "
  "instant oats behave differently.</li>"
  "<li><strong>Physical form.</strong> Whole fruit and juice from the same fruit are not the "
  "same food once the cell structure is gone.</li>"
  "<li><strong>Cooking and cooling.</strong> Cooling cooked potato or rice forms resistant "
  "starch, lowering the glycemic response on reheating.</li>"
  "</ul>"
  "<p>A more useful question than simple-versus-complex is what else came with the "
  "carbohydrate: fiber, water and micronutrients, or very little.</p>"),
],

"protein-powder-101": [
 ("How the main types differ",
  rows(["Type", "Protein per 30 g scoop", "Digestion", "Best suited to"], [
   ["Whey concentrate", "~22&ndash;24 g", "Fast", "General use, best value"],
   ["Whey isolate", "~25&ndash;27 g", "Fast", "Lactose sensitivity, leanest option"],
   ["Whey hydrolysate", "~25&ndash;27 g", "Fastest", "Little practical advantage for the price"],
   ["Casein", "~24 g", "Slow, over hours", "Before sleep, or long gaps between meals"],
   ["Soy", "~23 g", "Moderate", "Complete plant option"],
   ["Pea", "~21&ndash;24 g", "Moderate", "Plant-based; low in methionine"],
   ["Rice", "~20&ndash;22 g", "Moderate", "Usually blended with pea to complete it"],
  ]) +
  "<p>Whey concentrate is typically 70&ndash;80% protein by weight, isolate 90% or more. The "
  "difference is mostly lactose and fat, which matters for tolerance and for a strict calorie "
  "budget, and rarely for muscle.</p>"),
 ("Whether you need it at all",
  "<p>Powder is food, not medicine. It has no anabolic property that chicken or lentils lack; "
  "it is a convenient, cheap, shelf-stable way to add 25 g of protein without cooking. Someone "
  "already hitting their target from whole food gains nothing by adding it.</p>"
  "<p>Cost is worth comparing on protein rather than tub price. At &pound;25 for 1 kg of an 80% "
  "concentrate, that is about &pound;0.031 per gram of protein &mdash; usually cheaper than "
  "chicken breast and much cheaper than protein bars.</p>"),
 ("Quality and what to look for on the label",
  "<p>Supplements are regulated less strictly than food in most countries, and independent "
  "testing has repeatedly found products whose protein content differs from the label, or that "
  "contain heavy metals at levels worth noting. Third-party certification &mdash; Informed "
  "Sport, NSF Certified for Sport &mdash; is the practical check, and is essential for anyone "
  "subject to drug testing.</p>"
  "<p>Amino spiking is the other thing to watch: cheap free amino acids such as glycine and "
  "taurine raise measured nitrogen, so a label can claim protein the body cannot use for muscle. "
  "A protein source listed after those on the ingredients line is a warning sign.</p>"),
],

"plant-based-protein-sources": [
 ("Ranked by protein per calorie",
  "<p>Plant proteins are usually compared per 100 grams, which flatters nuts and seeds. Per "
  "calorie &mdash; the comparison that matters inside a calorie budget &mdash; the order "
  "changes considerably.</p>" +
  rows(["Food", "Protein per 100 g", "Protein per 100 kcal", "Typical serving"], [
   ["Seitan", "25 g", "~18 g", "85 g &rarr; 21 g"],
   ["Tempeh", "19 g", "~10 g", "85 g &rarr; 16 g"],
   ["Edamame", "11 g", "~9 g", "1 cup &rarr; 17 g"],
   ["Lentils, cooked", "9 g", "~8 g", "1 cup &rarr; 18 g"],
   ["Black beans, cooked", "9 g", "~7 g", "1 cup &rarr; 15 g"],
   ["Tofu, firm", "8 g", "~6 g", "&frac12; block &rarr; 10 g"],
   ["Hemp seeds", "31 g", "~6 g", "3 tbsp &rarr; 9 g"],
   ["Peanut butter", "25 g", "~4 g", "2 tbsp &rarr; 8 g"],
   ["Almonds", "21 g", "~4 g", "1 oz &rarr; 6 g"],
  ]) +
  "<p>Soy foods and legumes dominate the useful end. Nuts and seeds are worth eating for other "
  "reasons, but treating them as a protein strategy means buying a great deal of fat alongside.</p>"),
 ("Closing the gap on a plant-based diet",
  "<p>Two differences separate plant from animal protein in practice. Digestibility is lower, "
  "with plant proteins typically 10&ndash;20% less well absorbed, and leucine content is lower, "
  "so a larger serving is needed to trigger the same muscle-building response.</p>"
  "<p>The usual adjustment is to aim near the top of the protein range &mdash; roughly "
  "1.8&ndash;2.0 g/kg when training rather than 1.6 &mdash; and to build meals around soy, "
  "legumes and seitan rather than around nuts. Vitamin B12 needs separate attention, since it "
  "is not reliably available from plants; a supplement or fortified foods are standard advice "
  "rather than an optional extra.</p>"),
],

"protein-quality-scores-pdcaas-diaas": [
 ("What the two scores measure",
  "<p>Both scores answer the same question &mdash; how well does this protein supply the amino "
  "acids a human needs &mdash; but they measure it at different points in the gut.</p>"
  "<p><strong>PDCAAS</strong> (Protein Digestibility-Corrected Amino Acid Score) compares a "
  "protein's limiting amino acid against a reference pattern, then corrects for fecal "
  "digestibility. It is the older method and still the regulatory standard in many countries. "
  "Its main flaw is that it is truncated at 1.0: any protein exceeding the requirement scores "
  "1.0, so whey, egg and soy all appear identical.</p>"
  "<p><strong>DIAAS</strong> (Digestible Indispensable Amino Acid Score) measures digestibility "
  "at the end of the small intestine instead, which better reflects what is actually absorbed, "
  "and is not truncated &mdash; so it can distinguish between proteins PDCAAS flattens.</p>" +
  rows(["Protein", "PDCAAS", "DIAAS"], [
   ["Whey isolate", "1.00", "~1.09"],
   ["Whole egg", "1.00", "~1.13"],
   ["Milk protein", "1.00", "~1.18"],
   ["Soy protein isolate", "1.00", "~0.90"],
   ["Pea protein", "~0.89", "~0.82"],
   ["Wheat protein", "~0.45", "~0.45"],
  ])),
 ("How much this should change what you eat",
  "<p>Less than the numbers suggest. Quality scores matter most when protein intake is marginal "
  "or when a single source supplies nearly all of it &mdash; in food aid, infant formula, or a "
  "diet built on one grain. At the intakes typical of someone tracking macros and eating varied "
  "food, the shortfall a lower score describes is comfortably covered by total quantity.</p>"
  "<p>Where it has practical bite is in comparing a plant-based diet at the same gram total as "
  "an omnivorous one. A DIAAS of 0.82 against 1.09 is roughly the size of the gap the "
  "higher plant-protein recommendation is designed to close.</p>"),
],
})


EXPANSIONS.update({

"high-fiber-foods-list": [
 ("How much fiber you actually need",
  "<p>The recommendation is roughly 14 g per 1,000 calories, which works out at 25 g a day for "
  "most women and 38 g for most men. Average intake in the UK and US sits nearer 15 g, so most "
  "people are eating about half.</p>" +
  rows(["Food", "Serving", "Fiber", "Fiber per 100 kcal"], [
   ["Black beans, cooked", "1 cup (172 g)", "15 g", "6.5 g"],
   ["Lentils, cooked", "1 cup (198 g)", "16 g", "7.0 g"],
   ["Split peas, cooked", "1 cup (196 g)", "16 g", "6.7 g"],
   ["Raspberries", "1 cup (123 g)", "8 g", "9.5 g"],
   ["Chia seeds", "2 tbsp (24 g)", "10 g", "8.6 g"],
   ["Avocado", "&frac12; medium (100 g)", "7 g", "4.4 g"],
   ["Pear, with skin", "1 medium (178 g)", "6 g", "5.7 g"],
   ["Broccoli, cooked", "1 cup (156 g)", "5 g", "9.1 g"],
   ["Oats, dry", "&frac12; cup (40 g)", "4 g", "2.6 g"],
   ["Almonds", "1 oz (28 g)", "3.5 g", "2.1 g"],
  ]) +
  "<p>Legumes are the most efficient source by a wide margin, and the one most Western diets "
  "leave out. A single cup of lentils covers roughly half a day's target.</p>"),
 ("Increase it gradually, and drink more water",
  "<p>Going from 15 g to 35 g overnight reliably produces gas, bloating and cramping. The gut "
  "microbiome adapts to a higher fiber load over one to two weeks, so adding about 5 g a week "
  "is the usual advice.</p>"
  "<p>Fiber also needs water to work. Soluble fiber forms a gel and bulks stool by holding "
  "water; increasing intake without increasing fluid can make constipation worse rather than "
  "better, which is the opposite of what people expect.</p>"),
],

"healthy-high-fat-foods": [
 ("Ranked by what kind of fat they supply",
  "<p>The useful comparison is not fat content but fat type, since that is what the evidence "
  "actually distinguishes between.</p>" +
  rows(["Food", "Serving", "Total fat", "Mostly"], [
   ["Extra virgin olive oil", "1 tbsp (14 g)", "14 g", "Monounsaturated"],
   ["Avocado", "&frac12; medium (100 g)", "15 g", "Monounsaturated"],
   ["Almonds", "1 oz (28 g)", "14 g", "Monounsaturated"],
   ["Walnuts", "1 oz (28 g)", "18 g", "Polyunsaturated, omega-3"],
   ["Salmon", "4 oz (113 g)", "13 g", "Polyunsaturated, omega-3"],
   ["Chia seeds", "2 tbsp (24 g)", "9 g", "Polyunsaturated, omega-3"],
   ["Whole eggs", "2 large", "10 g", "Mixed"],
   ["Dark chocolate 85%", "1 oz (28 g)", "12 g", "Mixed, some saturated"],
  ]) +
  "<p>Fat carries 9 calories a gram against 4 for protein and carbohydrate, so these foods add "
  "up quickly. Two tablespoons of olive oil is 240 calories, which is easy to pour and easy to "
  "forget.</p>"),
 ("How much fat to aim for",
  "<p>Most guidelines put total fat at 20&ndash;35% of calories. Below about 20% becomes hard "
  "to sustain and risks shortfalls in the fat-soluble vitamins A, D, E and K, which need dietary "
  "fat to be absorbed at all. A practical floor is around 0.5 g per kilogram of body weight.</p>"
  "<p>On a 2,000 calorie diet, 30% is about 67 g of fat. That is roughly an avocado, a "
  "tablespoon of olive oil, an ounce of nuts and the fat that comes with the rest of the day's "
  "food &mdash; less room than most people assume.</p>"),
],

"high-protein-breakfast-ideas": [
 ("Why breakfast is where most targets are lost",
  "<p>The typical breakfast is the lowest-protein meal of the day by a wide margin: cereal with "
  "milk is about 10 g, toast and jam nearer 6 g, a pastry about 5 g. Someone aiming for 140 g a "
  "day who starts with 6 g has to find 134 g from two meals, which is why the target gets "
  "missed.</p>" +
  rows(["Breakfast", "Protein", "Roughly"], [
   ["Greek yogurt (200 g) + berries + 2 tbsp hemp seeds", "26 g", "330 kcal"],
   ["3-egg omelette + 30 g cheese", "27 g", "380 kcal"],
   ["Cottage cheese (1 cup) + fruit", "26 g", "270 kcal"],
   ["Oats (40 g) made with milk + 1 scoop whey", "32 g", "400 kcal"],
   ["2 eggs on toast + Greek yogurt pot", "28 g", "430 kcal"],
   ["Tofu scramble (200 g) + wholemeal toast", "24 g", "390 kcal"],
   ["Smoothie: milk, whey, banana, peanut butter", "35 g", "450 kcal"],
  ]) +
  "<p>Every one of those clears the 25&ndash;30 g that triggers a full muscle protein synthesis "
  "response, and none takes long to make.</p>"),
 ("If you do not want to eat in the morning",
  "<p>Skipping breakfast is not a nutritional error in itself. Total daily protein is what "
  "matters, and someone who eats nothing until noon can still reach 140 g across two large "
  "meals and a snack &mdash; it simply requires each of those to carry more.</p>"
  "<p>The distribution research suggests a modest advantage to spreading protein across three "
  "or four meals rather than two. Modest is the accurate word: it does not outweigh eating in a "
  "way you can actually keep up.</p>"),
],

"portion-sizes-without-a-scale": [
 ("Hand-based portions, and what they weigh",
  "<p>Hand size scales roughly with body size, which makes it a reasonable portable estimate. "
  "It is not precise, and it does not need to be: the point is to be consistently in the right "
  "region rather than exactly right once.</p>" +
  rows(["Guide", "Roughly equals", "Typical content"], [
   ["Palm (thickness and width of your palm)", "85&ndash;110 g cooked meat", "25&ndash;30 g protein"],
   ["Cupped hand", "About 40 g dry grains, or 150 g cooked", "25&ndash;30 g carbohydrate"],
   ["Fist", "About 1 cup of vegetables", "Low calorie, high volume"],
   ["Thumb", "About 1 tbsp of fat", "10&ndash;14 g fat"],
   ["Two fingers", "About 30 g of cheese", "7 g protein, 9 g fat"],
  ])),
 ("Common objects, for when your hands are full",
  "<ul>"
  "<li><strong>Deck of cards</strong> &mdash; 85 g of meat, about 3 oz</li>"
  "<li><strong>Tennis ball</strong> &mdash; roughly 1 cup, or a medium piece of fruit</li>"
  "<li><strong>Golf ball</strong> &mdash; about 2 tbsp, the right size for nut butter</li>"
  "<li><strong>Four dice</strong> &mdash; about 30 g of hard cheese</li>"
  "<li><strong>A closed fist</strong> &mdash; about a cup of cooked rice or pasta</li>"
  "</ul>"
  "<p>The two foods worth measuring properly at least once are oils and nut butters. Both are "
  "calorie-dense enough that a generous eyeball can add 150&ndash;200 calories without seeming "
  "different, and both are poured or spooned rather than portioned.</p>"),
 ("How wrong these estimates are",
  "<p>Studies of self-estimated portions consistently find people underestimating by "
  "20&ndash;30%, with the error growing for energy-dense foods and for larger servings. That "
  "is roughly 400 calories on a 2,000 calorie day &mdash; enough to explain a plateau.</p>"
  "<p>A practical compromise: weigh food for one or two weeks to calibrate what a portion "
  "actually looks like, then estimate from there. The goal is a trained eye, not a permanent "
  "relationship with a scale.</p>"),
],
})


EXPANSIONS.update({

"body-recomposition-explained": [
 ("Who can actually recomp, and how fast",
  "<p>Recomposition means losing fat and gaining muscle at the same time. It is real, it is "
  "measurable, and it is much slower than either goal pursued alone. The conditions that "
  "predict it are well described.</p>" +
  rows(["Situation", "Likelihood", "Why"], [
   ["New to resistance training", "High", "Untrained muscle responds strongly to any stimulus"],
   ["Returning after a long break", "High", "Muscle memory restores lost tissue quickly"],
   ["Higher body fat, overweight", "High", "Stored fat supplies the energy the deficit removes"],
   ["Trained, lean, years of lifting", "Low", "Both processes are near their ceiling"],
   ["On a large deficit", "Low", "Not enough energy for tissue building"],
  ]) +
  "<p>The practical implication is uncomfortable for the audience most interested in it: an "
  "experienced lifter at 12% body fat is the worst candidate, and is usually better served by "
  "alternating focused phases.</p>"),
 ("The conditions that make it possible",
  "<ul>"
  "<li><strong>A small deficit, not a large one.</strong> Around 10&ndash;15% below maintenance. "
  "Deeper than that and the body has no surplus for building.</li>"
  "<li><strong>High protein.</strong> Toward the upper end, 1.8&ndash;2.4 g/kg. This is the "
  "single largest lever.</li>"
  "<li><strong>Progressive resistance training.</strong> Without a stimulus asking for muscle, "
  "a deficit simply removes tissue.</li>"
  "<li><strong>Sleep.</strong> Restricted sleep in a deficit shifts weight loss toward lean "
  "mass, which is precisely the wrong direction.</li>"
  "<li><strong>Patience.</strong> Meaningful change takes months, and the scale barely moves.</li>"
  "</ul>"),
 ("Why the scale is the wrong instrument",
  "<p>If fat is falling and muscle is rising, body weight can stay flat for months while body "
  "composition changes substantially. Someone judging progress by the scale alone concludes "
  "nothing is happening and quits at exactly the point the approach is working.</p>"
  "<p>Better markers: waist circumference measured the same way each time, how clothes fit, "
  "photographs under consistent lighting a month apart, and strength progression in the gym. "
  "Strength going up while the waist goes down is a recomp, regardless of what the scale says.</p>"),
],

"bulking-without-gaining-fat": [
 ("How large a surplus actually needs to be",
  "<p>Muscle accrues slowly, and the surplus needed to support it is smaller than most bulking "
  "advice assumes. Building a kilogram of muscle takes roughly 5,000&ndash;7,000 extra calories "
  "spread over the weeks it takes to build; a kilogram of fat stores about 7,700. A large "
  "surplus does not accelerate the first process, it just funds the second.</p>" +
  rows(["Training age", "Realistic muscle gain", "Suggested surplus"], [
   ["First year", "0.9&ndash;1.4 kg/month", "10&ndash;20% above maintenance"],
   ["Second year", "0.5&ndash;0.7 kg/month", "10&ndash;15%"],
   ["Third year", "0.2&ndash;0.4 kg/month", "5&ndash;10%"],
   ["Advanced", "Under 0.2 kg/month", "5% or a maintenance recomp"],
  ]) +
  "<p>An advanced lifter eating 500 calories a day over maintenance is buying almost entirely "
  "fat, because the muscle ceiling is the binding constraint, not the energy supply.</p>"),
 ("Rate of weight gain as the control dial",
  "<p>The most usable rule is to target 0.25&ndash;0.5% of body weight gained per week. For an "
  "80 kg person that is 200&ndash;400 g a week. Faster than that and the extra is "
  "disproportionately fat.</p>"
  "<p>Weigh yourself under the same conditions several mornings a week and use the weekly "
  "average, not any single reading. Day-to-day fluctuation from food volume, salt and glycogen "
  "easily exceeds a week's real gain, so single weigh-ins will have you adjusting to noise.</p>"
  "<p>If the average has not moved in two weeks, add about 150 calories a day. If it is climbing "
  "faster than the target, remove a similar amount. That feedback loop is more reliable than any "
  "starting calculation.</p>"),
],

"intermittent-fasting-and-macros": [
 ("What fasting does and does not change",
  "<p>Controlled trials that match calories between a fasting group and a normal-eating group "
  "generally find similar fat loss. The benefit most people experience is real but indirect: a "
  "shorter eating window makes it harder to overeat, so intake falls without deliberate "
  "restriction.</p>"
  "<p>Claims about a metabolic advantage have not held up when energy intake is controlled. "
  "Fasting is a scheduling tool, and a good one for people it suits.</p>" +
  rows(["Protocol", "Pattern", "Main practical issue"], [
   ["16:8", "8-hour eating window daily", "Two meals must carry the whole target"],
   ["5:2", "Two low-calorie days a week", "Very low protein on fasting days"],
   ["OMAD", "One meal a day", "Hitting protein and fiber in a single sitting"],
   ["Alternate day", "Alternating deficit days", "Difficult alongside training"],
  ])),
 ("The protein problem, and how to solve it",
  "<p>The real conflict between fasting and macro targets is protein distribution. A 140 g "
  "target split across two meals means 70 g each, well above the 25&ndash;30 g that maximizes "
  "the muscle-building response per meal. The surplus is not wasted, but it is not fully used "
  "for muscle either.</p>"
  "<p>Three practical adjustments: widen the window to 10 hours so three meals fit; put the "
  "window around training rather than arbitrarily; and lean on protein-dense foods so the "
  "target fits without extreme volume. If building muscle is the main goal, a narrow window is "
  "working against you, and the scheduling benefit has to be worth that cost.</p>"),
],

"water-weight-vs-fat-loss": [
 ("Why the scale moves faster than fat ever could",
  "<p>Fat loss has a hard ceiling set by arithmetic. A kilogram of body fat stores roughly 7,700 "
  "calories, so a 500-calorie daily deficit can remove about 0.45 kg a week at most. Any change "
  "faster than that is not fat.</p>" +
  rows(["Cause", "Typical swing", "How fast"], [
   ["Glycogen and its bound water", "1&ndash;2 kg", "2&ndash;3 days"],
   ["Sodium and fluid shift", "0.5&ndash;1.5 kg", "Overnight"],
   ["Food and waste in transit", "0.5&ndash;1.5 kg", "Hours"],
   ["Menstrual cycle fluid", "0.5&ndash;2 kg", "Days"],
   ["Actual fat loss", "0.25&ndash;0.9 kg", "Per week, at best"],
  ]) +
  "<p>Each gram of stored glycogen holds about 3 grams of water. Starting a low-carbohydrate "
  "diet depletes glycogen and releases that water, which is the entire explanation for the "
  "dramatic first week that low-carb diets are famous for &mdash; and for the equally dramatic "
  "return when carbohydrates come back.</p>"),
 ("How to read the scale so it tells you something",
  "<p>Weigh under identical conditions: same time, first thing, after the bathroom, before "
  "eating or drinking. Then ignore the individual number and track the weekly average. A single "
  "morning tells you almost nothing; four weeks of averages tells you whether the plan is "
  "working.</p>"
  "<p>Two situations regularly hide real fat loss. Starting a new training program causes "
  "muscle inflammation and glycogen storage that can add a kilogram for a couple of weeks. And "
  "in a long deficit, elevated cortisol can mask several weeks of fat loss with retained fluid, "
  "which sometimes releases suddenly &mdash; the so-called whoosh &mdash; making it look like "
  "two kilograms vanished overnight.</p>"),
],

"meal-frequency-and-metabolism": [
 ("The claim, and what the trials found",
  "<p>The idea that frequent small meals stoke metabolism rests on the thermic effect of food, "
  "the energy used to digest and process what you eat. That is real: it accounts for roughly "
  "10% of intake. The error is in assuming it depends on how the intake is divided.</p>"
  "<p>It does not. TEF scales with the total amount and composition of food, not the number of "
  "sittings. Six 400-calorie meals and three 800-calorie meals produce the same thermic effect "
  "over a day, and controlled trials comparing meal frequencies at matched calories have "
  "consistently found no difference in weight loss or resting metabolic rate.</p>"),
 ("What meal frequency does affect",
  "<ul>"
  "<li><strong>Appetite and adherence.</strong> Genuinely individual. Some people find frequent "
  "meals control hunger; others find eating restarts it.</li>"
  "<li><strong>Protein distribution.</strong> Three or four meals clearing 25&ndash;30 g of "
  "protein each produces a slightly better muscle response than the same total in one or two "
  "sittings.</li>"
  "<li><strong>Training performance.</strong> Timing food around sessions matters more than "
  "total frequency.</li>"
  "<li><strong>Blood glucose stability.</strong> Relevant for some medical conditions, and a "
  "question for a clinician rather than a general guide.</li>"
  "</ul>"
  "<p>The honest answer is that meal frequency is a preference, not a lever. Choose the pattern "
  "you can hold for a year.</p>"),
],

"thermic-effect-of-food-explained": [
 ("How much energy digestion actually uses",
  "<p>The thermic effect of food is the energy your body spends absorbing, transporting and "
  "storing what you eat. It runs at about 10% of total intake for a mixed diet &mdash; roughly "
  "200 calories on a 2,000 calorie day &mdash; and it differs sharply by macronutrient.</p>" +
  rows(["Macronutrient", "Share of its calories used in processing", "Net available"], [
   ["Protein", "20&ndash;30%", "About 3 kcal per gram of the 4"],
   ["Carbohydrate", "5&ndash;10%", "About 3.7 kcal per gram"],
   ["Fat", "0&ndash;3%", "About 8.8 kcal per gram"],
   ["Alcohol", "10&ndash;30%", "Variable"],
  ]) +
  "<p>Protein's high thermic cost is one of three reasons a higher-protein diet helps with fat "
  "loss, alongside greater satiety and preservation of lean mass. On 150 g of protein a day, the "
  "thermic difference against the same calories as fat is roughly 100&ndash;140 calories &mdash; "
  "real, and smaller than it is often sold as.</p>"),
 ("What does not meaningfully raise it",
  "<p>Negative-calorie foods are a myth. Celery costs more energy to chew than it supplies only "
  "in the sense that the difference is trivial; no food burns more than it delivers by a margin "
  "that matters.</p>"
  "<p>Cold water, spicy food and green tea all raise energy expenditure measurably in a "
  "laboratory and negligibly in a life &mdash; tens of calories, well inside the error of any "
  "food tracking. Meal timing and frequency do not change the daily total, as covered on the "
  "meal frequency page. The macronutrient composition of what you eat is the only lever here "
  "large enough to plan around.</p>"),
],

"macros-for-vegetarians": [
 ("Where a vegetarian diet actually falls short",
  "<p>Vegetarian eating covers most nutritional needs comfortably. The gaps are specific and "
  "predictable rather than general, and each has a straightforward fix.</p>" +
  rows(["Nutrient", "Why it is harder", "Practical fix"], [
   ["Protein density", "Plant sources carry starch or fat alongside", "Soy, seitan, legumes, dairy, eggs"],
   ["Vitamin B12", "Not reliably present in plants", "Dairy and eggs, or a supplement"],
   ["Iron", "Non-heme iron is absorbed less well", "Pair with vitamin C; cook in cast iron"],
   ["Zinc", "Phytates in grains and legumes bind it", "Soaking, sprouting, fermenting"],
   ["Omega-3 EPA/DHA", "Plants supply ALA, converted poorly", "Algae oil, or eggs enriched with it"],
  ]) +
  "<p>Iron deserves particular attention: non-heme iron from plants is absorbed at roughly a "
  "third the rate of heme iron from meat. Vitamin C in the same meal can double or triple "
  "absorption, so lentils with tomatoes or peppers is a better combination than lentils with "
  "tea, which inhibits it.</p>"),
 ("Building the protein target without meat",
  "<p>The target itself does not change &mdash; 1.6&ndash;2.2 g/kg for someone training &mdash; "
  "but plant proteins are less digestible and lower in leucine, so aiming near the top of the "
  "range is the usual adjustment. A lacto-ovo vegetarian has an easier time than someone fully "
  "plant-based, since dairy and eggs are complete and protein-dense.</p>"
  "<p>A day reaching 120 g without meat: Greek yogurt with hemp seeds at breakfast (26 g), "
  "lentil soup with wholemeal bread at lunch (24 g), a tempeh stir-fry at dinner (28 g), "
  "cottage cheese as a snack (25 g), and the incidental protein in vegetables and grains "
  "(15&ndash;20 g). None of that is unusual food.</p>"),
],
})


EXPANSIONS.update({

"low-fat-diet-risks": [
 ("What goes wrong below about 20% of calories",
  "<p>Fat is not optional. Three specific problems appear when intake drops too low, and they "
  "are mechanistic rather than theoretical.</p>" +
  rows(["Problem", "Why it happens"], [
   ["Fat-soluble vitamin shortfall", "A, D, E and K need dietary fat to be absorbed at all"],
   ["Essential fatty acid deficiency", "Linoleic and alpha-linolenic acid cannot be synthesised"],
   ["Hormone disruption", "Cholesterol is the substrate for testosterone and estrogen"],
   ["Poor satiety", "Fat slows gastric emptying; very low fat leaves meals unsatisfying"],
  ]) +
  "<p>A practical floor is about 20% of calories, or roughly 0.5 g per kilogram of body weight, "
  "whichever is higher. On 2,000 calories that is around 45 g of fat.</p>"),
 ("Where the low-fat era went wrong",
  "<p>Dietary guidance from the 1980s onward pushed fat down, and the food industry replaced it "
  "with refined carbohydrate and sugar to keep products palatable. Low-fat products routinely "
  "carried the same calories as the versions they replaced, with worse satiety.</p>"
  "<p>The lesson is the substitution principle rather than a reversal: replacing saturated fat "
  "with polyunsaturated fat improves cardiovascular outcomes, and replacing it with refined "
  "carbohydrate does not. What fat is replaced with decides the result.</p>"
  "<p>Very low-fat diets are still used clinically in specific conditions &mdash; some "
  "gallbladder and pancreatic disease, certain lipid disorders &mdash; under supervision. That "
  "is a different situation from choosing one for weight loss.</p>"),
],

"carb-loading-for-athletes": [
 ("The protocol that is actually used",
  "<p>Carbohydrate loading raises muscle glycogen above normal so it lasts longer in prolonged "
  "events. The depletion phase from the 1960s has been abandoned; modern protocols are simpler "
  "and better tolerated.</p>" +
  rows(["Days before", "Carbohydrate", "Training"], [
   ["3 days out", "8&ndash;10 g/kg body weight", "Light"],
   ["2 days out", "8&ndash;10 g/kg", "Very light or rest"],
   ["1 day out", "8&ndash;10 g/kg", "Rest or short shakeout"],
   ["Race morning", "1&ndash;4 g/kg, 1&ndash;4 hours before", "&mdash;"],
  ]) +
  "<p>For a 70 kg runner that is 560&ndash;700 g of carbohydrate a day, which is a great deal "
  "of food and usually needs low-fiber, energy-dense sources plus drinks to be achievable.</p>"),
 ("When it is worth doing, and the weight it adds",
  "<p>Loading only helps when the event is long enough to deplete glycogen &mdash; generally "
  "beyond about 90 minutes of sustained effort. A 10k, a football match or a training session "
  "does not run the tank down far enough for it to matter, and loading for one just adds weight.</p>"
  "<p>Expect 1&ndash;2 kg of weight gain, because each gram of stored glycogen holds about 3 "
  "grams of water. For a marathon that trade is usually worth it. For a hill climb or a "
  "weight-category sport it may not be.</p>"
  "<p>Practise it in training before using it in a race. High-carbohydrate, low-fiber eating for "
  "three days causes gut trouble for some people, and race morning is the wrong time to find "
  "that out.</p>"),
],

"macros-for-endurance-vs-strength-athletes": [
 ("Two different jobs for the same three macronutrients",
  "<p>Endurance and strength training stress different systems, and the macro split follows "
  "from that. Endurance work runs primarily on glycogen and depletes it over hours; strength "
  "work is short, uses glycogen in smaller amounts, and its main nutritional demand is the raw "
  "material for repair.</p>" +
  rows(["", "Endurance", "Strength"], [
   ["Carbohydrate", "6&ndash;10 g/kg", "3&ndash;5 g/kg"],
   ["Protein", "1.2&ndash;1.6 g/kg", "1.6&ndash;2.2 g/kg"],
   ["Fat", "Remainder, 20&ndash;30% of calories", "Remainder, 20&ndash;35%"],
   ["Main limiter", "Fuel availability", "Recovery and stimulus"],
  ]) +
  "<p>For a 70 kg athlete that is 420&ndash;700 g of carbohydrate a day for endurance against "
  "210&ndash;350 g for strength &mdash; a difference of well over a thousand calories, entirely "
  "from one macronutrient.</p>"),
 ("Where the two overlap",
  "<p>Endurance athletes are routinely under-fuelled on protein, on the assumption it is a "
  "strength concern. It is not: prolonged endurance work causes meaningful protein breakdown, "
  "and intakes below about 1.2 g/kg impair recovery.</p>"
  "<p>Strength athletes make the opposite mistake, cutting carbohydrate low enough that training "
  "quality drops. Glycogen fuels the repeated high-intensity sets that drive adaptation; a "
  "depleted lifter simply does less work.</p>"
  "<p>For hybrid training &mdash; a runner who lifts, or a team-sport athlete &mdash; the "
  "workable approach is protein at the strength end and carbohydrate scaled to the week's "
  "endurance volume rather than a fixed number.</p>"),
],

"sports-drinks-vs-water": [
 ("When a sports drink earns its place",
  "<p>Sports drinks exist to supply three things water does not: carbohydrate for fuel, sodium "
  "to help retain fluid, and flavor that encourages drinking. Each matters only past a certain "
  "duration or intensity.</p>" +
  rows(["Situation", "What to drink"], [
   ["Under 60 minutes, any intensity", "Water"],
   ["60&ndash;90 minutes, moderate", "Water is usually enough"],
   ["Over 90 minutes continuous", "Carbohydrate and electrolytes help"],
   ["Hot conditions, heavy sweating", "Sodium matters, regardless of duration"],
   ["Multiple sessions in a day", "Carbohydrate aids the second session"],
   ["Everyday hydration", "Water"],
  ]) +
  "<p>A typical 500 ml sports drink carries around 30 g of sugar and 120 calories. Drunk at a "
  "desk it is a soft drink with electrolytes; drunk at 100 minutes into a long run it is fuel "
  "arriving exactly when glycogen is running down.</p>"),
 ("What the concentration is designed for",
  "<p>Most sports drinks sit at 6&ndash;8% carbohydrate, which is not arbitrary. Below that "
  "range the fuel delivery is slow; above it, gastric emptying slows and the drink can sit in "
  "the stomach, which is the usual cause of sloshing and nausea in long events.</p>"
  "<p>Sodium content varies widely, from around 200 to 500 mg per 500 ml. Heavy and salty "
  "sweaters &mdash; visible white residue on clothing after training &mdash; lose considerably "
  "more and generally need the higher end, or separate electrolyte tablets in water.</p>"
  "<p>For anything under an hour, water plus a normal diet covers it. The sodium and potassium "
  "lost in a 45-minute session are replaced by the next meal without any thought.</p>"),
],

"are-protein-bars-actually-healthy": [
 ("How to read a protein bar label",
  "<p>Protein bars sit on a spectrum from a genuine convenience food to a confectionery bar "
  "with whey added. Four numbers separate them.</p>" +
  rows(["Check", "Good sign", "Warning sign"], [
   ["Protein per 100 kcal", "8 g or more", "Under 5 g"],
   ["Protein source position", "First or second ingredient", "After syrups or chocolate"],
   ["Sugar alcohols", "Erythritol, or few", "Large amounts of maltitol"],
   ["Added sugar", "Under 8 g", "Over 15 g"],
  ]) +
  "<p>A bar with 20 g of protein and 350 calories delivers 5.7 g per 100 calories, roughly the "
  "density of a nut butter rather than of a protein food. A bar with 20 g at 200 calories is "
  "10 g per 100 calories, which is doing the job it claims.</p>"),
 ("The net-carb problem specifically",
  "<p>Bars marketed on a low net-carb figure often reach it by subtracting maltitol, which is "
  "absorbed enough to raise blood glucose to roughly half the degree sugar does. A bar claiming "
  "2 g net carbs while carrying 20 g of maltitol is not behaving like a 2 g food, and large "
  "amounts of sugar alcohol are also the most common reason a protein bar causes bloating and "
  "gas.</p>"
  "<p>Whole food is usually cheaper and more filling. A pot of Greek yogurt with fruit delivers "
  "comparable protein for less money and more volume. Bars earn their place in genuinely "
  "inconvenient moments &mdash; travel, a long day out &mdash; rather than as a daily habit.</p>"),
],

"carbohydrates-for-strength-training": [
 ("How much carbohydrate lifting actually needs",
  "<p>Strength training uses glycogen, but far less per session than endurance work. A hard "
  "hour of lifting depletes roughly 30&ndash;40% of muscle glycogen in the trained muscles, "
  "against near-total depletion in a long endurance effort.</p>" +
  rows(["Training volume", "Carbohydrate", "70 kg lifter"], [
   ["3 sessions a week, moderate", "3&ndash;4 g/kg", "210&ndash;280 g"],
   ["4&ndash;5 sessions, higher volume", "4&ndash;5 g/kg", "280&ndash;350 g"],
   ["6+ sessions or added conditioning", "5&ndash;6 g/kg", "350&ndash;420 g"],
  ]) +
  "<p>These figures assume maintenance or a surplus. In a deficit carbohydrate is the macro "
  "that gives way, since protein must stay high and fat has a hormonal floor &mdash; which is "
  "exactly why training quality tends to drop while cutting.</p>"),
 ("What low carbohydrate costs a lifter",
  "<p>The evidence for low-carbohydrate diets impairing one-rep-max strength is weak; a single "
  "maximal effort runs mainly on stored phosphocreatine. The cost appears in volume: sets to "
  "failure, total repetitions across a session, and the ability to repeat hard sessions. Since "
  "training volume is a primary driver of muscle growth, a lifter doing less work adapts more "
  "slowly even at the same strength on paper.</p>"
  "<p>Timing is a smaller lever than total. A carbohydrate-containing meal one to three hours "
  "before training covers most of the benefit; there is no need for anything more elaborate.</p>"),
],
})


EXPANSIONS.update({

"units-and-conversions-cheat-sheet": [
 ("Energy and macronutrients",
  rows(["Quantity", "Equals"], [
   ["1 g protein", "4 kcal"],
   ["1 g carbohydrate", "4 kcal"],
   ["1 g fat", "9 kcal"],
   ["1 g alcohol", "7 kcal"],
   ["1 g fiber", "0&ndash;2 kcal (varies; often counted as 2 in the EU, 0 in the US)"],
   ["1 kcal", "4.184 kJ"],
   ["1 kJ", "0.239 kcal"],
  ]) +
  "<p>The kcal/kJ difference catches people out on imported labels. A bar showing 900 is showing "
  "kilojoules, and is about 215 kcal &mdash; not a catastrophe.</p>"),
 ("Weight, volume and the trap between them",
  rows(["Unit", "Equals"], [
   ["1 oz", "28.35 g"],
   ["1 lb", "453.6 g (16 oz)"],
   ["1 kg", "2.205 lb"],
   ["1 stone", "6.35 kg (14 lb)"],
   ["1 cup (US)", "240 ml"],
   ["1 tbsp", "15 ml (3 tsp)"],
   ["1 tsp", "5 ml"],
   ["1 fl oz (US)", "29.6 ml"],
   ["1 inch", "2.54 cm"],
   ["1 foot", "30.48 cm"],
  ]) +
  "<p>The trap: a cup is a volume, not a weight, and the two only coincide for water. A cup of "
  "flour is about 120 g, a cup of sugar about 200 g, a cup of oil about 218 g. Recipes and "
  "nutrition data that mix the two are a common source of error, which is why weighing is more "
  "reliable than measuring for anything dense.</p>"),
 ("Cooked versus raw, and label rounding",
  "<p>Nutrition data is usually published for one state, and the two differ substantially "
  "because water leaves during cooking:</p>" +
  rows(["Food", "Change on cooking"], [
   ["Meat", "Loses about 25% of its weight as water"],
   ["Rice", "Roughly triples in weight (1 cup dry &rarr; 3 cooked)"],
   ["Pasta", "Roughly doubles"],
   ["Oats", "Roughly triples with liquid"],
   ["Spinach", "Loses about 90% of its volume"],
  ]) +
  "<p>100 g of raw chicken is not 100 g of cooked chicken. Weighing raw and using raw data, or "
  "weighing cooked and using cooked data, both work &mdash; mixing them does not.</p>"
  "<p>Labels are also allowed to round. In the US, under 0.5 g of fat per serving may be printed "
  "as 0 g, so a cooking spray with a one-second serving legitimately shows zero calories while "
  "the can holds several hundred.</p>"),
],

"restaurant-meal-guides": [
 ("How these guides are built",
  "<p>Every figure in the restaurant guides comes from the chain's own published nutrition "
  "information, for the standard build of the item as listed. That last clause carries most of "
  "the weight: a Chipotle bowl as configured on their nutrition calculator is not the bowl you "
  "get if you add cheese, sour cream and a tortilla on the side.</p>"
  "<p>Where a chain does not publish a value, these guides show a dash rather than a zero. A "
  "missing sodium figure is not a low sodium figure, and treating it as one would rank meals "
  "dishonestly.</p>"),
 ("What to check before you rely on a number",
  "<ul>"
  "<li><strong>Regional menus differ.</strong> The same chain publishes different data by "
  "country, and sometimes by region within one.</li>"
  "<li><strong>Recipes change.</strong> Chains reformulate without announcement; figures here "
  "are checked periodically rather than continuously.</li>"
  "<li><strong>Preparation varies by location.</strong> Portioning is done by people, and a "
  "scoop is not a measurement.</li>"
  "<li><strong>Combined orders are listed explicitly.</strong> Where a guide shows a meal made "
  "of several items, every item is named.</li>"
  "</ul>"
  "<p>Used as a way to compare options before you order, this data is reliable. Used as a "
  "precise accounting of what you ate, it is not, and no restaurant data is.</p>"),
],

"restaurant-nutrition-information": [
 ("How accurate published restaurant data actually is",
  "<p>Studies comparing laboratory analysis of restaurant meals against published values have "
  "repeatedly found meaningful discrepancies. One widely cited analysis found that measured "
  "calories averaged close to the stated figure, but individual items varied substantially, "
  "with a significant share exceeding their stated calories by 100 or more.</p>"
  "<p>The variation is not usually dishonesty. It comes from portioning done by hand, natural "
  "variation in ingredients, and the difference between a test-kitchen build and a Friday-night "
  "one.</p>" +
  rows(["Source of variation", "Typical size"], [
   ["Hand portioning of sauces and dressings", "50&ndash;200 kcal"],
   ["Protein portion variation", "20&ndash;40% by weight"],
   ["Cooking oil absorbed", "50&ndash;150 kcal"],
   ["Regional recipe differences", "Varies widely"],
  ])),
 ("Using the numbers without false precision",
  "<p>The right use of restaurant data is comparative rather than absolute. The difference "
  "between a 500-calorie option and a 1,200-calorie one is far larger than the error in either "
  "figure, so the comparison holds even when neither number is exact. Choosing between two "
  "items 40 calories apart is reading noise.</p>"
  "<p>Three habits make the data more useful: order sauces and dressings on the side, since "
  "they are the largest single source of variance; treat protein weights as approximate and "
  "the vegetables as reliable; and pay more attention to sodium than to calories when eating "
  "out often, because a single restaurant meal can carry most of a day's sodium and that is "
  "harder to see or taste than portion size.</p>"),
],

"balanced-breakfast-formula": [
 ("The formula, with numbers",
  "<p>A breakfast that holds until lunch generally clears three thresholds. Hitting all three "
  "matters more than what the food actually is.</p>" +
  rows(["Component", "Target", "Why"], [
   ["Protein", "25&ndash;30 g", "Triggers full muscle protein synthesis; strongest satiety signal"],
   ["Fiber", "5&ndash;8 g", "Slows gastric emptying and blunts the glucose rise"],
   ["Fat", "10&ndash;15 g", "Slows digestion further; carries fat-soluble vitamins"],
   ["Carbohydrate", "Whatever the day needs", "Fuel, and usually the easiest part to hit"],
  ]) +
  "<p>The typical failing breakfast &mdash; cereal, toast and jam, a pastry &mdash; clears none "
  "of the first three. That is why hunger returns at ten o'clock, and it is a formulation "
  "problem rather than a willpower one.</p>"),
 ("Worked examples, sweet and savoury",
  "<p><strong>Sweet.</strong> 200 g Greek yogurt (20 g protein), 1 cup raspberries (8 g fiber), "
  "2 tbsp hemp seeds (9 g protein, 12 g fat), a drizzle of honey. Roughly 29 g protein, 10 g "
  "fiber, 400 kcal.</p>"
  "<p><strong>Savoury.</strong> Three-egg omelette (18 g protein, 15 g fat), &frac12; avocado "
  "(7 g fiber), a slice of wholemeal toast (4 g protein, 3 g fiber). Roughly 24 g protein, "
  "10 g fiber, 450 kcal.</p>"
  "<p><strong>Plant-based.</strong> 200 g firm tofu scrambled (16 g protein), black beans "
  "(7 g protein, 7 g fiber), wholemeal tortilla, salsa. Roughly 27 g protein, 11 g fiber.</p>"
  "<p>The pattern is the same in each: a real protein source, a fiber source that is not "
  "refined grain, and enough fat to slow the whole thing down.</p>"),
],

"balanced-vegetarian-meal-formula": [
 ("Building the plate",
  "<p>A vegetarian meal fails in a predictable way: it becomes a carbohydrate dish with "
  "vegetables, and protein arrives almost by accident. The fix is to choose the protein first, "
  "the same way an omnivorous meal is usually planned.</p>" +
  rows(["Component", "Portion", "Supplies"], [
   ["Protein anchor", "Palm-sized or 1 cup legumes", "20&ndash;30 g protein"],
   ["Vegetables", "Half the plate", "Fiber, micronutrients, volume"],
   ["Whole grain or starch", "Cupped hand", "Fuel and additional fiber"],
   ["Fat source", "Thumb-sized", "Satiety, vitamin absorption"],
   ["Vitamin C element", "Any", "Doubles or triples non-heme iron absorption"],
  ]) +
  "<p>That last row is the one most vegetarian meal advice omits. Iron from plants is absorbed "
  "at roughly a third the rate of iron from meat, and vitamin C in the same meal changes that "
  "substantially &mdash; lentils with tomato and pepper, not lentils with tea.</p>"),
 ("Protein anchors ranked by density",
  rows(["Anchor", "Serving", "Protein"], [
   ["Seitan", "85 g", "21 g"],
   ["Tempeh", "85 g", "16 g"],
   ["Lentils, cooked", "1 cup", "18 g"],
   ["Edamame", "1 cup", "17 g"],
   ["Greek yogurt", "200 g", "20 g"],
   ["Cottage cheese", "1 cup", "25 g"],
   ["Black beans", "1 cup", "15 g"],
   ["Tofu, firm", "&frac12; block", "10 g"],
   ["Eggs", "2 large", "13 g"],
  ]) +
  "<p>Anything below about 10 g per serving is a contributor rather than an anchor. Two "
  "contributors can replace one anchor &mdash; beans plus yogurt &mdash; but a meal built only "
  "from contributors usually lands short.</p>"),
],
})


EXPANSIONS.update({

"pre-workout-meal-timing": [
 ("How long before, and how much",
  "<p>The further out the meal, the larger and more mixed it can be. Close to training, the "
  "constraint is digestion rather than nutrition &mdash; blood is being diverted to muscle, and "
  "a heavy meal sitting in the stomach is the usual cause of cramping and nausea.</p>" +
  rows(["Time before", "Size", "Composition"], [
   ["3&ndash;4 hours", "Full meal, 500&ndash;700 kcal", "Protein, carbohydrate, some fat and fiber"],
   ["2&ndash;3 hours", "Moderate, 300&ndash;500 kcal", "Protein and carbohydrate, lower fat"],
   ["1&ndash;2 hours", "Small, 200&ndash;300 kcal", "Mostly carbohydrate, some protein, minimal fat and fiber"],
   ["Under 1 hour", "Snack, 100&ndash;200 kcal", "Fast carbohydrate only &mdash; banana, toast, sports drink"],
  ]) +
  "<p>Fat and fiber are what get cut as the window narrows. Both slow gastric emptying, which "
  "is useful at breakfast and unhelpful thirty minutes before a hard session.</p>"),
 ("Training fasted, and when it matters",
  "<p>For short or moderate sessions, training fasted is fine and for some people more "
  "comfortable. The claim that it burns more fat is technically true and practically "
  "irrelevant: fasted training shifts fuel use toward fat during the session, but total daily "
  "energy balance decides fat loss, and the difference washes out over the day.</p>"
  "<p>Where fasted training does cost something is in performance on longer or harder sessions, "
  "and in muscle preservation when the last protein feeding was many hours earlier. If you "
  "train early and fasted, the case for protein soon afterwards is stronger than it is for "
  "someone who ate two hours before.</p>"),
],

"post-workout-meal-guide": [
 ("What recovery actually requires",
  "<p>Three things are being replaced after a hard session: muscle protein, glycogen and fluid. "
  "Only the last is urgent.</p>" +
  rows(["Target", "How much", "How urgent"], [
   ["Protein", "0.3&ndash;0.4 g/kg (20&ndash;30 g)", "Within a few hours"],
   ["Carbohydrate", "0.5&ndash;1.2 g/kg after long sessions", "Within hours; sooner if training again today"],
   ["Fluid", "125&ndash;150% of weight lost", "Promptly"],
   ["Sodium", "With the fluid, if sweating was heavy", "Promptly"],
  ]) +
  "<p>For a 70 kg person that is roughly 25 g of protein and, after a genuinely long session, "
  "35&ndash;85 g of carbohydrate. After an hour of lifting, the carbohydrate figure is at the "
  "very bottom of that range or unnecessary.</p>"),
 ("The window is hours, not minutes",
  "<p>The 30-minute anabolic window came from studies comparing post-workout protein against "
  "nothing at all. When later work controlled for total daily protein, the timing advantage "
  "mostly disappeared. If you ate a protein-containing meal within a few hours of training, "
  "sprinting to a shaker is solving a problem you do not have.</p>"
  "<p>Two genuine exceptions: training fasted, where the last feeding is far behind, and "
  "training twice in one day, where glycogen has to be restored quickly for the second session. "
  "Outside those, eat a normal meal when you are hungry and hit your daily totals.</p>"),
],

"high-protein-snacks-real-food": [
 ("Snacks that carry real protein",
  "<p>The gap between a snack that contributes to a daily target and one that does not is "
  "large, and it is not obvious from the packet.</p>" +
  rows(["Snack", "Serving", "Protein", "Calories"], [
   ["Greek yogurt, plain", "200 g", "20 g", "120"],
   ["Cottage cheese", "1 cup", "25 g", "165"],
   ["Tuna, canned", "1 can drained", "36 g", "155"],
   ["Boiled eggs", "2 large", "13 g", "155"],
   ["Edamame, shelled", "1 cup", "17 g", "190"],
   ["Turkey slices", "85 g", "18 g", "100"],
   ["Roasted chickpeas", "&frac12; cup", "10 g", "180"],
   ["Cheese, cheddar", "30 g", "7 g", "120"],
   ["Almonds", "1 oz", "6 g", "165"],
   ["Peanut butter", "2 tbsp", "8 g", "190"],
  ]) +
  "<p>The bottom three are the ones people over-rely on. Nuts and nut butter are worth eating, "
  "but at 4 g of protein per 100 calories they are a fat source that contains protein, not a "
  "protein source.</p>"),
 ("Why snacks decide most protein targets",
  "<p>Someone eating three solid meals typically reaches 90&ndash;110 g of protein without much "
  "planning. The distance from there to a 140&ndash;160 g target is almost entirely snacks, and "
  "the default snacks &mdash; fruit, crisps, biscuits, nuts &mdash; contribute between 0 and "
  "6 g each.</p>"
  "<p>Swapping two snacks a day from 4 g to 20 g closes a 32 g gap without changing a single "
  "meal. That is usually the difference between missing and hitting, and it is a smaller change "
  "than adding another chicken breast to a dinner that already had one.</p>"),
],

"recipe-macro-scaler": [
 ("How to get a recipe's macros right",
  "<p>Scaling a recipe is arithmetic. Getting the starting numbers right is where the error "
  "creeps in, and there are four places it usually enters.</p>"
  "<ul>"
  "<li><strong>Weigh ingredients raw, before cooking.</strong> Water loss during cooking changes "
  "weight but not calories, so raw weights are the stable basis.</li>"
  "<li><strong>Count the cooking fat.</strong> Oil in the pan is part of the dish. A tablespoon "
  "is 120 calories, and it is the most commonly omitted ingredient.</li>"
  "<li><strong>Weigh the finished dish.</strong> Total cooked weight divided into portions is "
  "far more accurate than eyeballing quarters of a tray.</li>"
  "<li><strong>Decide what a portion is once.</strong> By weight, not by scoop.</li>"
  "</ul>"
  "<p>The method: total the macros of every raw ingredient, weigh the finished dish, then divide "
  "the totals by the number of grams. That gives you macros per gram, and any portion size "
  "afterwards is one multiplication.</p>"),
 ("A worked example",
  "<p>A chicken and rice traybake: 600 g raw chicken breast (1,020 kcal, 186 g protein), 300 g "
  "dry rice (1,110 kcal, 22 g protein, 240 g carbohydrate), 30 g olive oil (265 kcal, 30 g "
  "fat), 400 g mixed vegetables (120 kcal, 20 g carbohydrate).</p>"
  "<p>Totals: 2,515 kcal, 208 g protein, 260 g carbohydrate, 44 g fat. The dish comes out of "
  "the oven at 1,850 g.</p>"
  "<p>Per 100 g: 136 kcal, 11 g protein, 14 g carbohydrate, 2.4 g fat. A 400 g serving is "
  "544 kcal and 45 g of protein &mdash; and you can now portion it any way you like without "
  "recalculating anything.</p>"),
],

"sweat-rate-calculator": [
 ("How to measure your own sweat rate",
  "<p>Fluid needs vary more between people than almost any other nutrition variable. Measured "
  "sweat rates range from about 0.5 to over 2.5 liters an hour depending on the person, the "
  "intensity and the conditions. General advice cannot cover that spread, but a single "
  "measurement can.</p>"
  "<p>The method takes one session:</p>"
  "<ol>"
  "<li>Weigh yourself, minimal clothing, before training.</li>"
  "<li>Train for a measured time, noting exactly how much you drink.</li>"
  "<li>Towel dry and weigh again in the same clothing.</li>"
  "<li><strong>Sweat loss = (weight before &minus; weight after) + fluid drunk</strong></li>"
  "<li>Divide by hours to get the rate.</li>"
  "</ol>"
  "<p>Example: 74.0 kg before, 72.9 kg after, 500 ml drunk over 90 minutes. Loss is 1.1 kg plus "
  "0.5 kg = 1.6 kg over 1.5 hours, so about <strong>1.07 liters an hour</strong>.</p>"),
 ("What to do with the number",
  "<p>Replacing fluid during exercise at close to the sweat rate is impractical for most people; "
  "the gut absorbs roughly 0.6&ndash;1.2 liters an hour at best. The realistic target is to "
  "limit losses to about 2% of body weight, which is where performance begins to measurably "
  "decline.</p>" +
  rows(["Body weight lost", "Effect"], [
   ["Under 2%", "No meaningful performance cost"],
   ["2&ndash;3%", "Endurance performance declines; perceived effort rises"],
   ["4%+", "Significant performance loss; heat illness risk rises"],
  ]) +
  "<p>After training, replace 125&ndash;150% of the weight lost &mdash; more than the deficit, "
  "because some of what you drink is excreted. Sodium alongside it helps retain the fluid rather "
  "than passing it through; this is why a salty meal after a long hot session is more effective "
  "than water alone.</p>"),
],

"nutrition-label-comparison-tool": [
 ("Comparing two labels honestly",
  "<p>Two products are rarely comparable straight off the pack, because manufacturers choose "
  "their own serving sizes. A cereal declaring 30 g and another declaring 45 g will show "
  "different numbers for identical food. Every meaningful comparison starts by putting both on "
  "the same basis.</p>"
  "<p>Two bases are useful, and they answer different questions:</p>"
  "<ul>"
  "<li><strong>Per 100 g</strong> answers: which food is more nutrient-dense by weight?</li>"
  "<li><strong>Per 100 calories</strong> answers: which food gives me more of what I want inside "
  "my calorie budget? This is usually the more decision-relevant number.</li>"
  "</ul>"
  "<p>A food can look better per 100 g and worse per 100 calories simply by being drier.</p>"),
 ("What to compare, in order of importance",
  rows(["Metric", "What good looks like"], [
   ["Protein per 100 kcal", "8 g or more is protein-dense"],
   ["Fiber per 100 kcal", "2 g or more is a genuinely high-fiber food"],
   ["Added sugar per 100 kcal", "Under 5 g"],
   ["Sodium per 100 kcal", "Under 100 mg for everyday foods"],
   ["Ingredient count and order", "Fewer, and the main food listed first"],
  ]) +
  "<p>Reference values worth knowing: the daily reference for fiber is 28 g, added sugar 50 g, "
  "and sodium 2,300 mg. A serving supplying 20% or more of a daily value is conventionally "
  "considered high in that nutrient, and 5% or less is low.</p>"
  "<p>One rounding rule affects comparisons directly: in the US, a serving with under 0.5 g of "
  "a nutrient may be declared as 0 g. Products engineered around that threshold can legitimately "
  "print zero while the package contains a meaningful amount.</p>"),
],
})


EXPANSIONS.update({

"carbohydrate-label-portion-tool": [
 ("Why label carbohydrate rarely matches your portion",
  "<p>A nutrition label describes a serving the manufacturer chose, and almost nobody eats "
  "exactly that. The gap is where carbohydrate counting goes wrong, and it is usually larger "
  "than people expect.</p>" +
  rows(["Food", "Label serving", "A common real portion", "Carbohydrate difference"], [
   ["Breakfast cereal", "30 g", "60&ndash;80 g", "2&ndash;2.7&times;"],
   ["Dry pasta", "75 g", "100&ndash;125 g", "1.3&ndash;1.7&times;"],
   ["Rice, dry", "50 g", "75&ndash;100 g", "1.5&ndash;2&times;"],
   ["Juice", "150 ml", "250&ndash;330 ml", "1.7&ndash;2.2&times;"],
   ["Crisps", "25 g", "Half a 150 g bag", "3&times;"],
  ]) +
  "<p>The arithmetic is simple &mdash; carbohydrate per gram, multiplied by the grams you "
  "actually ate &mdash; but it has to be done with the real portion, and the real portion has "
  "to be weighed at least a few times before it can be estimated.</p>"),
 ("Cooked versus dry, and the trap that follows",
  "<p>The single most common carbohydrate-counting error is mixing states. Rice roughly triples "
  "in weight when cooked, pasta roughly doubles, and oats roughly triple with liquid. A label "
  "showing 75 g of carbohydrate per 100 g is describing the dry product; 100 g of the cooked "
  "product carries about a third of that.</p>"
  "<p>Pick one basis and stay on it. Weighing dry and using the label is the most reliable for "
  "anything cooked in water, because the amount of water absorbed varies with cooking time and "
  "is not nutritionally relevant.</p>"
  "<p>Anyone counting carbohydrate to dose insulin should take their method from their own "
  "diabetes team rather than a general tool. The arithmetic here is the same, but the decisions "
  "that follow from it are clinical.</p>"),
],

"sodium-label-comparison-tool": [
 ("What the sodium numbers mean",
  "<p>Most guidance puts an upper limit around 2,300 mg of sodium a day, with 1,500 mg often "
  "suggested for people with raised blood pressure. Average intake in the UK and US runs well "
  "above the upper figure, and the great majority of it &mdash; roughly 70% &mdash; comes from "
  "packaged and restaurant food rather than from the salt cellar.</p>" +
  rows(["Reference", "Sodium", "As salt"], [
   ["Daily upper limit", "2,300 mg", "About 5.8 g salt (1 tsp)"],
   ["Often suggested target", "1,500 mg", "About 3.8 g salt"],
   ["'Low sodium' claim (US)", "140 mg or less per serving", "&mdash;"],
   ["'High' by daily value", "20% DV (460 mg) or more", "&mdash;"],
   ["Typical restaurant main", "1,000&ndash;2,000 mg", "&mdash;"],
  ]) +
  "<p>Sodium and salt are not the same number, and labels differ by country. Salt = sodium "
  "&times; 2.5. A UK label showing 2 g of salt is 800 mg of sodium.</p>"),
 ("Comparing products fairly",
  "<p>Compare sodium per 100 calories rather than per serving. Per-serving figures let a "
  "manufacturer look better by declaring a smaller serving, and per 100 g penalises anything "
  "with high water content, such as soup.</p>"
  "<p>Under 100 mg per 100 calories is genuinely modest for an everyday food. Over 300 mg per "
  "100 calories is high, whatever the front of the pack says.</p>"
  "<p>The categories that dominate most people's intake are bread, processed meat, cheese, "
  "sauces and soup &mdash; not obviously salty foods, but eaten in quantity. Reducing intake is "
  "usually more effective by swapping within those categories than by removing table salt, "
  "which contributes a small share of the total.</p>"),
],

"protein-value-calculator": [
 ("What protein actually costs",
  "<p>Comparing protein sources by pack price is misleading, because the packs contain very "
  "different amounts of protein. Cost per gram of protein is the number that lets you compare "
  "chicken against lentils against a tub of powder.</p>"
  "<p>The calculation: <strong>price &divide; (grams of product &times; protein per gram)</strong>. "
  "Rough figures, which will vary by country and shop:</p>" +
  rows(["Source", "Protein per 100 g", "Typical cost per 100 g protein"], [
   ["Dried lentils", "25 g (dry)", "Very low"],
   ["Eggs", "13 g", "Low"],
   ["Whey concentrate", "80 g", "Low"],
   ["Canned tuna", "25 g", "Moderate"],
   ["Chicken breast", "31 g (cooked)", "Moderate"],
   ["Greek yogurt", "10 g", "Moderate"],
   ["Beef mince", "26 g (cooked)", "Higher"],
   ["Protein bars", "20&ndash;30 g", "Highest by a wide margin"],
  ]) +
  "<p>Protein bars are consistently the most expensive way to buy protein, often several times "
  "the cost of powder for the same grams. That does not make them useless &mdash; convenience "
  "has value &mdash; but it should be a deliberate purchase rather than a default.</p>"),
 ("What cost per gram does not capture",
  "<p>Cheapest per gram is not automatically best. Three things sit outside the calculation:</p>"
  "<ul>"
  "<li><strong>What else comes with it.</strong> Dried lentils are the cheapest protein on most "
  "shelves and arrive with substantial carbohydrate and fiber. That is an advantage or a "
  "constraint depending on the rest of your day.</li>"
  "<li><strong>Protein quality.</strong> Plant sources are less digestible and lower in leucine, "
  "so the grams are not perfectly interchangeable.</li>"
  "<li><strong>Whether you will actually eat it.</strong> The cheapest protein you do not cook "
  "costs infinity per gram.</li>"
  "</ul>"
  "<p>Used sensibly, this is a tool for spotting the outliers &mdash; the products charging a "
  "large premium for grams you could buy far more cheaply &mdash; rather than for optimizing a "
  "grocery list to the penny.</p>"),
],

"about": [
 ("How the numbers on this site are produced",
  "<p>Two kinds of number appear across GetMacros, and they are sourced differently.</p>"
  "<p><strong>Restaurant nutrition data</strong> comes from each chain's own published "
  "information, for the standard build of the item as the chain lists it. Where a chain does "
  "not publish a value, the tables show a dash rather than a zero, because a missing sodium "
  "figure is not a low one and ranking it as such would be dishonest. Combined orders name "
  "every item included.</p>"
  "<p><strong>Calculator outputs</strong> use published equations rather than proprietary "
  "formulas. Energy needs use Mifflin-St Jeor with standard activity multipliers; protein "
  "targets use the ranges reported in resistance-training and weight-management research. Every "
  "calculator on the site uses the same equations, so two pages cannot give one person "
  "different answers.</p>"
  "<p>Goal tags in Healthy Order Match &mdash; high protein, lighter, high fiber &mdash; are derived "
  "from each meal's own numbers against stated thresholds rather than assigned by hand. A label "
  "the site states out loud is the threshold the site actually applies.</p>"),
 ("What this site is not",
  "<p>GetMacros publishes practical nutrition information for generally healthy adults. It does "
  "not publish clinical guidance, and pages covering the management of specific medical "
  "conditions were removed rather than maintained without the credentials such content "
  "requires.</p>"
  "<p>Nothing here is a substitute for advice from your own clinician, and there are situations "
  "where a general guide is the wrong tool entirely: pregnancy and breastfeeding, chronic kidney "
  "or liver disease, diabetes management, growth in children, and recovery from an eating "
  "disorder, where numeric targets can do harm.</p>"
  "<p>Estimates are presented as estimates. Mifflin-St Jeor predicts resting energy expenditure "
  "to within roughly 10% for most people, restaurant portioning varies by location and shift, "
  "and labels are permitted to round. Where a number is uncertain, the site says so rather than "
  "presenting a decimal place it has not earned.</p>"),
 ("Corrections",
  "<p>If something here is wrong, it should be fixed and the fix should be visible. Errors of "
  "fact are corrected and logged rather than quietly edited. The contact page is the fastest "
  "route, and specific pointers &mdash; the page, the figure, and what it should be &mdash; get "
  "acted on quickest.</p>"),
],
})
