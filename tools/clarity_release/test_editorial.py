"""Factual arithmetic and publication gates for the authored clarity articles."""
import unittest,sys,json,re,hashlib,tempfile,shutil
from pathlib import Path
from urllib.parse import urlparse,parse_qs
sys.path.insert(0,str(Path(__file__).parent))
import editorial as ed
class Editorial(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,cls.coverage=ed.new_articles();cls.improved=ed.improved_articles()
 def test_frozen_menu_facts(self):
  facts=[('CA','Tim Hortons','Latte - Medium',[140,10,14,5,0,115]),('CA','Tim Hortons','Protein Latte - Medium',[170,20,10,6,0,80]),('CA','Harvey’s','Angus Burger',[410,18,32,23,1,700]),('CA','Harvey’s','Veggie Burger',[330,20,32,14,4,680]),('CA','New York Fries','Classic Poutine, Snack',[890,27,77,52,5,1160]),('CA','Mary Brown’s','Fries (Small)',[324,2.3,35.6,21.4,2.3,663]),('GB','Greggs','Sausage Roll(s)',[347,9.1,24,24,1.5,600]),('GB','Greggs','Vegan Roll Pork-Free',[308,11,21,19,2.9,720]),('AU','Guzman y Gomez','Bowl — Mild Grilled Chicken',[659,43.8,74.1,20.5,6.3,1700]),('MX','Subway','6-inch sub — Chicken, Oven Roasted',[290,25,39,4,5,440])]
  for country,chain,name,values in facts:
   r=ed.item(country,chain,name)
   for k,value in zip(['cal','p','c','fat','f','na'],values):self.assertEqual(r[k],value,(r['id'],k))
 def test_complete_order_arithmetic(self):
  main=ed.item('CA','Mary Brown’s','Big Mary');fries=ed.item('CA','Mary Brown’s','Fries (Small)');taters=ed.item('CA','Mary Brown’s','Taters (Small)')
  a=ed.total('A',[main,fries]);b=ed.total('B',[main,taters])
  self.assertEqual(a['cal'],920);self.assertAlmostEqual(a['p'],35.3);self.assertEqual(b['cal'],1066);self.assertAlmostEqual(b['p'],42.4)
  self.assertEqual(a['na']-b['na'],52)
 def test_missing_component_does_not_become_zero(self):
  a=dict(market='CA',serving='1 serving',source='https://example.test',url='/source',cal=100,p=5,c=10,fat=4,f=None,na=0)
  b={**a,'f':2,'na':3};summed=ed.total('Unknown fiber',[a,b]);self.assertIsNone(summed['f']);self.assertEqual(summed['na'],3)
 def test_retailer_actual_portions(self):
  pb=ed.grocery('branded:retailer-ca:costco:321724');yg=ed.grocery('branded:retailer-ca:costco:1794181');mac=ed.grocery('branded:retailer-ca:costco:1195303')
  self.assertEqual(ed.portion(pb,30)['cal'],180);self.assertEqual(ed.portion(pb,30)['p'],8)
  self.assertAlmostEqual(ed.portion(mac,28)['cal'],218.4);self.assertAlmostEqual(ed.portion(mac,28)['p'],2.24)
  self.assertAlmostEqual(ed.portion(yg,175)['p']+ed.portion(pb,15)['p'],21)
 def test_source_units_and_rounded_pack(self):
  roll=ed.item('GB','Greggs','Sausage Roll(s)');pack=ed.item('GB','Greggs','Sausage Roll 4 Pack')
  self.assertEqual(pack['cal'],4*roll['cal']);self.assertNotEqual(pack['p'],4*roll['p']);self.assertAlmostEqual(1.5*1000/2.5,roll['na'])
  self.assertIn('g/ml',roll['serving']);self.assertIsNone(roll['servingGrams'])
 def test_subway_complete_identity(self):
  r=ed.item('MX','Subway','6-inch sub — Turkey Breast','MX|subway|1c5926505abe2837')
  self.assertEqual(r['servingGrams'],205);self.assertEqual(r['cal'],270);self.assertEqual(r['p'],15)
  self.assertEqual(r['sourcePage'],1)
 def test_portion_energy_calculation(self):
  self.assertAlmostEqual(2760/4.184,659.6558317399617);self.assertEqual(ed.item('AU','Guzman y Gomez','Bowl — Mild Grilled Chicken')['cal'],659)
  self.assertAlmostEqual(10*70+6.25*175-5*30+5,1648.75);self.assertAlmostEqual(1648.75*1.55,2555.5625)
 def test_actual_source_dates_retained(self):
  for r in ed.EVIDENCE.values():
   if r.get('chain')=='Tim Hortons':self.assertEqual(r['sourceDate'],'2026-07');self.assertEqual(r['checked'],'2026-10-09')
   if r.get('brand')=='Kirkland Signature':self.assertEqual(r['sourceChecked'],'2026-10-12')
 def test_source_linked_comparison_contract(self):
  for r in self.rows:
   for raw in re.findall(r'href="([^"]*compare-foods\.html[^"]*)"',r['body']):
    args=parse_qs(urlparse(ed.unescape(raw)).query);self.assertLessEqual(len(args['item']),2);self.assertIn(args['basis'][0],['portions','100g'])
    for identity in args['item']:
     if identity.startswith('order:'):
      _,market,rid=identity.split(':',2);record=next(x for x in ed.REG if x.get('id')==rid);self.assertEqual(record['market'],market)
     else:self.assertTrue(identity.startswith('branded:retailer-ca:'))
  country_page=next(r for r in self.rows if r['route']=='/subway-turkey-breast-canada-vs-mexico.html')
  raw=re.search(r'href="([^"]*compare-foods\.html[^"]*)"',country_page['body'])[1]
  identities=parse_qs(urlparse(ed.unescape(raw)).query)['item']
  self.assertEqual({identity.split(':',2)[1] for identity in identities},{'CA','MX'})
 def test_distinct_article_purposes(self):
  self.assertEqual(len(self.rows),11);self.assertEqual(len(self.improved),10)
  self.assertEqual(len({r['route'] for r in self.rows}),11);self.assertEqual(len({r['intent'] for r in self.rows}),11)
  for r in self.rows:self.assertTrue(r['existingOverlap']);self.assertTrue(r['uniqueValue']);self.assertTrue(r['body'].startswith('<p>'))
 def test_coverage_has_honest_denominators(self):
  for row in self.coverage:
   self.assertGreaterEqual(row['tracked'],row['finder']);self.assertGreaterEqual(row['tracked'],row['complete']);self.assertGreaterEqual(row['tracked'],row['fiber'])
  jp=next(r for r in self.coverage if r['market']=='JP');self.assertEqual(jp['fiber'],0)
  ca=next(r for r in self.coverage if r['market']=='CA');self.assertGreaterEqual(ca['caloriesOnly'],39)
 def test_rendered_metadata_and_crawlable_answer(self):
  for r in self.rows:
   path=ed.ROOT/r['route'].lstrip('/');text=path.read_text(encoding='utf-8')
   self.assertEqual(len(re.findall(r'<h1(?:\s[^>]*)?>',text)),1)
   self.assertIn('href="https://getmacros.net'+r['route']+'"',text)
   self.assertNotIn('noindex',text)
   schema=[json.loads(s) for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)]
   articles=[v for s in schema for v in (s if isinstance(s,list) else [s]) if v.get('@type')=='Article']
   self.assertEqual(len(articles),1);self.assertEqual(articles[0]['datePublished'],'2026-10-14')
   for schema in articles:self.assertNotIn('review',schema);self.assertNotIn('aggregateRating',schema)
   self.assertIn(ed.plain(r['body'].split('</p>',1)[0])[:60],ed.plain(text))
 def test_idempotence(self):
  # A late-generator regression must not undo root's integrated Save controls,
  # navigation, asset stamps or final manifest statuses in the shared checkout.
  original_root,original_out=ed.ROOT,ed.OUT
  temporary_parent=original_out/'editorial-test-isolation';temporary_parent.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='getmacros-editorial-test-',dir=temporary_parent) as directory:
   temp=Path(directory).resolve();self.assertEqual(temp.parent,temporary_parent.resolve())
   for row in self.rows+self.improved:
    rel=row['route'].lstrip('/');target=temp/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original_root/rel,target)
   retailer=temp/'data/branded-foods/retailer-ca/records';retailer.mkdir(parents=True)
   for p in (original_root/'data/branded-foods/retailer-ca/records').glob('*.json'):shutil.copyfile(p,retailer/p.name)
   try:
    ed.ROOT=temp;ed.OUT=temp/'docs/clarity-release-2026-10-14'
    ed.run();paths=[temp/r['route'].lstrip('/') for r in self.rows+self.improved]
    before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};ed.run()
    self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    for row in self.improved:
     text=(temp/row['route'].lstrip('/')).read_text(encoding='utf-8');self.assertEqual(text.count('<!-- clarity-editorial:start -->'),1)
     self.assertNotIn('All food figures and prices in the worked example are invented',text)
   finally:ed.ROOT,ed.OUT=original_root,original_out
if __name__=='__main__':unittest.main()
