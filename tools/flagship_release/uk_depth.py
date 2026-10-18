"""Additional UK category adapters; called by uk_stage, never a shared builder."""
import re,json,hashlib,collections

def unitnum(c,value):
    s=c.clean(value).replace(',','')
    s=re.sub(r'(?i)\s*(?:kcal|kj|mg|g)$','',s)
    return c.number(s)

def run(c):
    zizzi(c);ask(c);pizzaexpress(c);tortilla(c);tim(c);wasabi(c);nero(c);chipotle(c);chopstix(c)

def chopstix(c):
    from lxml import html
    linked=json.loads((c.ROOT/'tools/flagship_release/uk_chopstix_pages.json').read_text(encoding='utf-8'))
    for file,url in linked.items():
        src=c.source(file,'Chopstix',None,'official product-page nutrition table; every product page linked from the captured menu examined',
            'Exact source column labels retained. Base and topping portions are individual components, not complete boxes. Variable meal deals without fixed tables withheld. Conflicting energy/macros withheld; no decimal repaired.')
        doc=html.fromstring((c.SRC/file).read_text(encoding='utf-8'));name=c.clean(doc.xpath('string(//h1)')).replace('\u200b','')
        tables=[t for t in doc.xpath('//table') if 'Protein' in t.text_content()]
        if not tables:
            c.withheld.append(dict(chain='Chopstix',name=name,source=src['url'],reason='No fixed full-macro table for the linked meal deal/product'));continue
        for table in tables:
            rows=[[c.clean(z.text_content()) for z in row.xpath('./td|./th')] for row in table.xpath('.//tr')]
            if not rows:continue
            headers=rows[0];lookup={a[0].lower():a for a in rows[1:] if a}
            for index,size in enumerate(headers[1:],1):
                vals={k:unitnum(c,lookup.get(label,[None]*len(headers))[index]) for k,label in dict(kJ='energy (kj)',cal='energy (kcal)',fat='fat (g)',sat='of which saturates (g)',c='carbohydrate (g)',sugar='of which sugars (g)',f='fibre (g)',p='protein (g)',salt='salt (g)').items()}
                if size=='Fruit Shoot':
                    c.withheld.append(dict(chain='Chopstix',name=name+' — '+size,source=src['url'],reason='Separate drink column does not identify bottle/volume, not added to food total'));continue
                group='Published food combinations' if 'MINI STIX MEAL' in name else 'Dips and sauces' if 'sauce' in file or 'dip-pot' in file else 'Desserts' if any(x in file for x in ('baonut','fortune-cookie')) else 'Sides' if any(x in file for x in ('chips','panko','gyoza','prawn-cracker','spring-roll','chicken-balls')) else 'Bases' if any(x in file for x in ('veg-noodles','egg-fried-rice','skinny-rice')) else 'Toppings'
                category='entree' if group=='Published food combinations' else 'dessert' if group=='Desserts' else 'side' if group=='Sides' else 'component'
                c.add('Chopstix',name+' · '+size,'1 source-listed '+size+' allocation',vals,src,'nutrition-column-'+str(index),category,group=group,
                    notes='UK live source column, not an inferred gram amount. Base and topping rows must be combined deliberately; neither is a full box by itself. Named Mini Stix food combinations exclude the separately listed Fruit Shoot drink. Salt converted to sodium; no missing or contradictory decimal corrected.',extra=dict(sourceSize=size,sourceProductName=name))

def chipotle(c):
    # The official /nutrition-calculator response is a two-page PDF even though
    # its capture filename has .html. Content signatures were checked explicitly.
    src=c.source('chipotle.html','Chipotle',None,'official UK nutrition calculator response is a PDF, per-serving ingredient table',
        'Named ingredient portions only, no gram weights or publication date. Components are not complete burritos/bowls. Source carbohydrate is the local reported field, not silently equated to U.S. label conventions.')
    for page in c.read('chipotle-extracted.json'):
        for table in page['tables']:
            for a in table:
                if len(a)!=9 or c.number(a[1]) is None:continue
                vals={k:c.number(a[i]) for k,i in dict(cal=1,fat=2,sat=3,c=4,sugar=5,f=6,p=7,salt=8).items()}
                name=c.clean(a[0]);bounds={k:dict(operator='<',value=c.number(a[i][1:]),unit='g',sourceText=a[i]) for k,i in dict(fat=2,sat=3,c=4,sugar=5,f=6,p=7,salt=8).items() if a[i] and a[i].startswith('<')}
                c.add('Chipotle',name,'1 source-listed ingredient portion',vals,src,page['page'],'component',group='UK ingredient portions',
                    notes='Official UK ingredient table, per source serving with no published gram weights or edition date. This ingredient is not a complete bowl, taco or burrito. Retain local carbohydrate definition; do not substitute the U.S. formulation. Salt converted to sodium; source less-than quantities remain null/bounds.',extra=dict(nutrientBounds=bounds))

