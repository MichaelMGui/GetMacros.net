"""Stage reviewed country tables without changing shared runtime data.

No blanket source-reported zero is inferred for missing/less-than values.
"""
from pathlib import Path
import json,re,hashlib
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants'
OLD=ROOT/'docs/global-product-release-2026-10-11/sources'
DATE='2026-10-17'
records=[];updates=[];withheld=[];sources={}
existing=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
def read(file,d=D):return json.loads((d/file).read_text(encoding='utf-8'))
retrieval={r['file']:r for r in read('retrieval.json') if 'sha256' in r}
def clean(s):return ' '.join(str('' if s is None else s).split())
def num(s):
 s=clean(s)
 return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def source(file,market,chain,edition,url=None,old=False,method='official PDF table extraction',limitations=''):
 base=OLD if old else D
 if old: evidence=next(r for r in read('retrieval.json',OLD) if r['file']==file)
 else:evidence=retrieval.get(file,{})
 r={'file':str((base/file).relative_to(ROOT)).replace('\\','/'),'url':url or evidence['url'],'sha256':hashlib.sha256((base/file).read_bytes()).hexdigest(),'marketScope':market,'chain':chain,'sourceEdition':edition,'retrievedAt':evidence.get('retrievedAt',evidence.get('retrieved',DATE)),'verifiedAt':DATE,'captureMethod':method,'coverage':'reviewed table selection; not a full current-menu or local-stock audit','limitations':limitations,'retrievalIsVerification':False}
 sources[file]=r;return r
def add(market,chain,name,serving,values,src,page,category='entree',grams=None,notes='',language='en',group='',components=(),bounds=None):
 name=clean(name);serving=clean(serving)
 identity=market+'|'+slug(chain)+'|'+hashlib.sha256((name+'|'+serving).encode()).hexdigest()[:16]
 vals={k:values.get(k) for k in ('cal','p','c','fat','f','na','sugar','sat')}
 conversion=[]
 if vals['na'] is None and num(values.get('salt')) is not None:
  vals['na']=round(values['salt']*1000/2.5,8)
  conversion=[{'from':'salt','fromUnit':'g','to':'na','toUnit':'mg','formula':'salt (g) × 1000 ÷ 2.5','method':'salt-equivalent conversion; not source-reported sodium'}]
 complete=all(vals[k] is not None for k in ('cal','p','c','fat'))
 r={'id':identity,'chain':chain,'restaurantId':slug(chain),'restaurantMarketId':market+'|'+slug(chain),'name':name,'market':market,'country':market,'region':market,'language':language,'serving':serving,'servingGrams':grams,'category':category,'meal':'breakfast' if 'breakfast' in group.lower() or 'brekkie' in group.lower() or '朝モス' in group else 'main','size':'','diet':[],'components':[{'item':x,'quantity':None} for x in components],**vals,'source':src['url'],'sourceDate':src['sourceEdition'],'retrievedAt':src['retrievedAt'],'checked':DATE,'verificationStatus':'official-table-reviewed','sourcePage':page,'sourceHash':src['sha256'],'sourceCaptureMethod':src['captureMethod'],'nativeNutrients':values,'nutrientBasis':'per named serving','units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g'},'notes':notes,'conversions':conversion,'macroComplete':complete,'finderSupported':complete and category!='component','sourceGroup':group,'url':'/'+market.lower()+'/en/restaurants/'+slug(chain)+'/'}
 if market=='US' and chain=='Panda Express':r['url']='/panda-express-healthy-meals-macros.html'
 r['nutrientProvenance']={k:{'method':'salt-equivalent conversion' if k=='na' and conversion else 'official published serving','source':src['url'],'page':page,'edition':src['sourceEdition'],'verifiedAt':DATE} for k,v in vals.items() if v is not None}
 if bounds:r['nutrientBounds']=bounds
 r['t']=[tag for tag,yes in [('protein',r['p'] is not None and r['p']>=25),('light',r['cal'] is not None and r['cal']<=400),('energy',r['cal'] is not None and r['cal']>=600),('fibre',r['f'] is not None and r['f']>=5),('lowsodium',r['na'] is not None and r['na']<=600)] if yes]
 r['sourceVersion']=hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
 records.append(r);return r

