"""Country-scoped imports from inspected official tables. No U.S. substitution."""
from pathlib import Path
import hashlib,json,re
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-product-release-2026-10-11/sources'
DATE='2026-10-11'
retrieval={r['file']:r for r in json.loads((D/'retrieval.json').read_text(encoding='utf-8')) if 'sha256' in r}
records=[]
def read(name):return json.loads((D/(name+'-extracted.json')).read_text(encoding='utf-8'))
def num(s):
 s=str(s or '').strip()
 return float(s) if re.fullmatch(r'\d+(?:\.\d+)?',s) else None
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def row(market,chain,name,serving,values,file,edition,page,category='entree',notes='',grams=None,components=(),language='en'):
 evidence=retrieval[file];assert hashlib.sha256((D/file).read_bytes()).hexdigest()==evidence['sha256']
 fields={k:values.get(k) for k in ['cal','p','c','fat','f','na','sugar','sat']}
 identity=market+'|'+slug(chain)+'|'+hashlib.sha256((name+'|'+serving).encode()).hexdigest()[:16]
 r={'id':identity,'chain':chain,'restaurantId':slug(chain),'restaurantMarketId':market+'|'+slug(chain),'name':name,'market':market,'country':market,'region':market,'language':language,'serving':serving,'servingGrams':grams,'category':category,'meal':'breakfast' if 'Breakfast' in name else 'main','size':'','diet':[],'components':[{'item':c,'quantity':None} for c in components],**fields,'source':evidence['url'],'sourceDate':edition,'retrievedAt':DATE,'checked':DATE,'verificationStatus':'official-table-reviewed','sourcePage':page,'sourceHash':evidence['sha256'],'nativeNutrients':values,'nutrientBasis':'per named serving','units':{'cal':'kcal','p':'g','c':'g','fat':'g','f':'g','na':'mg','sugar':'g','sat':'g'},'notes':notes,'conversions':[],'url':'/'+market.lower()+'/en/restaurants/'+slug(chain)+'/'}
 if 'salt' in values:
  r['na']=values['salt']*1000/2.5 if values['salt'] is not None else None
  r['conversions']=[{'from':'salt','fromUnit':'g','to':'na','toUnit':'mg','formula':'salt (g) × 1000 ÷ 2.5','method':'salt-equivalent conversion; not source-reported sodium'}]
 r['nutrientProvenance']={k:{'method':'salt-equivalent conversion' if k=='na' and 'salt' in values else 'official published serving','source':r['source'],'page':page,'edition':edition,'verifiedAt':DATE} for k,v in fields.items() if v is not None}
 r['macroComplete']=all(r[k] is not None for k in ['cal','p','c','fat'])
 r['t']=[tag for tag,yes in [('protein',r['p'] is not None and r['p']>=25),('light',r['cal'] is not None and r['cal']<=400),('energy',r['cal'] is not None and r['cal']>=600),('fibre',r['f'] is not None and r['f']>=5),('lowsodium',r['na'] is not None and r['na']<=600)] if yes]
 r['sourceVersion']=hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
 records.append(r);return r

for page in read('greggs'):
 for table in page['tables']:
  for cells in table:
   if len(cells)!=27 or num(cells[5]) is None or num(cells[1]) is None:continue
   name=' '.join(cells[0].split());v={k:num(cells[i]) for k,i in {'cal':5,'fat':8,'sat':11,'c':14,'sugar':17,'f':20,'p':22,'salt':25,'kJ':3}.items()}
   category='component' if name.startswith(('Extra ','Spread')) else 'drink' if any(t in name.lower() for t in ['latte','americano','cappuccino','espresso','mocha','coffee','tea ','lemonade','cooler','water','juice']) else 'entree'
   row('GB','Greggs',name,'1 listed portion · source size '+cells[1]+' g/ml',v,'greggs.pdf','2026-09',page['page'],category,'September 2026 guide. Source uses a g/ml size column; gram conversion is unavailable for this entry. (HS) denotes a hospital-shop product. Regional recipes and availability may differ.')

