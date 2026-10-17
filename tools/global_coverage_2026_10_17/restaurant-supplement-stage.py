"""Pin the two official BK country explorer snapshots, preserving named servings."""
from pathlib import Path
import json,re,hashlib
from collections import Counter
import restaurant_stage as core
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/supplement'
DATE='2026-10-17'
retrieval={r['file']:r for r in json.loads((D/'retrieval.json').read_text())}
core.records=[];core.updates=[]
sources=[];withheld=[];raw_items={};presence=[]
def canonical(r):return hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
def source(file,market,url):
 evidence=retrieval[file]
 r={'file':str((D/file).relative_to(ROOT)).replace('\\','/'),'url':url,'captureUrl':evidence['url'],'sha256':hashlib.sha256((D/file).read_bytes()).hexdigest(),'marketScope':market,'chain':'Burger King','sourceEdition':None,'retrievedAt':evidence['retrievedAt'],'verifiedAt':DATE,'captureMethod':'Exact official public country CMS JSON response requested by nutrition explorer app; explicit prod_bk_'+market.lower()+' dataset','coverage':'Named products present in the captured official country nutrition explorer; not live branch stock or an independently complete current-menu claim','limitations':'No publication edition supplied. Explorer displays nutritionWithModifiers for each standard named item; no customizations calculated. Gram/volume units for native weight are not exposed by the inspected nutrition panel, so servingGrams and servingMillilitres are unavailable.','retrievalIsVerification':False}
 sources.append(r);return r
for market in ('CA','US'):
 file='bk-'+market.lower()+'-nutrition.json'
 url='https://www.burgerking.ca/nutrition-explorer' if market=='CA' else 'https://www.bk.com/nutrition-explorer'
 src=source(file,market,url)
 source('bk-'+market.lower()+'-routes.json',market,url)
 doc=json.loads((D/file).read_text())['data']['StaticPage']
 menu=next(w['menu'] for w in doc['widgets'] if w.get('_type')=='nutritionExplorerWidget')
 seen={}
 for section in menu['options']:
  group=section['name']['locale']
  for item in section['options']:
   assert item['_type']=='item','No inferred picker or combo builds permitted'
   if item['_id'] in seen:
    assert seen[item['_id']]==item,'Conflicting repeated source item'
    continue
   seen[item['_id']]=item
   n=item.get('nutritionWithModifiers') or {}
   v={key:n.get(native) for key,native in {'cal':'calories','p':'proteins','c':'carbohydrates','fat':'fat','f':'fiber','na':'sodium','sugar':'sugar','sat':'saturatedFat','salt':'salt'}.items()}
   name=core.clean(item['name']['locale'])
   if any(v[k] is None for k in ('cal','p','c','fat')):
    withheld.append({'market':market,'sourceItemId':item['_id'],'name':name,'reason':'Missing core macro; no substitution from base nutrition or zero fill'});continue
   group_lower=group.lower()
   category='component' if group_lower=='condiments' else 'drink' if any(s in group_lower for s in ('drink','coffee','shake')) else 'dessert' if group_lower=='sweets' else 'side' if group_lower=='sides' else 'entree'
   components=[core.clean(x['name']['locale']) for x in item.get('ingredients') or [] if x.get('name',{}).get('locale')]
   r=core.add(market,'Burger King',name,'1 named source item · standard per-serving build',v,src,'StaticPage '+doc['_id']+' / '+item['_id'],category,notes='Official '+('Canadian' if market=='CA' else 'U.S.')+' nutrition explorer snapshot. Values are its published nutritionWithModifiers field, which the official app displays as the per-serving facts for this named item. Base nutrition and modifier options are not additional records or recomposed into invented builds. Source publication date unavailable; retrieved and reviewed on October 17, 2026. Source weight unit is not shown in the inspected panel; no gram or cup volume inferred. Local branch availability and allergen safety are not established.',group=group,components=components)
   r.update({'sourceDataset':'prod_bk_'+market.lower(),'sourceNutritionField':'nutritionWithModifiers','sourceItemId':item['_id'],'sourceMenuId':menu['_id'],'sourceStaticPageId':doc['_id'],'sourcePublishedNutrition':{k:z for k,z in n.items() if k!='__typename'},'sourceSection':group,'defaultBuildOnly':True})
   r['nutrientBasis']='per source named standard serving'
   if market=='US':r['url']='/burger-king-healthy-meals-macros.html'
   r['sourceVersion']=canonical(r);raw_items[(market,item['_id'])]=item
 selected=[r for r in core.records if r['market']==market]
 presence.append({'id':market+'|burger-king','country':market,'restaurantBrand':'Burger King','restaurantId':'burger-king','localOperatingEntity':None,'officialCountryWebsite':'https://www.burgerking.ca/' if market=='CA' else 'https://www.bk.com/','localMenuSource':url,'presence':{'status':'confirmed','evidenceUrl':url,'evidenceType':'official country nutrition explorer and explicit country CMS dataset','observation':'Published named local menu and per-serving facts are present in prod_bk_'+market.lower()+'. U.S. support explicitly links its U.S. nutrition explorer; the Canadian site is independently scoped.','checkedAt':DATE},'nutritionSources':[url],'lastCheckedDate':DATE,'coverageStatus':'tracked-macro-selection','nutritionAvailable':True,'nutritionSourceStatus':'reviewed-selection','finderSupported':True,'trackedRecords':len(selected),'completeMacroRecords':len(selected),'finderRecords':sum(r['finderSupported'] for r in selected),'calculatedOrders':0,'caloriesOnlyRecords':0,'partialMacroRecords':0,'sourceRetrievalIsVerification':False,'limitations':'Captured official named source selection; no branch-stock, full-live-menu, full ingredient-formula completeness or allergy-safety claim.'})

