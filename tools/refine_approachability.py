"""Keep the task, useful inputs and clear results ahead of explanatory copy."""
from pathlib import Path
import re, html
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
SYMBOLS={key:(viewbox,body) for key,viewbox,body in re.findall(r'<symbol id="([^"]+)" viewBox="([^"]+)">(.*?)</symbol>',(ROOT/'icon-sprite.svg').read_text(encoding='utf-8'),re.S)}
def icon(key):
    viewbox,body=SYMBOLS.get('icon-'+key,SYMBOLS['icon-calculator'])
    return '<span class="clear-icon"><svg aria-hidden="true" viewBox="'+viewbox+'">'+body+'</svg></span>'
def remove(s,cls):
    d=Document(s)
    nodes=[n for n in d.nodes if cls in n['attrs'].get('class','').split() and 'end' in n]
    for n in reversed(nodes):s=s[:n['start']]+s[n['end']:]
    return s
def main(s,body):return re.sub(r'<main\b.*?</main>','<main id="main-content">'+body+'</main>',s,flags=re.S)
TOOLS=[
 ('recipe-macro-scaler.html','Recipe portions','See calories and macros in each portion.','carbs'),
 ('nutrition-label-comparison-tool.html','Compare two foods','Put two nutrition labels side by side.','document'),
 ('protein-value-calculator.html','Protein for your money','Compare the cost of protein in two foods.','protein'),
 ('budget-meal-builder.html','Meals from your pantry','Get meal ideas using what you already have.','grain'),
 ('sodium-label-comparison-tool.html','Sodium in your portion','See sodium in the amount you eat.','water'),
 ('carbohydrate-label-portion-tool.html','Carbs in your portion','Adjust label carbs to the amount you eat.','carbs'),
 ('weight-goal-timeline-calculator.html','Weight-goal timeline','See how a weekly change affects your timeline.','target'),
 ('sweat-rate-calculator.html','Sweat loss','Estimate fluid lost during a workout.','water'),
 ('restaurant-meal-finder.html','Find a restaurant meal','Choose meals that fit your goals.','quiz'),
]
def directory():
    return '<section class="clear-tool-library" id="tool-library"><div class="container"><h2>What would you like to work out?</h2><div class="clear-tool-grid">'+''.join('<a class="clear-tool-card" href="'+url+'">'+icon(ic)+'<span><h3>'+title+'</h3><p>'+desc+'</p></span></a>' for url,title,desc,ic in TOOLS)+'</div><span id="food-tools"></span><span id="goal-tools"></span></div></section>'
def about():
    cards=[('quiz','Find a meal','Choose your goals and restaurants. Get a shortlist with the nutrition beside it.','restaurant-meal-finder.html','Find my meal'),('calculator','Work out your macros','Enter your details for a daily calorie, protein, fat and carb estimate.','calculators.html','Calculate my macros'),('document','Compare foods','Check two labels or see which food gives you more protein for your money.','nutrition-label-comparison-tool.html','Compare two foods')]
    return '<section class="clear-page-intro"><div class="container"><h1>About GetMacros</h1><p>Food choices are easier when the numbers make sense.</p><div class="clear-coverage"><span><strong>83</strong><small>tracked menu options</small></span><span><strong>15</strong><small>restaurants</small></span><span><strong>9</strong><small>free tools</small></span></div></div></section><section class="clear-about"><div class="container"><h2>How it works</h2><div class="clear-about-grid">'+''.join('<article>'+icon(i)+'<h3>'+h+'</h3><p>'+p+'</p><a class="btn action-link" href="'+u+'">'+b+'</a></article>' for i,h,p,u,b in cards)+'</div></div></section><section class="clear-about-source"><div class="container"><h2>Where the numbers come from</h2><p>Restaurant guides link to official menus. Calculators explain their methods, and nutrition articles link to their sources. If something looks wrong, tell me so I can check it.</p><div class="clear-actions"><a class="btn action-link" href="sources.html">View sources</a><a class="btn action-link" href="contact.html">Get in touch</a></div></div></section>'
def contact():
    return '<section class="clear-page-intro contact-refresh"><div class="container">'+icon('document')+'<h1>Contact GetMacros</h1><p>Questions, ideas or something not working? I’d love to hear from you.</p><a class="contact-email" href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a><p>I read and reply to every email.</p><div class="contact-choices"><a class="btn action-link" href="mailto:getmacros.net@outlook.com?subject=An%20idea%20for%20GetMacros">Suggest an improvement</a><a class="btn action-link" href="mailto:getmacros.net@outlook.com?subject=Something%20to%20fix%20on%20GetMacros">Report a problem</a></div><p class="contact-small">If something is wrong, include the page link and what happened.</p></div></section>'