# Only the first nutrition page was calibrated and visually checked for GYG.
page=read('gyg')[16]
ingredients=read('gyg')[2]['tables'][1]+read('gyg')[3]['tables'][1][1:]
for table in page['tables']:
 build=table[0][0].title()
 for cells in table[1:]:
  if len(cells)!=11 or any(num(x) is None for x in cells[1:]):continue # modifiers/deltas are not standalone meals
  name=build+' — '+cells[0]
  v={k:num(cells[i]) for k,i in {'cal':3,'p':4,'fat':5,'sat':6,'c':7,'sugar':8,'f':9,'na':10,'kJ':2}.items()}
  column={'Burrito':2,'Bowl':3,'Caesar Burrito':5}[build]
  components=[c[0] for c in ingredients[1:] if c[column]=='X' and 'Spicy Only' not in c[0]]
  components.append(cells[0].removeprefix('Mild '))
  row('AU','Guzman y Gomez',name,'1 standard mild '+build.lower()+' · '+cells[1]+' g',v,'gyg.pdf','2026-03-09',17,grams=num(cells[1]),components=components,notes='Mild standard build. Source recipe and ingredient matrix, pages 3–4; includes the listed filling, standard sauces and accompaniments. Spicy/rice/bean swaps are not applied. March 9, 2026 edition; locally prepared portions vary. Named components are not a full ingredient formulation.')

for page in read('subway-mexico'):
 group=''
 for cells in page['tables'][0]:
  if len(cells)!=11:continue
  if num(cells[1]) is None:
   if cells[0] and all(x is None for x in cells[1:]):group=' '.join(cells[0].split())
   continue
  name=cells[0];prefix='6-inch sub' if '6"' in group else 'Salad' if 'Salads' in group else group
  category='entree' if '6"' in group or 'Salads' in group else 'component'
  v={k:num(cells[i]) for k,i in {'cal':2,'fat':4,'sat':5,'na':6,'c':7,'f':8,'sugar':9,'p':10}.items()}
  components=['Lettuce','Tomatoes','Onions','Green peppers','Cucumbers','Olives'] if 'Salads' in group else []
  note='November 2025 Mexican source snapshot, not a claim that the full current menu was audited. Standard source recipe; no extra sauces or sides.'
  if 'Salads' in group:note+=' Salad vegetables included. Dressing excluded unless the name says otherwise.'
  row('MX','Subway',prefix+' — '+name,'1 '+prefix.lower()+' · '+cells[1]+' g',v,'subway-mexico.pdf','2025-11',page['page'],category,note,grams=num(cells[1]),components=components)

for cells in read('subway-nz')[0]['tables'][0]:
 if len(cells)!=11 or any(num(x) is None for x in cells[1:]):continue
 name,_,recipe=cells[0].partition('\n');recipe=' '.join(recipe.strip('() ').split())
 v={k:num(cells[i]) for k,i in {'cal':3,'p':4,'fat':5,'sat':6,'c':7,'sugar':8,'f':9,'na':10,'kJ':2}.items()}
 r=row('NZ','Subway',name,'1 source 6-inch sub · '+cells[1]+' g',v,'subway-nz.pdf','2025-10',1,grams=num(cells[1]),components=[p.strip() for p in recipe.split(',') if p.strip()],notes='October 2025 New Zealand recipe snapshot, including the named bread, cheese, vegetables and sauce. Availability can change; custom builds are not equivalent to this recipe. Named recipe components are not full ingredient formulations.')
 r['ingredientDescription']=recipe

