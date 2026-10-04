"""Curated official-source rows, portions and publication payload. No shared writes."""
from pathlib import Path
import json,re,hashlib
BASE=Path(__file__).resolve().parent
DATES={'arbys':'2026-06','sonic':None,'qdoba':'2026','el-pollo-loco':'2026-09','del-taco':'2026-02','noodles':None,'culvers':'2025-07','taco-johns':None,'raising-canes':'2026-08','in-n-out':'2026-01'}
SLUGS={'arbys':'arbys','sonic':'sonic','qdoba':'qdoba','el-pollo-loco':'el-pollo-loco','del-taco':'del-taco','noodles':'noodles-and-company','culvers':'culvers','taco-johns':'taco-johns','raising-canes':'raising-canes','in-n-out':'in-n-out'}
CHARS={'arbys':'steak','sonic':'potato','qdoba':'avocado','el-pollo-loco':'chicken','del-taco':'tomato','noodles':'broccoli','culvers':'potato','taco-johns':'tomato','raising-canes':'chicken','in-n-out':'potato'}
INTRO={
 'arbys':'Roast-beef sandwiches, chicken wraps and breakfast orders, compared at their listed portions. Breakfast and regional items depend on the location.',
 'sonic':'Burgers, hot dogs and breakfast orders from SONIC’s linked U.S. brochure. Optional items are marked in the source; drinks and extra sides are separate.',
 'qdoba':'Named bowls, burritos, salads and three-taco orders. These are published builds; changing rice, beans or toppings creates a different order.',
 'el-pollo-loco':'Chicken bowls, burritos and salads from the September 2026 U.S. guide. Starred salads exclude dressing; complete chicken-meal entries name their sides.',
 'del-taco':'Tacos, burritos, salads and breakfast orders at their published gram weights. A single taco is shown as a single taco, never as an unnamed combination meal.',
 'noodles':'Regular-size noodle dishes, protein-containing entrées, salads and soup. Small, Duos and individual add-on portions are kept out of this comparison.',
 'culvers':'Single-patty burgers, chicken sandwiches and other listed orders. Dinner nutrition includes the specified protein, roll and butter; extra sides remain separate.',
 'taco-johns':'Compare tacos, burritos, bowls and breakfast orders without silently adding Potato Olés or a drink. Limited-time and select-location labels remain visible.',
 'raising-canes':'A sandwich and two clearly specified orders made from listed individual portions. Calculated orders are kept separate from the chain’s published combo entries.',
 'in-n-out':'Three standard burgers and their explicitly published mustard-and-ketchup or lettuce-wrap versions. Extra fries, drinks and spread packets are separate.'}
def clean(name,id):
 name=re.sub(r'^[•∆★*]+\s*','',name).strip()
 name=re.sub(r'[•∆★*]', '', name).strip()
 if id=='del-taco':name=re.sub(r'^(?:EPIC BURRITOS®|MACHO BURRITOS|\(In select restaurants\)|& NACHOS|SALADS|& FRIES)\s+','',name)
 if id=='noodles':name=re.sub(r' w$','',name)+(', regular')
 if id=='sonic':
  name=name.title().replace('Sonic','SONIC').replace('Supersonic','SuperSONIC').replace('Blt','BLT').replace('®','®')
 return name