def protein_foods(s):
    if 'data-protein-library' in s:return s
    tables=re.findall(r'<table class="data-table">.*?</table>',s,re.S)
    if len(tables)!=2:return s
    cards=[]
    for group,table in zip(['animal','plant'],tables):
        for row in re.findall(r'<tr>(.*?)</tr>',table,re.S):
            cols=re.findall(r'<(?:th|td)\b[^>]*>(.*?)</(?:th|td)>',row,re.S)
            if len(cols)!=6 or 'scope="row"' not in row:continue
            name=html.unescape(re.sub('<[^>]+>','',cols[0]))
            cards.append('<article class="protein-food-card" data-food-group="'+group+'" data-food-name="'+html.escape(name,quote=True)+'">'+icon('grain' if group=='plant' else 'protein')+'<h3>'+cols[0]+'</h3><p class="food-protein-number"><strong>'+cols[5]+'</strong> protein</p><p class="food-portion">'+cols[4]+'</p></article>')
    body='<section class="clear-page-intro"><div class="container"><h1>Find high-protein foods</h1><p>Pick foods for your meals. Each card shows protein in a typical portion.</p><a class="btn action-link" href="calculators.html#protein-calculator">Find my daily protein target</a></div></section><section class="protein-food-library" data-protein-library><div class="container"><div class="food-filter-controls" hidden><label for="protein-food-search">Search foods<input id="protein-food-search" type="search" placeholder="e.g. yogurt"></label><label for="protein-food-group">Show<select id="protein-food-group"><option value="">All foods</option><option value="animal">Meat, fish, eggs &amp; dairy</option><option value="plant">Plant-based foods</option></select></label></div><p class="food-count" role="status" aria-live="polite">25 foods</p><div class="protein-food-grid">'+''.join(cards)+'</div><p class="food-empty" hidden>No foods found. Try another search.</p><details class="food-reference"><summary>Compare equal weights and calories</summary><h2 id="animal-protein">Meat, fish, eggs &amp; dairy</h2><div class="table-scroll">'+tables[0]+'</div><h2 id="plant-protein">Plant-based foods</h2><div class="table-scroll">'+tables[1]+'</div></details><p class="food-reference-note">Values are approximate; brands and preparation vary. <a href="sources.html#protein-sources">See the sources.</a></p><div id="daily-protein"></div></div></section><script src="js/protein-foods.js" defer></script>'
    return main(s,body)

