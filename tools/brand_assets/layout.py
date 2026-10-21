"""Shared logo placement; brand artwork never implies local menu coverage."""
from pathlib import Path
from html import escape,unescape
import json,re
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[2]
def key(s):return re.sub('[^a-z0-9]','',s.lower())
def apply(text):
    logos=json.loads((ROOT/'images/restaurant-logos/manifest.json').read_text())['logos']
    names={key(alias):r for r in logos.values() for alias in r['aliases']}
    def mark(name):
        r=names.get(key(name))
        return '<span class="brand-logo" aria-hidden="true"><img src="'+r['src']+'" width="48" height="40" alt="" loading="lazy" decoding="async"></span>' if r else None
    from build_flagship_release import replace,find
    for node in sorted(Document(text).nodes,key=lambda n:n['start'],reverse=True):
        classes=node['attrs'].get('class','').split()
        if 'restaurant-shortcut' not in classes and 'restaurant-entry' not in classes and 'presence-row' not in classes:continue
        fragment=text[node['start']:node['end']]
        if 'brand-logo' in fragment:continue
        d=Document(fragment)
        if 'restaurant-shortcut' in classes:
            n=next((n for n in d.nodes if n['tag']=='span' and not n['attrs'].get('class')),None)
        else:n=next((n for n in d.nodes if n['tag']=='h2'),None)
        if not n:continue
        name=unescape(re.sub('<[^>]+>','',fragment[n['inner']:n['close']])).strip().removesuffix('→').strip()
        logo=mark(name)
        if not logo:continue
        old=find(fragment,'shortcut-mark') or find(fragment,'restaurant-mark')
        if old:fragment=replace(fragment,old,logo)
        elif 'presence-row' in classes:fragment=fragment[:n['inner']]+logo+fragment[n['inner']:]
        text=replace(text,node,fragment)
    if 'js/meal-view.js' in text or 'js/meal-guide.js' in text:
        if 'js/restaurant-brands.js' not in text:text=re.sub(r'(?=<script[^>]+src="/?js/(?:meal-images|meal-view|meal-guide)\.js)', '<script src="/js/restaurant-brands.js" defer></script>',text,count=1)
    # Credits live with the site's existing nutrition and asset methodology.
    if '<link rel="canonical" href="https://getmacros.net/sources.html"' in text:
        section='<section id="restaurant-logo-credits"><h2>Restaurant logos &amp; item images</h2><p>Logos identify independent restaurant brands. GetMacros is not affiliated with or endorsed by these restaurants. Trademarks remain with their owners.</p><p>These text and geometric logo files are sourced from Wikimedia Commons, whose individual file pages record their copyright status. Original colors and proportions are preserved.</p><ul>'+''.join('<li><a href="'+escape(r['sourcePage'],quote=True)+'">'+escape(r['name'])+' logo source</a></li>' for r in logos.values())+'</ul><p>Food illustrations are labeled. An official item-page link opens the restaurant’s own presentation; it does not transfer ownership or reuse rights to its photographs.</p></section>'
        old=next((n for n in Document(text).nodes if n['attrs'].get('id')=='restaurant-logo-credits'),None)
        if old:text=replace(text,old,section)
        else:text=text.replace('</main>',section+'</main>',1)
    return text
