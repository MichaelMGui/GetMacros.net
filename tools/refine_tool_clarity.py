"""Make each existing food tool explain a concrete task with less framing."""
from pathlib import Path
import html, json, re
from normalize_calculator_layouts import Document

ROOT=Path(__file__).resolve().parents[1]
PAGES={
 'recipe-macro-scaler.html':('Calories per recipe portion','Split one batch into different portions, or change how much you make. Use the nutrition already listed on your recipe.'),
 'nutrition-label-comparison-tool.html':('Compare two food labels','Choosing between two foods? Compare their labels per serving, per 100 g or per 100 calories.'),
 'protein-value-calculator.html':('Which protein costs less?','Compare two packages to find the cost of the same amount of protein.'),
 'sodium-label-comparison-tool.html':('Sodium in your food portion','Compare two foods using the sodium on each label and the number of servings you eat.'),
 'carbohydrate-label-portion-tool.html':('Carbs in your food portion','Enter the carbs on the label and how many servings you eat. For half a serving, enter 0.5.'),
 'budget-meal-builder.html':('What can I make with these ingredients?','Choose what you have. Find simple meal ideas and see any missing ingredients.'),
 'weight-goal-timeline-calculator.html':('When could I reach my goal weight?','Choose a weekly pace to see a possible timeline. This is a calculation, not a prediction of your progress.'),
 'sweat-rate-calculator.html':('How much did I sweat?','Use your weight before and after a workout, its length and what you drank to estimate fluid loss.'),
}
ICONS={
 'portions':'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16m6-16v16M3 12h18"/>',
 'labels':'<rect x="3" y="4" width="7" height="16" rx="2"/><rect x="14" y="4" width="7" height="16" rx="2"/><path d="M5 9h3m-3 4h3m8-4h3m-3 4h3"/>',
 'price':'<path d="M3 4h9l9 9-8 8-10-10V4Z"/><circle cx="8" cy="9" r="1.5"/>',
 'pantry':'<path d="M4 7h16v13H4V7Zm2-3h12v3M8 12h8m-8 4h5"/>',
 'drop':'<path d="M12 3s-7 8-7 12a7 7 0 0 0 14 0c0-4-7-12-7-12Z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
 'carbs':'<path d="M12 21V4M12 9C8 9 6 7 6 4c4 0 6 2 6 5Zm0 6c4 0 6-2 6-5-4 0-6 2-6 5Z"/>',
 'date':'<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v4m10-4v4M3 11h18m-13 5h3"/>',
}

def icon(key):
 return '<span class="clarity-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+ICONS[key]+'</svg></span>'

def replace_class(s, cls, replacement):
 d=Document(s)
 n=next((n for n in d.nodes if cls in n['attrs'].get('class','').split() and 'end' in n),None)
 return s[:n['start']]+replacement+s[n['end']:] if n else s

def directory():
 everyday=[
  ('recipe-macro-scaler.html','Calories per recipe portion','Turn a recipe for four into six portions.','portions'),
  ('nutrition-label-comparison-tool.html','Compare food labels','Check two foods at the same weight or calories.','labels'),
  ('protein-value-calculator.html','Compare protein prices','Find the better value between two packages.','price'),
  ('budget-meal-builder.html','Meals from your ingredients','See what you can make with what you have.','pantry'),
 ]
 more=[
  ('sodium-label-comparison-tool.html','Sodium in your portion','Compare the amounts you actually eat.','drop'),
  ('carbohydrate-label-portion-tool.html','Carbs in your portion','Adjust the label for half, one or more servings.','carbs'),
  ('weight-goal-timeline-calculator.html','Weight-goal timeline','See dates based on a weekly pace you choose.','date'),
  ('sweat-rate-calculator.html','Sweat loss per workout','Estimate fluid loss from your measurements.','drop'),
 ]
 def cards(items):
  return '<div class="clear-tool-grid clarity-tool-grid">'+''.join('<a class="clear-tool-card" href="'+url+'">'+icon(ic)+'<span><h3>'+title+'</h3><p>'+desc+'</p></span></a>' for url,title,desc,ic in items)+'</div>'
 return '<section class="clear-tool-library clarity-library" id="tool-library"><div class="container"><h2>Cooking or choosing food?</h2><span id="food-tools"></span>'+cards(everyday)+'<details class="clarity-more"><summary>More calculators</summary><span id="goal-tools"></span>'+cards(more)+'</details></div></section>'

