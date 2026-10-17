"""Checks for four new local markets: source integrity, units and regional scope."""
from pathlib import Path
import json,hashlib,re,unittest
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/newmarkets'
B=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-records.json').read_text(encoding='utf-8'))
R=B['records']
def row(country,name):return next(x for x in R if x['market']==country and x['name']==name)
class NewMarketTests(unittest.TestCase):
 def test_four_actual_markets_have_macro_records(self):
  self.assertEqual(set(B['marketCounts']),{'FR','IN','SG','ZA'})
  self.assertEqual(len(R),489)
  for m in B['marketCounts']:self.assertTrue(any(x['market']==m and x['finderSupported'] for x in R))
 def test_unique_ids_and_final_versions(self):
  self.assertEqual(len({x['id'] for x in R}),len(R))
  for r in R:
   expected=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
   self.assertEqual(r['sourceVersion'],expected)
 def test_source_hashes_are_actual_saved_bytes(self):
  sources=json.loads((D/'source-register.json').read_text(encoding='utf-8'));hashes=set()
  for s in sources:
   self.assertEqual(hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest(),s['sha256']);hashes.add(s['sha256'])
  self.assertTrue(all(r['sourceHash'] in hashes for r in R))
 def test_france_current_edition_is_linked_and_french_names_preserved(self):
  index=(D/'quick-fr-index.html').read_text(encoding='utf-8')
  self.assertIn('Declaration_Nutritionnelle_des_produits_Quick_valable_a_partir_du_6_octobre_2026_a98adac17b.pdf',index)
  r=row('FR','Méga Giant');self.assertEqual(r['language'],'fr');self.assertEqual(r['sourceDate'],'2026-10-06')
  self.assertEqual((r['cal'],r['p'],r['c'],r['fat'],r['na']),(859,46,38,58,1248))
 def test_france_volume_is_not_mass_or_an_unspecified_cup(self):
  a=row('FR','Coca Cola · 200 ml');z=row('FR','Coca Cola · 500 ml')
  self.assertEqual((a['servingMillilitres'],z['servingMillilitres']),(200,500))
  self.assertIsNone(z['servingGrams']);self.assertEqual(z['cal']-a['cal'],126)
  self.assertEqual(row('FR','Méga Giant')['cal']+z['cal'],1069)
 def test_published_zero_salt_and_zero_number_parsing(self):
  import restaurant_stage as core
  from restaurant_newmarkets_stage import n
  self.assertEqual(core.num(0),0);self.assertEqual(core.num(0.0),0);self.assertEqual(n(0),0)
  self.assertIsNone(core.num(None));self.assertIsNone(core.num('<0.1'));self.assertIsNone(n('<0,1',True))
  zero_salt=[r for r in R if r['nativeNutrients'].get('salt')==0]
  self.assertEqual(len(zero_salt),16)
  for r in zero_salt:
   self.assertEqual(r['na'],0);self.assertTrue(any(c['from']=='salt' and c['to']=='na' for c in r['conversions']))
  for r in R:
   if 'salt' in r.get('nutrientBounds',{}):self.assertIsNone(r['na'])
 def test_france_bounds_and_source_alcohol_energy(self):
  for r in R:
   for key,bound in r.get('nutrientBounds',{}).items():
    if key in r:self.assertIsNone(r[key])
  # 4/4/9 does not include alcohol energy; source beer is not corrected or discarded for that reason.
  self.assertEqual(row('FR','Boisson Heineken (**)')['cal'],139)
 def test_indian_operator_proof_and_visible_region(self):
  raw=(D/'mcd-in-ne-index.html').read_text(encoding='utf-8')
  self.assertIn('Connaught Plaza Restaurants Private Limited',raw);self.assertIn('North &amp; East India',raw)
  for r in R:
   if r['market']!='IN':continue
   self.assertEqual(r['chain'],'McDonald’s North & East India');self.assertEqual(r['region'],'IN-NORTH-EAST')
   self.assertEqual(r['localOperatingEntity'],'Connaught Plaza Restaurants Private Limited');self.assertIsNone(r['sourceDate'])
 def test_india_product_values_are_not_rda_columns(self):
  r=row('IN','Veg Mc Muffin')
  self.assertEqual((r['servingGrams'],r['cal'],r['p'],r['c'],r['fat'],r['na']),(119,303.35,10.22,38.86,11.78,804.63))
  self.assertNotEqual(r['cal'],2000);self.assertIsNone(r['f'])
 def test_india_missing_carbs_are_not_invented(self):
  held=json.loads((D/'withheld.json').read_text(encoding='utf-8'))
  self.assertTrue(any(x['name'].startswith('Nuggets') and 'c' in x.get('missingFields',[]) for x in held))
  self.assertFalse(any(x['market']=='IN' and x['name'].startswith('Nuggets') for x in R))
 def test_singapore_nine_category_sources_and_native_units(self):
  self.assertEqual(len(list(D.glob('bk-sg-category*.html'))),9)
  js=(D/'bk-sg-main.js').read_text(encoding='utf-8')
  self.assertIn('Protein</h5>',js);self.assertIn('unit">mg</abbr>',js)
  r=row('SG','WHOPPER®');z=row('SG','WHOPPER® with Cheese')
  self.assertEqual((r['cal'],r['p'],r['c'],r['fat'],r['na']),(625,24,54,35,1400))
  self.assertEqual((z['cal']-r['cal'],z['na']-r['na']),(75,300))
 def test_singapore_fountain_reference_is_not_a_complete_cup(self):
  refs=[r for r in R if r['market']=='SG' and r.get('servingMillilitres')==100]
  self.assertTrue(refs)
  for r in refs:self.assertFalse(r['finderSupported']);self.assertIsNone(r['servingGrams']);self.assertEqual(r['nutrientBasis'],'per 100 ml source reference')
 def test_south_africa_energy_conversion_has_correct_scale(self):
  r=row('ZA','Real Deal® — BBQ Chicken · Small · standard / halaal')
  self.assertAlmostEqual(r['cal'],r['sourceEnergyKilojoules']/4.184)
  self.assertAlmostEqual(r['cal'],520.6739961759082)
  self.assertEqual((r['p'],r['c'],r['fat'],r['na']),(26.54,73.89,13.07,397.66))
  self.assertIsNone(r['servingGrams']);self.assertIsNone(r['sat']);self.assertIsNone(r['sugar'])
  self.assertEqual(r['nutrientProvenance']['cal']['method'],'energy-unit conversion from source kJ')
 def test_south_africa_conflicting_small_and_identical_variants(self):
  self.assertFalse(any(r['market']=='ZA' and 'BBQ BEEF · Small' in r['name'] for r in R))
  common=[r for r in R if r['market']=='ZA' and set(r['sourceVariants'])=={'standard','halaal'}]
  self.assertEqual(len(common),136)
  self.assertTrue(all('standard / halaal' in r['name'] for r in common))
 def test_definitions_presence_and_briefs_match_actual_records(self):
  defs=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-definitions.json').read_text(encoding='utf-8'))
  presence=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-newmarkets-presence-upserts.json').read_text(encoding='utf-8'))['relationships']
  briefs=json.loads((D/'guide-briefs.json').read_text(encoding='utf-8'))['briefs'];ids={r['id'] for r in R}
  self.assertEqual(len(presence),4);self.assertEqual(len(briefs),4)
  for code,count in B['marketCounts'].items():self.assertEqual(defs[code]['recordCount'],count)
  self.assertTrue(all(all(i in ids for i in b['recordIds']) for b in briefs))
  self.assertEqual({b['market'] for b in briefs},set(defs))
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NewMarketTests))
 (D/'test-results.json').write_text(json.dumps({'passed':result.wasSuccessful(),'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'records':len(R),'marketCounts':B['marketCounts'],'finderEligible':dict(Counter(r['market'] for r in R if r['finderSupported']))},indent=2)+'\n',encoding='utf-8')
 raise SystemExit(0 if result.wasSuccessful() else 1)