for path in ROOT.glob('*.html'):
    s=path.read_text(encoding='utf-8')
    for cls in ['focused-guide-kicker']:s=remove(s,cls)
    s=s.replace('By the GetMacros editorial team','By GetMacros')
    s=s.replace('<p>These short lists answer different questions. Every card keeps calories, protein, fiber and sodium together.</p>','')
    s=s.replace('These are standard U.S. menu builds from the central GetMacros dataset. Dashes mean the value was not available in a form we could verify—not zero.','U.S. menu items. A dash means the restaurant has not published a verified value.')
    s=s.replace('Protein per 100 calories = protein grams ÷ calories × 100. It is a transparent efficiency metric, not a health score.','Protein per 100 calories compares protein for the same calorie amount.')
    s=s.replace('Higher-energy meals for bulking','Higher-calorie meals for weight gain')
    s=s.replace('Healthy fast-food options by the metric you care about','Compare meals by your goal')
    s=s.replace('Only substantial tracked items with published sodium qualify. Missing sodium is never treated as zero.','Meals and entrées with published sodium values.')
    if 'data-chain-finder' in s:
        s=s.replace('type="radio" name="chain-goal"','type="checkbox" name="chain-goal"').replace('type="radio" name="chain-diet"','type="checkbox" name="chain-diet"')
        s=s.replace('<legend>What should this meal help with?</legend>','<legend>Your goals · choose any</legend>')
        s=re.sub(r'(<header class="chain-finder-intro"><h2>.*?</h2>).*?(</header>)',r'\1\2',s,flags=re.S)
    s=s.replace('<p>GetMacros uses primary research, position stands and official resources where possible. These sources support the guide; they do not make it individualized medical advice.</p>','')
    if path.name=='about.html':s=main(s,about())
    if path.name=='contact.html':s=main(s,contact())
    if path.name=='calculators.html':
        for cls in ['breadcrumb','calc-nav-wrap','calculator-scope','single-card-note','single-card-copy']:s=remove(s,cls)
        s=s.replace('<h2>Your details</h2>','').replace('Free macro calculator</h1>','Macro calculator</h1>')
        s=s.replace('<p class="hint">The calorie equation uses a different constant for each sex.</p>','')
        s=s.replace('<label for="weight">Weight (','<label class="sr-only" for="weight">Weight (')
        s=s.replace('<span class="field-label">Height in feet and inches</span>','')
        s=s.replace('<label for="height-cm">Height in centimeters</label>','<label class="sr-only" for="height-cm">Height in centimeters</label>')
        s=s.replace('<p>Estimate calories, protein, carbs and fat for your goal.</p>','')
        s=s.replace('Protein, fat and carb calculators','Just one macro?').replace('Carbohydrate target','Carb target')
        s=s.replace('Your daily protein range will appear here.','').replace('Your daily fat range will appear here.','').replace('Your daily carb range will appear here.','')
        s=s.replace('What should the range support?','Goal')
        s=s.replace('<p class="calculator-safety-note">These are educational estimates for generally healthy adults, not individualized medical advice. See the <a href="sources.html">methods and sources</a>.</p>','<p class="calculator-safety-note"><a href="sources.html">How these estimates are calculated</a></p>')
        d=Document(s)
        node=next((n for n in d.nodes if 'tool-library' in n['attrs'].get('class','').split() and n['tag']=='section'),None)
        if node:s=s[:node['start']]+directory()+s[node['end']:]
    if path.name=='high-protein-foods-list.html':s=protein_foods(s)
    if path.name in {x[0] for x in TOOLS[:8]}:
        # Long generated appendices repeat the working tool and the linked guides.
        s=remove(s,'expanded');s=remove(s,'reading-map')
        d=Document(s);edits=[]
        for n in d.nodes:
            if n['tag']!='section' or 'end' not in n:continue
            block=s[n['start']:n['end']]
            if any(t in block for t in ['Price is not nutritional quality','Read the result in context','Use total carbohydrate first','<h2>The equation</h2>','How to interpret the result']):
                if '<form' not in block and '<input' not in block:edits.append((n['start'],n['end']))
        for a,b in sorted(edits,reverse=True):s=s[:a]+s[b:]
        # Keep methods accessible without putting an essay ahead of the inputs.
        s=remove(s,'breadcrumb')
        if path.name=='protein-value-calculator.html':
            s=s.replace('Protein cost per gram calculator</h1>','Compare protein costs</h1>')
            s=s.replace('A low package price is not always a low price per usable serving. Compare foods on one transparent metric, then consider the rest of the meal.','Which food gives you more protein for your money? Compare two packages below.')
            s=s.replace('Enter package price, servings per package, and protein per serving for two foods. The calculator shows cost per gram of protein and the equivalent cost per 25 grams.','Enter prices in US dollars. Results update as you type.')
            s=s.replace('Enter prices in the same currency. Results update as you type.','Enter prices in US dollars. Results update as you type.')
            s=re.sub(r'<h2[^>]*>Compare protein cost</h2>','',s,count=1)
            s=re.sub(r'<div class="editorial-note" style="margin-top:2rem"><h2[^>]*>Price is not nutritional quality</h2>.*?</div>','<details class="simple-tool-help"><summary>What does the price mean?</summary><p>The results show the cost of 1 gram and 25 grams of protein. They compare price, not overall food quality. <a href="how-to-hit-protein-goal-on-budget.html">More ways to save on protein.</a></p></details>',s,count=1,flags=re.S)
        if path.name=='carbohydrate-label-portion-tool.html':
            s=s.replace('Use the Nutrition Facts panel to calculate total carbohydrate in the portion you expect to eat. Entries stay in your browser.','Enter the carbs on a food label and how many servings you eat.')
            s=re.sub(r'<h2>Use total carbohydrate first</h2>.*?(?=</section>)','<details class="simple-tool-help"><summary>Which number is total carbs?</summary><p>Use “Total Carbohydrate” on the label. It already includes fiber and sugars; do not add them again. <a href="how-to-read-a-nutrition-label.html">How to read a food label.</a></p></details>',s,count=1,flags=re.S)
        if path.name=='budget-meal-builder.html':
            s=s.replace('Budget meal builder</h1>','What can I make with these ingredients?</h1>')
            s=s.replace('Select available ingredients. The builder suggests flexible combinations and identifies the smallest useful gap instead of generating a long new shopping list.','Choose what you have at home. Get simple meal ideas and see what else you might need.')
            s=s.replace('Your available ingredients','What do you have?').replace('Protein or hearty base','Protein foods').replace('Grain or starchy base','Grains &amp; potatoes').replace('Flavor or energy','Sauces &amp; extras')
            s=s.replace('<p>No selections or personal data leave this page.</p>','')
            s=remove(s,'all-ideas-section')
        if path.name=='weight-goal-timeline-calculator.html':
            s=s.replace('How long will it take to reach my goal weight?</h1>','Weight-goal timeline</h1>')
            s=s.replace('Enter where you are now and where you want to be. You will get a realistic date range, the daily calorie change it implies, and what to do when progress slows.','See when you would reach your goal at a chosen weekly pace. Actual progress can vary.')
            s=re.sub(r'<section class="tight"><div class="container">\s*<h2>Frequently asked questions</h2>.*?</section>','',s,count=1,flags=re.S)
            s=re.sub(r'<script type="application/ld\+json">(?:(?!</script>).)*?"@type"\s*:\s*"FAQPage".*?</script>','',s,flags=re.S)
            s=re.sub(r'<p class="calc-fineprint">(.*?)</p>',r'<details class="simple-tool-help"><summary>About this estimate</summary><p>\1</p></details>',s,count=1,flags=re.S)
        if path.name=='sodium-label-comparison-tool.html':
            s=s.replace('Enter sodium per labeled serving and the number of servings you expect to eat. The tool compares actual portions and uses the FDA’s 2,300 mg Daily Value only as a general label reference.','Compare the sodium in the portions you eat. Enter the numbers from two food labels.')
            s=re.sub(r'<h2>Read the result in context</h2>.*?(?=</section>)','<details class="simple-tool-help"><summary>About the daily value</summary><p>The 2,300 mg Daily Value is a general label reference, not a personal target. <a href="how-much-sodium-per-day.html">More about sodium.</a></p></details>',s,count=1,flags=re.S)
            s=re.sub(r'<aside class="callout"><strong>Not a personal target:</strong>.*?</aside>','',s,count=1,flags=re.S)
        if path.name=='sweat-rate-calculator.html':
            s=s.replace('Use measurements from one representative training session to estimate hourly fluid loss. Repeat under different conditions to build a useful range.','Enter your weight before and after a workout, plus anything you drank, to estimate sweat loss.')
            s=s.replace('Body-mass unit','Weight unit').replace('Body mass before','Weight before exercise').replace('Body mass after','Weight after exercise').replace('Fluid consumed (mL)','Amount you drank (mL)')
            s=s.replace('<strong>Before measuring:</strong> Use the same scale, minimal dry clothing, and a session long enough to observe meaningful change. Towel off and remove wet clothing before the final weigh-in.','Use the same scale before and after exercise. Weigh yourself in dry, light clothing.')
            s=re.sub(r'<h2>The equation</h2>.*?(?=</div></section>)','<details class="simple-tool-help"><summary>How this estimate works</summary><p>Weight lost in kilograms + drinks in litres − urine in litres, divided by hours of exercise. One litre of water weighs about one kilogram.</p><p>This measures one workout; heat, clothing and intensity change your sweat loss. It is not a target to replace every drop during exercise. Avoid drinking enough to finish heavier than you started.</p><p><a href="sources.html">Methods and sources</a></p></details>',s,count=1,flags=re.S)
    # Stable, compact names in navigation and action links; retain descriptive SEO titles.
    descriptions={
        'protein-value-calculator.html':'Compare the cost of protein in two foods. Enter package prices and label values to see the price per gram and per 25 grams of protein.',
        'budget-meal-builder.html':'Find meal ideas using ingredients you already have. Choose pantry foods, see simple combinations and find out what else you might need.',
        'sodium-label-comparison-tool.html':'Compare sodium in two food portions. Enter sodium per serving and the amount you eat to see milligrams and the general Daily Value.',
        'carbohydrate-label-portion-tool.html':'Calculate carbs in the portion you eat using a food label. See total carbohydrate, fiber and added sugar for your chosen number of servings.',
        'sweat-rate-calculator.html':'Estimate sweat loss during exercise from your weight before and after a workout, time spent exercising and how much you drank.',
        'weight-goal-timeline-calculator.html':'Estimate a weight-goal timeline from your current weight, goal weight and chosen weekly pace. See dates and milestones with the calculation assumptions.',
    }
    if path.name in descriptions:
        for attr,key in [('name','description'),('property','og:description'),('name','twitter:description')]:
            s=re.sub(r'(<meta '+attr+'="'+key+'" content=")[^"]*(")',lambda m:m[1]+html.escape(descriptions[path.name],quote=True)+m[2],s)
    s=s.replace('>Recipe portions </a>','>Recipe portions</a>')
    if '<link rel="preload" href="fonts/manrope-latin-700.woff2"' not in s:s=s.replace('</head>','<link rel="preload" href="fonts/manrope-latin-700.woff2" as="font" type="font/woff2" crossorigin></head>')
    s=re.sub(r'<link rel="stylesheet" href="css/site-refresh.css(?:\?[^"]*)?">','',s)
    s=s.replace('</head>','<link rel="stylesheet" href="css/site-refresh.css"></head>')
    s=re.sub(r'<script src="js/page-experience.js(?:\?[^"]*)?" defer></script>','',s)
    s=s.replace('</body>','<script src="js/page-experience.js" defer></script></body>')
    s=re.sub(r'(?m)[ \t]+$','',s)
    s=s.replace('</main></main>','</main>')
    path.write_text(s,encoding='utf-8')
print('Simplified About, tools, calculator, protein foods and contact.')
