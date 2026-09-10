"""Add practical context below tools and distinguish help from reading on home."""
from pathlib import Path
import re
from refine_tool_clarity import replace_class

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
 'recipe-macro-scaler.html': ('One recipe, two ways to change it', 'Your recipe makes four portions at 450 calories each. Here is what changes when you enter six.', [('Split the same batch', '300 calories per portion', 'The whole recipe still has 1,800 calories. Divide it into six smaller portions instead of four.'), ('Make a bigger batch', '450 calories per portion', 'Use 1.5 times each ingredient to make six of the original-sized portions. The bigger batch has 2,700 calories.')], 'Protein, carbs and fat follow the same calculation. If you swap ingredients, update the original nutrition first.', 'how-to-read-a-nutrition-label.html', 'Understand serving sizes'),
 'protein-value-calculator.html': ('The cheaper package is not always better value', 'Here is an example with two different package sizes.', [('Package A: $6', '$1.25 per 25 g protein', 'Six servings with 20 g of protein each give you 120 g of protein in the package.'), ('Package B: $5', '$2.08 per 25 g protein', 'Four servings with 15 g of protein each give you 60 g of protein in the package.')], 'Package A costs more at the checkout, but less for the same amount of protein. Taste, storage and whether you will finish it still matter. These are example prices.', 'high-protein-foods-list.html', 'Explore protein foods'),
 'nutrition-label-comparison-tool.html': ('Why the serving size matters', 'The example cereals use different serving sizes. That changes how their numbers look.', [('Per labeled serving', '160 vs. 210 calories', 'Cereal A lists 40 g per serving. Cereal B lists 55 g, so you are comparing different amounts of food.'), ('For the same 100 g', '400 vs. 382 calories', 'Cereal B has fewer calories at the same weight. The larger serving made its original number look higher.')], 'Use equal weight to compare the foods themselves, or per serving if those are the portions you plan to eat. One number alone does not make a food the better choice.', 'how-to-read-a-nutrition-label.html', 'Read a food label'),
 'sodium-label-comparison-tool.html': ('Compare the portion you will eat', 'Imagine choosing between two soups. The label alone does not tell the whole story.', [('Soup A', '450 mg sodium', 'The label says 300 mg per serving. Eating 1.5 servings gives you 300 × 1.5 = 450 mg.'), ('Soup B', '500 mg sodium', 'The label says 250 mg per serving. Eating two servings gives you 250 × 2 = 500 mg.')], 'Soup B starts with the lower label number, but the larger portion has more sodium. Include toppings or sides separately if they are not covered by the label.', 'how-much-sodium-per-day.html', 'Understand sodium labels'),
 'carbohydrate-label-portion-tool.html': ('Turn a label into your portion', 'Suppose one serving lists 32 g of total carbohydrate and 4 g of fiber.', [('Eating half a serving', '16 g carbs · 2 g fiber', 'Multiply both label values by 0.5.'), ('Eating 1.5 servings', '48 g carbs · 6 g fiber', 'Multiply both label values by 1.5.')], 'On a US nutrition label, fiber is already included in total carbohydrate. Do not add it to the total again. Check that the serving size on your label matches the amount you enter.', 'how-to-read-a-nutrition-label.html', 'Understand carbohydrate labels'),
 'budget-meal-builder.html': ('Start with what you already have', 'Choose the ingredients in your kitchen. Use the suggestions as starting points, then adjust the seasoning and portions to suit you.', [('Beans, rice and vegetables', 'A simple rice bowl', 'Warm the beans and vegetables, serve over cooked rice, and add a sauce or seasoning you like.'), ('Eggs, bread and tomatoes', 'Eggs on toast', 'Cook the eggs the way you like, put them on toast, and serve the tomatoes alongside.')], 'The builder suggests combinations, not exact nutrition or shopping prices. For calories per portion, use a recipe with ingredient amounts and known nutrition.', 'recipe-macro-scaler.html', 'Calculate recipe portions'),
 'weight-goal-timeline-calculator.html': ('What does a weekly percentage mean?', 'The pace you choose is a percentage of the weight at each week of the calculation.', [('Starting at 80 kg', '0.4 kg in the first week', 'At a selected pace of 0.5%, the calculation is 80 × 0.005 = 0.4 kg.'), ('Later, at 76 kg', '0.38 kg for that week', 'The same percentage is a smaller amount: 76 × 0.005 = 0.38 kg.')], 'This explains the calculation, not a recommended pace. Real progress does not follow an exact schedule, and a change in scale weight is not the same as a change in body fat.', 'cutting-bulking-maintenance-explained.html', 'Understand weight goals'),
 'sweat-rate-calculator.html': ('A worked workout example', 'Imagine a 60-minute workout: 70 kg before, 69.5 kg after, 500 mL drunk and no urine passed.', [('Weight change', '0.5 kg lost', 'The calculation treats this as roughly 0.5 liters of fluid.'), ('Add what you drank', 'About 1 liter per hour', 'Add the 0.5 liters you drank to the estimated 0.5 liters lost from body weight, then divide by one hour.')], 'This describes one workout; it is not a drinking target. Clothing, measurement errors and conditions can affect the estimate. Use the same scale and similar dry clothing for both measurements.', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC5634236/', 'Read the fluid-loss method'),
}

