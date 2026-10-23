"""Every generated route must retain its privacy boundary and consent controls."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analytics_measurement.build import ROOT, pages, scope, privacy
from normalize_calculator_layouts import Document


class AnalyticsBuild(unittest.TestCase):
    def test_all_routes_and_private_boundaries(self):
        for path in pages():
            text=path.read_text(encoding='utf-8');name=path.relative_to(ROOT).as_posix()
            self.assertEqual(text.count('data-source-path="js/analytics.js"')+text.count('src="/js/analytics.js"'),1,name)
            self.assertEqual(text.count('id="analytics-preferences"'),1,name)
            self.assertEqual(text.count('data-analytics-footer'),1,name)
            self.assertIn('data-analytics-page="'+scope(text,name)+'"',text,name)
            self.assertNotIn('src="https://www.googletagmanager.com',text,name)
        for name in ['food-diary.html','food-library.html','food-shelf.html','search.html','calculators.html','protein-value-calculator.html','compare-foods.html','budget-meal-builder.html','contact.html','offline.html','ca/en/find-meals/index.html']:
            path=ROOT/name
            if path.exists(): self.assertIn('data-analytics-page="private"',path.read_text(encoding='utf-8'),name)

    def test_csp_and_privacy(self):
        for name,expected in [('index.html',True),('articles.html',True),('food-diary.html',False),('calculators.html',False)]:
            nodes=Document((ROOT/name).read_text(encoding='utf-8')).nodes
            policy=next(n['attrs']['content'] for n in nodes if n['tag']=='meta' and n['attrs'].get('http-equiv','').lower()=='content-security-policy')
            self.assertEqual('https://www.googletagmanager.com' in policy,expected,name)
            self.assertIn("default-src 'self'",policy)
            self.assertIn("object-src 'none'",policy)
        text=(ROOT/'privacy.html').read_text(encoding='utf-8')
        self.assertIn('after you choose Allow analytics',text)
        self.assertNotIn('does not load Google Analytics 4',text)
        self.assertEqual(privacy(text),text)

    def test_all_build_entry_points(self):
        for name in ['tools/build_site.sh','tools/run_food_build.py','tools/product_release/test-generators.py']:
            text=(ROOT/name).read_text(encoding='utf-8')
            self.assertEqual(text.count('analytics_measurement/build'),1,name)

if __name__=='__main__':unittest.main(verbosity=2)
