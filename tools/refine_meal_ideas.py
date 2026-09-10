"""Replace the pantry form with concrete meal examples and clarify protein pricing."""
from pathlib import Path
import re,html,json
ROOT=Path(__file__).resolve().parents[1]
MEALS=[
 ('bean-rice','Bean & rice bowl','lunch vegetarian','Beans, cooked rice, mixed vegetables and salsa.','Warm the beans and vegetables. Spoon them over cooked rice, then add salsa.','Try chickpeas instead of beans, or use a microwave rice pouch.', 'bowl'),
 ('egg-toast','Eggs on toast','breakfast vegetarian','Eggs, whole-grain bread, tomatoes and a little cooking oil.','Cook the eggs how you like them. Toast the bread and serve with the tomatoes.','Add spinach to the eggs, or use a tortilla instead of toast.', 'toast'),
 ('yogurt-oats','Yogurt, oats & berries','breakfast vegetarian','Plain Greek yogurt, rolled oats, berries and a spoonful of nut butter.','Stir the oats into the yogurt and top with berries and nut butter. Leave overnight in the fridge if you prefer softer oats.','Use a soy yogurt or seed butter if that suits you better. Check the label because protein amounts vary.', 'yogurt'),
 ('chicken-wrap','Chicken & avocado wrap','lunch','Cooked chicken, a tortilla, avocado and shredded cabbage.','Slice the cooked chicken and avocado. Add them to the tortilla with cabbage, then fold and roll.','Use leftover cooked turkey, or chickpeas for a meat-free version.', 'wrap'),
 ('tofu-noodles','Tofu & vegetable noodles','lunch vegetarian','Firm tofu, noodles, frozen vegetables and your favourite stir-fry sauce.','Cook the noodles as directed. Pan-fry cubed tofu, add the vegetables and cook through, then toss with the noodles and sauce.','Use rice instead of noodles. Pick a sauce you enjoy and add a little at a time.', 'noodles'),
 ('tuna-potato','Tuna baked potato','lunch','A potato, canned tuna, plain yogurt and sweetcorn.','Bake or microwave the potato until soft. Mix drained tuna with yogurt and sweetcorn, then spoon over the split potato.','Use mashed beans instead of tuna, or serve the filling in a sandwich.', 'potato')]

def illustration(kind):
 base='<ellipse cx="160" cy="112" rx="100" ry="52" fill="#fffaf0"/><ellipse cx="160" cy="110" rx="86" ry="40" fill="#e6dec9"/>'
 foods={
 'bowl':'<path d="M77 107h166c-10 62-150 62-166 0Z" fill="#47886a"/><ellipse cx="160" cy="104" rx="83" ry="30" fill="#eddbad"/><g fill="#955447"><ellipse cx="113" cy="95" rx="13" ry="8"/><ellipse cx="141" cy="90" rx="13" ry="8"/><ellipse cx="125" cy="113" rx="13" ry="8"/></g><g fill="#438050"><circle cx="190" cy="91" r="13"/><circle cx="212" cy="106" r="12"/><circle cx="182" cy="115" r="12"/></g><path d="m153 112 12-15 13 19Z" fill="#d17e51"/>',
 'toast':'<rect x="96" y="72" width="129" height="76" rx="20" fill="#ba7e42"/><rect x="104" y="79" width="112" height="61" rx="15" fill="#e9bf7c"/><path d="M125 92c-28 4-23 44 7 40 20 9 58 1 58-22 0-24-42-36-65-18Z" fill="#fffcef"/><circle cx="153" cy="109" r="18" fill="#dfa138"/><circle cx="237" cy="104" r="16" fill="#c96c52"/>',
 'yogurt':'<path d="M79 100h162c-6 59-154 59-162 0Z" fill="#719aad"/><ellipse cx="160" cy="100" rx="81" ry="30" fill="#fffcf4"/><g fill="#be9b6f"><ellipse cx="126" cy="91" rx="20" ry="8"/><ellipse cx="138" cy="110" rx="22" ry="8"/></g><g fill="#655684"><circle cx="184" cy="88" r="10"/><circle cx="208" cy="101" r="11"/><circle cx="180" cy="116" r="10"/></g>',
 'wrap':'<path d="m96 88 131-10-41 76-77-19Z" fill="#d5a96b"/><path d="m96 88 90 66-77-19Z" fill="#f2d59e"/><path d="m108 83 108-12-19 32Z" fill="#638c4b"/><path d="m131 81 48-5 19 13-52 9Z" fill="#e9c79c"/><path d="m189 73 23 6-10 17-20-6Z" fill="#a8bb70"/>',
 'noodles':'<path d="M78 105h164c-8 62-156 62-164 0Z" fill="#7394a0"/><ellipse cx="160" cy="104" rx="82" ry="29" fill="#d9b56b"/><g fill="none" stroke="#f7df9e" stroke-width="4"><path d="M108 93q75 45 91 0M103 103q55 35 100 0M123 87q-10 45 55 29"/></g><g fill="#eee0b6"><rect x="121" y="79" width="24" height="19" rx="3"/><rect x="163" y="105" width="24" height="19" rx="3"/></g><g fill="#4b8452"><circle cx="201" cy="91" r="13"/><circle cx="106" cy="111" r="12"/></g>',
 'potato':'<ellipse cx="160" cy="109" rx="72" ry="39" fill="#ac7846"/><ellipse cx="160" cy="105" rx="61" ry="27" fill="#f1d690"/><path d="M114 100q44-32 91 0l-7 19h-76Z" fill="#e6c5b3"/><g fill="#ddb74b"><circle cx="128" cy="100" r="6"/><circle cx="167" cy="91" r="6"/><circle cx="183" cy="112" r="6"/></g><path d="m144 101 11 6 15-5" fill="none" stroke="#548557" stroke-width="5"/>'}
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 190">'+base+foods[kind]+'</svg>'