def run():
 for filename, (title, intro, cards, note, url, link) in EXAMPLES.items():
  path=ROOT/filename
  # Fail rather than publish a broken guide link.
  assert url.startswith('https://') or (ROOT/url).exists(), url
  s=path.read_text(encoding='utf-8')
  s=s.replace('<!-- reading-map:start --><!-- reading-map:end -->','')
  if filename == 'weight-goal-timeline-calculator.html':
   s=re.sub(r'var tips=losing\?\[.*?\];', '''var tips=[
      "<strong>A date is only an estimate.</strong> This calculation assumes your selected percentage changes every week. It cannot predict your actual progress.",
      "<strong>Scale weight is not just body fat.</strong> Fluid, food and muscle also affect what the scale shows. The calorie figure is a simplified calculation, not a personal intake target."
    ];''',s,flags=re.S)
   s=re.sub(r'\$\("wg-summary"\)\.textContent=.*?;\s*\n', '''$("wg-summary").textContent="From "+shown(curKg)+" to "+shown(goalKg)+" at a selected pace of "+(pace*100)+"% per week. The weekly amount changes as the modeled weight changes.";
''',s,flags=re.S)
   s=s.replace('Planning your next steps</h3>','What this result means</h3>')
  s=re.sub(r'<!-- practical-example:start -->.*?<!-- practical-example:end -->', '', s, flags=re.S)
  content='<section class="practical-example" aria-labelledby="example-title"><div class="container"><h2 id="example-title">'+title+'</h2><p class="example-intro">'+intro+'</p><div class="example-grid">'
  content+=''.join('<article><h3>'+label+'</h3><strong>'+value+'</strong><p>'+desc+'</p></article>' for label,value,desc in cards)
  content+='</div><p class="example-note">'+note+'</p><a class="btn action-link" href="'+url+'">'+link+'</a></div></section>'
  s=s.replace('</main>','<!-- practical-example:start -->'+content+'<!-- practical-example:end --></main>',1)
  path.write_text(s,encoding='utf-8')
 path=ROOT/'index.html';s=path.read_text(encoding='utf-8')
 s=s.replace('images/meal-play.svg','images/meal-plate.svg')
 s=s.replace('Meal finder questions</h2>','Using the meal finder</h2>')
 cards=[('how-many-calories-should-i-eat-a-day.html','journal-calories-vs-macros.svg','How many calories should I eat?','Understand your daily estimate and how your goal changes it.'),('how-much-protein-per-day.html','journal-protein-absorption.svg','How much protein do I need?','Find out how body weight and activity affect your daily target.'),('best-fast-food-restaurants-for-your-goals.html','journal-restaurant-comparison.svg','Which fast-food restaurant should I choose?','Compare complete orders for more protein, weight loss or a bigger meal.')]
 guide='<section class="gm6-learning"><div class="container"><div class="home-guides-head"><h2>Nutrition guides</h2><a class="btn action-link" href="articles.html">Browse all guides</a></div><div class="home-reading-grid">'
 for url,img,title,desc in cards:
  guide+='<article class="home-reading-card"><img src="images/'+img+'" alt="" loading="lazy" width="600" height="400"><div><h3>'+title+'</h3><p>'+desc+'</p><a class="btn action-link" href="'+url+'" aria-label="Read guide: '+title+'">Read guide</a></div></article>'
 guide+='</div></div></section>'
 s=replace_class(s,'gm6-learning',guide);path.write_text(s,encoding='utf-8')
 path=ROOT/'contact.html';s=path.read_text(encoding='utf-8')
 s=re.sub(r'<!-- contact-help:start -->.*?<!-- contact-help:end -->','',s,flags=re.S)
 s=s.replace('</main>','<!-- contact-help:start --><section class="practical-example contact-help"><div class="container"><h2>Help me find the problem</h2><div class="example-grid"><article><h3>A meal or nutrition number</h3><p>Send the restaurant, menu item and page link. If you found a different number on the restaurant’s website, include that link too.</p></article><article><h3>A calculator or button</h3><p>Tell me which page you used, what you entered and what happened. Your device and browser help me check the same setup.</p></article></div><p class="example-note">For a new idea, tell me what you were trying to do and what would have helped. Please leave out private health details.</p></div></section><!-- contact-help:end --></main>',1)
 path.write_text(s,encoding='utf-8')

if __name__=='__main__': run()
