"""Synchronize current restaurant presentation without rebuilding its template.

Reads central meals/provenance, replaces only data tables, included-order notes,
source-date explanations and numeric metadata. Never alters header/footer/theme,
source facts or unrelated article writing. Safe to run repeatedly.
"""
from pathlib import Path
import json, re, html
from collections import defaultdict
from build_meal_finder import parse_meals
from normalize_calculator_layouts import Document
from strengthen_meal_comparisons import CHOICES

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-03'
def esc(v):return html.escape(str(v),quote=True)
def n(v):return '—' if v is None else f'{v:,g}'
def ancestors(node):
    while node:
        yield node
        node=node['parent']
def inside(node,parent):return any(n is parent for n in ancestors(node))

def validate_menu(text,entries,provenance,efficiency=True):
    """Check rendered rows against source data without replacing composition."""
    finished=Document(text)
    menu=finished.find(id='menu-comparison')
    assert menu is not None,'Missing menu comparison section'
    table=next(node for node in finished.nodes if node['tag']=='table' and inside(node,menu))
    data_rows=[node for node in finished.nodes if node['tag']=='tr' and inside(node,table) and any(a['tag']=='tbody' for a in ancestors(node))]
    assert len(data_rows)==len(entries),(len(data_rows),len(entries))
    for row,meal in zip(data_rows,entries):
        name=next(node for node in finished.nodes if node['tag']=='strong' and inside(node,row))
        actual_name=html.unescape(re.sub('<[^>]*>','',text[name['inner']:name['close']]))
        assert actual_name==meal['name'],(meal['name'],actual_name)
        cells=[node for node in finished.nodes if node['tag']=='td' and node['parent'] is row]
        source=provenance[meal['chain']+'||'+meal['name']]
        expected=[n(meal.get(k)) for k in ('cal','p','c')]+[n(source.get('fat'))]+[n(meal.get(k)) for k in ('f','na')]
        if efficiency:expected.append('—' if not meal.get('cal') or meal.get('p') is None else f'{meal["p"]/meal["cal"]*100:.1f}')
        actual=[html.unescape(re.sub('<[^>]*>','',text[cell['inner']:cell['close']])) for cell in cells]
        assert expected==actual,(meal['name'],expected,actual)
    assert text.count('<table')==text.count('</table>'),'Unbalanced tables'
    return finished,table

def validate_expansion_comparison(text,entries,provenance,doc,menu):
    """New guides choose their own actual rows; no legacy CHOICES assumptions."""
    names=[]
    known={m['name']:m for m in entries}
    for table in (node for node in doc.nodes if node['tag']=='table' and not inside(node,menu)):
        rows=[node for node in doc.nodes if node['tag']=='tr' and inside(node,table) and any(a['tag']=='tbody' for a in ancestors(node))]
        for row in rows:
            strong=next(node for node in doc.nodes if node['tag']=='strong' and inside(node,row))
            name=html.unescape(re.sub('<[^>]*>','',text[strong['inner']:strong['close']]))
            assert name in known,('Unknown comparison row',name)
            meal=known[name];source=provenance[meal['chain']+'||'+name]
            cells=[node for node in doc.nodes if node['tag']=='td' and node['parent'] is row]
            actual=[html.unescape(re.sub('<[^>]*>','',text[cell['inner']:cell['close']])) for cell in cells]
            expected=[n(meal.get(k)) for k in ('cal','p','c')]+[n(source.get('fat'))]+[n(meal.get(k)) for k in ('f','na')]
            assert expected==actual,(name,expected,actual)
            names.append(name)
    return names

