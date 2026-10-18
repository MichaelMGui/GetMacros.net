"""Immutable reviewed market batch; caller owns shared registry and rendering.

Usage: import markets_integrate; registry = markets_integrate.integrate(registry)
No network or application mutation occurs in integrate().
"""
from pathlib import Path
from collections import Counter
import copy, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/markets'
ARTIFACT=Path(__file__).with_name('markets_release_records.json')
DATE='2026-10-18'

def load():
    return json.loads(ARTIFACT.read_text(encoding='utf-8'))

def integrate(registry):
    """Return registry/list with additions and exact-ID updates. Idempotent."""
    batch=load();rows=registry['records'] if isinstance(registry,dict) else registry
    withdrawn=set(batch.get('withdrawnIds',[]))
    rows=[r for r in rows if r.get('id')not in withdrawn]
    replacements={r['id']:r for r in batch['updates']}
    known={r.get('id') for r in rows}
    missing=set(replacements)-known
    if missing:raise ValueError('Refresh IDs missing from supplied registry: '+str(sorted(missing)))
    out=[copy.deepcopy(replacements.get(r.get('id'),r)) for r in rows]
    by_id={r.get('id'):r for r in out if r.get('id')}
    for r in batch['records']:
        if r['id'] in by_id:
            if by_id[r['id']]!=r:
                old=by_id[r['id']]
                hashed={k:v for k,v in old.items()if k!='sourceVersion'}
                valid_old=old.get('sourceVersion')==hashlib.sha256(json.dumps(hashed,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
                if not (valid_old and old.get('sourceHash')==r['sourceHash'] and old.get('market')==r['market'] and old.get('chain')==r['chain']):
                    raise ValueError('Conflicting imported identity: '+r['id'])
                out[out.index(old)]=copy.deepcopy(r);by_id[r['id']]=r
        else:out.append(copy.deepcopy(r));by_id[r['id']]=r
    return {**copy.deepcopy(registry),'records':out} if isinstance(registry,dict) else out

def package(validate_against_current=True):
    files=[Path(__file__).with_name(x) for x in ('markets_records.json','markets_extra_records.json')]
    inputs=[json.loads(p.read_text(encoding='utf-8')) for p in files]
    additions=[r for b in inputs for r in b['records']]
    updates=[r for b in inputs for r in b['updates']]
    assert len({r['id'] for r in additions+updates})==len(additions+updates),'Duplicate source identity'
    baseline=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    ids={r.get('id') for r in baseline}
    if validate_against_current:
        assert all(r['id'] not in ids for r in additions),'Additions already in baseline; review staging before packaging'
        assert all(r['id'] in ids for r in updates),'Unknown refresh identity'
    source_rows=json.loads((DOC/'source-register.json').read_text(encoding='utf-8'))+json.loads((DOC/'extra-source-register.json').read_text(encoding='utf-8'))
    presence=[]
    for market,chain in sorted({(r['market'],r['chain'])for r in additions+updates}):
        scoped=[r for r in additions+updates if (r['market'],r['chain'])==(market,chain)]
        restaurant_id=scoped[0]['restaurantId'];url=scoped[0]['url']
        source_urls=sorted({r['source']for r in scoped})
        presence.append({'id':market+'|'+restaurant_id,'country':market,'restaurantBrand':chain,'restaurantId':restaurant_id,'localOperatingEntity':None,
            'officialCountryWebsite':source_urls[0],'localMenuSource':source_urls[0],
            'presence':{'status':'confirmed','evidenceUrl':source_urls[0],'evidenceType':'official explicitly market-scoped published menu or nutrition table','observation':'Country-specific named portions reviewed against captured primary source. Does not establish every branch or whole live menu.','checkedAt':DATE},
            'nutritionSources':source_urls,'lastCheckedDate':DATE,'coverageStatus':'tracked-macro-selection','nutritionAvailable':True,'finderSupported':any(r.get('finderSupported')for r in scoped),
            'sourceRetrievalIsVerification':False,'nutritionSourceStatus':'reviewed-selection','guideUrl':url,
            'limitations':'Only identified source snapshots and exact named portions; no complete live-menu, every-branch availability, ingredient or allergen-safety claim. Source dates and retrieval dates remain separate.'})
    calculated=[r for r in additions if r['verificationStatus']=='calculated-from-official-components']
    counts={'newSourcePortionRecords':len(additions)-len(calculated),'newCalculatedOrders':len(calculated),'refreshedSourcePortions':len(updates),
        'newByMarket':dict(Counter(r['market']for r in additions)),
        'newByChain':dict(Counter(r['market']+'|'+r['chain']for r in additions)),
        'newSourceProductFamiliesWithExplicitSourceIdentity':len({(r['market'],r['chain'],r['sourceProductFamily'])for r in additions if r.get('sourceProductFamily')}),
        'unknownProductFamilyIdentityPortions':sum(not r.get('sourceProductFamily')for r in additions if r not in calculated)}
    prior=load() if ARTIFACT.exists() else {}
    new_ids={r['id']for r in additions}
    withdrawn=sorted(set(prior.get('withdrawnIds',[]))|{r['id']for r in prior.get('records',[])if r['id']not in new_ids})
    artifact={'schemaVersion':1,'reviewedAt':DATE,'records':additions,'updates':updates,'withdrawnIds':withdrawn,'counts':counts,'presenceUpserts':presence,
        'sources':source_rows,'inputArtifacts':[{'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files],
        'scope':'Source-reviewed exact local portions and four explicitly calculated Canadian orders. Product families, portions and composed orders are different counts. No claim of complete menus or exact food photographs.'}
    ARTIFACT.write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'integration-counts.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'presence-upserts.json').write_text(json.dumps({'schemaVersion':1,'reviewedAt':DATE,'relationships':presence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(counts,ensure_ascii=False,indent=2))
    return artifact

if __name__=='__main__':package()
