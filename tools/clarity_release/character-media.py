"""Focused, idempotent media and game presentation, after shared template builds.

This modifies only the Read & Watch main and existing play header/objective
markup. Character/game JavaScript is owned source; no dataset or score changes.
"""
from pathlib import Path
from html import escape
import json,re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/clarity-release-2026-10-14'
DATE='2026-10-14'
EXTERNAL='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9"/></svg>'

def e(value):return escape(str(value),quote=True)
def icon(kind):
    paths={
      'book':'<path d="M10 8h14a8 8 0 0 1 8 8v38a9 9 0 0 0-8-6H10Zm44 0H40a8 8 0 0 0-8 8v38a9 9 0 0 1 8-6h14Z"/><path d="M17 19h7m-7 9h7m16-9h7m-7 9h7"/>',
      'film':'<rect x="8" y="12" width="48" height="40" rx="5"/><path d="m28 23 13 9-13 9Z"/><path d="M15 12v40m34-40v40M8 21h7m-7 11h7M8 43h7m34-22h7m-7 11h7m-7 11h7"/>',
      'guide':'<path d="M16 8h25l9 9v39H16Z"/><path d="M41 8v10h9M24 27h18m-18 8h18m-18 8h11"/>'}
    return '<svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[kind]+'</svg>'

RESOURCES=[
 {'id':'cooking','kind':'book','type':'Book','title':'Salt, Fat, Acid, Heat','creator':'Samin Nosrat · illustrations by Wendy MacNaughton','edition':'Simon & Schuster · April 25, 2017','description':'A cooking framework for seasoning, texture and heat. Use it to understand what ingredients do; use a food label or reference profile to calculate their macros.','limit':'Cooking instruction, not a nutrition database or clinical guide.','href':'https://www.simonandschuster.net/books/Salt-Fat-Acid-Heat/Samin-Nosrat/9781476753836','action':'View publisher & edition','related':'/recipe-macro-scaler.html','relatedText':'Calculate a recipe portion'},
 {'id':'science','kind':'film','type':'Documentary archive','title':'NOVA: The Truth About Fat','creator':'PBS · NOVA','edition':'Premiered April 8, 2020 · 53 minutes','description':'An introduction to the biology of body fat and the limits of judging it by appearance. Read its scientific claims in their research context.','limit':'PBS lists online streaming as unavailable. Access can differ by region.','href':'https://www.pbs.org/wgbh/nova/video/the-truth-about-fat/','action':'View official episode archive','related':'/diet-patterns-evidence.html','relatedText':'Read diet evidence'},
 {'id':'practical','kind':'guide','type':'Free resource collection','title':'Following DASH','creator':'U.S. National Heart, Lung, and Blood Institute','edition':'Food-group examples, serving guidance and downloadable resources','description':'A public-health collection explaining the DASH eating plan. Its food-group and serving examples can help you understand the plan’s structure.','limit':'General guidance; personal medical advice needs appropriate professional care.','href':'https://www.nhlbi.nih.gov/health/dash/following-dash','action':'Read the official collection','related':'/how-to-read-a-nutrition-label.html','relatedText':'Understand a food label'}]

def media_main():
    cards=[]
    for r in RESOURCES:
        cards.append('<article class="clarity-media-item" id="media-'+e(r['id'])+'"><div class="clarity-media-mark" data-media-kind="'+r['kind']+'" aria-hidden="true">'+icon(r['kind'])+'</div><div class="clarity-media-content"><p class="clarity-media-kind">'+e(r['type'])+'</p><h2><a href="'+e(r['href'])+'">'+e(r['title'])+'</a></h2><p class="clarity-media-credit">'+e(r['creator'])+'</p><p class="clarity-media-edition">'+e(r['edition'])+'</p><p>'+e(r['description'])+'</p><p class="clarity-media-limit">'+e(r['limit'])+'</p><div class="clarity-media-actions"><a class="text-action" href="'+e(r['href'])+'">'+e(r['action'])+' '+EXTERNAL+'</a><a href="'+e(r['related'])+'">'+e(r['relatedText'])+'</a></div></div></article>')
    return '<main id="main-content" class="container" data-family="editorial"><section class="food-app food-reading clarity-media"><header class="food-app-head"><div><h1>Read &amp; watch.</h1><p>Cooking, science and practical guidance, with a clear source for each.</p></div></header><div class="clarity-media-shelf">'+''.join(cards)+'</div><details class="clarity-media-method"><summary>How we choose this shelf</summary><p>These original summaries use official descriptions and edition details. They do not claim firsthand reading, video viewing, testing or professional nutrition review.</p><p>No affiliate links, sponsorships, copied covers or video artwork. Availability can change. Creator and publisher pages were checked October 14, 2026; the PBS availability statement was checked in its official indexed archive.</p></details></section></main>'

def write(path,text):
    if path.read_text(encoding='utf-8')!=text:path.write_text(text,encoding='utf-8',newline='\n')

def build():
    p=ROOT/'read-and-watch.html';text=p.read_text(encoding='utf-8')
    text=re.sub(r'<main\b[\s\S]*?</main>',lambda _:media_main(),text,count=1)
    title='Nutrition reading, cooking books & documentary resources | GetMacros'
    description='Explore source-linked cooking, nutrition and documentary resources. See creators, editions, limitations and honest streaming availability.'
    text=re.sub(r'<title>.*?</title>','<title>'+e(title)+'</title>',text,count=1,flags=re.S)
    text=re.sub(r'(<meta (?:name|property)="(?:description|og:description|twitter:description)" content=")[^"]*',lambda m:m.group(1)+e(description),text)
    text=re.sub(r'(<meta (?:name|property)="(?:og:title|twitter:title)" content=")[^"]*',lambda m:m.group(1)+e(title),text)
    write(p,text)
    catalogue=json.loads((ROOT/'js/play-catalogue.json').read_text(encoding='utf-8'))
    for item in catalogue:
        p=ROOT/item['route'];text=p.read_text(encoding='utf-8')
        # The runtime's current objective belongs in the work area. Keep the
        # richer rule explanation in How it works, not a repeated top subtitle.
        text=re.sub(r'(<header class="play-head"><div><h1>.*?</h1>)<p>.*?</p>',r'\1',text,count=1,flags=re.S)
        text=re.sub(r'<!-- master-game-entry:start -->.*?<!-- master-game-entry:end -->','',text,flags=re.S)
        text=text.replace('class="play-page container"','class="play-page container clarity-game"')
        text=text.replace('data-play-stage aria-label=','data-play-stage role="region" aria-label=')
        text=text.replace('data-play-pause>','data-play-pause aria-pressed="false">')
        write(p,text)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'character-media-manifest.json').write_text(json.dumps({'date':DATE,'mediaRoutes':['/read-and-watch.html'],'gameRoutes':['/'+x['route'] for x in catalogue],'gameCount':len(catalogue),'gameFamilyCount':7,'resources':RESOURCES,'claims':'Sources inspected; no firsthand video-viewing or book-reading claim. No copied third-party media.'},indent=2)+'\n',encoding='utf-8')
    print('Character/media presentation: source-linked shelf and 56 existing game headers; no games added.')
if __name__=='__main__':build()
