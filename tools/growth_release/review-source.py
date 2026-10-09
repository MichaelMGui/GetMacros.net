"""Build a bounded current-source menu catalogue, preserving published uncertainty.

The source HTML is private evidence, not a runtime dependency. Once reviewed,
the curated JSON remains deterministic and is verified by --validate when the
HTML is unavailable. This script never changes the existing meal-finder data.
"""
from __future__ import annotations
import argparse,collections,hashlib,html,json,math,re,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'docs/growth-release-2026-10-09/private-sources/chickfila.html'
OUT=ROOT/'tools/growth_release/menu-records.json'
PUBLIC=ROOT/'js/order-catalogue.json'
AUDIT=ROOT/'docs/growth-release-2026-10-09/source-audit'
DATE='2026-10-09'
URL='https://www.chick-fil-a.com/nutrition-allergens'
FIELDS={'Calories':'calories','Protein (g)':'proteinG','Carbohydrates (g)':'carbsG','Fat (g)':'fatG','Fiber (g)':'fiberG','Sodium (mg)':'sodiumMg','Sugar (g)':'totalSugarG'}
CATEGORIES={'Breakfast':'breakfast','Entrées':'entree','Sides':'side','Treats':'treat','Drinks':'drink','Coffee':'drink','Dipping Sauces':'sauce','Dressings':'dressing'}
OLD_IDS={10324,10325,10305,10150,576,10335,10507,10460,10309}
BASELINE_NAMES={10324:'Grilled Nuggets, 8 count',10325:'Grilled Nuggets, 12 count',10305:'Grilled Chicken Sandwich',10150:'Egg White Grill',576:'Kale Crunch Side',10335:'Chick-fil-A Cool Wrap'}
# Explicitly bounded selection: useful breakfast, entree, side, drink and packet
# choices. Seasonal tests, ambiguous parent rows, catering and add-on padding
# are not brought into this release merely to increase the count.
PARENTS={
 'Breakfast':{10168,10152,10147,10194,10192,10190,10188,10186,10184,10150,631,39847,10196},
 'Entrées':{613,10322,616,600,10290,10335,10305,10296,39841},
 'Sides':{10342,581,10346,576,10207,10200,10351,32963,10256},
 'Treats':{10264,10525,10514,10537,10539,10535,10533,10531,10529,51481,51479,51477,10519},
 'Drinks':{10354,10409,10404,10381,10385,10389,10376,10372,10367,10363,10419,10423,10425,10421,10417},
 'Coffee':{10427,12414,51458,51470},
 'Dipping Sauces':{10577,10576,10575,10574,10573,10572,10571,10570},
 'Dressings':{10584,10583,10582,10581,10580,10579,10578},
}
BAD_IDS={10395,51476} # Conflicting plain Iced Coffee definitions; not guessed.

def normalize(s):
 s=html.unescape(s).replace('®','').replace('™','').replace('’',"'").casefold()
 s=re.sub(r'\bwith\b','w',s);s=re.sub(r'\bcount\b','ct',s)
 return re.sub(r'[^a-z0-9]+',' ',s).strip()

def number(raw):
 if isinstance(raw,(int,float)) and not isinstance(raw,bool):
  if not math.isfinite(raw) or raw<0:raise ValueError(f'Invalid nutrient {raw!r}')
  return raw,None
 text=str(raw).strip()
 if re.fullmatch(r'\d+(?:\.\d+)?',text):return float(text) if '.' in text else int(text),None
 m=re.fullmatch(r'([<>≤≥])\s*(\d+(?:\.\d+)?)',text)
 if m:return None,{'operator':m[1],'value':float(m[2]),'raw':text}
 if text in {'','—','-','N/A','NA','None','null'}:return None,None
 raise ValueError(f'Unknown source representation {raw!r}')

def source_groups():
 text=SOURCE.read_text(encoding='utf-8')
 m=re.search(r'<script id="wp-script-module-data-@wordpress/interactivity" type="application/json">(.*?)</script>',text,re.S)
 if not m:raise ValueError('The full official nutrition UI state is missing')
 data=json.loads(m[1])['state']['nutrition-allergens-table-store']['activeTableData']
 return data,hashlib.sha256(SOURCE.read_bytes()).hexdigest()

