"""Complete, consistent working surfaces for the four additional calculators."""
from pathlib import Path
import re,json,html
from refine_colour_system import art
ROOT=Path(__file__).resolve().parents[1]

def number(id,label,value='',unit='',optional=False,min='0',max='100000',hint=''):
    accessible=f' aria-label="{label} ({unit})"' if unit else ''
    return f'<label class="focused-field" for="{id}"><span>{label}</span><span class="focused-input"><input id="{id}" name="{id}" type="number" inputmode="decimal" min="{min}" max="{max}" step="any" value="{value}"{accessible}{ "" if optional else " required"}><span aria-hidden="true">{unit}</span></span>{f"<small>{hint}</small>" if hint else ""}</label>'

def select(id,label,options):
    return f'<label class="focused-field" for="{id}"><span>{label}</span><select id="{id}" name="{id}">{options}</select></label>'

def food(prefix,n):
    return f'<fieldset class="focused-food"><legend><span>{n}</span> Food {n}</legend><label class="focused-field" for="{prefix}n"><span>Food name <small>(optional)</small></span><input id="{prefix}n" name="{prefix}n" maxlength="70" placeholder="Food {n}"></label>'+number(prefix+'m','Sodium per label serving',unit='mg')+number(prefix+'s','Servings you will eat','1',min='0.01',max='100',hint='Half a serving = 0.5')+'</fieldset>'

PAGES={
 'sodium-label-comparison-tool.html':dict(kind='sodium',title='Sodium calculator',intro='Compare the sodium in two foods, using the portions you actually eat.',heading='Compare two foods',fields='<div class="focused-pair">'+food('a',1)+food('b',2)+'</div>',button='Compare portions',form='tool',output='out',empty='Add the sodium and servings for both foods to compare your portions.',help_title='How to use the label',help='<p>Multiply sodium per serving by the number of servings you eat. A 300 mg serving becomes 450 mg when you eat 1.5 servings.</p><p>The 2,300 mg Daily Value is a general label reference, not a personal target. <a href="how-much-sodium-per-day.html">More about sodium.</a></p>',example={'am':'300','as':'1.5','an':'Soup A','bm':'250','bs':'2','bn':'Soup B'}),
 'carbohydrate-label-portion-tool.html':dict(kind='carbs',title='Carb calculator',intro='Find the carbs in your portion from the numbers on a food label.',heading='Your food label',fields='<div class="focused-pair">'+number('c','Total carbs per serving',unit='g')+number('s','Servings you will eat','1',min='0.01',max='100',hint='Half a serving = 0.5')+'</div><details class="focused-optional"><summary>Add fiber and sugar</summary><div class="focused-pair">'+number('f','Fiber per serving',unit='g',optional=True)+number('a','Added sugar per serving',unit='g',optional=True)+'</div><p>Optional. Leave these blank if your label does not list them.</p></details>',button='Calculate carbs',form='tool',output='out',empty='Enter total carbs and your portion size to see the grams you will eat.',help_title='Which number should I enter?',help='<p>Use “Total Carbohydrate” on the label. Fiber and sugars are already included, so do not add them again.</p><p>This is food-label math, not an insulin calculator. <a href="how-to-read-a-nutrition-label.html">How to read a food label.</a></p>',example={'c':'32','s':'1.5','f':'4','a':'6'}),
 'weight-goal-timeline-calculator.html':dict(kind='timeline',title='Weight goal timeline',intro='Choose a weekly pace to estimate the time between your current and goal weight.',heading='Your weight goal',fields=select('wg-unit','Weight unit','<option value="lb">Pounds (lb)</option><option value="kg">Kilograms (kg)</option>')+'<div class="focused-pair">'+number('wg-current','Current weight','200',unit='lb',min='1',max='1500')+number('wg-goal','Goal weight','175',unit='lb',min='1',max='1500')+'</div>'+select('wg-rate','Weekly change','<option value="0.25">0.25% of body weight</option><option value="0.5" selected>0.5% of body weight</option><option value="0.75">0.75% of body weight</option><option value="1">1% of body weight</option>')+'<p class="focused-hint">A pace for the calculation, not a recommended weight-loss or weight-gain rate.</p>',button='Show my timeline',form='wg-tool',output='wg-results',empty='Enter your weights and choose a weekly pace to see an estimated timeline.',help_title='What this estimate means',help='<p>The calculation changes your modeled weight by the chosen percentage each week. Real progress varies; this is not a predicted date or a personal calorie target.</p><p>This general adult estimate does not fit pregnancy, growth, illness or eating-disorder recovery. <a href="cutting-bulking-maintenance-explained.html">Understanding weight goals.</a></p>',example={'wg-unit':'lb','wg-current':'200','wg-goal':'175','wg-rate':'0.5'}),
 'sweat-rate-calculator.html':dict(kind='sweat',title='Sweat rate calculator',intro='Estimate how much fluid you lost during a workout.',heading='Your workout',fields='<div class="focused-pair">'+select('unit','Weight unit','<option value="kg">Kilograms (kg)</option><option value="lb">Pounds (lb)</option>')+number('time','Workout length','60',unit='min',min='15',max='600')+'</div><div class="focused-pair">'+number('before','Weight before',unit='kg',min='1',max='1500')+number('after','Weight after',unit='kg',min='1',max='1500')+'</div><p class="focused-hint">Use the same scale and dry, light clothing for both measurements.</p><div class="focused-pair">'+number('drink','Fluid you drank','0',unit='mL',max='10000')+number('urine','Urine during workout','0',unit='mL',max='5000',hint='Use 0 if none.')+'</div>',button='Calculate sweat rate',form='form',output='result',empty='Add your before-and-after weights and workout details to estimate fluid loss.',help_title='How the calculation works',help='<p>Weight lost in kilograms + drinks in liters − urine in liters = estimated sweat loss. Divide by workout hours to get liters per hour.</p><p>This measures one workout, not how much you should drink. Heat, clothing and exercise intensity affect the result. Avoid drinking enough to finish heavier than you started. <a href="sources.html">Methods and sources.</a></p>',example={'unit':'kg','time':'60','before':'70','after':'69.5','drink':'500','urine':'0'})
}

