"""Boundary tests contain private fixtures, never public invented products."""
import gzip
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import off_expand as off


def row(**changes):
    value = {'code': '0068100084245', 'product_name': 'Smooth Peanut Butter', 'brands': 'Kraft',
             'countries_tags': 'en:canada', 'quantity': '1 kg', 'serving_size': '1 tbsp (15 g)',
             'serving_quantity': '15', 'energy-kcal_100g': '600', 'proteins_100g': '20',
             'carbohydrates_100g': '20', 'fat_100g': '50', 'sodium_100g': '0.3',
             'last_modified_datetime': '2026-10-01T00:00:00Z', 'ingredients_text': 'Peanuts'}
    value.update(changes)
    return value


class ExpansionBoundaries(unittest.TestCase):
    def test_any_real_source_brand_is_eligible(self):
        source = row(brands='Private test brand', countries_tags='en:ireland')
        records, reason = off.normalize(source)
        self.assertIsNone(reason)
        self.assertEqual(records[0]['brand'], source['brands'])
        self.assertEqual(records[0]['market'], 'IE')
        self.assertEqual(off.previous.normalize(source)[1], 'outside-published-brand-selection')

    def test_existing_ids_and_formulation_are_preserved(self):
        source = row(countries_tags='en:canada,en:united-states')
        prior, _ = off.previous.normalize(source)
        current, _ = off.normalize(source)
        self.assertEqual([(r['id'], r['formulation']) for r in prior], [(r['id'], r['formulation']) for r in current])

    def test_missing_stays_null_zero_is_retained(self):
        item = off.normalize(row(proteins_100g='', fiber_100g='', fat_100g='0'))[0][0]
        self.assertIsNone(item['nutrients']['p'])
        self.assertIsNone(item['nutrients']['f'])
        self.assertEqual(item['nutrients']['fat'], 0)
        self.assertIsNone(item['sourceChecked'])
        self.assertIsNone(item['labelDate'])

    def test_volume_never_becomes_grams(self):
        item = off.normalize(row(serving_size='250 ml', serving_quantity='250', **{'energy-kcal_100g': '40', 'fat_100g': '1', 'proteins_100g': '3', 'carbohydrates_100g': '5'}))[0][0]
        self.assertEqual(item['basis'], {'amount': 1, 'unit': 'serving'})
        self.assertEqual(item['nutrients']['cal'], 100)
        self.assertEqual(item['sourcePer100']['unit'], 'ml')
        self.assertEqual(item['portions'], [])
        self.assertFalse(any('grams' in portion for portion in item['portions']))

    def test_missing_ambiguous_or_mismatched_units_are_not_guessed(self):
        for serving in ['', '1 cup', '15 oz', '250 ml / 250 g', '>15 g', '15 g (30 g)']:
            with self.subTest(serving=serving):
                self.assertEqual(off.normalize(row(serving_size=serving))[1], 'ambiguous-or-missing-serving-unit')
        # Package weight is no evidence of the nutrition-table basis.
        self.assertEqual(off.normalize(row(serving_size='', quantity='100 g'))[1], 'ambiguous-or-missing-serving-unit')

    def test_invalid_barcode_and_nonfinite_values(self):
        self.assertIsNone(off.barcode('0068100084246'))
        self.assertIsNone(off.barcode('00000000'))
        self.assertIsNone(off.number('NaN'))
        self.assertIsNone(off.number('Infinity'))
        self.assertIsNone(off.number('-1'))

    def test_formulations_flavours_packages_and_markets_stay_distinct(self):
        records = [off.normalize(row(**changes))[0][0] for changes in [{}, {'quantity': '2 kg'}, {'product_name': 'Crunchy Peanut Butter'}, {'ingredients_text': 'Peanuts, sugar'}, {'countries_tags': 'en:mexico'}]]
        self.assertEqual(len({r['formulation'] for r in records}), 5)
        self.assertNotEqual(records[0]['id'], records[-1]['id'])

    def test_mg_microgram_and_kilojoule_conversions(self):
        item = off.normalize(row(calcium_100g='0.12', iron_100g='0.001', **{'vitamin-d_100g': '0.000001', 'energy-kcal_100g': '', 'energy-kj_100g': '418.4'}))[0][0]
        for key, expected in [('na', 300), ('calcium', 120), ('iron', 1), ('vitaminD', 1), ('cal', 100)]:
            self.assertAlmostEqual(item['nutrients'][key], expected)
        for key in ['vitaminA', 'folateDFE', 'vitaminK']:
            self.assertIsNone(item['nutrients'][key])
        self.assertEqual(item['provenance']['cal']['sourceField'], 'energy-kj_100g')

    def test_carbohydrates_are_never_fiber_adjusted(self):
        item = off.normalize(row(fiber_100g='8'))[0][0]
        self.assertEqual(item['nutrients']['c'], 20)
        self.assertIn('not established', item['carbohydrateDefinition'])

    def test_quality_quarantine_and_density_checks(self):
        for changes, reason in [({'data_quality_errors_tags': 'en:nutrition-error'}, 'source-quality-errors'), ({'energy-kcal_100g': '2000'}, 'implausible-source-density'), ({'energy-kcal_100g': '0'}, 'zero-energy-positive-macros-pending-label-or-rounding-review'), ({'no_nutrition_data': 'on'}, 'source-no-nutrition'), ({'categories_tags': 'en:infant-formula'}, 'excluded-supplement-or-infant-product')]:
            self.assertEqual(off.normalize(row(**changes))[1], reason)

    def test_country_is_reported_never_inferred_from_brand(self):
        self.assertEqual(off.normalize(row(countries_tags='en:france'))[1], 'no-supported-source-market')
        items = off.normalize(row(countries_tags='en:canada,en:united-states'))[0]
        self.assertEqual({r['market'] for r in items}, {'CA', 'US'})
        self.assertTrue(all(r['markets'] == ['CA', 'US'] for r in items))

    def test_source_version_status_and_rights_are_honest(self):
        item = off.normalize(row())[0][0]
        self.assertEqual(item['retrievedAt'], '2026-10-13')
        self.assertEqual(item['status'], 'community-label-imported')
        self.assertEqual(item['license'], 'ODbL-1.0')
        self.assertEqual(item['contentsLicense'], 'DbCL-1.0')
        self.assertNotIn('image', item)
        self.assertIn('Open Food Facts', item['attribution'])
        self.assertIn('source-records.ndjson.gz', item['redistributionUrl'])

    def test_deterministic_gzip_does_not_embed_path_or_clock(self):
        with tempfile.TemporaryDirectory(prefix='off-gzip-fixture-', dir=off.OUT) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(off.OUT.resolve()))
            first = Path(directory) / 'first.json.gz'
            second = Path(directory) / 'second.json.gz'
            off.json_gzip(first, [{'name': 'Café 明治'}])
            off.json_gzip(second, [{'name': 'Café 明治'}])
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(json.loads(gzip.decompress(first.read_bytes())), [{'name': 'Café 明治'}])

    def test_downloaded_normalizer_is_standalone(self):
        with tempfile.TemporaryDirectory(prefix='off-standalone-fixture-', dir=off.OUT) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(off.OUT.resolve()))
            normalizer = Path(directory) / 'normalization.py'
            normalizer.write_text(off.standalone_normalizer(), encoding='utf-8')
            source = Path(directory) / 'source.ndjson.gz'
            with gzip.open(source, 'wt', encoding='utf-8') as handle:
                handle.write(json.dumps(row()) + '\n')
            run = subprocess.run([sys.executable, '-X', 'utf8', str(normalizer), str(source)], cwd=directory, capture_output=True, text=True, encoding='utf-8', check=True)
            item = json.loads(run.stdout)
            self.assertEqual(item, off.normalize(row())[0][0])


if __name__ == '__main__':
    unittest.main()