def record(group,parent,row,digest,is_new):
 raw={f['label']:f['value'] for f in row['fields']}
 if set(FIELDS)-set(raw):raise ValueError(f'Missing nutrient columns {row["title"]}')
 match=re.fullmatch(r'(\d+(?:\.\d+)?)g',str(raw.get('Serving Size','')))
 if not match:raise ValueError(f'Unknown serving weight {row["title"]}: {raw.get("Serving Size")}')
 weight=float(match[1]);weight=int(weight) if weight.is_integer() else weight
 nutrients,bounds={},{}
 for label,key in FIELDS.items():
  nutrients[key],bound=number(raw[label])
  if bound:bounds[key]=bound
 # Added sugar is not in this source table. It is not inferred from total sugar.
 nutrients['addedSugarG']=None
 name=html.unescape(row['title']);key=f'{row["ID"]}|{normalize(name)}|{weight}'
 size_match=re.match(r'(Small|Medium|Large)\b',name)
 count_match=re.match(r'(\d+)\s*(?:ct|pack)\b',name,re.I)
 temperature='Hot' if re.search(r'\bHot\b',name) else 'Iced' if re.search(r'\bIced\b',name) else None
 notes=[]
 if group in ('Drinks','Coffee','Treats'):notes.append('The printed weight is the published serving, not a conversion to fluid ounces. Added sugar and unlisted customizations are unknown.')
 if group in ('Dipping Sauces','Dressings'):notes.append('One published packet/container portion. Adding it to an order is an additional portion; do not add a packet already included in an entree total.')
 if 'Hash Brown Scramble' in name:notes.append('Use only the named published recipe. No unlisted protein or hash-brown substitution is calculated.')
 if row['ID']==10305:notes.append('Sauce inclusion is unresolved: the product page ingredient list includes Honey Roasted BBQ ingredients, while its prose says the sandwich pairs with that sauce. Do not label this 390 kcal row as sauce-free or subtract a packet.')
 if row['ID']==10335:notes.append('The source publishes a suggested-dressing total. Do not add the same suggested dressing again.')
 if row['ID']==576:notes.append('The 112 g published side includes kale, cabbage, vinaigrette and roasted almonds. It is not a catering tray or an almond-free customization.')
 if 'Fruit Cup' in name:notes.append('Use the exact named size: Small 107 g, Medium 125 g, Large 215 g. No generic fruit-cup portion is substituted.')
 if row['ID']==10427:notes.append('Plain Hot Coffee is a published 340 g serving with 0 kcal. Added cream, sugar and unlisted sizes are not included or calculated.')
 source={'url':URL,'productUrl':parent['link'] or None,'id':row['ID'],'parentId':parent['ID'],'group':group,'rowTitle':name,'checkedAt':DATE,'sha256':digest,'method':'complete-official-interface-payload-and-rendered-table','country':'US','sourceEdition':None}
 portion_label=f'{weight:g} g · published serving'
 if size_match:portion_label=f'{size_match[1]} · {weight:g} g'
 elif count_match:portion_label=f'{count_match[1]} count · {weight:g} g'
 return {'id':'cfa-us-'+str(row['ID'])+'-'+hashlib.sha256(key.encode()).hexdigest()[:8],'baselineKey':None if is_new else 'Chick-fil-A||'+BASELINE_NAMES[row['ID']],'restaurant':'Chick-fil-A','chain':'Chick-fil-A','country':'US','category':CATEGORIES[group],'name':name,'portion':{'label':portion_label,'weightG':weight,'sourceLabel':str(raw['Serving Size'])},'size':size_match[1] if size_match else None,'temperature':temperature,'recipe':name,'nutrients':nutrients,'bounds':bounds,'rawPublishedValues':raw,'status':'verified-published','isNew':is_new,'source':source,'sourceDate':None,'checkedAt':DATE,'includedSauces':None,'customizationsSupported':False,'notes':notes,'versionHistory':[{'checkedAt':DATE,'action':'newly-recorded' if is_new else 'existing-row-reverified','sourceSha256':digest}]}

