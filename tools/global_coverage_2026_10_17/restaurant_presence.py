"""Stage relationship upserts. Shared presence registry remains the integrator's job."""
from pathlib import Path
import json
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants'
batch=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-records.json').read_text(encoding='utf-8'))
base=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
presence=json.loads((ROOT/'data/restaurant-presence.json').read_text(encoding='utf-8'))['relationships']
known={r.get('id') for r in base if r.get('id')}
updates={r['id']:r for r in batch['updates']}
all_rows=[updates.get(r.get('id'),r) for r in base]+[r for r in batch['records'] if r['id'] not in known]
keys=sorted({(r['market'],r['restaurantId'],r['chain']) for r in batch['records']})
rows=[]
for market,rid,chain in keys:
 previous=next((r for r in presence if r['country']==market and r['restaurantId']==rid),None)
 selected=[r for r in all_rows if r['market']==market and (r.get('restaurantId')==rid or r.get('chain')==chain)]
 scoped=[r for r in batch['records']+batch['updates'] if r['market']==market and r['restaurantId']==rid]
 source_urls=sorted({r['source'] for r in scoped})
 if previous:r=json.loads(json.dumps(previous))
 else:
  r={'id':market+'|'+rid,'country':market,'restaurantBrand':chain,'restaurantId':rid,'localOperatingEntity':None,'officialCountryWebsite':'https://www.kfc.co.uk/','localMenuSource':'https://www.kfc.co.uk/nutrition-allergens','presence':{'status':'confirmed','evidenceUrl':'https://www.kfc.co.uk/kfc-near-me/london' if market=='GB' else 'https://www.kfc.co.uk/kfc-near-me','evidenceType':'current official restaurant directory','observation':'Official London directory lists local restaurants.' if market=='GB' else 'Official shared directory explicitly offers a Republic of Ireland region. The shared local nutrition edition independently labels Ireland-only products.','checkedAt':'2026-10-17'}}
 r.update({'nutritionSources':source_urls,'nutritionAvailable':True,'nutritionSourceStatus':'reviewed-selection','finderSupported':any(x.get('finderSupported',x.get('category')!='component' and all(x.get(k) is not None for k in ('cal','p','c','fat'))) for x in selected),'trackedRecords':len(selected),'completeMacroRecords':sum(all(x.get(k) is not None for k in ('cal','p','c','fat')) for x in selected),'finderRecords':sum(x.get('finderSupported',x.get('category')!='component' and all(x.get(k) is not None for k in ('cal','p','c','fat'))) for x in selected),'calculatedOrders':sum(x.get('verificationStatus')=='calculated-from-official-components' for x in selected),'caloriesOnlyRecords':sum(x.get('cal') is not None and all(x.get(k) is None for k in ('p','c','fat')) for x in selected),'partialMacroRecords':sum(not all(x.get(k) is not None for k in ('cal','p','c','fat')) for x in selected),'coverageStatus':'tracked-macro-selection','lastCheckedDate':'2026-10-17','sourceRetrievalIsVerification':False,'limitations':'Reviewed named source selections and editions; no complete current-menu, every-branch, full-ingredient or allergen-safety claim. Source editions, retrieval and review dates remain separate on each record.','batchNewRecords':len([x for x in batch['records'] if x['market']==market and x['restaurantId']==rid]),'batchRefreshedRecords':len([x for x in batch['updates'] if x['market']==market and x['restaurantId']==rid])})
 if previous and previous.get('nutritionSources'):r['nutritionSources']=sorted(set(previous['nutritionSources']+source_urls))
 rows.append(r)
# Operational presence is confirmed independently, but misleading nutrition is withheld.
mx=next(r for r in presence if r['id']=='MX|kfc').copy()
mx.update({'nutritionAvailable':True,'nutritionSourceStatus':'official-source-withheld-conflicts','finderSupported':False,'coverageStatus':'official-source-withheld-conflicts','lastCheckedDate':'2026-10-17','nutritionSources':['https://kfc.com.mx/tabla-nutricional'],'limitations':'Official 2026 linked nutrition images were inspected; severe internal energy/macronutrient discrepancies prevent trustworthy full-macro import. The source values are not corrected by inference. See restaurant source-review notes.'})
rows.append(mx)
(ROOT/'tools/global_coverage_2026_10_17/restaurant-presence-upserts.json').write_text(json.dumps({'schemaVersion':1,'reviewedAt':'2026-10-17','scope':'Proposed relationship upserts. Recompute counters after shared integration.','relationships':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'relationshipUpserts':len(rows),'newSourceRows':sum(r['batchNewRecords'] for r in rows if 'batchNewRecords' in r)},ensure_ascii=False))
