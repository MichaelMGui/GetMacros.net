"""Keep long reading pages easy to navigate without changing their substance."""
from pathlib import Path
import re, html
ROOT=Path(__file__).resolve().parents[1]
count=0
for p in ROOT.glob('*.html'):
    s=p.read_text(encoding='utf-8')
    def complete_card(match):
        target=ROOT/match.group(1).split('#')[0]
        if not target.is_file():return match.group(0)
        metadata=re.search(r'<meta name="description" content="([^"]+)"',target.read_text(encoding='utf-8'))
        if not metadata:return match.group(0)
        return re.sub(r'<span>.*?</span>','<span>'+html.escape(html.unescape(metadata.group(1)))+'</span>',match.group(0),flags=re.S)
    s=re.sub(r'<a class="explore-card" href="([^"]+)">.*?</a>',complete_card,s,flags=re.S)
    s=re.sub(r'<!-- reading-map:start -->.*?<!-- reading-map:end -->','',s,flags=re.S)
    if p.name=='how-much-protein-per-day.html':
        s=re.sub(r'("dateModified":\s*")[^"]+',r'\g<1>2026-09-08',s)
    if p.name=='privacy.html':
        s=s.replace('how localStorage is used for quizzes and tools','how browser preferences and saved meals are stored')
        s=s.replace('This site displays ads served by Google AdSense.','This site integrates Google AdSense. Ad availability depends on account approval and Google’s serving decisions.')
        if 'id="traffic-measurement"' not in s:
            s=s.replace('<h2>Advertising</h2>','<h2 id="traffic-measurement">Traffic measurement</h2><p>Cloudflare adds a web analytics script to the live site. It measures page visits and performance. See <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a> for information about its handling of visitor data.</p><h2>Advertising</h2>')
    body=re.search(r'<body[^>]*class="([^"]*)"',s)
    main=re.search(r'<main\b[^>]*>(.*?)</main>',s,re.S)
    if not main or not body or 'article-page' not in body.group(1) or '<form' in main.group(1) or 'journal-contents' in s or p.name in ['blog.html','articles.html','search.html']:
        p.write_text(s,encoding='utf-8');continue
    headings=[]
    def heading(m):
        title=html.unescape(re.sub('<[^>]+>','',m.group(2))).strip()
        if title in ['Continue exploring','Keep reading','Related guides']:return m.group(0)
        existing=re.search(r'\bid="([^"]+)"',m.group(1))
        ident=existing.group(1) if existing else 'read-'+str(len(headings)+1)
        headings.append((ident,title))
        return '<h2'+m.group(1)+('' if existing else ' id="'+ident+'"')+'>'+m.group(2)+'</h2>'
    updated=re.sub(r'<h2([^>]*)>(.*?)</h2>',heading,main.group(1),flags=re.S)
    if len(headings)>=4:
        contents='<!-- reading-map:start --><div class="container reading-map"><details><summary>On this page</summary><nav aria-label="Page sections">'+''.join('<a href="#'+ident+'">'+html.escape(title)+'</a>' for ident,title in headings)+'</nav></details></div><!-- reading-map:end -->'
        # Insert after the introductory hero, leaving the primary heading first.
        end=updated.find('</section>')
        if end>=0:
            end+=len('</section>');updated=updated[:end]+contents+updated[end:];count+=1
        s=s[:main.start(1)]+updated+s[main.end(1):]
    p.write_text(s,encoding='utf-8')
print(f'Added section navigation to {count} long reading pages; refreshed privacy disclosures.')
