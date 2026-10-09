"""Integrate reviewed data and tools into existing routes; no guessed package content."""
from pathlib import Path
from html import escape
import json,re
from normalize_calculator_layouts import Document
from restaurant_identity import mark

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-10-09'
DATA=ROOT/'tools/growth_release'
CHANGED=set()
def e(s):return escape(str(s),quote=True)
def clean(text,name):return re.sub(r'<!-- growth:'+name+r':start -->.*?<!-- growth:'+name+r':end -->','',text,flags=re.S)
def block(name,body):return '<!-- growth:'+name+':start -->'+body+'<!-- growth:'+name+':end -->'
def scripts(text,names,style=True):
 for name in names:
  text=re.sub(r'<script[^>]*src="js/'+re.escape(name)+r'(?:\?[^" ]*)?"[^>]*>\s*</script>','',text)
 added=''.join('<script src="js/'+name+'" defer></script>' for name in names)
 positions=[text.find('<script src="js/'+name) for name in ('meal-finder.js','protein-value.js')]
 at=min((p for p in positions if p>=0),default=-1)
 text=text[:at]+added+text[at:] if at>=0 else text.replace('</body>',added+'</body>')
 if style:
  text=re.sub(r'<link[^>]*href="css/growth-tools.css[^" ]*"[^>]*>','',text)
  text=text.replace('</head>','<link rel="stylesheet" href="css/growth-tools.css"></head>')
 return text
def write(route,text):
 (ROOT/route).write_text(text,encoding='utf-8');CHANGED.add(route)
def article_insert(route,name,body,names=('order-tools-core.js','order-notebook.js','order-tools.js')):
 text=clean((ROOT/route).read_text(encoding='utf-8'),name);node=Document(text).find(cls='article-container')
 if not node:raise ValueError('No reading template: '+route)
 at=text.rfind('</article>',node['start'],node['end']);text=text[:at]+block(name,body)+text[at:]
 write(route,scripts(text,list(names)))
def tool(id,mode,title,detail,button):
 return f'<section id="{id}" class="growth-tool" data-order-tool="{mode}" aria-labelledby="{id}-title"><header><span data-food-character="egg" aria-hidden="true"><svg viewBox="0 0 160 160" aria-hidden="true"><use href="images/food-characters.svg#food-egg"/></svg></span><h2 id="{id}-title">{title}</h2></header><p>{detail}</p><button class="btn btn-primary" type="button" data-order-load>{button}</button><p data-order-status role="status"></p><div data-order-workspace hidden></div><noscript><p>The interactive tool needs JavaScript. The article tables and official sources remain available.</p></noscript></section>'
def metadata(route):
 p=ROOT/route;text=p.read_text(encoding='utf-8')
 def update(m):
  try:data=json.loads(m[1])
  except ValueError:return m[0]
  def visit(node):
   if isinstance(node,list):
    for x in node:visit(x)
   if isinstance(node,dict):
    types=node.get('@type',[]);types=[types] if isinstance(types,str) else types
    if any(t in types for t in ('Article','BlogPosting')):node['dateModified']=DATE
    if '@graph' in node:visit(node['@graph'])
  visit(data);return '<script type="application/ld+json">'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'</script>'
 text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update,text,flags=re.S);p.write_text(text,encoding='utf-8')
