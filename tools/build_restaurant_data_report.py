#!/usr/bin/env python3
"""Build the public data snapshot from integrated meals and lossless provenance.

Default writes a private page/statistics artifact; --apply installs ONLY the report
page. --preview-expansion simulates the verified append without shared data writes.
Run this after release-resource/article generation so that an older report body
does not replace the current coverage and unknown-value counts.
"""
from pathlib import Path
import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import re
import statistics
from build_meal_finder import parse_meals
from meal_provenance import read
from build_restaurant_expansion import payload, append_meals, metadata_overrides

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tools/restaurant_release'
ROUTE='fast-food-nutrition-data-report.html'
FIELDS={'cal':('Calories','kcal'),'p':('Protein','g'),'c':('Carbohydrate','g'),'fat':('Fat','g'),'f':('Fiber','g'),'na':('Sodium','mg')}

def load(preview=False):
    source=(ROOT/'js/meal-data.js').read_text(encoding='utf-8')
    provenance=read(ROOT/'js/meal-provenance.js')
    if preview:
        source=append_meals(source)
        provenance.update(metadata_overrides())
    records=[]
    for meal in parse_meals(source):
        key=meal['chain']+'||'+meal['name']
        if key not in provenance:
            raise ValueError('Missing provenance: '+key)
        proof=provenance[key]
        records.append({'key':key,'meal':meal,'proof':proof,'values':{k:proof.get('fat') if k=='fat' else meal.get(k) for k in FIELDS}})
    expected=payload()
    if len(records)!=expected['baseRecords']+expected['newOrders'] or len({r['meal']['chain'] for r in records})!=expected['baseChains']+expected['newChains']:
        raise ValueError('Report requires the complete integrated release inventory; use --preview-expansion for a private preview')
    if len({r['key'] for r in records})!=len(records):
        raise ValueError('Duplicate record identities')
    for r in records:
        if r['proof'].get('region')!='U.S.':
            raise ValueError('Unestablished geographic scope: '+r['key'])
    return records

def statistics_for(records):
    version=payload()['date']
    inspection_start='2026-10-03'
    def checked(info):
        return inspection_start <= str(info.get('retrieved','')) <= version
    inspected=[r for r in records if any(checked(info) for info in r['proof'].get('nutrientProvenance',{}).values())]
    exact_inspected=[r for r in records if all(r['values'][k] is not None and checked(r['proof'].get('nutrientProvenance',{}).get(k,{})) for k in FIELDS)]
    exact_all=[r for r in records if all(r['values'][k] is not None for k in FIELDS)]
    ranges={}
    for k in FIELDS:
        values=[r['values'][k] for r in records if r['values'][k] is not None]
        ranges[k]={'known':len(values),'unknown':len(records)-len(values),'min':min(values),'median':statistics.median(values),'max':max(values)}
    chains=defaultdict(list)
    for r in records:chains[r['meal']['chain']].append(r)
    coverage=[]
    for chain,rows in sorted(chains.items()):
        calories=[r['values']['cal'] for r in rows if r['values']['cal'] is not None]
        proteins=[r['values']['p'] for r in rows if r['values']['p'] is not None]
        coverage.append({'chain':chain,'route':rows[0]['meal']['url'],'records':len(rows),
            'calorieMin':min(calories),'calorieMax':max(calories),'proteinMin':min(proteins),'proteinMax':max(proteins),
            'unknownFiber':sum(r['values']['f'] is None for r in rows),'unknownFat':sum(r['values']['fat'] is None for r in rows)})
    sources={url for r in records for url in [r['proof'].get('source'),*[info.get('source') for info in r['proof'].get('nutrientProvenance',{}).values()]] if url}
    data=[{'key':r['key'],'values':r['values'],'proof':r['proof']} for r in records]
    digest=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    original_audit_path=ROOT/'docs/release-2026-10-03/data-audited-patches.json'
    original=json.loads(original_audit_path.read_text(encoding='utf-8'))['records']
    original_exact=[r['values'] for r in original if len(r['values'])==6 and all(v is not None for v in r['values'].values())]
    return {'snapshotDate':version,'inspectionStart':inspection_start,'market':'U.S.','records':len(records),'chains':len(chains),
        'sourceInspectedRecords':len(inspected),'sourceInspectedChains':len({r['meal']['chain'] for r in inspected}),
        'exactSixNutrients':len(exact_all),'exactSixNutrientsInspectedThisRelease':len(exact_inspected),
        'exactFinderNutrients':sum(all(r['values'][k] is not None for k in ('cal','p','f','na')) for r in records),
        'sourceURLs':len(sources),'ranges':ranges,'coverage':coverage,'snapshotSHA256':digest,
        'originalOctober3Subset':{'inspected':len(original),'exactSixNutrients':len(original_exact),'medianCalories':statistics.median(r['cal'] for r in original_exact),'medianProtein':statistics.median(r['p'] for r in original_exact)},
        'inspectionNotClaimed':['Kitchen measurements','Local menu availability','Allergen safety','Price verification','Representative population survey']}