def rows_table(meals,provenance,compact=False):
    keys=('cal','p','f','na') if compact else ('cal','p','c','fat','f','na')
    labels={'cal':'Calories','p':'Protein (g)','c':'Carbs (g)','fat':'Fat (g)','f':'Fiber (g)','na':'Sodium (mg)'}
    rows=''
    for meal in meals:
        source=provenance[meal['chain']+'||'+meal['name']]
        cell='<strong>'+esc(meal['name'])+'</strong>'
        cell+='<details><summary>Portion and source</summary><p>'+esc(source.get('serving','1 listed order'))+'</p>'
        if source.get('nutrientProvenance'):
            dates=defaultdict(list)
            for nutrient,record in source['nutrientProvenance'].items():
                if record.get('retrieved'):dates[record['retrieved']].append(labels.get(nutrient,nutrient).split(' (')[0].lower())
            for date,nutrients in sorted(dates.items()): cell+='<p>'+esc(', '.join(nutrients).capitalize()+' inspected '+date+'.')+'</p>'
        else:cell+='<p>Recorded check date: '+esc(source.get('checked','not recorded'))+'.</p>'
        if source.get('sourceDate'):cell+='<p>Source edition/date: '+esc(source['sourceDate'])+'.</p>'
        if source.get('notes'):cell+='<p>'+esc(source['notes'])+'</p>'
        urls=list(dict.fromkeys([source['source']]+[r['source'] for r in source.get('nutrientProvenance',{}).values() if r.get('source')]))
        cell+=''.join('<p><a href="'+esc(url)+'">'+('Ingredient nutrition source' if len(urls)>1 and index==0 else 'Published menu source' if len(urls)>1 else 'Linked nutrition source')+'</a></p>' for index,url in enumerate(urls))+'</details>'
        rows+='<tr><th scope="row">'+cell+'</th>'
        rows+=''.join('<td>'+n(source.get('fat') if key=='fat' else meal.get(key))+'</td>' for key in keys)
        if not compact:rows+='<td>'+('—' if not meal.get('cal') or meal.get('p') is None else f'{meal["p"]/meal["cal"]*100:.1f}')+'</td>'
        rows+='</tr>'
    head='<th scope="col">Order and portion</th>'+''.join('<th scope="col">'+labels[k]+'</th>' for k in keys)
    if not compact:head+='<th scope="col">Protein per 100 calories (g)</th>'
    columns='<colgroup><col class="restaurant-order-column order-column">'+('<col class="restaurant-nutrient-column nutrient-column">'*(len(keys)+(0 if compact else 1)))+'</colgroup>'
    return '<table class="comparison-table restaurant-comparison-table'+(' restaurant-comparison-table-compact' if compact else '')+'">'+columns+'<thead><tr>'+head+'</tr></thead><tbody>'+rows+'</tbody></table>'

SOURCE_NOTES={
 'Chipotle':'Ingredient values use the October 2024 printed U.S. table, inspected October 3, 2026. Published High Protein Menu calories, protein and fiber come from the December 18, 2025 announcement; other nutrients are ingredient sums. The light-rice amount is an explicit calculation assumption, not a measured scoop.',
 'Sweetgreen':'The linked published recipe totals and gram portions were inspected October 3, 2026. A source publication date was not established. Standard dressing is included in the named recipes.',
 'Panera':'The inspected U.S. guide is effective September 2, 2026; the five listed portions were inspected October 3, 2026. Half, whole, cup and bowl portions remain distinct, and extra bread or sides are excluded.',
 'CAVA':'The accessible official April-2025-named nutrition document was inspected October 3, 2026. Its printed publication date and current live menu linkage could not be established. The values describe its named recipes, not every customized bowl.',
 'Popeyes':'The linked U.S. PDF is labeled September 2026 and was inspected October 3, 2026. The three-tender-plus-side record is an explicit sum of the published three-tender and regular-side portions; biscuits, drinks and extra sauce are excluded.',
 'Panda Express':'The official table was inspected October 3, 2026. The Super Greens base is 10 oz, distinct from the separate 3.5 oz entree entry. Combinations sum full named entree and base portions; no half-side weight or extra sauce is assumed.',
 'Starbucks':'Three food records were inspected October 3, 2026 in indexed text from their official nutrition pages; direct page retrieval returned a script shell. Other records retain their previous check dates. A drink or added spread is not included in a food-only total.',
 'Chick-fil-A':'Selected dedicated item pages were inspected October 3, 2026. The twelve-count nuggets page exposed calories, protein, carbs and fat only; its retained fiber/sodium were not newly verified. Two large combinations and other records retain earlier check dates. The Cool Wrap figure includes suggested Avocado Lime Ranch dressing.',
}

