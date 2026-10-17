"""Small import-boundary regressions; production data tests are separate."""
import unittest
import sys
from pathlib import Path
from import_branded_foods import normalize as legacy_normalize
from import_branded_cnf import number
import io
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'global_coverage_2026_10_17'))
from usda_expand import normalize, barcode, stream_array, iso_date

def source(**extra):
    food={'fdcId':123,'description':'Oreo Original cookies','brandName':'Oreo','brandOwner':'Example manufacturer','marketCountry':'United States','gtinUpc':'012345678901','servingSize':30,'servingSizeUnit':'g','householdServingFullText':'3 cookies','ingredients':'Wheat flour, sugar','publicationDate':'2026-04-30','modifiedDate':'2025-10-01','foodNutrients':[{'nutrient':{'id':1008,'unitName':'kcal'},'amount':480},{'nutrient':{'id':1003,'unitName':'g'},'amount':6},{'nutrient':{'id':1004,'unitName':'g'},'amount':20}]}
    food.update(extra);return food

class Boundaries(unittest.TestCase):
    def test_source_market_alias(self):
        for market in ['United States','US']:self.assertEqual(normalize(source(marketCountry=market))[0]['market'],'US')
        self.assertEqual(normalize(source(marketCountry='New Zealand'))[0]['market'],'NZ')
        self.assertEqual(normalize(source(marketCountry='Canada'))[1],'unsupported-source-market')
        self.assertEqual(normalize(source(marketCountry='unknown'))[1],'unsupported-source-market')
        # The legacy publisher remains a dependency of the Canadian importer.
        self.assertEqual(legacy_normalize(source(marketCountry='Canada'))[0]['market'],'CA')
        self.assertEqual(legacy_normalize(source(marketCountry='unknown'))[1],'unknown-market')
    def test_missing_nutrient_is_null(self):
        item,_=normalize(source());self.assertIsNone(item['nutrients']['c']);self.assertIsNone(item['nutrients']['vitaminD']);self.assertIsNone(item['sourceChecked'])
    def test_formulation_and_nation_are_not_merged(self):
        a=normalize(source())[0];b=normalize(source(ingredients='Rice flour, sugar'))[0];c=normalize(source(description='Oreo Lemon cookies'))[0];d=normalize(source(marketCountry='New Zealand'))[0]
        self.assertEqual(len({r['formulation'] for r in [a,b,c,d]}),4)
        self.assertNotEqual(legacy_normalize(source())[0]['formulation'],legacy_normalize(source(marketCountry='Canada'))[0]['formulation'])
    def test_milliliters_not_grams(self):
        item,_=normalize(source(servingSize=250,servingSizeUnit='ml'));self.assertEqual(item['basis']['unit'],'serving');self.assertEqual(item['nutrients']['cal'],1200);self.assertEqual(item['portions'],[])
    def test_failures_not_zero_or_guessed(self):
        self.assertEqual(normalize(source(servingSize=None))[1],'unsupported-or-absent-serving-basis')
        self.assertEqual(normalize(source(servingSizeUnit='cup'))[1],'unsupported-or-absent-serving-basis')
        self.assertEqual(normalize(source(foodNutrients=[]))[1],'missing-core-nutrition')
        self.assertIsNone(number('NA'));self.assertIsNone(number('nan'));self.assertEqual(number('0'),0)
    def test_barcodes_and_streaming(self):
        self.assertEqual(barcode('012345678901'),barcode('0012345678901'));self.assertIsNone(barcode('unknown'));self.assertIsNone(barcode('123'))
        self.assertEqual(list(stream_array(io.StringIO('{"BrandedFoods": [{"id":1},{"id":2}]}'))),[{'id':1},{'id':2}])
        with self.assertRaises(ValueError):list(stream_array(io.StringIO('{"BrandedFoods":[{"id":1')))
    def test_long_labels_preserve_source_identity(self):
        label='Oreo original cookies '+('source wording '*50)
        item,_=normalize(source(description=label));self.assertLessEqual(len(item['name']),240);self.assertEqual(item['sourceName'],label.strip());self.assertTrue(item['flags']);self.assertNotEqual(item['formulation'],normalize(source(description=label+' changed'))[0]['formulation'])
    def test_all_source_brands_and_standard_unit_codes(self):
        item,reason=normalize(source(brandName='Publix',servingSizeUnit='GRM'))
        self.assertIsNone(reason);self.assertEqual(item['sourceServing']['rawUnit'],'GRM');self.assertEqual(item['sourceServing']['unit'],'g');self.assertEqual(item['portions'][0]['grams'],30)
        liquid,reason=normalize(source(brandName='H-E-B',servingSize=250,servingSizeUnit='MLT'))
        self.assertIsNone(reason);self.assertEqual(liquid['basis'],{'amount':1,'unit':'serving'});self.assertEqual(liquid['portions'],[]);self.assertEqual(liquid['nutrients']['cal'],1200)
    def test_source_versions_preserve_ids_and_changed_nutrition(self):
        a=normalize(source(publicationDate='9/30/2020'))[0]
        newer=source(fdcId=124,publicationDate='11/13/2020');newer['foodNutrients'][0]['amount']=500
        b=normalize(newer)[0]
        self.assertNotEqual(a['id'],b['id']);self.assertEqual(a['versionGroup'],b['versionGroup']);self.assertNotEqual(a['formulation'],b['formulation'])
        self.assertGreater(b['sourcePublished'],a['sourcePublished']);self.assertEqual(iso_date('11/13/2020'),'2020-11-13')
    def test_history_is_a_reference_without_invented_nutrients(self):
        item,_=normalize(source(foodUpdateLog=[{'fdcId':99,'publicationDate':'4/1/2019'}]))
        self.assertEqual(item['sourceHistory'][-1],{'sourceRef':'99','sourcePublished':'2019-04-01'})
        self.assertNotIn('nutrients',item['sourceHistory'][-1])
if __name__=='__main__':unittest.main()
