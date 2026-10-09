"""Composed release surfaces; run after the shared publication build."""
from pathlib import Path
from html import escape
import json,re
from normalize_calculator_layouts import Document
from redesign_inventory import family
R=Path(__file__).resolve().parents[1]

def food(name,interactive=False):
 return '<span data-food-character="'+name+'"'+(' data-interactive="true"' if interactive else ' aria-hidden="true"')+'><svg viewBox="0 0 160 160" aria-hidden="true"><use href="images/food-characters.svg#food-'+name+'"/></svg></span>'
def replace(text,cls,value):
 node=Document(text).find(cls=cls)
 return text[:node['start']]+value+text[node['end']:] if node else text
ARROW='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>'
def task(url,title,detail):return '<a '+('data-market-route="finder" ' if url=='restaurant-meal-finder.html' else '')+'href="'+url+'"><span>'+title+'</span><small>'+detail+'</small>'+ARROW+'</a>'

def calculator(text):
 head='<section class="market-page-head"><div class="container"><div class="tools-masthead"><div><h1>Macro calculator.</h1><nav class="tool-jump" aria-label="Calculator tasks"><a href="#macro-calculator">My daily macros</a><a href="#food-tools">Meal &amp; portion tools</a><a href="#single-macro-calculators">Individual nutrients</a></nav></div>'+food('broccoli')+'</div></div></section>'
 text=replace(text,'market-page-head',head)
 text=re.sub(r'<!-- workbench-heading:start -->.*?<!-- workbench-heading:end -->','',text,flags=re.S)
 text=text.replace('<div class="calculation-workbench">','<!-- workbench-heading:start --><div class="workbench-heading"><p>Enter your details for an adult calorie and macro estimate.</p></div><!-- workbench-heading:end --><div class="calculation-workbench">',1)
 waiting='<div class="calculator-waiting">'+food('egg')+'<h3>A starting point.<br>Not a prescription.</h3><p>Your calorie and macro estimates appear here when you finish.</p><a class="text-action" href="sources.html">How it works '+ARROW+'</a></div>'
 text=replace(text,'calculator-waiting',waiting)
 groups='<section class="clear-tool-library clarity-library" id="tool-library"><div class="container"><div class="section-heading"><h2>Other nutrition tools</h2></div><span id="food-tools"></span><div class="tool-tasks"><div class="tool-task-group"><h3>At the kitchen table</h3>'+task('recipe-macro-scaler.html','Recipe portions','Divide a whole recipe into the portions you serve.')+task('budget-meal-builder.html','Simple meal ideas','Six straightforward meals to make at home.')+task('protein-value-calculator.html','Protein cost per gram','Compare two packages using your own prices.')+'</div><div class="tool-task-group"><h3>Read the label</h3>'+task('nutrition-label-comparison-tool.html','Compare food labels','Use the same weight or calorie amount.')+task('sodium-label-comparison-tool.html','Sodium in your portion','Scale two labels to what you actually eat.')+task('carbohydrate-label-portion-tool.html','Carbs in your portion','Half a serving, a whole package, or anything between.')+'</div><div class="tool-task-group"><h3>Planning &amp; movement</h3><span id="goal-tools"></span>'+task('weight-goal-timeline-calculator.html','Weight-goal timeline','Model a pace you choose; real progress varies.')+task('sweat-rate-calculator.html','Sweat loss per workout','Estimate fluid loss from measured weight changes.')+'</div><div class="tool-task-group"><h3>Put a number to work</h3>'+task('restaurant-meal-finder.html','Find a meal','Use calorie and protein limits with source-linked orders.')+task('sources.html','Sources &amp; methods','See the formulas, assumptions and boundaries.')+'</div></div><section class="portion-example" aria-labelledby="portion-example-title"><div><h3 id="portion-example-title">Same recipe.<br>A different portion.</h3><p>Illustrative example: a recipe with 2,400 kcal in total.</p><a class="text-action" href="recipe-macro-scaler.html">Calculate all the macros '+ARROW+'</a></div><form id="portion-example-form"><label>Total recipe calories<input name="total" type="number" min="0" max="100000" step="any" value="2400" required></label><label>Number of portions<input name="portions" type="number" min="1" max="1000" step="1" value="6" required></label><output id="portion-example-output" aria-live="polite">400 kcal per portion<small>2,400 ÷ 6 equal portions</small></output></form></section></div></section>'
 return replace(text,'clear-tool-library',groups)

