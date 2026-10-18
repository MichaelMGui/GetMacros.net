"""Review the official Chick-fil-A CA/US menu snapshots without shared mutation.

The public WordPress nutrition store contains the same item/portion facts as the
server-rendered tables. Parent defaults are not imported twice when a specific
portion list is provided. Canadian breakfast is explicitly unavailable.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, re, unicodedata

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/flagship-release-2026-10-18/markets'
DATE = '2026-10-18'
FIELDS = {'Calories':'cal','Protein (g)':'p','Carbohydrates (g)':'c',
          'Fat (g)':'fat','Fiber (g)':'f','Sodium (mg)':'na',
          'Sugar (g)':'sugar','Sat. Fat (g)':'sat',
          'Trans Fat (g)':'trans','Cholesterol (mg)':'cholesterol'}

def clean(value):
    return ' '.join(str(value or '').split())

def norm(value):
    value=unicodedata.normalize('NFKD',clean(value)).casefold()
    return re.sub(r'[^a-z0-9]+','',value)

def scalar(value):
    if isinstance(value,(int,float)): return value
    text=clean(value)
    return float(text) if re.fullmatch(r'\d+(?:\.\d+)?',text) else None

def source_store(market):
    # lxml is needed only to regenerate a source import, not at application build.
    from lxml import html
    file=DOC/'sources'/('cfa-'+market.lower()+'-nutrition.html')
    tree=html.fromstring(file.read_bytes())
    store=json.loads(tree.xpath('//script[@id="wp-script-module-data-@wordpress/interactivity"]')[0].text)
    return store['state']['nutrition-allergens-table-store']['tableData']['nutrition'], file

def build():
    baseline=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
    additions=[];updates=[];withheld=[];sources=[];category_report=[]
    for market in ('CA','US'):
        groups,file=source_store(market)
        country_url='https://www.chick-fil-a.'+('ca' if market=='CA' else 'com')
        url=country_url+'/nutrition-allergens'
        source_hash=hashlib.sha256(file.read_bytes()).hexdigest()
        sources.append({'id':'cfa-'+market.lower()+'-nutrition','file':file.relative_to(ROOT).as_posix(),
          'url':url,'marketScope':market,'chain':'Chick-fil-A','sha256':source_hash,
          'retrievedAt':DATE,'verifiedAt':DATE,'sourceEdition':None,
          'captureMethod':'official public rendered table and embedded nutrition store',
          'retrievalIsVerification':False,
          'coverage':'all numeric named leaf portions in this identified nutrition snapshot; not every branch or real-time stock',
          'limitations':'No source publication date. Source portions, not inferred combo totals. Shared preparation is not an allergy guarantee. '+
           ('Canada does not serve breakfast; official FAQ reviewed separately.' if market=='CA' else 'Breakfast is time/location dependent. Limited-time sandwiches remain identified; no all-branch availability claim.')})
        slots={};families=defaultdict(set)
        for group in groups:
            g=group['menu'];observed=set();eligible=set()
            for parent in group['items']:
                family=str(parent['ID']);families[g].add(family)
                for item in parent['sub_items'] or [parent]:
                    key=str(item['ID']);observed.add(key)
                    values={clean(f['label']):f['value'] for f in item['fields']}
                    name=clean(item['title']);serving=clean(values.get('Serving Size'))
                    nutrients={target:scalar(values.get(label)) for label,target in FIELDS.items()}
                    if not name or not serving or any(nutrients[k] is None for k in ('cal','p','c','fat')):
                        withheld.append({'market':market,'sourceItemId':key,'name':name,'group':g,'reason':'missing exact serving or core nutrient','rawFields':values})
                        continue
                    eligible.add(key)
                    if key in slots:
                        before=slots[key]
                        assert before['nativeNutrients']==nutrients and before['sourceServing']==serving, (market,key)
                        if g not in before['sourceGroups']:before['sourceGroups'].append(g)
                        continue
                    category=('component' if any(x in g for x in ('Sauce','Dressing','Buns','Proteins','Toppings')) or parent['title']=='Breakfast Breads'
                              else 'drink' if g in ('Drinks','Coffee','Catering Drinks')
                              else 'dessert' if g=='Treats' else 'side' if g=='Sides' else 'entree')
                    grams=re.fullmatch(r'(\d+(?:\.\d+)?)g',serving)
                    grams=float(grams[1]) if grams else None
                    count=re.match(r'^(\d+) ct ',name)
                    portion=(''+count[1]+' count · ' if count else '')+serving+' · published serving'
                    size=next((x for x in ('Small','Medium','Large','Gallon') if name.startswith(x+' ')),'')
                    if size:portion=size+' · '+portion
                    row={'id':market+'|chick-fil-a|official-'+key,'chain':'Chick-fil-A',
                         'restaurantId':'chick-fil-a','restaurantMarketId':market+'|chick-fil-a',
                         'market':market,'country':market,'region':market,'language':'en',
                         'name':name,'serving':portion,'sourceServing':serving,'servingGrams':grams,'size':size,
                         'category':category,'meal':'breakfast' if g=='Breakfast' else 'main',
                         'diet':[],'components':[],**nutrients,'nativeNutrients':nutrients.copy(),
                         'source':url,'sourceItemUrl':item.get('link') or parent.get('link'),
                         'sourceItemId':key,'sourceProductFamily':family,'sourceGroups':[g],
                         'sourceGroup':g,'sourceDate':None,'retrievedAt':DATE,'checked':DATE,
                         'verificationStatus':'official-table-reviewed','sourceHash':source_hash,
                         'sourceCaptureMethod':'official public rendered table and embedded nutrition store',
                         'sourcePage':'nutrition/'+g+'/'+key,'nutrientBasis':'per named serving',
                         'units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g','trans':'g','cholesterol':'mg'},
                         'macroComplete':True,'finderSupported':category!='component' and size!='Gallon' and g not in ('Trays','Catering Entrées','Catering Drinks',"Kid's Meals (nutrition per entrée only)"),
                         'url':('/ca/en/restaurants/chick-fil-a/' if market=='CA' else '/chick-fil-a-healthy-meals-macros.html'),
                         'conversions':[],
                         'notes':'Official '+('Canadian' if market=='CA' else 'U.S.')+' named serving reviewed October 18, 2026. No publication date supplied. Includes only this listed item/build; sides, sauces and drinks are not added unless the source names them. '+
                          ('No Canadian breakfast service. ' if market=='CA' else ('Limited-time menu; confirm local availability. ' if 'Waffle' in name else ''))+
                          ('Nutrition per entrée only: not a complete kids’ meal. ' if g.startswith("Kid's Meals") else '')+
                          ('Catering quantity is the exact published serving, not a single-person portion. ' if 'Catering' in g or g=='Trays' else '')+
                          ('Salad topping/dressing assumptions follow the named source variant, not an invented substitution. ' if g=='Salads' else '')}
                    row['nutrientProvenance']={k:{'method':'official published serving','source':url,'sourceItemId':key,'verifiedAt':DATE,'edition':None} for k,v in nutrients.items() if v is not None}
                    row['t']=[tag for tag,yes in [('protein',row['p']>=25),('light',row['cal']<=400),('energy',row['cal']>=600),('fibre',row['f'] is not None and row['f']>=5),('lowsodium',row['na'] is not None and row['na']<=600)] if yes]
                    slots[key]=row
            category_report.append({'market':market,'restaurant':'Chick-fil-A','sourceGroup':g,'sourceProductFamilies':len(group['items']),'sourceNamedPortions':len(observed),'numericPortionsReviewed':len(eligible),'sourceUrl':url,'snapshot':source_hash,'sourceEdition':None,'status':'numeric leaf portions reviewed','limitations':'Snapshot scope only; categories may overlap and counts must not be summed as distinct products.'})
        distinct={}
        for row in slots.values():
            identity=(norm(row['name']),row['sourceServing'],tuple(row['nativeNutrients'].items()))
            if identity in distinct:
                distinct[identity].setdefault('sourceItemAliases',[]).append(row['sourceItemId'])
                continue
            distinct[identity]=row
        for row in distinct.values():
            if market=='CA' and row['name']=='Buddy Fruits® Multifruit':
                row['sourceReportedServingGrams']=row['servingGrams']
                row['servingGrams']=None
                row['serving']='1 named Multifruit pouch; published mass conflict (90 g / 100 g)'
                row['sourceServing']='1 named Multifruit pouch'
                row['portionVerificationStatus']='conflicting official mass descriptions'
                row['portionConflict']={'nutritionTableGrams':100,'productDescriptionGrams':90,'productUrl':'https://www.chick-fil-a.ca/menu/sides/buddy-fruits-multifruit','checkedAt':DATE}
                row['notes']+='Official product description says 90 g, while nutrition table says 100 g. Nutrients are the named per-container published values, not values rescaled between weights. Actual mass remains unresolved. '
            if 'Breakfast' in row['sourceGroups']:row['meal']='breakfast'
            row['sourceGroup']=' / '.join(row['sourceGroups'])
            matches=[x for x in baseline if x['market']==market and x['chain']=='Chick-fil-A' and norm(x['name'])==norm(row['name']) and (x.get('servingGrams') is None or x.get('servingGrams')==row['servingGrams']) and x.get('verificationStatus')!='calculated-from-official-components']
            # Some legacy custom variants have no exact source identity. Never merge
            # different builds just because calories happen to match.
            if len(matches)==1:
                row['id']=matches[0]['id'];updates.append(row)
            elif len(matches)>1:
                withheld.append({'market':market,'name':row['name'],'reason':'ambiguous legacy identity; integration must resolve explicitly','matches':[x['id'] for x in matches]})
                continue
            else:additions.append(row)
            row['sourceVersion']=hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
        # Demonstrably unsupported category, not a placeholder imported from U.S.
        if market=='CA':category_report.append({'market':'CA','restaurant':'Chick-fil-A','sourceGroup':'Breakfast','sourceProductFamilies':0,'sourceNamedPortions':0,'numericPortionsReviewed':0,'sourceUrl':country_url+'/customer-support/our-restaurants/hours-of-operation/are-chick-fil-a-restaurants-in-canada-open-for-breakfast','status':'not offered according to official Canadian FAQ','limitations':'No U.S. breakfast nutrition substituted.'})
    from markets_chipotle import stage as stage_chipotle, compose_reviewed_orders
    chip_rows,chip_source,chip_categories=stage_chipotle()
    additions.extend(chip_rows);sources.append(chip_source);category_report.extend(chip_categories)
    orders=compose_reviewed_orders(additions+updates)
    withheld.append({'market':'CA','chain':'Chick-fil-A','name':'Grilled sandwich, Multifruit & small unsweet tea','reason':'Exact fruit-pouch mass conflicts between official product description (90 g) and nutrition table (100 g); composed order withheld pending reconciliation.','sources':['https://www.chick-fil-a.ca/nutrition-allergens','https://www.chick-fil-a.ca/menu/sides/buddy-fruits-multifruit']})
    additions.extend(orders)
    batch={'schemaVersion':1,'reviewedAt':DATE,'records':additions,'updates':updates,
           'newCounts':dict(Counter(r['market'] for r in additions)),
           'updateCounts':dict(Counter(r['market'] for r in updates)),
           'counts':{'newPortionRecords':len(additions)-len(orders),'updatedPortionRecords':len(updates),'calculatedOrders':len(orders),
                    'newSourceProductFamilies':len({(r['market'],r['chain'],r['sourceProductFamily']) for r in additions if 'sourceProductFamily' in r}-{(r['market'],r['chain'],r['sourceProductFamily']) for r in updates}),
                    'allReviewedSourceProductFamilies':len({(r['market'],r['chain'],r['sourceProductFamily']) for r in additions+updates if 'sourceProductFamily' in r})},
           'scope':'Reviewed exact official named portions from identified CA/US nutrition snapshots. Product-family and portion counts differ. No combo total inferred.'}
    target=ROOT/'tools/flagship_release/markets_records.json'
    target.write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,data in [('source-register.json',sources),('category-completeness.json',category_report),('withheld.json',withheld)]:
        (DOC/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in batch.items() if k not in ('records','updates')},indent=2))
    return batch

def integrate(registry):
    """Pure integration callable: caller owns shared files and recomputed indices."""
    batch=json.loads((ROOT/'tools/flagship_release/markets_records.json').read_text(encoding='utf-8'))
    updates={r['id']:r for r in batch['updates']}
    rows=registry['records'] if isinstance(registry,dict) else registry
    known={r.get('id') for r in rows}
    missing=set(updates)-known
    if missing:raise ValueError('Cannot refresh unknown source IDs: '+', '.join(sorted(missing)))
    result=[updates.get(r.get('id'),r) for r in rows]
    by_id={r['id']:r for r in result}
    for r in batch['records']:
        if r['id'] in by_id:
            if by_id[r['id']]!=r:raise ValueError('ID collision: '+r['id'])
        else:result.append(r);by_id[r['id']]=r
    if isinstance(registry,dict):return {**registry,'records':result}
    return result

if __name__=='__main__':build()