def run():
 CHANGED.add('articles.html')
 (ROOT/'css/growth-tools.css').write_text((DATA/'tools.css').read_text(encoding='utf-8'),encoding='utf-8')
 article_insert('compare-complete-restaurant-orders.html','builder',tool('order-builder','builder','Build the order you mean.','Add exact listed foods, sides, drinks or packets. Known subtotals stay separate from unknown component values.','Open order builder'))
 article_insert('breakfast-drinks-and-add-ons.html','drinks',tool('drink-comparison','drink','Compare the drinks, too.','Choose source-checked recipes and portions. No guessed milk swaps, syrup removals or protein additions. Current component coverage is Chick-fil-A; other brands await their full nutrition panels.','Open drink comparison'))
 text=(ROOT/'restaurant-meal-finder.html').read_text(encoding='utf-8');write('restaurant-meal-finder.html',scripts(text,['order-tools-core.js','order-notebook.js']))
 text=clean((ROOT/'food-shelf.html').read_text(encoding='utf-8'),'notebook')
 notebook='<section id="order-notebook" class="growth-tool"><h2>Your order notebook.</h2><p>Exact saved portions and private notes, only in this browser. Older saves need a current record check to create their first snapshot. Nothing is synced or sent to analytics.</p><div class="action-row"><button class="btn" type="button" data-notebook-load>Check current records</button><button class="quiet-button" type="button" data-notebook-export>Export orders &amp; notes</button><button class="quiet-button" type="button" data-notebook-clear>Delete notebook</button></div><p data-notebook-status role="status" tabindex="-1"></p><div data-notebook-list></div><noscript><p>The local notebook needs JavaScript. <a href="restaurant-meal-finder.html?view=saved">Open saved meals</a>.</p></noscript></section>'
 text=text.replace('</main>',block('notebook',notebook)+'</main>');write('food-shelf.html',scripts(text,['order-tools-core.js','order-tools.js','order-notebook.js']))
 text=clean((ROOT/'protein-value-calculator.html').read_text(encoding='utf-8'),'receipt-settings')
 text=text.replace('Example prices in US dollars. Results update as you type.','Enter the amount paid for each whole receipt line. Quantity means packages or listed orders; servings and protein describe one package or order. All figures use the same currency, without conversion.')
 text=text.replace('Compare two packages to find the cost of the same amount of protein.','Use your receipt to compare protein value and the amount you actually paid.')
 text=text.replace('Package price','Amount paid for this line')
 for prefix in ('a','b'):
  text=re.sub(r'<div class="field" data-receipt-quantity="'+prefix+r'">.*?</div>','',text,flags=re.S)
  input=f'<div class="field" data-receipt-quantity="{prefix}"><label for="{prefix}q">Packages or orders on this line</label><input id="{prefix}q" type="number" min="1" max="1000" step="1" value="1" required></div>'
  text=text.replace('<div class="field"><label for="'+prefix+'s">',input+'<div class="field"><label for="'+prefix+'s">',1)
 settings='<div class="receipt-settings"><label for="receipt-currency">Receipt currency<select id="receipt-currency"><option value="USD">USD — U.S. dollars</option><option value="CAD">CAD — Canadian dollars</option><option value="GBP">GBP — British pounds</option><option value="EUR">EUR — euros</option><option value="AUD">AUD — Australian dollars</option></select></label></div>'
 text=text.replace('<div class="form-grid">',block('receipt-settings',settings)+'<div class="form-grid">',1)
 text=clean(text,'checkouts');text=text.replace('<p id="winner"',block('checkouts','<div class="receipt-checkouts"><p data-checkout-a></p><p data-checkout-b></p></div><p class="clarity-hint">Per-25-g cost is a proportional comparison, not a purchasable portion or a protein recommendation. Prices are yours, not universal menu prices.</p>')+'<p id="winner"',1)
 write('protein-value-calculator.html',scripts(text,['order-tools-core.js']))
 # Additional data are source-checked components, not fictitious full-lunch totals.
 catalogue=json.loads((DATA/'menu-records.json').read_text(encoding='utf-8'));records=catalogue['records'];new=sum(r['isNew'] for r in records)
 table='<div class="table-wrap" tabindex="0" role="region" aria-label="Source-checked menu components"><table class="component-snapshot-table"><caption>U.S. published portions checked October 9, 2026. Sugar means total sugars; added sugars are unknown.</caption><thead><tr>'+''.join('<th scope="col">'+v+'</th>' for v in ('Exact item','Portion','Status','Calories','Protein (g)','Carbs (g)','Fat (g)','Fiber (g)','Sodium (mg)','Total sugars (g)'))+'</tr></thead><tbody>'
 for r in records:
  n=r['nutrients'];table+='<tr><th scope="row"><a href="'+e(r['source']['productUrl'] or r['source']['url'])+'">'+e(r['name'])+'</a><small>'+e(r['category'])+'</small></th><td>'+e(r['portion']['label'])+'</td><td>'+('New' if r['isNew'] else 'Reverified existing')+'</td>'+''.join('<td>'+('Unknown' if n[k] is None else e(n[k]))+'</td>' for k in ('calories','proteinG','carbsG','fatG','fiberG','sodiumMg','totalSugarG'))+'</tr>'
 table+='</tbody></table></div>'
 snapshot=f'<section id="component-snapshot" class="growth-tool"><h2>More of the order, recorded.</h2><p><strong>{new} new Chick-fil-A menu records</strong> and {len(records)-new} reverified existing items, alongside the separate 463-order finder snapshot above. These foods, sides, drinks, packets and dressings are not {new} new complete meals.</p><p>Portions and recipes follow the current full official table. Ambiguous parent values, conflicting plain iced coffee, unclear salad builds and misleading catering serving names are excluded. Sandwich packet inclusion remains unresolved; the builder warns before extra sauce is added. Added sugars remain unknown.</p><label class="snapshot-search">Find a component<input type="search" placeholder="Fruit cup, nuggets, tea…"></label><p data-snapshot-count role="status">{len(records)} component records shown</p><details><summary>Open the reproducible component table</summary>{table}</details><p><a href="js/order-catalogue.json" download>Download the factual component snapshot (JSON)</a> · <a href="compare-complete-restaurant-orders.html#order-builder">Build a source-linked order</a> · <a href="breakfast-drinks-and-add-ons.html#drink-comparison">Compare drinks</a></p><p class="source-note">Source: <a href="https://www.chick-fil-a.com/nutrition-allergens">Chick-fil-A U.S. nutrition interface</a>. Checked October 9. These are published calculations, not laboratory measurements or allergy guarantees. Source versions, exclusions and missing values are retained in the download.</p></section>'
 article_insert('fast-food-nutrition-data-report.html','snapshot',snapshot)
 # Substantive additions reviewed individually by the editorial workstream.
 reviewed=DATA/'editorial-improvements.json'
 if reviewed.exists():
  for row in json.loads(reviewed.read_text(encoding='utf-8'))['improvements']:
   if row['status']!='checked':continue
   route=row['route'];text=clean((ROOT/route).read_text(encoding='utf-8'),'editorial')
   if row.get('removeLegacyComparisonSelector'):
    for node in sorted([n for n in Document(text).nodes if 'chain-picks-section' in n['attrs'].get('class','').split()],key=lambda n:n['start'],reverse=True):
     text=text[:node['start']]+text[node['end']:]
   if row.get('directoryCorrection'):
    correction=row['directoryCorrection'];doc=Document(text);node=doc.find(cls='hub-restaurant-list')
    directory='<details class="hub-restaurant-list"><summary>'+e(correction['heading'])+'</summary><div class="chain-grid">'+''.join('<a class="chain-card" href="'+e(r['route'])+'">'+mark(r['chain'])+'<span>'+e(r['chain'])+'</span><b>'+str(r['recordCount'])+' recorded orders</b></a>' for r in correction['entries'])+'</div></details>'
    text=text[:node['start']]+directory+text[node['end']:]
   anchor=row['insertBefore'];at=text.find(anchor)
   if at<0:raise ValueError('Missing reviewed insertion anchor: '+route+' '+anchor)
   section=row['sectionHTML'].replace('growth-ordering-note','growth-ordering-note growth-update')
   text=text[:at]+block('editorial',section)+text[at:]
   toc=next((n for n in Document(text).nodes if 'article-toc' in n['attrs'].get('class','').split()),None)
   if toc and 'href="#growth-'+route.removesuffix('.html')+'"' not in text:
    pos=text.rfind('</ol>',toc['start'],toc['end'])
    if pos>=0:text=text[:pos]+'<li><a href="#growth-'+route.removesuffix('.html')+'">'+e(row['heading'])+'</a></li>'+text[pos:]
   write(route,scripts(text,[],True))
 # Do not casually alter legal promises; describe only the actual new local storage.
 route='privacy.html';text=clean((ROOT/route).read_text(encoding='utf-8'),'notebook-privacy')
 body='<section class="growth-update"><h2>Private order notes and exports</h2><p>The order notebook stores saved portions, source-check dates and optional notes in this browser’s local storage. Notes are not sent to an account, analytics or an advertising platform. You can delete entries or the whole notebook. Clearing site data can erase them. Export is a download you request; it includes private notes, so choose deliberately before sharing it.</p></section>'
 node=Document(text).find(cls='article-container')
 if node:
  at=text.rfind('</article>',node['start'],node['end']);write(route,text[:at]+block('notebook-privacy',body)+text[at:])
 for route in CHANGED:metadata(route)
 sitemap=ROOT/'sitemap.xml';xml=sitemap.read_text(encoding='utf-8')
 for route in CHANGED:
  xml=re.sub(r'(<loc>https://getmacros.net/'+re.escape(route)+r'</loc>\s*<lastmod>)[^<]+',r'\g<1>'+DATE,xml)
 sitemap.write_text(xml,encoding='utf-8')
 out=ROOT/'docs/growth-release-2026-10-09';out.mkdir(parents=True,exist_ok=True)
 (out/'implemented-routes.json').write_text(json.dumps({'date':DATE,'routes':sorted(CHANGED),'newMenuRecords':new,'reverifiedExistingRecords':len(records)-new,'newArticles':0,'packageStatus':'missing; supplied drafts and briefs not reviewed or counted'},indent=2),encoding='utf-8')
 print('Growth tools integrated across',len(CHANGED),'existing routes;',new,'new component records. No missing-package article was fabricated.')
if __name__=='__main__':run()
