"""Reproducible UK-only nutrition staging from the captured official sources.

This module never writes the shared registry or generated public pages.  Retrieving
a source is not verification; each adapter has explicit serving and unit rules.
"""
from pathlib import Path
import collections, hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/flagship-release-2026-10-18/uk'
SRC = DOC / 'sources'
DATE = '2026-10-18'
FIELDS = ('cal', 'p', 'c', 'fat', 'f', 'na', 'sugar', 'sat')
records, withheld, sources, inventory = [], [], {}, []
retrieval = {x['file']: x for x in json.loads((SRC/'retrieval.json').read_text(encoding='utf-8'))}

def read(name):
    return json.loads((SRC/name).read_text(encoding='utf-8'))

def clean(value):
    return ' '.join(str(value or '').replace('\u200d','').split())

def number(value):
    if isinstance(value, (float, int)) and not isinstance(value, bool): return float(value)
    value = clean(value).replace(',', '')
    return float(value) if re.fullmatch(r'\d+(?:\.\d+)?', value) else None

def slug(value):
    known={"Nando’s":'nandos',"Wendy’s":'wendys',"Pepe’s":'pepes','Caffè Nero':'caffe-nero'}
    return known.get(value) or re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def source(name, chain, edition, method, limitations):
    row = retrieval[name]
    assert row.get('status') == 200 and row.get('sha256'), (name, row)
    assert hashlib.sha256((SRC/name).read_bytes()).hexdigest() == row['sha256']
    value = dict(file=str((SRC/name).relative_to(ROOT)).replace('\\','/'), url=row['url'],
        sha256=row['sha256'], chain=chain, marketScope='GB', sourceEdition=edition,
        retrievedAt=row['retrievedAt'], verifiedAt=DATE, captureMethod=method,
        limitations=limitations, retrievalIsVerification=False)
    sources[name] = value
    return value