def stage_mos():
 src=source('mos-jp.pdf','JP','MOS Burger','2026-10-14',limitations='Japanese item names preserved. Separately listed sauces remain separate. Cold drink weights exclude ice. MOS Cafe has its own source recipes.')
 seen={};group=''
 for p in read('mos-jp-extracted.json'):
  cafe=p['page']==6
  for t in p['tables']:
   for a in t:
    if a[0] and a[0].startswith('【'):group=clean(a[0]);continue
    if len(a) not in (21,8) or num(a[1]) is None or num(a[2]) is None:continue
    name=clean(a[0]);v={k:num(a[i]) for k,i in {'cal':2,'p':3,'fat':4,'c':5,'na':6}.items()}
    if len(a)==21:v.update({'f':num(a[19]),'salt':num(a[20])})
    else:v['salt']=num(a[7])
    if cafe:name+=' · MOS Cafe'
    key=(name,num(a[1]))
    if key in seen:
     if seen[key]!=v:withheld.append({'source':src['url'],'name':name,'reason':'same named serving has conflicting source values'})
     continue
    seen[key]=v
    category='drink' if 'ドリンク' in group or (cafe and any(x in name for x in ['コーヒー','ラテ','ココア','ミルクティー','シェイク','ジンジャー','紅茶'])) else 'component' if any(x in name for x in ['ソース','ドレッシング','シュガー','シロップ','フレッシュ','ポーションバター','ごま油']) and not any(x in name for x in ['バーガー','フォカッチャ','ホットドッグ','含まず','粥','トースト']) else 'dessert' if any(x in name for x in ['ケーキ','マフィン','ポム','デザート']) else 'entree'
    note='Japan-only published recipe and named serving. Separately listed accompaniments are not added. Cold drink source weight excludes ice. Source zero may include trace amounts. Sugar and saturated fat are not supplied.'
    if '限定' in group:note+=' Source availability restriction: '+group+'.'
    if cafe:note+=' MOS Cafe-only recipe; not interchangeable with the ordinary MOS Burger drink or food.'
    add('JP','MOS Burger',name,'1 named source item · '+a[1]+' g',v,src,p['page'],category,num(a[1]),note,'ja',group)

def stage_kfc_ca():
 src=source('kfc-ca.pdf','CA','KFC','2025-11-17',limitations='English Canadian table only. French table is not silently substituted. Source is a dated snapshot; current branch availability is not guaranteed.')
 group=''
 for p in read('kfc-ca-extracted.json')[:3]:
  for t in p['tables']:
   for a in t:
    if len(a)!=12:continue
    if a[0] and all(not clean(x) for x in a[1:]):group=clean(a[0]);continue
    if num(a[2]) is None:continue
    name=clean(a[0]);v={k:num(a[i]) for k,i in {'cal':2,'fat':3,'sat':4,'na':7,'c':8,'f':9,'sugar':10,'p':11}.items()}
    energy=4*v['p']+4*v['c']+9*v['fat']
    if abs(v['cal']-energy)>max(50,0.2*v['cal']):
     withheld.append({'source':src['url'],'name':name,'page':p['page'],'published':v,'screeningEstimate':energy,'reason':'large internal energy/macronutrient discrepancy; no correction inferred'});continue
    category='component' if group=='DIPS' else 'drink' if 'BEVERAGE' in group else 'dessert' if 'DESSERT' in group else 'side' if group in ('SALADS','SIDES') else 'entree'
    name=group.title()+' — '+name if 'CHICKEN' in group or group=='SIDES' else name
    add('CA','KFC',name,clean(a[1]),v,src,p['page'],category,notes='English Canadian source snapshot updated November 17, 2025. Serving unit is preserved; gram weight is unavailable. Includes only the named menu item, not an inferred combo. Availability and French-table differences require separate review.',group=group)