def zizzi(c):
    src=c.source('zizzi.pdf','Zizzi','2026-09-15','official UK Autumn 2026 nutrition PDF, per-portion columns separated from per-100g references',
        'UK guide, separate from official ROI/Belfast guide. Whole named portions, not pizza slices. Fibre and general gram weights absent. Modifier rows are components. Duplicate conflicts withheld.')
    groups={3:'Aperitivo and starters',4:'Starters',5:'Signature dishes and salads',6:'Rustica pizza',7:'Non-gluten pizza',8:'Calzone and classic pizza',9:'Non-gluten dishes',10:'Pasta',11:'Al forno',12:'Desserts',13:'Gelato',14:'Extras',15:'Extras',16:'Extras',17:'Extras',18:'Kids',19:'Kids',20:'Cold drinks',21:'Cold drinks',22:'Hot drinks',23:'Hot drinks',24:'Seasonal specials',25:'Seasonal specials'}
    for page in c.read('zizzi-extracted.json'):
        group=groups.get(page['page'])
        if not group:continue
        for table in page['tables']:
            for a in table:
                if len(a)==18 and not a[1]:a=[a[0]]+a[2:]
                if len(a)!=17 or c.number(a[10]) is None:continue
                name=c.clean(a[0]);vals={k:c.number(a[i]) for k,i in dict(kJ=9,cal=10,fat=11,sat=12,c=13,sugar=14,p=15,salt=16).items()}
                category='component' if group=='Extras' or name.startswith(('Add ','Even better','Extra ')) else 'dessert' if group in ('Desserts','Gelato') else 'drink' if 'drinks' in group else 'side' if group in ('Aperitivo and starters','Starters') else 'entree'
                c.add('Zizzi',name,'1 whole named source portion',vals,src,page['page'],category,group=group,
                    notes='UK Autumn 2026 guide, September 15 edition. One complete named portion; a pizza portion is the whole published pizza, not a slice. No extra ingredient added. Salt converted to sodium. Fibre and source weight unavailable. Separate ROI/Belfast guide is not substituted.',
                    scope='UK-guide restaurants; separate ROI/Belfast source not substituted',extra=dict(nativePer100g={k:c.number(a[i]) for k,i in dict(kJ=1,cal=2,fat=3,sat=4,c=5,sugar=6,p=7,salt=8).items()}))

def ask(c):
    src=c.source('askitalian.pdf','ASK Italian','2026-09-10','official Autumn 2026 UK guide, named menu section and per-portion columns',
        'Version 2 September 10. Core menu dish/portion, no substitutions or extras. General weight/fibre absent; food and beverage rows retained only with unambiguous per-portion macro columns.')
    group=''
    for page in c.read('askitalian-extracted.json'):
        for table in page['tables']:
            for a in table:
                if len(a)!=18 or c.number(a[11]) is None:continue
                if c.clean(a[0]):group=c.clean(a[0])
                name=c.clean(a[1]);vals={k:c.number(a[i]) for k,i in dict(kJ=10,cal=11,fat=12,sat=13,c=14,sugar=15,p=16,salt=17).items()}
                lower=group.lower();category='component' if any(z in lower for z in ('extra','dressing','topping','syrup')) else 'drink' if any(z in lower for z in ('coffee','tea','drink','latte','chocolate','cappuccino','espresso','mocha')) else 'dessert' if 'dessert' in lower or 'gelato' in lower else 'side' if 'side' in lower or 'nibble' in lower or 'bread' in lower else 'entree'
                c.add('ASK Italian',name,'1 named source portion',vals,src,page['page'],category,group=group,
                    notes='UK Autumn 2026 Version 2, September 10. Named core dish/portion without substitutions or additional ingredients. Source per-portion values retained; per-100g values are references, not another serving. Salt converted to sodium; fibre and serving weight unavailable.',
                    extra=dict(nativePer100g={k:c.number(a[i]) for k,i in dict(kJ=2,cal=3,fat=4,sat=5,c=6,sugar=7,p=8,salt=9).items()}))

