"""Source identity, null handling, portions and arithmetic integration gates."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_master_restaurants import guide_specs
PAYLOAD=json.loads((ROOT/'tools/master_release/restaurant_records.json').read_text(encoding='utf-8'))
ROWS=PAYLOAD['records']
PRESENCE=json.loads((ROOT/'tools/master_release/restaurant_presence.json').read_text(encoding='utf-8'))['relationships']

class RestaurantIntegrity(unittest.TestCase):
 def test_market_and_identity(self):
  self.assertEqual(len({r['id'] for r in ROWS}),len(ROWS))
  for r in ROWS:
   self.assertEqual((r['market'],r['country'],r['region']),('CA','CA','CA'))
   self.assertTrue(r['id'].startswith('CA|'));self.assertTrue(r['url'].startswith('/ca/en/restaurants/'))
   self.assertEqual(r['retrievedAt'],'2026-10-12');self.assertEqual(len(r['sourceHash']),64)
   self.assertTrue(r['source'].startswith('https://'));self.assertEqual(len(r['sourceVersion']),16)
 def test_core_completeness_is_exact(self):
  for r in ROWS:self.assertEqual(r['macroComplete'],all(r[k] is not None for k in ['cal','p','c','fat']))
  for r in ROWS:
   if r['finderSupported']:self.assertTrue(r['macroComplete']);self.assertNotIn(r['category'],['component','sauce'])
 def test_unknown_pizza_nova_macros(self):
  rows=[r for r in ROWS if r['chain']=='Pizza Nova'];self.assertEqual(len(rows),39)
  for r in rows:
   self.assertTrue(r['cal']>0);self.assertFalse(r['finderSupported'])
   for key in ['p','c','fat','f','na','sat','sugar','servingGrams']:self.assertIsNone(r[key])
 def test_mary_source_errors_not_guessed(self):
  names={r['name'] for r in ROWS if r['chain']=='Mary Brown’s'}
  for name in ['Taters (Large)','Fries (Large)','3 PC: Spicy Chicken Tenders','5 PC: Spicy Chicken Tenders']:self.assertNotIn(name,names)
  self.assertTrue(any('exceeds' in i['reason'] for i in PAYLOAD['issues']))
 def test_pizza_pizza_contradiction_is_null(self):
  row=next(r for r in ROWS if r['name']=='Small Pepperoni Pizza — 1 slice')
  self.assertEqual(row['cal'],210);self.assertEqual(row['fat'],8);self.assertIsNone(row['sat'])
  self.assertEqual(row['sourceIssues'][0]['rawValue'],35)
 def test_booster_sizes_and_micronutrients(self):
  row=next(r for r in ROWS if r['name']=='Ripped Berry (R)')
  self.assertEqual((row['p'],row['cal']),(29,470));self.assertEqual(row['servingMillilitres'],710);self.assertIsNone(row['servingGrams'])
  self.assertEqual(row['additionalNutrients']['calcium'],{'value':400,'unit':'mg','method':'official reported serving'})
  row=next(r for r in ROWS if r['name']=='Chocolate NOT-ty Butter (S)');self.assertEqual((row['cal'],row['p']),(360,12))
 def test_dominos_exact_component_sums(self):
  byid={r['id']:r for r in ROWS}
  builds=[r for r in ROWS if r['verificationStatus']=='calculated-from-official-components'];self.assertEqual(len(builds),3)
  for r in builds:
   comp=[byid[c['id']] for c in r['calculatedFrom']]
   self.assertTrue(all(x['sourcePage']==5 for x in comp));self.assertTrue(all(x['builderScope']=='CA|dominos|small-hand-tossed|one-sixth' for x in comp))
   for k in ['cal','p','c','fat','f','na']:self.assertEqual(r[k],sum(x[k] for x in comp))
  cheese=next(r for r in builds if r['name']=='Small hand-tossed cheese pizza — 1 slice');self.assertEqual((cheese['cal'],cheese['p']),(195,10))
  pepperoni=next(r for r in builds if r['name']=='Small hand-tossed pepperoni pizza — 1 slice');self.assertEqual((pepperoni['cal'],pepperoni['p']),(200,9))
 def test_subway_same_named_different_builds(self):
  classic=next(r for r in ROWS if r['name']=='6" Classics Subs — Rotisserie-Style Chicken')
  fresh=next(r for r in ROWS if r['name']=='6-inch Fresh Fit — Rotisserie-Style Chicken')
  self.assertNotEqual(classic['id'],fresh['id']);self.assertEqual((classic['p'],fresh['p']),(28,30));self.assertNotEqual(classic['servingGrams'],fresh['servingGrams'])
 def test_presence_and_coverage_are_separate(self):
  ca={r['restaurantBrand']:r for r in PRESENCE if r['country']=='CA'};self.assertEqual(len(ca),25)
  for brand in ['McDonald’s','Burger King','Chipotle','Wendy’s','KFC','Popeyes']:
   self.assertEqual(ca[brand]['presence']['status'],'confirmed');self.assertFalse(ca[brand]['finderSupported']);self.assertEqual(ca[brand]['trackedRecords'],0)
  self.assertEqual(ca['Pizza Nova']['coverageStatus'],'calories-only');self.assertFalse(ca['Pizza Nova']['finderSupported'])
  self.assertTrue(ca['Subway']['finderSupported']);self.assertEqual(ca['Subway']['completeMacroRecords'],85)
 def test_guides_have_distinct_useful_content(self):
  specs=guide_specs();self.assertEqual(len(specs),6);self.assertEqual(len({s['route'] for s in specs}),6)
  for s in specs:
   self.assertTrue(s['route'].startswith('/ca/en/restaurants/'));self.assertEqual(s['body'].count('<h1>'),1)
   self.assertRegex(s['body'],r'<table(?:\s|>)');self.assertIn('Source edition:',s['body']);self.assertNotIn('U.S. source values',s['body'])
  nova=next(s for s in specs if '/pizza-nova/' in s['route']);self.assertIn('denominator',nova['body']);self.assertNotIn('Find an order',nova['body'])
  domino=next(s for s in specs if '/domino-s/' in s['route']);self.assertIn('120 kcal crust + 5 kcal pizza sauce + 70 kcal regular cheese',domino['body'])
 def test_mary_complete_order_arithmetic(self):
  a=next(r for r in ROWS if r['chain']=='Mary Brown’s' and r['name']=='Big Mary');b=next(r for r in ROWS if r['chain']=='Mary Brown’s' and r['name']=='Taters (Small)')
  self.assertEqual(a['cal']+b['cal'],1066);self.assertAlmostEqual(a['p']+b['p'],42.4);self.assertEqual(a['na']+b['na'],1266)

if __name__=='__main__':unittest.main(verbosity=2)
