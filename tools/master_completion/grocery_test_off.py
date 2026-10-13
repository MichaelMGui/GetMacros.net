"""OFF boundary tests use isolated fixtures, never public invented products."""
import gzip, json, sys, tempfile, unittest, io, contextlib
from unittest.mock import patch
from pathlib import Path
from grocery_import_off import normalize, barcode, source_serving, number, MAP, text, run, merge_quarantine, SOURCE_FIELDS, ROOT
import grocery_import_off as importer

def row(**changes):
    source={'code':'0068100084245','product_name':'Smooth Peanut Butter','brands':'Kraft','countries_tags':'en:canada','quantity':'1 kg','serving_size':'1 tbsp (15 g)','serving_quantity':'15','energy-kcal_100g':'600','proteins_100g':'20','carbohydrates_100g':'20','fat_100g':'50','sodium_100g':'0.3','last_modified_datetime':'2026-10-01T00:00:00Z','ingredients_text':'Peanuts'}
    source.update(changes);return source
class Boundaries(unittest.TestCase):
    def test_real_barcode_and_invalid_check_digit(self):
        self.assertEqual(barcode('0068100084245'),'00068100084245')
        self.assertIsNone(barcode('0068100084246'));self.assertIsNone(barcode('123'));self.assertIsNone(barcode('00000000'))
    def test_source_market_not_brand_origin(self):
        result,error=normalize(row());self.assertIsNone(error);self.assertEqual(result[0]['market'],'CA')
        self.assertEqual(normalize(row(countries_tags='en:france'))[1],'no-supported-source-market')
        self.assertEqual(normalize(row(countries_tags='en:united-states',brands='No fake familiar brand'))[1],'outside-published-brand-selection')
    def test_source_multimarket_kept_explicit(self):
        result,error=normalize(row(countries_tags='en:canada,en:united-states',brands='Kirkland Signature'))
        self.assertEqual({r['market'] for r in result},{'CA','US'});self.assertNotEqual(result[0]['formulation'],result[1]['formulation']);self.assertTrue(any('multiple markets' in flag for flag in result[0]['flags']))
    def test_missing_not_zero(self):
        result,error=normalize(row(proteins_100g='',fiber_100g='',fat_100g='0'));item=result[0]
        self.assertIsNone(item['nutrients']['p']);self.assertIsNone(item['nutrients']['f']);self.assertEqual(item['nutrients']['fat'],0);self.assertIsNone(item['sourceChecked'])
    def test_mass_serving(self):
        item=normalize(row())[0][0];self.assertEqual(item['basis'],{'amount':100,'unit':'g'});self.assertEqual(item['portions'][0]['grams'],15);self.assertEqual(item['nutrients']['cal'],600)
    def test_volume_not_grams(self):
        item=normalize(row(serving_size='250 ml',serving_quantity='250',**{'energy-kcal_100g':'40','fat_100g':'1','proteins_100g':'3','carbohydrates_100g':'5'}))[0][0]
        self.assertEqual(item['basis'],{'amount':1,'unit':'serving'});self.assertEqual(item['nutrients']['cal'],100);self.assertEqual(item['portions'],[]);self.assertEqual(item['sourcePer100']['unit'],'ml')
    def test_ambiguous_units_not_guessed(self):
        for label in ['1 cup','1 cup (250 ml / 250 g)','<15 g','15 g (30 g)','15 oz','1 tbsp (15 g)']:
            source=row(serving_size=label,serving_quantity='30' if label=='1 tbsp (15 g)' else '15');self.assertEqual(normalize(source)[1],'ambiguous-or-missing-serving-unit')
    def test_unit_conversions(self):
        item=normalize(row(calcium_100g='0.12',iron_100g='0.001',**{'vitamin-d_100g':'0.000001'}))[0][0]
        self.assertEqual(item['nutrients']['na'],300);self.assertEqual(item['nutrients']['calcium'],120);self.assertEqual(item['nutrients']['iron'],1);self.assertEqual(item['nutrients']['vitaminD'],1)
        self.assertIsNone(item['nutrients']['vitaminA']);self.assertIsNone(item['nutrients']['folateDFE']);self.assertIsNone(item['nutrients']['vitaminK'])
    def test_kilojoule_conversion_only_if_available(self):
        item=normalize(row(**{'energy-kcal_100g':'','energy-kj_100g':'418.4'}))[0][0];self.assertAlmostEqual(item['nutrients']['cal'],100);self.assertIn('cal',item['provenance'])
        item=normalize(row(**{'energy-kcal_100g':'','energy-kj_100g':''}))[0][0];self.assertIsNone(item['nutrients']['cal'])
    def test_bad_quality_and_density_excluded(self):
        for changes,reason in [({'data_quality_errors_tags':'en:nutrition-error'},'source-quality-errors'),({'energy-kcal_100g':'2000'},'implausible-source-density'),({'sugars_100g':'40'},'sugars-exceed-carbohydrate'),({'no_nutrition_data':'on'},'source-no-nutrition'),({'categories_tags':'en:food-supplements'},'excluded-supplement-or-infant-product')]:self.assertEqual(normalize(row(**changes))[1],reason)
    def test_product_package_and_formulation_distinct(self):
        items=[normalize(row(**changes))[0][0] for changes in [{},{'quantity':'2 kg'},{'product_name':'Crunchy Peanut Butter'},{'ingredients_text':'Peanuts, sugar'}]]
        self.assertEqual(len({r['formulation'] for r in items}),4)
    def test_status_and_license_are_honest(self):
        item=normalize(row())[0][0];self.assertEqual(item['status'],'community-label-imported');self.assertEqual(item['license'],'ODbL-1.0');self.assertEqual(item['contentsLicense'],'DbCL-1.0');self.assertIn('Open Food Facts',item['attribution']);self.assertNotIn('image',item);self.assertIsNone(item['sourceChecked']);self.assertIsNone(item['labelDate'])
    def test_zero_energy_ambiguities_quarantined_without_invented_calories(self):
        self.assertEqual(normalize(row(**{'energy-kcal_100g':'0'}))[1],'zero-energy-positive-macros-pending-label-or-rounding-review')
        result,error=normalize(row(**{'energy-kcal_100g':'0','proteins_100g':'0','carbohydrates_100g':'0','fat_100g':'0'}));self.assertIsNone(error);self.assertEqual(result[0]['nutrients']['cal'],0)
    def test_subset_reprocessing_preserves_quarantine_idempotently(self):
        parent=ROOT/'docs/master-completion-2026-10-13'
        existing=json.loads((ROOT/'data/branded-foods/off/quarantined.json').read_text(encoding='utf-8'))['records'][:1]
        self.assertEqual(len(existing),1)
        with tempfile.TemporaryDirectory(prefix='grocery-ledger-fixture-',dir=parent) as directory:
            work=Path(directory).resolve();self.assertTrue(work.is_relative_to(parent.resolve()));output=work/'partition';output.mkdir()
            source=work/'eligible.ndjson.gz';report=work/'report.json'
            payload={key:row().get(key,'') for key in SOURCE_FIELDS}
            with gzip.open(source,'wt',encoding='utf-8') as file:file.write(json.dumps(payload)+'\n')
            (output/'manifest.json').write_text(json.dumps({'source':{'retrievedAt':'2026-10-13','sha256':'original-bulk-provenance'}}),encoding='utf-8')
            (output/'quarantined.json').write_text(json.dumps({'records':existing}),encoding='utf-8')
            report.write_text(json.dumps({'sourceRowsRead':99,'skipped':{'zero-energy-positive-macros-pending-label-or-rounding-review':1}}),encoding='utf-8')
            states=[]
            with patch.object(importer,'REPORT',report),contextlib.redirect_stdout(io.StringIO()):
                for ignored in range(2):
                    run(source,output,subset=True)
                    ledger=json.loads((output/'quarantined.json').read_text(encoding='utf-8'))['records']
                    manifest=json.loads((output/'manifest.json').read_text(encoding='utf-8'))
                    status=json.loads(report.read_text(encoding='utf-8'))
                    self.assertEqual(ledger,existing);self.assertEqual(status['quarantinedSourceProducts'],1)
                    self.assertEqual(status['skipped']['zero-energy-positive-macros-pending-label-or-rounding-review'],1)
                    self.assertEqual(manifest['source']['sha256'],'original-bulk-provenance')
                    self.assertEqual(status['sourceRowsRead'],99)
                    record_files=[file.read_bytes() for file in sorted((output/'records').glob('*.json'))]
                    states.append((manifest['version'],status['publishedMarketRecords'],record_files))
            self.assertEqual(states[0],states[1])
        self.assertEqual(merge_quarantine(existing,existing),existing)
        with self.assertRaisesRegex(ValueError,'product code'):merge_quarantine([{}],[])
    def test_failed_import_preserves_existing_partition(self):
        parent=ROOT/'docs/master-completion-2026-10-13'
        with tempfile.TemporaryDirectory(prefix='grocery-failure-',dir=parent) as directory:
            work=Path(directory).resolve();self.assertTrue(work.is_relative_to(parent.resolve()));output=work/'partition';output.mkdir();sentinel=output/'manifest.json';sentinel.write_text('{\"unchanged\":true}',encoding='utf-8')
            source=work/'empty.tsv.gz'
            with gzip.open(source,'wt',encoding='utf-8') as file:file.write('\t'.join(SOURCE_FIELDS)+'\n')
            with self.assertRaisesRegex(ValueError,'No source records'):run(source,output)
            self.assertEqual(sentinel.read_text(encoding='utf-8'),'{\"unchanged\":true}')
            with gzip.open(source,'wt',encoding='utf-8') as file:file.write('unexpected_schema\n')
            with self.assertRaisesRegex(ValueError,'schema changed'):run(source,output)
            self.assertEqual(sentinel.read_text(encoding='utf-8'),'{\"unchanged\":true}')
    def test_unicode_product_identity_and_search(self):
        self.assertEqual(text('Café 明治 ヨーグルト'),'cafe 明治 ヨークルト')
        a=normalize(row(product_name='明治チョコレート'))[0][0];b=normalize(row(product_name='明治ヨーグルト'))[0][0];self.assertNotEqual(a['formulation'],b['formulation'])
    def test_actual_current_api_contract(self):
        file=Path(__file__).resolve().parents[2]/'docs/master-completion-2026-10-13/grocery-sources/probe-0.json'
        if not file.exists():self.skipTest('Private live-source evidence not in CI; isolated fixtures tested above')
        products=json.loads(json.loads(file.read_text(encoding='utf-8'))['body'])['products'];counts=0
        for product in products:
            source={key:product.get(key,'') for key in ['code','product_name','brands','quantity','serving_size','serving_quantity','ingredients_text']};source['countries_tags']=','.join(product.get('countries_tags',[]));source.update(product.get('nutriments',{}))
            items,error=normalize(source)
            if items:counts+=len(items);self.assertTrue(all(item['market'] in item['markets'] for item in items))
        self.assertGreater(counts,15)
if __name__=='__main__':unittest.main()
