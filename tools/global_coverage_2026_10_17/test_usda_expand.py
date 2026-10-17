"""Regression tests for real import risks: units, nulls, history and identity."""
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest

from usda_expand import barcode, dump_json, iso_date, json_array, load_brand_counts, normalize, stream_array


def source(**changes):
    row = {'fdcId': 9876543, 'description': 'Unlisted independent grocery product',
           'brandName': 'An independent brand absent from the old allowlist',
           'brandOwner': 'Example manufacturer', 'marketCountry': 'United States',
           'gtinUpc': '012345678901', 'servingSize': 30, 'servingSizeUnit': 'g',
           'householdServingFullText': '3 pieces', 'publicationDate': '11/13/2020',
           'modifiedDate': '9/2/2020', 'availableDate': '8/14/2020',
           'foodNutrients': [{'nutrient': {'id': 1008, 'unitName': 'kcal'}, 'amount': 400},
                             {'nutrient': {'id': 1003, 'unitName': 'g'}, 'amount': 0},
                             {'nutrient': {'id': 1004, 'unitName': 'g'}, 'amount': 8}],
           'foodUpdateLog': [{'fdcId': 9876543, 'publicationDate': '11/13/2020'},
                             {'fdcId': 123456, 'publicationDate': '4/1/2019'}]}
    row.update(changes)
    return row


