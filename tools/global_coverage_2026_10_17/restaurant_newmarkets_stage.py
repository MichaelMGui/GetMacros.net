"""Four additional markets, staged separately from the stable eight-market batch."""
from pathlib import Path
import json,re,hashlib
from collections import Counter,defaultdict
import restaurant_stage as core
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/newmarkets'
core.D=D
core.retrieval={r['file']:r for r in json.loads((D/'retrieval.json').read_text(encoding='utf-8')) if 'sha256' in r}
core.records=[];core.updates=[];core.sources={};core.withheld=[]
def read(file):return json.loads((D/file).read_text(encoding='utf-8'))
def n(value,comma=False):
 s=re.sub(r'\s+','',str('' if value is None else value))
 s=s.replace(',','.' if comma else '')
 return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def text(s):return core.clean(s)
def htmltext(s):
 import lxml.html
 try:return text(lxml.html.fromstring('<div>'+s+'</div>').text_content())
 except Exception:return text(s)
def screen(name,v,src,page):
 if not all(v.get(k) is not None for k in ('cal','p','c','fat')):
  core.withheld.append({'name':name,'source':src['url'],'sourcePage':page,'published':v,'missingFields':[k for k in ('cal','p','c','fat') if v.get(k) is None],'reason':'Full macros unavailable or unclear after source extraction; missing fields not inferred'});return False
 # Alcohol contributes energy beyond P/C/fat. Do not call the source beer row
 # contradictory merely because 4/4/9 omits its alcohol energy.
 if 'heineken' in name.lower():return True
 estimate=v['p']*4+v['c']*4+v['fat']*9
 if v['cal']>10000 or any(v[k]>1000 for k in ('p','c','fat')) or abs(v['cal']-estimate)>max(65,0.25*v['cal']):
  core.withheld.append({'name':name,'source':src['url'],'sourcePage':page,'published':v,'screeningEstimate':estimate,'reason':'large source energy/macro discrepancy or implausible extracted numeric cell; no inferred correction'});return False
 return True
def france():
 src=core.source('quick-fr-current.pdf','FR','Quick','2026-10-06',limitations='All three per-portion source tables reviewed. Corrupted or inconsistent cells withheld. Source weights are not supplied; per-100g columns are not separate menu items. (*) participating restaurants; (**) prepackaged and participating restaurants.')
 group=''
 for page in read('quick-fr-current-extracted.json'):
  for table in page['tables']:
   for a in table:
    if len(a)!=19:continue
    if a[0] and n(a[2],True) is None and not any(n(x,True) is not None for x in a[1:10]):
     if not a[0].startswith(('(*)','(**)')):group=text(a[0])
     continue
    if n(a[2],True) is None:continue
    name=text(a[0]);v={k:n(a[i],True) for k,i in {'kJ':1,'cal':2,'fat':3,'sat':4,'c':5,'sugar':6,'p':7,'salt':8,'f':9}.items()}
    if not screen(name,v,src,page['page']):continue
    bounds={k:{'operator':'<','value':float(re.sub(r'\s+','',a[i])[1:].replace(',','.')),'unit':'g','sourceText':a[i]} for k,i in {'fat':3,'sat':4,'c':5,'sugar':6,'p':7,'salt':8,'f':9}.items() if a[i] and re.fullmatch(r'<\s*\d+(?:[,.]\d+)?',a[i])}
    group_lower=group.lower();category='component' if any(z in group_lower for z in ('sauce','assaisonnement')) or name.lower().startswith(('sucre sachet','sucre churros','coupelle de lait')) else 'drink' if any(z in group_lower for z in ('boisson','milk-shake','shake','softs')) else 'dessert' if any(z in group_lower for z in ('dessert','softy','mix mania','pâtisser')) else 'side' if any(z in group_lower for z in ('frite','salade','accompagne')) else 'entree'
    volume=re.search(r'(\d+)\s*ml',group,re.I)
    if volume:name+=' · '+volume[1]+' ml'
    r=core.add('FR','Quick',name,'1 portion publiée / format nommé'+(' · '+volume[1]+' ml' if volume else ''),v,src,page['page'],category,notes='France-only October 6, 2026 source edition. One named published portion. No menu sides or drink added. Sodium converted from source salt; no source serving weight available. (*) marks participating restaurants; (**) prepackaged products at participating restaurants. French source product names preserved.',language='fr',group=group,bounds=bounds)
    if volume:r['servingMillilitres']=int(volume[1])
    r['sourceAvailabilityMarkers']={'participatingRestaurants':True,'prepackaged':'(**)' in name}
