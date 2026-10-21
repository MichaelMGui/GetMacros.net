"""Regression checks for useful local landing pages and honest source portions."""
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from search_recovery.build import ROOT, individual_examples, markets, eligible, html_path


class RecoveryTests(unittest.TestCase):
    def test_editorial_selection_excludes_bulk_and_unknowns(self):
        base={'market':'GB','chain':'Example','category':'entree','name':'Chicken wrap','cal':400,'p':30,'c':40,'fat':15,'serving':'one wrap'}
        candidates=[base,dict(base,name='Pizza Box 6 Pack'),dict(base,name='Sharing platter'),dict(base,name='Unknown protein',p=None),dict(base,name='Tiny side',category='side'),dict(base,name='Large item',cal=1200),dict(base,name='Oversized portion',servingGrams=1200)]
        self.assertEqual(individual_examples(candidates),[base])
        self.assertIsNone(candidates[3]['p'])

    def test_brands_have_space_before_repeat_items(self):
        rows=[dict(market='CA',chain=chain,category='entree',name=str(i),cal=300+i,p=30,c=30,fat=10) for chain in ['A','B','C'] for i in range(6)]
        selected=individual_examples(rows,4)
        self.assertEqual([r['chain'] for r in selected],['A','B','C','A'])

    def test_current_market_counts_and_crawlable_local_guides(self):
        registry=json.loads((ROOT/'js/order-registry.json').read_text(encoding='utf-8'))['records']
        sitemap={n.text for n in ET.parse(ROOT/'sitemap.xml').findall('.//{*}loc')}
        for code,info in markets().items():
            rows=[r for r in registry if r['market']==code and eligible(r)]
            s=(ROOT/html_path(info['finder'])).read_text(encoding='utf-8')
            self.assertTrue(f'{len(rows):,} source-defined menu portions' in s,code+' current count missing')
            self.assertEqual(s.count('id="local-menu-heading"'),1)
            self.assertIn('href="'+info['collection']+'"',s)
            self.assertIn('href="https://getmacros.net'+info['finder']+'"',s)
            self.assertIn('https://getmacros.net'+info['finder'],sitemap)
            self.assertNotIn('content="noindex',s)
            for r in rows:
                if r.get('url'):self.assertTrue('href="/'+r['url'].lstrip('/')+'"' in s,code+' guide link missing: '+r['url'])
            if code!='US':
                collection=(ROOT/html_path(info['collection'])).read_text(encoding='utf-8')
                self.assertIn('250–900 calories',collection)
                self.assertIn('not a personal target',collection) if individual_examples(rows) else None
                self.assertNotIn('Pizza Box 6 Pack',collection)
                for row in individual_examples(rows):
                    self.assertEqual(row['market'],code)
                    self.assertIn(row['source'].replace('&','&amp;'),collection)
                for region,other in markets().items():
                    if region!='US':self.assertIn('hreflang="en-'+region+'" href="https://getmacros.net'+other['collection']+'"',collection)

    def test_us_metadata_follows_current_catalog(self):
        s=(ROOT/'healthy-fast-food.html').read_text(encoding='utf-8')
        self.assertNotIn('Compare 83 U.S.',s)
        self.assertTrue('Compare 463 recorded orders' not in s,'Obsolete U.S. count')
        self.assertEqual(s.count('id="fast-food-choice"'),1)
        self.assertIn('A listed main is not a complete meal', (ROOT/'ca/en/find-a-meal/index.html').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()
