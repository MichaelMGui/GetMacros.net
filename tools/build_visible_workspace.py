"""Recompose the shared homepage and diary without changing food data or storage."""
from pathlib import Path
import re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]

def swap(text,cls,value):
    node=Document(text).find(cls=cls)
    return text[:node['start']]+value+text[node['end']:] if node else text

def build():
    for p in [ROOT/'index.html',*ROOT.glob('*/en/index.html')]:
        text=p.read_text(encoding='utf-8')
        if 'data-home-template=' not in text:continue
        text=text.replace('class="market-home"','class="market-home home-composed"')
        text=text.replace('<h1>Find a meal<br>that fits.</h1>','<h1>Find a meal.<br><span>That fits you.</span></h1>')
        text=text.replace('Compare restaurant meals by calories, protein, carbs and fat.','Compare restaurant orders by calories, protein, carbs and fat.')
        text=text.replace('<div class="hero-copy"><h1>','<div class="hero-copy"><h1>')
        # One coherent finder bar replaces stacked fields and competing actions.
        form=next((n for n in Document(text).nodes if 'home-finder-entry' in n['attrs'].get('class','').split()),None)
        if form:
            old=text[form['start']:form['end']]
            old=old.replace('Calories, up to','Max. calories').replace('Protein, at least (g)','Min. protein (g)').replace('Find my meal','Find a meal')
            text=text[:form['start']]+text[form['end']:]
            hero=Document(text).find(cls='food-hero')
            text=text[:hero['end']-10]+old+text[hero['end']-10:]
        scene=Document(text).find(cls='market-scene')
        if scene:
            art='''<svg class="market-scene" viewBox="0 0 500 390" aria-hidden="true"><path class="scene-canopy" d="M78 315V158C78 54 169 31 250 31s172 23 172 127v157Z"/><circle class="scene-sun" cx="356" cy="105" r="37"/><path class="scene-stem" d="M52 310q-8-69 22-115m373 116q7-72-24-113"/><path class="scene-leaf" d="M61 261c-32-4-39-28-22-37 21 1 27 19 22 37Zm0-22c0-29 18-43 33-34 3 20-12 33-33 34Zm375 21c29-7 34-29 18-37-18 4-25 20-18 37Zm-2-22c-1-27-19-40-32-30-1 18 12 30 32 30Z"/><ellipse class="scene-plate" cx="250" cy="330" rx="200" ry="30"/><ellipse class="scene-plate-line" cx="250" cy="330" rx="167" ry="19"/></svg>'''
            text=text[:scene['start']]+art+text[scene['end']:]
        text=text.replace('<h2>On the menu</h2>','<h2>A few good orders.</h2>')
        text=text.replace('<h2>Your usual spot?</h2>','<h2>Start with your usual.</h2>')
        for n in reversed([n for n in Document(text).nodes if n['tag']=='link' and (n['attrs'].get('data-source-path')=='css/home-workspace.css' or n['attrs'].get('href','').split('?')[0]=='/css/home-workspace.css')]):
            text=text[:n['start']]+text[n['end']:]
        text=text.replace('</head>','<link rel="stylesheet" href="/css/home-workspace.css"></head>',1)
        p.write_text(text,encoding='utf-8')

    p=ROOT/'food-diary.html';text=p.read_text(encoding='utf-8')
    # Render safely from either fresh generator output or an existing workspace.
    if 'class="food-app diary-app diary-workspace"' in text:
        return
    text=text.replace('class="food-app diary-app"','class="food-app diary-app diary-workspace"')
    doc=Document(text)
    header=doc.find(cls='diary-header');fragment=text[header['start']:header['end']]
    buddy=Document(fragment).find(cls='food-companion');buddy_html=fragment[buddy['start']:buddy['end']] if buddy else ''
    dates=Document(fragment).find(cls='diary-date-tools');dates_html=fragment[dates['start']:dates['end']] if dates else ''
    summary=doc.find(cls='diary-summary');summary_html=text[summary['start']:summary['end']]
    log=doc.find(cls='diary-log');log_html=text[log['start']:log['end']]
    end=log['end']
    # This replaces the complete old workspace, leaving dialogs and their hooks intact.
    start=header['start']
    workspace='''<header class="diary-header"><div><p class="diary-private-label"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg> Your private food diary</p><h1 data-diary-title>Today’s food.</h1></div><button class="btn btn-primary" type="button" data-diary-add><span aria-hidden="true">+</span> Add food</button></header>'''+dates_html+'''<div class="diary-columns"><div class="diary-main"><div class="diary-log-heading"><h2>Your meals</h2><span>Breakfast to bedtime</span></div>'''+log_html+'''</div><aside class="diary-overview" aria-label="Daily overview"><div class="diary-overview-heading"><div><h2>Day at a glance</h2><p data-diary-empty-day>One meal at a time.</p></div>'''+buddy_html+'''</div>'''+summary_html+'''<p class="diary-storage-note">Saved on this device. Just for you.</p><nav class="diary-quick-tools" aria-label="Diary tools"><button class="text-action" type="button" data-repeat-open>Repeat a meal <span aria-hidden="true">↗</span></button><button class="text-action" type="button" data-open-recipes>Your recipes <span aria-hidden="true">↗</span></button><button class="text-action" type="button" data-open-preferences>Preferences &amp; backups <span aria-hidden="true">↗</span></button></nav></aside></div>'''
    text=text[:start]+workspace+text[end:]
    browse=Document(text).find(cls='diary-food-browse')
    if browse and browse['tag']=='div':
        fragment=text[browse['start']:browse['end']]
        fragment=fragment.replace('<div class="diary-food-browse"','<details class="diary-food-browse"',1)
        fragment=fragment.replace('hidden>','hidden><summary>Browse food categories</summary>',1)
        fragment=fragment[:-6]+'</details>'
        text=text[:browse['start']]+fragment+text[browse['end']:]
    text=text.replace('placeholder="Try rice, Kirkland or a barcode"','placeholder="Food, brand or barcode"')
    text=text.replace('Search a food, brand or barcode, or browse the everyday foods below.','')
    text=text.replace('Country for menus &amp; packages','Country')
    text=text.replace('>Saved orders</button>','>Saved</button>')
    p.write_text(text,encoding='utf-8')
    print('Recomposed all market homepages and the private diary workspace.')

if __name__=='__main__':build()
