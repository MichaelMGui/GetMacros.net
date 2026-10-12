"""Small import-boundary regressions; production data tests are separate."""
import unittest
from import_branded_foods import normalize, barcode, stream_array
from import_branded_cnf import number
import io

def source(**extra):
    food={'fdcId':123,'description':'Oreo Original cookies','brandName':'Oreo','brandOwner':'Example manufacturer','marketCountry':'United States','gtinUpc':'012345678901','servingSize':30,'servingSizeUnit':'g','householdServingFullText':'3 cookies','ingredients':'Wheat flour, sugar','publicationDate':'2026-04-30','modifiedDate':'2025-10-01','foodNutrients':[{'nutrient':{'id':1008,'unitName':'kcal'},'amount':480},{'nutrient':{'id':1003,'unitName':'g'},'amount':6},{'nutrient':{'id':1004,'unitName':'g'},'amount':20}]}
    food.update(extra);return food

class Boundaries(unittest.TestCase):
    def test_source_market_alias(self):
        for market in ['United States','US']:self.assertEqual(normalize(source(marketCountry=market))[0]['market'],'US')
        self.assertEqual(normalize(source(marketCountry='Canada'))[0]['market'],'CA')
        self.assertEqual(normalize(source(marketCountry='unknown'))[1],'unknown-market')
    def test_missing_nutrient_is_null(self):
        item,_=normalize(source());self.assertIsNone(item['nutrients']['c']);self.assertIsNone(item['nutrients']['vitaminD']);self.assertIsNone(item['sourceChecked'])
    def test_formulation_and_nation_are_not_merged(self):
        a=normalize(source())[0];b=normalize(source(ingredients='Rice flour, sugar'))[0];c=normalize(source(description='Oreo Lemon cookies'))[0];d=normalize(source(marketCountry='Canada'))[0]
        self.assertEqual(len({r['formulation'] for r in [a,b,c,d]}),4)
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
if __name__=='__main__':unittest.main()