# Retain short exact app-code excerpts to explain the country and displayed-field
# mapping without publishing the unrelated 13 MB application bundle.
bundle=(D/'browser-response-5.js').read_text(encoding='utf-8') if (D/'browser-response-5.js').exists() else ''
snippets=[]
for term in ['V=()=>`${O()}_${b()}`','sanityDataset)()}_${l.toLowerCase()}','sanity-project-id','n.nutritionWithModifiers.calories','facts:L,allergenGroups:A','androidIntentFilterHosts']:
 pos=bundle.find(term)
 if pos>=0:snippets.append({'match':term,'excerpt':bundle[max(0,pos-170):pos+len(term)+250]})
proof={'sourceUrl':'https://www.burgerking.ca/_expo/static/js/web/index-a5e4389cc3f23924515d4198cf1faad0.js','originalSha256':hashlib.sha256((D/'browser-response-5.js').read_bytes()).hexdigest(),'originalBytes':(D/'browser-response-5.js').stat().st_size,'retrievedAt':DATE,'captureMethod':'Selected exact source-code excerpts; not a full-bundle capture','snippets':snippets,'scopeObservation':'Shared official app explicitly maps US to bk.com and CA to burgerking.ca; Sanity dataset is environment/brand/region. U.S. and Canadian static Nutrition Explorer IDs and payloads are distinct.'} if bundle else json.loads((D/'app-source-excerpts.json').read_text(encoding='utf-8'))
(D/'app-source-excerpts.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources.append({'file':str((D/'app-source-excerpts.json').relative_to(ROOT)).replace('\\','/'),'url':proof['sourceUrl'],'sha256':hashlib.sha256((D/'app-source-excerpts.json').read_bytes()).hexdigest(),'marketScope':['CA','US'],'chain':'Burger King','sourceEdition':None,'retrievedAt':DATE,'verifiedAt':DATE,'captureMethod':proof['captureMethod'],'coverage':'App configuration and field-display evidence only; numeric rows use separately registered exact JSON payloads','limitations':'Full original bundle intentionally not reproduced; original hash and selected exact excerpts retained','retrievalIsVerification':False})

rows=core.records
report={'schemaVersion':1,'reviewedAt':DATE,'scope':'Separate current official Canadian and U.S. Burger King nutrition explorer snapshots; standard named servings only, no inferred customizations.','marketCounts':dict(Counter(r['market'] for r in rows)),'chainCounts':dict(Counter(r['market']+'|'+r['chain'] for r in rows)),'records':rows,'updates':[]}
(ROOT/'tools/global_coverage_2026_10_17/restaurant-supplement-records.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
(D/'source-register.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(D/'presence-upserts.json').write_text(json.dumps({'reviewedAt':DATE,'relationships':presence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(D/'withheld.json').write_text(json.dumps(withheld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(D/'summary.json').write_text(json.dumps({k:v for k,v in report.items() if k not in ('records','updates')},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'records':len(rows),'marketCounts':report['marketCounts'],'finderEligible':dict(Counter(r['market'] for r in rows if r['finderSupported'])),'sources':len(sources),'withheld':len(withheld)},ensure_ascii=False))
