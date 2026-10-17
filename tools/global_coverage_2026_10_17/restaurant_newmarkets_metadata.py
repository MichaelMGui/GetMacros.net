"""Market seeds, presence upserts and four editorial briefs; no shared writes."""
from pathlib import Path
import json,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/newmarkets'
B=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-records.json').read_text(encoding='utf-8'))
rows=B['records']
spec={
 'FR':{'name':'France','continent':'Europe','currency':'EUR','flag':'🇫🇷','chain':'Quick','sourceLanguage':'fr','website':'https://www.quick.fr/','presenceUrl':'https://www.quick.fr/tous-les-quicks','operator':None,'scope':'Quick France official menu. French source product names are preserved; English site navigation is a separate language choice.','presenceObservation':'Official directory explicitly lists the Quick restaurants of France.','edition':'2026-10-06'},
 'IN':{'name':'India','continent':'Asia','currency':'INR','flag':'🇮🇳','chain':'McDonald’s North & East India','sourceLanguage':'en','website':'https://mcdindia.com/','presenceUrl':'https://mcdindia.com/nutritional-information/','operator':'Connaught Plaza Restaurants Private Limited','scope':'North & East India only: Connaught Plaza Restaurants Private Limited. No West/South India franchise equivalence. This regional scope must remain visible on cards, finder rows, directories and country home.','presenceObservation':'Official nutrition page footer identifies Connaught Plaza Restaurants Private Limited as McDonald’s licensee in North & East India.','edition':None},
 'SG':{'name':'Singapore','continent':'Asia','currency':'SGD','flag':'🇸🇬','chain':'Burger King','sourceLanguage':'en','website':'https://burgerking.com.sg/','presenceUrl':'https://burgerking.com.sg/Locator','operator':None,'scope':'Burger King Singapore local menu. All nine linked category pages were captured; selected conflicting source rows withheld. Beverage 100ml reference entries remain reference amounts.','presenceObservation':'Official Singapore restaurant locator is available from the locally scoped menu site.','edition':None},
 'ZA':{'name':'South Africa','continent':'Africa','currency':'ZAR','flag':'🇿🇦','chain':'Debonairs Pizza','sourceLanguage':'en','website':'https://debonairspizza.co.za/','presenceUrl':'https://debonairspizza.co.za/nutritional-and-allergen-guide/','operator':None,'scope':'Debonairs Pizza South Africa official standard/halaal source guide. Source variants and named sizes preserved; identical nutritional variants merged. Local legal franchisees are not inferred.','presenceObservation':'Official South African site publishes its own standard and halaal menu nutrition guide and local location-directory links.','edition':None},
}
definitions={};presence=[]
for code,s in spec.items():
 selected=[r for r in rows if r['market']==code];rid=selected[0]['restaurantId'];base='/'+code.lower()+'/en/'
 definitions[code]={k:s[k] for k in ('name','continent','currency','flag')}
 definitions[code].update({'home':base,'finder':base+'find-a-meal/','restaurants':base+'restaurants/','collection':base+'collections/protein-meals/','chains':[s['chain']],'sourceLanguage':s['sourceLanguage'],'officialCountryWebsite':s['website'],'officialOperatorScope':s['scope'],'localOperatingEntity':s['operator'],'coverageLabel':'Reviewed named source selection','reviewedAt':'2026-10-17','recordCount':len(selected),'finderRecordCount':sum(r['finderSupported'] for r in selected),'sourceEdition':s['edition'],'translationsReviewed':False,'fullIngredientFormulasInferred':False})
 presence.append({'id':code+'|'+rid,'country':code,'restaurantBrand':s['chain'],'restaurantId':rid,'localOperatingEntity':s['operator'],'officialCountryWebsite':s['website'],'localMenuSource':s['website'],'presence':{'status':'confirmed','evidenceUrl':s['presenceUrl'],'evidenceType':'current official country or explicitly regional operating resource','observation':s['presenceObservation'],'checkedAt':'2026-10-17'},'nutritionSources':sorted({r['source'] for r in selected}),'lastCheckedDate':'2026-10-17','coverageStatus':'tracked-macro-selection','nutritionAvailable':True,'nutritionSourceStatus':'reviewed-selection','finderSupported':True,'trackedRecords':len(selected),'completeMacroRecords':sum(r['macroComplete'] for r in selected),'finderRecords':sum(r['finderSupported'] for r in selected),'calculatedOrders':0,'caloriesOnlyRecords':0,'partialMacroRecords':sum(not r['macroComplete'] for r in selected),'sourceRetrievalIsVerification':False,'limitations':s['scope']+' Source snapshots do not establish a complete live menu, stock at every branch, full ingredient formulation or allergen safety.'})
