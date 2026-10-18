"""Lossless browser payload regressions; no source data is altered."""
from pathlib import Path
import json, subprocess, sys, unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_global_coverage_release import finder_script, finder_record, eligible

class FinderPayloadTests(unittest.TestCase):
    def verify(self,rows):
        script=finder_script(rows)
        check="const fs=require('fs'),vm=require('vm'),assert=require('assert/strict'),x=JSON.parse(fs.readFileSync(0,'utf8')),c={window:{}};vm.runInNewContext(x.script,c);assert.deepEqual(JSON.parse(JSON.stringify(c.window.GM_MEALS)),x.expected);"
        result=subprocess.run(['node','-e',check],input=json.dumps(dict(script=script,expected=[finder_record(r) for r in rows])),capture_output=True,encoding='utf-8',cwd=ROOT)
        self.assertEqual(result.returncode,0,result.stderr)
        return script
    def test_null_zero_absent_and_nested_values(self):
        self.verify([dict(id='a',name='Same named source serving',cal=0,p=None,nutrientBounds={'cal':{'max':0}},notes=['Shared source description']),dict(id='b',name='Same named source serving',cal=2.5,notes=['Shared source description'])])
        self.verify([])
    def test_every_market_is_exact_and_within_budget(self):
        rows=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
        for market in sorted({r['market'] for r in rows}):
            with self.subTest(market=market):
                local=[r for r in rows if r['market']==market and eligible(r)]
                for row in local:
                    self.assertEqual(finder_record(row).get('url'),row.get('url'))
                    self.assertTrue(row.get('url'),'A visible meal detail needs a real guide destination')
                    self.assertEqual(finder_record(row).get('components'),row.get('components'))
                packed=self.verify(local).encode()
                plain=json.dumps([finder_record(r) for r in local],ensure_ascii=False,separators=(',',':')).encode()
                self.assertLess(len(packed),len(plain)*.65)
                self.assertLess(len(packed),1_500_000)
if __name__=='__main__':unittest.main()