def shell(title,desc,url,main):
 template=(R/'about.html').read_text(encoding='utf-8');d=Document(template);n=next(n for n in d.nodes if n['tag']=='main');s=template[:n['start']]+main+template[n['end']:]
 s=re.sub(r'<title>.*?</title>','<title>'+escape(title)+' | GetMacros</title>',s,count=1,flags=re.S)
 for attr,key,value in [('name','description',desc),('property','og:title',title+' | GetMacros'),('property','og:description',desc),('property','og:url','https://getmacros.net/'+url),('name','twitter:title',title+' | GetMacros'),('name','twitter:description',desc)]:s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*',lambda m:m[1]+escape(value,quote=True),s,count=1)
 s=re.sub(r'<link rel="canonical" href="[^"]+">','<link rel="canonical" href="https://getmacros.net/'+url+'">',s,count=1)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
 return s

def run():
 p=R/'calculators.html';p.write_text(calculator(p.read_text(encoding='utf-8')),encoding='utf-8')
 main='<main id="main-content" class="container"><section class="shelf-heading"><div><h1>Your food shelf.</h1><p class="shelf-note">Meals, reads and games you want to come back to.</p></div>'+food('avocado')+'</section><p class="shelf-note">Stored only in this browser. No account, syncing or health profile. Private browsing and clearing site data can remove your saves.</p><div id="food-shelf"><section class="shelf-empty"><h2>Make a little room.</h2><p>Save an order in the meal finder, or bookmark a guide or game.</p><div class="action-row"><a class="text-action" href="restaurant-meal-finder.html?view=saved">Saved meals '+ARROW+'</a><a class="text-action" href="articles.html">Find a read '+ARROW+'</a></div></section></div></main>'
 (R/'food-shelf.html').write_text(shell('Saved meals, articles and games','Keep your favorite meals, practical guides and games on a local food shelf. No account needed.','food-shelf.html',main),encoding='utf-8')
 for path in R.glob('*.html'):
  text=path.read_text(encoding='utf-8')
  text=re.sub(r'<link[^>]*href="css/food-shelf.css[^>]*>','',text)
  if family(path.name,text)=='article':
   text=re.sub(r'<!-- shelf-action:start -->.*?<!-- shelf-action:end -->','',text,flags=re.S)
   d=Document(text);h=next(n for n in d.nodes if n['tag']=='h1');title=re.sub('<[^>]*>','',text[h['inner']:h['close']])
   action='<div class="article-actions"><button type="button" data-shelf-save data-kind="article" data-url="'+path.name+'" data-title="'+escape(title,quote=True)+'" aria-pressed="false">Save this guide</button><a class="text-action" href="food-shelf.html">Your shelf '+ARROW+'</a></div>'
   text=text[:h['end']]+'<!-- shelf-action:start -->'+action+'<!-- shelf-action:end -->'+text[h['end']:]
  if family(path.name,text)=='article' or path.name=='food-shelf.html' or 'class="play-page' in text or 'data-game-id' in text:
   text=re.sub(r'<script[^>]*src="js/food-shelf.js[^>]*>.*?</script>','',text,flags=re.S)
   text=text.replace('</body>','<script src="js/food-shelf.js" defer></script></body>')
   text=text.replace('</head>','<link rel="stylesheet" href="css/food-shelf.css"></head>')
  path.write_text(text,encoding='utf-8')
 print('Calculator composition, task hub, live portion example and local food shelf built.')
if __name__=='__main__':run()
