"""Second creative direction: structural migrations, not an override cascade."""
import re
from html import escape
from normalize_calculator_layouts import Document
THEME="try{var p=localStorage.getItem('gm-theme');document.documentElement.dataset.theme=p==='light'||p==='dark'?p:(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}catch(e){document.documentElement.dataset.theme='light'}"
def transform(text,name):
 text=text.replace('data-design="botanical"','data-design="edition"')
 text=re.sub(r'<script>try\{document.documentElement.dataset.theme=.*?</script>','<script>'+THEME+'</script>',text,flags=re.S)
 text=re.sub(r'<link\b(?=[^>]*rel="preload")(?=[^>]*fraunces)[^>]*>','',text)
 text=re.sub(r'<link\b(?=[^>]*rel="preload")(?=[^>]*manrope)[^>]*>','',text)
 if name=='restaurant-meal-finder.html':
  start=text.index('<section class="match-intro"') if '<section class="match-intro"' in text else -1
  if start!=-1:
   end=text.index('<!--MEALS:START-->',start)
   text=text[:start]+'''<section class="finder-introduction container"><p class="section-overline">Find your next order</p><h1>Healthy fast-food meals</h1><p>Compare calories, protein and what’s included. Adjust the filters to make the list yours.</p></section>
<section class="finder-shell container"><div id="meal-quiz"><p role="status">Loading meal filters…</p><p><a href="#browse-meals">Browse the recorded meals</a> while the finder loads.</p></div></section>
'''+text[end:]
  text=re.sub(r'<script\b[^>]*src="js/meal-quiz.js[^>]*>.*?</script>','<script src="js/meal-finder.js" defer></script>',text)
  text=re.sub(r'<link\b[^>]*href="js/meal-quiz.js[^>]*>','',text)
  text=text.replace('<strong>Browse all meals</strong>','<strong>All recorded orders &amp; restaurant links</strong>')
 text=re.sub(r'<div class="hub-art"[^>]*>.*?</div>','',text,flags=re.S)
 # Article summaries already explain the point. Remove disconnected fact slogans
 # and repeated abstract art instead of dressing those fragments as cards.
 text=re.sub(r'<div class="article-facts">.*?</div>','',text,flags=re.S)
 text=re.sub(r'<figure class="article-illustration">.*?</figure>','',text,flags=re.S)
 if name=='calculators.html':
  activities=[('Mostly sitting · little exercise','Mostly sitting'),('Light activity · 1–3 days/week','Lightly active'),('Moderate activity · 3–5 days/week','Moderately active'),('Very active · 6–7 days/week','Very active')]
  for old,new in activities:text=text.replace(old,new)
  if 'id="activity-examples"' not in text:
   text=re.sub(r'(<select id="activity".*?</select>)',r'\1<details id="activity-examples" class="calc-assumptions"><summary>Activity examples</summary><p>Mostly sitting: little exercise. Lightly active: exercise 1–3 days a week. Moderately active: 3–5 days. Very active: 6–7 days. Choose physical job + training if both are part of your routine.</p></details>',text,count=1,flags=re.S)
  note=re.search(r'<p class="clarity-hint publication-calculator-note">.*?</p>',text,re.S)
  if note:
   text=text.replace(note[0],'')
   text=text.replace('Calculate my macros</button>','Calculate my macros</button>'+note[0],1)
  text=text.replace('<form class="calc-form" id="macro-form">','<form class="calc-form compact-macro-form" id="macro-form">')
 if 'data-chain-form' in text:
  chain=re.search(r'data-chain="([^"]+)"',text)
  if chain:
   chain=chain[1]
   doc=Document(text)
   form=next((n for n in doc.nodes if n['tag']=='form' and 'data-chain-form' in n['attrs']),None)
   if form and 'end' in form:
    replacement='<form class="restaurant-entry" action="restaurant-meal-finder.html" method="get"><input type="hidden" name="chain" value="'+escape(chain,quote=True)+'"><label>Calories, up to<input type="number" name="maxCal" min="150" max="2500" placeholder="Any" inputmode="numeric"></label><label>Protein, at least (g)<input type="number" name="minProtein" min="0" max="200" placeholder="Any" inputmode="numeric"></label><button class="btn btn-primary" type="submit">Find a '+escape(chain)+' meal</button></form>'
    text=text[:form['start']]+replacement+text[form['end']:]
   text=re.sub(r'<div\b[^>]*data-chain-results[^>]*>.*?</div>','',text,flags=re.S)
   text=re.sub(r'<script\b[^>]*src="js/chain-meal-finder.js[^>]*>.*?</script>','',text)
 text=re.sub(r'<span class="clarity-icon"[^>]*>.*?</span>','',text,flags=re.S)
 text=text.replace('The journal','Food & nutrition').replace('The GetMacros Journal','Food & nutrition')
 text=re.sub(r'\sdata-(?:page-tone|design-family|spotlight|reveal-title)(?:="[^"]*")?','',text)
 text=re.sub(r'\sclass="([^"]*)"',lambda m:' class="'+' '.join(c for c in m[1].split() if c not in {'liquid-surface','site-v3','finder-v2','order-match-page','site-v4','interactive-page'})+'"',text)
 text=text.replace('Protein Cost per Gram Calculator','Protein cost per gram calculator').replace('Simple Meal Ideas','Simple meal ideas')
 text=text.replace('A multigrain bun and grilled fillet. The reliable everyday order.','A grilled chicken fillet on a multigrain bun. Sides, sauces and drinks are separate.')
 text=text.replace('Choose your goals and restaurants. Get a shortlist with the nutrition beside it.','Set a calorie or protein limit, choose restaurants and compare the orders.')
 text=text.replace('Choose two or three affordable protein anchors','Choose two or three affordable protein foods')
 if name=='blog.html':
  text=re.sub(r'<title>.*?</title>','<title>Food &amp; nutrition articles | GetMacros</title>',text,count=1,flags=re.S)
 if name=='restaurant-meal-finder.html':
  text=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="Compare U.S. fast-food orders by calories, protein, fiber and sodium. Filter by restaurant, see what is included and compare two meals side by side.">',text)
 # Keep social previews aligned after the page-specific editorial changes.
 title=re.search(r'<title>(.*?)</title>',text,re.S)
 description=re.search(r'<meta name="description" content="([^"]*)"',text)
 for key,value in [('title',title[1] if title else ''),('description',description[1] if description else '')]:
  if value:
   text=re.sub(r'(<meta (?:property|name)="(?:og|twitter):'+key+r'" content=")[^"]*(")',lambda m:m[1]+value+m[2],text)
 return text