def india():
 src=core.source('mcd-in-ne.pdf','IN','McDonald’s North & East India',None,limitations='Currently linked official Connaught Plaza North & East India booklet, 71 product pages plus cover. PDF has no whole-book edition date; /2025/12/ upload path is not treated as publication date. Per-product version labels remain in names. No West/South India equivalence.')
 for page in read('mcd-in-ne-extracted.json'):
  if not page['tables']:continue
  t=page['tables'][0]
  name=text(t[1][0]);header=t[0]
  if not name:continue
  size_row=next((a for a in t if len(a)>2 and re.fullmatch(r'(?:serve\s*)?size\s*(?:\((?:g|ml)\))?',text(a[1]).lower())),None)
  if not size_row:
   core.withheld.append({'source':src['url'],'sourcePage':page['page'],'name':name,'reason':'No unambiguous source serving row'});continue
  for col in range(2,len(header)):
   serving=text(size_row[col])
   if not re.fullmatch(r'\d+(?:\.\d+)?\s*(?:g|ml)',serving,re.I):continue
   values={}
   for a in t:
    if len(a)<=col:continue
    label=text(a[1]).lower();value=n(a[col])
    if label.startswith('energy'):values['cal']=value
    elif label.startswith('protein'):values['p']=value
    elif label in ('fat','total fat (g)','total fat(g)'):values['fat']=value
    elif label.startswith(('sat fat','saturated fat')):values['sat']=value
    elif 'carbohydrate' in label or label.startswith(('total carb','carb')):values['c']=value
    elif label.startswith('total sugar') or label=='sugar':values['sugar']=value
    elif label.startswith('sodium'):values['na']=value
   variant=text(header[col]).replace('Regula r','Regular').replace('Regul ar','Regular')
   if not variant or variant.lower() in ('regular','serve size / per serve','serve size/ per serve'):variant=''
   item_name=name+(' · '+variant if variant and 'RDA' not in variant else '')
   if not screen(item_name,values,src,page['page']):continue
   lower=name.lower();category='component' if any(z in lower for z in ('dip sauce','chilli sauce','slice','ketchup','milk tub','spice mix','sachet','syrup','butter chiplet','seeded bun')) else 'drink' if any(z in lower for z in ('coffee','cappuccino','latte','americano','chocolate milk','coca','coke','fanta','sprite','tea','chai','water','minute made','float')) else 'dessert' if any(z in lower for z in ('sundae','mcflurry','mcswirl','waffle','cone','brownie','ice cream')) else 'side' if 'fries' in lower or 'hash brown' in lower else 'entree'
   grams_match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*g',serving,re.I)
   r=core.add('IN','McDonald’s North & East India',item_name,'1 named source portion · '+serving,values,src,page['page'],category,float(grams_match[1]) if grams_match else None,notes='Connaught Plaza Restaurants Private Limited, North & East India only. Currently linked official booklet; whole-book edition date unavailable. Source upload path is not its edition date. Named sizes/counts and product version labels preserved. Not interchangeable with West/South India franchises. Fibre unavailable.',group='North & East India official product booklet')
   r['operatingRegion']='North & East India';r['localOperatingEntity']='Connaught Plaza Restaurants Private Limited';r['region']='IN-NORTH-EAST';r['sourceUploadedPath']='2025/12';r['nutrientBasis']='per named source serving'
