"""Independent source, named-serving, country and arithmetic regression checks."""
from pathlib import Path
import json,hashlib,unittest,math
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/global-coverage-2026-10-17/restaurants/supplement'
B=json.loads((ROOT/'tools/global_coverage_2026_10_17/restaurant-supplement-records.json').read_text(encoding='utf-8'));R=B['records']
raw={}
for market in ('CA','US'):
 doc=json.loads((D/('bk-'+market.lower()+'-nutrition.json')).read_text(encoding='utf-8'))
 raw[market]={x['_id']:x for sec in doc['data']['StaticPage']['widgets'][0]['menu']['options'] for x in sec['options']}
def row(m,name):return next(r for r in R if r['market']==m and r['name']==name)
class SupplementTests(unittest.TestCase):
 def test_actual_country_counts_and_no_updates(self):
  self.assertEqual(B['marketCounts'],{'CA':134,'US':256});self.assertEqual(len(R),390);self.assertEqual(B['updates'],[])
  self.assertEqual(len({r['id'] for r in R}),390)
 def test_exact_source_files_hashes_and_publication_size(self):
  sources=json.loads((D/'source-register.json').read_text(encoding='utf-8'));self.assertEqual(len(sources),7)
  for s in sources:
   f=ROOT/s['file'];self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),s['sha256']);self.assertLessEqual(f.stat().st_size,2*1024*1024)
  self.assertLess(sum((ROOT/s['file']).stat().st_size for s in sources),20*1024*1024)
 def test_country_payloads_are_distinct(self):
  a=json.loads((D/'bk-ca-nutrition.json').read_text())['data']['StaticPage'];b=json.loads((D/'bk-us-nutrition.json').read_text())['data']['StaticPage']
  self.assertEqual(a['_id'],'56ed3383-9c4c-41ae-a125-49cb2f2e6188');self.assertEqual(b['_id'],'415f9110-e7bf-45d8-8f22-33702a1b4fcc');self.assertNotEqual(a['_id'],b['_id'])
  for r in R:self.assertEqual(r['sourceDataset'],'prod_bk_'+r['market'].lower())
 def test_canadian_whopper_matches_actual_rendered_panel(self):
  r=row('CA','Whopper®');self.assertEqual((r['cal'],r['p'],r['c'],r['fat'],r['na']),(710,33,50,43,1150))
  text=(D/'bk-ca-whopper-rendered.txt').read_text(encoding='utf-8')
  for x in ('Per serving\nCalories\n710 Cal','Proteins\n33 g','Sodium\n1,150 mg'):self.assertIn(x,text)
 def test_us_direct_sodium_does_not_use_inconsistent_rounded_salt(self):
  r=row('US','Whopper');self.assertEqual((r['cal'],r['p'],r['c'],r['fat'],r['na']),(710,34,57,42,1250))
  self.assertEqual(r['nativeNutrients']['salt'],2.95);self.assertNotEqual(r['na'],2.95*400);self.assertEqual(r['conversions'],[])
 def test_published_standard_field_is_not_base_nutrition(self):
  r=row('US',"Fully Loaded Croissan'wich");src=raw['US']['item_14383']
  self.assertEqual(src['nutrition']['calories'],540);self.assertEqual(src['nutritionWithModifiers']['calories'],620)
  self.assertEqual((r['cal'],r['p'],r['c'],r['fat']),(620,30,31,43));self.assertEqual(r['sourceNutritionField'],'nutritionWithModifiers')
 def test_every_nutrient_is_exact_from_its_own_country_item(self):
  fields={'cal':'calories','p':'proteins','c':'carbohydrates','fat':'fat','f':'fiber','na':'sodium','sugar':'sugar','sat':'saturatedFat'}
  for r in R:
   src=raw[r['market']][r['sourceItemId']];self.assertEqual(r['name'],' '.join(src['name']['locale'].split()))
   for k,native in fields.items():self.assertEqual(r[k],src['nutritionWithModifiers'].get(native),(r['id'],k))
   for k in ('cal','p','c','fat'):self.assertTrue(math.isfinite(r[k]));self.assertGreaterEqual(r[k],0)
 def test_no_gram_or_volume_guesses_and_only_named_servings(self):
  for r in R:
   self.assertIsNone(r['servingGrams']);self.assertIsNone(r.get('servingMillilitres'))
   self.assertEqual(r['serving'],'1 named source item · standard per-serving build');self.assertTrue(r['defaultBuildOnly'])
   self.assertTrue(all(x['quantity'] is None for x in r['components']))
 def test_source_zero_is_retained_without_missing_zero_fill(self):
  a=row('CA','Medium Diet Coke');self.assertEqual((a['cal'],a['p'],a['c'],a['fat']),(0,0,0,0))
  self.assertTrue(any(r['cal']==0 for r in R));self.assertTrue(all(r[k] is not None for r in R for k in ('cal','p','c','fat')))
 def test_repeated_navigation_rows_are_deduplicated(self):
  for m in ('CA','US'):
   staged=[r for r in R if r['market']==m];self.assertEqual(len(staged),len({r['sourceItemId'] for r in staged}));self.assertEqual(len(staged),len(raw[m]))
 def test_missing_edition_is_not_retrieval_date(self):
  for r in R:
   self.assertIsNone(r['sourceDate']);self.assertTrue(r['retrievedAt'].startswith('2026-10-17'));self.assertEqual(r['checked'],'2026-10-17')
 def test_versions_and_provenance_describe_final_rows(self):
  for r in R:
   self.assertEqual(r['sourceVersion'],hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16])
   self.assertEqual(r['nutrientProvenance']['na']['method'],'official published serving')
   if r['market']=='US':self.assertEqual(r['url'],'/burger-king-healthy-meals-macros.html')
 def test_country_ingredient_comparison_has_actual_source_statements(self):
  ca=raw['CA']['item_11895'];us=raw['US']['item_953']
  def ingredient(x,label):return ' '.join(next(z['ingredients'] for z in x['ingredients'] if z['name']['locale']==label)).lower()
  for term in ('water','onion powder','garlic powder'):self.assertIn(term,ingredient(ca,'Mayonnaise'))
  for term in ('ground red pepper','dried garlic','mustard oil'):self.assertIn(term,ingredient(us,'Mayonnaise'))
  self.assertIn('canola or soybean',ingredient(ca,'Sesame Seed Bun'));self.assertIn('faba bean',ingredient(us,'Sesame Seed Bun'))
 def test_brief_arithmetic_and_presence_match_rows(self):
  briefs=json.loads((D/'guide-briefs.json').read_text(encoding='utf-8'))['briefs'];self.assertEqual(len(briefs),3)
  byid={r['id']:r for r in R}
  for b in briefs:
   a,z=[byid[i] for i in b['recordIds']]
   for k in ('cal','p','c','fat','na'):self.assertEqual(b['calculations'][0][k],z[k]-a[k])
  presence=json.loads((D/'presence-upserts.json').read_text(encoding='utf-8'))['relationships'];self.assertEqual(len(presence),2)
  for p in presence:self.assertEqual(p['trackedRecords'],B['marketCounts'][p['country']])
 def test_mcdonalds_and_historical_pdf_not_substituted(self):
  self.assertTrue(all(r['chain']=='Burger King' for r in R));self.assertFalse(any(r['source'].endswith('.pdf') for r in R))
  blockers=json.loads((D/'blockers.json').read_text(encoding='utf-8'));self.assertIn('blocked',blockers['mcdonaldsCanada']['status']);self.assertIn('resolved',blockers['burgerKingUS']['status'])
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SupplementTests))
 report={'passed':result.wasSuccessful(),'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'records':len(R),'marketCounts':B['marketCounts'],'finderEligible':dict(Counter(r['market'] for r in R if r['finderSupported'])),'sourceEditionIsRetrievalDate':False}
 (D/'test-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 raise SystemExit(0 if result.wasSuccessful() else 1)
