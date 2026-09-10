"""Original inline illustrations and semantic colour families, with no image requests."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
ART={
 'meal':'<ellipse cx="80" cy="85" rx="55" ry="6" class="art-shadow"/><circle cx="80" cy="48" r="38" class="art-paper"/><circle cx="80" cy="48" r="29" class="art-leaf"/><path d="M80 19a29 29 0 0 1 0 58Z" class="art-orange"/><circle cx="67" cy="39" r="9" class="art-blue"/><circle cx="67" cy="57" r="9" class="art-berry"/><path d="M25 19v20m-6-20v14q0 12 12 0V19M25 40v40M134 19v61m0-61q-13 15 0 26" class="art-line"/>',
 'tools':'<ellipse cx="80" cy="88" rx="42" ry="5" class="art-shadow"/><rect x="43" y="7" width="74" height="79" rx="13" class="art-paper"/><rect x="54" y="18" width="52" height="21" rx="5" class="art-leaf"/><path d="M85 25h13m-13 7h13" class="art-cut"/><g class="art-blue"><rect x="54" y="49" width="13" height="11" rx="3"/><rect x="74" y="49" width="13" height="11" rx="3"/><rect x="54" y="67" width="13" height="11" rx="3"/><rect x="74" y="67" width="13" height="11" rx="3"/></g><rect x="94" y="49" width="13" height="29" rx="4" class="art-orange"/>',
 'labels':'<rect x="20" y="15" width="53" height="72" rx="9" class="art-paper"/><rect x="86" y="7" width="53" height="72" rx="9" class="art-paper"/><rect x="29" y="25" width="35" height="13" rx="3" class="art-leaf"/><rect x="95" y="17" width="35" height="13" rx="3" class="art-blue"/><path d="M30 48h32m-32 10h23m-23 10h28M96 40h32m-32 10h23m-23 10h28" class="art-line"/><circle cx="127" cy="79" r="13" class="art-orange"/><path d="m121 79 4 4 8-8" class="art-line"/>',
 'learn':'<path d="M26 20q25-10 54 4 29-14 54-4v60q-27-8-54 3-27-11-54-3Z" class="art-paper"/><path d="M26 20q25-10 54 4v59q-27-11-54-3Z" class="art-leaf"/><path d="M94 22v24l9-6 9 6V20Z" class="art-orange"/><path d="M39 38h25m-25 13h25m-25 13h17" class="art-cut"/><path d="M95 58h25m-25 12h19M80 27v52" class="art-line"/>',
 'site':'<rect x="34" y="9" width="65" height="76" rx="10" class="art-paper"/><path d="M47 28h37m-37 12h29m-29 12h25" class="art-line"/><path d="m105 35 25 9v19q-1 17-25 26-24-9-25-26V44Z" class="art-leaf"/><path d="m94 61 8 8 16-17" class="art-cut"/>',
 'contact':'<rect x="23" y="25" width="112" height="59" rx="12" class="art-leaf"/><path d="m27 30 52 34 52-34" class="art-cut"/><rect x="43" y="7" width="74" height="42" rx="9" class="art-paper"/><path d="M56 21h47m-47 13h32" class="art-line"/><circle cx="131" cy="24" r="15" class="art-orange"/><path d="m124 24 5 5 9-10" class="art-line"/>',
 'search':'<circle cx="70" cy="40" r="30" class="art-paper"/><circle cx="70" cy="40" r="20" class="art-blue"/><path d="m91 63 24 22" stroke-width="12" class="art-line"/><path d="M59 40h22m-11-11v22" class="art-cut"/><circle cx="125" cy="23" r="9" class="art-orange"/>',
 'cost':'<path d="M35 31h72l8 55H27Z" class="art-paper"/><path d="M48 32V23a23 23 0 0 1 46 0v9" class="art-line"/><path d="M47 44h47v29H47Z" class="art-leaf"/><circle cx="118" cy="65" r="24" class="art-orange"/><path d="M123 54h-8a5 5 0 0 0 0 10h5a5 5 0 0 1 0 10h-9m7-24v28" class="art-line"/>'
}
ART.update({
 'sodium':'<ellipse cx="80" cy="89" rx="40" ry="5" class="art-shadow"/><path d="M55 34h50l9 44a8 8 0 0 1-8 9H54a8 8 0 0 1-8-9Z" class="art-paper"/><path d="M55 34V23a25 16 0 0 1 50 0v11Z" class="art-blue"/><path d="M67 22h1m11-3h1m11 3h1" class="art-cut"/><rect x="60" y="48" width="40" height="24" rx="6" class="art-leaf"/><path d="M69 56h1m9 5h1m8-5h1m-19 9h1m17 1h1" class="art-cut"/><circle cx="129" cy="59" r="3" class="art-orange"/><circle cx="134" cy="74" r="3" class="art-orange"/><circle cx="124" cy="83" r="3" class="art-orange"/>',
 'carbs':'<ellipse cx="82" cy="88" rx="51" ry="5" class="art-shadow"/><path d="M35 76V43q-12-4-10-16 2-18 25-18h54q25 0 26 18 1 12-12 16v33q0 9-10 9H45q-10 0-10-9Z" class="art-orange"/><path d="M46 71V37q-9-2-9-9 0-8 16-8h48q16 0 17 8 0 7-11 9v34q0 4-5 4H51q-5 0-5-4Z" class="art-paper"/><path d="M59 38v20m17-24v20m17-16v20" class="art-line"/><path d="M118 70q-2-18 21-22 0 23-21 22Z" class="art-leaf"/>',
 'timeline':'<ellipse cx="80" cy="90" rx="50" ry="4" class="art-shadow"/><rect x="31" y="15" width="98" height="70" rx="12" class="art-paper"/><path d="M43 15h74q12 0 12 12v9H31v-9q0-12 12-12Z" class="art-leaf"/><path d="M51 9v15m58-15v15" class="art-line"/><path d="M47 65 67 54l20 7 25-16" class="art-line"/><circle cx="47" cy="65" r="5" class="art-blue"/><circle cx="67" cy="54" r="5" class="art-blue"/><circle cx="87" cy="61" r="5" class="art-blue"/><circle cx="112" cy="45" r="8" class="art-orange"/>',
 'sweat':'<ellipse cx="79" cy="90" rx="47" ry="4" class="art-shadow"/><rect x="81" y="10" width="25" height="12" rx="4" class="art-leaf"/><path d="M81 22h25l9 16v41q0 8-9 8H81q-9 0-9-8V38Z" class="art-paper"/><path d="M79 54q10-7 29 0v24q0 3-4 3H83q-4 0-4-3Z" class="art-blue"/><path d="M91 35h10m-10 10h10" class="art-line"/><path d="M41 23Q17 52 23 64q5 12 18 12t18-12q6-12-18-41Z" class="art-blue"/><path d="M32 56q-2 9 7 11" class="art-cut"/>'
})
def art(kind):
 drawing=ART[kind]
 if kind=='meal':drawing=drawing.replace('class="art-line"','class="art-edge"')
 if kind=='search':drawing=drawing.replace('stroke-width="12" class="art-line"','class="art-edge"')
 if kind=='cost':drawing=drawing.replace('v9" class="art-line"','v9" class="art-edge"')
 return '<svg class="colour-art" viewBox="0 0 160 100" aria-hidden="true" focusable="false">'+drawing+'</svg>'
def kind_for(name):
 if 'sodium-label' in name:return 'sodium'
 if 'carbohydrate-label' in name:return 'carbs'
 if 'weight-goal-timeline' in name:return 'timeline'
 if 'sweat-rate' in name:return 'sweat'
 if 'protein-value' in name:return 'cost'
 if any(x in name for x in ['label','portion','recipe-macro']):return 'labels'
 if any(x in name for x in ['calculator','sweat-rate']):return 'tools'
 if any(x in name for x in ['restaurant','fast-food','meal-builder','high-protein-foods','balanced-meal']):return 'meal'
 if name=='contact.html':return 'contact'
 if name=='search.html':return 'search'
 if name in ['privacy.html','terms.html','accessibility.html','corrections.html','editorial-policy.html','sources.html','about.html','404.html']:return 'site'
 return 'learn'
def run():
 for p in ROOT.glob('*.html'):
  s=p.read_text(encoding='utf-8');kind=kind_for(p.name)
  tone='blue' if kind in ['tools','labels','search'] or 'protein' in p.name else 'orange' if kind in ['cost','contact'] or any(x in p.name for x in ['carb','fat','calorie']) else 'berry' if any(x in p.name for x in ['creatine','diet-drinks']) else 'leaf'
  s=re.sub(r' data-page-tone="[^"]*"','',s);s=s.replace('<body','<body data-page-tone="'+tone+'"',1)
  s=re.sub(r'(<span class="(?:page-emblem|suite-hero-mark)"[^>]*>).*?</span>',lambda m:m[1]+art(kind)+'</span>',s,flags=re.S)
  def tool(m):
   block=m[0];url=re.search(r'href="([^"]+)"',block)[1]
   return re.sub(r'(<span class="clarity-icon"[^>]*>).*?</span>',lambda n:n[1]+art(kind_for(url))+'</span>',block,flags=re.S)
  s=re.sub(r'<a class="clear-tool-card"[^>]*>.*?</a>',tool,s,flags=re.S)
  if p.name=='index.html':
   from refine_homepage_finish import refine_homepage
   s=refine_homepage(s)
   s=s.replace('Use what you have','Simple meal ideas').replace('Get meal ideas from ingredients in your kitchen.','Six easy meals to make at home.')
   glyphs=iter(['<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M9 4v16m6-16v16M3 12h18"/>','<path d="m3 12 9-9h8v8l-9 10Z"/><circle cx="16" cy="7" r="1"/><path d="m8 13 4 4m-6-2 4 4"/>','<circle cx="12" cy="12" r="7"/><path d="M2 3v7m-1-7v4q1 4 3 0V3M2 10v11M22 3v18m0-18q-4 5 0 8"/>'])
   s=re.sub(r'(<span class="home-everyday-icon">).*?</span>',lambda m:m[1]+'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'+next(glyphs)+'</svg></span>',s,flags=re.S)
  if p.name=='search.html':
   def card(m):
    block=re.sub(r'<span class="colour-tile-art".*?</span>','',m[0],flags=re.S)
    kind='meal' if 'restaurant-meal-finder.html' in block else 'tools' if 'calculators.html' in block else 'learn'
    return block.replace('>','><span class="colour-tile-art" aria-hidden="true">'+art(kind)+'</span>',1)
   s=re.sub(r'<a class="search-start-tile"[^>]*>.*?</a>',card,s,flags=re.S)
  if p.name=='about.html':
   sequence=iter(['meal','tools','labels'])
   s=re.sub(r'(<article><span class="clear-icon"[^>]*>).*?</span>',lambda m:m[1]+art(next(sequence))+'</span>',s,flags=re.S)
  if re.search(r'<link rel="stylesheet" href="css/site-refresh\.css',s):
   s=re.sub(r'<link rel="stylesheet" href="css/colour-system\.css(?:\?[^\"]*)?"[^>]*>','',s)
   s=re.sub(r'(<link rel="stylesheet" href="css/site-refresh\.css(?:\?[^\"]*)?"[^>]*>)',r'\1<link rel="stylesheet" href="css/colour-system.css">',s,count=1)
  p.write_text(s,encoding='utf-8')
if __name__=='__main__':run()