operator_file=D/'mcd-in-ne-index.html'
definitions['IN']['operatorEvidence']={'file':str(operator_file.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(operator_file.read_bytes()).hexdigest(),'url':spec['IN']['presenceUrl'],'sourceText':"Connaught Plaza Restaurants Private Limited (licensee of McDonald's in North & East India)"}
(ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-definitions.json').write_text(json.dumps(definitions,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-presence-upserts.json').write_text(json.dumps({'schemaVersion':1,'reviewedAt':'2026-10-17','relationships':presence},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def find(code,name):return next(r for r in rows if r['market']==code and r['name']==name)
briefs=[]
def brief(code,slug,title,names,paragraphs):
 selected=[find(code,n) for n in names]
 briefs.append({'market':code,'slug':slug,'title':title,'reviewedAt':'2026-10-17','scope':spec[code]['scope'],'paragraphs':paragraphs,'comparisonRows':[{k:r.get(k) for k in ('id','name','serving','servingGrams','servingMillilitres','cal','p','c','fat','f','na','sugar','sat','ingredientDescription','source','sourceDate','sourcePage','checked')} for r in selected],'calculations':[],'sources':sorted({r['source'] for r in selected}),'recordIds':[r['id'] for r in selected]})
brief('FR','quick-france-coca-cola-volumes-and-mega-giant','Quick France: match the drink volume to the menu entry',
 ['Coca Cola · 200 ml','Coca Cola · 500 ml','Méga Giant'],[
 'Quick France’s declaration valid from October 6, 2026 separates fountain drinks into 200 ml, 350 ml and 500 ml source portions. The French product names are preserved so that the local menu entry can be matched directly.',
 'The Coca Cola source serving is 84 kcal and 21 g carbohydrate at 200 ml, versus 210 kcal and 53 g carbohydrate at 500 ml. The larger source serving adds 126 kcal. These volumes do not become serving weights: 500 ml is not recorded as 500 g.',
 'A Méga Giant is a separate published burger portion at 859 kcal, 46 g protein, 38 g carbohydrate and 58 g fat. Adding the actually consumed Coca Cola serving gives 943 kcal with the 200 ml drink or 1,069 kcal with the 500 ml drink. Those sums do not include fries or a sauce.',
 'The guide reports salt, so sodium is a documented conversion from salt rather than a separately published sodium measurement. Less-than source salt values remain bounds; missing exact sodium is not replaced by zero. Source participating-restaurant and prepackaged-product markers still apply.'
 ])
briefs[-1]['calculations']=[{'expression':'Méga Giant + 200ml Coca Cola','cal':943},{'expression':'Méga Giant + 500ml Coca Cola','cal':1069},{'expression':'500ml minus 200ml Coca Cola','cal':126,'c':32}]
brief('IN','mcdonalds-north-east-india-veg-and-egg-mcmuffin','McDonald’s North & East India: Veg and Egg Mc Muffin',
 ['Veg Mc Muffin','Egg Mc Muffin'],[
 'This comparison covers the Connaught Plaza Restaurants Private Limited menu in North & East India. It does not apply automatically to the West or South India franchise menus. That operating-region label belongs with the food entry whenever it is searched, compared or saved.',
 'The local booklet lists a 119 g Veg Mc Muffin at 303.35 kcal, 10.22 g protein, 38.86 g carbohydrate and 11.78 g fat. The 112 g Egg Mc Muffin is 283.46 kcal, 14.05 g protein, 28.12 g carbohydrate and 12.31 g fat.',
 'For those exact named servings, Egg Mc Muffin has 19.89 fewer calories and 3.83 g more protein, while fat is 0.53 g higher. Sodium is 804.63 mg for Veg Mc Muffin and 519.31 mg for Egg Mc Muffin. The numbers compare complete listed items, not an isolated egg substitution.',
 'The current official page links the booklet, but the PDF supplies no whole-book edition date. Its December 2025 upload path is not treated as a publication or review date. Some pages retain older product-version labels, which are preserved. Fibre and unclear source macro fields are not filled with assumed zeroes.'
 ])
briefs[-1]['calculations']=[{'expression':'Egg minus Veg Mc Muffin','cal':-19.89,'p':3.83,'c':-10.74,'fat':0.53,'na':-285.32}]
brief('SG','burger-king-singapore-whopper-and-cheese','Burger King Singapore: Whopper and Whopper with Cheese',
 ['WHOPPER®','WHOPPER® with Cheese'],[
 'Burger King Singapore’s local menu publishes separate nutrition for WHOPPER and WHOPPER with Cheese. These are Singapore source recipes; a burger with the same brand name in another country is a separate record.',
 'WHOPPER is 625 kcal with 24 g protein, 54 g carbohydrate, 35 g fat and 1,400 mg sodium. WHOPPER with Cheese is 700 kcal with 29 g protein, 55 g carbohydrate, 40 g fat and 1,700 mg sodium. The published cheese version adds 75 kcal, 5 g protein, 5 g fat and 300 mg sodium.',
 'The official description names a beef patty, pickles, ketchup, tomato, lettuce, onion, mayonnaise and a sesame bun for WHOPPER. That is a useful menu description; it is not a full additive, supplier or allergen formulation. The comparison uses the two published builds and does not calculate a universal cheese-slice value from their difference.',
 'All nine linked local categories were captured. Two conflicting nutrition rows were withheld, and publication dates are unavailable. Some fountain beverages are explicitly reported per 100 ml: those references remain 100 ml entries and are excluded from complete-order matching until actual consumed volume is specified.'
 ])
briefs[-1]['calculations']=[{'expression':'WHOPPER with Cheese minus WHOPPER','cal':75,'p':5,'c':1,'fat':5,'na':300}]
brief('ZA','debonairs-south-africa-bbq-chicken-source-sizes','Debonairs South Africa: log the whole named pizza size',
 ['Real Deal® — BBQ Chicken · Small · standard / halaal','Real Deal® — BBQ Chicken · Medium · standard / halaal'],[
 'Debonairs Pizza South Africa’s local nutrition guide supplies separate whole named sizes. The selected Real Deal BBQ Chicken Small and Medium entries have the same published nutrition in its standard and halaal sections, so identical nutritional variants are merged with both source labels retained.',
 'The Small source portion is 26.54 g protein, 73.89 g carbohydrate, 13.07 g fat and 397.66 mg sodium. The Medium is 45.04 g protein, 110.83 g carbohydrate, 24 g fat and 603.71 mg sodium. These numbers describe each whole source-sized portion, not one slice.',
 'Source energy is in kilojoules. Dividing by 4.184 gives about 520.67 kcal for Small and 841.83 kcal for Medium. Calculated kcal is labelled as a unit conversion, while protein, carbs, fat and sodium remain source-reported. The Medium therefore adds about 321.15 kcal and 18.5 g protein.',
 'The table does not supply gram weights, saturated fat or sugar for these entries. Several other source panels repeat conflicting Small labels or contain implausible decimal values; they were withheld together without guessing which size or decimal was intended. A local stock, full ingredient-formula or allergen-safety claim is not inferred.'
 ])
a=find('ZA','Real Deal® — BBQ Chicken · Small · standard / halaal');z=find('ZA','Real Deal® — BBQ Chicken · Medium · standard / halaal')
briefs[-1]['calculations']=[{'expression':'Medium minus Small whole source portion',**{k:z[k]-a[k] for k in ('cal','p','c','fat','na')}}]
(D/'guide-briefs.json').write_text(json.dumps({'reviewedAt':'2026-10-17','briefs':briefs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'definitions':len(definitions),'presenceUpserts':len(presence),'guideBriefs':len(briefs),'rows':len(rows),'markets':B['marketCounts']}))
