"""Source adapter, nutrient provenance and real finder behavior regression tests."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import build_restaurant_expansion as expansion
from build_meal_finder import parse_meals
from meal_provenance import pack, read
from sync_restaurant_release import validate_menu, validate_expansion_comparison
from normalize_calculator_layouts import Document
from restaurant_identity import MARKS, mark
from build_meal_finder import write_tags
import sync_restaurant_release
import build_restaurant_data_report as data_report

class Expansion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = expansion.payload()
        cls.rows = cls.p['records']

    def test_validates_curated_source_records(self):
        result = expansion.validate()
        self.assertEqual(result['newOrders'],380)
        self.assertEqual(result['newChains'],10)
        self.assertEqual(result['calculatedOrders'],2)

    def test_private_source_snapshots_are_optional_but_never_ignored_when_available(self):
        real_exists = Path.exists
        def absent(path):
            return False if path.parent == expansion.DATA/'sources' else real_exists(path)
        with patch.object(Path, 'exists', absent):
            result = expansion.validate()
            self.assertEqual(len(result['sourceSnapshotsUnavailable']),9)
            self.assertEqual(result['sourceSnapshotsVerified'],[])
            with self.assertRaisesRegex(ValueError,'Private research snapshot unavailable'):
                expansion.validate(require_source_snapshots=True)
        real_read = Path.read_bytes
        def corrupt(path):
            return b'%PDF corrupted' if path.parent == expansion.DATA/'sources' else real_read(path)
        with patch.object(Path,'read_bytes',corrupt), patch.object(Path,'exists',lambda path: True):
            with self.assertRaisesRegex(ValueError,'Source snapshot changed'):
                expansion.validate()

    def test_append_is_idempotent_and_preserves_existing_rows(self):
        src = "window.GM_MEALS = [\n{chain:'Existing chain',name:'Existing order',cal:400,p:20,c:40,f:4,na:500,t:[],diet:[],meal:'main',url:'existing.html',why:'Unrelated text'}\n];\n"
        one = expansion.append_meals(src)
        two = expansion.append_meals(one)
        self.assertEqual(one,two)
        meals = parse_meals(one)
        self.assertEqual(len(meals),381)
        self.assertEqual(meals[0],parse_meals(src)[0])
        self.assertTrue(all(m['meal'] in ('main','breakfast') for m in meals))

    def test_mixed_quoted_names_survive_generated_single_quoted_tags(self):
        meal={'chain':"Quoted chain",'name':"Chef's bowl with \"house\" rice",'cal':540,'p':35,'c':60,'f':7,'na':800,'t':[],'diet':[],'meal':'main','url':'example.html','why':"One chef's portion."}
        src='window.GM_MEALS = [\n'+expansion.serialize(meal)+'\n];\n'
        tagged=write_tags(src,parse_meals(src))
        self.assertIn("t:['protein'",tagged)
        parsed=parse_meals(tagged)
        self.assertEqual(parsed[0]['name'],meal['name'])
        self.assertEqual(parsed[0]['why'],meal['why'])
        self.assertEqual(expansion.append_meals(tagged),expansion.append_meals(expansion.append_meals(tagged)))

    def test_review_merge_preserves_unrelated_facts(self):
        unrelated = {'chain':'Unrelated','name':'Known order','source':'Original','values':{'f':None}}
        merged = expansion.merge_review([unrelated])
        self.assertEqual(merged[0],unrelated)
        self.assertEqual(merged,expansion.merge_review(merged))
        self.assertEqual(len(merged),381)

    def test_packed_provenance_round_trip_preserves_bounds_and_fat(self):
        original = expansion.metadata_overrides()
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/'metadata.js'
            file.write_text(pack(original),encoding='utf-8')
            self.assertEqual(original,read(file))
        self.assertTrue(any(v['fat'] is not None for v in original.values()))
        for r in self.rows:
            for nutrient,info in r['provenance']['nutrientProvenance'].items():
                if info.get('publishedBound'):
                    self.assertIsNone(r['values'][nutrient])

    def test_individual_canes_sum_is_not_a_published_combo(self):
        rows = [r for r in self.rows if r['sourceId']=='raising-canes' and r['provenance']['components']]
        self.assertEqual(sorted(r['values']['cal'] for r in rows),[630,1150])
        for r in rows:
            self.assertIsNone(r['values']['f'])
            self.assertNotIn('Combo',r['meal']['name'])
            self.assertEqual(r['provenance']['nutrientProvenance']['cal']['method'],'calculated')

    def test_dressing_and_culvers_dinner_limits_are_retained(self):
        salads = [r for r in self.rows if r['sourceId']=='el-pollo-loco' and '*' in r['sourceRow'] and ('Salad' in r['meal']['name'] or 'Tostada' in r['meal']['name'])]
        self.assertTrue(salads)
        for r in salads:
            self.assertIn('dressing excluded',r['provenance']['serving'])
            self.assertNotIn('*',r['meal']['name'])
        dinner = next(r for r in self.rows if r['sourceId']=='culvers' and 'Dinner' in r['meal']['name'])
        self.assertIn('protein, lemon wedge, dinner roll and butter only',dinner['provenance']['serving'])
        self.assertEqual(dinner['provenance']['sourceDate'],'2025-07')

    def test_impossible_source_rows_are_absent(self):
        self.assertFalse(any('Quesabirria' in r['meal']['name'] for r in self.rows if r['sourceId']=='qdoba'))
        self.assertFalse(any('Fiesta Rice Bowl, Beef'==r['meal']['name'] for r in self.rows if r['sourceId']=='taco-johns'))
        self.assertEqual({c['id'] for c in self.p['chains']},{'arbys','sonic','qdoba','el-pollo-loco','del-taco','noodles','culvers','taco-johns','in-n-out','raising-canes'})

    def test_existing_finder_handles_new_data_and_share_state(self):
        # Executes the actual production engine, not a test-only copy.
        script = r"""