def render():
 cards=[]
 for slug,title,tags,ingredients,method,swap,kind in MEALS:
  (ROOT/'images'/('meal-idea-'+slug+'.svg')).write_text(illustration(kind),encoding='utf-8')
  cards.append('<article class="meal-idea" data-meal-tags="'+tags+'"><div class="meal-idea-art"><img src="images/meal-idea-'+slug+'.svg" width="320" height="190" alt="" loading="lazy"></div><div class="meal-idea-copy"><h2>'+html.escape(title)+'</h2><p class="meal-idea-ingredients"><strong>Ingredients:</strong> '+html.escape(ingredients)+'</p><p>'+html.escape(method)+'</p><details><summary>Easy swap</summary><p>'+html.escape(swap)+'</p></details></div></article>')
 return '<main id="main-content"><section class="meal-ideas-intro container"><h1>Simple Meal Ideas</h1><p>Cooking at home? Start with one of these six easy meals and adjust the portions to suit you.</p></section><section class="container meal-ideas-library" aria-label="Meal ideas"><div class="meal-idea-filters" role="group" aria-label="Filter meal ideas" hidden><button type="button" data-meal-filter="all" aria-pressed="true">All meals</button><button type="button" data-meal-filter="breakfast" aria-pressed="false">Breakfast</button><button type="button" data-meal-filter="lunch" aria-pressed="false">Lunch &amp; dinner</button><button type="button" data-meal-filter="vegetarian" aria-pressed="false">Vegetarian</button></div><p class="meal-idea-status sr-only" role="status"></p><div class="meal-ideas-grid">'+''.join(cards)+'</div></section><section class="container meal-ideas-next"><h2>Make it fit your day</h2><p>These are meal ideas, not calculated macro totals. Your ingredients, brands and portions determine the numbers.</p><div><a class="btn action-link" href="calculators.html">Find my daily macros</a><a class="btn action-link" href="how-to-calculate-recipe-nutrition.html">Work out a meal’s macros</a></div></section></main>'

def run():
 for p in ROOT.glob('*.html'):
  s=p.read_text(encoding='utf-8')
  for old,new in [('Which protein costs less?','Protein Cost per Gram Calculator'),('Compare protein prices','Protein Cost per Gram Calculator'),('Protein Price Calculator: Compare Cost per Gram','Protein Cost per Gram Calculator'),('Meals from your ingredients','Simple Meal Ideas'),('Budget meal builder','Simple meal ideas'),('See what you can make with what you have.','Easy meals with ingredients and quick preparation tips.')]:s=s.replace(old,new)
  if p.name=='budget-meal-builder.html':
   s=re.sub(r'<main\b[^>]*>.*?</main>',render(),s,count=1,flags=re.S)
   s=re.sub(r'<body[^>]*>','<body class="site-v3 meal-ideas-page" data-design-family="meal">',s,count=1)
   s=re.sub(r'<script src="js/(?:budget-builder|meal-ideas|main|lang|calculator-suite)\.js[^\"]*"[^>]*></script>','',s)
   if 'js/meal-ideas.js' not in s:s=s.replace('</body>','<script src="js/meal-ideas.js" defer></script></body>')
   title='Simple Meal Ideas: Easy Breakfasts, Lunches & Dinners | GetMacros';desc='Six simple meal ideas with ingredients, quick preparation steps and easy swaps. Find breakfast, lunch, dinner and vegetarian options.'
   s=re.sub(r'<title>.*?</title>','<title>'+html.escape(title)+'</title>',s,flags=re.S)
   for key,value in [('description',desc),('og:description',desc),('twitter:description',desc),('og:title',title),('twitter:title',title)]:s=re.sub(r'(<meta (?:name|property)="'+key+'" content=")[^\"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],s)
   # This is an article collection now, not a calculator application.
   s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
  p.write_text(s,encoding='utf-8')
 # Refresh the two search cards after final page titles have been applied.
 p=ROOT/'search.html';s=p.read_text(encoding='utf-8')
 def preview(m):
  block=m[0];u=re.search(r'href="([^\"]+)"',block)
  if not u or u[1] not in ['budget-meal-builder.html','protein-value-calculator.html']:return block
  target=(ROOT/u[1]).read_text(encoding='utf-8');title=re.search(r'<h1[^>]*>(.*?)</h1>',target,re.S)[1];desc=re.search(r'<meta name="description" content="([^\"]+)"',target)[1]
  block=re.sub(r'(<span class="search-hit-name">).*?(</span>)',lambda n:n[1]+title+n[2],block,flags=re.S)
  block=re.sub(r'(<span class="search-hit-copy">).*?(</span>)',lambda n:n[1]+desc+n[2],block,flags=re.S)
  return re.sub(r'data-search="[^\"]*"','data-search="'+html.escape(html.unescape(title+' '+desc),quote=True)+'"',block)
 s=re.sub(r'<a\b[^>]*class="[^"]*search-hit[^\"]*"[^>]*>.*?</a>',preview,s,flags=re.S);p.write_text(s,encoding='utf-8')
if __name__=='__main__':run()