def stage_kfc_uki():
 src=source('kfc-uki.pdf',['GB','IE'],'KFC','2026-09',limitations='Official shared UK&I edition; Ireland-only # and NI/Ireland-only ~ entries excluded from GB. Less-than quantities remain bounds, not exact zero or upper-bound values.')
 seen=set();groups={0:'',13:''}
 for p in read('kfc-uki-extracted.json'):
  for t in p['tables']:
   for cells in t:
    if len(cells)!=26:continue
    for off in (0,13):
     a=cells[off:off+13]
     if a[3]=='kJ':groups[off]=clean(a[0]);continue
     if num(a[4]) is None:continue
     name=clean(a[0]);key=name+'|'+str(p['page'])
     if key in seen:continue
     seen.add(key);v={k:num(a[i]) for k,i in {'kJ':3,'cal':4,'fat':5,'sat':6,'c':7,'sugar':8,'p':9,'salt':10}.items()}
     bounds={k:{'operator':'<','value':float(a[i][1:]),'unit':'g','sourceText':a[i]} for k,i in {'fat':5,'sat':6,'c':7,'sugar':8,'p':9,'salt':10}.items() if a[i] and re.fullmatch(r'<\d+(?:\.\d+)?',a[i])}
     group=groups[off];category='component' if group in ('Add-ons','Sauces','Sauce') else 'drink' if any(x in group.lower() for x in ('drink','coffee','krushem','kwench')) else 'dessert' if 'dessert' in group.lower() else 'side' if group=='Sides' else 'entree'
     for market in (['IE'] if '#' in name or '~' in name else ['GB','IE']):
      note='September 2026 official shared UK&I table; published item/size only. Source salt is converted to sodium; fibre is unavailable. '
      if '#' in name:note+='Source # marker means Ireland-only. '
      if '~' in name:note+='Source ~ marker means Northern Ireland and Ireland only. '
      if '∆' in name:note+='Source ∆ marker means selected restaurants. '
      if bounds:note+='Less-than source values remain unavailable as exact scalars; see nutrientBounds. '
      add(market,'KFC',name,'1 source-listed item / named size',v,src,p['page'],category,notes=note,group=group,bounds=bounds)

def stage_gyg():
 src=source('gyg.pdf','AU','Guzman y Gomez','2026-03-09',old=True,limitations='Expanded exact published mild recipes and named sides. Spicy modifiers/deltas are not standalone meals; source restricted-store notes are retained.')
 original_snapshot=json.loads((ROOT/'tools/product_release/menu-records.json').read_text(encoding='utf-8'))['records']
 existing_keys={(r['name'],r['servingGrams']) for r in original_snapshot if r['market']=='AU' and r['chain']=='Guzman y Gomez'}
 for p in read('gyg-extracted.json',OLD)[16:35]:
  for t in p['tables']:
   group=clean(t[0][0]);build=group.title()
   if group.startswith('EXTRAS'):continue
   for a in t[1:]:
    if len(a)!=11 or any(num(z) is None for z in a[1:]):continue
    # Delta-only rows use positive/negative signs or labels such as spicy.
    if any(x in clean(a[0]).lower() for x in ('make it spicy','add ', 'swap ', 'remove ')):continue
    name=build+' — '+clean(a[0]);grams=num(a[1])
    if (name,grams) in existing_keys:continue
    v={k:num(a[i]) for k,i in {'kJ':2,'cal':3,'p':4,'fat':5,'sat':6,'c':7,'sugar':8,'f':9,'na':10}.items()}
    category='component' if 'DIPPING SAUCES' in group else 'side' if group in ('FRIES','QUESO FRIES','SIDES','LITTLE G’S SIDES') or group.startswith('CORN CHIPS') else 'dessert' if group in ('DESSERTS','CHURROS') else 'entree'
    note='March 9, 2026 Australian guide, exact named standard mild serving. No spicy modifier or ingredient swap applied. Source grams include the published build; named recipe components are not full ingredient formulations.'
    if 'ONLY' in group:note+=' Availability is restricted to the source-listed stores in the item name.'
    add('AU','Guzman y Gomez',name,'1 source-listed '+build.lower()+' · '+a[1]+' g',v,src,p['page'],category,grams,note,group=group)

