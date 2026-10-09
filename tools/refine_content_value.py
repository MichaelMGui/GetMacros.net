"""Idempotent editorial corrections; do not change nutrition or legal records."""
from pathlib import Path
import re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]

SECTIONS=[
('What are you trying to measure?', '''<p>Body recomposition means gaining muscle while losing fat. This guide is about judging progress without treating every scale change as a result. For the research on whether muscle gain can happen during weight loss, read <a href="can-you-build-muscle-in-a-calorie-deficit.html">muscle growth in a calorie deficit</a>.</p><p>Separate the goal from the evidence. A change in body weight measures total mass, not muscle and fat separately. A stronger lift records performance, not a direct muscle measurement. Looking at more than one measure helps you avoid drawing a big conclusion from a small change.</p>'''),
('Keep a small, repeatable record', '''<p>Choose measurements you can repeat comfortably. You do not need to collect every possible number.</p><ul><li><strong>Training:</strong> note the exercise, load and repetitions. Comparing the same movement with similar technique is more useful than comparing unrelated workouts.</li><li><strong>Waist or clothing fit:</strong> use the same measurement position or the same garment. Write down the method so you can repeat it.</li><li><strong>Weight, if useful to you:</strong> look at a trend across comparable measurements rather than reacting to one morning.</li><li><strong>Recovery:</strong> note whether you can complete your usual training and whether the routine fits your daily life.</li></ul><p>Photos are optional. Home body-fat scales are estimates; do not treat a small change in their muscle reading as a confirmed gain.</p>'''),
('How to read mixed signals', '''<p>These are interpretation examples, not results from a GetMacros experiment or a prediction of your progress.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Examples of progress signals"><table><thead><tr><th scope="col">What you notice</th><th scope="col">What it tells you</th><th scope="col">What it does not prove</th></tr></thead><tbody><tr><th scope="row">Similar weight, smaller waist, stronger lifts</th><td>Several measures are moving in a direction consistent with your goal.</td><td>The exact amount of muscle gained or fat lost.</td></tr><tr><th scope="row">Lower weight, worse training and recovery</th><td>The scale is down, but the routine may need reviewing.</td><td>That every pound lost is fat, or that eating less again will help.</td></tr><tr><th scope="row">Higher weight after one meal or workout</th><td>One measurement changed.</td><td>That your longer-term plan has stopped working.</td></tr></tbody></table></div><p>Strength can improve through practice as well as muscle growth. Measurements can also vary with technique. Repeat the observation before changing the plan; <a href="why-did-i-gain-weight-overnight.html">overnight weight changes</a> are a different question from long-term body composition.</p>'''),
('Use calorie estimates as a starting point', '''<p>The macro calculator’s recomposition option uses a smaller deficit. It cannot predict whether you will gain muscle at that intake. Keep the focus on a suitable resistance-training program, enough protein, enough food and recovery rather than trying to make every daily measurement match the calculator.</p><p>If you change your intake, write down what changed and why. Changing food, training and measurement methods all at once makes the next result harder to interpret. The <a href="when-to-recalculate-calories-and-macros.html">recalculation guide</a> explains when an estimate needs another look.</p>'''),
('Decide whether the goal still fits', '''<p>Recomposition is gradual and uncertain. You do not have to pursue muscle gain and fat loss at the same time. If your priority changes, a clearer single goal may be easier to plan and assess.</p><p>Review whether you can sustain the routine and recover from training. Persistent fatigue, poor recovery or health concerns deserve individual help, rather than increasingly strict targets from a website. GetMacros offers educational estimates; it does not measure body composition or diagnose the cause of a change.</p>'''),
]

def finder_methodology():
 p=ROOT/'sources.html';t=p.read_text(encoding='utf-8')
 old='The meal finder ranks the menu options in our dataset against your chosen preferences. It does not search every item a restaurant sells. Unconfirmed values stay unknown; the finder excludes incomplete records by default and lets you include them explicitly.'
 new='The meal finder searches our tracked selection, not every item a restaurant sells. Calorie and nutrient limits exclude orders that do not meet them. Priorities change the order of the remaining results; they are not a personal health score.</p><p>Complete macros means known calories, protein, carbs and fat. Fiber and sodium are checked separately when you filter them. You can explicitly include items with missing macros, but any active nutrient limit still requires that nutrient to be known. Unknown values are never treated as zero.</p><p>Choose the country where you are ordering. Canadian and U.S. records have separate portions and official sources. Open an order’s details for its serving and source history; a comparison’s writing date does not mean its restaurant values were rechecked that day.'
 t=t.replace(old,new)
 t=re.sub(r'<p>The meal finder searches the orders in our dataset,.*?</p><p>By default, a result needs.*?</p><p>The restaurant comparisons are calculations.*?</p>',lambda m:'<p>'+new+'</p>',t,flags=re.S)
 p.write_text(t,encoding='utf-8')

def run():
 removed=0
 for p in ROOT.glob('*.html'):
  t=p.read_text(encoding='utf-8')
  if 'class="reading-contents"' in t:
   t,n=re.subn(r'<!-- reading-map:start -->.*?<!-- reading-map:end -->','',t,flags=re.S);removed+=n
  p.write_text(t,encoding='utf-8')
 p=ROOT/'body-recomposition-explained.html';t=p.read_text(encoding='utf-8')
 for i,(heading,body) in enumerate(SECTIONS,1):
  doc=Document(t);h=next(n for n in doc.nodes if n['attrs'].get('id')==f'guide-section-{i}');section=h['parent']
  assert section['tag']=='section'
  t=t[:section['start']]+f'<section class="reading-section"><h2 id="guide-section-{i}">{heading}</h2>{body}</section>'+t[section['end']:]
  t=re.sub(r'(<a href="#guide-section-'+str(i)+r'">).*?(</a>)',lambda m:m[1]+heading+m[2],t)
 t=re.sub(r'<h1>.*?</h1>','<h1>Body recomposition: how to track progress</h1>',t,count=1,flags=re.S)
 title='Body Recomposition: How to Track Progress | GetMacros'
 description='Track body recomposition with consistent measurements, training notes and realistic expectations. Learn what changes in weight, waist and strength can tell you.'
 t=re.sub(r'<title>.*?</title>','<title>'+title+'</title>',t,count=1,flags=re.S)
 for key,value in [('description',description),('og:description',description),('twitter:description',description),('og:title',title),('twitter:title',title)]:
  t=re.sub(r'(<meta (?:name|property)="'+key+r'" content=")[^"]*',lambda m:m[1]+value,t)
 t=t.replace('Body recomposition means losing body fat while gaining muscle. It can happen, but progress is gradual and the scale may not show the full change.','Use training notes, measurements and weight trends together. No single number can tell you how much muscle you gained.')
 t=t.replace('Updated September 9, 2026','Updated September 28, 2026')
 t=re.sub(r'("dateModified"\s*:\s*")[^"]+',r'\g<1>2026-09-28',t)
 p.write_text(t,encoding='utf-8')
 finder_methodology()
 print(f'Removed {removed} duplicated article contents blocks; distinguished recomposition guide; clarified finder methodology.')

if __name__=='__main__':run()