def pizzaexpress(c):
    src=c.source('pizzaexpress.pdf','PizzaExpress','2026-09','official England/Wales/Scotland September 2026 guide, named per-portion columns',
        'Excludes separately documented Northern Ireland and Brixton/Finsbury Park/Earls Court editions. Classic/Romana/Large Classic pizzas are separate source recipes. Airport breakfast restricted to Edinburgh/Gatwick. Irregular merged tables withheld.')
    groups={3:'Dough Balls',4:'Starters',5:'Sides',6:'Pizzas - Classic',7:'Pizzas - Classic',8:'Pizzas - Romana',9:'Pizzas - Romana',10:'Pizzas - Large Classic',11:'Al Forno',12:'Salads',13:'Dips',14:'Extra toppings',15:'Desserts',16:'Drinks',17:'Hot Drinks',18:'Piccolo starters',19:'Piccolo pizzas and pasta',20:'Piccolo extras',21:'Airport breakfast',22:'Airport breakfast extras',23:'Airport pancakes and pastries',24:'Airport smoothies and juices'}
    for page in c.read('pizzaexpress-extracted.json'):
        if page['page']<3:continue
        group=groups[page['page']]
        for table in page['tables']:
            if len(table[0])!=19:
                if len(table[0])>10:c.withheld.append(dict(chain='PizzaExpress',source=src['url'],sourcePage=page['page'],reason='Irregular merged per-portion table requires separate geometry review',columns=len(table[0])))
                continue
            for a in table:
                if len(a)!=19 or c.number(a[1]) is None:continue
                name=c.clean(a[0]);name=(group.removeprefix('Pizzas - ')+' — '+name) if group.startswith('Pizzas - ') else ('Piccolo — '+name) if group.startswith('Piccolo') else name
                vals={k:c.number(a[i]) for k,i in dict(cal=1,kJ=2,fat=3,sat=4,c=5,sugar=6,f=7,p=8,salt=9).items()}
                category='component' if group in ('Dips','Extra toppings','Piccolo extras','Airport breakfast extras') else 'side' if group in ('Dough Balls','Starters','Sides','Piccolo starters') else 'drink' if group in ('Drinks','Hot Drinks','Airport smoothies and juices') else 'dessert' if group=='Desserts' else 'entree'
                scope='Edinburgh and Gatwick airport sites only' if group.startswith('Airport') else 'England, Wales and Scotland; separately documented local editions excluded'
                c.add('PizzaExpress',name,'1 whole named source portion',vals,src,page['page'],category,group=group,meal='breakfast' if group.startswith('Airport') else 'main',scope=scope,
                    notes='September 2026 England/Wales/Scotland guide. Whole named serving, not one pizza slice. Classic, Romana and Large Classic source builds are distinct. No topping, side or drink added beyond the named recipe. Salt converted to sodium. No weight inferred from rounded per-100g data.',
                    extra=dict(nativePer100g={k:c.number(a[i+9]) for k,i in dict(cal=1,kJ=2,fat=3,sat=4,c=5,sugar=6,f=7,p=8,salt=9).items()}))

def tortilla(c):
    src=c.source('tortilla.pdf','Tortilla','2026-09-17','official UK September 17 guide; ingredient portions are scoped to their exact order format',
        'Component amounts for medium/large burrito, bowl, salad and breakfast formats are not interchangeable. Source supplies no gram weights for these recipe allocations. Mexican-rice energy conflicts withheld; no inferred repair.')
    for page in c.read('tortilla-extracted.json'):
        if page['page']<4:continue
        group=c.clean(page['text'].splitlines()[0]).title()
        for table in page['tables']:
            for a in table:
                if len(a)!=13 or c.number(a[1]) is None:continue
                name=c.clean(a[0]);vals={k:c.number(a[i]) for k,i in dict(cal=1,kJ=2,fat=3,sat=4,c=5,sugar=6,f=7,p=8,salt=9).items()}
                if vals['kJ'] is not None and abs(vals['cal']-vals['kJ']/4.184)>max(20,.1*vals['cal']):
                    c.withheld.append(dict(chain='Tortilla',name=name,source=src['url'],sourcePage=page['page'],reason='Published kcal/kJ conflict; not repaired by guessing',values=vals));continue
                category='component' if page['page']<=17 or 20<=page['page']<=23 else 'side' if page['page']==18 else 'dessert' if page['page']==19 else 'drink'
                title=group+' — '+name
                c.add('Tortilla',title,'1 source allocation for '+group.lower(),vals,src,page['page'],category,group=group,meal='breakfast' if 21<=page['page']<=23 else 'main',
                    notes='UK September 17, 2026 guide. Ingredient allocations apply only to the named format; a filling or rice row is not a full burrito. No extra ingredients summed automatically. Source serving mass unavailable. Salt converted to sodium.',
                    extra=dict(sourceComponentName=name,sourceOrderFormat=group))