def recipe_inputs(s):
 def field(id,label):
  inp=re.search(r'<input\b[^>]*id="'+id+r'"[^>]*>',s)[0]
  return '<div class="field"><label for="'+id+'">'+label+'</label>'+inp+'</div>'
 return '<div class="tool-inputs recipe-clear-inputs"><div class="field"><label for="recipe-mode">What are you changing?</label><select id="recipe-mode"><option value="portion">Number of portions</option><option value="scale">Size of the whole batch</option></select></div><fieldset><legend>Portions</legend><div class="clarity-fields">'+field('orig','Original recipe')+field('nextServ','New amount')+'</div></fieldset><fieldset><legend>Nutrition per original portion</legend><p class="clarity-hint">Edit the example values. Results update as you type.</p><div class="clarity-fields">'+field('cal','Calories')+field('pro','Protein (g)')+field('carb','Carbs (g)')+field('fat','Fat (g)')+'</div></fieldset></div>'

def run():
 for path in ROOT.glob('*.html'):
  s=path.read_text(encoding='utf-8')
  if path.name in PAGES:
   title,desc=PAGES[path.name]
   s=re.sub(r'(<body\b[^>]*class=")([^\"]*)"',lambda m:m[1]+m[2]+(' clarity-tool' if 'clarity-tool' not in m[2].split() else '')+'"',s,count=1)
   s=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(title)+m[2],s,count=1,flags=re.S)
   s=re.sub(r'(<h1\b[^>]*>.*?</h1>\s*<p\b[^>]*>).*?(</p>)',lambda m:m[1]+html.escape(desc)+m[2],s,count=1,flags=re.S)
   for attr,key,value in [('name','description',desc),('property','og:description',desc),('name','twitter:description',desc)]:
    s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
   # Keep useful, descriptive search titles while matching the visible purpose.
   seo={'recipe-macro-scaler.html':'Recipe Portion Calculator: Calories per Serving', 'nutrition-label-comparison-tool.html':'Compare Nutrition Labels: Calories, Protein & More', 'protein-value-calculator.html':'Protein Price Calculator: Compare Cost per Gram'}
   if path.name in seo:
    t=seo[path.name]+' | GetMacros';s=re.sub(r'<title>.*?</title>','<title>'+html.escape(t)+'</title>',s,flags=re.S)
    for attr,key in [('property','og:title'),('name','twitter:title')]:s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*(")',lambda m:m[1]+html.escape(t)+m[2],s)
   s=re.sub(r'<input\b[^>]*type="number"[^>]*>',lambda m:m[0] if 'inputmode=' in m[0] else m[0][:-1]+' inputmode="decimal">',s)
  if path.name=='calculators.html':
   s=replace_class(s,'clear-tool-library',directory())
   if 'class="calc-purpose"' not in s:s=s.replace('</h1></div><div class="calc-welcome-macros"','</h1><p class="calc-purpose">Find daily calorie, protein, carb and fat targets for your goal.</p></div><div class="calc-welcome-macros"',1)
   s=s.replace('Just one macro?','Calculate protein, fat or carbs')
   s=re.sub(r'(Get (?:protein|fat|carb) target)\s*(?:→|&rarr;)',r'\1',s)
  if path.name=='recipe-macro-scaler.html':
   s=replace_class(s,'tool-inputs',recipe_inputs(s))
   s=replace_class(s,'suite-hero-mark','<div class="suite-hero-mark" aria-hidden="true">'+icon('portions')+'</div>')
   if 'id="recipe-result-title"' not in s:s=s.replace('<aside class="tool-output" aria-label="Calculation results">','<aside class="tool-output" aria-label="Calculation results"><h2 id="recipe-result-title">Per new portion</h2>',1)
  if path.name=='nutrition-label-comparison-tool.html':
   s=s.replace('Example values are filled in. Replace them with the numbers on your two labels.','Example labels are filled in. Replace them with your foods.')
   s=s.replace('One listed serving of each','One serving of each food').replace('The same weight: 100 g','Equal weight: 100 g').replace('The same calories: 100 kcal','Equal calories: 100 kcal')
   if 'id="comparison-note"' not in s:s=s.replace('<div class="table-wrap">','<p class="clarity-hint" id="comparison-note"></p><div class="table-wrap">',1)
   s=replace_class(s,'simple-tool-help','<section class="simple-tool-help clarity-help"><div class="container"><details><summary>Which comparison should I use?</summary><p><strong>Per serving:</strong> the amounts listed on the packages. <strong>Per 100 g:</strong> equal weights, useful when serving sizes differ. <strong>Per 100 calories:</strong> nutrients for the same energy.</p><p>Choose the numbers that matter to your meal. This tool does not give foods an overall health score.</p><a class="btn action-link" href="how-to-read-a-nutrition-label.html">Understand a food label</a></details></div></section>')
  if path.name=='protein-value-calculator.html':
   s=s.replace('Enter prices in US dollars. Results update as you type.','Example prices in US dollars. Results update as you type.').replace('Example prices in US dollars. Replace them with your two packages.','Example prices in US dollars. Results update as you type.')
   s=s.replace('<strong>Food A</strong>','<strong>First food</strong>').replace('<strong>Food B</strong>','<strong>Second food</strong>')
   for letter,name in [('a','First food'),('b','Second food')]:
    s=re.sub(r'<div class="result"><span>(?:Food [AB]|First food|Second food)</span><strong id="r'+letter+r'">.*?</strong><small id="r'+letter+r'25">.*?</small></div>','<div class="result price-result"><span>'+name+'</span><strong id="r'+letter+'25">—</strong><small>per 25 g protein</small><span id="r'+letter+'" class="price-per-gram">—</span></div>',s,count=1,flags=re.S)
  if path.name=='about.html':
   s=s.replace('83</strong><small>tracked menu options','83</strong><small>menu options')
   s=s.replace('Food choices are easier when the numbers make sense.','Find meals that fit your goals, work out daily targets and make sense of food labels.')
   s=s.replace('GetMacros is an independent site for finding restaurant meals and understanding everyday nutrition.','GetMacros helps you find restaurant meals, work out daily targets and compare food labels.')
  path.write_text(s,encoding='utf-8')
 # Search previews should use the actual final page names, including the home.
 path=ROOT/'search.html';s=path.read_text(encoding='utf-8')
 def preview(m):
  block=m[0];u=re.search(r'href="([^"#]+)',block)
  if not u or not (ROOT/u[1]).is_file():return block
  target=(ROOT/u[1]).read_text(encoding='utf-8');h=re.search(r'<h1\b[^>]*>(.*?)</h1>',target,re.S);d=re.search(r'<meta name="description" content="([^"]+)"',target)
  if not h or not d:return block
  title=html.unescape(re.sub('<[^>]+>',' ',h[1])).strip();desc=html.unescape(d[1])
  for cls,value in [('search-hit-name',title),('search-hit-copy',desc)]:block=re.sub(r'(<span class="'+cls+'">).*?(</span>)',lambda n:n[1]+html.escape(value)+n[2],block,flags=re.S)
  seo=re.search(r'<title>(.*?)</title>',target,re.S)
  terms=title+' '+desc+' '+(html.unescape(seo[1]) if seo else '')+' '+u[1].removesuffix('.html').replace('-',' ')
  return re.sub(r'data-search="[^"]*"','data-search="'+html.escape(terms,quote=True)+'"',block)
 s=re.sub(r'<a\b[^>]*class="[^"]*search-hit[^\"]*"[^>]*>.*?</a>',preview,s,flags=re.S)
 path.write_text(s,encoding='utf-8')
 print('Clarified eight tools, prioritised the calculator library and refreshed search previews.')

if __name__=='__main__':run()