def singapore():
 seen={}
 for file in sorted(D.glob('bk-sg-category*.html')):
  raw=file.read_text(encoding='utf-8');match=re.search(r'window.BK_MENU_PRODUCTS = (.*?);\s*</script>',raw,re.S)
  if not match:continue
  src=core.source(file.name,'SG','Burger King',None,limitations='All nine live linked Singapore menu categories captured. Source publication date not supplied. 100ml fountain references remain 100ml references, not cups. Public embedded BK_MENU_PRODUCTS nutrition data; gram/mg unit labels verified in the official main.js display template.')
  for product_id,a in json.loads(match[1]).items():
   if product_id in seen:continue
   seen[product_id]=a
   v={k:n(a.get(native)) for k,native in {'cal':'calories','p':'protein','c':'carbohydrates','fat':'fat','sat':'saturatedfat','f':'fiber','na':'sodium','sugar':'sugar'}.items()}
   name=htmltext(a['title'])+(' '+htmltext(a['size']) if a.get('size') else '')
   if not screen(name,v,src,'BK_MENU_PRODUCTS.'+product_id):continue
   description=htmltext(a.get('description',''));low=name.lower()
   drink=any(x in low for x in ('coca','sprite','fanta','fuze tea','minute maid','iced','ice lemon','coffee','cappuccino','latte','americano','tea','milo','water'))
   category='drink' if drink else 'dessert' if any(x in low for x in ('sundae','pie','taro','float','fusion','ice cream','hershey')) else 'side' if any(x in low for x in ('fries','onion rings','hash brown')) else 'entree'
   reference='100ml' in low
   serving='100 ml source reference amount' if reference else '1 named source item'+(' · '+htmltext(a['size']) if a.get('size') else '')
   r=core.add('SG','Burger King',name,serving,v,src,'BK_MENU_PRODUCTS.'+product_id,category,notes='Singapore local live menu product data. One source-listed item; no inferred meal, cup or double-patty recipe. No publication/edition date supplied. '+('Published per-100ml beverage reference; scale to actual consumed volume, not an unspecified cup. ' if reference else '')+'Official description is a menu description, not a full ingredient formulation.',group='Singapore category '+file.stem.removeprefix('bk-sg-category'))
   r['productId']=product_id;r['productUrl']='https://burgerking.com.sg/Menu/Category/'+file.stem.removeprefix('bk-sg-category')+'#product-'+product_id;r['ingredientDescription']=description
   if reference:r['servingMillilitres']=100;r['nutrientBasis']='per 100 ml source reference';r['finderSupported']=False
def south_africa():
 import lxml.html
 src=core.source('debonairs-za-index.html','ZA','Debonairs Pizza',None,limitations='Live standard/halaal source nutrition panels. No publication date or gram weight supplied. Same-size conflicting panels withheld together. Source decimal/size inconsistencies not repaired. kJ converted to kcal; a whole source-sized portion is not one slice.')
 doc=lxml.html.fromstring((D/'debonairs-za-index.html').read_text(encoding='utf-8'))
 candidates=[]
 for article in doc.xpath('//article[contains(@class,"nutri-item")]'):
  name=text(article.xpath('string(.//span[@class="nutri-item__name"])'))
  section=article.getparent().getparent();group=text(section.xpath('string(./h2|./h3|./h4)'))
  panel=article.xpath('.//div[@class="nutri-item__panel"]')[0];panel_id=panel.get('id')
  variant='halaal' if 'halaal' in panel_id else 'standard'
  for size_node in panel.xpath('.//div[@class="nutri-size"]'):
   size=text(size_node.xpath('string(.//h3)'))
   vals={text(x.xpath('string(./dt)')):n(x.xpath('string(./dd)')) for x in size_node.xpath('.//div[@class="nutri-row"]')}
   v={k:vals.get(native) for k,native in {'c':'Carbohydrates (g)','p':'Protein (g)','fat':'Fat (g)','kJ':'Energy (kJ)','na':'Total Sodium (mg)','f':'Dietary Fibre (g)'}.items()}
   v['cal']=v['kJ']/4.184 if v['kJ'] is not None else None
   candidates.append({'name':name,'size':size,'group':group,'variant':variant,'panel':panel_id,'values':v})
 counts=Counter((c['name'],c['size'],c['group'].lower(),c['variant']) for c in candidates)
 duplicate_groups={key for key,count in counts.items() if count>1}
 seen={}
 for c in candidates:
  key=(c['name'],c['size'],c['group'].lower(),c['variant'])
  if key in duplicate_groups:
   core.withheld.append({'name':c['name'],'size':c['size'],'group':c['group'],'variant':c['variant'],'source':src['url'],'sourcePage':c['panel'],'reason':'Repeated same named source size within one section has conflicting/ambiguous portion data; all occurrences withheld'});continue
  label=c['group']+' — '+c['name']+' · '+c['size']+' · '+c['variant']
  if not screen(label,c['values'],src,c['panel']):continue
  # An identical standard/halaal entry adds no new nutritional build.
  common=(c['name'],c['size'],c['group'].lower(),tuple(c['values'].items()))
  if common in seen:
   seen[common]['sourceVariants'].append(c['variant']);continue
  group_lower=c['group'].lower();category='component' if group_lower in ('extras','sauces','base') else 'side' if group_lower=='sides' else 'entree'
  r=core.add('ZA','Debonairs Pizza',label,'1 whole named source portion · '+c['size'],c['values'],src,c['panel'],category,notes='South Africa official live guide. '+c['variant'].title()+' source section and exact named size retained. Whole listed portion, not a slice or per-100g entry. Gram weight unavailable. Energy source is kJ; displayed kcal is calculated as kJ ÷ 4.184. Saturated fat and sugar unavailable. Source size conflicts withheld together.',group=c['group'])
  r['sourceVariants']=[c['variant']];r['sourceEnergyKilojoules']=c['values']['kJ'];r['conversions'].append({'from':'kJ','fromUnit':'kJ','to':'cal','toUnit':'kcal','formula':'kJ ÷ 4.184','method':'energy-unit conversion; source reports kJ'})
  r['nutrientProvenance']['cal']['method']='energy-unit conversion from source kJ';seen[common]=r
 for r in seen.values():
  if len(r['sourceVariants'])>1:r['name']=r['name'].rsplit(' · ',1)[0]+' · standard / halaal';r['notes']+=' Identical standard and halaal source values merged into one nutritional record.'
 return {'sourcePanels':len(candidates),'ambiguousRepeatedSizeGroups':len(duplicate_groups)}
