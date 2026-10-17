"""Structural regressions; browser evidence is recorded separately."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from normalize_calculator_layouts import Document
from build_master_interface import countries,market_file
ROOT=Path(__file__).resolve().parents[1]
for code,info in countries().items():
    text=market_file(info).read_text(encoding='utf-8');doc=Document(text)
    hero=doc.find(cls='food-hero');form=doc.find(cls='home-finder-entry');art=doc.find(cls='food-ensemble')
    assert 'home-composed' in text and hero['start']<art['end']<=form['start']<hero['end'],code
    assert form['attrs']['action']==info['finder'],code
    assert text.count('name="maxCal"')==1 and text.count('name="minProtein"')==1,code
    assert text.count('data-home-market="'+code+'"')==1,code
text=(ROOT/'food-diary.html').read_text(encoding='utf-8');doc=Document(text)
assert 'diary-workspace' in text
assert doc.find(cls='diary-header')['end']<=doc.find(cls='diary-date-tools')['start']<doc.find(cls='diary-columns')['start']
for hook in ['data-diary-add','data-diary-date','data-diary-entries','data-diary-totals','data-repeat-open','data-open-recipes','data-open-preferences','data-diary-empty-day']:
    assert len([n for n in doc.nodes if hook in n['attrs']])==1,hook
assert doc.find(cls='diary-food-browse')['tag']=='details'
assert not doc.find(cls='diary-food-browse')['attrs'].get('open')
assert text.count('id="food-picker"')==1 and text.count('id="food-review"')==1
assert 'Install GetMacros' not in text
print('PASS: eight shared finder compositions; single diary hooks, dialogs, private workspace and native category disclosure.')