def stage_panda():
 src=source('panda-us-web-extract.txt','US','Panda Express',None,url='https://www.pandaexpress.com/nutritioninformation',method='official live table through web text extraction',limitations='Selected food rows through source line L82; final Cub Meal category is partial. Fountain beverages omitted. Capture hash identifies saved web-extracted numeric evidence, not raw HTML. No source publication date supplied.')
 group=''
 for line in (D/'panda-us-web-extract.txt').read_text(encoding='utf-8').splitlines():
  if ': ## ' in line:group=line.split(': ## ',1)[1];continue
  if '| Portion (oz)' not in line:continue
  lineid=line.split(':',1)[0];parts=[x.strip() for x in line.split(': ',1)[1].split('|')]
  name=parts[0];fields={}
  if (group,name) in {('Chicken','Grilled Teriyaki Chicken'),('Base','Super Greens'),('Chicken Breast','String Bean Chicken Breast')}:continue # already tracked with this exact official portion
  mapping={'Calories':'cal','Total Fat (g)':'fat','Saturated Fat (g)':'sat','Sodium (mg)':'na','Total Carb (g)':'c','Dietary Fiber (g)':'f','Sugars (g)':'sugar','Protein (g)':'p'}
  for segment in parts[2:]:
   for label,key in mapping.items():
    if segment.startswith(label+' ') and num(segment[len(label)+1:]) is not None:fields[key]=num(segment[len(label)+1:])
  if not all(fields.get(k) is not None for k in ('cal','p','c','fat')):continue
  serving=parts[1].removeprefix('Portion (oz) ')
  category='component' if group=='Sauces & More' or 'Cub Meal' in group else 'side' if group=='Base' else 'entree'
  note='U.S. live official table reviewed October 17, 2026. Portion unit is the source oz column; no fluid-volume-to-mass conversion is inferred. Side and entree versions of the same food retain distinct source portions. * indicates selected restaurants. Cub Meal rows are published food components, not an invented total.'
  r=add('US','Panda Express',group+' — '+name,'1 source portion · '+serving+' oz' if 'oz' not in serving else '1 source portion · '+serving,fields,src,lineid,category,notes=note,group=group)

