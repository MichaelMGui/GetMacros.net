"""Check crawlable entry points, honest list labels and internal destinations."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
from build_restaurant_pages import parse_meals

ROOT=Path(__file__).resolve().parents[1]

class Links(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        if tag=='a' and 'href' in attrs:self.hrefs.append(attrs['href'])

pages={p.name:p.read_text(encoding='utf-8') for p in ROOT.glob('*.html')}
parsed={}
for name,text in pages.items():
    assert 'search_term_string' not in text, name+' contains a search placeholder'
    p=Links();p.feed(text);parsed[name]=p

checked=0
for name,page in parsed.items():
    for href in page.hrefs:
        url=urlsplit(href)
        if url.scheme and url.scheme not in {'http','https'}:continue
        if url.netloc and url.hostname not in {'getmacros.net','www.getmacros.net'}:continue
        if url.scheme=='http':raise AssertionError(name+' links to insecure site URL '+href)
        target=unquote(url.path).lstrip('/') or (name if url.fragment else 'index.html')
        if target in parsed:
            if url.fragment:assert unquote(url.fragment) in parsed[target].ids, (name,href,'missing anchor')
        else:assert (ROOT/target).is_file(),(name,href,'missing internal destination')
        checked+=1

text=pages['healthy-fast-food.html']
sections={key:re.search(r'<details[^>]*id="'+key+r'".*?</details>',text,re.S)[0]
          for key in ['high-protein-orders','under-500-calories']}
meals={m['name']:m for m in parse_meals()}
for key,section in sections.items():
    parser=Links();parser.feed(section)
    assert len(parser.hrefs)==6
    names=re.findall(r'<strong><a[^>]*>(.*?)</a>',section,re.S)
    import html
    for name in names:
        meal=meals[html.unescape(name)]
        assert meal['cal']>=250
        if key=='high-protein-orders':assert meal['cal']<600 and meal['p']>=25
        else:assert meal['cal']<500
        assert '#menu-comparison' in section
schema=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)]
listing=next(s for s in schema if s.get('@type')=='ItemList')
assert listing['numberOfItems']==6
assert [item['name'] for item in listing['itemListElement']]==[
    html.unescape(n) for n in re.findall(r'<strong><a[^>]*>(.*?)</a>',sections['high-protein-orders'],re.S)]
print(f'Search visibility passed: {len(pages)} pages, {checked} internal links and anchors; meal labels match source data.')
