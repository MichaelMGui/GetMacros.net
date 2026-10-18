"""Canadian Chipotle published components; no U.S. nutrient substitution."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,copy
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/markets'
DATE='2026-10-18'

def clean(x):return ' '.join(str(x or '').split())
def number(x):
    s=clean(x)
    return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def version(r):
    r.pop('sourceVersion',None)
    r['sourceVersion']=hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
    return r
def stage():
    f=DOC/'sources/chipotle-ca-2025.pdf'
    file_hash=hashlib.sha256(f.read_bytes()).hexdigest()
    url='https://www.chipotle.ca/content/dam/chipotle/menu/nutrition/CA-Nutrition-Facts-Paper-Menu-3-2025.pdf'
    src={'id':'chipotle-ca-components','file':f.relative_to(ROOT).as_posix(),'url':url,
      'marketScope':'CA','chain':'Chipotle','sha256':file_hash,'retrievedAt':DATE,
      'verifiedAt':DATE,'sourceEdition':'2024-10','captureMethod':'official PDF p2 table extraction and rendered page inspection',
      'retrievalIsVerification':False,'coverage':'all named nutrient rows on page 2, with identical kids/adult portions deduplicated',
      'limitations':'Printed edition CAN OCT 24, despite 3-2025 filename. Historical official snapshot, not current live availability. Beverage ml is not converted to grams. <1 values remain bounds. No added price or availability claims.'}
    tables=json.loads((DOC/'sources/chipotle-ca-tables.json').read_text(encoding='utf-8'))
    rows=[];dedup={};reports=[]
    mapping={2:'cal',3:'fat',4:'sat',5:'trans',6:'cholesterol',7:'na',8:'c',9:'f',10:'sugar',11:'p'}
    for ti,table in enumerate(tables):
        previous='';accepted=0;group='Kids menu components' if ti else 'Standard components and drinks'
        # PDF column rules visually span paired beverage sizes; pdfplumber places
        # both printed numbers in the first cell. Split only two explicit values
        # into the two existing rows, requiring an empty second cell.
        for ri,cells in enumerate(table[1:],1):
            for ci,cell in enumerate(cells[2:],2):
                if cell is not None and '\n' in cell:
                    parts=cell.splitlines()
                    assert len(parts)==2 and ri+1<len(table) and table[ri+1][ci] is None,(ri,ci,cell)
                    cells[ci],table[ri+1][ci]=parts
        for index,cells in enumerate(table[1:],1):
            assert len(cells)==12,(ti,index,cells)
            name=clean(cells[0]) or previous
            if cells[0]:previous=name
            serving=clean(cells[1])
            assert name and serving and number(cells[2]) is not None,(ti,index,cells)
            nutrients={key:number(cells[i]) for i,key in mapping.items()}
            bounds={key:{'operator':'<','value':float(clean(cells[i]).replace('<','').strip()),'unit':'g','sourceText':cells[i]} for i,key in mapping.items() if '<' in clean(cells[i])}
            identity=(name,serving,tuple(nutrients.items()),tuple(bounds))
            if identity in dedup:
                dedup[identity]['sourceGroups'].append(group)
                continue
            grams=re.fullmatch(r'(\d+(?:\.\d+)?) g',serving)
            is_drink='ml' in serving and any(x in name for x in ('Beer','Margarita','Coca-Cola','Coke','Nestea','Sprite','Fanta','Tractor','Ginger Ale','Root Beer','Iced Tea','Juice','Milk'))
            complete=all(nutrients.get(k) is not None for k in ('cal','p','c','fat'))
            r={'id':'CA|chipotle|official-'+hashlib.sha256((name+'|'+serving+'|'+group).encode()).hexdigest()[:14],
              'chain':'Chipotle','restaurantId':'chipotle','restaurantMarketId':'CA|chipotle',
              'name':('Kids’ menu — '+name if ti else name),'sourceName':name,'market':'CA','country':'CA','region':'CA','language':'en',
              'serving':serving+' · published '+('kids’' if ti else 'standard')+' portion',
              'sourceServing':serving,'servingGrams':float(grams[1]) if grams else None,
              'sourceProductFamily':name,'sourceGroups':[group],'sourceGroup':group,
              'category':'drink' if is_drink else 'side' if name in ('Mandarins','Valencia Oranges') or name.startswith('Chips') else 'component',
              'meal':'main','size':serving,'diet':[],'components':[],**nutrients,
              'nativeNutrients':nutrients.copy(),'nutrientBounds':bounds,
              'source':url,'sourceDate':'2024-10','retrievedAt':DATE,'checked':DATE,
              'sourceHash':file_hash,'sourcePage':'2 / '+group+' / row '+str(index),
              'verificationStatus':'official-table-reviewed','sourceCaptureMethod':src['captureMethod'],
              'nutrientBasis':'per named serving','macroComplete':complete,'finderSupported':False,
              'units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g','trans':'g','cholesterol':'mg'},
              'conversions':[],'t':[],'url':'/ca/en/restaurants/chipotle/',
              'notes':'Canadian CAN OCT 24 official PDF snapshot, retrieved October 18, 2026; not a guarantee of current availability. This is one published component or drink portion, not a complete burrito/bowl/combo. '+('Kids menu portion; not inferred from half an adult portion. ' if ti else '')+('Less-than source values are bounds, not zero or exact one. ' if bounds else '')+('Published alcoholic drink energy may include alcohol, which is not represented by the three macro fields. ' if any(x in name for x in ('Beer','Margarita')) else '')}
            r['nutrientProvenance']={k:{'method':'official published serving','source':url,'page':2,'edition':'2024-10','verifiedAt':DATE} for k,v in nutrients.items() if v is not None}
            rows.append(r);dedup[identity]=r;accepted+=1
        reports.append({'market':'CA','restaurant':'Chipotle','sourceGroup':group,'sourceNamedPortions':len(table)-1,'numericPortionsReviewed':len(table)-1,'distinctNewPortions':accepted,'sourceUrl':url,'snapshot':file_hash,'sourceEdition':'2024-10','status':'all page-2 named portions reviewed; less-than retained as bounds','limitations':'Snapshot components only; no complete live-menu or all-branch stock claim.'})
    for r in rows:r['sourceGroup']=' / '.join(r['sourceGroups']);version(r)
    return rows,src,reports

def compose_reviewed_orders(rows):
    """A small useful set of explicit sums, never restaurant-published combo totals."""
    def find(chain,name,serving=None):
        found=[r for r in rows if r['market']=='CA' and r['chain']==chain and r['name']==name and (serving is None or r.get('sourceServing')==serving)]
        assert len(found)==1,(chain,name,serving,len(found))
        return found[0]
    specs=[
      ('Chipotle','Chicken, brown rice & black bean bowl', [('Chicken','113 g'),('Cilantro-Lime Brown Rice','113 g'),('Black Beans','113 g'),('Fresh Tomato Salsa','113 g'),('Fajita Vegetables','57 g')]),
      ('Chipotle','Steak, white rice & pinto bean bowl', [('Steak','113 g'),('Cilantro-Lime White Rice','113 g'),('Pinto Beans','113 g'),('Tomatillo-Red Chili Salsa','59 ml'),('Fajita Vegetables','57 g')]),
      ('Chipotle','Sofritas, brown rice & black bean bowl', [('Sofritas','113 g'),('Cilantro-Lime Brown Rice','113 g'),('Black Beans','113 g'),('Roasted Chili-Corn Salsa','113 g'),('Fajita Vegetables','57 g')]),
      ('Chick-fil-A','Grilled sandwich, small waffle fries & small unsweet tea', [('Grilled Chicken Sandwich',None),('Small Chick-fil-A Waffle Potato Fries®',None),('Small Freshly-Brewed Unsweetened Iced Tea',None)]),
    ]
    result=[]
    for chain,name,parts in specs:
        components=[find(chain,n,s) for n,s in parts]
        r=copy.deepcopy(components[0])
        for key in ('sourceItemId','sourceItemAliases','sourceProductFamily','sourceServing','sourceItemUrl','nutrientBounds'):r.pop(key,None)
        r.update({'id':'CA|'+r['restaurantId']+'|calculated-'+hashlib.sha256(name.encode()).hexdigest()[:14],
          'name':name,'category':'entree','meal':'main','size':'','serving':'1 exact composed order: '+' + '.join(x['name']+' ('+x['sourceServing']+')' for x in components),
          'servingGrams':sum(x['servingGrams'] for x in components) if all(x['servingGrams'] is not None for x in components) else None,
          'verificationStatus':'calculated-from-official-components','sourceGroups':['GetMacros composed orders'],'sourceGroup':'GetMacros composed orders','finderSupported':True,
          'components':[{'id':x['id'],'item':x['name'],'quantity':1,'serving':x['sourceServing'],'source':x['source'],'sourceDate':x['sourceDate']} for x in components],
          'notes':'GetMacros arithmetic from the exact Canadian component portions listed below; not a restaurant-published combo total or a guaranteed preset offer. No unlisted sauce, drink, cheese or other add-on is included. '+('Chipotle component edition CAN OCT 24; check current local availability. ' if chain=='Chipotle' else 'Chick-fil-A Canada does not serve breakfast. '),
          'sourcePage':'sum of listed official component portions'})
        for key in ('cal','p','c','fat','f','na','sugar','sat','trans','cholesterol'):
            r[key]=round(sum(x[key] for x in components),8) if all(x.get(key) is not None for x in components) else None
        r['nativeNutrients']=None
        r['nutrientProvenance']={k:{'method':'sum of official components','source':r['source'],'componentIds':[x['id'] for x in components],'verifiedAt':DATE} for k in ('cal','p','c','fat','f','na','sugar','sat') if r[k] is not None}
        r['t']=[tag for tag,yes in [('protein',r['p']>=25),('light',r['cal']<=400),('energy',r['cal']>=600),('fibre',r['f'] is not None and r['f']>=5),('lowsodium',r['na'] is not None and r['na']<=600)] if yes]
        result.append(version(r))
    return result
