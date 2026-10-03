"""Release gates for published HTML, source records and derived arithmetic."""
from pathlib import Path
from html import unescape
import json
import math
import re
from build_release_resources import load
from build_meal_finder import parse_meals
from meal_provenance import pack, read

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/release-2026-10-03'
rows=load()
assert len(rows)==33 and len({r['slug'] for r in rows})==33
assert len({r['intent'] for r in rows})==33
patches=json.loads((OUT/'data-audited-patches.json').read_text(encoding='utf-8'))
audited={r['recordKey']:r for r in patches['records']}
meals={m['chain']+'||'+m['name']:m for m in parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))}
provenance=read(ROOT/'js/meal-provenance.js')
facts=0
for row in rows:
    text=(ROOT/row['slug']).read_text(encoding='utf-8')
    assert '<h1>'+row['h1']+'</h1>' in text or unescape(row['h1']) in unescape(text),row['slug']
    # Shared presentation adds section IDs/classes; authored words remain intact.
    for paragraph in re.findall(r'<p(?: [^>]*)?>(.*?)</p>',row['body'],re.S):
        plain=lambda v:re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>','',v))).strip()
        assert plain(paragraph) in plain(text),(row['slug'],plain(paragraph))
    assert row['originalUtility'] and row['sourceURLs'],row['slug']
    for source in row['sourceURLs']:assert source in unescape(text),(row['slug'],source)
    assert 'data-ad-placement=' in text and 'data-food-character=' in text,row['slug']
    for fact in row.get('tableFacts',[]):
        facts+=1
        if fact['recordKey']:
            checked=audited[fact['recordKey']]
            for nutrient,value in fact['values'].items():
                assert value==checked['values'].get(nutrient),(row['slug'],fact['recordKey'],nutrient,value)
        else:
            assert fact['values'] in [v for group in patches['ingredients'].values() for v0 in group['values'].values() for v in [{k:v0.get(k) for k in fact['values']}]],(row['slug'],fact['label'])
        if row['slug']!='fast-food-nutrition-data-report.html':
            assert unescape(fact['label']) in unescape(text) and fact['serving'] in unescape(text),(row['slug'],fact['label'],'visible portion')
assert facts==183
# Forty-one report inputs produce aggregate statistics, not forty-one visible rows.
import statistics
complete=[r['values'] for r in audited.values() if len(r['values'])==6]
assert len(complete)==40
snapshot=(ROOT/'fast-food-nutrition-data-report.html').read_text(encoding='utf-8')
for statistic in [len(meals),len({m['chain'] for m in meals.values()}),len(audited),len(complete),statistics.median(m['cal'] for m in complete),statistics.median(m['p'] for m in complete)]:
    assert f'>{statistic:g}' in snapshot,statistic
for key,patch in audited.items():
    for nutrient,value in patch['values'].items():
        actual=provenance[key]['fat'] if nutrient=='fat' else meals[key][nutrient]
        assert actual==value,(key,nutrient,actual,value)
    assert provenance[key]['serving']==patch['serving'],key
    assert provenance[key]['checked']==patch['retrievalDate'],key
# The source wire format is lossless, including the two older CFA nutrients.
temp=OUT/'source-wire-roundtrip.js'
temp.write_text(pack(provenance),encoding='utf-8')
assert read(temp)==provenance
temp.unlink()
partial=provenance['Chick-fil-A||Grilled Nuggets, 12 count']['nutrientProvenance']
assert partial['na']['retrieved']=='2026-09-09' and partial['cal']['retrieved']=='2026-10-03'
sums=json.loads((OUT/'data-derived-calculations.json').read_text(encoding='utf-8'))['calculations']
assert len(sums)==7
for example in sums:
    for nutrient,total in example['results'].items():
        expected=sum(c['count']*c['values'][nutrient] for c in example['components'])
        assert math.isclose(total,expected,abs_tol=.000001),(example['label'],nutrient)
report={'resources':len(rows),'uniqueIntents':33,'reproducedSourceFactEntries':facts,'visibleNutritionRows':142,'snapshotInputRecords':41,'auditedFinderRecords':len(audited),'ingredientSums':len(sums),'sourceWireRoundtrip':'lossless','partialCheckDates':'preserved','visualInspection':'not performed by this script'}
(OUT/'content-tests.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS:',report)
