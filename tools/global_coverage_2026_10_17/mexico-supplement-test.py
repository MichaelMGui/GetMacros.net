"""Source tests: ambiguous Mexico CMS data must remain outside accepted records."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
PATH = Path(__file__).with_name('mexico-supplement-report.py')
SPEC = importlib.util.spec_from_file_location('mexico_supplement_report', PATH)
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


class MexicoSourceExclusions(unittest.TestCase):
    def test_no_ambiguous_records_accepted(self):
        batch = json.loads(PATH.with_name('mexico-supplement-records.json').read_text(encoding='utf-8'))
        self.assertEqual(batch['records'], [])
        self.assertEqual(batch['updates'], [])
        self.assertEqual(batch['marketCounts'], {})
        withheld = REPORT.read('withheld.json')
        self.assertEqual(len(withheld), 78)
        self.assertTrue(all(not row['accepted'] and row['reasons'] for row in withheld))

    def test_source_payload_hashes(self):
        for source in REPORT.read('retrieval.json'):
            if source.get('sha256') and source.get('retained', True):
                with self.subTest(file=source['file']):
                    data = (REPORT.DEST / source['file']).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(), source['sha256'])
                    self.assertEqual(len(data), source['bytes'])

    def test_local_fries_portion_conflicts(self):
        rows = [row for row in REPORT.read('withheld.json') if row['name'].get('es') == 'Papas Grandes']
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row['productSize'], '176 Gramos')
            self.assertEqual(row['nativeNutrients']['weight'], 159)
            self.assertTrue(any('Conflicting source portion' in reason for reason in row['reasons']))

    def test_soda_zero_macros_are_not_repaired(self):
        rows = [row for row in REPORT.read('withheld.json')
                if row['name'].get('es', '').startswith('Manzanita Sol')]
        self.assertEqual({row['nativeNutrients']['calories'] for row in rows}, {150, 350})
        for row in rows:
            self.assertEqual([row['nativeNutrients'][key] for key in
                              ('proteins', 'carbohydrates', 'fat')], [0, 0, 0])
            self.assertTrue(any('energy/macronutrient discrepancy' in reason for reason in row['reasons']))

    def test_template_and_test_objects_not_menu_proof(self):
        summary = REPORT.read('summary.json')['publicDataset']
        self.assertEqual(summary['nutritionItems'], 418)
        self.assertEqual(summary['withoutSpanishName'], 59)
        self.assertEqual(summary['explicitTestName'], 6)
        self.assertTrue(any(name.get('en') == 'Antarctica Menu' for name in summary['menuNames']))

    def test_mcdonalds_access_limits_retained(self):
        attempts = [row for row in REPORT.read('retrieval.json') if row['file'].startswith('mcd-')]
        self.assertEqual(len(attempts), 6)
        self.assertTrue(all('403' in row['error'] for row in attempts))

    def test_existing_mexico_rows_unchanged(self):
        current = REPORT.mexico_baseline()
        # The prior accepted Subway snapshot remains byte-equivalent in this
        # factual projection. A separately reviewed Starbucks release may add
        # local calorie-only sizes; it is not part of the excluded BK CMS batch.
        baseline = [row for row in current if row['chain'] == 'Subway']
        newer_path = REPORT.ROOT / 'tools/flagship_release/markets_mexico_calories.json'
        newer = json.loads(newer_path.read_text(encoding='utf-8'))['records'] if newer_path.exists() else []
        self.assertEqual({row['id'] for row in current if row['chain'] != 'Subway'}, {row['id'] for row in newer})
        expected = REPORT.read('summary.json')['mexicoBaseline']
        self.assertEqual(len(baseline), 100)
        self.assertEqual({row['chain'] for row in baseline}, {'Subway'})
        self.assertEqual(REPORT.digest(baseline), expected['identityNutritionSourceSha256'])


if __name__ == '__main__':
    unittest.main()
