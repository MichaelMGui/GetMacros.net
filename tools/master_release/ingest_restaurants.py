"""Reproducible imports from visually reviewed, official Canadian source snapshots.

This research command needs pdfplumber. Production consumes its pinned JSON output;
it never downloads a mutable menu during a build. No cross-country substitutions.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,re
import pdfplumber

ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'docs/master-release-2026-10-12/sources'
OUT=ROOT/'tools/master_release'
DATE='2026-10-12'
retrieval={r['file']:r for r in json.loads((S/'restaurant-retrieval.json').read_text(encoding='utf-8')) if 'sha256' in r}
records=[];issues=[]
CORE=['cal','p','c','fat'];FIELDS=CORE+['f','na','sugar','sat']
UNITS={'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g'}

def num(s):
 s=str(s or '').strip()
 return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(chain,name,serving,values,file,edition,page,category='entree',grams=None,components=(),notes='',**extra):
 ev=retrieval[file];assert digest(S/file)==ev['sha256']
 identity='CA|'+slug(chain)+'|'+hashlib.sha256((name+'|'+serving).encode()).hexdigest()[:16]
 nutrients={k:values.get(k) for k in FIELDS}
 r={'id':identity,'chain':chain,'restaurantId':slug(chain),'restaurantMarketId':'CA|'+slug(chain),'name':name,'country':'CA','market':'CA','region':'CA','language':'en','serving':serving,'servingGrams':grams,'category':category,'meal':'breakfast' if category=='breakfast' else 'main','size':'','diet':[],'t':[],**nutrients,'components':[{'item':c,'quantity':None} for c in components],'source':ev.get('finalUrl') or ev['url'],'sourceDate':edition,'retrievedAt':DATE,'checked':DATE,'verificationStatus':'official-table-reviewed','sourcePage':page,'sourceHash':ev['sha256'],'nativeNutrients':values.copy(),'nutrientBasis':'per named source serving','units':UNITS,'conversions':[],'notes':notes,'url':'/ca/en/restaurants/'+slug(chain)+'/','sourceDateProvenance':'printed source edition' if edition else 'no publication date supplied'}
 r.update(extra)
 r['macroComplete']=all(r[k] is not None for k in CORE)
 r['finderSupported']=r['macroComplete'] and category not in ['component','sauce']
 r['nutrientProvenance']={k:{'method':'official published serving','source':r['source'],'page':page,'edition':edition,'verifiedAt':DATE} for k,v in nutrients.items() if v is not None}
 for tag,k,test in [('protein','p',lambda x:x>=25),('light','cal',lambda x:x<=400),('energy','cal',lambda x:x>=600),('fibre','f',lambda x:x>=5),('lowsodium','na',lambda x:x<=600)]:
  if r[k] is not None and test(r[k]):r['t'].append(tag)
 records.append(r);return r

# Subway: preserve the printed category in the identity. Fresh Fit and Classics
# with the same protein name have different builds and must not be deduplicated.
group='';components=[];category='entree'
for pg in json.loads((S/'subway-ca-extracted.json').read_text(encoding='utf-8'))[:2]:
 for table in pg['tables']:
  for cells in table:
   if len(cells)!=14:continue
   if num(cells[1]) is None:
    label=' '.join(str(cells[0] or '').split())
    if label.startswith('BREADS &'):group='components';continue
    if group=='components':continue
    if label.startswith('6"') and 'Subs' in label:group=label.split(' Double')[0];components=[];category='entree'
    elif label.startswith('6" Fresh Fit'):group='6-inch Fresh Fit';components=[];category='entree'
    elif label.startswith('Snackwiches'):group='Snackwich';components=['Ciabatta','Select vegetables; varieties not fully specified','Sauce indicated by item name'];category='entree'
    elif label.startswith('Classics Wraps'):group='Classics wrap';components=['Wrap','Processed Cheddar','Mayonnaise','Lettuce','Tomato','Onion','Cucumber'];category='entree'
    elif label=='SALADS':group='Salad';components=['Lettuce','Spinach','Tomatoes','Onions','Green peppers','Cucumbers','Olives'];category='entree'
    elif label.startswith('6" Limited'):group='Regional salad';category='entree'
    elif label=='Power Bowls':group='Power bowl';components=[];category='entree'
    elif '6" Breakfast Sandwiches' in label:group='6-inch breakfast sandwich';components=['6-inch Italian bread','Scrambled egg patty','Canadian cheddar cheese'];category='breakfast'
    elif label.startswith('Breakfast Wraps'):group='Breakfast wrap';components=['Wrap','Scrambled egg patty','Canadian cheddar cheese'];category='breakfast'
    elif label.startswith('Breakfast Ciabatta'):group='Breakfast ciabatta';components=['Ciabatta','Scrambled egg patty','Canadian cheddar cheese'];category='breakfast'
    continue
   if group=='components' or not group:continue
   n={k:num(cells[i]) for k,i in {'cal':2,'fat':3,'sat':4,'na':7,'c':8,'f':9,'sugar':10,'p':11}.items()}
   assert all(n[k] is not None for k in CORE)
   note='June 2026 Canadian table, linked by the official Canadian nutrition page on October 12. Listed standard recipe; extras are not added. No equivalence to another country is assumed.'
   if 'salad' in group.lower():note+=' Dressing is excluded unless the item name says otherwise.'
   if group.startswith('6'):note+=' One footlong is two source 6-inch servings, as specified by Subway.'
   if group=='Regional salad':note+=' Source labels this a limited-time/regional offering; local availability is not guaranteed.'
   included=components
   if str(cells[0])=='Sausage & Cheese' and category=='breakfast':
    included=[];note+=' The group note mentions egg while this item name does not; ingredient inclusion is not inferred for this entry.'
   r=add('Subway',group+' — '+str(cells[0]),'1 '+group.lower()+' · '+str(cells[1])+' g',n,'subway-ca.pdf','2026-06',pg['page'],category,num(cells[1]),included,notes=note)
   if r['name']=='6-inch Fresh Fit — Rotisserie-Style Chicken':
    r['components']=[{'item':x,'quantity':None} for x in ['Multigrain bread','Rotisserie-style chicken','Canadian cheddar cheese','Lettuce','Spinach','Tomatoes','Cucumbers','Green peppers','Onions','Mayonnaise']]
    r['componentSource']='https://www.subway.com/en-ca/restaurant/71870-0/customizer/productsummary/15328/category/sandwiches'
    r['componentVerification']='Named standard build displayed by official Canadian item page, retrieved October 12, 2026; not full ingredient formulation or allergen certification.'

# Domino's: only the visually inspected SMALL HAND-TOSSED page is used.
# Source differentiates cheese-only quantities from cheese with other toppings.
pg=json.loads((S/'dominos-ca-extracted.json').read_text(encoding='utf-8'))[4]
group='';component_map={}
for cells in pg['tables'][0]:
 if len(cells)!=14 or num(cells[2]) is None:continue
 if cells[0]:group=' '.join(cells[0].split())
 label=group+' — '+cells[1]
 n={k:num(cells[i]) for k,i in {'cal':3,'fat':5,'sat':6,'na':9,'c':10,'f':11,'sugar':12,'p':13}.items()}
 r=add('Domino’s',label,'Component amount for 1/6 of a small hand-tossed pizza · '+cells[2]+' g',n,'dominos-ca.pdf','2025-08',5,'component',num(cells[2]),notes='August 2025 Canadian guide currently served by Domino’s Canada. Small hand-tossed pizza component only; not a complete slice. Amounts depend on pizza size and topping count. Rounded published components are not laboratory measurements.',builderScope='CA|dominos|small-hand-tossed|one-sixth',sourceGroup=group,sourceItem=cells[1])
 component_map[(group,cells[1])]=r

def build_pizza(title,keys):
 rows=[component_map[k] for k in keys]
 v={k:sum(r[k] for r in rows) if all(r[k] is not None for r in rows) else None for k in FIELDS}
 r=add('Domino’s',title,'1 slice = 1/6 of a small hand-tossed pizza',v,'dominos-ca.pdf','2025-08',5,grams=sum(r['servingGrams'] for r in rows),components=[r['sourceItem'] for r in rows],notes='GetMacros sums the rounded Canadian component values for this exact small hand-tossed build. One slice is 1/6 of the pizza. No extra toppings or sides. Actual prepared portions can vary.',verificationStatus='calculated-from-official-components',calculatedFrom=[{'id':r['id'],'quantity':1} for r in rows],calculation='Sum of named published component amounts for one-sixth of small pizza')
 r['nutrientProvenance']={k:{'method':'sum of official component values','source':r['source'],'page':5,'componentIds':[x['id'] for x in rows],'verifiedAt':DATE} for k in FIELDS}
build_pizza('Small hand-tossed cheese pizza — 1 slice',[('Crust','Hand Tossed - serving size is 1/6 of pizza'),('Sauce','Pizza Sauce'),('Cheese Only Pizza','Regular Cheese')])
build_pizza('Small hand-tossed pepperoni pizza — 1 slice',[('Crust','Hand Tossed - serving size is 1/6 of pizza'),('Sauce','Pizza Sauce'),('Cheese Pizza Along with other toppings','Regular Cheese'),('1-Topping Pizza Additional toppings will change nutrition values','Pepperoni')])
build_pizza('Small hand-tossed chicken pizza — 1 slice',[('Crust','Hand Tossed - serving size is 1/6 of pizza'),('Sauce','Pizza Sauce'),('Cheese Pizza Along with other toppings','Regular Cheese'),('1-Topping Pizza Additional toppings will change nutrition values','Chicken')])

# Mary Brown's July file is the current menu's actual download link. Multi-serving
# buckets/large sides have unclear denominator and are excluded, not guessed.
pg=json.loads((S/'marybrowns-july2026-extracted.json').read_text(encoding='utf-8'))[0]
group=''
for cells in pg['tables'][0]:
 if len(cells)!=13:continue
 if num(cells[2]) is None:
  if cells[0] and all(x is None for x in cells[1:]):group=cells[0]
  continue
 name=' '.join(cells[0].split());portion=' '.join(str(cells[1] or '').split())
 v={k:num(cells[i]) for k,i in {'cal':3,'fat':4,'sat':5,'na':8,'c':9,'f':10,'sugar':11,'p':12}.items()}
 reason=None
 if v['fat'] is not None and v['fat']>num(cells[2]):reason='Published fat exceeds source serving mass; no correction guessed'
 elif re.search(r'\b(?:2|4|6|9|14) servings\b',portion):reason='Multi-serving order denominator unresolved'
 elif v['na'] is not None and v['na']>5000:reason='Unusually high source sodium; held for clarification'
 elif not all(v[k] is not None for k in CORE):reason='Unresolved numeric row'
 if reason:issues.append({'chain':'Mary Brown’s','name':name,'reason':reason,'sourcePage':1});continue
 cat='side' if group=='SIDES' else 'sauce' if group=='SAUCES' else 'entree'
 if name.startswith(('2 PC','3 PC')) and group=='CHICKEN':name+=' — chicken only'
 add('Mary Brown’s',name,portion+' · '+cells[2]+' g',v,'marybrowns-july2026.pdf','2026-07',1,cat,num(cells[2]),notes='July 2026 file linked by the current Canadian menu. Listed item or chicken pieces only; combo sides, drinks and dipping sauces are separate. Exact multi-serving buckets and large-side totals are withheld where the serving denominator is unclear.',sourceDateProvenance='edition from filename linked by official menu')

# Booster Juice: line extraction is calibrated against rendered pages 1–2.
# Table extraction drops alternating product names, so never forward-fill those.
pattern=re.compile(r'^(.+?)\s+(\d+)\s+m[Ll]\s+((?:\d+(?:\.\d+)?\s+){13}\d+(?:\.\d+)?)\s*$')
with pdfplumber.open(S/'booster-sept2026.pdf') as pdf:
 for pi,page in enumerate(pdf.pages[:2]):
  for line in page.extract_text(x_tolerance=1).splitlines():
   m=pattern.match(line)
   if not m:continue
   name=m[1];values=[float(x) for x in m[3].split()];assert len(values)==14
   v=dict(zip(['cal','fat','sat','trans','p','c','f','sugar','chol','na','potassium','calcium','iron','caffeine'],values))
   vol=int(m[2]);size='regular' if name.endswith('(R)') else 'snack' if name.endswith('(S)') else 'listed'
   r=add('Booster Juice',name,'1 '+size+' drink · '+str(vol)+' mL',v,'booster-sept2026.pdf','2026-09',pi+1,'drink',notes='September 2026 Canadian nutrition guide. Named regular/snack recipe, not a guessed customization. Millilitres are volume; no gram weight or density is assumed. Sugar is total sugar; added sugar is not provided.',servingMillilitres=vol)
   r['additionalNutrients']={k:{'value':v[k],'unit':'mg','method':'official reported serving'} for k in ['potassium','calcium','iron','caffeine','chol']}

# Pizza Pizza: use SMALL rows only. Exact source's missing decimals in saturated
# fat are contradictory to total fat; retain source text and set sat unknown.
for cells in json.loads((S/'pizza-pizza-small-tables.json').read_text(encoding='utf-8')):
 if len(cells)!=20 or cells[:2]!=['Pizza','Small'] or num(cells[6]) is None:continue
 v={k:num(cells[i]) for k,i in {'cal':6,'p':7,'c':8,'f':9,'sugar':10,'fat':11,'sat':12,'na':15}.items()}
 if not all(v[k] is not None for k in CORE):continue
 problem=v['sat'] is not None and v['sat']>v['fat']
 rawsat=v['sat']
 if problem:v['sat']=None;issues.append({'chain':'Pizza Pizza','name':cells[2],'reason':'Source saturated-fat text exceeds total fat; held as unknown, not decimal-corrected','rawSaturatedFat':rawsat})
 edition='2026-03-12' if 'March 12, 2026' in cells[19] else None
 r=add('Pizza Pizza','Small '+cells[2]+' — 1 slice','1 slice = 1/6 of a 10-inch small pizza',v,'pizza-pizza-small.html',edition,None,notes='Current Canadian small-pizza table: one slice is 1/6 of a 10-inch pizza. This is not a walk-in slice or another pizza size. Blank rows are not imported. Source does not supply gram weights; current local availability is not guaranteed.'+(' Saturated-fat field conflicts with total fat in the source and is withheld.' if problem else ''))
 if problem:r['sourceIssues']=[{'field':'sat','rawValue':rawsat,'reason':'source contradiction'}]

# Pizza Nova: ONLY the explicitly labelled IN-STORE 1 SLICE entries. Signature
# size tables lack an explicit denominator in the retrieved interface.
render=S/'pizza-nova-rendered.html';renderhash=digest(render)
retrieval['pizza-nova-rendered.html']={'url':'https://pizzanova.com/nutrition','sha256':renderhash,'retrieved':DATE}
for text in json.loads((S/'pizza-nova-instore.json').read_text(encoding='utf-8')):
 m=re.fullmatch(r'IN-STORE SLICES (.+) Calories: (\d+) Serving Size : 1 SLICE',text)
 assert m,text
 add('Pizza Nova',m[1].title()+' — in-store slice','1 in-store slice; gram weight not provided',{'cal':float(m[2])},'pizza-nova-rendered.html',None,None,notes='Official Canadian in-store slice calorie listing. Protein, carbohydrate, fat, fibre, sodium, weight and complete ingredient formulation are not supplied. Not interchangeable with a made-to-order signature pizza slice.',verificationStatus='official-calories-only',finderSupported=False)

assert len({r['id'] for r in records})==len(records)
for r in records:r['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
report={'schemaVersion':1,'retrievedAt':DATE,'reviewedAt':DATE,'scope':'Selected official Canadian source servings; not an audited full live menu or independent laboratory verification.','sourceTables':retrieval,'records':records,'issues':issues,'counts':{'total':len(records),'byChain':dict(Counter(r['chain'] for r in records)),'completeMacros':sum(r['macroComplete'] for r in records),'calculatedOrders':sum(r['verificationStatus']=='calculated-from-official-components' for r in records),'caloriesOnly':sum(r['verificationStatus']=='official-calories-only' for r in records)}}
(OUT/'restaurant_records.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
(ROOT/'docs/master-release-2026-10-12/restaurant-import-review.json').write_text(json.dumps({'counts':report['counts'],'issues':issues},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(report['counts'],indent=2))
