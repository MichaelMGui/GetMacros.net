"""Publish distinct reviewed resources; initial HTML is fully crawlable."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import json,re,csv
from normalize_calculator_layouts import Document
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/release-2026-10-03'
def load():
 result=[]
 for name in ['release_explainers.json','release_collections.json']:
  path=ROOT/'tools'/name
  if path.exists():result+=json.loads(path.read_text(encoding='utf-8'))
 return result
def source_name(url):
 parts=urlsplit(url)
 return parts.hostname.replace('www.','')+' — '+parts.path.strip('/').split('/')[-1].replace('-',' ').replace('.html','').replace('.pdf','')
def character(row):
 special={'raw-vs-cooked-food-weight.html':'chicken','drained-weight-nutrition-label.html':'beans','calories-in-multi-serving-packages.html':'blueberry','as-packaged-vs-prepared-nutrition.html':'carrot','nutrition-label-rounding.html':'apple','edible-portion-vs-purchased-weight.html':'avocado','unequal-recipe-portions.html':'salmon','calculate-macros-mixed-bowl.html':'broccoli','protein-powder-scoop-weight.html':'banana','protein-cost-food-waste.html':'strawberry','use-calorie-target-meal-finder.html':'pear','compare-complete-restaurant-orders.html':'steak','missing-restaurant-nutrition.html':'shrimp','breakfast-drinks-and-add-ons.html':'egg','grams-vs-milliliters-nutrition-labels.html':'orange','vegetarian-fast-food-protein-comparison.html':'tofu'}
 if row['slug'] in special:return special[row['slug']]
 title=(row['title']+' '+row['category']).lower()
 return next((c for word,c in [('chicken','chicken'),('protein cost','beans'),('breakfast','egg'),('plant','tofu'),('rice','carrot'),('salad','avocado'),('sodium','shrimp'),('fiber','broccoli'),('label','apple'),('recipe','salmon'),('weight','pear'),('scoop','banana'),('drink','orange') ] if word in title),'strawberry')
def resource_main(row):
 slug=row['slug'];body=row.get('bodyHTML',row.get('body',''))
 headings=[]
 def heading(match):
  i=len(headings)+1;label=re.sub('<[^>]*>','',match[1]);headings.append((i,label));return '<h2 id="resource-section-'+str(i)+'">'+match[1]+'</h2>'
 body=re.sub(r'<h2>(.*?)</h2>',heading,body,flags=re.S)
 body=re.sub(r'<div class="table-wrap">','<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable comparison table">',body)
 toc='<details class="reading-contents"><summary>In this guide</summary><nav class="garden-toc" aria-label="On this page">'+''.join('<a href="#resource-section-'+str(i)+'">'+escape(label)+'</a>' for i,label in headings)+'</nav></details>'
 sources='<section class="resource-sources"><h2 id="resource-sources">Sources and scope</h2><ul>'+''.join('<li><a href="'+escape(url,quote=True)+'">'+escape(source_name(url))+'</a></li>' for url in row['sourceURLs'])+'</ul><p>These sources support the factual explanations above. Worked label examples are illustrative where stated. Restaurant comparisons use the listed U.S. portions; availability and local recipes may differ.</p></section>'
 if 'Sources and date boundaries' in body:sources=''
 related=row.get('related',[])
 if not related:related=[{'url':'restaurant-meal-finder.html','label':'Filter restaurant meals'},{'url':'sources.html','label':'Data sources and limitations'}]
 relatedHTML='<aside class="source-ribbon"><div><h2>Use this with your own meal</h2>'+''.join('<p><a href="'+escape(r['url'],quote=True)+'">'+escape(r['label'])+'</a></p>' for r in related)+'</div></aside>'
 return '<main id="main-content"><nav class="breadcrumb container" aria-label="Breadcrumb"><ol><li><a href="articles.html">Guides</a></li><li>'+escape(row['category'])+'</li></ol></nav><section class="market-page-head"><div class="container page-head-grid"><div class="page-category">'+escape(row['category'])+'</div><div class="page-intro-content"><div class="release-character-heading"><span data-food-character="'+character(row)+'" aria-hidden="true"><svg viewBox="0 0 160 160" aria-hidden="true" focusable="false"><use href="/images/food-characters.svg#food-'+character(row)+'"></use></svg></span><h1>'+escape(row['h1'])+'</h1></div><p>'+escape(row['description'])+'</p></div></div></section><div class="market-reading-layout">'+toc+'<article class="article-container release-article"><p class="submission-byline">By GetMacros · Published October 3, 2026</p>'+body+sources+'<aside class="ad-placement" data-ad-placement="article-after-content" hidden aria-label="Advertisement"></aside>'+relatedHTML+'</article></div></main>'
def run():
 rows=load();assert len({r['slug'] for r in rows})==len(rows)
 template=(ROOT/'how-to-read-a-nutrition-label.html').read_text(encoding='utf-8')
 for row in rows:
  slug=row['slug'];slug=slug if slug.endswith('.html') else slug+'.html';row['slug']=slug
  assert re.fullmatch(r'[a-z0-9-]+\.html',slug)
  assert row['sourceURLs'] and len(re.sub('<[^>]*>',' ',row.get('bodyHTML',row.get('body',''))).split())>=220,slug
  text=template;d=Document(text);main=next(n for n in d.nodes if n['tag']=='main');text=text[:main['start']]+resource_main(row)+text[main['end']:]
  title=row['title']+' | GetMacros';desc=row['description'];url='https://getmacros.net/'+slug
  text=re.sub(r'<title>.*?</title>','<title>'+escape(title)+'</title>',text,count=1,flags=re.S)
  for attr,key,value in [('name','description',desc),('property','og:title',title),('property','og:description',desc),('property','og:url',url),('name','twitter:title',title),('name','twitter:description',desc)]:
   text=re.sub(r'(<meta '+attr+'="'+re.escape(key)+r'" content=")[^"]*',lambda m:m[1]+escape(value,quote=True),text,count=1)
  text=re.sub(r'<link rel="canonical" href="[^"]+">','<link rel="canonical" href="'+url+'">',text,count=1)
  text=re.sub(r'<script type="application/ld\+json">.*?</script>','',text,flags=re.S)
  schema={'@context':'https://schema.org','@type':'Article','headline':row['h1'],'description':desc,'url':url,'datePublished':'2026-10-03','author':{'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/about.html'},'publisher':{'@type':'Organization','name':'GetMacros','url':'https://getmacros.net/'}}
  text=text.replace('</head>','<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script></head>')
  (ROOT/slug).write_text(text,encoding='utf-8')
 # A grouped, crawlable library is part of the existing guides index.
 groups={}
 for r in rows:
  category=r['category']
  if category in ('Food labels','Portions & recipes'):group=category
  elif 'protein' in category.lower() or 'budget' in category.lower():group='Protein and food costs'
  elif r.get('tableFacts') and len(r.get('recordKeys',[]))>3:group='Meal collections and data'
  elif r.get('tableFacts'):group='Restaurant decisions'
  else:group='Planning and comparing meals'
  groups.setdefault(group,[]).append(r)
 library='<section class="container release-library" id="practical-resources"><div class="section-heading"><div><p class="section-overline">Worked examples and recorded orders</p><h2>Practical meal and label guides</h2></div></div>'
 for category,entries in groups.items():
  library+='<details class="release-topic"><summary><span>'+escape(category)+'</span><small>'+str(len(entries))+' guides</small></summary><div class="release-library-grid">'+''.join('<article class="release-resource"><h3><a href="'+r['slug']+'">'+escape(r['h1'])+'</a></h3><p>'+escape(r['description'])+'</p></article>' for r in entries)+'</div></details>'
 library+='</section>'
 p=ROOT/'articles.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- release-library:start -->.*?<!-- release-library:end -->','',text,flags=re.S);text=text.replace('</main>','<!-- release-library:start -->'+library+'<!-- release-library:end --></main>');p.write_text(text,encoding='utf-8')
 p=ROOT/'search.html';text=p.read_text(encoding='utf-8');text=re.sub(r'<!-- release-search:start -->.*?<!-- release-search:end -->','',text,flags=re.S)
 hits=''.join('<a class="search-hit" href="'+r['slug']+'" data-search="'+escape(r['title']+' '+r['description']+' '+r['category'],quote=True)+'"><span class="search-hit-name">'+escape(r['h1'])+'</span><span class="search-hit-copy">'+escape(r['description'])+'</span></a>' for r in rows)
 section='<section class="search-group" data-group><div class="search-group-head"><h2>Practical comparisons and portions</h2><span class="search-group-count" data-count>'+str(len(rows))+'</span></div><div class="search-hits">'+hits+'</div><p class="search-group-more" data-more hidden></p></section>'
 text=text.replace('<div class="search-results-actions">','<!-- release-search:start -->'+section+'<!-- release-search:end --><div class="search-results-actions">',1)
 text=re.sub(r'Show all \d+ pages','Show all '+str(len(re.findall('class="search-hit"',text)))+' pages',text);p.write_text(text,encoding='utf-8')
 # No change to existing modification dates here; these pages are new.
 p=ROOT/'sitemap.xml';text=p.read_text(encoding='utf-8')
 for r in rows:
  if 'https://getmacros.net/'+r['slug']+'</loc>' not in text:text=text.replace('</urlset>','<url><loc>https://getmacros.net/'+r['slug']+'</loc><lastmod>2026-10-03</lastmod></url></urlset>')
 p.write_text(text,encoding='utf-8')
 OUT.mkdir(exist_ok=True,parents=True)
 with (OUT/'content-manifest.csv').open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['route','type','intent','original_utility','source_count','remaining_issues']);w.writeheader()
  for r in rows:w.writerow({'route':r['slug'],'type':'new resource','intent':r.get('intent',r['h1']),'original_utility':r.get('originalUtility','Recorded portions, sourced table and specific interpretation'),'source_count':len(r['sourceURLs']),'remaining_issues':r.get('sourceStatus','Illustrative arithmetic distinguished from real product data')})
 print(f'Published {len(rows)} distinct sourced resources; guides, search and sitemap updated.')
if __name__=='__main__':run()