def tim(c):
    src=c.source('timhortons.pdf','Tim Hortons','2026-10-08','official C5 October 8 Version7 UK&I nutrition PDF; explicit portions and units',
        'Source title UK & Ireland is not itself proof of Republic of Ireland operations. Only GB staged here. Source (Draft) labels retained as published; no customization data invented. Less-than values retained as null/bounds.')
    group=''
    for page in c.read('timhortons-extracted.json'):
        if page['page']<6:continue
        for table in page['tables']:
            for a in table:
                if len(a)!=18:continue
                if a[0] and all(not c.clean(v) for v in a[1:]):group=c.clean(a[0]);continue
                if unitnum(c,a[3]) is None:continue
                vals={k:unitnum(c,a[i]) for k,i in dict(kJ=2,cal=3,fat=5,sat=7,c=9,sugar=11,f=13,p=14,salt=16).items()}
                name=c.clean(a[0]).replace('\u200b','');portion=c.clean(a[1]);gram=re.fullmatch(r'(\d+(?:\.\d+)?)\s*g',portion,re.I)
                bounds={k:dict(operator='<',value=unitnum(c,c.clean(a[i])[1:]),unit='g',sourceText=a[i]) for k,i in dict(fat=5,sat=7,c=9,sugar=11,f=13,p=14,salt=16).items() if c.clean(a[i]).startswith('<')}
                lower=group.lower();category='drink' if 'beverage' in lower else 'component' if any(z in lower for z in ('dip','sauce','custom','ingredient')) else 'dessert' if any(z in lower for z in ('donut','timbits','bake','dessert','cookie','impulse')) else 'side' if 'side' in lower else 'entree'
                c.add('Tim Hortons',name,'1 named source portion · '+portion,vals,src,page['page'],category,float(gram[1]) if gram else None,group,
                    'C5 October 8, 2026 Version7 local guide. Printed portion/ounce label retained without an inferred fluid-volume or gram conversion. Named recipe only, dips separately listed. Salt converted to sodium. Source (Draft) means the source-named draft drink recipe, not GetMacros verification.',
                    meal='breakfast' if 'breakfast' in lower else 'main',extra=dict(nutrientBounds=bounds,sourceSize=portion))

def wasabi(c):
    src=c.source('wasabi.pdf','Wasabi','2026-09-17','official Version34 local guide; published serving calories, other macros scaled from per-100g using explicit source grams',
        'Single-size unambiguous tables only. Platters/multi-size/condiment alternatives held when geometry/basis is unclear. Published serving kcal retained, not replaced by rounded per-100g arithmetic. Fibre absent.')
    groups={4:'Onigiri',5:'Sushi set boxes',6:'Sushi set boxes',7:'Sushi set boxes',8:'Platters',9:'Salads and bowls',10:'Salads and bowls',11:'Potto salad pot',12:'Soups',13:'Bain marie',14:'Bain marie',15:'Mixed bento',16:'Mixed bento',17:'Mixed bento',18:'Hot cabinet',19:'Hot cabinet',20:'Breakfast hot cabinet',21:'Breakfast hot cabinet',22:'Hot sides',23:'Hot sides',24:'Hot beverages',25:'Hot beverages',26:'Hot beverages',27:'Sauces and dressings',28:'Sauces and dressings'}
    for page in c.read('wasabi-extracted.json'):
        if page['page']<4:continue
        group=groups[page['page']]
        for table in page['tables']:
            if not table:continue
            header=[c.clean(v).lower() for v in table[0]]
            if not header or header[0]!='product':continue
            # Map column headings rather than assuming every page has same width.
            def col(test):return next((i for i,h in enumerate(header) if test(h)),None)
            ix=dict(cal=col(lambda h:'kcal' in h and '100g' not in h),p=col(lambda h:'protein' in h),c=col(lambda h:'carbo' in h),sugar=col(lambda h:'sugar' in h),fat=col(lambda h:h.startswith('fat ')),sat=col(lambda h:'sat fat' in h),salt=col(lambda h:'salt' in h),grams=col(lambda h:'portion' in h and 'size' in h))
            # Multiple serving-energy columns or duplicated portion weights mean
            # a separate size adapter is needed; never guess their association.
            energycols=[i for i,h in enumerate(header) if 'kcal' in h and '100g' not in h]
            if len(energycols)!=1 or any(v is None for v in ix.values()):
                c.withheld.append(dict(chain='Wasabi',source=src['url'],sourcePage=page['page'],reason='Multiple/unclear serving columns require distinct size adapter',headings=header));continue
            for a in table[1:]:
                if len(a)!=len(header):continue
                grams=c.number(a[ix['grams']]);cal=c.number(a[ix['cal']])
                if grams is None or cal is None:continue
                native={k:c.number(a[ix[k]]) for k in ('p','c','sugar','fat','sat','salt')}
                vals={k:round(v*grams/100,8) if v is not None else None for k,v in native.items()};vals['cal']=cal
                name=c.clean(a[0]);category='drink' if group=='Hot beverages' else 'component' if group=='Sauces and dressings' else 'side' if group=='Hot sides' else 'entree'
                row=c.add('Wasabi',name,'1 named source portion · '+str(grams).removesuffix('.0')+' g',vals,src,page['page'],category,grams,group,
                    'UK Version34 September17, 2026 guide. Source publishes serving calories; protein/carbohydrate/fat/sugar/salt are per-100g and multiplied by source serving grams ÷100. Native serving kcal retained. No side or separate sauce inferred. Fibre unavailable.',meal='breakfast' if 'Breakfast' in group else 'main',extra=dict(nativePer100g=native,nutrientBasis='published serving kcal; other nutrients calculated from source per-100g and serving weight'))
                if row:
                    for k in row['nutrientProvenance']:
                        if k!='cal':row['nutrientProvenance'][k]['method']='source per-100g value × printed serving grams ÷100'+('; salt converted to sodium' if k=='na' else '')

