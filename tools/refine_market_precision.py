"""One-time editorial/layout migration; maintained styles stay in the Market sources."""
from pathlib import Path
import re, json
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
changes=[]
def edit(file, pairs):
 p=ROOT/file;s=p.read_text(encoding='utf-8')
 for old,new in pairs:
  if old in s:
   s=s.replace(old,new);changes.append({'file':file,'removed':old,'replacement':new})
 p.write_text(s,encoding='utf-8')

# Preserve the direction; remove competing captions and repeat instructions.
edit('tools/market-home.inc',[
 ('<p class="section-overline">The healthy fast-food meal finder</p><h1>Fast food.<br><span>Your macros.</span></h1><p>Find an order that fits your calories and protein.</p>', '<h1>Fast food.<br><span>Your macros.</span></h1><p>Find fast-food meals by calories and protein.</p>'),
 ('<p class="section-overline">A place in mind?</p><h2>Start with the restaurant.</h2>', '<h2>Choose a restaurant</h2>'),
 ('<p class="section-overline">The rest of your day</p><h2>Know your starting point.</h2><p>Estimate your daily calories, protein, carbs and fat. Then explore meals that work for you.</p>', '<h2>Your daily<br>starting point.</h2><p>Estimate calories, protein, carbs and fat for your goal.</p>'),
 ('<p class="section-overline">Food, explained</p><h2>A little clarity goes a long way.</h2>', '<h2>Nutrition, explained</h2>'),
 ('<strong>Numbers you can check.</strong><p>Order details link to restaurant sources. Unknown nutrition stays unknown.</p>', '<p>Every recorded order links to its restaurant nutrition source.</p>'),
])
edit('tools/market-header.inc',[
 ('<p class="brand-caption">Food choices.<br>Clearer numbers.</p>',''),
 ('<p class="mobile-menu-title">Where would you like to go?</p>','<p class="mobile-menu-title">Explore GetMacros</p>'),
 ('<p class="menu-heading">Know your order</p>',''),('<p class="menu-heading">Work out the numbers</p>',''),('<p class="menu-heading">A useful read</p>',''),
 ('<small>Bowls and salads</small>',''),('<small>Sandwiches and nuggets</small>',''),
 ('<small>Where our information comes from</small>',''),('<small>Your daily calorie and macro estimate</small>',''),
])
edit('tools/market-footer.inc', [('<p>Good decisions start<br>with useful information.</p>','')])
edit('tools/market-blog.inc', [('<p>Everyday questions. Evidence you can follow.</p>',''),('<p class="section-overline">In the journal</p>',''),('<p>Different numbers, different jobs.</p>',''),('<strong>Start with the basics.</strong><p>Understand calories, macros and food labels.</p>','<p>New to macros and food labels?</p>')])
edit('js/meal-finder.js',[
 ('<h2>Make it your meal.</h2>','<h2>Filter meals</h2>'),
 ('<p class="section-overline">On your shortlist</p>',''),
 ('<span>Goals, food choices &amp; nutrients</span>',''),
 ('<small>One or more</small>',''),
 ('<p>Unknown values cannot meet a numeric limit.</p>',''),
 ('<h3>What\'s included</h3>',''),
 ('<p>Per listed order. Extras are separate unless included above. Missing numbers are not zero.</p>','<p>Extras are separate unless listed above. Unverified values are not zero.</p>'),
 ("+' meal'+(results.length===1?'':'s')", "+' meal'+(results.length===1?'':'s')+' match'"),
 ('<a href="${esc(m.url)}">${esc(m.chain)}</a>', '<a href="${esc(m.url)}">${restaurantMark(m.chain)}<span>${esc(m.chain)}</span></a>'),
 ('<span>${esc(label)}</span>', '<span>${esc(label)}</span>'),
 ])

