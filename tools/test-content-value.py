from pathlib import Path
from html import unescape
import re
from strengthen_meal_comparisons import CHOICES
from build_restaurant_pages import parse_meals
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
meals=parse_meals()
for chain,(_,a,b,_,_) in CHOICES.items():
 pair=[next(m for m in meals if m['chain']==chain and m['name']==name) for name in (a,b)]
 text=(ROOT/pair[0]['url']).read_text(encoding='utf-8');d=Document(text)
 section=next(n for n in d.nodes if n['attrs'].get('id')=='ordering-comparison')
 content=text[section['inner']:section['close']]
 assert content.count('<tr>')==3,chain
 assert content.count('Restaurant nutrition source')==2,chain
 for m in pair:
  assert m['name'] in unescape(content),m['name']
  for key,unit in [('cal',''),('p',' g'),('f',' g'),('na',' mg')]:
   value='—' if m.get(key) is None else f'{m[key]:,g}'+unit
   assert '<td>'+value+'</td>' in content,(chain,key,value)
 assert 'class="pick-card"' not in text,chain
 assert 'This is not a new verification of restaurant data' in content
for p in ROOT.glob('*.html'):
 t=p.read_text(encoding='utf-8')
 assert not ('class="reading-contents"' in t and '<!-- reading-map:start -->' in t),p.name
t=(ROOT/'body-recomposition-explained.html').read_text(encoding='utf-8')
for i in range(1,7):assert f'id="guide-section-{i}"' in t
assert 'not results from a GetMacros experiment' in t
assert 'Fat or carbohydrate values can still be unverified' in (ROOT/'sources.html').read_text(encoding='utf-8')
print('PASS: 15 comparisons match source records; missing values retained; duplicate menus absent; article anchors and methodology intact.')