def add(chain, name, serving, values, src, page, category='entree', grams=None,
        group='', notes='', meal='main', identity='', scope='', extra=None):
    values = {k: values.get(k) for k in (*FIELDS, 'salt', 'kJ')}
    if any(v is not None and (not isinstance(v,(int,float)) or v < 0) for v in values.values()):
        raise ValueError((chain,name,values))
    complete = all(values[k] is not None for k in ('cal','p','c','fat'))
    if not complete:
        withheld.append(dict(chain=chain,name=name,source=src['url'],sourcePage=page,
            reason='One or more core macro values are unavailable; no zero inferred', values=values)); return
    energy = 4*values['p']+4*values['c']+9*values['fat']
    if values['cal'] > 10000 or abs(values['cal']-energy) > max(70,.25*values['cal']):
        withheld.append(dict(chain=chain,name=name,source=src['url'],sourcePage=page,
            reason='Large energy/macronutrient discrepancy; source not silently corrected', values=values, screeningEnergy=energy)); return
    if grams and sum(values[k] for k in ('p','c','fat')) > grams+max(5,.05*grams):
        withheld.append(dict(chain=chain,name=name,source=src['url'],sourcePage=page,
            reason='Published portion mass contradicts macro mass', values=values, servingGrams=grams)); return
    native = dict(values)
    conversions=[]
    if values['na'] is None and values['salt'] is not None:
        values['na'] = round(values['salt']*400,8)
        conversions.append(dict(from_='salt',fromUnit='g',to='na',toUnit='mg',formula='salt (g) × 1000 ÷ 2.5',method='salt-equivalent conversion; not source-reported sodium'))
        conversions[-1]['from']=conversions[-1].pop('from_')
    identifier='GB|'+slug(chain)+'|'+hashlib.sha256((identity or name+'|'+serving+'|'+scope).encode()).hexdigest()[:16]
    row=dict(id=identifier,chain=chain,restaurantId=slug(chain),restaurantMarketId='GB|'+slug(chain),
        name=clean(name),market='GB',country='GB',region='GB',language='en',serving=serving,
        servingGrams=grams,category=category,meal=meal,size='',diet=[],components=[],
        **{k:values[k] for k in FIELDS},source=src['url'],sourceDate=src['sourceEdition'],
        retrievedAt=src['retrievedAt'],checked=DATE,verificationStatus='official-table-reviewed',
        sourcePage=page,sourceHash=src['sha256'],sourceCaptureMethod=src['captureMethod'],
        nativeNutrients=native,nutrientBasis='per named serving',
        units=dict(cal='kcal',p='g',c='g',fat='g',f='g',na='mg',sugar='g',sat='g'),
        notes=notes,conversions=conversions,macroComplete=True,finderSupported=category!='component',
        sourceGroup=group,url='/gb/en/restaurants/'+slug(chain)+'/',availabilityScope=scope or 'UK source-listed item; check restaurant availability')
    row['nutrientProvenance']={k:dict(method='salt-equivalent conversion' if k=='na' and conversions else 'official published serving',source=src['url'],page=page,edition=src['sourceEdition'],verifiedAt=DATE) for k in FIELDS if values[k] is not None}
    row['t']=[t for t,yes in [('protein',values['p']>=25),('light',values['cal']<=400),('energy',values['cal']>=600),('fibre',values['f'] is not None and values['f']>=5),('lowsodium',values['na'] is not None and values['na']<=600)] if yes]
    if extra: row.update(extra)
    row['sourceVersion']=hashlib.sha256(json.dumps(row,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    records.append(row)
    return row

def nandos():
    src=source('nandos-data.json',"Nando’s",None,'official live menu page-data JSON, units/side-size mapping checked against linked UI component',
        'Base named dishes only. Modifier deltas not standalone meals. Regional and Gatwick restrictions retained. Source lists no gram weights. Bundle choices without a fixed combined total and alcoholic drinks withheld.')
    data=read('nandos-data.json')['result']['data']['nandos']['menu']
    # The linked production UI explicitly labels facts[0] Regular, facts[1] Large.
    proof=(SRC/'nandos-component.js').read_text(encoding='utf-8')
    assert 'null,"Regular"' in proof and 'null,"Large"' in proof and 'nutritionalFacts:t[1]' in proof
    seen={}
    for section in data['sections']:
        group=section['displayName']; total=0
        for item in section['items']:
            facts=item['nutritionalInfo']['factsForPortionSizes']
            if item.get('ageRestricted') or any((a.get('alcoholByVolumePercent') or 0)>0 for a in facts):
                withheld.append(dict(chain="Nando’s",name=item['displayName'],reason='Alcoholic drink outside meal discovery scope',source=src['url']));continue
            if section['kind'] in ('BUNDLES','PLATTERS') or group=='Sharing Platters' or 'Meal' in item['displayName'] and group=='Flying Solo':
                withheld.append(dict(chain="Nando’s",name=item['displayName'],reason='Bundle choice contains unspecified side/drink; source base total is not a complete order',source=src['url']));continue
            if not facts:
                withheld.append(dict(chain="Nando’s",name=item['displayName'],reason='No fixed portion nutrition in source',source=src['url']));continue
            # An item offered under multiple pricing groups is not another food.
            scope=item.get('restaurantGroup') or ''
            if scope in ('Regional pricing trial 26','Tiered Menu pricing trial'):scope=''
            for i,fact in enumerate(facts):
                name=item['displayName']+(' · '+('Regular' if i==0 else 'Large') if len(facts)==2 else '')
                key=(name,scope,tuple(sorted(fact.items())))
                if key in seen:continue
                seen[key]=True
                if scope:name+=' · '+scope
                vals={k:fact.get(native)/1000 if fact.get(native) is not None else None for k,native in dict(p='proteinMg',c='totalCarbsMg',fat='fatMg',f='fibreMg',sugar='sugarsMg',sat='saturatesMg',salt='saltMg').items()}
                vals.update(cal=fact.get('energyKcal'),kJ=fact.get('energyKj'))
                category='component' if group in ('Dips & Extras','Extras') else 'side' if group in ('Sides','Starters') else 'drink' if group=='Drinks' else 'dessert' if group in ('Desserts','Sweet Treats') else 'entree'
                portion='1 named source portion'+(' · '+('Regular' if i==0 else 'Large') if len(facts)==2 else '')
                if item.get('servingInfo') and (len(facts)==1 or i==1):portion+=' · '+item['servingInfo']
                note='UK live menu snapshot. Named dish only: no optional spices, sides or extras added. Salt converted to sodium. No source gram weight supplied.'
                row=add("Nando’s",name,portion,vals,src,item['id']+'#facts-'+str(i),category,group=group,notes=note,
                    meal='breakfast' if group in ('The Classics','Breakfast Rolls','Eggs','The Works') else 'main',scope=scope,
                    extra=dict(productId=item['id'],productUrl='https://www.nandos.co.uk/food/menu/#'+item['slug'],sourceMessages=item['nutritionalInfo']['messages'],sourceServingInfo=item.get('servingInfo'),sourceAllergens=item.get('allergens',[])))
                if row:total+=1
        inventory.append(dict(chain="Nando’s",category=group,sourceItems=len(section['items']),stagedRecords=total,scope='Base named dishes; pricing duplicates merged; regional restrictions retained'))

def leon():
    src=source('leon.html','LEON',None,'official server-rendered menu item data, per-portion field labels verified on official item page',
        'Published named UK menu items only. Package sizes and national availability not inferred. Items missing core macros withheld.')
    data=read('leon-products.json');seen=set();counts=collections.Counter()
    for item in data:
        if item['_id'] in seen:continue
        seen.add(item['_id']);info=item.get('nutritionInfo') or {};group=(item.get('submenuType') or {}).get('name') or 'Uncategorized'
        vals={k:number(info.get(native)) for k,native in dict(cal='kcal',p='protein',c='carb',fat='fat',f='fibre',sugar='sugar',sat='satFat',salt='salt').items()}
        grams=number(info.get('totalPortionWeight'))
        menu=(item.get('menuType') or {}).get('name','')
        category='component' if group=='Sauces' else 'side' if group in ('Fries','Sides','Breakfast Sides') else 'drink' if group in ('Coffee','Oat Milk Coffee','Juices & Cans','Functional Drinks','Smoothies') else 'dessert' if group in ('Cakes','Pastries','Yoghurts','Snacks') else 'entree'
        ingredients=' '.join(child.get('text','') for block in item.get('ingredients',[]) for child in block.get('children',[]))
        row=add('LEON',item['name'],'1 named source portion'+(' · '+str(grams).removesuffix('.0')+' g' if grams else ''),vals,src,item['_id'],category,grams,group,
            'UK published menu recipe, no extras added. Salt converted to sodium; zero retained only where explicitly published. Menu time: '+menu,
            meal='breakfast' if 'Breakfast' in menu else 'main',extra=dict(productId=item['_id'],productUrl='https://leon.co/menu/'+item['slug']+'/',ingredientDescription=clean(ingredients),sourceDaypart=menu))
        if row:counts[group]+=1
    for group,total in counts.items():inventory.append(dict(chain='LEON',category=group,stagedRecords=total,scope='Distinct published recipes; missing core macros withheld'))

def wagamama():
    src=source('wagamama.html','Wagamama','2026-10-07','official menu embedded nutrition-service records, named serving/size and nutrient unit labels retained; unrelated request geolocation redacted',
        'Public UK nutrition service snapshot. Source modification timestamps are not publication dates. Sodium source reports grams, explicitly converted to mg. No gram mass inferred from rounded per-100g values.')
    menu=read('wagamama-menu.json')['Menus'][0]
    assert menu['Name']=='07/10/2026 - UK - main website'
    def items(section,parents):
        for item in section.get('Recipes',[]):yield item,parents
        for child in section.get('Sections',[]):yield from items(child,parents+[child['Name']])
    for item,path in items(menu,[]):
        for size in item['Sizes']:
            code=size['Code'];rows=[a for a in item['Nutrs'] if a.get('RSCode') in (code,None,'')]; lookup={a['Desc'].lower():a for a in rows}
            names={'cal':'energy (kcal)','kJ':'energy (kj)','p':'protein (g)','c':'carb (g)','fat':'fat (g)','sat':'sat fat (g)','sugar':'of which sugars (g)','f':'fibre (g)','salt':'salt (g)'}
            vals={k:number(lookup.get(label,{}).get('PerServ')) for k,label in names.items()}
            sodium=number(lookup.get('sodium (g)',{}).get('PerServ'))
            if sodium is not None:vals['na']=sodium*1000
            name=clean(item['Name']);portion='1 '+clean(size['Name']).lower()+' source serving · '+clean(size['Size'])+' '+clean(size['Uom1'])
            if path and path[0]=='gluten free':name+=' · Gluten-free menu'
            if path and path[0]=='kids':name+=' · Kids menu'
            if len(item['Sizes'])>1:name+=' · '+size['Name']
            group=' / '.join(path)
            category='drink' if path[0]=='drinks' or 'drinks' in path else 'dessert' if path[0]=='desserts + sweet treats' or 'desserts' in path else 'component' if path[0]=='extras' else 'side' if path[0]=='sides' else 'entree'
            row=add('Wagamama',name,portion,vals,src,item['Ident']+'|'+code,category,group=group,notes='Named UK source serving, no side or drink added. Per-100g reference is retained separately. Source sodium grams converted to mg; independently rounded salt may differ. Source modification time is not a publication or fresh verification date. A gluten-free source-menu label is not an allergy guarantee.',extra=dict(productId=item['Ident'],ingredientDescription=item.get('Desc',''),sourceRecipeName=item.get('OrigName'),sourceRecipeModified=item.get('Modified'),sourceSize=size,nativePer100g={a['Desc']:a['Per100g'] for a in rows}))
            if row and sodium is not None:
                row['conversions'].append(dict(from_='sodium',fromUnit='g',to='na',toUnit='mg',formula='sodium (g) × 1000',method='unit conversion of source-reported sodium'))
                row['conversions'][-1]['from']=row['conversions'][-1].pop('from_')
                row['nutrientProvenance']['na']['method']='source sodium grams converted to mg'
    inventory.append(dict(chain='Wagamama',category='All 224 captured service recipes',sourceItems=224,scope='Named sizes in the public UK nutrition service; independent dishes, not combos'))

def wendys():
    src=source('wendys.pdf',"Wendy’s",'2026-03-25','official UK PDF tables, both pages extracted and first page visually reviewed',
        'March 25, 2026 document edition identified by official filename. No current local-stock claim. Salad table includes toppings and dressing. Ingredients are components, not standalone meals.')
    group=''
    for page in read('wendys-extracted.json'):
        for table in page['tables']:
            for a in table:
                if len(a)!=23:continue
                if a[0] and all(not clean(v) for v in a[1:]):group=clean(a[0]);continue
                if number(a[4]) is None:continue
                values={k:number(a[i]) for k,i in dict(cal=4,fat=5,sat=6,c=7,sugar=8,f=9,p=10,salt=11).items()}
                grams=number(a[2]);category='component' if 'INGREDIENT' in group else 'drink' if 'BEVERAGE' in group else 'dessert' if 'FROSTY' in group else 'side' if group=='SIDES' else 'entree'
                add("Wendy’s",clean(a[0]),'1 named source portion · '+clean(a[2])+' g',values,src,page['page'],category,grams,group,
                    'UK-only March 25, 2026 nutrition snapshot. Named item, no inferred combo. Salad category includes toppings and dressings. Salt converted to sodium. Availability and later recipe changes are not independently confirmed.',meal='breakfast' if group=='BREAKFAST' else 'main')

def fiveguys():
    src=source('fiveguys.pdf','Five Guys','2026-10-13','currently linked official UK PDF nutrition table; per-portion columns separated from per-100g columns',
        'UK locations only, * selected-store breakfast/extras. Full named burgers and individual ingredients remain distinct. No weight inferred from rounded per-100g values. Source includes multiple shake sizes and named mix-ins.')
    table=read('fiveguys-extracted.json')[0]['tables'][2];group=''
    for a in table:
        if len(a)!=19:continue
        if a[0] and all(not clean(v) for v in a[1:]):group=clean(a[0]);continue
        if number(a[2]) is None:continue
        values={k:number(a[i]) for k,i in dict(kJ=1,cal=2,fat=3,sat=4,c=5,sugar=6,f=7,p=8,salt=9).items()}
        name=clean(a[0]);category='component' if group in ('MEAT','BUN','TOPPINGS','OTHER ITEMS') or group.startswith(('MILKSHAKES','LITTLE MILKSHAKES','BUILD YOUR OWN')) else 'side' if 'FRIES' in group or 'SIDES' in group or 'HASH BROWN' in group else 'drink' if 'DRINK' in group else 'entree'
        if group.startswith(('MILKSHAKES','BIG KIDS','LITTLE MILKSHAKES')):name=group.split('+')[0].strip().title()+' — '+name
        add('Five Guys',name,'1 published source portion',values,src,1,category,group=group,
            notes='UK source snapshot dated October 13, 2026 in the current official link. Published portion only; toppings/mix-ins are additional unless the named row says otherwise. Salt converted to sodium. Source * means selected stores; breakfast is not available at every location.',
            meal='breakfast' if any(x in group for x in ('BREAKFAST','HASH BROWN')) else 'main',scope='Heathrow Airport only' if 'HEATHROW ONLY' in group else 'Selected stores' if '*' in name else '',extra=dict(nativePer100g={k:number(a[i+9]) for k,i in dict(kJ=1,cal=2,fat=3,sat=4,c=5,sugar=6,f=7,p=8,salt=9).items()}))

def pepes():
    import lxml.html
    src=source('pepes-nutrition.html',"Pepe’s",None,'official live UK nutrition item table',
        'UK nutrition source, not Ireland. Add Flavour millilitres remain an instruction, not a nutrient or ingredient already added. Source gives no general gram weights or fibre. Distinct source categories preserved.')
    doc=lxml.html.fromstring((SRC/'pepes-nutrition.html').read_text(encoding='utf-8'))
    seen={}
    for i,item in enumerate(doc.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," nutrition-table-item ")]')):
        name=item.get('data-title');group=item.get('data-category');v={}
        for cell in item.xpath('.//div[@class="ntc-item"]'):
            label=clean(''.join(cell.xpath('.//strong//text()'))); alltext=clean(cell.text_content());v[label]=number(alltext.removeprefix(label))
        values={k:v.get(label) for k,label in dict(cal='Kcal',p='Protein (g)',c='Carbohydrates (g)',fat='Fat (g)',sat='Saturated Fat (g)',sugar='Sugars (g)',salt='Salt (g)').items()}
        key=(name,group,tuple(values.items()))
        if key in seen:continue
        seen[key]=True
        category='component' if any(s in group for s in ('dips','sauce')) else 'dessert' if 'dessert' in group else 'side' if any(s in name.lower() for s in ('fries','corn','rice','salad','halloumi')) and 'box' not in name.lower() else 'entree'
        add("Pepe’s",name,'1 named source item',values,src,'nutrition-item-'+str(i),category,group=group,
            notes='Official UK named-item nutrition. No source gram weight supplied. Fibre unavailable. Optional flavour quantity, where shown, must be looked up separately; do not silently add a sauce or meal accompaniment. Salt converted to sodium.',extra=dict(sourceOptionalFlavourMillilitres=v.get('Add Flavour (ml)')))

def starbucks_drinks():
    src=source('starbucks-drinks.pdf','Starbucks','2026-09-18','official Autumn 2026 UK PDF, named size/milk/build table rows',
        'Autumn September–November 2026 edition. Exact named sizes and milk recipes, no inferred customization deltas. Most table rows extracted; irregular non-14-column tables separately withheld. No cup millilitres inferred.')
    for page in read('starbucks-drinks-extracted.json'):
        match=re.search(r'\| Beverages \| (.+?) Version:',page['text'] or '')
        if not match:continue
        group=clean(match[1]);category='component' if 'Syrups' in group else 'drink'
        current='';ingredients=''
        for table in page['tables']:
            if len(table[0])!=14:
                if len(table[0])>1:withheld.append(dict(chain='Starbucks',source=src['url'],sourcePage=page['page'],reason='Irregular beverage table geometry requires separate review',columns=len(table[0])))
                continue
            for index,a in enumerate(table):
                if a[0] and 'Product' not in a[0]:current=clean(a[0]);ingredients=clean(a[1])
                if not current:continue
                size=clean(a[2]);values=[clean(v) for v in a[3:13]]
                if len(size.split())==11 and all(v is None or not clean(v) for v in a[3:13]):
                    tokens=size.split();size=tokens[0];values=tokens[1:]
                if size not in ('Short','Tall','Grande','Venti','Mini','Solo','Doppio','Triple','Quad'):
                    if number(a[4]) is not None:withheld.append(dict(chain='Starbucks',name=current,source=src['url'],sourcePage=page['page'],reason='Unsupported source serving label; no cup or pump amount inferred',size=size))
                    continue
                vals={k:number(values[i]) for k,i in dict(kJ=0,cal=1,fat=2,sat=3,c=4,sugar=5,f=6,p=7,salt=8).items()}
                bounds={k:dict(operator='<',value=number(values[i][1:]),unit='g',sourceText=values[i]) for k,i in dict(fat=2,sat=3,c=4,sugar=5,f=6,p=7,salt=8).items() if values[i].startswith('<') and number(values[i][1:]) is not None}
                name=current+' · '+size
                extra=dict(sourceSize=size,productId='sb-uk-'+hashlib.sha256(current.encode()).hexdigest()[:16],ingredientDescription=ingredients,sourceCaffeineMilligrams=number(values[9]))
                if bounds:extra['nutrientBounds']=bounds
                add('Starbucks',name,'1 '+size+' named UK source build',vals,src,str(page['page'])+':'+str(index),category,group=group,
                    notes='UK Autumn 2026 beverage guide, September 18 edition. Named size, milk and complete source build retained, including toppings where included in its ingredient list. No unlisted substitution inferred. Salt converted to sodium; caffeine is source mg. Cup millilitres unavailable in this table.',extra=extra)

def starbucks_food():
    src=source('starbucks-food.pdf','Starbucks','2026-10-05','official Autumn 2026 UK food PDF; aligned per-portion numeric/name columns',
        'October 5 food guide. Per-portion values, not per 100g. Source does not give general gram weights. Less-than nutrients remain bounds/null exact values. Source ingredients remain in the original PDF.')
    textpages={p['page']:p['text'] or '' for p in read('starbucks-food-extracted.json')}
    for page in read('starbucks-food-coordinates.json'):
        text=textpages[page['page']];match=re.search(r'\| Food \| (.+?) Version:',text)
        if not match:continue
        group=clean(match[1]);words=[w for w in page['numbers'] if w['upright'] and w['top']>120 and w['top']<515 and re.fullmatch(r'<?\d+(?:\.\d+)?',w['text'])]
        anchors=sorted(w['top'] for w in words if 523<=w['x0']<546)
        names=[w for w in page['names'] if w['upright'] and w['x0']<94 and 5.8<=w['height']<=6.3]
        for i,y in enumerate(anchors):
            cells=sorted([w for w in words if abs(w['top']-y)<2],key=lambda w:w['x0'])
            if len(cells)!=9:
                withheld.append(dict(chain='Starbucks',source=src['url'],sourcePage=page['page'],reason='Food numeric row has unexpected column count',rowY=y,cells=[w['text'] for w in cells]));continue
            low=(anchors[i-1]+y)/2 if i else 110;high=(y+anchors[i+1])/2 if i+1<len(anchors) else 515
            name=clean(' '.join(w['text'] for w in sorted([w for w in names if low<w['top']<high],key=lambda w:(round(w['top']/2),w['x0']))))
            if not name or 'ingredients' in name.lower():
                withheld.append(dict(chain='Starbucks',source=src['url'],sourcePage=page['page'],reason='Food name extraction not unambiguous',rowY=y,name=name));continue
            # PDF extraction sometimes exposes an unencodable trademark symbol.
            name=name.replace('\ufffd',' ').replace('  ',' ').strip()
            if name=='Mini Caramel Waffles':
                withheld.append(dict(chain='Starbucks',name=name,source=src['url'],sourcePage=page['page'],reason='Published 787-kcal mini-waffle row lacks an identifiable package weight/count; hold for portion clarification'));continue
            keys=('kJ','cal','fat','sat','c','sugar','f','p','salt');v={k:number(w['text']) for k,w in zip(keys,cells)}
            bounds={k:dict(operator='<',value=number(w['text'][1:]),unit='g',sourceText=w['text']) for k,w in zip(keys,cells) if w['text'].startswith('<')}
            category='dessert' if group in ('Seasonal Menu','Bakery Menu') else 'drink' if any(x in name.lower() for x in ('water','juice','kombucha','smoothie','protein drink')) else 'entree' if group in ('Breakfast Menu','Sandwiches & Toasties') else 'dessert'
            extra=dict(sourceRowY=y)
            if bounds:extra['nutrientBounds']=bounds
            add('Starbucks',name,'1 named UK source portion',v,src,page['page'],category,group=group,meal='breakfast' if group=='Breakfast Menu' else 'main',
                notes='UK October 5, 2026 food guide. Published per-portion values, without extras. Source gives no general serving weight. Salt converted to sodium; less-than values are not exact scalars.',extra=extra)

def chickfila():
    import pdfplumber
    src=source('chickfila.pdf','Chick-fil-A','2026-07 (0726 footer)','official UK per-100g PDF with printed serving weights; per-serving values explicitly calculated',
        'July 2026 footer, currently linked September-upload PDF. Per-100g figures scaled by each printed gram serving. GB-only/NI-only recipes remain separate; no U.S./Canadian substitution. No UK breakfast table exists in this source.')
    with pdfplumber.open(SRC/'chickfila.pdf') as pdf:
        words=[w for w in pdf.pages[0].extract_words() if w['upright']]
    anchors=[w for w in words if 260<w['x0']<280 and w['top']>280 and re.fullmatch(r'\d+(?:\.\d+)?',w['text'])]
    for anchor in anchors:
        y=anchor['top'];line=sorted([w for w in words if abs(w['top']-y)<4 and w['x0']<440],key=lambda w:w['x0'])
        # Name width is narrower in the three-size sides and two-size drinks.
        name_limit=180 if 940<y<1080 else 205 if 1250<y<1600 else 230
        name=clean(' '.join(w['text'] for w in line if w['x0']<name_limit))
        if not name:continue
        numeric=[w for w in line if w['x0']>=name_limit and number(w['text']) is not None]
        nutrient=[w for w in numeric if w['x0']>260]
        portions=[w for w in numeric if w['x0']<260]
        if len(nutrient)!=7 or not portions:
            withheld.append(dict(chain='Chick-fil-A',name=name,source=src['url'],sourcePage=1,reason='Per-100g row/portion geometry not unambiguous',rowY=y));continue
        native={k:number(w['text']) for k,w in zip(('cal','fat','sat','c','sugar','p','salt'),nutrient)}
        group='Mains' if y<510 else 'Salads and protein components' if y<690 else 'Sauces and toppings' if y<940 else 'Sides' if y<1080 else 'Kids portions' if y<1250 else 'Drinks' if y<1650 else 'Treats'
        for i,portion in enumerate(portions):
            grams=number(portion['text']);size=(['Small','Regular','Large'][i] if len(portions)==3 else ['Regular','Large'][i] if len(portions)==2 else '')
            title=name+(' · '+size if size else '')
            if group=='Kids portions' and title=='Chick-fil-A® Waffle Potato Fries - Small':
                # Identical printed 63 g serving already captured in Sides.
                continue
            scope='Northern Ireland only' if '(NI only)' in name else 'Great Britain only (not Northern Ireland)' if '(GB only)' in name else ''
            vals={k:round(v*grams/100,8) if v is not None else None for k,v in native.items()}
            category='component' if group in ('Salads and protein components','Sauces and toppings') or name=='Gluten Free Bun' else 'side' if group=='Sides' else 'drink' if group=='Drinks' or 'Milk' in name or 'Juicy Water' in name else 'dessert' if group=='Treats' else 'entree'
            if 'Fruit Cup' in name or 'Fries - Small' in name:category='side'
            row=add('Chick-fil-A',title,'1 named source portion · '+str(grams).removesuffix('.0')+' g',vals,src,'1:y'+str(round(y,1)),category,grams,group,
                'UK official sheet reports nutrient values per 100 g. GetMacros calculates this serving as source per-100g value × printed serving grams ÷ 100. Exact named main/side/sauce only, no drink, dressing or combo inferred. Fibre unavailable. Regional recipes retained.',scope=scope,extra=dict(nativePer100g=native,sourceRowY=y,nutrientBasis='calculated per printed source serving'))
            if row:
                row['nativeNutrients']=native
                row['conversions'].insert(0,dict(from_='per100g',to='perServing',formula='source per-100g nutrient × source serving grams ÷ 100',method='serving calculation from official source',servingGrams=grams))
                row['conversions'][0]['from']=row['conversions'][0].pop('from_')
                for k in row['nutrientProvenance']:row['nutrientProvenance'][k]['method']='source per-100g nutrient × printed serving grams ÷ 100'+('; source salt then converted to sodium' if k=='na' else '')

def save():
    # Same exact name/portion/source can occur in multiple visible groups. Merge
    # duplicate numeric identities; withhold conflicting versions together.
    seen={};bad=set()
    for row in records:
        identity=row['id']
        if identity in seen:
            if any(row.get(k)!=seen[identity].get(k) for k in FIELDS):bad.add(identity)
            else:seen[identity].setdefault('duplicateSourcePages',[]).append(row['sourcePage'])
        else:seen[identity]=row
    final=[r for key,r in seen.items() if key not in bad]
    for identity in bad:withheld.append(dict(id=identity,reason='Conflicting same-name/serving source rows withheld together'))
    # The inspected baseline contained GB Greggs, KFC and Subway only; none of
    # this batch's 17 chains overlaps those identities. Do not filter against a
    # mutable post-integration registry: that would erase the reproducible batch
    # on a later run. The integration contract handles ID upserts explicitly.
    summary=dict(schemaVersion=1,reviewedAt=DATE,market='GB',counts=dict(collections.Counter(r['chain'] for r in final)),records=len(final),
        categories=dict(collections.Counter(r['category'] for r in final)),withheld=len(withheld),baseline=456,
        products=len({(r['chain'],r.get('productId',r['name'].split(' · ')[0])) for r in final}),
        composedOrders=0,scope='Reviewed UK source snapshots and named portions; not an audited full live-menu/stock guarantee')
    for row in final:
        row['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in row.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    out=ROOT/'tools/flagship_release/uk_records.json'
    out.write_text(json.dumps(dict(schemaVersion=1,reviewedAt=DATE,records=final,updates=[]),ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    (DOC/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'source-register.json').write_text(json.dumps(list(sources.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOC/'withheld.json').write_text(json.dumps(withheld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    actual=collections.Counter((r['chain'],r['sourceGroup']) for r in final)
    for row in inventory:row['publishedStagedRecords']=actual[row['chain'],row['category']]
    (DOC/'source-category-capture-notes.json').write_text(json.dumps(dict(scope='Raw adapter diagnostics before final audit/deduplication; repeated pricing groups are not additive coverage counts.',groups=inventory),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    nandos();leon();wagamama();wendys();fiveguys();pepes();starbucks_drinks();starbucks_food();chickfila()
    import uk_depth
    import sys
    uk_depth.run(sys.modules[__name__]);save()
    import uk_quality
    uk_quality.main()
