"""Source/structure regression for shared homes; does not claim visual review."""
from pathlib import Path
import json,sys,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_master_interface import countries,market_file,featured
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records'];architecture=None
for code,info in countries().items():
 text=market_file(info).read_text(encoding='utf-8');doc=Document(text)
 main=next(n for n in doc.nodes if n['tag']=='main');assert main['attrs']['data-home-template']=='shared-market-v1'
 sections=[n['attrs'].get('class') for n in doc.nodes if n['tag']=='section' and n['start']>main['start'] and n['end']<main['end']]
 if architecture is None:architecture=sections
 else:assert sections==architecture,(code,'template divergence')
 assert len([n for n in doc.nodes if n['tag']=='h1'])==1
 cards=[n for n in doc.nodes if 'data-home-record' in n['attrs']]
 assert len(cards)==len(featured([r for r in records if r['market']==code]))
 for n in cards:
  assert n['attrs']['data-record-market']==code
  key=n['attrs']['data-home-record'];row=next(r for r in records if r['market']==code and (r.get('id') or r['restaurantMarketId']+'|'+r['name'])==key)
  card=text[n['inner']:n['close']]
  assert f'{row["cal"]:g}<span> kcal' in card
  assert f'{row["p"]:g}<span> g' in card
  assert row['source'].replace('&','&amp;') in card
 form=doc.find(cls='home-finder-entry');assert form['attrs']['action']==info['finder']
 choices=[n for n in doc.nodes if 'data-country-choice' in n['attrs']]
 assert len(choices)==len(countries())
 assert not doc.find(cls='country-panel')['attrs'].get('data-country-form')
 assert 'data-theme-choice="light"' in text and 'data-theme-choice="dark"' in text
 assert 'data-country-select' not in text
 assert len(re.findall(r'<link rel="canonical"',text))==1
 canonical='https://getmacros.net'+info['home'];assert 'rel="canonical" href="'+canonical+'"' in text
print('PASS: eight shared home structures, exact market/record/portion values, country links, appearance choices and canonicals.')
