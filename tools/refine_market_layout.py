from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'tools/market-system.css';s=p.read_text(encoding='utf-8')
s=s.replace('font-size:clamp(3.2rem,6.8vw,6.4rem)','font-size:clamp(3rem,5vw,4.8rem)').replace('.market-welcome h1{font-size:4rem}', '.market-welcome h1{font-size:3rem}')
s=s.replace('.finder-shell{min-height:80svh}', '.finder-shell{min-height:80svh;padding-block:10px 35px}')
s=s.replace('.finder-introduction{padding-block:30px 20px}', '.finder-introduction{padding-block:20px 12px}')
s=s.replace('.filter-deck{background:', '.filter-deck{position:relative;background:')
s=s.replace('.filter-panel-head h2{font-size:1.2rem;margin-bottom:20px}', '.filter-panel-head h2{font-size:1.2rem;margin-bottom:20px}.finder-shell .filter-deck .filter-panel-head{display:none}')
s=s.replace('.filter-reset p{font-size:.78rem;color:var(--muted);margin:0}', '.filter-reset p{display:none}')
s=s.replace('.filter-launch{margin-left:auto}', '.filter-launch{margin-left:auto;display:none!important}')
s=s.replace('@media(max-width:900px){html', '@media(max-width:800px){.finder-shell .filter-deck{display:none}.filter-launch{display:inline-flex!important}}\n@media(max-width:900px){html')
p.write_text(s,encoding='utf-8')
# Tests keep the business assertions and follow the new disclosure structure.
p=r/'tools/test-edition-finder.cjs';s=p.read_text(encoding='utf-8').replace("hasText:'Fiber & sodium'","hasText:'More preferences'");p.write_text(s,encoding='utf-8')
p=r/'tools/test-botanical-routes.cjs';s=p.read_text(encoding='utf-8').replace("check.design!=='edition'","check.design!=='market'");p.write_text(s,encoding='utf-8')
