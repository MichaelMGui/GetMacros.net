"""Give food tools a clear purpose and keep the shared footer compact."""
from pathlib import Path
from normalize_calculator_layouts import Document
import re,html
ROOT=Path(__file__).resolve().parents[1]
FOOTER=(ROOT/'tools/plain-footer.inc').read_text(encoding='utf-8').strip()
NAMES={'Recipe Macro Scaler':'Adjust recipe portions','Recipe macro scaler':'Adjust recipe portions','recipe macro scaler':'recipe portion calculator','Recipe calories and macros calculator':'Adjust recipe portions','Recipe Calories and Macros Calculator':'Adjust recipe portions','Compare nutrition labels side by side':'Compare two foods','Compare Nutrition Labels Side by Side':'Compare two foods','Compare Labels':'Compare two foods','Recipe Macro Calculator':'Recipe portion calculator','Private in-browser comparison':'Food portions','Free practical tool':'Food tools'}
def remove_class(s,cls):
 doc=Document(s)
 nodes=[n for n in doc.nodes if cls in n['attrs'].get('class','').split()]
 for n in reversed(nodes):s=s[:n['start']]+s[n['end']:]
 return s
def replace_node(s,cls,new):
 doc=Document(s);n=doc.find(cls=cls)
 return s[:n['start']]+new+s[n['end']:]
for p in ROOT.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 for old,new in NAMES.items():s=s.replace(old,new)
 s=re.sub(r'<footer\b.*?</footer>',lambda m:FOOTER,s,flags=re.S)
 if 'gm-sibling-tools' in s:
  s=remove_class(s,'gm-sibling-tools')
  # Removing the repeated tool directory must also remove its contents link.
  s=re.sub(r'<a href="#[^"]+">Other numbers worth checking</a>','',s)
 if p.name in ['recipe-macro-scaler.html','nutrition-label-comparison-tool.html']:
  s=re.sub(r'<!-- reading-map:start -->.*?<!-- reading-map:end -->','',s,flags=re.S)
  s=re.sub(r'<!--EXPANSION:START-->.*?<!--EXPANSION:END-->','',s,flags=re.S)
 if p.name=='recipe-macro-scaler.html':
  s=s.replace('Scale a recipe up or down and see the calories, protein, carbs and fat in each new serving—without redoing the math by hand.','Splitting a recipe for 4 into 6 portions? See the calories and macros in each portion.')
  s=s.replace('Scale a recipe or meal','Your recipe').replace('Enter nutrition per original serving. Choose whether to divide the same batch differently or make more of the recipe.','Use the nutrition already listed on your recipe. The example below starts with 4 portions at 450 calories each.')
  s=s.replace('Divide the same batch into new portions','Split the same recipe into different portions').replace('Make more or less of the recipe','Make a bigger or smaller batch')
  s=s.replace('Split the same recipe into different portions','Split into new portions').replace('Make a bigger or smaller batch','Change the batch size')
  s=s.replace('Original servings','Portions in the original recipe').replace('New servings','Portions you want').replace('Calories per original serving','Calories per original portion')
  s=s.replace('calories per new serving','calories per portion')
  s=remove_class(s,'recipe-art-card')
  s=replace_node(s,'recipe-assumptions','<details class="editorial-note recipe-assumptions"><summary>Need to calculate a recipe from ingredients?</summary><p>This tool adjusts nutrition you already know. To start from ingredients, use our <a href="how-to-calculate-recipe-nutrition.html">guide to calculating recipe calories</a>.</p><p>Divide portions evenly. Ingredient changes and food left in the pan can affect the result.</p></details>')
 if p.name=='nutrition-label-comparison-tool.html':
  s=s.replace('Enter the numbers from two packages to compare each listed serving and the nutrients per 100 calories, while keeping serving size and your real eating pattern in view.','Choosing between two foods? Enter their labels to compare calories, protein, fiber, sugar and sodium.')
  s=s.replace('value="Food A"','value="Example cereal A"').replace('value="Food B"','value="Example cereal B"')
  s=s.replace('<h2>Food A</h2>','<h2>First food</h2>').replace('<h2>Food B</h2>','<h2>Second food</h2>')
  s=s.replace('>Compare labels</button>','>Compare my foods</button>')
  s=s.replace('<div class="compare-form">','<p class="food-example-note">Example values are filled in. Replace them with the numbers on your two labels.</p><div class="compare-form">') if 'food-example-note' not in s else s
  if 'id="compare-basis"' not in s:s=s.replace('<h2>Side-by-side results</h2>','<h2>Your comparison</h2><label class="comparison-basis" for="compare-basis">Compare<select id="compare-basis"><option value="serving">One listed serving of each</option><option value="weight">The same weight: 100 g</option><option value="calories">The same calories: 100 kcal</option></select></label>')
  s=remove_class(s,'context')
  doc=Document(s)
  for n in reversed(doc.nodes):
   if n['tag']=='section' and 'How to read this comparison' in s[n['inner']:n['end']]:
    s=s[:n['start']]+'<section class="simple-tool-help"><div class="container"><h2>Which view should I use?</h2><p><strong>Per serving</strong> compares the amounts on each label. <strong>Per 100 g</strong> compares equal weights. <strong>Per 100 calories</strong> compares nutrients for the same calorie amount.</p><p>Use the numbers that matter to you; no single nutrient makes a food the winner. <a href="how-to-read-a-nutrition-label.html">Learn how to read a food label.</a></p></div></section>'+s[n['end']:]
    break
  s=re.sub(r'<script>\s*\(function\(\)\{const ids=\["serv".*?</script>','<script src="js/food-compare.js" defer></script>',s,flags=re.S)
 if p.name=='sodium-label-comparison-tool.html':
  s=s.replace('<p>Read the sodium label guide · Heart-health collection</p>','<p><a href="how-much-sodium-per-day.html">Understand sodium on food labels.</a></p>')
 if p.name=='contact.html':
  s=re.sub(r'<main\b.*?</main>','<main id="main-content"><section class="page-hero contact-plain"><div class="container"><p class="eyebrow">Get in touch</p><h1>Send me a message</h1><p>Have a question, an idea, or spotted something wrong? I’d love to hear from you.</p><a class="contact-email" href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a><p>I read and reply to every email.</p><p class="contact-small">If you found an error, include the page link so I can check it.</p></div></section></main>',s,flags=re.S)
 meta={
  'recipe-macro-scaler.html':('Recipe Portion Calculator: Calories per Serving | GetMacros','Adjust recipe portions and see calories, protein, carbs and fat per portion using the nutrition already listed on your recipe.'),
  'nutrition-label-comparison-tool.html':('Compare Two Foods: Calories & Nutrition | GetMacros','Compare two food labels by serving, equal weight or equal calories. See protein, fiber, added sugar and sodium side by side.'),
  'contact.html':('Contact GetMacros','Have a question, suggestion or correction? Email GetMacros. I read and reply to every email.')
 }
 if p.name in meta:
  title,desc=meta[p.name];s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',s,flags=re.S)
  for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('name','twitter:title',title),('name','twitter:description',desc)]:
   s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
 p.write_text(s,encoding='utf-8')
print('Simplified food tools, contact and the shared footer.')