def nero(c):
    from lxml import html
    names=['coffee','iced-drinks','hot-drinks','breakfast','panini-tostati-nero-deli','salads-soups-hot-pots','snacks','sweet-treats']
    seen={}
    for part in names:
        file='caffenero-'+part+'.html';src=c.source(file,'Caffè Nero',None,'official live GB category HTML tables; per-product values, named option and size',
            'UK site with separate Northern Ireland guide. Named milk/size option retained; no gram weight inferred from rounded per-100g references. Exact live recipe, no customization deltas.')
        doc=html.fromstring((c.SRC/file).read_text(encoding='utf-8'))
        for t in doc.xpath('//table[@class="dataset"]'):
            product=t.xpath('ancestor::div[contains(concat(" ",normalize-space(@class)," ")," menu__product-detail ")]')
            if not product:continue
            # The published markup can nest details wrappers; use the nearest
            # product/option/size, never the first document-order ancestor.
            product=product[-1];name=c.clean(product.xpath('string(./h2)'))
            opt=t.xpath('ancestor::details[@class="menu__product-detail__options__option"]');size=t.xpath('ancestor::details[@class="menu__product-detail__size"]')
            option=c.clean(opt[-1].xpath('string(./summary)')) if opt else '';portion=c.clean(size[-1].xpath('string(./summary)')) if size else ''
            title=' · '.join(v for v in (name,option,portion) if v)
            lookup={};per100={}
            for row in t.xpath('.//tbody/tr'):
                cell=row.xpath('./th|./td')
                if len(cell)!=3:continue
                label=c.clean(cell[0].text_content());lookup[label]=unitnum(c,cell[2].text_content());per100[label]=unitnum(c,cell[1].text_content())
            vals={k:lookup.get(label) for k,label in dict(kJ='Energy (kJ)',cal='Energy (kcal)',fat='Fat',sat='Saturated Fat',c='Carbohydrates',sugar='Sugars',f='Fibre',p='Protein',salt='Salt').items()}
            identity=(title,tuple(vals.items()))
            if identity in seen:continue
            seen[identity]=True
            group=part.replace('-',' ').title();category='drink' if part in ('coffee','iced-drinks','hot-drinks') else 'dessert' if part in ('snacks','sweet-treats') else 'entree'
            ni='(NI)' in title
            c.add('Caffè Nero',title,'1 named source product'+(' · '+portion if portion else ''),vals,src,size[-1].get('name') if size else title,category,group=group,
                notes='Official live UK menu, named milk/size option and per-product nutrition. Explicit (NI) menu names apply only to Northern Ireland. Source per-100g values retained as reference; portion grams not inferred. Salt converted to sodium.',meal='breakfast' if part=='breakfast' else 'main',scope='Northern Ireland only' if ni else 'GB source; explicit Northern Ireland alternatives remain distinct',
                extra=dict(productId=product.get('id') or 'nero-'+hashlib.sha256((name+'|'+option).encode()).hexdigest()[:16],nativePer100g=per100,sourceSize=portion,sourceMilkOption=option,productUrl=src['url']))
