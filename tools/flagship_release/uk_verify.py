"""Regression, market-isolation and source-arithmetic checks for the UK batch.

Offline and standard-library only. Does not fetch sources, mutate the shared
registry or imply that automated checks are a visual review of every PDF page.
"""
from pathlib import Path
import collections, copy, csv, hashlib, json, math, unittest
from urllib.parse import urlsplit
import uk_integration as api

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/'docs/flagship-release-2026-10-18/uk'
SRC=DOC/'sources'
BATCH=api.load_batch()
ROWS=BATCH['records']
FIELDS=('cal','p','c','fat','f','na','sugar','sat')

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def exact(chain,name):
    found=[r for r in ROWS if r['chain']==chain and r['name']==name]
    assert len(found)==1,(chain,name,len(found))
    return found[0]

class UKReleaseTests(unittest.TestCase):
    def test_01_scope_counts_and_unique_identities(self):
        self.assertEqual(len(ROWS),4736)
        self.assertEqual(len({r['id'] for r in ROWS}),len(ROWS))
        self.assertEqual(len({r['chain'] for r in ROWS}),17)
        for r in ROWS:
            self.assertEqual((r['market'],r['country'],r['region']),('GB','GB','GB'))
            self.assertTrue(r['id'].startswith('GB|'+r['restaurantId']+'|'))
            self.assertEqual(r['restaurantMarketId'],'GB|'+r['restaurantId'])
            self.assertTrue(r['name'] and r['serving'] and r['availabilityScope'])

    def test_02_units_unknowns_and_numeric_integrity(self):
        for r in ROWS:
            for k in FIELDS:
                value=r.get(k)
                self.assertTrue(value is None or isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0,(r['id'],k,value))
            self.assertTrue(all(r.get(k) is not None for k in ('cal','p','c','fat')))
            self.assertEqual(r['units'],dict(cal='kcal',p='g',c='g',fat='g',f='g',na='mg',sugar='g',sat='g'))
            grams=r.get('servingGrams')
            self.assertTrue(grams is None or grams>0,(r['id'],grams))
            for child,parent in [('sat','fat'),('sugar','c')]:
                if r.get(child) is not None:
                    self.assertLessEqual(r[child],r[parent]+.5,(r['id'],child,parent))

    def test_03_source_capture_hashes_and_provenance(self):
        sources=read(DOC/'source-register.json')
        allowed={(s['url'],s['sha256']) for s in sources}
        for s in sources:
            self.assertFalse(s['retrievalIsVerification'])
            self.assertEqual(hashlib.sha256((ROOT/s['file']).read_bytes()).hexdigest(),s['sha256'])
            self.assertEqual(s['marketScope'],'GB')
        for r in ROWS:
            self.assertIn((r['source'],r['sourceHash']),allowed,r['id'])
            self.assertEqual(urlsplit(r['source']).scheme,'https')
            self.assertTrue(r['sourcePage'] is not None and r['sourceCaptureMethod'])
            self.assertTrue(r['retrievedAt'])
            for k in FIELDS:
                self.assertEqual(k in r['nutrientProvenance'],r.get(k) is not None,(r['id'],k))
            version=hashlib.sha256(json.dumps({k:v for k,v in r.items() if k!='sourceVersion'},sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
            self.assertEqual(version,r['sourceVersion'],r['id'])

    def test_04_source_and_verification_dates_remain_distinct(self):
        for r in ROWS:
            self.assertEqual(r['checked'],'2026-10-18')
            self.assertTrue(r['retrievedAt'].startswith('2026-10-18'))
            if r['chain'] in ('Nando’s','LEON','Pepe’s','Caffè Nero','Chipotle','Chopstix'):
                self.assertIsNone(r['sourceDate'])
        self.assertEqual(exact('Starbucks','Pumpkin Spice Latte - skimmed milk · Tall')['sourceDate'],'2026-09-18')
        self.assertEqual(exact('Chick-fil-A','Chick-fil-A® Chicken Sandwich')['sourceDate'],'2026-07 (0726 footer)')

    def test_05_salt_sodium_conversion(self):
        checked=0
        for r in ROWS:
            if r['chain']=='Wagamama':continue
            salt=r['nativeNutrients'].get('salt')
            if salt is None:continue
            factor=r['servingGrams']/100 if r['chain']=='Chick-fil-A' else 1
            self.assertAlmostEqual(r['na'],salt*factor*400,places=6,msg=r['id'])
            checked+=1
        self.assertGreater(checked,4000)

    def test_06_chickfila_per100g_serving_arithmetic(self):
        for r in [r for r in ROWS if r['chain']=='Chick-fil-A']:
            self.assertIsNone(r['f'])
            for k in ('cal','p','c','fat','sugar','sat'):
                self.assertAlmostEqual(r[k],r['nativePer100g'][k]*r['servingGrams']/100,places=6)
            self.assertIn('calculated',r['nutrientBasis'])
        row=exact('Chick-fil-A','Chick-fil-A® Chicken Sandwich')
        self.assertEqual(row['servingGrams'],178)
        self.assertAlmostEqual(row['cal'],226*1.78)
        self.assertAlmostEqual(row['p'],15*1.78)
        self.assertFalse(any(r['meal']=='breakfast' for r in ROWS if r['chain']=='Chick-fil-A'))

    def test_07_wasabi_mixed_nutrient_basis(self):
        for r in [r for r in ROWS if r['chain']=='Wasabi']:
            self.assertIsNone(r['f'])
            for k in ('p','c','fat','sugar','sat'):
                self.assertAlmostEqual(r[k],r['nativePer100g'][k]*r['servingGrams']/100,places=6)
            self.assertIn('published serving kcal',r['nutrientBasis'])
        r=exact('Wasabi','Avocado and Edamame Onigiri')
        self.assertEqual(r['cal'],194)
        self.assertAlmostEqual(r['p'],4*1.21)

    def test_08_nandos_native_units_and_subregions(self):
        menu=read(SRC/'nandos-data.json')['result']['data']['nandos']['menu']
        lookup={}
        for section in menu['sections']:
            for item in section['items']:
                for i,facts in enumerate(item['nutritionalInfo']['factsForPortionSizes']):
                    scope=item.get('restaurantGroup') or ''
                    if scope in ('Regional pricing trial 26','Tiered Menu pricing trial'):scope=''
                    lookup[(item['id']+'#facts-'+str(i),scope)]=facts
        for r in [r for r in ROWS if r['chain']=='Nando’s']:
            scope=r['availabilityScope']
            if scope=='UK source-listed item; check restaurant availability':scope=''
            native=lookup[(r['sourcePage'],scope)]
            self.assertEqual(r['cal'],native['energyKcal'])
            for k,n in [('p','proteinMg'),('c','totalCarbsMg'),('fat','fatMg'),('f','fibreMg')]:
                self.assertAlmostEqual(r[k],native[n]/1000)
            if 'Gatwick' in r['name']:self.assertIn('Gatwick',r['availabilityScope'])
            if 'Northern Ireland' in r['name']:self.assertIn('Northern Ireland',r['availabilityScope'])
        self.assertEqual(exact('Nando’s','Spicy Rice · Regular')['cal'],246)
        ni=[r for r in ROWS if r['chain']=='Nando’s' and r['name'].startswith('Spicy Rice · Regular') and 'Northern Ireland' in r['name']]
        self.assertEqual(len(ni),1)
        self.assertEqual(ni[0]['cal'],197)

    def test_09_leon_explicit_ingredients_and_weights(self):
        lookup={x['_id']:x for x in read(SRC/'leon-products.json')}
        for r in [r for r in ROWS if r['chain']=='LEON']:
            info=lookup[r['productId']]['nutritionInfo']
            self.assertEqual(r['cal'],float(info['kcal']))
            self.assertEqual(r['p'],float(info['protein']))
        r=exact('LEON','Smoked Salmon & Pickle Dill Cream Muffin')
        self.assertEqual((r['servingGrams'],r['cal'],r['p']),(136,320,9.9))
        for name in ['Unsweetened Iced Matcha Latte','Moju Ginger Shot','Unsweetened Matcha Latte']:
            r=exact('LEON',name);self.assertIsNone(r['servingGrams']);self.assertEqual(r['sourceServingGrams'],0)

    def test_10_component_rows_not_claimed_as_complete_orders(self):
        chipotle=[r for r in ROWS if r['chain']=='Chipotle']
        self.assertEqual(len(chipotle),24)
        self.assertTrue(all(r['category']=='component' and not r['finderSupported'] for r in chipotle))
        for r in ROWS:
            if r['category']=='component':self.assertFalse(r['finderSupported'])
            if r['chain']=='Tortilla' and '—' in r['name'] and r['sourcePage']<=17:
                self.assertEqual(r['category'],'component')
        self.assertFalse(any(r['verificationStatus']=='calculated-from-official-components' for r in ROWS))

    def test_11_unknown_fibre_not_inferred_as_zero(self):
        for chain in ['Pepe’s','Chick-fil-A','Zizzi','ASK Italian','Wasabi']:
            self.assertTrue(all(r['f'] is None for r in ROWS if r['chain']==chain),chain)
        self.assertGreater(sum(r['na'] is None for r in ROWS),0)

    def test_12_edition_and_portion_reference_anchors(self):
        # Explicit source-row anchors catch swapped per-100g/portion columns,
        # milk alternatives, and condiment/base versus whole-order mistakes.
        anchors=[('Wendy’s',"Wendy's Single",524,28),('Wendy’s',"Wendy's Double",879,54),
            ('Wagamama','katsu chicken wrap',481,29.8),('Wagamama','yasai katsu wrap',596,18.6),
            ('Five Guys','Bacon**',78,6.4),('Five Guys','Beef Burger Patty',195,18),
            ('Pepe’s','1/2 Chicken',798,125.6),('Pepe’s','1/4 Chicken',399,62.8),
            ('Starbucks','Pumpkin Spice Latte - skimmed milk · Short',128,4.3),('Starbucks','Pumpkin Spice Latte - skimmed milk · Tall',185,6.7),
            ('Zizzi','Complimentary Pasta Crisps',38,0),('Zizzi','Complimentary Hot Chocolate',28,1),
            ('ASK Italian','Lasagne Garlic Bread',874,35),('ASK Italian',"S'mores Dessert Pizza",1182,26),
            ('PizzaExpress','Dough Balls Al Forno',527,31.1),('PizzaExpress','Dough Balls Al Forno GF',582,25.7),
            ('Tortilla','Medium Burrito/Bowl — Tortilla Wrap',195,5),('Tortilla','Medium Burrito/Bowl — Coriander Rice (Burrito)',117,3),
            ('Tim Hortons','Americano',0,.02),('Tim Hortons','Americano (Small)',0,.01),
            ('Caffè Nero','Cinnamon Roll Latte · Semi Skimmed Milk',195,9.5),('Caffè Nero','Cinnamon Roll Latte · Skimmed Milk',167,9.6),
            ('Chipotle','Flour Tortilla* (burrito)',297,7.9),('Chipotle','Flour Tortilla* (taco)',94,2.5),
            ('Chopstix','VEGETABLE CHOW MEIN · Taster',123,3.7),('Chopstix','VEGETABLE CHOW MEIN · Small',246,7.4)]
        for chain,name,cal,p in anchors:
            r=exact(chain,name);self.assertEqual((r['cal'],r['p']),(cal,p),(chain,name))

    def test_13_airport_and_recipe_portions_distinct(self):
        for name in ['Goats Cheese','Spinach']:
            regular=exact('PizzaExpress',name+' · Pizza topping')
            airport=exact('PizzaExpress',name+' · Airport breakfast extra')
            self.assertNotEqual(regular['id'],airport['id'])
            self.assertNotEqual(regular['serving'],airport['serving'])
            self.assertIn('airport',airport['availabilityScope'])
        for r in ROWS:
            if r['chain']=='PizzaExpress' and r['meal']=='breakfast':
                self.assertIn('Edinburgh and Gatwick',r['availabilityScope'])
            if r['chain']=='Caffè Nero' and '(NI)' in r['name']:
                self.assertEqual(r['availabilityScope'],'Northern Ireland only')

    def test_14_withdrawals_do_not_survive_upsert(self):
        withdrawn=set(BATCH['withdrawnIds'])
        self.assertEqual(len(withdrawn),11)
        self.assertFalse(withdrawn & {r['id'] for r in ROWS})
        old=[dict(id=x,market='GB',country='GB',name='old withdrawn') for x in withdrawn]
        integrated=api.integrate(old)
        self.assertFalse(withdrawn & {r['id'] for r in integrated})
        self.assertEqual(len(integrated),len(ROWS))

    def test_15_market_preservation_and_idempotence(self):
        unrelated=[dict(id='US|regression-fixture',market='US',cal=None,p=5,privateMarker='unchanged'),dict(id='GB|preserved-fixture',market='GB',cal=123)]
        before=copy.deepcopy(unrelated)
        once=api.integrate(unrelated);twice=api.integrate(once)
        self.assertEqual(once,twice)
        self.assertEqual(unrelated,before)
        self.assertEqual(once[:2],before)

    def test_16_presence_is_not_synonymous_with_finder_support(self):
        relations=api.presence_upserts()
        self.assertEqual(len(relations),17)
        chip=next(x for x in relations if x['restaurantId']=='chipotle')
        self.assertTrue(chip['nutritionAvailable'])
        self.assertFalse(chip['finderSupported'])
        self.assertEqual(chip['coverageStatus'],'tracked-components-only')
        self.assertEqual(chip['finderRecords'],0)
        self.assertTrue(all(x['calculatedOrders']==0 for x in relations))

    def test_17_all_named_candidate_dispositions_and_reports(self):
        matrix=read(DOC/'country-restaurant-matrix.json')['relationships']
        self.assertEqual(len(matrix),36)
        self.assertEqual(len({r['restaurant'] for r in matrix}),36)
        self.assertEqual(sum(r['disposition']=='not-implemented-specific-gap' for r in matrix),16)
        self.assertEqual(sum(r['newPortions'] for r in matrix),len(ROWS))
        for r in matrix:
            self.assertTrue(r['presenceSource'].startswith('https://') and r['remaining'])
            self.assertEqual(r['exactPhotoAssetsAdded'],0)
        defs=api.definitions()
        self.assertEqual(sum(d['records'] for d in defs),len(ROWS))
        with (DOC/'menu-category-completeness.csv').open(encoding='utf-8',newline='') as f:
            groups=list(csv.DictReader(f))
        self.assertEqual(sum(int(g['stagedNamedPortions']) for g in groups),len(ROWS))
        self.assertEqual(len(groups),244)

    def test_18_no_unlicensed_photos_or_unreviewed_customization_claim(self):
        for r in ROWS:
            self.assertFalse(r.get('image') or r.get('imageUrl') or r.get('photo'))
            self.assertFalse(r.get('allergenSafe',False))
            self.assertNotIn('perfect for',r['name'].lower())
        for r in [r for r in ROWS if r['chain']=='Starbucks']:
            self.assertTrue(r['serving'] and r['sourceGroup'])

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(UKReleaseTests))
    report=dict(checkedAt='2026-10-18',testsRun=result.testsRun,failures=len(result.failures),errors=len(result.errors),records=len(ROWS),chains=dict(collections.Counter(r['chain'] for r in ROWS)),sourceCaptureFiles=len(read(DOC/'source-register.json')),withdrawnIds=BATCH.get('withdrawnIds',[]),scope='Offline unit, market-isolation, arithmetic and source-byte integrity checks; not a claim that every source PDF page or rendered public page was visually inspected.')
    (DOC/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