def esc(value):return html.escape(str(value),quote=True)
def num(value):return f'{value:,g}'

def render_body(s):
    measures=[('Recorded orders',s['records'],'Individual foods, explicitly named portions and defined combinations.'),
        ('Restaurant names',s['chains'],'Distinct U.S. chain labels; not a store-location count.'),
        ('Records with all six exact nutrition values',s['exactSixNutrients'],'Calories, protein, carbohydrate, fat, fiber and sodium; includes earlier source checks.'),
        ('Records with all finder nutrients known',s['exactFinderNutrients'],'Calories, protein, fiber and sodium; the finder’s complete-data setting uses this subset.'),
        ('Unknown exact fiber values',s['ranges']['f']['unknown'],'Includes less-than bounds; unknown values are not zero.'),
        ('Unknown fat values',s['ranges']['fat']['unknown'],'Fat comes from recorded provenance, never inferred from calories.'),
        ('Source-inspected records, October 3–4',s['sourceInspectedRecords'],'At least one nutrient source inspected during this release; not a new recipe date.'),
        ('Chains in that source inspection',s['sourceInspectedChains'],'Inspection coverage, not every store or full menu.'),
        ('Six exact values inspected or calculated, October 3–4',s['exactSixNutrientsInspectedThisRelease'],'All six nutrients have release-period provenance and an exact number.')]
    coverage='<div class="table-wrap" tabindex="0" role="region" aria-label="Dataset coverage"><table class="comparison-table"><thead><tr><th scope="col">Measure</th><th scope="col">Records</th><th scope="col">Meaning</th></tr></thead><tbody>'+''.join('<tr><th scope="row">'+label+'</th><td>'+str(count)+'</td><td>'+meaning+'</td></tr>' for label,count,meaning in measures)+'</tbody></table></div>'
    ranges='<div class="table-wrap" tabindex="0" role="region" aria-label="Known-value nutrition ranges"><table class="comparison-table"><thead><tr><th scope="col">Nutrient</th><th scope="col">Minimum</th><th scope="col">Median</th><th scope="col">Maximum</th><th scope="col">Unknown</th></tr></thead><tbody>'
    for k,(label,unit) in FIELDS.items():
        r=s['ranges'][k]
        ranges+='<tr><th scope="row">'+label+' ('+unit+')</th>'+''.join('<td>'+num(r[v])+'</td>' for v in ('min','median','max','unknown'))+'</tr>'
    ranges+='</tbody></table></div>'
    chain_table='<details><summary>Coverage by restaurant</summary><div class="table-wrap" tabindex="0" role="region" aria-label="Recorded coverage by restaurant"><table class="comparison-table"><thead><tr><th scope="col">Restaurant</th><th scope="col">Orders</th><th scope="col">Calories: min–max</th><th scope="col">Protein: min–max (g)</th><th scope="col">Unknown fiber</th><th scope="col">Unknown fat</th></tr></thead><tbody>'
    for c in s['coverage']:
        chain_table+=f'<tr><th scope="row"><a href="{esc(c["route"])}">{esc(c["chain"])}</a></th><td>{c["records"]}</td><td>{num(c["calorieMin"])}–{num(c["calorieMax"])}</td><td>{num(c["proteinMin"])}–{num(c["proteinMax"])}</td><td>{c["unknownFiber"]}</td><td>{c["unknownFat"]}</td></tr>'
    chain_table+='</tbody></table></div></details>'
    historic=s['originalOctober3Subset']
    history=f'<details><summary>The earlier October 3 subset</summary><p>The initial source audit covered {historic["inspected"]} records. Of those, {historic["exactSixNutrients"]} had six exact inspected or calculated values. Its median was {num(historic["medianCalories"])} calories and {num(historic["medianProtein"])} g protein. Those figures describe that earlier subset only.</p><div class="table-wrap"><table class="comparison-table"><thead><tr><th scope="col">Earlier subset measure</th><th scope="col">October 3 value</th></tr></thead><tbody>'+''.join('<tr><th scope="row">'+label+'</th><td>'+num(count)+'</td></tr>' for label,count in [('Inspected records',historic['inspected']),('Six exact inspected values',historic['exactSixNutrients']),('Median calories',historic['medianCalories']),('Median protein (g)',historic['medianProtein'])])+'</tbody></table></div></details>'
    return f'''<p class="submission-byline">By GetMacros · Published October 3, 2026 · Data snapshot October 4, 2026</p>
<p>The current dataset contains <strong>{s['records']} recorded orders across {s['chains']} U.S. restaurant names</strong>. These are selected portions and explicitly assembled orders. Coverage is recorded below; it is not a survey of the restaurant market.</p>
<h2 id="resource-section-1">What the snapshot covers</h2>{coverage}{chain_table}
<h2 id="resource-section-2">Known values and unknown values</h2><p>Each minimum, median and maximum uses only records with a known value for that nutrient. Different nutrients can therefore describe different subsets. A listed “less than 1 g” is a bound, not an exact zero or one.</p>{ranges}
<p>These ranges include single tacos, breakfast items, sides retained in the original dataset and large combinations. The maximum is a recorded portion, not a suggested target. The median is not a typical lunch or an estimate of what people eat.</p>
<h2 id="resource-section-3">Portions and calculations stay visible</h2><p>A single taco remains one taco. Extra sides, sauce packets and drinks are excluded unless the named build includes them. Regular Noodles dishes are not small portions. Culver’s July 2025 dinner figures include the protein, lemon wedge, roll and butter; extra sides are separate. El Pollo Loco’s marked salads and tostadas exclude dressing.</p>
<p>A published recipe total and a GetMacros component sum are different kinds of evidence. Chipotle and Panda builds retain their ingredient assumptions. The two new Raising Cane’s finger orders sum explicitly listed individual portions and are not presented as official combo totals. If one component has unknown exact fiber, the total stays unknown. No missing fat is estimated from a calorie equation.</p>
<h2 id="resource-section-4">Source dates are not recipe dates</h2><p>The October 3–4 inspection covered {s['sourceInspectedRecords']} records from {s['sourceInspectedChains']} chains at least partly. The remaining records retain earlier check dates. A source inspection means the published document or page was inspected; it is not a kitchen measurement, local availability test or promise that a recipe just changed.</p>
<p>Arby’s printed effective date is June 2026. SONIC’s linked filename says September 2026 but its cover says Summer 2026. Culver’s uses an official July 2025 PDF; check its live guide for later changes. In-N-Out uses the January 2026 PDF linked by its nutrition page, which differs from some HTML values. Exact printed dates remain unknown for Noodles and Taco John’s.</p>
<p>The earlier CAVA document’s current menu linkage remains unresolved. Starbucks source access used indexed official text. The twelve-count Chick-fil-A nuggets have separate dates for four newly inspected nutrients and their older fiber and sodium records. These limits do not disappear when the site design changes.</p>{history}
<h2 id="resource-section-5">Use or cite these figures</h2><p>Cite “GetMacros restaurant-data snapshot, October 4, 2026,” this URL, the statistic, units and subset definition. For a specific restaurant nutrient claim, also cite that order’s official source and portion. These U.S. records are not Canadian or globally interchangeable menu data.</p>
<p>The snapshot is computed from the central meal records and their recorded provenance. A deterministic snapshot fingerprint is <code>{s['snapshotSHA256'][:16]}</code>. It identifies this record set, not independent certification.</p>
<h2 id="resource-section-6">Sources and limits</h2><p><a href="sources.html">Sources and methodology</a> explains the record definitions. Individual <a href="restaurant-meal-guides.html">restaurant guides</a> provide official links, source editions and serving notes. Prices, allergen safety and unsupported menu customizations are not inferred. GetMacros does not republish restaurant photographs or source PDFs as its own artwork.</p>
<aside class="ad-placement" data-ad-placement="article-after-content" hidden aria-label="Advertisement"></aside><aside class="source-ribbon"><div><h2>Find an order with these values</h2><p><a href="restaurant-meal-finder.html">Find and compare meals</a></p><p><a href="restaurant-meal-guides.html">Browse restaurant guides</a></p></div></aside>'''