def stage_nz():
 lines={}
 for file in sorted(D.glob('subway-nz-2026-web-extract-*.txt')):
  for line in file.read_text(encoding='utf-8').splitlines():
   m=re.match(r'L(\d+)@P([0-9-]+): (.*)',line)
   if m and int(m[1])<397:lines[int(m[1])]=(int(m[2].split('-')[0])+1,m[3])
 assert set(range(397)).issubset(lines),'May 2026 per-portion source capture incomplete'
 capture='\n'.join(f'L{i}@P{page}: {text}' for i,(page,text) in sorted(lines.items()))+'\n'
 (D/'subway-nz-2026-web-extract.txt').write_text(capture,encoding='utf-8')
 src=source('subway-nz-2026-web-extract.txt','NZ','Subway','2026-05',url='https://media.subway.com/dam/urn:aaid:aem:0e28bcc2-9385-4a0d-b54f-3a177e7dd86d/original/as/NZ%20Nutritional%20Web%20Guide%20May%202026.pdf',method='official PDF through web text extraction',limitations='Only per-serve pages 1–5. Per-100g pages not imported. Capture hash identifies saved extracted evidence, not original PDF bytes. Current source has internally inconsistent Meatball Mozza Pot and Boysenberry Danish rows, withheld.')
 # Source text extraction sometimes places section captions after their rows.
 # Boundaries below were reviewed against the named source sections, not guessed from nutrients.
 groups=[(0,'6-inch sub','entree'),(75,'wrap','entree'),(138,'regular salad','entree'),(190,'large salad','entree'),(240,'mini sub','entree'),(244,'breakfast 6-inch sub','entree'),(262,'breakfast wrap','entree'),(270,'Sides & Snacks','side'),(301,'Cookies','dessert'),(307,'Baked Goods','dessert'),(311,'Smoothies','drink'),(317,'Breads','component'),(327,'Meat, Poultry, Egg, Seafood & Vegetarian Items','component'),(352,'Sauces & Dressings','component'),(365,'Cheeses','component'),(370,'Vegetables','component'),(383,'Toppings','component'),(385,'Seasonings','component')]
 headings={0,1,2,75,80,81,82,83,177,240,244,245,257,258,259,260,261,262,270,301,307,311,317,327,336,337,338,352,365,370,383,385,388,389,390,391,392,393,394,395,396}
 pattern=re.compile(r'^(.*?)\s*((?:\d+(?:\.\d+)?\s+){9}\d+(?:\.\d+)?)$')
 pending=[];parsed=[]
 for lineid,(page,text) in sorted(lines.items()):
  if lineid in headings:continue
  m=pattern.match(text)
  if not m:
   pending.append(text);continue
  prefix=clean(m[1]);values=m[2].split();assert len(values)==10
  label=clean(' '.join(pending+([prefix] if prefix else [])));pending=[]
  name,sep,recipe=label.partition('(');name=name.strip();recipe=recipe.rstrip(')')
  group,category=next((g,c) for boundary,g,c in reversed(groups) if lineid>=boundary)
  v={k:num(values[i]) for k,i in {'kJ':1,'cal':2,'p':3,'fat':4,'sat':5,'c':6,'sugar':7,'f':8,'na':9}.items()}
  parsed.append((lineid,page,name,recipe,group,category,values))
  energy=4*v['p']+4*v['c']+9*v['fat']
  if abs(v['cal']-energy)>max(60,0.2*v['cal']):
   withheld.append({'source':src['url'],'name':name,'page':page,'published':v,'screeningEstimate':energy,'reason':'large internal energy/macronutrient discrepancy; no correction inferred'});continue
  full_name=group.title()+' — '+name
  note='May 2026 New Zealand source per-serve recipe. Bread, cheese, vegetables and sauce follow the listed named recipe; substitutions are not applied. '+('Ingredient amount only, not a full sandwich. ' if category=='component' else '')
  if group in ('regular salad','large salad'):
   recipe='lettuce, spinach, tomato, cucumber, capsicum, onion, carrot, olive; '+recipe
   note+='Source-listed salad vegetables are included in addition to the named filling, cheese and dressing. '
  if group in ('Baked Goods','Smoothies'):note+='Availability is restricted or varies by location as indicated by the source. '
  r=add('NZ','Subway',full_name,'1 source '+group.lower()+' · '+values[0]+' g',v,src,page,category,num(values[0]),note,group=group,components=[recipe] if recipe else [])
  r['ingredientDescription']=recipe
  if group=='6-inch sub':
   original_snapshot=json.loads((ROOT/'tools/product_release/menu-records.json').read_text(encoding='utf-8'))['records']
   old=next((x for x in original_snapshot if x['market']=='NZ' and x['chain']=='Subway' and x['name']==name),None)
   if old:
    r['id']=old['id'];records.pop();updates.append(r)
 (D/'subway-nz-parse-summary.json').write_text(json.dumps({'numericSourceRows':len(parsed),'groups':dict(Counter(a[4] for a in parsed)),'firstRows':[(a[0],a[2]) for a in parsed[:2]],'lastRows':[(a[0],a[2]) for a in parsed[-3:]]},ensure_ascii=False,indent=2),encoding='utf-8')

