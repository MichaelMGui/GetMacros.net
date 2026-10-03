"""Apply inspected source values and rebuild derived tags without legacy pages."""
from pathlib import Path
import json,re
from build_meal_finder import parse_meals, goal_tags, write_tags
ROOT=Path(__file__).resolve().parents[1]
def run():
 patches=json.loads((ROOT/'docs/release-2026-10-03/data-audited-patches.json').read_text(encoding='utf-8'))['records']
 path=ROOT/'js/meal-data.js';text=path.read_text(encoding='utf-8')
 for patch in patches:
  chain,name=patch['recordKey'].split('||')
  # Match the same full object syntax consumed by the data parser.
  found=False
  for match in list(re.finditer(r'\{chain:.*?\},?',text,re.S)):
   block=match.group(0)
   parsed=parse_meals('window.GM_MEALS = [\n'+block.rstrip(',')+'\n];')
   if not parsed or parsed[0]['chain']!=chain or parsed[0]['name']!=name:continue
   replacement=block
   for k,value in patch['values'].items():
    if k=='fat':continue # Fat belongs to the provenance layer; f is fiber.
    replacement,count=re.subn(r'\b'+k+r':(?:null|[\d.]+)',k+':'+('null' if value is None else str(value)),replacement,count=1)
    if count!=1:raise ValueError('Missing nutrient '+patch['recordKey']+' '+k)
   text=text[:match.start()]+replacement+text[match.end():];found=True;break
  if not found:raise ValueError('Unmatched source record '+patch['recordKey'])
 meals=parse_meals(text)
 for meal in meals:meal['t']=goal_tags(meal)
 text=write_tags(text,meals);path.write_text(text,encoding='utf-8')
 records=json.loads((ROOT/'tools/restaurant-review.json').read_text(encoding='utf-8'))
 bykey={r['recordKey']:r for r in patches}
 for r in records:
  p=bykey.get(r['chain']+'||'+r['name'])
  if p:
   r['values'].update({k:v for k,v in p['values'].items() if k!='fat'})
   omitted=set(r['values'])-set(p['values'])
   retained={}
   if omitted:
    assert p['recordKey']=='Chick-fil-A||Grilled Nuggets, 12 count' and omitted=={'f','na'}
    retained={k:{'method':'published','source':'https://www.chick-fil-a.com/nutrition-allergens','retrieved':'2026-09-09','status':'retained; not reverified in October inspection'} for k in sorted(omitted)}
   r['nutrientProvenance']={**retained,**p['nutrientProvenance']}
   p['nutrientProvenance']=r['nutrientProvenance']
   r.update(source=p['source'],checked=p['retrievalDate'],sourceDate=p['sourceDate'],serving=p['serving'],nutrientProvenance=p['nutrientProvenance'])
 (ROOT/'tools/restaurant-review.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(f'Applied source patches to {len(patches)} of {len(meals)} records; no uninspected dates refreshed.')
if __name__=='__main__':run()