# All retained HTML is the editable inner-page source, not a second generator.
copy={
 'Find daily calorie, protein, carb and fat targets for your goal.':'Estimate your daily calories and macros.',
 'Pick a restaurant. Compare U.S. menu options, calories, protein and ordering tips.':'15 U.S. restaurant chains. Compare the exact order and portion.',
 'Find a clear answer to your food and nutrition questions.':'',
 'Pick foods for your meals. Each card shows protein in a typical portion.':'Protein per typical portion, with food sources below.',
 'Cooking at home? Start with one of these six easy meals and adjust the portions to suit you.':'Six meals to make at home. Adjust the portions to suit you.',
 'Find meals from different restaurants for your goals.':'',
 'Enter your details and calculate to see calories, protein, carbs and fat.':'',
 'Your protein range will appear here.':'',
 'Enter calories to see your range.':'',
 'Easy meals with ingredients and quick preparation tips.':'',
 'Compare the amounts you actually eat.':'',
 'Compare calories, protein and what’s included. Adjust the filters to make the list yours.':'',
 'The number studio':'Calculators',
 'The GetMacros reader':'Nutrition guide',
 'The recorded menu':'',
 'Cooking or choosing food?':'Food calculators',
 'Questions, ideas or something not working? I read and reply to every email.':'Questions, ideas or a problem with the site? Get in touch.',
}
for p in ROOT.glob('*.html'):
 s=p.read_text(encoding='utf-8')
 for old,new in copy.items():
  if old in s:
   # Only visible text; do not rewrite metadata or structured data by accident.
   s=re.sub(r'(?<=>)'+re.escape(old)+r'(?=<)',lambda m:new,s)
   changes.append({'file':p.name,'removed':old,'replacement':new})
 s=re.sub(r'<p\b(?![^>]*(?:\bid=|\bdata-|\brole=))[^>]*>\s*</p>','',s)
 s=re.sub(r'<span class="result-placeholder">\s*</span>','',s)
 s=re.sub(r'<script\b[^>]*src="js/page-experience\.js[^>]*>.*?</script>','',s,flags=re.S)
 s=s.replace('<p class="section-overline">Find your next order</p>','')
 s=s.replace('<div class="work-empty-art" aria-hidden="true"><i></i><i></i><i></i></div>','')
 if p.name=='calculators.html':
  # Move native unit choices alongside their label, outside the aligned input rows.
  d=Document(s);form=next(n for n in d.nodes if n['attrs'].get('id')=='macro-form')
  old=s[form['inner']:form['close']]
  activity=re.search(r'<div class="field">\s*<label for="activity">.*?</select>',old,re.S)[0]+'</div>'
  goal=re.search(r'<div class="field">\s*<label for="goal">.*?</select>',old,re.S)[0]+'</div>'
  helps=re.findall(r'<details\b.*?</details>',old,re.S)
  new='''<fieldset class="macro-details"><legend class="sr-only">Your details</legend>
<div class="field"><span class="field-heading" id="sex-label">Sex</span><div class="radio-row" role="radiogroup" aria-labelledby="sex-label"><label><input type="radio" name="sex" value="male" checked>Male</label><label><input type="radio" name="sex" value="female">Female</label></div></div>
<div class="field"><label class="field-heading" for="age">Age (years)</label><input type="number" id="age" name="age" min="18" max="100" value="30" required></div>
<div class="field"><div class="field-heading"><label for="weight">Weight <span class="sr-only" id="weight-unit-label">lb</span></label><div class="units-toggle" aria-label="Weight unit"><button type="button" class="active" data-weight-unit="lb">lb</button><button type="button" data-weight-unit="kg">kg</button></div></div><input type="number" id="weight" name="weight" min="1" step="0.1" value="170" required></div>
<div class="field"><div class="field-heading"><span>Height</span><div class="units-toggle height-units" aria-label="Height unit"><button type="button" class="active" data-height-unit="ftin">ft / in</button><button type="button" data-height-unit="cm">cm</button></div></div><div id="height-ftin-field" class="height-pair"><label><span class="sr-only">Feet</span><input type="number" id="height-ft" name="height_ft" min="3" max="8" value="5" required><span class="input-unit" aria-hidden="true">ft</span></label><label><span class="sr-only">Inches</span><input type="number" id="height-in" name="height_in" min="0" max="11" value="9"><span class="input-unit" aria-hidden="true">in</span></label></div><div id="height-cm-field" hidden><label><span class="sr-only">Height in centimeters</span><input type="number" id="height-cm" name="height_cm" min="120" max="230" value="175"></label></div></div>'''+activity+goal+'''</fieldset><div class="macro-explanations">'''+''.join(helps)+'''</div><div id="macro-error" class="error-msg" hidden></div><button type="submit" class="calc-submit">Calculate my macros</button><p class="clarity-hint publication-calculator-note">Adult estimates, not a prescription. <a href="sources.html">Formula and limitations</a>.</p>'''
  s=s[:form['inner']]+new+s[form['close']:]
  # Protein unit buttons belong to its weight label, not above every field.
  s=re.sub(r'(<form id="protein-calc-form"[^>]*>)\s*(<div class="units-toggle".*?</div>)\s*<div class="field">\s*(<label for="protein-weight">.*?</label>)',r'\1<div class="field"><div class="field-heading">\3\2</div>',s,flags=re.S)
  s=s.replace('Get protein target <span aria-hidden="true">&rarr;</span>','Calculate protein').replace('Get fat target <span aria-hidden="true">&rarr;</span>','Calculate fat').replace('Get carb target <span aria-hidden="true">&rarr;</span>','Calculate carbs')
  s=re.sub(r'<div class="results empty" id="macro-results">.*?</div>','<div class="results empty" id="macro-results" hidden></div>',s,flags=re.S)
 p.write_text(s,encoding='utf-8')

(ROOT/'docs/redesign/refinement').mkdir(exist_ok=True)
(ROOT/'docs/redesign/refinement/copy-changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2),encoding='utf-8')
print('Edited',len(changes),'specific copy/template occurrences')
