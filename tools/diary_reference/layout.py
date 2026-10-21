"""Reference-led diary composition. No invented user, intake or target values."""
import re
from normalize_calculator_layouts import Document

def apply(text,find,replace):
    if 'data-reference-diary' in text:return text
    root=find(text,'diary-app');header=find(text,'diary-header');overview=find(text,'diary-overview');utilities=find(text,'diary-utilities')
    if not all([root,header,overview,utilities]):raise ValueError('Expected the current shared diary')
    old=text[overview['start']:overview['end']];buddy=find(old,'food-companion');summary=find(old,'diary-summary')
    if not buddy or not summary:raise ValueError('Diary summary or character missing')
    companion=old[buddy['start']:buddy['end']]
    totals=old[summary['start']:summary['end']].replace(' hidden aria-label="Logged nutrition"',' aria-label="Logged nutrition"')
    new='<section class="diary-overview" aria-label="Daily overview"><header class="diary-overview-header"><h2>Your day</h2><button class="text-action" type="button" data-edit-goals>Set daily goals</button></header><p class="diary-empty-message" data-diary-empty-day hidden></p>'+totals+'</section>'
    text=replace(text,overview,new)
    header=find(text,'diary-header');part=text[header['start']:header['end']]
    button=next(n for n in Document(part).nodes if 'data-diary-add' in n['attrs'])
    action=part[button['start']:button['end']]
    part=replace(part,button,'<div class="diary-header-companion">'+companion+'</div>')
    text=replace(text,header,part)
    main=find(text,'diary-main');text=text[:main['start']]+'<div class="diary-add-row">'+action+'</div>'+text[main['start']:]
    text=text.replace('botanical-diary"','botanical-diary reference-diary" data-reference-diary',1)
    dialog='<dialog id="diary-goals" class="food-picker diary-goals" aria-labelledby="diary-goals-title"><header class="food-review-header"><h2 id="diary-goals-title">Your daily goals</h2><button class="dialog-close" type="button" data-goals-close aria-label="Close daily goals">Close</button></header><p>Optional targets you choose. Leave any field blank to track without a goal.</p><form method="dialog"><div class="diary-goal-fields">'
    for key,label,unit,maximum in [('cal','Calories','kcal',50000),('p','Protein','g',10000),('c','Carbs','g',10000),('fat','Fat','g',10000)]:
        dialog+='<label>'+label+' <span>'+unit+'</span><input type="number" name="'+key+'" min="0.1" max="'+str(maximum)+'" step="any" inputmode="decimal" autocomplete="off"></label>'
    dialog+='</div><p class="diary-goal-storage">Your current goals apply to the date you view. They stay on this device and are included in diary backups.</p><p data-goals-status role="alert"></p><div class="food-actions"><button class="btn btn-primary" type="submit">Save goals</button><button type="button" data-goals-clear>Remove goals</button></div></form></dialog>'
    root=find(text,'diary-app');text=text[:root['close']]+dialog+text[root['close']:]
    mobile=find(text,'mobile-task-nav')
    if mobile:
        part=text[mobile['start']:mobile['end']]
        part=part.replace('class="mobile-task-nav"','class="mobile-task-nav diary-task-nav"')
        links=[n for n in Document(part).nodes if n['tag']=='a'];third=links[2]
        button='<button class="diary-dock-add" type="button" data-diary-quick-add aria-label="Add food"><span aria-hidden="true">+</span><small>Add food</small></button>'
        part=part[:third['start']]+button+part[third['start']:]
        text=replace(text,mobile,part)
    if 'js/diary-dashboard.js' not in text:
        pattern=r'(?=<script\b[^>]*(?:data-source-path="js/food-app.js"|src="/?js/food-app.js")[^>]*>)'
        text,count=re.subn(pattern,'<script src="/js/diary-dashboard.js" defer></script>',text,count=1)
        if count!=1:raise ValueError('Food app script order not found')
    return text

def privacy(text):
    text=text.replace('source-value snapshots, recipes and optional private notes in this browser’s IndexedDB.','source-value snapshots, recipes, optional daily goals and private notes in this browser’s IndexedDB.')
    text=text.replace('Export files include your notes and should only be shared deliberately.','Export files include your notes and any daily goals you set, and should only be shared deliberately.')
    text=text.replace('Food diary inputs, descriptions, photos and notes are not included in product-event or advertising data.','Food diary inputs, daily goals, descriptions, photos and notes are not included in product-event or advertising data.')
    text=text.replace('This section updated October 12, 2026.','This section updated October 20, 2026.')
    return text