class ImportBoundaries(unittest.TestCase):
    def test_unlisted_brands_are_imported(self):
        row, reason = normalize(source())
        self.assertIsNone(reason)
        self.assertEqual(row['id'], 'branded:usda:9876543')
        self.assertIsNone(row['sourceChecked'])
        self.assertEqual(row['license'], 'CC0-1.0')

    def test_iso_dates_are_actual_chronology(self):
        row, _ = normalize(source())
        self.assertEqual(row['sourcePublished'], '2020-11-13')
        self.assertEqual(row['sourceModified'], '2020-09-02')
        self.assertEqual(row['labelDate'], '2020-08-14')
        self.assertGreater(iso_date('11/1/2020'), iso_date('9/30/2020'))
        self.assertIsNone(iso_date('2/30/2020'))
        self.assertIsNone(iso_date(None))

    def test_missing_negative_nonfinite_and_wrong_units_are_unknown(self):
        food = source()
        food['foodNutrients'].extend([
            {'nutrient': {'id': 1005, 'unitName': 'g'}, 'amount': -5},
            {'nutrient': {'id': 2000, 'unitName': 'g'}, 'amount': float('nan')},
            {'nutrient': {'id': 1093, 'unitName': 'g'}, 'amount': 100},
            {'nutrient': {'id': 1258, 'unitName': 'g'}, 'amount': True},
        ])
        row, _ = normalize(food)
        self.assertEqual(len(row['nutrients']), 30)
        self.assertEqual(row['nutrients']['p'], 0)
        for key in ('c', 'sugar', 'na', 'sat', 'vitaminD'):
            self.assertIsNone(row['nutrients'][key])
            self.assertNotIn(key, row['provenance'])

    def test_documented_gs1_unit_aliases_preserve_amounts_and_raw_codes(self):
        grams, _ = normalize(source(servingSizeUnit='GRM'))
        self.assertEqual(grams['sourceServing']['unit'], 'g')
        self.assertEqual(grams['sourceServing']['rawUnit'], 'GRM')
        self.assertEqual(grams['portions'][0]['grams'], 30)
        self.assertEqual(grams['nutrients']['cal'], 400)
        liquid, _ = normalize(source(servingSize=250, servingSizeUnit='MLT'))
        self.assertEqual(liquid['basis'], {'amount': 1, 'unit': 'serving'})
        self.assertEqual(liquid['nutrients']['cal'], 1000)
        self.assertEqual(liquid['sourcePer100']['nutrients']['cal'], 400)
        self.assertEqual(liquid['portions'], [])
        self.assertEqual(liquid['sourceServing']['unit'], 'ml')

    def test_unclear_or_absent_units_and_invalid_servings_rejected(self):
        for changes in ({'servingSizeUnit': 'IU'}, {'servingSizeUnit': 'MG'},
                        {'servingSizeUnit': 'GM'}, {'servingSizeUnit': 'cup'},
                        {'servingSize': 0}, {'servingSize': None},
                        {'servingSize': float('inf')}, {'servingSize': True}):
            self.assertEqual(normalize(source(**changes))[1], 'unsupported-or-absent-serving-basis')

    def test_history_references_do_not_fabricate_nutrients(self):
        row, _ = normalize(source())
        self.assertEqual(row['sourceHistory'], [
            {'sourceRef': '9876543', 'sourcePublished': '2020-11-13'},
            {'sourceRef': '123456', 'sourcePublished': '2019-04-01'}])
        self.assertNotIn('nutrients', row['sourceHistory'][1])

    def test_source_versions_and_changed_nutrition_are_distinct(self):
        row, _ = normalize(source())
        newer = source(fdcId=9876544)
        newer['foodNutrients'][0]['amount'] = 500
        changed, _ = normalize(newer)
        self.assertEqual(row['versionGroup'], changed['versionGroup'])
        self.assertNotEqual(row['formulation'], changed['formulation'])
        self.assertNotEqual(row['id'], changed['id'])
        other, _ = normalize(source(marketCountry='New Zealand'))
        self.assertNotEqual(row['versionGroup'], other['versionGroup'])
        self.assertEqual(normalize(source(marketCountry='Canada'))[1], 'unsupported-source-market')

    def test_source_barcode_keeps_leading_zeros(self):
        self.assertEqual(barcode('012345678901'), '00012345678901')
        self.assertEqual(barcode('0012345678901'), '00012345678901')
        self.assertIsNone(barcode('123'))

    def test_streaming_and_deterministic_gzip(self):
        self.assertEqual(list(stream_array(io.StringIO('{"BrandedFoods":[{"fdcId":1},{"fdcId":2}]}'))), [{'fdcId': 1}, {'fdcId': 2}])
        with self.assertRaises(ValueError):
            list(stream_array(io.StringIO('{"BrandedFoods":[{"fdcId":1}')))
        with self.assertRaises(ValueError):
            list(stream_array(io.StringIO('{"unrelated":[]}')))
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            self.assertTrue(Path(temporary).resolve().is_relative_to(Path(__file__).resolve().parent))
            a, b = Path(temporary) / 'a.json.gz', Path(temporary) / 'b.json.gz'
            json_array(a, iter([{'a': 1}, {'b': None}]))
            json_array(b, iter([{'a': 1}, {'b': None}]))
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(json.loads(gzip.decompress(a.read_bytes())), [{'a': 1}, {'b': None}])

    def test_brand_counts_aggregate_markets_with_legacy_fallback(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temporary:
            directory = Path(temporary).resolve()
            self.assertTrue(directory.is_relative_to(Path(__file__).resolve().parent))
            legacy, markets = load_brand_counts(directory, {'brands': {'Brand A': 3, 'Brand B': 1}})
            self.assertEqual(dict(legacy), {'Brand A': 3, 'Brand B': 1})
            self.assertIsNone(markets)
            dump_json(directory / 'brands/US.json.gz', {'Brand A': 2, 'Brand B': 1}, compressed=True)
            dump_json(directory / 'brands/NZ.json.gz', {'Brand A': 1}, compressed=True)
            combined, markets = load_brand_counts(directory, {'brandCountsPrefix': 'brands', 'markets': {'US': 3, 'NZ': 1}})
            self.assertEqual(dict(combined), {'Brand A': 3, 'Brand B': 1})
            self.assertEqual(len(combined), 2)
            self.assertEqual(sum(markets['US'].values()), 3)


if __name__ == '__main__':
    unittest.main()
