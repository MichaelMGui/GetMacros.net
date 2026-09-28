from pathlib import Path
p=Path('tools/market_presentation.py');s=p.read_text(encoding='utf-8');needle=" if name=='about.html'";insert=''' if kind=='restaurant' and 'restaurant-menu-sheet' not in text:
  doc=Document(text);menu=next((n for n in doc.nodes if n['attrs'].get('id')=='menu-comparison'),None);picks=next((n for n in doc.nodes if 'chain-picks-section' in n['attrs'].get('class','').split()),None)
  if menu and picks:
   frag=text[menu['start']:menu['end']]
   frag=frag.replace('<details class="restaurant-menu-details">','<div class="restaurant-menu-sheet">').replace('</details>','</div>')
   frag=re.sub(r'<summary><span><small>Complete nutrition table</small><strong>(.*?)</strong></span><b>Open table</b></summary>',r'<div class="section-heading"><div><p class="section-overline">The recorded menu</p><h2>\\1</h2></div></div>',frag,flags=re.S)
   text=text[:menu['start']]+text[menu['end']:]
   text=text[:picks['start']]+frag+text[picks['start']:]
'''
s=s.replace(needle,insert+needle,1);p.write_text(s,encoding='utf-8')
p=Path('tools/market-content.css');s=p.read_text(encoding='utf-8');import re
# Remove superseded global tables, contents positioning and old result rows; the new system owns these.
s=re.sub(r'(?m)^\.(?:macro-result-row|hub-hero|calc-hero-grid|garden-toc\{)[^\n]*\n','',s)
s=re.sub(r'(?m)^(?:table\{|caption\{|th,td\{|th\{|thead\{)[^\n]*\n','',s)
s=s.replace('.chain-finder-layout{display:block}','')
p.write_text(s,encoding='utf-8')
p=Path('tools/market-system.css');s=p.read_text(encoding='utf-8');s=s.replace('button[aria-pressed=true]','button[aria-pressed=true]:not(.theme-toggle)')
s+='''\n.chain-finder-layout{display:grid;grid-template-columns:1fr 2fr;gap:40px;align-items:center}.chain-finder-intro h2{font-size:1.6rem;margin-bottom:12px}.restaurant-entry{display:grid;grid-template-columns:1fr 1fr auto;align-items:end;gap:18px}.restaurant-entry label{margin:0}.restaurant-entry .btn{margin-bottom:2px}.restaurant-menu-sheet{padding:0;background:none}.restaurant-menu-content{padding:0}.restaurant-menu-content>p{max-width:85ch;color:var(--muted);font-size:.92rem}.restaurant-menu-sheet .section-heading h2{font-size:1.8rem}.restaurant-menu-sheet th:first-child{min-width:220px}.restaurant-menu-sheet td:not(:first-child){font-variant-numeric:tabular-nums}.chain-finder-section{background:var(--soft)}.eyebrow{font-size:.78rem;letter-spacing:.03em;color:var(--muted)}
@media(max-width:1050px){.chain-finder-layout{grid-template-columns:1fr}.restaurant-entry{grid-template-columns:1fr 1fr auto}}@media(max-width:640px){.restaurant-entry{grid-template-columns:1fr 1fr;gap:16px}.restaurant-entry .btn{grid-column:1/-1}.chain-finder-layout{gap:18px}}
''';p.write_text(s,encoding='utf-8')
p=Path('tools/test-publication-accessibility.cjs');s=p.read_text();s=s.replace('.home-finder button[type=submit]','.market-feature .btn-primary');p.write_text(s)
p=Path('tools/test-botanical-resilience.cjs');s=p.read_text();s=s.replace(".no-script-nav a').count(),5",".no-script-nav a').count(),4").replace('.home-finder button[type=submit]','#finder-filters [name=maxCal]');p.write_text(s)
p=Path('tools/market-home.inc');s=p.read_text(encoding='utf-8').replace('<p role="status">Preparing your meal list…</p>','<p>Compare restaurant orders by calories and protein.</p>');p.write_text(s,encoding='utf-8')
p=Path('tools/capture-reset.cjs');s=p.read_text();s=s.replace("await page.screenshot({path:dir+'/'+route.split('?')[0]+'-'+theme+'-'+width+'-viewport.png'});", "await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:dir+'/'+route.split('?')[0]+'-'+theme+'-'+width+'-viewport.png'});");p.write_text(s)
