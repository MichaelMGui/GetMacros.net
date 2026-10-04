"""Build 56 independent playable routes plus the Play directory.

Shared header/footer are taken from the active homepage. Run after the normal
publication pass, before metadata/search/sitemap stamping. No seed URL is a page.
"""
from pathlib import Path
from html import escape as e
import json,re,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/'tools/play_release/catalogue.json'

def character(food):
 return f'<svg class="play-food" viewBox="0 0 160 160" aria-hidden="true"><use href="images/food-characters.svg#food-{e(food)}"/></svg>'

def records():
 code="""const fs=require('fs'),vm=require('vm'),s={window:{}};vm.createContext(s);for(const f of ['meal-data','meal-provenance'])vm.runInContext(fs.readFileSync('js/'+f+'.js','utf8'),s);console.log(JSON.stringify(s.window.GM_MEALS.filter(x=>x.verificationStatus==='source inspected').map(x=>({chain:x.chain,name:x.name,cal:x.cal,p:x.p,portion:x.serving,source:x.source,checked:x.checked,ingredients:(x.components||[]).map(c=>c.item)}))));"""
 return json.loads(subprocess.run(['node','-e',code],cwd=ROOT,check=True,capture_output=True,encoding='utf-8').stdout)

def build():
 catalogue=json.loads(CAT.read_text(encoding='utf-8')); assert len(catalogue)==56
 original=(ROOT/'index.html').read_text(encoding='utf-8')
 prefix=original[:original.index('<main ')];footer=re.search(r'<footer\b[\s\S]*?</footer>',original).group(0)
 prefix=re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>','',prefix)
 prefix=prefix.replace('</head>','<link rel="stylesheet" href="css/play-release.css">\n</head>')
 def page(route,title,description,main,scripts=''):
  head=re.sub(r'<title>[\s\S]*?</title>','<title>'+e(title+' | GetMacros')+'</title>',prefix,count=1)
  for pattern,value in [(r'(<meta name="description" content=")[^"]*',description),(r'(<meta (?:property|name)="(?:og:title|twitter:title)" content=")[^"]*',title+' | GetMacros'),(r'(<meta (?:property|name)="(?:og:description|twitter:description)" content=")[^"]*',description),(r'(<link rel="canonical" href=")[^"]*','https://getmacros.net/'+route),(r'(<meta property="og:url" content=")[^"]*','https://getmacros.net/'+route)]:
   head=re.sub(pattern,lambda m:m.group(1)+e(value,quote=True),head)
  base='<script src="js/unified-v7.js" defer></script><script src="js/food-characters.js" defer></script><script src="js/food-experience.js" defer></script>'
  if (ROOT/'js/food-shelf.js').exists():base+='<script src="js/food-shelf.js" defer></script>'
  (ROOT/route).write_text(head+main+footer+base+scripts+'</body></html>\n',encoding='utf-8',newline='\n')
 data=records();routes=[]
 for slug,title,category,food,objective,explanation in catalogue:
  route='play-'+slug+'.html';routes.append({'route':route,'id':slug,'title':title,'category':category,'description':objective,'character':food,'status':'implemented'})
  categoryid=category.lower().replace(' & ','-').replace(' ','-')
  source='<p>All numerical labels in this puzzle are fictional examples. They are not menu values or personal targets.</p>' if category in ['Numbers & labels','Meal decisions','Advanced puzzles'] and slug not in ['restaurant-order-builder','menu-mystery'] else ''
  if slug in ['restaurant-order-builder','menu-mystery']:source='<p>Uses tracked U.S. menu data. The complete portion and official source appear after solving. Additional toppings and other markets are not implied.</p>'
  if slug=='nutrition-term-match':source+='<p>Label definitions: <a href="https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label">FDA Nutrition Facts label guide</a>.</p>'
  main=f'''<main id="main-content" class="play-page container"><nav class="play-breadcrumb" aria-label="Breadcrumb"><a href="play.html">Play</a> / <a href="play.html#{categoryid}">{e(category)}</a></nav><header class="play-head"><div><h1>{e(title)}</h1><p>{e(objective)}</p></div>{character(food)}</header><div class="play-workspace"><div class="play-toolbar"><button type="button" data-play-restart>Restart</button><button type="button" data-play-new>New puzzle</button><button type="button" data-play-pause>Pause</button><button type="button" data-shelf-save data-kind="game" data-url="{route}" data-title="{e(title,quote=True)}" aria-pressed="false">Save game</button><small>Untimed · Puzzle <span data-play-seed>1</span></small></div><div class="play-stage" data-play-stage aria-label="{e(title,quote=True)} game"></div><div class="play-paused" data-play-paused hidden><h2>Take your time.</h2><p>Your puzzle is right where you left it.</p><button type="button" class="btn btn-primary" data-play-resume>Resume</button></div><p class="play-feedback" data-play-feedback role="status" aria-live="polite" aria-atomic="true"></p><noscript><p>This interactive game needs JavaScript. The instructions below remain available, or <a href="articles.html">read the nutrition guides</a>.</p></noscript><div class="play-notes"><section><h2>How it works</h2><p>{e(explanation)}</p><p>Touch the controls or use Tab and Enter. There is no time limit or mandatory sound. Pause at any point; restarting repeats this puzzle and New puzzle changes its seed.</p></section><section><h2>Behind the game</h2>{source}<p>Original GetMacros rules and food artwork. Progress and saved creations stay in this browser. No account or public leaderboard.</p><a href="how-to-read-a-nutrition-label.html">Read a food label</a> · <a href="restaurant-meal-finder.html">Find a meal</a></section></div></div></main>'''
  meta={'id':slug,'title':title,'character':food,'explanation':explanation}
  safe=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
  scripts='<script>window.GM_PLAY_META='+safe(meta)+';window.GM_PLAY_RECORDS='+safe(data if slug in ['restaurant-order-builder','menu-mystery'] else [])+';</script><script src="js/play-rules.js" defer></script><script src="js/play-release.js" defer></script>'
  page(route,title+' — food puzzle',objective,main,scripts)
 groups={}
 for item in routes:groups.setdefault(item['category'],[]).append(item)
 nav=''.join(f'<a href="#{k.lower().replace(" & ","-").replace(" ","-")}">{e(k)}</a>'for k in groups)
 directory=''
 for i,(category,items) in enumerate(groups.items()):
  cards=''.join(f'<a class="play-game-link" href="{x["route"]}">{character(x["character"])}<span><strong>{e(x["title"])}</strong><p>{e(x["description"])}</p><small>Untimed · touch &amp; keyboard</small></span></a>'for x in items)
  directory+=f'<details id="{category.lower().replace(" & ","-").replace(" ","-")}" {"open"if i==0 else ""}><summary>{e(category)} <small>· {len(items)} games</small></summary><div class="play-game-list">{cards}</div></details>'
 main=f'''<main id="main-content" class="play-page container"><section class="play-hub-intro"><div><h1>Play with your food.</h1><p>Small puzzles, good company. Make something, solve something, or take a little break.</p><a class="btn btn-primary" href="play-market-memory.html">Start with Market Memory</a></div><div class="play-hub-art" aria-hidden="true">{character('potato')}{character('strawberry')}{character('egg')}</div></section><section class="play-daily" data-play-daily>{character('carrot')}<div><h2>Today’s little challenge.</h2><p>A shared puzzle seed, a different game each day.</p></div><a class="btn btn-primary" href="play-serving-size-detective.html">Play today</a></section><nav class="play-directory-nav" aria-label="Game categories">{nav}</nav><div class="play-directory">{directory}</div><p class="play-hint">56 original games. No account, reaction timer or mandatory sound. Nutrition examples are labeled; games are for play and learning, not dietary prescriptions.</p></main>'''
 page('play.html','Food games & puzzles','Play 56 original food puzzles, memory games, creative studios and untimed coordination challenges. Touch and keyboard controls, no account needed.',main,'<script src="js/play-directory.js" defer></script>')
 manifest=ROOT/'tools/play_release/manifest.json';manifest.write_text(json.dumps({'games':routes,'routes':['play.html']+[x['route']for x in routes],'count':56},indent=2)+'\n',encoding='utf-8')
 (ROOT/'js/play-catalogue.json').write_text(json.dumps(routes,separators=(',',':'))+'\n',encoding='utf-8')
 (ROOT/'css').mkdir(exist_ok=True);shutil.copyfile(ROOT/'tools/play-release.css',ROOT/'css/play-release.css')
 print(f'Built {len(routes)} game routes + Play directory; {len(data)} verified records available to restaurant puzzles.')
 return routes
if __name__=='__main__':build()
