from pathlib import Path
from PIL import Image,ImageDraw
r=Path('docs/redesign/reset');out=r/'comparisons';out.mkdir(exist_ok=True)
cases=[('home-desktop','index.html','light',1440),('home-mobile','index.html','light',390),('results-desktop','restaurant-meal-finder.html','light',1440),('results-mobile','restaurant-meal-finder.html','light',390),('calculator','calculators.html','light',1440),('restaurant','chipotle-healthy-meals-macros.html','light',1440),('article','how-much-protein-can-your-body-absorb.html','light',1440),('night','index.html','dark',1440)]
pairs=[]
for label,route,theme,width in cases:
 name=f'{route}-{theme}-{width}-viewport.png';pairs.append((label,r/'replacement-before'/name,r/'replacement-final'/name,'Before this replacement','Current implementation'))
pairs.extend([('filters-open',r/'replacement-before/restaurant-meal-finder.html-light-1440-viewport.png',r/'families/filters-desktop-light.png','Before: restaurant filters visible in sidebar','After: restaurant filter menu open'),('navigation-open',Path('docs/redesign/screenshots/state-navigation-light-390.png'),r/'families/navigation-calculators-light.png','Earlier saved baseline: menu open','Current menu open')])
html=['<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>GetMacros implementation comparison</title><style>body{font:16px system-ui;margin:36px;background:#f5f5f5;color:#14291f}img{display:block;max-width:100%;height:auto}section{margin:50px 0}p{max-width:75ch}a{color:#276443}</style><h1>GetMacros: before and after</h1><p>Actual browser captures. These are implemented pages, not mockups. Before captures are from this task’s initial working tree, except the open navigation comparison, which uses an earlier saved baseline. The filter comparison shows the old visible desktop sidebar and the new open restaurant menu.</p><p><a href="http://127.0.0.1:4187/index.html">Open the current local website</a></p>']
for label,a,b,ca,cb in pairs:
 im1=Image.open(a).convert('RGB');im2=Image.open(b).convert('RGB');w=720 if im1.width>800 else 390
 im1=im1.resize((w,round(im1.height*w/im1.width)));im2=im2.resize((w,round(im2.height*w/im2.width)))
 sheet=Image.new('RGB',(w*2+24,max(im1.height,im2.height)+48),'#e6e8e3');d=ImageDraw.Draw(sheet);d.text((12,12),ca,fill='#14291f');d.text((w+24,12),cb,fill='#14291f');sheet.paste(im1,(0,48));sheet.paste(im2,(w+24,48));sheet.save(out/(label+'.jpg'),quality=92)
 html.append(f'<section><h2>{label.replace("-"," ").title()}</h2><img src="{label}.jpg" alt="{label}: before and after browser screenshots"></section>')
(out/'index.html').write_text('\n'.join(html),encoding='utf-8')
print('Created 10 honest before/after comparisons.')