# Official edition explicitly covers UK and Republic of Ireland. Market identities stay distinct.
group=''
for cells in read('subway-uk')[0]['tables'][0]:
 if len(cells)!=23:continue
 if num(cells[1]) is None:
  if cells[0] and all(x is None for x in cells[1:]):group=cells[0]
  continue
 if group not in ['Subs','Toasties','Saver Subs','Wraps','Salads']:continue
 for market in ['GB','IE']:
  v={k:num(cells[i]) for k,i in {'cal':3,'fat':4,'sat':5,'c':6,'sugar':7,'f':8,'p':9,'salt':10,'kJ':2}.items()}
  components=['Onions','Cucumbers','Lettuce'];components+=['Bread (variety not specified in this table)'] if group in ['Subs','Saver Subs','Toasties'] else []
  row(market,'Subway',group+' — '+cells[0],'1 listed '+('6-inch sub' if group in ['Subs','Saver Subs'] else group.lower().rstrip('s'))+' · '+cells[1]+' g',v,'subway-uk.pdf','2026-09',1,grams=num(cells[1]),components=components,notes='September 2026 edition explicitly covers UK and Republic of Ireland. Table basis: bread except salads/spuds, named protein and vegetables (onions, cucumbers, lettuce). Exact bread type and full ingredient formulation are not supplied here. Sauce/cheese changes require separate source values. Sodium is converted from published salt.')

japan=json.loads((D/'mcdonalds-japan-tables.json').read_text(encoding='utf-8'))
japan_html=(D/'mcdonalds-japan.html').read_text(encoding='utf-8')
kinds={}
for tr in re.findall(r"<tr data-kind='([^']+)'[^>]*>(.*?)</tr>",japan_html,re.S):
 href=re.search(r"href='(/products/[^']+)'",tr[1])
 if href:kinds[href[1]]=tr[0]
footnotes={kind:{cells[0]['text'].removeprefix('備考'):cells[1]['text'] for cells in table if len(cells)==2} for kind,table in zip(['バーガー','サイド','ドリンク','バリスタ'],japan[1:])}
for ti,table in enumerate(japan[:1]):
 for cells in table[2:]:
  if len(cells)!=9 or not cells[0]['href'] or num(cells[1]['text']) is None:continue
  v={k:num(cells[i]['text']) for k,i in {'cal':1,'p':2,'fat':3,'sat':4,'c':5,'sugar':6,'salt':7}.items()}
  kind=kinds[cells[0]['href']];reference=cells[8]['text'];note=footnotes[kind].get(reference,'')
  name=cells[0]['text']+(' · McCafé by Barista' if kind=='バリスタ' else '')
  r=row('JP','McDonald’s Japan',name,'1 source-listed item / named size',v,'mcdonalds-japan.html',None,ti+1,'drink' if kind in ['ドリンク','バリスタ'] else 'entree',notes='Japanese names and sizes are preserved from the official per-item table. Gram weights, fiber and full ingredient formulations are unavailable in this table. Sodium is converted from salt equivalent; sugar is total sugar. No equivalence to U.S. or Canadian recipes is assumed.'+(' Source serving note ('+reference+'): '+note if note else ''),language='ja')
  r['sourceFootnote']=note;r['sourceCategory']=kind
  r['productUrl']='https://www.mcdonalds.co.jp'+cells[0]['href'];r['sourceModified']='2026-10-08';r['sourceVersion']=hashlib.sha256(json.dumps(r,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]

assert len({r['id'] for r in records})==len(records)
for r in records:
 r['sourceVersion']=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
report={'sourceTables':{n:r for n,r in retrieval.items() if n.endswith(('.pdf','.html'))},'marketCounts':dict(Counter(r['market'] for r in records)),'records':records,'reviewedAt':DATE,'scope':'Inspected source table snapshots; not independent lab measurement or full-menu availability audit.'}
(ROOT/'tools/product_release/menu-records.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
(ROOT/'docs/global-product-release-2026-10-11/menu-import.json').write_text(json.dumps({'counts':report['marketCounts'],'newRecords':len(records),'scope':report['scope']},indent=2),encoding='utf-8')
print('Imported',len(records),'country-scoped rows:',report['marketCounts'])
