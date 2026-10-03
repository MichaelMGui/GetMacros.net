from pathlib import Path
from html import unescape
import re
from strengthen_meal_comparisons import CHOICES
from build_restaurant_pages import parse_meals
from normalize_calculator_layouts import Document
from meal_provenance import read
ROOT=Path(__file__).resolve().parents[1]
meals=parse_meals()
provenance=read(ROOT/'js/meal-provenance.js')
for chain,(_,a,b,_,_) in CHOICES.items():
 pair=[next(m for m in meals if m['chain']==chain and m['name']==name) for name in (a,b)]
 text=(ROOT/pair[0]['url']).read_text(encoding='utf-8');d=Document(text)
 section=next(n for n in d.nodes if n['attrs'].get('id')=='ordering-comparison')
 content=text[section['inner']:section['close']]
 assert content.count('<tr>')==3,chain
 table=Document(content)
 rows=[n for n in table.nodes if n['tag']=='tr' and n['parent']['tag']=='tbody']
 assert len(rows)==2,chain
 for row,m in zip(rows,pair):
  rendered=content[row['inner']:row['close']]
  assert m['name'] in unescape(rendered),m['name']
  cells=[n for n in table.nodes if n['tag']=='td' and n['parent'] is row]
  expected=['—' if m.get(key) is None else f'{m[key]:,g}' for key in ('cal','p','f','na')]
  actual=[unescape(content[n['inner']:n['close']]) for n in cells]
  assert actual==expected,(chain,m['name'],actual,expected)
  record=provenance[chain+'||'+m['name']]
  assert record['serving'] in unescape(rendered),(chain,'portion')
  urls={record['source']}|{r['source'] for r in record.get('nutrientProvenance',{}).values() if r.get('source')}
  for url in urls:assert url in unescape(rendered),(chain,'source',url)
  dates={r['retrieved'] for r in record.get('nutrientProvenance',{}).values() if r.get('retrieved')} or {record['checked']}
  for date in dates:assert date in rendered,(chain,'inspection date',date)
 for label in ('Protein (g)','Fiber (g)','Sodium (mg)'):assert label in content,(chain,'units',label)
 assert 'class="pick-card"' not in text,chain
 assert 'Before you order' in content and 'Included items and sources' in content,chain
for p in ROOT.glob('*.html'):
 t=p.read_text(encoding='utf-8')
 assert not ('class="reading-contents"' in t and '<!-- reading-map:start -->' in t),p.name
t=(ROOT/'body-recomposition-explained.html').read_text(encoding='utf-8')
for i in range(1,7):assert f'id="guide-section-{i}"' in t
assert 'not results from a GetMacros experiment' in t
assert 'Fat or carbohydrate values can still be unverified' in (ROOT/'sources.html').read_text(encoding='utf-8')
print('PASS: 15 comparisons match source records; missing values retained; duplicate menus absent; article anchors and methodology intact.')
