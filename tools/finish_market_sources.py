from pathlib import Path
from market_presentation import LOGO
r=Path(__file__).resolve().parents[1]
p=r/'tools/market-system.css';s=p.read_text(encoding='utf-8').replace('html{scroll-padding-top:150px}','html{scroll-padding-top:150px;scroll-behavior:auto}')
p.write_text(s,encoding='utf-8')
p=r/'tools/validate_site.py';s=p.read_text(encoding='utf-8').replace('content="#f7faf3"','content="#fffefb"');p.write_text(s,encoding='utf-8')
p=r/'js/unified-v7.js';s=p.read_text(encoding='utf-8').replace('"#171c1a" : "#ffffff"','"#101e19" : "#fffefb"');p.write_text(s,encoding='utf-8')
svg=LOGO.replace('<svg viewBox="0 0 40 40" aria-hidden="true">','<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" style="color:#276443">')
for name in ['favicon.svg','images/botanical-mark.svg']:(r/name).write_text(svg,encoding='utf-8')
p=r/'tools/render-botanical-brand.cjs';s=p.read_text(encoding='utf-8').replace('#fbfcf9','#fffefb').replace('#202c26','#152d24').replace('#176d46','#276443').replace('#b6e578','#bed780').replace('Lunch plans.<br>Made simpler.','Fast food.<br>Your macros.')
p.write_text(s,encoding='utf-8')
