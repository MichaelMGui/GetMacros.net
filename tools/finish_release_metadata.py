"""Truthful release metadata and technical gates for the completed changes."""
from pathlib import Path
import re,json
from normalize_calculator_layouts import Document
from build_restaurant_pages import parse_meals
from build_release_resources import load
ROOT=Path(__file__).resolve().parents[1]
def run():
 changed={'','index.html','blog.html','articles.html','search.html','restaurant-meal-finder.html','calculators.html','sources.html','privacy.html'}|{m['url'] for m in parse_meals()}|{'healthy-fast-food.html','best-fast-food-restaurants-for-your-goals.html','are-diet-drinks-bad-for-you.html','calories-vs-macros-what-matters-more.html','does-creatine-cause-hair-loss.html','how-much-protein-can-your-body-absorb.html'}|{r['slug'] for r in load()}
 p=ROOT/'sitemap.xml';text=p.read_text(encoding='utf-8')
 for name in changed:text=re.sub(r'(<loc>https://getmacros\.net/'+re.escape(name)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-10-03',text)
 p.write_text(text,encoding='utf-8')
 for path in [ROOT/'sources.html',ROOT/'privacy.html']:
  text=path.read_text(encoding='utf-8');text=re.sub(r'<!-- release-note:start -->.*?<!-- release-note:end -->','',text,flags=re.S)
  if path.name=='sources.html':note='<section class="reading-section" id="release-source-audit"><h2>October 3 source inspection</h2><p>This release inspected 41 of the 83 tracked order records, including published item values and reproducible ingredient sums. The other records keep their earlier source dates. A retrieval date describes when a source was inspected; it does not change the document’s publication date.</p><p>Per-nutrient notes distinguish published values from component sums. The twelve-count Chick-fil-A nuggets retain older fiber and sodium records; their four freshly inspected nutrients have separate dates. CAVA’s accessible document does not establish current local menu availability. Starbucks entries rely on inspected official indexed text because the live page did not expose its nutrition table to this inspection.</p><p>The new comparisons use the source-inspected subset, with unavailable values left blank. These are selected U.S. orders, not a complete-menu survey or a Canadian menu substitute. <a href="fast-food-nutrition-data-report.html">Read the coverage and missing-data report</a>.</p></section>'
  else:note='<section class="reading-section" id="release-privacy-details"><h2>Product events and future advertising</h2><p>No analytics or advertising provider is connected to the new product-event and placement code. Product events currently stay in the browser: they contain only an action name and a version number. They contain no calculator answers, search terms, meal identifiers, account identifiers or health profiles.</p><p>Advertising remains disabled. An authorized provider adapter and affirmative consent are required before a placement can load. A future provider may introduce separate data processing; its configuration, consent requirements and this notice must be reviewed before activation. The disabled placement code does not send requests to an ad provider.</p></section>'
  marker='<aside class="source-ribbon"'
  # Place the source/commitment note in the existing reading column.
  doc=Document(text)
  target=next((n for n in doc.nodes if 'policy-content' in n['attrs'].get('class','').split()),None)
  if target is None:target=next((n for n in doc.nodes if any(c in n['attrs'].get('class','').split() for c in ('clear-page-body','article-container','policy-body','sources-content'))),None)
  if target is None:raise ValueError('Missing reading container '+path.name)
  pos=target['close']
  text=text[:pos]+'<!-- release-note:start -->'+note+'<!-- release-note:end -->'+text[pos:]
  path.write_text(text,encoding='utf-8')
 print('Release modification dates and source/privacy implementation notes reconciled; prior data-review dates preserved.')
if __name__=='__main__':run()