def save(extra):
 for file,market,chain,url in [
  ('quick-fr-index.html','FR','Quick','https://www.quick.fr/'),
  ('mcd-in-ne-index.html','IN','McDonald’s North & East India','https://mcdindia.com/nutritional-information/'),
  ('bk-sg-main.js','SG','Burger King','https://burgerking.com.sg/Content/js/main.js')]:
  core.source(file,market,chain,None,url=url,method='official menu linkage, operating-region or nutrient-unit display evidence',limitations='Supporting source proof; not a separate nutrition record, publication-date claim or reusable visual asset.')
 seen={};output=[];conflicted=set()
 for r in core.records:
  identity=r['market']+'|'+r['restaurantId']+'|'+hashlib.sha256((r['name']+'|'+r['serving']).encode()).hexdigest()[:16]
  r['id']=identity
  if identity in seen:
   old=seen[identity]
   if all(r.get(k)==old.get(k) for k in ('cal','p','c','fat','f','na','sugar','sat')):
    old.setdefault('duplicateSourcePages',[old['sourcePage']]).append(r['sourcePage']);continue
   core.withheld.append({'name':r['name'],'source':r['source'],'sourcePage':[r['sourcePage'],old['sourcePage']],'reason':'conflicting same named serving occurs twice in source; both withheld'});conflicted.add(identity);continue
  seen[identity]=r;output.append(r)
 core.records=[r for r in output if r['id'] not in conflicted]
 for r in core.records:
  r['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
 report={'schemaVersion':1,'reviewedAt':'2026-10-17','scope':'Four additional real markets, exact reviewed country/regional source snapshots. Not a complete current-menu/local-stock audit.','marketCounts':dict(Counter(r['market'] for r in core.records)),'chainCounts':dict(Counter(r['market']+'|'+r['chain'] for r in core.records)),'records':core.records,'updates':[]}
 (ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-records.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 (D/'source-register.json').write_text(json.dumps(list(core.sources.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (D/'withheld.json').write_text(json.dumps(core.withheld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 summary={k:v for k,v in report.items() if k not in ('records','updates')};summary.update(extra);summary['withheldEntries']=len(core.withheld)
 (D/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({**summary,'records':len(core.records),'finderEligible':dict(Counter(r['market'] for r in core.records if r['finderSupported']))},ensure_ascii=False))
if __name__=='__main__':
 france();india();singapore();extra=south_africa();save(extra)
