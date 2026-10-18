"""Regression checks for source scope, arithmetic, nulls and safe integration."""
import copy, hashlib, json, math, unittest
from pathlib import Path
from collections import Counter
import markets_integrate
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/flagship-release-2026-10-18/markets'
B=markets_integrate.load();ALL=B['records']+B['updates']
def one(market,chain,name):
    matches=[r for r in ALL if r['market']==market and r['chain']==chain and r['name']==name]
    assert len(matches)==1,(market,chain,name,len(matches))
    return matches[0]

class MarketReleaseTests(unittest.TestCase):
    def test_country_identities_and_counts(self):
        self.assertEqual(len(ALL),len({r['id']for r in ALL}))
        self.assertEqual(B['counts']['newSourcePortionRecords'],1967)
        self.assertEqual(B['counts']['newCalculatedOrders'],4)
        self.assertEqual(len(B['updates']),135)
        self.assertEqual({r['market']for r in ALL},{'CA','US','AU','NZ','IN','SG','FR','JP','IE'})
        for r in ALL:
            self.assertEqual(r['market'],r['country']);self.assertEqual(r['market'],r['region'])
            if r in B['records']:self.assertTrue(r['id'].startswith(r['market']+'|'))
            self.assertEqual(r['restaurantMarketId'],r['market']+'|'+r['restaurantId'])

    def test_primary_source_capture_hashes(self):
        source_hashes=set()
        for src in B['sources']:
            p=ROOT/src['file'];self.assertTrue(p.is_file(),src['file'])
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),src['sha256'])
            self.assertFalse(src['retrievalIsVerification']);source_hashes.add(src['sha256'])
        for r in ALL:self.assertIn(r['sourceHash'],source_hashes)

    def test_source_versions_are_reproducible(self):
        for r in ALL:
            x={k:v for k,v in r.items() if k!='sourceVersion'}
            self.assertEqual(r['sourceVersion'],hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16],r['id'])

    def test_cfa_markets_and_breakfast(self):
        ca=one('CA','Chick-fil-A','Chick-fil-A® Chicken Sandwich')
        us=one('US','Chick-fil-A','Chick-fil-A® Chicken Sandwich')
        self.assertEqual((ca['servingGrams'],ca['cal'],ca['p']),(185,440,29))
        self.assertEqual((us['servingGrams'],us['cal']),(183,420))
        self.assertFalse(any(r['meal']=='breakfast' for r in ALL if r['market']=='CA' and r['chain']=='Chick-fil-A'))
        self.assertEqual(one('US','Chick-fil-A','Egg White Grill')['cal'],300)
        self.assertEqual(sum(r['meal']=='breakfast'for r in B['records'] if r['market']=='US'),20)

    def test_unresolved_pouch_mass_is_not_scaled(self):
        r=one('CA','Chick-fil-A','Buddy Fruits® Multifruit')
        self.assertIsNone(r['servingGrams']);self.assertEqual(r['sourceReportedServingGrams'],100)
        self.assertEqual(r['portionConflict']['productDescriptionGrams'],90)
        self.assertEqual(r['cal'],60)
        self.assertFalse(any('Multifruit' in r['name']for r in ALL if r['verificationStatus']=='calculated-from-official-components'))

    def test_precise_component_totals_and_nulls(self):
        by_id={r['id']:r for r in ALL}
        for r in ALL:
            if r['verificationStatus']!='calculated-from-official-components':continue
            for k in ('cal','p','c','fat','f','na','sugar','sat'):
                parts=[by_id[c['id']].get(k)for c in r['components']]
                if any(x is None for x in parts):self.assertIsNone(r[k])
                else:self.assertAlmostEqual(r[k],sum(parts))
            self.assertTrue(all(c['id'].startswith('CA|')for c in r['components']))
        r=one('CA','Chick-fil-A','Grilled sandwich, small waffle fries & small unsweet tea')
        self.assertEqual((r['cal'],r['p'],r['c'],r['fat']),(700,32.1,79,30))

    def test_bounded_and_missing_values_remain_unknown(self):
        bounded=[r for r in ALL if r.get('nutrientBounds')]
        self.assertTrue(bounded)
        for r in bounded:
            for k in r['nutrientBounds']:self.assertIsNone(r[k])
        self.assertIsNone(one('JP','KFC','オリジナルチキン')['sugar'])
        self.assertEqual(one('JP','KFC','オリジナルチキン')['na'],585)

    def test_pizza_units_not_whole_pizza(self):
        for r in ALL:
            if r['market']not in ('AU','NZ') or r['chain']!='Domino’s' or not r.get('sourceServingCount'):continue
            if '1 slice' in r['serving']:
                self.assertIn(r['sourceServingCount'],(4,6,8))
                if r['sourceVariant']=='Mini':self.assertEqual(r['sourceServingCount'],4)
                self.assertIn('1 slice',r['serving'])
        r=one('IN','Domino’s','Margherita — Cheese Burst-Regular')
        self.assertAlmostEqual(r['cal'],899.21);self.assertIsNone(r['servingGrams'])

    def test_sg_category_table_order(self):
        r=one('SG','Chick-fil-A','Chick-fil-A® Waffle Potato Fries — Small')
        self.assertEqual((r['category'],r['sourceGroup'],r['cal']),('side','Sides',323))
        treats=[r for r in ALL if r['market']=='SG' and r['sourceGroup']=='Treats']
        self.assertTrue(treats);self.assertTrue(all(r['category']=='dessert'for r in treats))

    def test_independent_audit_dispositions(self):
        removed=set(B['withdrawnIds'])
        self.assertIn('NZ|domino-s|official-S00179-41a6c3af-4a90-4b94-8485-0f53a100231f',removed)
        self.assertFalse(any(r['id']in removed for r in B['records']))
        self.assertEqual(len([r for r in B['records']if r['market']=='FR' and 'Baby Whopper' in r['name']]),0)
        self.assertTrue(one('IN','Domino’s','Chicken Sausage — Fresh Pan Pizza-Regular — Pizza Mania'))
        kids=one('FR','Burger King','Hamburger — menu enfant (produit seul)')
        self.assertEqual(kids['cal'],262)

    def test_irish_serving_variants_are_distinct(self):
        rustica=one('IE','Zizzi','Margherita — Rustica pizza')
        classic=one('IE','Zizzi','Margherita — Classic pizza')
        self.assertEqual((rustica['cal'],classic['cal']),(929,780))
        self.assertNotEqual(rustica['id'],classic['id'])
        self.assertIn('ROI.BEL',rustica['source'])
        self.assertEqual(one('IE','Zizzi','Tiramisu')['category'],'dessert')

    def test_gallon_catering_and_sauce_not_person_meal(self):
        for r in ALL:
            if r.get('size')=='Gallon' or r['category']=='component':self.assertFalse(r['finderSupported'],r['id'])

    def test_integration_is_idempotent_and_preserves_unrelated(self):
        updates=copy.deepcopy(B['updates'])
        unrelated={'id':'US|unrelated|test','market':'US','note':'must survive'}
        before={'records':updates+[unrelated],'unrelatedMetadata':'retain'}
        snapshot=copy.deepcopy(before)
        result=markets_integrate.integrate(before)
        self.assertEqual(before,snapshot)
        self.assertEqual(result,markets_integrate.integrate(result))
        self.assertEqual(result['unrelatedMetadata'],'retain');self.assertIn(unrelated,result['records'])
        with self.assertRaises(ValueError):markets_integrate.integrate([])
        conflicting=copy.deepcopy(result);next(r for r in conflicting['records']if r['id']==B['records'][0]['id'])['cal']=-1
        with self.assertRaises(ValueError):markets_integrate.integrate(conflicting)

    def test_every_market_candidate_has_disposition(self):
        m=json.loads((D/'country-restaurant-matrix.json').read_text(encoding='utf-8'))
        pairs={(r['market'],r['chain'])for r in m['rows']}
        for country in m['markets']:
            for chain in m['globalCandidates']:self.assertIn((country,chain),pairs)
        for row in m['rows']:
            self.assertTrue(row['disposition']);self.assertTrue(row['unresolvedGaps'])
            self.assertNotEqual(row['presenceStatus'],'absent')

if __name__=='__main__':unittest.main(verbosity=2)