def page(records,s):
    source=(ROOT/ROUTE).read_text(encoding='utf-8')
    body=render_body(s)
    # Retain direct citations from the earlier audit as well as each current
    # record's official source. A link to a guide does not replace a citation.
    from build_release_resources import load as earlier_resources
    references={r['proof']['source']:r['meal']['chain']+' official nutrition source' for r in records}
    earlier=next(r for r in earlier_resources() if r['slug']==ROUTE)
    for url in earlier['sourceURLs']:references.setdefault(url,'Earlier October 3 audit reference')
    bibliography='<details><summary>Official source references</summary><ul>'+''.join('<li><a href="'+esc(url)+'">'+esc(label)+'</a></li>' for url,label in sorted(references.items(),key=lambda x:(x[1],x[0])))+'</ul></details>'
    body=body.replace('<aside class="ad-placement"',bibliography+'<aside class="ad-placement"',1)
    source,n=re.subn(r'(<article\b[^>]*class="article-container release-article"[^>]*>).*?(</article>)',lambda m:m[1]+body+m[2],source,count=1,flags=re.S)
    if n!=1:raise ValueError('Report reading template not recognized; refusing mutation')
    toc_labels=['What the snapshot covers','Known values and unknown values','Portions and calculations stay visible','Source dates are not recipe dates','Use or cite these figures','Sources and limits']
    toc='<details class="reading-contents"><summary>In this guide</summary><nav class="garden-toc" aria-label="On this page">'+''.join(f'<a href="#resource-section-{i}">{label}</a>' for i,label in enumerate(toc_labels,1))+'</nav></details>'
    source,n=re.subn(r'<details class="reading-contents">.*?</details>',toc,source,count=1,flags=re.S)
    if n!=1:raise ValueError('Report table of contents not recognized')
    def metadata(match):
        obj=json.loads(match[1])
        if obj.get('@type')=='Article':
            obj['dateModified']=s['snapshotDate']
        return '<script type="application/ld+json">'+json.dumps(obj,ensure_ascii=False)+'</script>'
    source=re.sub(r'<script type="application/ld\+json">(.*?)</script>',metadata,source,flags=re.S)
    return source

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply',action='store_true')
    p.add_argument('--preview-expansion',action='store_true')
    args=p.parse_args()
    if args.apply and args.preview_expansion:
        raise ValueError('A simulated expansion must not be published; integrate the actual dataset first')
    records=load(args.preview_expansion)
    stats=statistics_for(records)
    generated=page(records,stats)
    (OUT/'data-report-statistics.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'data-report-preview.html').write_text(generated,encoding='utf-8')
    if args.apply:(ROOT/ROUTE).write_text(generated,encoding='utf-8')
    print(json.dumps({k:stats[k] for k in ('records','chains','exactSixNutrients','exactFinderNutrients','sourceInspectedRecords','sourceInspectedChains','exactSixNutrientsInspectedThisRelease','ranges')},ensure_ascii=False))

if __name__=='__main__':main()
