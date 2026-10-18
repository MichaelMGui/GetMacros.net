"""Read-only integration contract for the flagship UK menu batch.

No network calls or optional PDF libraries are imported by the site build.
"""
from pathlib import Path
import collections,json

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/uk'

def load_batch():
    return json.loads((ROOT/'tools/flagship_release/uk_records.json').read_text(encoding='utf-8'))

def integrate(existing):
    """Return preserved existing records plus this GB batch, idempotently."""
    batch=load_batch()
    withdrawn=set(batch.get('withdrawnIds',[]))
    result=[r for r in existing if r.get('id') not in withdrawn]
    positions={r.get('id'):i for i,r in enumerate(result) if r.get('id')}
    for row in batch['records']:
        assert row['market']=='GB' and row['country']=='GB'
        if row['id'] in positions:result[positions[row['id']]]=row
        else:positions[row['id']]=len(result);result.append(row)
    return result

def definitions():
    """Chain metadata for the integrator's existing international guide builder."""
    return json.loads((ROOT/'tools/flagship_release/uk_definitions.json').read_text(encoding='utf-8'))['restaurants']

def presence_upserts(existing=()):
    all_rows=integrate(existing)
    rows=[]
    for item in definitions():
        selected=[r for r in all_rows if r.get('market')=='GB' and r.get('restaurantId')==item['restaurantId']]
        rows.append(dict(id='GB|'+item['restaurantId'],country='GB',restaurantBrand=item['chain'],restaurantId=item['restaurantId'],
            localOperatingEntity=None,officialCountryWebsite=item['officialCountryWebsite'],localMenuSource=item['menuSource'],
            presence=dict(status='confirmed',evidenceUrl=item['presenceSource'],evidenceType='current official local menu/restaurant evidence',observation=item['presenceObservation'],checkedAt='2026-10-18'),
            nutritionSources=sorted({r['source'] for r in selected}),nutritionAvailable=True,nutritionSourceStatus='reviewed-selection',
            finderSupported=any(r.get('finderSupported') for r in selected),trackedRecords=len(selected),completeMacroRecords=sum(r.get('macroComplete',False) for r in selected),
            finderRecords=sum(r.get('finderSupported',False) for r in selected),calculatedOrders=sum(r.get('verificationStatus')=='calculated-from-official-components' for r in selected),
            caloriesOnlyRecords=0,partialMacroRecords=sum(not r.get('macroComplete',False) for r in selected),coverageStatus='tracked-macro-selection' if any(r.get('finderSupported') for r in selected) else 'tracked-components-only',
            lastCheckedDate='2026-10-18',sourceRetrievalIsVerification=False,limitations=item['limitations']))
    return rows

if __name__=='__main__':
    batch=load_batch()['records']
    print(json.dumps(dict(records=len(batch),chains=dict(collections.Counter(r['chain'] for r in batch)),relationships=len(presence_upserts())),ensure_ascii=False,indent=2))