def build():
 groups,digest=source_groups();records=[];seen={};excluded=[];corrections=[]
 for g in groups:
  group=g['menu']
  for p in g['items']:
   if group not in PARENTS or p['ID'] not in PARENTS[group]:continue
   for row in p['sub_items'] or [p]:
    name=html.unescape(row['title'])
    if row['ID'] in BAD_IDS or (name=='Iced Coffee'):
     excluded.append({'sourceId':row['ID'],'name':name,'group':group,'reason':'Conflicting plain Iced Coffee rows have different portion, calories and sugar; no chosen replacement without clarification.'});continue
    # Keep standard scramble builds; omit no-hash variants and seasonal extras.
    if 'no hash brown' in name.lower() or 'Toasted Marshmallow' in name:continue
    # Six-pack cookies are not an individual serving and do not add distinct food.
    if name.startswith('6 pack'):continue
    n=normalize(name)
    raw={f['label']:f['value'] for f in row['fields']}
    if n in seen:
     old=seen[n]
     if raw!=old['rawPublishedValues']:raise ValueError(f'Conflicting duplicate {name}')
     excluded.append({'sourceId':row['ID'],'name':name,'group':group,'reason':'Same named portion already recorded from another category.'});continue
    item=record(group,p,row,digest,row['ID'] not in OLD_IDS)
    seen[n]=item;records.append(item)
    if not item['isNew']:corrections.append({'recordId':item['id'],'sourceId':row['ID'],'name':name,'action':'reverified-existing','numericCorrection':False,'note':'Existing finder nutrition was not rewritten. Explicit current portion, fat and total sugar are documented in this catalogue.'})
 # Preserve source/UI mismatches as blockers, never guessed facts.
 exclusions=[{'scope':'Salads and Side Salad','reason':'Suggested dressing/standard topping assumptions require explicit build confirmation before use in an additive order builder.'},{'scope':'Grilled Chicken Club variants','reason':'Existing named default overlaps; no assumed cheese default or sauce-free build.'},{'scope':'Gallon beverages, trays, catering, kid meal labels and isolated toppings','reason':'Not individual complete meals; source serving definitions or included items can be misleading when aggregated.'},{'scope':'Starbucks Protein Latte / Protein Milk / Protein Cold Foam','reason':'The required release ZIP is absent and exact current complete nutrition/customization panels have not been verified; marketing ranges and search excerpts were not imported.'},{'scope':"McDonald's Canada versus United States",'reason':'The required release ZIP and packaged menu snapshots are absent; no cross-country records were reconstructed.'}]
 sys.path.insert(0,str(ROOT/'tools'))
 from build_meal_finder import parse_meals
 baseline=parse_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))
 counts=collections.Counter(r['category'] for r in records if r['isNew'])
 out={'schemaVersion':1,'checkedAt':DATE,'source':{'url':URL,'country':'US','sha256':digest,'method':'complete-official-interface-payload-and-rendered-table','editionDate':None,'limitation':'Current national standard recipes; location, testing, seasonal and preparation differences can change values. This is not an allergy-safety resource.'},'baseline':{'finderRecords':len(baseline),'chickFilARecords':sum(m['chain']=='Chick-fil-A' for m in baseline)},'counts':{'newRecords':sum(r['isNew'] for r in records),'reverifiedExistingRecords':sum(not r['isNew'] for r in records),'correctedOldRecords':0,'totalCatalogueRecords':len(records),'newByCategory':dict(counts)},'records':records,'corrections':corrections,'exclusions':exclusions+excluded,'unresolved':{'packageMissing':'GetMacros_Content_Release_2026-10-08.zip','sauceInclusion':'Grilled Chicken Sandwich source ingredients and prose do not settle whether the suggested Honey Roasted BBQ packet is inside the nutrition total. No subtraction is made.','plainIcedCoffee':'Drinks source row 10395: 661 g / 200 kcal / 34 g sugar; Coffee sub-item 51476: 624 g / 110 kcal / 10 g sugar. Both excluded.'}}
 validate(out)
 OUT.parent.mkdir(parents=True,exist_ok=True);AUDIT.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 PUBLIC.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 (AUDIT/'counts.json').write_text(json.dumps(out['counts'],indent=2)+'\n',encoding='utf-8')
 print(json.dumps(out['counts'],indent=2))
 return out

