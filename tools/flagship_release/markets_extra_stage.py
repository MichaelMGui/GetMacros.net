"""Source-scoped imports for existing markets, separate from shared integration."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
import json,re,hashlib,copy,math
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/markets'
DATE='2026-10-18'
KEYS=('cal','p','c','fat','f','na','sugar','sat')
records=[];sources=[];withheld=[];reports=[]

def clean(x):return ' '.join(str('' if x is None else x).split())
def num(x):
    s=clean(x).replace(',','')
    return float(s) if re.fullmatch(r'(?:\d+(?:\.\d+)?|\.\d+)',s) else None
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def source(file,market,chain,edition,coverage,limitations='',url=None,method='official PDF table extraction and rendered table inspection'):
    f=DOC/'sources'/file
    evidence=next(r for r in json.loads((DOC/'retrieval.json').read_text(encoding='utf-8')) if r.get('sha256') and Path(r['file']).name==file)
    row={'id':f.stem,'file':f.relative_to(ROOT).as_posix(),'url':url or evidence['url'],
      'marketScope':market,'chain':chain,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
      'retrievedAt':DATE,'verifiedAt':DATE,'sourceEdition':edition,'captureMethod':method,
      'retrievalIsVerification':False,'coverage':coverage,'limitations':limitations}
    sources.append(row);return row
def add(market,chain,name,portion,values,src,page,category='entree',grams=None,group='',notes='',language='en',source_id=None,conversions=None,finder=True):
    v={k:values.get(k) for k in KEYS}
    conversions=conversions or []
    if v['cal'] is None and values.get('kJ') is not None:
        v['cal']=round(values['kJ']/4.184,2)
        conversions.append({'from':'kJ','fromUnit':'kJ','to':'cal','toUnit':'kcal','formula':'kJ ÷ 4.184','method':'energy unit conversion; not source-reported kcal'})
    if v['na'] is None and values.get('salt') is not None:
        v['na']=round(values['salt']*400,8)
        conversions.append({'from':'salt','fromUnit':'g','to':'na','toUnit':'mg','formula':'salt (g) × 400','method':'salt-equivalent conversion; not source-reported sodium'})
    complete=all(v[k] is not None for k in ('cal','p','c','fat'))
    if not complete:
        withheld.append({'market':market,'chain':chain,'name':name,'source':src['url'],'page':page,'reason':'missing exact core nutrient','values':values});return None
    # Screening catches impossible source quantities; it never corrects them.
    if v['sugar'] is not None and v['c'] is not None and v['sugar']>v['c']+1:
        withheld.append({'market':market,'chain':chain,'name':name,'source':src['url'],'page':page,'reason':'source sugar materially exceeds carbohydrate','values':values});return None
    energy=4*v['p']+4*v['c']+9*v['fat']
    if abs(v['cal']-energy)>max(50,.2*max(v['cal'],energy)):
        withheld.append({'market':market,'chain':chain,'name':name,'source':src['url'],'page':page,'reason':'gross source energy/macronutrient discrepancy; no correction inferred','values':values,'screeningEstimate':energy});return None
    if grams is not None and v['p']+v['c']+v['fat']>max(grams+3,grams*1.15):
        withheld.append({'market':market,'chain':chain,'name':name,'source':src['url'],'page':page,'reason':'source macronutrient mass materially exceeds serving mass','values':values,'servingGrams':grams});return None
    r={'id':market+'|'+slug(chain)+'|official-'+(str(source_id) if source_id else hashlib.sha256((name+'|'+portion).encode()).hexdigest()[:16]),
       'chain':chain,'restaurantId':slug(chain),'restaurantMarketId':market+'|'+slug(chain),
       'name':clean(name),'market':market,'country':market,'region':market,'language':language,
       'serving':clean(portion),'servingGrams':grams,'size':'','category':category,
       'meal':'breakfast' if 'breakfast' in group.lower() else 'main','diet':[],'components':[],
       **v,'source':src['url'],'sourceDate':src['sourceEdition'],'retrievedAt':DATE,'checked':DATE,
       'verificationStatus':'official-table-reviewed','sourceHash':src['sha256'],'sourcePage':page,
       'sourceCaptureMethod':src['captureMethod'],'sourceGroup':group,'sourceGroups':[group],
       'nativeNutrients':values,'nutrientBasis':'per named serving',
       'units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g'},
       'macroComplete':complete,'finderSupported':finder and category!='component','conversions':conversions,
       'url':'/'+market.lower()+'/en/restaurants/'+slug(chain)+'/',
       'notes':notes+' Source snapshot only; not an audit of every live menu, local stock, ingredient formulation or allergen safety.'}
    r['nutrientProvenance']={k:{'method':'official published serving','source':src['url'],'page':page,'edition':src['sourceEdition'],'verifiedAt':DATE} for k,x in v.items() if x is not None}
    for c in conversions:
        r['nutrientProvenance'][c['to']]['method']=c['method']
    r['t']=[tag for tag,yes in [('protein',r['p']>=25),('light',r['cal']<=400),('energy',r['cal']>=600),('fibre',r['f'] is not None and r['f']>=5),('lowsodium',r['na'] is not None and r['na']<=600)] if yes]
    records.append(r);return r

def dominos_anz():
    from lxml import html
    for market in ('AU','NZ'):
        file='dominos-'+market.lower()+'-nutrition.html';tree=html.fromstring((DOC/'sources'/file).read_bytes())
        src=source(file,market,'Domino’s',None,'all numeric named product/variant rows in official country nutrition page',
          'Pizza values are per slice, not whole pizza. Mini count follows source script (4 slices); other counts follow printed card. Fibre unavailable. Missing kcal is converted from published kJ.',method='official public rendered nutrition cards and embedded serving data')
        before=len(records);products=0;seen=set()
        mapping={'Serving Size':'grams','Energy (Calories)':'cal','Energy (kilojoules)':'kJ','Protein':'p','Fat - Total':'fat','Fat - Sat':'sat','Carbohydrate':'c','Sugars':'sugar','Sodium':'na'}
        for card in tree.xpath('//*[@data-productservinginfo]'):
            products+=1;heading=card.xpath('.//*[contains(@class,"product-card-heading")]')[0].text_content().strip()
            labels={}
            for e in card.xpath('.//*[contains(@class,"serving-info-name")]'):
                match=re.search(r'([0-9a-f-]{36})$',e.attrib['id'])
                if match:labels[match[1]]=mapping.get(clean(e.text_content()))
            variants={x.attrib['data-servingid']:json.loads(x.attrib['data-servinginfo'])['Name'] for x in card.xpath('.//*[@data-servinginfo]')}
            values=defaultdict(dict)
            for a in json.loads(card.attrib['data-productservinginfo']):
                k=labels.get(a['ServingParameterId'])
                if k:values[a['ServingId']][k]=num(a['Value'])
            section=card.getparent().getparent();parent=section.getparent()
            lead=next((clean(x.text_content()) for x in parent if 'nutritional-info-menu-' not in x.attrib.get('id','') and len(clean(x.text_content()))<100), 'Menu')
            count_node=card.xpath('.//*[contains(@class,"serving-per-slice")]')
            counttext=clean(count_node[0].text_content()) if count_node else ''
            base_count=num(count_node[0].attrib.get('origserv')) if count_node else None
            for key,v in values.items():
                variant=variants.get(key)
                if not variant:
                    withheld.append({'market':market,'chain':'Domino’s','name':heading,'reason':'nutrition variant is not offered by source control','source':src['url'],'sourceVariant':key});continue
                name=heading+' — '+variant
                identity=(heading,variant)
                if identity in seen:continue
                seen.add(identity)
                is_pizza='pizza' in counttext.lower()
                slices=4 if is_pizza and variant=='Mini' else base_count
                portion=('1 slice of '+str(int(slices)) if is_pizza and slices else '1 published serving')+' · '+str(v.get('grams'))+' g · '+variant
                category='entree' if is_pizza else 'drink' if 'drink' in counttext.lower() else 'side'
                if any(x in heading.lower() for x in ('brownie','choc','cookie','sundae','dessert','mousse','cinnamon')):category='dessert'
                if category=='side' and any(x in heading.lower() for x in ('sauce','dipping','dressing')):category='component'
                r=add(market,'Domino’s',name,portion,{k:v.get(k) for k in ('cal','kJ','p','fat','sat','c','sugar','na')},src,
                     card.attrib.get('id')+'/'+key,category,v.get('grams'),lead,
                     'Official '+market+' recipe and named crust/size. '+('Values represent one slice; source pizza count '+str(int(slices))+'. ' if is_pizza and slices else counttext+'. '),source_id=card.attrib.get('id','').split('-nutritional')[0]+'-'+key)
                if r:r.update({'sourceProductFamily':heading,'sourceVariant':variant,'sourceServingCount':slices if is_pizza else base_count})
        reports.append({'market':market,'restaurant':'Domino’s','sourceGroup':'all published nutrition cards','sourceProducts':products,'reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':None,'status':'all numeric offered variants reviewed','limitations':'Per-slice/serving scope, not whole pizza or real-time branch availability. Fibre unavailable.'})

def dominos_india():
    from lxml import html
    tree=html.fromstring((DOC/'sources/dominos-in-site.html').read_bytes())
    data=json.loads(tree.xpath('//brand-menu-data')[0].attrib['data-results'])
    src=source('dominos-in-site.html','IN','Domino’s',None,'numeric active product variants from current public Indian menu',
       'Only variants with explicit nutrition elements imported; no value copied from another size/crust. Whole named variant, not per-100g or inferred slice. No prices or stock guarantees.',method='official public country menu data embedded in rendered menu document')
    before=len(records);missing=0;seen=set();families=set()
    mapping={'Energy':'cal','Protein':'p','Sodium':'na','Total_Carbohydrate':'c','Total_Fat':'fat','Total_Saturated_Fat':'sat','Total_Sugar':'sugar','Total_Trans-fat':'trans'}
    for p in data['productDefinitions']:
        assert any(x.get('regionCode')=='INDIA' for x in p.get('taxation',[])),'Unscoped menu product'
        for v in p.get('variants',[]):
            if any(v.get(x) for x in ('masterDisabled','cartDisabled','isCartDisabled','isMasterDisabled')):continue
            elems=v.get('metadataMap',{}).get('Elements',{}).get('values',[])
            if not elems:missing+=1;continue
            nutrients={};native={}
            for a in elems:
                name,value,unit=a.split('|');native[name]={'value':value,'unit':unit}
                if name in mapping:nutrients[mapping[name]]=num(value)
            key=v['productUID']
            if key in seen:continue
            seen.add(key)
            description=v.get('displayName') or v['name']
            title=(p.get('displayName') or p['name'])+' — '+description
            if p['productMasterUID']=='b6945854-005c-483e-b6f6-ee0b94723c03':title+=' — Pizza Mania'
            group=p.get('family',{}).get('name','Menu')
            category='entree' if group=='Pizza' else 'drink' if any(x in group.lower() for x in ('beverage','drink')) else 'dessert' if any(x in group.lower() for x in ('dessert','sweet')) else 'side'
            r=add('IN','Domino’s',title,'1 complete named '+description+' item',nutrients,src,'product/'+p['productMasterUID']+'/variant/'+key,category,None,group,
                  'Indian national online menu variant. Nutrition belongs only to this named product/crust/size; no extra cheese, dips, seasoning or combo added. Gram weight and dietary fibre are not published for this variant. ',source_id=key)
            if r:r.update({'sourceProductFamily':p['productMasterUID'],'sourceVariant':description,'sourceNativeElements':native,'sourceItemUrl':src['url']});families.add(p['productMasterUID'])
    reports.append({'market':'IN','restaurant':'Domino’s','sourceGroup':'active menu product variants','sourceProducts':len(data['productDefinitions']),'reviewedProductFamilies':len(families),'reviewedPortionRecords':len(records)-before,'variantsWithoutNutrition':missing,'sourceUrl':src['url'],'status':'only explicit numeric active variants imported','limitations':'Missing variants are not filled from a different crust/size; no full nutrition coverage claim.'})

def hungry_jacks():
    known={};before=len(records);candidates=[]
    retrieval=json.loads((DOC/'retrieval.json').read_text(encoding='utf-8'))
    for f in sorted((DOC/'sources').glob('hjs-au-??-extracted.json')):
        pdf=f.name.replace('-extracted.json','.pdf')
        evidence=next(r for r in retrieval if Path(r.get('file','')).name==pdf)
        url=evidence['url'];part=Path(url).name
        m=re.search(r'(\d{1,2})-([A-Za-z]+)-(20\d{2})',part)
        edition=datetime.strptime('-'.join(m.groups()),'%d-%B-%Y').date().isoformat() if m else ('2026-06-16' if '16062026' in part else None)
        group=re.sub(r'(?:Nutritional-Guide-|Final-|Nutritionals.*|_.*|\.pdf)','',part)
        if 'Chicken-NutritionalGuide' in part:group='Chicken'
        group=re.sub(r'\d{1,2}-[A-Za-z]+-20\d{2}-','',group).replace('-',' ')
        src=source(pdf,'AU','Hungry Jack’s',edition,'numeric per-serving rows from official linked '+group+' guide',
           'Per-100g columns are not confused with per-serving values. Source kJ is converted to kcal. Serving stores/LTO markers retained; no allergen or halal classification inferred.')
        files=json.loads(f.read_text(encoding='utf-8'));accepted=0
        for page in files:
            for t in page['tables']:
                for cells in t:
                    if len(cells)!=19 or num(cells[4]) is None or num(cells[6]) is None:continue
                    name=clean(cells[0]);grams=num(cells[4]);v={k:num(cells[i]) for k,i in {'kJ':6,'p':8,'fat':10,'sat':12,'c':14,'sugar':16,'na':18}.items()}
                    cat='drink' if any(x in group.lower() for x in ('drink','cafe','frozen')) else 'dessert' if 'dessert' in group.lower() else 'component' if 'condiment' in group.lower() else 'side' if 'side' in group.lower() else 'entree'
                    # The source's explicit fields are retained, rather than turning
                    # a store or halal column into a dietary safety claim.
                    candidates.append((name,grams,v,src,page['page'],group,cat,clean(cells[1]),clean(cells[2]),{k:num(cells[i]) for k,i in {'kJ':5,'p':7,'fat':9,'sat':11,'c':13,'sugar':15,'na':17}.items()}));accepted+=1
        reports.append({'market':'AU','restaurant':'Hungry Jack’s','sourceGroup':group,'sourceNamedPortions':accepted,'sourceUrl':src['url'],'sourceEdition':edition,'status':'numeric per-serving rows reviewed','limitations':'Category files overlap. Conflicting duplicate portions use latest identified edition only; equal-edition conflicts are withheld.'})
    grouped=defaultdict(list)
    for a in candidates:grouped[(a[0],a[1])].append(a)
    for key,variants in grouped.items():
        latest=max(a[3]['sourceEdition'] or '' for a in variants)
        picked=[a for a in variants if (a[3]['sourceEdition'] or '')==latest]
        fingerprints={json.dumps(a[2],sort_keys=True) for a in picked}
        if len(fingerprints)>1:
            withheld.append({'market':'AU','chain':'Hungry Jack’s','name':key[0],'reason':'same named portion has conflicting equal-edition source values','edition':latest,'sources':[a[3]['url'] for a in picked]});continue
        name,grams,v,src,page,group,cat,store,select,per100=picked[0]
        r=add('AU','Hungry Jack’s',name,'1 named source serving · '+str(grams)+' g',v,src,page,cat,grams,group,
          'Australian category PDF, exact published serving. Energy converted from kJ to kcal. Store status: '+store+'. Selected-store flag: '+select+'. No combo components summed again. ',finder=('Bundle' not in group and 'Kid' not in group))
        if r:r.update({'sourceProductFamily':name,'sourcePer100g':per100,'sourceStoreStatus':store,'sourceSelectedStores':select})
    return len(records)-before

def burgerking_nz():
    src=source('bk-nz.pdf','NZ','Burger King','2026-07-29','numeric per-serve rows from Core Menu and Limited Time Offers pages; allergens page excluded',
       'Both kJ and kcal retained; per-100g fields are not serving fields. Published internally inconsistent rows withheld; no inferred correction.')
    pages=json.loads((DOC/'sources/bk-nz-extracted.json').read_text(encoding='utf-8'));before=len(records)
    for page in pages[:2]:
        for table in page['tables']:
            for row in table:
                if len(row)!=19 or num(row[2]) is None or num(row[4]) is None:continue
                group=clean(row[0]);name=clean(row[1]);grams=num(row[2])
                v={k:num(row[i]) for k,i in {'kJ':3,'cal':4,'p':5,'fat':6,'sat':7,'c':8,'sugar':9,'na':10}.items()}
                if v['cal'] and abs(v['kJ']/4.184-v['cal'])>max(25,v['cal']*.08):
                    withheld.append({'market':'NZ','chain':'Burger King','name':name,'reason':'source kcal and kJ materially disagree','values':v,'source':src['url']});continue
                category='drink' if 'drink' in group.lower() or any(x in name.lower() for x in ('coke','fanta','sprite','tea','juice','water','coffee')) else 'side' if any(x in name.lower() for x in ('fries','rings','hash','nuggets','chicken fries')) else 'dessert' if any(x in name.lower() for x in ('sundae','fusion','shake','funnel')) else 'component' if any(x in name.lower() for x in ('sauce','dressing','ketchup')) else 'entree'
                add('NZ','Burger King',name,'1 source-listed portion · '+str(grams)+' g',v,src,page['page'],category,grams,group or ('Core menu' if page['page']==1 else 'Limited-time menu'),
                    'New Zealand published portion. July 29, 2026 edition; local availability may vary. No sauce, side or drink added unless named. ')
    reports.append({'market':'NZ','restaurant':'Burger King','sourceGroup':'Core Menu and Limited Time Offers','reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':'2026-07-29','status':'per-serve rows reviewed with conflicts withheld','limitations':'Source dual-energy inconsistencies are not corrected by inference; fibre unavailable.'})

def chickfila_sg():
    src=source('cfa-sg.pdf','SG','Chick-fil-A','2025-11','all numeric main, salad, side, treat, drink and sauce rows in official linked guide',
      'November 2025 source, not all 2026 additions. Sugar greater than carbohydrate in several drinks is withheld, never changed by guess. No U.S./Canadian figures substituted.')
    data=json.loads((DOC/'sources/cfa-sg-extracted.json').read_text(encoding='utf-8'));before=len(records)
    groups=['Mains','Filets','Salads','Treats','Sides','Drinks','Sauces','Dressings']
    tables=[t for t in data[0]['tables'] if len(t)>1]
    assert len(tables)==8
    for group,table in zip(groups,tables):
        for row in table[1:]:
            offset=1 if group in ('Drinks','Treats') else 0
            if len(row)<11+offset:continue
            name=clean(row[0]);quantity=clean(row[1+offset]);grams=num(row[2+offset])
            if grams is None:continue
            v={k:num(row[i+offset]) for k,i in {'cal':3,'p':4,'fat':5,'sat':6,'c':7,'sugar':8,'f':9,'na':10}.items()}
            category='component' if group in ('Filets','Sauces','Dressings') else 'drink' if group=='Drinks' else 'side' if group=='Sides' else 'dessert' if group=='Treats' else 'entree'
            add('SG','Chick-fil-A',name+' — '+quantity,quantity+' · '+str(grams)+' g',v,src,'1 / '+group,category,grams,group,
                'Singapore recipe and official November 2025 serving only. No inferred breakfast availability or U.S. substitution. Separate sauces/dressings remain separate. ')
    reports.append({'market':'SG','restaurant':'Chick-fil-A','sourceGroup':'all November 2025 source categories','reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':'2025-11','status':'consistent named portions imported; contradictory drinks withheld','limitations':'Current 2026 menu additions not covered by dated source; no all-menu completeness claim.'})

def burgerking_fr():
    data=json.loads((DOC/'sources/bk-fr-menu-data.json').read_text(encoding='utf-8'))
    src=source('bk-fr-menu.html','FR','Burger King',None,'nutrient-bearing products reachable from current public menu categories; menu combos are not inferred',
      'Named French source portions; weight unavailable. Salt is converted to sodium. Historical/unlinked and internal KINGDOM products excluded.',method='official public rendered menu hydration data')
    reachable=set();visited=set();categories=defaultdict(set)
    def visit(cid,path):
        if cid in visited:return
        visited.add(cid);cat=data['categories'][cid];path=path+[cat['title']]
        for key,kind in cat.get('items',{}).items():
            if kind=='CATEGORY' and key in data['categories']:visit(key,path)
            elif kind=='PRODUCT':reachable.add(key);categories[key].update(path)
            elif kind=='MENU' and key in data['menus']:
                for group in data['menus'][key].get('content',{}).values():
                    for pid in group.get('ids',[]):
                        if pid in data['products']:reachable.add(pid);categories[pid].update(path)
    visit(data['homeCategory'],[])
    mapping={'energy':'cal','fat':'fat','saturates':'sat','protein':'p','carbs':'c','sugars':'sugar','salt':'salt'}
    before=len(records)
    for pid in sorted(reachable):
        item=data['products'].get(pid)
        if not item or not item.get('displayNutrition') or not item.get('nutrition') or '[' in item.get('name',''):continue
        values={mapping[x['item'].split('.')[-1]]:num(str(x.get('portion','')).replace(',','.')) for x in item['nutrition'] if x['item'].split('.')[-1] in mapping}
        if not all(values.get(k) is not None for k in ('cal','p','c','fat')):continue
        name=clean(item['name']);cats=sorted(categories[pid]);group=' / '.join(cats)
        if pid in ('6103988203432489853','6992014596576420432','7780170669187313138','7862637256457491716'):
            withheld.append({'market':'FR','chain':'Burger King','sourceProductId':pid,'name':name,'source':src['url'],'page':'catalog product/'+pid,'reason':'Current linked source supplies same named Baby burger with materially different nutrient totals and no clear portion qualifier. All conflicting named versions withheld; no serving inferred.','values':values});continue
        if 'Menus enfants' in cats:
            name+=' — menu enfant (produit seul)'
        category='component' if any(x in name.lower() for x in ('sauce','ketchup','mayonnaise')) else 'drink' if any(x in name.lower() for x in ('coca','sprite','fanta','ice tea','vittel','expresso','café','cappuccino','jus ','espresso','nectar','eau ','orangina','minute maid')) else 'dessert' if any(x in name.lower() for x in ('sundae','fusion','brownie','donut','muffin','cookie','glace','mousse','beignet')) else 'side' if any(x in name.lower() for x in ('frites','onion rings','nuggets','chili cheese','mozzarella')) else 'entree'
        r=add('FR','Burger King',name,'1 portion du produit nommé',values,src,'catalog version '+str(data['version'])+'/product/'+pid,category,None,group,
            'French recipe and named published portion. Per-100g values are not used as serving values. No complete menu/combination inferred. Source weight unavailable; salt converted to sodium. ',language='fr',source_id=pid)
        if r:r.update({'sourceProductFamily':pid,'sourceItemUrl':'https://www.burgerking.fr/produit/'+item['routeId'],'sourceCatalogVersion':data['version']})
    reports.append({'market':'FR','restaurant':'Burger King','sourceGroup':'current category-linked product portions','sourceProductsReachable':len(reachable),'reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':None,'status':'numeric reachable products reviewed','limitations':'Unlinked/internal products and theoretical combo variants excluded; fibre and weights not supplied.'})

def kfc_japan():
    src=source('kfc-jp.pdf','JP','KFC','2026-09-11','all numeric Japanese food rows and source drink sizes; English duplicate pages excluded',
       'Source dash means unavailable; zero may include traces. Drinks publish size names without gram weights. Sodium is source-reported, not recomputed from rounded salt.')
    data=json.loads((DOC/'sources/kfc-jp-extracted.json').read_text(encoding='utf-8'));before=len(records)
    for page in data[:5]:
        for table in page['tables']:
            for a in table:
                if len(a)!=21 or not clean(a[0]):continue
                if page['page']<4:
                    if num(a[1]) is None or num(a[2]) is None:continue
                    names=[clean(a[0])];split=[a]
                else:
                    # Japanese soft-drink S/M/L values share table cells. Their
                    # printed size is a size label, never interpreted as grams.
                    sizes=clean(a[1]).split()
                    if not sizes or not all(x in ('S','M','L','1杯','1個','1本') for x in sizes):continue
                    assert all(len(clean(x).split())==len(sizes) for x in a[1:]),a
                    names=[clean(a[0])+' — '+x for x in sizes]
                    split=[[a[0]]+[clean(x).split()[i] for x in a[1:]] for i in range(len(sizes))]
                for name,a in zip(names,split):
                    v={k:num(a[i]) for k,i in {'cal':2,'p':3,'fat':4,'c':5,'na':7,'f':19,'salt':20}.items()}
                    grams=num(a[1]) if page['page']<4 else None
                    category='component' if name.startswith(('（','(')) or any(s in name for s in ('ソース','スパイス','シュガー','シロップ','フレッシュ')) else 'drink' if page['page']>=4 or 'ちゅる' in name else 'side' if any(s in name for s in ('ポテト','コールスロー','ビスケット')) else 'dessert' if 'パイ' in name else 'entree'
                    add('JP','KFC',name,('1 source item · '+str(grams)+' g edible average weight' if grams is not None else '1 source drink/accessory · '+a[1]),v,src,page['page'],category,grams,
                        ['Chicken and separate sauces','Burgers and wraps','Sides and sweets','Cold drinks','Drinks and accessories'][page['page']-1],
                        'Japan-only September 11, 2026 named recipe. Edible average weight, not gross bone/packaging weight. Separately listed sauces are excluded from the food total. Source zero may include trace amounts; dash remains unknown. ',language='ja')
    reports.append({'market':'JP','restaurant':'KFC','sourceGroup':'Japanese nutrition pages 1–5','reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':'2026-09-11','status':'named portions and sizes reviewed','limitations':'English pages 6–10 duplicate same items and are not counted twice; sugar/saturated fat unavailable.'})

def zizzi_ireland():
    src=source('zizzi-ie.pdf','IE','Zizzi','2026-09-28','numeric per-portion dishes, extras, kids and non-alcoholic drinks in explicitly ROI/Belfast Autumn2026 V2 guide',
      'Republic of Ireland and Belfast source is not the UK guide. Source gives cooked per-portion nutrition without gram serving weights. Substitutions/extras excluded. Alcohol contributes energy beyond macros.')
    data=json.loads((DOC/'sources/zizzi-ie-extracted.json').read_text(encoding='utf-8'));before=len(records);seen={}
    for page in data[2:]:
        for table in page['tables']:
            for a in table:
                if len(a) not in (17,18) or num(a[-16]) is None or num(a[-15]) is None or num(a[-8]) is None or num(a[-7]) is None:continue
                name=clean(a[0]);vals=a[-16:];v={k:num(vals[i]) for k,i in {'kJ':8,'cal':9,'fat':10,'sat':11,'c':12,'sugar':13,'p':14,'salt':15}.items()}
                # Alcohol-only categories need separate modelling of ethanol;
                # don't present apparent zero-macro energy as a data error or meal.
                if page['page']>=24:continue
                if not name:continue
                group={3:'Aperitivo',4:'Starters',5:'Salads and signature dishes',6:'Rustica pizza',7:'Classic pizza',8:'Non-gluten pizza',9:'Pasta',10:'Al forno',11:'Sides',12:'Desserts',13:'Gelato and sorbet',14:'Extras',15:'Extras',16:'Extras',17:'Extras',18:'Bambini kids menu',19:'Bambini kids menu',20:'Mocktails',21:'Soft drinks',22:'Coffee',23:'Coffee'}[page['page']]
                if page['page'] in (6,7):name+=' — '+group
                if page['page'] in (18,19):name+=' — Bambini kids menu'
                identity=(name,tuple(v.items()))
                if identity in seen:continue
                seen[identity]=True
                category='dessert' if page['page'] in (12,13) else 'drink' if 20<=page['page']<=23 else 'component' if 14<=page['page']<=17 else 'side' if page['page'] in (3,4,11) else 'entree'
                if any(x in name.lower() for x in ('sauce','add chicken','add prawns','extra')):category='component'
                add('IE','Zizzi',name,'1 named core-menu portion; cooked serving',v,src,page['page'],category,None,
                    group,
                    'Republic of Ireland/Belfast official Autumn 2026 V2 recipe, checked with current Dublin restaurant/menu evidence. Source nutrients represent the cooked named dish; no substitution, extra ingredient or drink added. Gram weight and fibre are unavailable. ')
    reports.append({'market':'IE','restaurant':'Zizzi','sourceGroup':'ROI/Belfast food, extras, kids and non-alcoholic drinks (pages 3–23)','reviewedPortionRecords':len(records)-before,'sourceUrl':src['url'],'sourceEdition':'2026-09-28','status':'per-portion dishes reviewed','limitations':'Alcohol pages 24–25 not imported. Combined ROI/Belfast source does not imply all products at every branch.'})

def build():
    records.clear();sources.clear();withheld.clear();reports.clear()
    dominos_anz();dominos_india();hungry_jacks();burgerking_nz();chickfila_sg();burgerking_fr();kfc_japan();zizzi_ireland()
    # Exact repeated identities from overlapping source categories collapse. A
    # different portion, country, formulation or nutrient profile never collapses.
    unique={};final=[]
    for r in records:
        key=(r['market'],r['chain'],r['name'],r['serving'],tuple(r[k] for k in KEYS))
        if key in unique:continue
        unique[key]=r;final.append(r)
    for r in final:r['sourceVersion']=hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    batch={'schemaVersion':1,'reviewedAt':DATE,'records':final,'updates':[],
           'newCounts':dict(Counter(r['market'] for r in final)),
           'chainCounts':dict(Counter(r['market']+'|'+r['chain'] for r in final)),
           'scope':'Source-identified local published portions; not complete current live menus or exact image coverage.'}
    (ROOT/'tools/flagship_release/markets_extra_records.json').write_text(json.dumps(batch,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for file,value in [('extra-source-register.json',sources),('extra-category-completeness.json',reports),('extra-withheld.json',withheld)]:
        (DOC/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'newRecords':len(final),'newCounts':batch['newCounts'],'chainCounts':batch['chainCounts'],'withheld':len(withheld)},indent=2))
    return batch

if __name__=='__main__':build()