def run():
    meals=parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))
    provenance=__import__('meal_provenance').read(ROOT/'js/meal-provenance.js')
    chains=defaultdict(list)
    for meal in meals:chains[meal['chain']].append(meal)
    payload_path=ROOT/'tools/restaurant_release/expansion-payload.json'
    expanded_chains={c['chain'] for c in json.loads(payload_path.read_text(encoding='utf-8'))['chains']} if payload_path.exists() else set()
    report=[]
    for chain,entries in chains.items():
        path=ROOT/entries[0]['url']; text=path.read_text(encoding='utf-8');doc=Document(text)
        menu=doc.find(id='menu-comparison')
        tables=[node for node in doc.nodes if node['tag']=='table']
        if chain in expanded_chains:
            # The new guides already contain source-specific portions, notes and
            # independently chosen comparison rows. Validate all values; preserve
            # the authored composition rather than fitting it into the old pair.
            validate_menu(text,entries,provenance,efficiency=False)
            pair_names=validate_expansion_comparison(text,entries,provenance,doc,menu)
            report.append({'route':path.name,'chain':chain,'records':len(entries),'comparisonRecords':pair_names,
                'tableValues':'central meals and provenance, including known fat',
                'sourceNarrativeUpdated':False,'sourceCheckDates':sorted({provenance[chain+'||'+m['name']].get('checked') for m in entries if provenance[chain+'||'+m['name']].get('checked')}),
                'template':'new source-specific composition preserved','visualInspection':'not performed by this synchronization tool'})
            continue
        comparison=doc.find(id='ordering-comparison')
        menu_table=next(node for node in tables if inside(node,menu))
        comparison_table=next(node for node in tables if inside(node,comparison))
        choice=CHOICES[chain]
        pair=[next(m for m in entries if m['name']==name) for name in choice[1:3]]
        edits=[(menu_table['start'],menu_table['end'],rows_table(entries,provenance)),
               (comparison_table['start'],comparison_table['end'],rows_table(pair,provenance,True))]
        heading=next((node for node in doc.nodes if node['tag']=='h2' and inside(node,comparison)),None)
        if heading is None:
            # The final presentation pass turns this optional explanation into
            # an accordion. Preserve its summary instead of assuming a heading
            # still exists or removing the working disclosure control.
            heading=next(node for node in doc.nodes if node['tag']=='summary' and inside(node,comparison) and not inside(node,comparison_table))
        explanation=next(node for node in doc.nodes if node['tag']=='p' and node['start']>=heading['end'] and inside(node,comparison))
        edits.extend([(heading['start'],heading['end'],'<'+heading['tag']+'>'+esc(choice[0])+'</'+heading['tag']+'>'),
                      (explanation['start'],explanation['end'],'<p>'+esc(choice[3])+'</p>')])
        # Contiguous tags can share end/start offsets; an earlier strict > check
        # selected the following disclaimer instead of the first explanation.
        # Repair that duplication and make repeated synchronizations stable.
        for node in doc.nodes:
            if node['tag']=='p' and node is not explanation and node['parent'] is explanation['parent'] and node['start']<comparison_table['start']:
                raw=html.unescape(re.sub('<[^>]*>','',text[node['inner']:node.get('close',node['end'])]))
                if raw==choice[3]:edits.append((node['start'],node['end'],'<p>Recorded U.S. portions; extra items excluded. A dash means unverified.</p>'))
        before_order=next(node for node in doc.nodes if node['tag']=='h3' and inside(node,comparison) and 'Before you order' in text[node['inner']:node.get('close',node['end'])])
        check=next(node for node in doc.nodes if node['tag']=='p' and node['start']>=before_order['end'] and inside(node,comparison))
        edits.append((check['start'],check['end'],'<p>'+esc(choice[4])+'</p>'))
        detail=next(node for node in doc.nodes if node['tag']=='details' and inside(node,comparison) and not inside(node,comparison_table))
        included=next(node for node in doc.nodes if node['tag']=='ul' and inside(node,detail))
        items='<ul>'
        for meal in pair:
            source=provenance[chain+'||'+meal['name']]
            items+='<li><strong>'+esc(meal['name'])+'</strong><p>'+esc(meal['why'])+'</p><p>'+esc(source.get('serving','1 listed order'))+'</p><a href="'+esc(source['source'])+'">Linked nutrition source</a></li>'
        items+='</ul>'
        edits.append((included['start'],included['end'],items))
        if chain in SOURCE_NOTES:
            old=next((node for node in doc.nodes if node['tag']=='p' and inside(node,detail) and 'Comparison written' in text[node['inner']:node.get('close',node['end'])]),None)
            if old:edits.append((old['start'],old['end'],'<p>Comparison first written September 28, 2026. Selected source values were inspected October 3, 2026; individual nutrient check dates and source editions are recorded above.</p>'))
            box=doc.find(cls='source-box')
            source_p=next(node for node in doc.nodes if node['tag']=='p' and node['parent'] is box)
            edits.append((source_p['start'],source_p['end'],'<p>'+esc(SOURCE_NOTES[chain])+'</p>'))
        for start,end,new in sorted(edits,reverse=True):text=text[:start]+new+text[end:]
        # Only a changed Panda table invalidated the previous summary numbers.
        # Other distinct descriptions are preserved instead of mass rewriting.
        if chain=='Panda Express':
            description='Compare 7 tracked Panda Express portions, including teriyaki chicken at 280 calories and 38 g protein. Full bases and extra sauce stay distinct.'
            text=re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*(")',lambda m:m[1]+esc(description)+m[2],text)
            def schema_refresh(match):
                obj=json.loads(match[1])
                if obj.get('@type')=='WebPage':obj['description']=description;obj['dateModified']=DATE
                return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
            text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',schema_refresh,text,flags=re.S)
        if chain=='Chipotle':
            text=text.replace('For the two current High Protein Menu items,','For the two named High Protein Menu items,')
        # Actual newly sourced data and its explanations are substantive edits;
        # mark only those guide pages, not uninspected sources, as modified.
        if chain in SOURCE_NOTES and chain!='Panda Express':
            def date_refresh(match):
                obj=json.loads(match[1])
                if obj.get('@type')=='WebPage':obj['dateModified']=DATE
                return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
            text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',date_refresh,text,flags=re.S)
        assert text.count('<table')==text.count('</table>'),path.name
        path.write_text(text,encoding='utf-8')
        validate_menu(text,entries,provenance)
        report.append({'route':path.name,'chain':chain,'records':len(entries),'comparisonRecords':[m['name'] for m in pair],
            'tableValues':'central meals and provenance, including known fat','sourceNarrativeUpdated':chain in SOURCE_NOTES,
            'template':'preserved','visualInspection':'not performed by this synchronization tool'})
    out=ROOT/'docs/release-2026-10-03/data-restaurant-sync.json'
    used_sources=[provenance[m['chain']+'||'+m['name']] for m in meals]
    source_urls={url for source in used_sources for url in [source.get('source'),*[r.get('source') for r in source.get('nutrientProvenance',{}).values()]] if url}
    out.write_text(json.dumps({'date':DATE,'restaurantCount':len(chains),'orderCount':len(meals),
        'officialSourceCount':len(source_urls),
        'sourceCheckDates':sorted({r['checked'] for r in used_sources if r.get('checked')}),
        'pages':report,'checks':[f'{len(report)} guide tables match {len(meals)} central order rows','All comparison pairs resolve to central records','Balanced generated tables','No dates refreshed for uninspected restaurant data']},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Synchronized {len(report)} restaurant guides and {len(meals)} source-defined rows.')

if __name__=='__main__':run()