const assert=require('node:assert/strict');
const engine=require('./js/meal-engine.js');
const payload=require('./tools/restaurant_release/expansion-payload.json');
const rows=payload.records.map(r=>({...r.meal,fat:r.values.fat,market:'US',country:'US'}));
for(const c of payload.chains){
 const state=engine.fromSearch('?chain='+encodeURIComponent(c.chain)+'&complete=0',rows);
 assert.equal(engine.results(rows,state).length,c.records);
 assert.deepEqual(engine.fromSearch('?'+engine.toSearch(state),rows),state);
}
const limited=engine.fromSearch('?chain='+encodeURIComponent('In-N-Out')+'&maxCal=400&minProtein=15',rows);
const results=engine.results(rows,limited);
assert.deepEqual(results.map(r=>r.name).sort(),['Cheeseburger with onion, Protein Style (lettuce instead of bun)','Cheeseburger with onion, mustard and ketchup instead of spread','Hamburger with onion','Hamburger with onion, mustard and ketchup instead of spread'].sort());
const unknown=rows.find(m=>m.chain==='Raising Cane’s'&&m.f===null);
assert.ok(unknown);
assert.equal(engine.eligible(unknown,engine.normalize({complete:false,minFiber:1},rows)),false);
assert.equal(engine.eligible(unknown,engine.normalize({complete:true},rows)),engine.complete(unknown));
assert.equal(engine.eligible({...unknown,fat:null},engine.normalize({complete:true},rows)),false);
assert.equal(engine.eligible(unknown,engine.normalize({complete:false},rows)),true);
assert.equal(engine.results(rows,engine.normalize({meal:['breakfast'],complete:false},rows)).every(m=>m.meal==='breakfast'),true);
console.log('Production engine: all10 chains, numeric filters, unknown nutrients, breakfast and share-state round trips passed.');
"""
        result = subprocess.run(['node','-e',script],cwd=ROOT,text=True,capture_output=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_new_guide_metadata_and_serving_rows(self):
        for chain in self.p['chains']:
            text=(expansion.DATA/'pages'/chain['route']).read_text(encoding='utf-8')
            self.assertEqual(text.count('<main '),1)
            self.assertEqual(text.count('<h1>'),1)
            self.assertIn('https://getmacros.net/'+chain['route'],text)
            self.assertIn(str(chain['records'])+' recorded orders · U.S.',text)
            self.assertIn('calculated',text) if chain['id']=='raising-canes' else None
            self.assertNotIn('dateModified',text)
            self.assertNotIn('Chipotle nutrition',text)

    def test_new_guides_match_central_rows_without_legacy_pairs(self):
        for chain in self.p['chains']:
            text=(expansion.DATA/'pages'/chain['route']).read_text(encoding='utf-8')
            rows=[r for r in self.rows if r['sourceId']==chain['id']]
            entries=[r['meal'] for r in rows]
            provenance=expansion.metadata_overrides()
            validate_menu(text,entries,provenance,efficiency=False)
            doc=Document(text)
            pairs=validate_expansion_comparison(text,entries,provenance,doc,doc.find(id='menu-comparison'))
            self.assertEqual(len(pairs),2)
        # A stale rendered number must fail instead of being silently accepted.
        text=(expansion.DATA/'pages'/'in-n-out-nutrition-guide.html').read_text(encoding='utf-8')
        stale=text.replace('<td>360</td>','<td>0</td>')
        with self.assertRaises(AssertionError):
            validate_menu(stale,[r['meal'] for r in self.rows if r['sourceId']=='in-n-out'],expansion.metadata_overrides(),efficiency=False)

    def test_every_new_chain_has_an_original_food_symbol(self):
        for chain in self.p['chains']:
            self.assertIn(chain['chain'],MARKS)
            symbol=mark(chain['chain'])
            self.assertIn('aria-hidden="true"',symbol)
            self.assertIn('currentColor',symbol)
            self.assertNotIn('<img',symbol)

    def test_full_sync_keeps_new_compositions_without_old_comparison_id(self):
        source=expansion.append_meals((ROOT/'js/meal-data.js').read_text(encoding='utf-8'))
        meals=parse_meals(source)
        provenance=read(ROOT/'js/meal-provenance.js')
        provenance.update(expansion.metadata_overrides())
        with tempfile.TemporaryDirectory() as d:
            fixture=Path(d)
            (fixture/'js').mkdir()
            (fixture/'tools/restaurant_release').mkdir(parents=True)
            (fixture/'docs/release-2026-10-03').mkdir(parents=True)
            (fixture/'js/meal-data.js').write_text(source,encoding='utf-8')
            (fixture/'js/meal-provenance.js').write_text(pack(provenance),encoding='utf-8')
            (fixture/'tools/restaurant_release/expansion-payload.json').write_text(json.dumps(self.p),encoding='utf-8')
            new_routes={c['route'] for c in self.p['chains']}
            before={}
            for route in {m['url'] for m in meals}:
                source_path=expansion.DATA/'pages'/route if route in new_routes else ROOT/route
                text=source_path.read_text(encoding='utf-8')
                (fixture/route).write_text(text,encoding='utf-8')
                if route in new_routes:
                    self.assertNotIn('id="ordering-comparison"',text)
                    before[route]=text
            with patch.object(sync_restaurant_release,'ROOT',fixture):
                sync_restaurant_release.run()
            for route,text in before.items():
                self.assertEqual((fixture/route).read_text(encoding='utf-8'),text)
            report=json.loads((fixture/'docs/release-2026-10-03/data-restaurant-sync.json').read_text(encoding='utf-8'))
            self.assertEqual(report['restaurantCount'],25)
            self.assertEqual(report['orderCount'],463)

    def test_data_report_counts_exact_unknowns_from_provenance(self):
        records=data_report.load(preview=True)
        stats=data_report.statistics_for(records)
        self.assertEqual(stats['records'],463)
        self.assertEqual(stats['chains'],25)
        self.assertEqual(stats['ranges']['f']['unknown'],sum(r['values']['f'] is None for r in records))
        self.assertEqual(stats['ranges']['fat']['unknown'],sum(r['proof'].get('fat') is None for r in records))
        self.assertEqual(sum(r['records'] for r in stats['coverage']),463)
        for k in data_report.FIELDS:
            known=[r['values'][k] for r in records if r['values'][k] is not None]
            self.assertEqual(stats['ranges'][k]['min'],min(known))
            self.assertEqual(stats['ranges'][k]['max'],max(known))
        text=data_report.page(records,stats)
        self.assertIn('unknown values are not zero',text)
        self.assertIn('463 recorded orders across 25 U.S.',text)

if __name__=='__main__':
    unittest.main(verbosity=2)
