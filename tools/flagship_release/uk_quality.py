"""Apply independent-audit dispositions to the frozen UK handoff, idempotently.

Does not read or write the shared restaurant registry. Source contradictions are
withheld, never repaired by guessing a decimal or substituting another market.
"""
from pathlib import Path
import collections, hashlib, json

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/uk'
BATCH=ROOT/'tools/flagship_release/uk_records.json'

def main():
    batch=json.loads(BATCH.read_text(encoding='utf-8'))
    records=batch['records']; withheld=json.loads((DOC/'withheld.json').read_text(encoding='utf-8'))
    withdrawn=set(batch.get('withdrawnIds',[])); review=[]; kept=[]
    previous=DOC/'quality-dispositions.json'
    if previous.exists():review=json.loads(previous.read_text(encoding='utf-8'))
    for row in records:
        reason=None
        if row['name']=='Kids Pick and Mix Meals' and row['chain']=='LEON':
            reason='Variable pick-and-mix bundle has zero placeholder weight and nutrients, not a specified zero-calorie meal.'
        elif row['name']=='Chives' and row['chain']=='Wendy’s' and row.get('servingGrams')==0:
            reason='Source prints a zero-gram, all-zero condiment allocation; no meaningful loggable portion established.'
        else:
            for child,parent in [('sat','fat'),('sugar','c')]:
                if row.get(child) is not None and row.get(parent) is not None and row[child]>row[parent]+.5:
                    reason=f'Official source contradicts its own subset nutrient: {child}={row[child]} exceeds {parent}={row[parent]}. Withheld pending source correction; not guessed.'
                    break
        if reason:
            withdrawn.add(row['id'])
            disposition=dict(id=row['id'],chain=row['chain'],name=row['name'],source=row['source'],sourcePage=row['sourcePage'],reason=reason,values={k:row.get(k) for k in ['cal','p','c','fat','f','sugar','sat','na']},sourceHash=row['sourceHash'],reviewedAt='2026-10-18')
            withheld.append(disposition);review.append(dict(**disposition,action='withheld'));continue
        if row.get('servingGrams')==0:
            row['servingGrams']=None
            row['sourceServingGrams']=0
            row['serving']=row['serving'].replace(' · 0 g','')
            row['notes']+=' Source zero gram-weight is treated as unavailable, not a zero-size serving; the named published recipe nutrients remain source-reported.'
            review.append(dict(id=row['id'],chain=row['chain'],name=row['name'],source=row['source'],sourcePage=row['sourcePage'],action='invalid mass changed to unknown',reason='Published zero gram-weight cannot define a serving; original source weight retained as sourceServingGrams=0.'))
        if row['chain']=='PizzaExpress' and row['name'] in ('Goats Cheese','Spinach'):
            row['sourceProductName']=row['name']
            row['name']+=' · '+('Airport breakfast extra' if row['sourceGroup']=='Airport breakfast extras' else 'Pizza topping')
            row['serving']='1 published '+('airport breakfast extra portion' if row['sourceGroup']=='Airport breakfast extras' else 'pizza topping portion')
            review.append(dict(id=row['id'],chain=row['chain'],name=row['name'],source=row['source'],sourcePage=row['sourcePage'],action='portion scope made visible',reason='Different source recipe allocations must not share an indistinguishable name/serving. Stable record ID preserved.'))
        # Minor parent/subset differences can arise from separately rounded
        # published fields. Keep them visible in provenance rather than altering
        # a reported field. Anything greater than 0.5 g is withheld above.
        warnings=[]
        for child,parent in [('sat','fat'),('sugar','c')]:
            if row.get(child) is not None and row.get(parent) is not None and row[child]>row[parent]:
                warnings.append(dict(field=child,parent=parent,difference=round(row[child]-row[parent],8),status='source-rounding-or-inconsistency',explanation='Source-reported values retained; small parent/subset difference is not silently corrected.'))
        if warnings:row['sourceQualityWarnings']=warnings
        if row['chain']=='Zizzi' and row['name']=='Birthday Cake':
            row['serving']='1 whole source-listed birthday cake (not one slice)'
        if row['chain']=='Pepe’s' and row['name']=='Mega (Serves 5-6)':
            row['serving']='1 whole Mega order, source says serves 5–6 (not one person)'
        row['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in row.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
        kept.append(row)
    batch.update(records=kept,withdrawnIds=sorted(withdrawn))
    BATCH.write_text(json.dumps(batch,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    summary=json.loads((DOC/'summary.json').read_text(encoding='utf-8'))
    summary.update(counts=dict(collections.Counter(r['chain'] for r in kept)),records=len(kept),categories=dict(collections.Counter(r['category'] for r in kept)),withheld=len(withheld),products=len({(r['chain'],r.get('productId',r['name'].split(' · ')[0])) for r in kept}),withdrawnAfterIndependentAudit=len(withdrawn))
    (DOC/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'withheld.json').write_text(json.dumps(withheld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    review=list({(x['id'],x['action']):x for x in review}.values())
    (DOC/'quality-dispositions.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(records=len(kept),withdrawnIds=sorted(withdrawn),dispositions=len(review)),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
