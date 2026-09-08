"""Keep tool surfaces and plain-language search intent through site rebuilds."""
from pathlib import Path
import re,html,json
from recover_site_focus import build_search,metadata
ROOT=Path(__file__).resolve().parents[1]
PAGES={
 'calculators.html':('Free Macro Calculator: Calories, Protein, Carbs & Fat | GetMacros','Free macro calculator','Calculate daily calories, protein, carbs and fat for weight loss, maintenance or muscle gain. Enter your age, weight, height and activity level.'),
 'restaurant-meal-finder.html':('Healthy Fast-Food Meal Finder: High-Protein & Low-Calorie Meals','Find healthy fast-food meals','Find fast-food meals for high protein, cutting or bulking. Compare calories, protein, fiber and sodium from 15 restaurant chains.'),
 'healthy-fast-food.html':('Healthy Fast Food: Compare Calories & Protein | GetMacros','Healthy fast food by restaurant','Compare healthy fast-food options by restaurant, calories, protein, fiber and sodium. Explore menu guides and find meals for your goals.'),
 'articles.html':('Nutrition Guides: Calories, Macros & Healthy Eating | GetMacros','Nutrition guides for everyday questions','Find clear answers about calories, protein, carbs, fat and eating out. Browse practical nutrition guides with examples and sources.'),
 'about.html':('About GetMacros | Nutrition Tools, Data & Editorial Standards','About GetMacros','Learn how GetMacros builds its macro calculators, restaurant nutrition guides and articles, including the data sources and editorial standards.'),
 'sources.html':('Nutrition Sources & Calculator Methods | GetMacros','Nutrition sources and calculation methods','Check the nutrition references and calculation methods behind GetMacros tools, articles and restaurant meal comparisons.'),
 'serving-size-vs-portion-size.html':('Serving Size vs. Portion Size: What Is the Difference?','Serving size vs. portion size: what is the difference?','Learn the difference between a label serving and the portion you eat, and how to calculate calories and nutrients for your actual portion.'),
 'how-to-eat-out-without-wrecking-your-goal.html':('How to Eat Out While Losing Weight or Building Muscle','How to eat out while working toward your goals','Learn how to compare restaurant meals for weight loss, muscle gain or maintenance using portions, calories, protein and practical ordering changes.'),
 'blog.html':('Nutrition Blog: Protein, Diet Drinks & Creatine | GetMacros','Nutrition questions, explained','Explore the evidence on protein absorption, diet drinks, creatine and hair loss, restaurant meals, and calories versus macros.')
}
for p in ROOT.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 # Use the actual product name wherever a visitor needs to identify the tool.
 s=s.replace('Healthy Order Match','Fast-food meal finder')
 if p.name in PAGES:
  title,h1,desc=PAGES[p.name]
  s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',s,flags=re.S)
  s=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(h1)+m[2],s,count=1,flags=re.S)
  for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc)]:
   s=re.sub(r'(<meta '+attr+'="'+re.escape(key)+'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
  def schema(m):
   data=json.loads(m[1])
   if data.get('@type') in ['Article','BlogPosting','WebPage','CollectionPage']:
    if 'headline' in data:data['headline']=h1
    if 'name' in data:data['name']=h1
    if 'description' in data:data['description']=desc
   return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False)+'</script>'
  s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema,s,flags=re.S)
 if p.name=='calculators.html':
  s=s.replace('>Feet &amp; inches</button>','>ft / in</button>').replace('>Centimeters</button>','>cm</button>')
  s=re.sub(r'<div class="calc-hero-actions">.*?</div>','',s,flags=re.S)
  s=s.replace('Sedentary (little or no exercise)','Mostly sitting · little exercise').replace('Lightly active (1–3 days/week)','Light activity · 1–3 days/week').replace('Moderately active (3–5 days/week)','Moderate activity · 3–5 days/week').replace('Very active (6–7 days/week)','Very active · 6–7 days/week').replace('Athlete (2x/day or physical job + training)','Physical job + training')
  s=re.sub(r'(<div class="results empty" id="macro-results">).*?(</div>)',r'\1<div class="work-empty-art" aria-hidden="true"><i></i><i></i><i></i></div><h3>Your daily targets</h3><p>Enter your details and calculate to see calories, protein, carbs and fat.</p></div>',s,count=1,flags=re.S) if 'work-empty-art' not in s else s
 if p.name=='restaurant-meal-finder.html':
  s=s.replace('Choose what matters today. We compare real menu items from 15 restaurants and explain the strongest matches.','Pick your goals. Compare meals from 15 restaurants.')
  s=s.replace('Optional: open the complete cross-chain nutrition database and rankings.','Compare every listed meal and its nutrition.')
  s=s.replace("The quiz answers one question at a time. These are the standing lists behind it: all 83 tracked menu options from 15 chains, sorted the ways people actually ask for them. Every figure is the chain's published standard build.","Compare 83 menu options from 15 restaurants. Nutrition values refer to the named standard order.")
 # Remove repeated promotional qualifiers from link summaries, preserving facts.
 s=s.replace(' — with cited sources.','.').replace(' — with cited sources','')
 replacements={
  'The method is deliberately simple enough to inspect.':'How the tools use your inputs and published nutrition data.',
  'Find your best meal across all restaurants':'Compare meals across all restaurants',
  'Best starting points':'Meal ideas by goal',
  'What to decide before you arrive, and which swaps actually change the numbers.':'Compare portions, sauces and sides before ordering.',
  'Scale a recipe or compare the foods you are actually choosing.':'Compare food labels, recipe portions and protein costs.',
  'The cheapest package is not always the cheapest protein—and the best bargain is food you will actually finish.':'Compare the cost per gram of protein, along with portion size and the food you expect to use.',
  'Same math our calculator runs automatically — worked out step by step, in case you need to show your work.':'Calculate daily calories and macros step by step using the same formulas as our calculator.',
  'Recipe math that survives leftovers':'Recipe calories and portion sizes',
  'What protein actually does':'What protein does in your body',
  'choose a calorie range, and compare five best matches':'choose a meal size, and compare the first five matches',
  'select the calorie range and one or two priorities in Fast-food meal finder':'choose your goal and meal size in the fast-food meal finder',
  'A dependable lean order. Ask for extra vegetables at no real calorie cost.':'Add vegetables if you like, and include any sauces in the nutrition total.',
  'The best-value protein plate here once you skip the fried rice.':'Compare the protein and calories with your preferred side.',
  'Lowest-calorie hot breakfast that still brings real protein.':'A lower-calorie hot breakfast option with protein.',
  'A real 1,000-calorie-plus order with 80 g protein.':'An order with over 1,000 calories and 80 g protein.',
  'A side with real fiber.':'A side that contributes fiber.',
  'The five people ask for most':'Choose a starting point'
 }
 for old,new in replacements.items():s=s.replace(old,new)
 p.write_text(s,encoding='utf-8')
# Refresh the search index from the finished headings and descriptions.
build_search([metadata(p) for p in sorted(ROOT.glob('*.html'))])
print('Updated tool layouts, search discovery and descriptive page metadata.')
