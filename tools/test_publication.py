"""Validate the delivered rebuild, not the historical content-generator CSS."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,csv
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for path in ROOT.glob('*.html'):
 text=path.read_text(encoding='utf-8');doc=Document(text)
 styles=[n['attrs']['href'].split('?')[0] for n in doc.nodes if n['tag']=='link' and n['attrs'].get('rel')=='stylesheet']
 assert styles==['css/publication.css'],(path.name,styles)
 scripts=[n['attrs'].get('src','') for n in doc.nodes if n['tag']=='script']
 assert not any('adsbygoogle' in s or re.search(r'js/(main|tide-motion|lang)\.js',s) for s in scripts),path.name
 assert 'data-ads="off"' in text and 'data-publication="2026-09"' in text,path.name
 ids=[n['attrs']['id'] for n in doc.nodes if 'id' in n['attrs']]
 assert len(ids)==len(set(ids)),path.name
 assert len([n for n in doc.nodes if n['tag']=='h1'])==1,path.name
 assert text.count('data-theme-toggle')==1,path.name
 main=next(n for n in doc.nodes if n['tag']=='main')
 content=text[main['inner']:main['close']]
 plain=re.sub('<[^>]+>',' ',content)
 source_count=len(re.findall(r'href="https://(?!getmacros.net)',content))
 words=len(plain.split())
 family='tool' if any(x in content for x in ['<form','data-focused-calculator','id="meal-quiz"']) else 'guide' if 'article-container' in content else 'directory / publisher'
 rows.append({'page':path.name,'type':family,'visible_words':words,'external_sources':source_count,'disposition':'Retained; worked example added' if 'id="worked-comparison"' in text else 'Retained; source body preserved, layout rebuilt','follow_up':'Recheck source freshness before changing any nutrient/date' if family=='guide' else 'Maintain tool/data functionality'})
 if 'js/meal-data.js' in text:
  assert text.index('js/meal-data.js')<text.index('js/meal-provenance.js'),path.name
css=(ROOT/'css/publication.css').read_text(encoding='utf-8')
assert len(css.encode())<55000
assert 'prefers-reduced-motion:reduce' in css and 'html[data-theme=dark]' in css
assert 'google.com, pub-2316153877942502, DIRECT, f08c47fec0942fa0' in (ROOT/'ads.txt').read_text()
with (ROOT/'docs/publication-page-audit.csv').open('w',encoding='utf-8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
print(f'Publication: {len(rows)} pages; single stylesheet ({len(css.encode()):,} bytes), preserved verification, no automatic ad loader, unique IDs, theme controls and provenance ordering passed.')
