"""Independent anchors, units, source integrity and honest source boundaries."""
from pathlib import Path
import json,hashlib,unittest
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants'
BATCH=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-records.json').read_text(encoding='utf-8'))
ROWS=BATCH['records']+BATCH['updates']
def find(market,name):return next(r for r in ROWS if r['market']==market and r['name']==name)
class RestaurantEvidenceTests(unittest.TestCase):
 def test_every_existing_country_has_actual_new_macros(self):
  self.assertEqual(set(BATCH['marketCounts']),{'US','CA','MX','GB','IE','AU','NZ','JP'})
  for market in BATCH['marketCounts']:self.assertTrue(any(r['market']==market and r['finderSupported'] for r in BATCH['records']))
 def test_unique_new_ids_and_source_hashes(self):
  self.assertEqual(len(ROWS),len({r['id'] for r in ROWS}))
  sources=json.loads((D/'source-register.json').read_text(encoding='utf-8'))
  hashes={r['sha256'] for r in sources}
  for src in sources:self.assertEqual(src['sha256'],hashlib.sha256((ROOT/src['file']).read_bytes()).hexdigest())
  for row in ROWS:self.assertIn(row['sourceHash'],hashes)
 def test_canadian_chicken_anchor_and_real_piece_unit(self):
  r=find('CA','Original Recipe® Chicken — Drumstick')
  self.assertEqual((r['cal'],r['p'],r['c'],r['fat'],r['na']),(140,15,2,8,150))
  self.assertEqual(r['serving'],'1 piece');self.assertIsNone(r['servingGrams'])
  self.assertEqual((2*r['cal'],2*r['p'],2*r['na']),(280,30,300))
 def test_ireland_markers_are_not_british_availability(self):
  self.assertFalse(any('#' in r['name'] or '~' in r['name'] for r in ROWS if r['market']=='GB'))
  r=find('IE','Original Recipe Chicken Fillet Roll #')
  self.assertEqual((r['cal'],r['p'],r['c'],r['fat']),(662,28.6,78.7,24.5))
 def test_salt_conversion_and_unavailable_fibre(self):
  r=find('GB','Fillet Burger')
  self.assertEqual(r['nativeNutrients']['salt'],2.2);self.assertEqual(r['na'],880)
  self.assertIsNone(r['f']);self.assertEqual(r['units']['na'],'mg')
 def test_exact_published_zero_salt_converts_and_bounds_do_not(self):
  zero_salt=[r for r in ROWS if r['nativeNutrients'].get('salt')==0 and r['nativeNutrients'].get('na') is None]
  self.assertEqual(len(zero_salt),6)
  for r in zero_salt:
   self.assertEqual(r['na'],0);self.assertTrue(any(c['from']=='salt' and c['to']=='na' for c in r['conversions']))
   self.assertEqual(r['nutrientProvenance']['na']['method'],'salt-equivalent conversion')
  for r in ROWS:
   if 'salt' in r.get('nutrientBounds',{}):
    self.assertIsNone(r['na']);self.assertFalse(any(c['from']=='salt' for c in r['conversions']))
 def test_less_than_is_not_zero_or_exact_upper_bound(self):
  bounded=[r for r in ROWS if r.get('nutrientBounds')]
  self.assertTrue(bounded)
  for r in bounded:
   for field,bound in r['nutrientBounds'].items():
    self.assertEqual(bound['operator'],'<')
    if field in r:self.assertIsNone(r[field])
    if field in ('p','c','fat'):self.assertFalse(r['finderSupported'])
 def test_japanese_direct_sodium_is_not_recomputed_from_rounded_salt(self):
  r=find('JP','モスバーガー')
  self.assertEqual((r['servingGrams'],r['cal'],r['p'],r['fat'],r['c'],r['f'],r['na']),(211.2,372,15.2,17,40,3.4,906))
  self.assertEqual(r['nativeNutrients']['salt'],2.3)
  self.assertEqual(r['conversions'],[]);self.assertIsNone(r['sat']);self.assertIsNone(r['sugar'])
 def test_nz_large_salad_is_published_not_doubled(self):
  small=find('NZ','Regular Salad — Sweet Onion Chicken Teriyaki');large=find('NZ','Large Salad — Sweet Onion Chicken Teriyaki')
  self.assertEqual((small['servingGrams'],large['servingGrams']),(300,500))
  self.assertEqual((small['cal'],large['cal']),(208,402))
  self.assertNotEqual(large['cal'],2*small['cal'])
  self.assertAlmostEqual(large['p']-small['p'],19.2)
  self.assertEqual(small['sourceDate'],'2026-05')
 def test_australian_named_mini_recipe(self):
  r=find('AU','Mini Bowl — Mild Grilled Chicken')
  self.assertEqual((r['cal'],r['p'],r['fat'],r['c'],r['na']),(409,24.2,12.8,48.6,992))
  self.assertEqual(r['servingGrams'],264)
 def test_mexican_named_builds_no_size_inference(self):
  a=find('MX','Pastor — Gran Pastor');b=find('MX','Pastor — Gringo Pastor')
  self.assertEqual((a['cal'],b['cal'],a['p'],b['p']),(470,420,31,31))
  self.assertNotIn('6-inch',a['serving']);self.assertEqual(a['sourceDate'],'2026-08')
 def test_us_real_portions_and_no_combo_invention(self):
  a=find('US','Chicken — Mushroom Chicken');b=find('US','Chicken — The Original Orange Chicken®')
  self.assertEqual((a['cal'],a['p'],b['cal'],b['p']),(180,13,560,19))
  self.assertIsNone(a['servingGrams']);self.assertIn('5.7',a['serving'])
  self.assertEqual(a['url'],'/panda-express-healthy-meals-macros.html')
  self.assertIsNone(a['sourceDate'])
  self.assertTrue(all(not r['finderSupported'] for r in ROWS if r['market']=='US' and 'Cub Meal' in r['sourceGroup']))
 def test_source_refresh_keeps_original_ids(self):
  existing=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
  ids={r.get('id') for r in existing}
  self.assertEqual(len(BATCH['updates']),17)
  self.assertTrue(all(r['id'] in ids for r in BATCH['updates']))
 def test_inconsistent_official_rows_are_withheld(self):
  withheld=json.loads((D/'withheld.json').read_text(encoding='utf-8'))
  self.assertTrue(any(r['name']=='Meatball Mozza Pot' for r in withheld))
  self.assertFalse(any('Meatball Mozza Pot' in r['name'] for r in ROWS if r['market']=='NZ'))
  self.assertFalse(any(r['market']=='MX' and r['chain']=='KFC' for r in ROWS))
 def test_versions_describe_final_rows(self):
  for r in ROWS:
   version=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
   self.assertEqual(r['sourceVersion'],version)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RestaurantEvidenceTests))
 report={'passed':result.wasSuccessful(),'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'newRows':len(BATCH['records']),'refreshedRows':len(BATCH['updates']),'marketCounts':BATCH['marketCounts'],'newFinderEligible':dict(Counter(r['market'] for r in BATCH['records'] if r['finderSupported'])),'sourceEditionIsRetrievalDate':False}
 (D/'test-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 raise SystemExit(0 if result.wasSuccessful() else 1)
