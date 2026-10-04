"""Original food-category symbols, not reproductions of restaurant trademarks."""
from html import escape
import json,re
from pathlib import Path
SHAPES={
 'bowl':'<path d="M3 11h18a9 9 0 0 1-18 0Zm4 9h10M7 8c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5"/>',
 'sandwich':'<path d="M3 9c0-4 4-6 9-6s9 2 9 6H3Zm0 6h18v2a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-2Zm0-3 4 1 5-1 5 1 4-1M8 6h.01M12 5h.01M16 6h.01"/>',
 'chicken':'<path d="M8 15c-4-2-4-7-1-10s8-3 10 0 1 7-3 9l-3 1-4 4a2 2 0 1 1-3-3l4-1Zm3-8 3-1"/>',
 'cup':'<path d="M5 8h12v9a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V8Zm12 1h2a3 3 0 0 1 0 6h-2M8 5V2m5 3V2M3 22h17"/>',
 'sub':'<path d="m4 10 10-6a4 4 0 0 1 5 6L9 17a4 4 0 0 1-5-7Zm0 5 1 4a4 4 0 0 0 5 1l10-7 1-4M9 7l3 2m2-5 3 2M6 13l3 1 3-3 3 1 3-3"/>',
 'taco':'<path d="M3 19a9 9 0 0 1 18 0H3Zm3-2 2-2 3 1 3-2 3 2m-9-5 1 1m5-2 1 1"/>',
 'leaf':'<path d="M5 16C2 6 13 3 20 4c0 9-4 16-12 14m-4 3L16 9m-7 7V9m4 3h5"/>',
}
MARKS={'CAVA':('cava','bowl'),'Chick-fil-A':('chick-fil-a','chicken'),'Chipotle':('chipotle','bowl'),'Dunkin’':('dunkin','cup'),'Jersey Mike’s':('jersey-mikes','sub'),'KFC':('kfc','chicken'),'McDonald’s':('mcdonalds','sandwich'),'Panda Express':('panda-express','bowl'),'Panera':('panera','sub'),'Popeyes':('popeyes','chicken'),'Starbucks':('starbucks','cup'),'Subway':('subway','sub'),'Sweetgreen':('sweetgreen','leaf'),'Taco Bell':('taco-bell','taco'),'Wendy’s':('wendys','sandwich')}
MARKS.update({'Arby’s':('arbys','sandwich'),'SONIC':('sonic','sandwich'),
 'QDOBA':('qdoba','bowl'),'El Pollo Loco':('el-pollo-loco','chicken'),
 'Del Taco':('del-taco','taco'),'Noodles & Company':('noodles-and-company','bowl'),
 'Culver’s':('culvers','sandwich'),'Taco John’s':('taco-johns','taco'),
 'In-N-Out':('in-n-out','sandwich'),'Raising Cane’s':('raising-canes','chicken')})
def mark(chain):
 return '<span class="restaurant-mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'+SHAPES[MARKS[chain][1]]+'</svg></span>'
def run():
 root=Path(__file__).resolve().parents[1]
 for p in root.glob('*.html'):
  text=p.read_text(encoding='utf-8')
  for chain,(slug,_) in MARKS.items():
   text=re.sub(r'<img\b[^>]*src="images/restaurant-marks/'+slug+r'\.svg[^>]*>',mark(chain),text)
  p.write_text(text,encoding='utf-8')
 p=root/'js/meal-finder.js';s=p.read_text(encoding='utf-8')
 code='  const restaurantMarks='+json.dumps({c:mark(c) for c in MARKS},ensure_ascii=False,separators=(',',':'))+';\n  function restaurantMark(chain){return restaurantMarks[chain]||"";}\n'
 s=s.replace('  const chains =',code+'  const chains =',1)
 s=s.replace("<span>'+esc(label)+'</span>","'+(k==='chain'?restaurantMark(v):'')+'<span>'+esc(label)+'</span>")
 p.write_text(s,encoding='utf-8')
if __name__=='__main__':run()