def validate(out):
 assert out['schemaVersion']==1 and out['source']['country']=='US'
 ids=set();names=set();expected=len(FIELDS)+1
 for r in out['records']:
  assert r['id'] not in ids;ids.add(r['id'])
  name=normalize(r['name']);assert name not in names;names.add(name)
  assert r['country']=='US' and r['source']['country']=='US' and r['source']['url']==URL
  assert r['portion']['weightG']>0 and r['source']['id']>0
  assert len(r['nutrients'])==expected and r['nutrients']['addedSugarG'] is None
  assert r['sourceDate'] is None and r['checkedAt']==DATE and r['status']=='verified-published'
  assert r['baselineKey']==(None if r['isNew'] else 'Chick-fil-A||'+BASELINE_NAMES[r['source']['id']])
  assert len(r['source']['sha256'])==64 and r['source']['sha256']==out['source']['sha256']
  for label,key in FIELDS.items():
   value,bound=number(r['rawPublishedValues'][label]);assert value==r['nutrients'][key]
   assert bound==r['bounds'].get(key)
  for value in r['nutrients'].values():assert value is None or (not isinstance(value,bool) and isinstance(value,(int,float)) and math.isfinite(value) and value>=0)
  assert r['temperature'] is None or re.search(r'\b'+r['temperature']+r'\b',r['name'])
  assert not any(t in r['name'].lower() for t in ('gallon','tray','catering',"kid's meal",'kid’s meal'))
  assert r['name']!='Iced Coffee'
  assert r['isNew']==(r['source']['id'] not in OLD_IDS)
 assert out['counts']['totalCatalogueRecords']==len(ids)
 assert out['counts']['newRecords']==sum(r['isNew'] for r in out['records'])>=100
 assert out['counts']['reverifiedExistingRecords']==sum(not r['isNew'] for r in out['records'])
 # Arithmetic is a sum of published rounded values, never forced 4/4/9 equality.
 by_id={r['source']['id']:r for r in out['records']}
 assert by_id[10209]['portion']['weightG']==107 and by_id[10209]['nutrients']['calories']==60
 assert by_id[10210]['portion']['weightG']==125 and by_id[10210]['nutrients']['calories']==70
 assert by_id[10211]['portion']['weightG']==215 and by_id[10211]['nutrients']['calories']==120
 assert by_id[576]['portion']['weightG']==112 and by_id[576]['nutrients']['fatG']==12
 assert by_id[10577]['portion']['weightG']==12 and by_id[10577]['nutrients']['calories']==60
 assert by_id[10374]['nutrients']['totalSugarG']==11 and by_id[10374]['nutrients']['addedSugarG'] is None
 # These are calculated examples from named rows, not restaurant-published combo
 # totals. They check serving choice and prevent sauce quantities disappearing.
 for source_ids,expected in [([10150,10209],[360,28,43,8,3,990,13]),([10318,10338,10571],[710,31,52,43,4,1570,8])]:
  keys=list(FIELDS.values())
  assert [sum(by_id[i]['nutrients'][key] for i in source_ids) for key in keys]==expected
  assert all(by_id[i]['nutrients']['addedSugarG'] is None for i in source_ids)
 assert by_id[10577]['nutrients']['calories']*2==120 and by_id[10577]['nutrients']['sodiumMg']*2==150
 assert number('<1')==(None,{'operator':'<','value':1.0,'raw':'<1'})
 assert number('—')==(None,None) and number(0)==(0,None)
 if SOURCE.exists():
  groups,digest=source_groups();assert digest==out['source']['sha256'],'Private snapshot hash mismatch'
  source_rows={}
  for g in groups:
   for parent in g['items']:
    for row in parent['sub_items'] or [parent]:source_rows[(g['menu'],parent['ID'],row['ID'])]=row
  for r in out['records']:
   raw=source_rows[(r['source']['group'],r['source']['parentId'],r['source']['id'])]
   assert r['rawPublishedValues']=={f['label']:f['value'] for f in raw['fields']}
 print(f'PASS curated schema/raw values, {len(ids)} unique menu rows, null/bounds, size/sugar and three portion arithmetic regressions; private source snapshot '+('hash and rows verified' if SOURCE.exists() else 'unavailable (historical browser evidence retained, no fresh retrieval claimed)'))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--validate',action='store_true');args=ap.parse_args()
 if args.validate:
  output=json.loads(OUT.read_text(encoding='utf-8'));validate(output)
  assert json.loads(PUBLIC.read_text(encoding='utf-8'))==output,'Public catalogue diverges'
 else:build()