def stage_mx():
 src=source('subway-mx-2026-web-extract.txt','MX','Subway','2026-08',url='https://media.subway.com/dam/urn:aaid:aem:246fd30f-0f78-4d1c-bd45-750bda1a695a/original/as/MEX%20Nutrition%20ENG%208.2026.pdf',method='official PDF through web text extraction',limitations='Newly named Golazo/Pastor selections only. Existing English/Spanish official sheets disagree on multiple other recipes; those are not silently refreshed. Capture hash covers saved web extraction, not raw PDF.')
 # Independently compared with the same-date Spanish sheet: these seven rows agree in all macro fields.
 wanted={30:'Golazo — BBQ Rib',32:'Golazo — Milanesa de Pollo',33:'Golazo — Ultra Golazo Steak',36:'Pastor — Gran Pastor',37:'Pastor — Gringo Pastor',38:'Pastor — Campechano',39:'Pastor — Golazo Pastor'}
 spanish=source('subway-mx-2026-spanish-web-extract.txt','MX','Subway','2026-08',url='https://media.subway.com/dam/urn:aaid:aem:d0cb17ed-a9aa-4b24-a855-f8f9dca5a82b/original/as/Mexico%20Nutrition%208.2026%20SP.pdf',method='official PDF through web text extraction',limitations='Independent same-edition cross-check of seven newly named Golazo/Pastor recipes; not a second set of duplicate menu records.')
 es_rows={int(m[1]):m[2].split()[-10:] for line in (D/'subway-mx-2026-spanish-web-extract.txt').read_text(encoding='utf-8').splitlines() if (m:=re.match(r'L(\d+)@P\d+: (.*)',line)) and int(m[1]) in wanted}
 for line in (D/'subway-mx-2026-web-extract.txt').read_text(encoding='utf-8').splitlines():
  m=re.match(r'L(\d+)@P(\d+): (.*)',line)
  if not m or int(m[1]) not in wanted:continue
  a=m[3].split();nums=a[-10:];assert all(num(x) is not None for x in nums)
  assert [num(z) for z in nums]==[num(z) for z in es_rows[int(m[1])]],'EN/ES disagreement in approved Mexican row'
  v={k:num(nums[i]) for k,i in {'cal':1,'fat':3,'sat':4,'na':5,'c':6,'f':7,'sugar':8,'p':9}.items()}
  add('MX','Subway',wanted[int(m[1])],'1 named local sandwich · '+nums[0]+' g',v,src,int(m[2])+1,'entree',num(nums[0]),'August 2026 Mexico-specific named Golazo/Pastor build. Macro values agree with the official same-date Spanish sheet. This is the named source serving, not an inferred 6-inch/footlong size. No extra cheese, sauce, sides or drink added.',group='Golazo Sandwiches' if int(m[1])<35 else 'Pastor Sandwiches')
 for name in ('Ham and Cheese with Guacomole','Golazo Kids Sub'):
  withheld.append({'source':src['url'],'name':name,'reason':'same-edition official English and Spanish values disagree; no preferred value inferred'})

def save():
 # Remove duplicated identical source rows, never conflicting values.
 seen={};dedup=[]
 for r in records:
  key=(r['market'],r['chain'],r['name'],r['serving'])
  if key in seen:
   assert [r[k] for k in ('cal','p','c','fat')]==[seen[key][k] for k in ('cal','p','c','fat')],key
   continue
  seen[key]=r;dedup.append(r)
 assert len({r['id'] for r in dedup})==len(dedup)
 for r in dedup+updates:r['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
 report={'schemaVersion':1,'reviewedAt':DATE,'scope':'Exact reviewed country-specific source selections; no complete/live full-menu claim.','marketCounts':dict(Counter(r['market'] for r in dedup)),'chainCounts':dict(Counter(r['market']+'|'+r['chain'] for r in dedup)),'records':dedup,'updates':updates}
 (ROOT/'tools/global_coverage_2026_10_17/restaurant-records.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 (D/'source-register.json').write_text(json.dumps(list(sources.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (D/'withheld.json').write_text(json.dumps(withheld,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (D/'summary.json').write_text(json.dumps({k:v for k,v in report.items() if k not in ('records','updates')},indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'records':len(dedup),'updates':len(updates),'markets':report['marketCounts'],'chains':report['chainCounts'],'withheld':len(withheld)},ensure_ascii=False))
if __name__=='__main__':
 stage_mos();stage_kfc_ca();stage_kfc_uki();stage_gyg();stage_panda();stage_nz();stage_mx();save()
