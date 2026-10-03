"""Original SVG launch graphics using audited facts, not restaurant photographs."""
from pathlib import Path
from html import escape
import json
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'docs/release-2026-10-03/launch'
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 patches=json.loads((ROOT/'docs/release-2026-10-03/data-audited-patches.json').read_text(encoding='utf-8'))
 data={r['recordKey']:r for r in patches['records']}
 a=data['Chick-fil-A||Grilled Nuggets, 8 count'];b=data['Panda Express||Grilled Teriyaki Chicken']
 sets=[('protein-density','Protein density is not meal size.', 'Compare the protein portion, then add your sides.',[
  ('Chick-fil-A',a['serving'],f"{a['values']['cal']} calories · {a['values']['p']} g protein",f"{a['values']['p']/a['values']['cal']*100:.1f} g protein / 100 calories"),
  ('Panda Express',b['serving'],f"{b['values']['cal']} calories · {b['values']['p']} g protein",f"{b['values']['p']/b['values']['cal']*100:.1f} g protein / 100 calories")],
  'getmacros.net/protein-density-fast-food.html','Selected U.S. portions. Extra sauces, sides and drinks excluded.'),
 ('panda-bases','The base changes your order.', 'Compare full Panda Express base portions.',[
  ('White steamed rice','12 oz base','570 calories · 11 g protein','129 g carbs · 0 g fiber'),
  ('Super Greens','10 oz base','180 calories · 8 g protein','17 g carbs · 8 g fiber')],
  'getmacros.net/panda-express-base-nutrition-comparison.html','Unequal base weights shown deliberately. Entrées and extras excluded.')]
 # All base facts asserted against inspected ingredient values in the patch.
 ingredients=patches['ingredients']['Panda Express']['values']
 assert ingredients['white rice']['cal']==570 and ingredients['super greens base']['cal']==180
 for slug,title,subtitle,rows,url,note in sets:
  blocks=''
  for i,(name,portion,total,secondary) in enumerate(rows):
   x=60+i*555
   blocks+=f'<rect x="{x}" y="220" width="525" height="220" rx="16" fill="#fff" stroke="#dce2d8"/><text x="{x+24}" y="266" font-size="27" font-weight="600">{escape(name)}</text><text x="{x+24}" y="304" font-size="20" fill="#59665d">{escape(portion)}</text><text x="{x+24}" y="356" font-size="27" font-weight="600">{escape(total)}</text><text x="{x+24}" y="396" font-size="21" fill="#276443">{escape(secondary)}</text>'
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><title>{escape(title)}</title><desc>{escape(note)} Facts inspected October 3, 2026; official sources are linked on the reference page.</desc><rect width="1200" height="630" fill="#fffefb"/><g fill="#152d24" font-family="Inter, Arial, sans-serif"><text x="60" y="66" font-size="26" fill="#276443" font-weight="600">GetMacros / Menu notes</text><text x="60" y="132" font-size="44" font-weight="600">{escape(title)}</text><text x="60" y="179" font-size="26" fill="#59665d">{escape(subtitle)}</text>{blocks}<text x="60" y="490" font-size="20">{escape(note)}</text><text x="60" y="544" font-size="21" fill="#276443">{escape(url)}</text><text x="60" y="588" font-size="18" fill="#59665d">Source-linked analysis · Inspected October 3, 2026 · Original graphic</text></g></svg>'
  (OUT/(slug+'.svg')).write_text(svg,encoding='utf-8')
 (OUT/'README.md').write_text('''# Launch package — drafts, not externally posted

Two original SVG graphics use inspected restaurant numbers and label portions. The linked resources provide official sources and limits. These illustrations are not branded restaurant photos. Their typography is designed for a 1200 × 630 social image.

**Protein density:** A small chicken portion can have a high protein-per-calorie ratio without describing a full lunch. Compare the portion and add-ons before choosing. https://getmacros.net/protein-density-fast-food.html

**Panda Express bases:** White steamed rice and Super Greens have different full base weights and nutrient totals. See the portions and build assumptions before comparing your order. https://getmacros.net/panda-express-base-nutrition-comparison.html

No posts, messages, purchases or outreach were sent. Do not present the numeric comparison as a healthiest-food ranking. Check source freshness before later reuse.
''',encoding='utf-8')
 print('Created two original fact-checked SVG social assets and accurate posting drafts; nothing posted.')
if __name__=='__main__':run()
