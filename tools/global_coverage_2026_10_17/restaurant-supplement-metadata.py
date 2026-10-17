from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/supplement'
B=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-supplement-records.json').read_text(encoding='utf-8'))
R=B['records'];DATE='2026-10-17'
def find(m,name):return next(r for r in R if r['market']==m and r['name']==name)
briefs=[]
def brief(m,slug,title,rows,paragraphs):
 briefs.append({'market':m,'slug':slug,'title':title,'reviewedAt':DATE,'scope':'Country-specific named standard Burger King per-serving products from separate official nutrition explorer snapshots. No customizations invented.','paragraphs':paragraphs,'comparisonRows':[{k:r.get(k) for k in ('id','market','country','chain','name','serving','servingGrams','cal','p','c','fat','f','na','sugar','sat','source','sourceDate','sourcePage','checked')} for r in rows],'calculations':[],'sources':sorted({r['source'] for r in rows}),'recordIds':[r['id'] for r in rows]})
ca=find('CA','Whopper®');cac=find('CA','Whopper® with Cheese');us=find('US','Whopper');usc=find('US','Whopper with Cheese')
brief('CA','burger-king-canada-whopper-cheese-standard-serving','Burger King Canada: Whopper and Whopper with Cheese',[ca,cac],[
 'The current Canadian nutrition explorer supplies two separate named standard servings: Whopper and Whopper with Cheese. Its Whopper is 710 kcal, 33 g protein, 50 g carbohydrate, 43 g fat and 1,150 mg sodium.',
 'The Canadian Whopper with Cheese is 790 kcal, 37 g protein, 51 g carbohydrate, 50 g fat and 1,420 mg sodium. Comparing those two complete published products gives an increase of 80 kcal, 4 g protein, 1 g carbohydrate, 7 g fat and 270 mg sodium.',
 'Those are named whole-item servings from the official explorer. No fries or drink is included, and the difference is not a measured nutrition statement for an arbitrary cheese slice or a custom cheese quantity.',
 'The explorer does not show a publication date or a serving-weight unit in its inspected facts panel. The saved record therefore preserves an unknown publication date and leaves gram weight unavailable. Retrieval and review were October 17, 2026; branch stock and allergy safety are separate questions.'
 ])
briefs[-1]['calculations']=[{'expression':'Canadian named Whopper with Cheese minus Whopper',**{k:cac[k]-ca[k] for k in ('cal','p','c','fat','na')}}]
brief('US','burger-king-us-whopper-cheese-standard-serving','Burger King U.S.: use the local Whopper serving',[us,usc],[
 'The official U.S. nutrition explorer has its own published country payload. Its standard Whopper is 710 kcal, 34 g protein, 57 g carbohydrate, 42 g fat and 1,250 mg sodium.',
 'The U.S. Whopper with Cheese is 790 kcal, 37 g protein, 58 g carbohydrate, 49 g fat and 1,660 mg sodium. For these complete named products, the cheese version adds 80 kcal, 3 g protein, 1 g carbohydrate, 7 g fat and 410 mg sodium.',
 'Use the named standard per-serving build. The official app displays the nutritionWithModifiers field for that default build; the separate base-nutrition object and optional modifier choices are not additional whole meals and are not recombined into new records.',
 'Sodium is directly source-reported. A separately supplied rounded salt field does not replace that direct sodium value. The source has no publication edition; the snapshot was retrieved and reviewed October 17, 2026, and does not prove availability at every branch.'
 ])
briefs[-1]['calculations']=[{'expression':'U.S. named Whopper with Cheese minus Whopper',**{k:usc[k]-us[k] for k in ('cal','p','c','fat','na')}}]
brief('CA','burger-king-canada-us-whopper-local-ingredients','Canada and U.S. Whoppers: same calories, different local records',[ca,us],[
 'Both current official country explorers list the standard Whopper at 710 kcal, but their remaining values differ. Canada lists 33 g protein, 50 g carbohydrate, 43 g fat and 1,150 mg sodium. The U.S. lists 34 g protein, 57 g carbohydrate, 42 g fat and 1,250 mg sodium. These are separate local records, not interchangeable servings.',
 'Each local source publishes ingredient statements for named components. Both identify the beef patty as beef. The Canadian mayonnaise statement includes water, onion powder and garlic powder; the U.S. mayonnaise statement includes ground red pepper, dried garlic and mustard oil. These are differences in the published statements, without assuming that either statement specifies ingredient quantities.',
 'The bun statements also differ. Canada lists a canola-or-soybean vegetable oil option and pea protein; the U.S. statement lists soybean oil and a vegetable-protein group containing pea, potato and faba bean. Supplier alternatives and the source wording matter when comparing local menus.',
 'No isolated ingredient change is claimed to cause the macro differences: the whole products, source rounding and local standard servings can all differ. Full recipe quantities, unpublished processing details, branch stock and allergy safety are not inferred from these ingredient statements. Use the correct country when finding or logging a meal.'
 ])