def run():
 for filename,c in PAGES.items():
    p=ROOT/filename;s=p.read_text(encoding='utf-8')
    # Preserve the existing worked examples, outside the actual calculator.
    example=re.search(r'<!-- practical-example:start -->.*?<!-- practical-example:end -->',s,re.S)
    example=example[0] if example else ''
    output=f'<aside class="tool-output" aria-label="Calculation results"><h2>Your results</h2><div class="focused-empty"><span aria-hidden="true">{art(c["kind"])}</span><p>{c["empty"]}</p></div><section id="{c["output"]}" class="focused-result" tabindex="-1" aria-live="polite" hidden></section></aside>'
    form=f'<form id="{c["form"]}" class="tool-inputs" data-focused-calculator="{c["kind"]}" data-example-values="{html.escape(json.dumps(c["example"]),quote=True)}"><h2>{c["heading"]}</h2>{c["fields"]}<p class="focused-error" role="alert" hidden></p><div class="focused-actions"><button type="submit">{c["button"]}</button><button type="reset">Reset</button></div><button type="button" class="focused-example" data-example>Try an example</button></form>'
    main=f'<main id="main-content"><div class="focused-shell"><a class="focused-back" href="calculators.html">All calculators</a><header class="focused-hero"><div><h1>{c["title"]}</h1><p>{c["intro"]}</p></div><div class="focused-art" aria-hidden="true">{art(c["kind"])}</div></header><div class="tool-workspace focused-workspace">{form}{output}</div><details class="focused-help"><summary>{c["help_title"]}</summary>{c["help"]}</details><noscript><p>Turn on JavaScript to use this calculator. The worked example below explains the math.</p></noscript></div>{example}</main>'
    s=re.sub(r'<main\b.*?</main>',lambda _:main,s,count=1,flags=re.S)
    def body_class(m):
      classes=[v for v in m[2].split() if not v.startswith('calculator-suite') and v not in ['clarity-tool','focused-tool']]
      return m[1]+'focused-tool '+' '.join(classes)+'"'
    s=re.sub(r'(<body[^>]*class=")([^"]*)"',body_class,s,count=1)
    # Remove only the obsolete per-page calculator handlers; keep theme, ads and schema.
    def script(m):
      t=m[0]
      return '' if ('src=' not in t and 'application/ld+json' not in t and any(key in t for key in ["getElementById('tool')",'getElementById("form")','var KCAL_PER_KG=7700'])) else t
    s=re.sub(r'<script\b[^>]*>.*?</script>',script,s,flags=re.S)
    s=re.sub(r'<script src="js/focused-calculators.js[^\"]*"[^>]*></script>','',s)
    s=s.replace('</body>','<script src="js/focused-calculators.js" defer></script></body>')
    s=re.sub(r'<title>.*?</title>',f'<title>{c["title"]} | GetMacros</title>',s,count=1)
    for key in ['og:title','twitter:title']:
      s=re.sub(r'(<meta (?:property|name)="'+key+r'" content=")[^"]*',lambda m:m[1]+c['title']+' | GetMacros',s)
    s=s.replace('at a safe rate, and the daily calorie deficit or surplus that pace actually requires.','at a selected weekly pace, with the assumptions shown.')
    p.write_text(s,encoding='utf-8')
 if __name__=='__main__':print('Rebuilt four focused calculator pages.')

if __name__=='__main__':run()
