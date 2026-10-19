"""Editorial, theme and shared-template contracts for the integrated release."""
from pathlib import Path
from html.parser import HTMLParser
import json,sys,re,hashlib,unittest,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from build_ultimate_release import articles,pages,markets
from normalize_calculator_layouts import Document

class Release(unittest.TestCase):
 def test_twenty_nine_new_distinct_resources(self):
  rows=articles();self.assertEqual(len(rows),29)
  old=json.loads((ROOT/'tools/ultimate_release/existing-library.json').read_text(encoding='utf-8'));existing={r['href'].lstrip('/') for r in old}
  slugs=[r['slug'].removesuffix('.html')+'.html' for r in rows];self.assertEqual(len(slugs),len(set(slugs)))
  self.assertFalse(set(slugs)&existing)
  for row,slug in zip(rows,slugs):
   self.assertTrue(row['answer'] and row['question'] and row['review']['scope'] and row['overlap_review'],slug)
   self.assertTrue(row['sources'] and all(s['url'].startswith('https://') for s in row['sources']),slug)
   self.assertTrue(row['search_observations'] and row['related'],slug)
   self.assertGreaterEqual(len(re.sub('<[^>]*>',' ',row['body_html']).split()),300,slug)
   self.assertTrue('<table' in row['body_html'] or '<svg' in row['body_html'],slug)
   text=(ROOT/slug).read_text(encoding='utf-8');d=Document(text)
   self.assertEqual(len([n for n in d.nodes if n['tag']=='h1']),1,slug)
   self.assertIn('https://getmacros.net/'+slug,text)
   self.assertIn('class="editorial-story"',text)
   self.assertNotIn('noindex',text)
   schemas=[json.loads(text[n['inner']:n['close']]) for n in d.nodes if n['tag']=='script' and n['attrs'].get('type')=='application/ld+json']
   a=next(s for s in schemas if s.get('@type')=='Article');self.assertEqual(a['datePublished'],'2026-10-19');self.assertEqual(a['author']['@type'],'Organization')

 def test_every_route_has_four_accessible_choices(self):
  for p in pages():
   s=p.read_text(encoding='utf-8');d=Document(s)
   buttons=[n for n in d.nodes if 'data-theme-choice' in n['attrs']]
   self.assertEqual({b['attrs']['data-theme-choice'] for b in buttons},{'light','citrus','berry','dark'},p)
   self.assertTrue(all(b['tag']=='button' and b['attrs']['type']=='button' and 'aria-pressed' in b['attrs'] for b in buttons),p)
   self.assertEqual(s.count('id="appearance-dialog"'),1,p)
   self.assertIn("['light','citrus','berry','dark'].includes(p)",s,p)
   self.assertNotIn('class="product-panel appearance-picker"',s,p)

 def test_same_home_architecture_real_market_data(self):
  structures=[]
  for code,m in markets().items():
   p=ROOT/('index.html' if code=='US' else m['home'].strip('/')+'/index.html');s=p.read_text(encoding='utf-8');d=Document(s)
   self.assertIn('data-home-market="'+code+'"',s)
   structures.append([n['attrs'].get('class') for n in d.nodes if n['tag']=='section' and n['attrs'].get('class','').startswith('home-')])
   for n in d.nodes:
    if 'data-record-market' in n['attrs']:self.assertEqual(n['attrs']['data-record-market'],code)
  self.assertTrue(all(x==structures[0] for x in structures))

 def test_new_articles_crawlable_from_topics_search_sitemap(self):
  index=(ROOT/'articles.html').read_text(encoding='utf-8');search=(ROOT/'search.html').read_text(encoding='utf-8');tree=ET.parse(ROOT/'sitemap.xml');urls={n.text for n in tree.findall('.//{*}loc')}
  searchable={'/'+n['attrs']['href'].lstrip('/').split('?')[0] for n in Document(search).nodes if n['tag']=='a' and 'search-hit' in n['attrs'].get('class','').split()}
  for row in articles():
   route='/'+row['slug'].removesuffix('.html')+'.html';self.assertTrue('href="'+route+'"' in index,route);self.assertIn(route,searchable);self.assertIn('https://getmacros.net'+route,urls)
  self.assertNotIn('https://getmacros.net/food-diary.html',urls)
  self.assertNotIn('reading-topic-select',index)

 def test_document_title_does_not_include_accessible_chart_titles(self):
  from validate_site import PageParser
  p=PageParser();p.feed('<html><head><title>Page title</title></head><body><svg role="img"><title>Chart title</title></svg></body></html>')
  self.assertEqual(''.join(p.title_parts),'Page title')

 def test_source_check_dates_come_from_source_evidence(self):
  for row in articles():
   path=ROOT/(row['slug'].removesuffix('.html')+'.html')
   text=path.read_text(encoding='utf-8')
   dates=sorted({source['checked_on'] for source in row['sources'] if source.get('checked_on')})
   self.assertTrue(dates,path)
   self.assertIn('Sources checked '+', '.join(dates)+'.',text,path)
   self.assertNotIn('Sources checked None',text,path)

 def test_image_identity_and_honest_labels(self):
  manifest=json.loads((ROOT/'images/meal-cutouts/provenance.json').read_text(encoding='utf-8'))
  self.assertEqual(len(manifest['assets']),17)
  for row in manifest['assets']:
   self.assertFalse(row['exactMealPhotograph']);self.assertEqual(row['kind'],'original-category-illustration')
   data=(ROOT/row['path'].lstrip('/')).read_bytes().replace(b'\r\n',b'\n');self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])
  home=(ROOT/'index.html').read_text(encoding='utf-8');self.assertIn('grilled-sandwich.svg',home);self.assertIn('Illustration</figcaption>',home)

 def test_private_storage_and_no_obsolete_presentation(self):
  privacy=(ROOT/'privacy.html').read_text(encoding='utf-8');self.assertIn('IndexedDB',privacy);self.assertNotIn('Cloudflare adds a web analytics script',privacy)
  quiz=(ROOT/'js/meal-guide.js').read_text(encoding='utf-8');self.assertIn("const storage='gm-meal-guide-v2-'+market",quiz)
  for path in ['tools/food-design.css','css/food-app.css']:
   s=(ROOT/path).read_text(encoding='utf-8');self.assertNotIn('.icon-action)',s);self.assertNotIn('.diary-workspace .diary-workspace',s)
  source=(ROOT/'js/liquid-motion.js').read_text(encoding='utf-8');self.assertIn('prefers-reduced-motion',source);self.assertIn('data-calculator-stage',source)

if __name__=='__main__':unittest.main(verbosity=2)