briefs[-1]['calculations']=[{'expression':'U.S. named Whopper minus Canadian Whopper',**{k:us[k]-ca[k] for k in ('cal','p','c','fat','na')}}]
(D/'guide-briefs.json').write_text(json.dumps({'reviewedAt':DATE,'briefs':briefs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
link={'sourceUrl':'https://help.bk.com/hc/en-us/articles/36913083446935-Where-can-I-view-the-nutrition-and-allergen-information-for-Burger-King-menu-items','retrievedAt':DATE,'verifiedAt':DATE,'captureMethod':'Official page read with web.run; selected short evidence excerpt','pageTitle':'Where can I view the nutrition and allergen information for Burger King menu items?','pageUpdatedAt':'2026-03-17 15:20','observedLinkText':'BK Nutrition Explorer – USA','observedLinkUrl':'https://www.bk.com/nutrition-explorer','observation':'Official U.S. help article directs users to the current U.S. explorer. The linked article date is not an edition date for the nutrition payload.'}
(D/'bk-us-official-linkage.json').write_text(json.dumps(link,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=json.loads((D/'source-register.json').read_text(encoding='utf-8'))
for file,url,market,method in [('bk-us-official-linkage.json',link['sourceUrl'],'US',link['captureMethod']),('bk-ca-whopper-rendered.txt','https://www.burgerking.ca/nutrition-explorer','CA','Official explorer rendered in Edge and standard Whopper facts opened; visible text captured')]:
 sources=[s for s in sources if not s['file'].endswith('/'+file)]
 sources.append({'file':str((D/file).relative_to(ROOT)).replace('\\','/'),'url':url,'sha256':hashlib.sha256((D/file).read_bytes()).hexdigest(),'marketScope':market,'chain':'Burger King','sourceEdition':None,'retrievedAt':DATE,'verifiedAt':DATE,'captureMethod':method,'coverage':'Country linkage and visible per-serving unit/display verification','limitations':'Not a separate nutrition dataset or a menu edition date','retrievalIsVerification':False})
(D/'source-register.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
blockers={'reviewedAt':DATE,'mcdonaldsCanada':{'status':'blocked; no records staged','urls':['https://www.mcdonalds.com/ca/en-ca/full-menu.html','https://www.mcdonalds.com/ca/en-ca/about-our-food/nutrition-calculator.html','https://www.mcdonalds.com/dnaapp/itemDetails?country=CA&language=en&showLiveData=true&item=200154&nutrient_req=Y'],'evidence':'HTTP403 on direct requests; Edge full-menu rendering explicitly Access Denied. Official indexed product pages contain dynamic empty nutrition panels in web text. No macros inferred from names, third-party sources or an old unlinked PDF.'},'burgerKingUS':{'status':'public nutrition data resolved; browser country redirect remains','requestedUrl':'https://www.bk.com/nutrition-explorer','browserRedirect':'https://www.burgerking.ca/nutrition-explorer','resolution':'Explicitly select prod_bk_us using the official public app CMS query and its separate U.S. StaticPage. Canadian data remains in prod_bk_ca and is never relabelled.','rejectedHistoricalSource':{'url':'https://bk-use1-prod.sites.rbictg.com/nutrition/nutrition.pdf','edition':'2022-11','reason':'Not a current linked live-menu source; no records imported from this PDF.'}}}
(D/'blockers.json').write_text(json.dumps(blockers,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'briefs':len(briefs),'sources':len(sources),'records':len(R)}))