def run():
 sources={r['id']:r for r in json.loads((BASE/'sources/retrieval-log.json').read_text(encoding='utf8')) if not r.get('error')}
 sources['in-n-out']={'id':'in-n-out','chain':'In-N-Out','url':'https://www.in-n-out.com/docs/default-source/downloads/nutrition_info.pdf?sfvrsn=332aab37_36','landing':'https://www.in-n-out.com/menu/nutrition-info','retrieved':'2026-10-04','inspection':'Current official landing-page download clicked and PDF text inspected through web. Direct local PDF download returned a challenge, not the PDF; no local PDF snapshot claimed.'}
 selected=json.loads((BASE/'selected-candidates.json').read_text(encoding='utf8'));records=[];seen=set();blocked=[]
 def add(id,row,serving=None,notes='',components=None,method='published'):
  source=sources[id];name=clean(row['name'],id);key=source['chain']+'||'+name
  if key in seen:return
  seen.add(key);v={k:(int(x) if x is not None and x==int(x) else x) for k,x in row['values'].items()}
  assert v['f'] is None or v['f']<=v['c'],(key,'fiber exceeds carbs')
  if not serving:
   unit=' oz' if id=='el-pollo-loco' else ' g'
   weight=str(row['portion']).rstrip('g') if row.get('portion') else None
   serving='1 published order'+(f', {weight}{unit}' if weight else '')
   if id=='noodles':serving='1 regular-size published dish; add-on proteins excluded unless named'
   if id in ('sonic','arbys','del-taco','taco-johns'):serving+='; extra sides, sauce packets and drink excluded'
   if id=='culvers':
    if 'Dinner' in name:serving+='; protein, lemon wedge, dinner roll and butter only; extra sides excluded'
    elif '**' in row['name']:serving+='; listed protein and lemon wedge only; fries, coleslaw and drink excluded'
    else:serving+='; extra sides and drink excluded'
   if id=='el-pollo-loco' and '*' in row['name']:serving+='; dressing excluded'
  qualifiers=row.get('qualifiers',{})
  if qualifiers:notes+=(' ' if notes else '')+'Published bounds: '+', '.join({'f':'fiber','p':'protein','fat':'fat','c':'carbohydrate','na':'sodium'}.get(k,k)+' '+val+' '+('mg' if k=='na' else 'g') for k,val in qualifiers.items())+'. Exact values are not given.'
  if any(t in row['sourceRow'] for t in ('•','∆','★','select locations','Limited Time')):notes+=(' ' if notes else '')+'Source marks this item as limited-time or location-dependent; check availability.'
  if id=='arbys' and (name.startswith('Quarter Pound ') or name.startswith('Pecan Chicken Salad')):notes+=(' ' if notes else '')+'Listed in the source’s limited-time section; check availability.'
  if id=='culvers':notes+=(' ' if notes else '')+'Uses the official July 2025 PDF edition, retrieved October 4, 2026. Check the restaurant’s live nutrition guide for subsequent changes.'
  if id=='sonic':notes+=(' ' if notes else '')+'Linked file name says September 2026; printed cover says Summer 2026. Retrieval is not a claim of recipe re-testing.'
  if id=='noodles':notes+=(' ' if notes else '')+'Regular (REG) columns used; small (SM), Duos and side portions not substituted.'
  if id=='in-n-out':notes+=(' ' if notes else '')+'January 2026 PDF edition linked by the official nutrition page. Some HTML-page rows differ; these values consistently use the linked PDF.'
  isbreakfast=bool(re.search(r'breakfast|biscuit|croissant|sourdough|egg.*(?:wrap|sandwich)|french toast',name,re.I)) and id in ('arbys','sonic','taco-johns','del-taco')
  meal={'chain':source['chain'],'name':name,**{k:v[k] for k in ('cal','p','c','f','na')},'t':[],'diet':[],'meal':'breakfast' if isbreakfast else 'main','url':SLUGS[id]+'-nutrition-guide.html','why':serving+'.'}
  prov={'source':source['url'],'checked':'2026-10-04','sourceDate':DATES[id],'region':'U.S.','serving':serving,'fat':v['fat'],'components':components or [],'verificationStatus':'official source inspected; published row transcribed' if method=='published' else 'official individual portions inspected; GetMacros sum calculated','notes':notes,'nutrientProvenance':{k:{'method':method,'source':source['url'],'retrieved':'2026-10-04',**({'publishedBound':qualifiers[k]} if k in qualifiers else {})} for k in v}}
  records.append({'recordKey':key,'meal':meal,'provenance':prov,'values':v,'sourceId':id,'sourcePage':row['page'],'sourceRow':row['sourceRow'],'orderKind':'calculated complete order' if components else 'published complete order'})
 for id,rows in selected.items():
  for row in rows:
   # Exclude ordinary serving-size duplicates and incomplete stand-alone sides.
   if (id=='el-pollo-loco' and row['name']=='Double Chicken Tostada*') or (id=='sonic' and row['name']=='SuperSONIC® DOUBLE CHEESEBURGER WITH KETCHUP & MAYO'):continue
   if id=='del-taco' and row['name']=='Double Del® Cheeseburger':continue
   add(id,row)
 # This source was actually inspected through web; numeric facts copied from its nine explicit rows.
 names=['Hamburger with onion','Hamburger with onion, mustard and ketchup instead of spread','Hamburger with onion, Protein Style (lettuce instead of bun)','Cheeseburger with onion','Cheeseburger with onion, mustard and ketchup instead of spread','Cheeseburger with onion, Protein Style (lettuce instead of bun)','Double-Double with onion','Double-Double with onion, mustard and ketchup instead of spread','Double-Double with onion, Protein Style (lettuce instead of bun)']
 values=[[209,360,16,670,38,2,16],[202,300,10,610,38,2,16],[211,210,14,390,9,2,12],[229,430,21,1080,40,2,20],[222,380,15,1020,39,2,20],[231,280,19,800,11,2,16],[287,610,34,1670,42,2,34],[280,550,27,1600,41,2,34],[289,460,32,1390,12,2,30]]
 for name,(g,cal,fat,na,c,f,p) in zip(names,values):add('in-n-out',{'name':name,'portion':str(g),'page':1,'sourceRow':name+' '+json.dumps([g,cal,fat,na,c,f,p]),'values':dict(cal=cal,fat=fat,na=na,c=c,f=f,p=p)})
 cane=sources['raising-canes'];add('raising-canes',{'name':'Chicken Sandwich','page':1,'sourceRow':'Chicken Sandwich 10.5 oz (297 g) 810 40 6 0 120 1650 68 4 13 45','values':dict(cal=810,fat=40,na=1650,c=68,f=4,p=45)},serving='1 chicken sandwich, 10.5 oz (297 g); extra sides and drink excluded')
 components={'finger':('Chicken Finger','1.9 oz (55 g)',dict(cal=130,fat=6,na=230,c=5,f=None,p=12)), 'fries':('Crinkle-Cut Fries','5.1 oz (144 g)',dict(cal=420,fat=21,na=320,c=53,f=6,p=5)), 'sauce':('Cane’s Sauce','1.5 oz (43 g)',dict(cal=190,fat=18,na=570,c=6,f=None,p=0)), 'toast':('Texas Toast','1.7 oz (47 g)',dict(cal=150,fat=4.5,na=300,c=23,f=2,p=4)), 'slaw':('Coleslaw','3.1 oz (87 g)',dict(cal=90,fat=6,na=310,c=10,f=2,p=1))}
 for name,build in [('3 fingers with fries, sauce and Texas Toast (individual portions)',[('finger',3),('fries',1),('sauce',1),('toast',1)]),('3 fingers with Texas Toast and coleslaw (individual portions)',[('finger',3),('toast',1),('slaw',1)])]:
  parts=[dict(item=components[k][0],count=n,serving=components[k][1],values=components[k][2]) for k,n in build]
  summed={key:None if any(p['values'][key] is None for p in parts) else sum(p['values'][key]*p['count'] for p in parts) for key in ('cal','p','c','f','na','fat')}
  serving=' + '.join(str(p['count'])+' × '+p['item']+' ('+p['serving']+')' for p in parts)+'; drink excluded'
  add('raising-canes',{'name':name,'page':1,'sourceRow':'GetMacros sum of the five inspected individual-item rows','values':summed},serving=serving,components=parts,method='calculated',notes='These are orders of individually listed items, not the published Combo portion. Published Combo lines do not equal sums of the listed individual portions; they are not substituted. Chicken finger and sauce fiber are published as less than 1 g, so exact total fiber is unknown.')
 blocked=[{'chain':'QDOBA','order':'Quesabirria Burrito / Quesabirria Quesadilla','reason':'Official rows list 95/127 g fat, strongly inconsistent with published calories and other macros. Not corrected or published.'},{'chain':'Taco John’s','order':'Fiesta Rice Bowl, Beef','reason':'Official row lists 100 g fiber and 76 g carbohydrate. Excluded pending restaurant clarification.'},{'chain':'Raising Cane’s','order':'Published combination meals','reason':'Published combo values do not equal sums of listed individual portions; serving reconciliation unresolved. Individual-portion builds are labeled as GetMacros calculations.'},{'chain':'Jimmy John’s','reason':'Official page retrieved a script shell, not nutrition data.'},{'chain':'Potbelly','reason':'Official nutrition page direct retrieval HTTP403; no unofficial substitute used.'},{'chain':'Shake Shack','reason':'Official nutrition PDF redirect direct retrieval HTTP403; no unofficial substitute used.'}]
 chains=[{'id':id,'chain':sources[id]['chain'],'route':SLUGS[id]+'-nutrition-guide.html','character':CHARS[id],'intro':INTRO[id],'source':sources[id],'sourceDate':DATES[id],'records':sum(r['sourceId']==id for r in records)} for id in [*selected,'in-n-out','raising-canes']]
 payload={'date':'2026-10-04','baseRecords':83,'baseChains':15,'newOrders':len(records),'newChains':len(chains),'records':records,'chains':chains,'blocked':blocked,'evidence':'Official PDF rows and header layouts inspected; regular/small column selection verified. This is not a kitchen test, allergen assessment, price survey or promise of current local availability.'}
 (BASE/'expansion-payload.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Verified',len(records),'additional orders across',len(chains),'new chains');print({c['chain']:c['records'] for c in chains})
if __name__=='__main__':run()
