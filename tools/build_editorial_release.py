"""Publish checked, individually authored editorial release articles.

Owns article routes and its private manifests only. Site integration is explicit:
the main release build must call run() before shared presentation and indexing.
No external dependencies, invented nutrition records, or date changes to old pages.
"""
from pathlib import Path
from html import escape, unescape
import csv, json, re, hashlib
from normalize_calculator_layouts import Document

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/editorial_release'
OUT = ROOT / 'docs/playful-release-2026-10-04/editorial'

def load():
    return json.loads((DATA/'articles.json').read_text(encoding='utf-8'))

def plain(value):
    return re.sub(r'\s+', ' ', unescape(re.sub('<[^>]*>', ' ', value))).strip()

def main(row):
    entries=[]
    def section(m):
        section_id='reading-section-'+str(len(entries)+1)
        entries.append((section_id,plain(m[1])))
        return '<h2 id="'+section_id+'">'+m[1]+'</h2>'
    body=re.sub(r'<h2>(.*?)</h2>',section,row['body'],flags=re.S)
    body=body.replace('<div class="table-wrap">','<div class="table-wrap" role="region" aria-label="Scrollable worked example" tabindex="0">')
    toc='<details class="reading-contents"><summary>In this guide</summary><nav class="garden-toc" aria-label="On this page">'+''.join('<a href="#'+i+'">'+escape(t)+'</a>' for i,t in entries)+'</nav></details>'
    sources='<section class="resource-sources"><h2 id="sources">Sources and example boundaries</h2><ul>'+''.join('<li><a href="'+escape(s['url'],quote=True)+'">'+escape(s['label'])+'</a><p>'+escape(s['supports'])+'</p></li>' for s in row['sources'])+'</ul><p>'+escape(row['scope'])+'</p></section>'
    related='<aside class="source-ribbon"><div><h2>Put this to use</h2>'+''.join('<p><a href="'+escape(r['url'],quote=True)+'">'+escape(r['label'])+'</a></p>' for r in row['related'])+'</div></aside>'
    return '<main id="main-content"><nav class="breadcrumb container" aria-label="Breadcrumb"><ol><li><a href="articles.html">Learn</a></li><li>'+escape(row['category'])+'</li></ol></nav><section class="market-page-head"><div class="container page-head-grid"><div class="page-intro-content"><h1>'+escape(row['title'])+'</h1><p>'+escape(row['description'])+'</p></div></div></section><div class="market-reading-layout">'+toc+'<article class="article-container release-article"><p class="submission-byline">By GetMacros · Published October 4, 2026</p>'+body+sources+related+'</article></div></main>'

def render(row,template):
    d=Document(template);node=next(n for n in d.nodes if n['tag']=='main')
    text=template[:node['start']]+main(row)+template[node['end']:]
    title=row['title']+' | GetMacros';desc=row['description'];url='https://getmacros.net/'+row['slug']
    text=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',text,count=1,flags=re.S)
    for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('property','og:url',url),('name','twitter:title',title),('name','twitter:description',desc),('property','og:image','https://getmacros.net/images/og-default.png'),('name','twitter:image','https://getmacros.net/images/og-default.png'),('property','og:image:alt','GetMacros — practical food and nutrition guides')]:
        text=re.sub(r'(<meta '+attr+'="'+re.escape(key)+r'" content=")[^"]*',lambda m:m[1]+escape(value,quote=True),text,count=1)
    text=re.sub(r'<link rel="canonical" href="[^"]+">','<link rel="canonical" href="'+url+'">',text,count=1)
    text=re.sub(r'<script type="application/ld\+json">.*?</script>','',text,flags=re.S)
    schema={'@context':'https://schema.org','@type':'Article','headline':row['title'],'description':desc,'url':url,'mainEntityOfPage':url,'datePublished':'2026-10-04','author':{'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/about.html'},'publisher':{'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/'}}
    text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
    return text

def run():
    rows=load();sources=json.loads((DATA/'sources.json').read_text(encoding='utf-8'))
    known={s['url'] for s in sources if s['status']=='inspected'}
    assert len({r['slug'] for r in rows})==len(rows)
    template=(ROOT/'how-to-read-a-nutrition-label.html').read_text(encoding='utf-8')
    OUT.mkdir(parents=True,exist_ok=True);manifest=[]
    for row in rows:
        assert re.fullmatch(r'[a-z0-9-]+\.html',row['slug'])
        assert row['sources'] and all(s['url'] in known for s in row['sources']),row['slug']
        assert row['intent'] and row['utility'] and row['scope'] and row['related']
        if row['status']!='checked':
            manifest.append({**row,'published':False});continue
        text=render(row,template)
        (ROOT/row['slug']).write_text(text,encoding='utf-8')
        manifest.append({'route':row['slug'],'title':row['title'],'category':row['category'],'intent':row['intent'],'original_utility':row['utility'],'research_status':'inspected primary sources','writing_status':'authored','editorial_status':'checked','publication_status':'published in release candidate','render_status':'pending parent route/browser verification','word_count':len(plain(row['body']).split()),'source_count':len(row['sources']),'body_hash':hashlib.sha256(row['body'].encode()).hexdigest(),'remaining_issues':row.get('remaining','')})
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    published=[r for r in manifest if r.get('publication_status')]
    fields=list(published[0]) if published else ['route']
    with (OUT/'manifest.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(published)
    (OUT/'integration.json').write_text(json.dumps({'publicationDate':'2026-10-04','newArticleCount':len(published),'existingArticlesImproved':0,'blockedArticleCount':len(rows)-len(published),'routes':[{'route':r['slug'],'title':r['title'],'description':r['description'],'category':r['category'],'intent':r['intent'],'datePublished':'2026-10-04'} for r in rows if r['status']=='checked']},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Editorial release: '+str(len(published))+' authored, checked new article routes; indexes untouched.')

if __name__=='__main__':run()
