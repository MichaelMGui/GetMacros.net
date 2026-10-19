"""Source and worked-example regression gate for the authored restaurant guides."""
from pathlib import Path
from decimal import Decimal
from urllib.parse import urlsplit, parse_qs
from html import unescape
import hashlib
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from ultimate_release import editorial_restaurants as content


class EditorialRestaurants(unittest.TestCase):
    def test_fifteen_distinct_complete_articles(self):
        rows = content.articles()
        self.assertEqual(len(rows), 15)
        self.assertEqual(len({a['slug'] for a in rows}), 15)
        self.assertEqual(len({a['question'] for a in rows}), 15)
        for article in rows:
            self.assertTrue(article['answer'])
            self.assertGreaterEqual(len(re.findall('<h2>', article['body_html'])), 4)
            self.assertIn('<table>', article['body_html'])
            self.assertIn('<svg', article['body_html'])
            self.assertTrue(article['sources'])
            self.assertTrue(article['related'])
            self.assertTrue(article['overlap_review']['distinct_value'])
            self.assertIsNone(article['search_observations'][0]['measured_volume'])
            self.assertNotIn('published-and-live', article['review']['status'])
            self.assertEqual({content.USED[key]['market'] for key in article['source_record_ids']}, {article['country']})

    def test_frozen_values_and_provenance_match_registry(self):
        registry = json.loads((ROOT / 'js/order-registry.json').read_text(encoding='utf-8'))['records']
        current = {r['id']: r for r in registry if r.get('id')}
        for row in content.RECORDS:
            self.assertIn(row['id'], current)
            for field in ('market', 'chain', 'name', 'serving', 'cal', 'p', 'c', 'fat', 'f', 'na', 'sugar', 'source'):
                self.assertEqual(row.get(field), current[row['id']].get(field), (row['id'], field))
            for field in ('cal', 'p', 'c', 'fat'):
                self.assertIsNotNone(row.get(field))
                self.assertTrue(row['nutrientProvenance'].get(field))

    def test_current_capture_integrity(self):
        directory = content.OUT / 'sources'
        checks = json.loads((directory / 'source-checks.json').read_text(encoding='utf-8'))
        self.assertEqual(len(checks), 15)
        identical = 0
        for check in checks:
            if check.get('file'):
                self.assertEqual(hashlib.sha256((directory / check['file']).read_bytes()).hexdigest(), check['sha256'])
            identical += int(check.get('sameAsPreviousCapture') is True)
        self.assertGreaterEqual(identical, 8)
        # Tim Hortons predates sourceHash in its registry, so verify its retained official PDF explicitly.
        self.assertEqual(hashlib.sha256((directory / 'CA-tim-hortons.pdf').read_bytes()).hexdigest(), hashlib.sha256((ROOT / 'docs/clarity-release-2026-10-14/editorial-source-evidence/tim-hortons.pdf').read_bytes()).hexdigest())
        dynamic = json.loads((directory / 'selected-dynamic-values.json').read_text(encoding='utf-8'))
        self.assertEqual(len(dynamic['selectedRecords']), 9)
        self.assertTrue(all(all(r['checks'].values()) for r in dynamic['selectedRecords']))

    def test_worked_order_arithmetic(self):
        get = content.get
        examples = [
            ([get('CA', 'Tim Hortons', 'Egg & Cheese English Muffin'), get('CA', 'Tim Hortons', 'Hash Brown'), get('CA', 'Tim Hortons', 'Original Blend Coffee - Medium')], 394, 15),
            ([get('CA', 'Harvey’s', 'Original Burger'), get('CA', 'Harvey’s', 'Fries (Regular)')], 810, 23),
            ([get('CA', 'Harvey’s', 'Original Burger'), get('CA', 'Harvey’s', 'Onion Rings (Regular)')], 680, 21),
            ([get('GB', 'Greggs', 'Bacon Breakfast Baguette'), get('GB', 'Greggs', 'Latte Regular')], 576, 33.8),
            ([get('GB', 'Five Guys', 'Little Hamburger'), get('GB', 'Five Guys', 'Mini Fries')], 814, 29),
            ([get('GB', 'Five Guys', 'Little Hamburger'), get('GB', 'Five Guys', 'Little Fries')], 1123, 34),
            ([get('GB', 'Chopstix', 'VEGETABLE CHOW MEIN · Regular'), get('GB', 'Chopstix', 'CARAMEL DRIZZLE CHICKEN · R/L/XL'), get('GB', 'Chopstix', 'SWEET & SOUR CHICKEN · R/L/XL')], 639, 29.5),
            ([get('US', 'Burger King', "Bacon, Egg, & Cheese Croissan'wich"), get('US', 'Burger King', 'Small Hash Browns'), get('US', 'Burger King', 'Small Brewed Coffee')], 630, 17),
        ]
        for rows, calories, protein in examples:
            total = content.add('example', rows, 'one named portion each')
            self.assertEqual(total['cal'], calories)
            self.assertEqual(total['p'], protein)
            self.assertTrue(total['calculated'])
            self.assertEqual(len(total['componentIds']), len(rows))

    def test_tortilla_uses_format_specific_rice(self):
        get = lambda name: content.get('GB', 'Tortilla', 'Medium Burrito/Bowl — ' + name)
        common = [get('Black Beans'), get('Chicken Asado'), get('Pico de Gallo')]
        burrito = content.add('burrito', [get('Tortilla Wrap'), get('Coriander Rice (Burrito)')] + common, 'medium')
        bowl = content.add('bowl', [get('Coriander Rice (Bowl)')] + common, 'medium')
        self.assertEqual((burrito['cal'], burrito['p']), (536, 34))
        self.assertEqual((bowl['cal'], bowl['p']), (399, 30))
        self.assertNotEqual(bowl['cal'], burrito['cal'] - get('Tortilla Wrap')['cal'])

    def test_chopstix_salt_arithmetic_matches_source_columns(self):
        get = lambda name: content.get('GB', 'Chopstix', name)
        toppings = [get('CARAMEL DRIZZLE CHICKEN · R/L/XL'), get('SWEET & SOUR CHICKEN · R/L/XL')]
        expected = [('VEGETABLE CHOW MEIN · Regular', 5.08), ('EGG FRIED RICE · Regular', 3.71), ('CAULI RICE · Regular', 4.51)]
        for name, salt in expected:
            total = content.add(name, [get(name)] + toppings, 'matching source allocations')
            self.assertEqual(total['salt'], salt)
        article = next(a for a in content.ARTICLES if a['slug'].startswith('chopstix-'))
        for value in ('5.08 g salt', '3.71 g', '4.51 g'):
            self.assertIn(value, article['body_html'])

    def test_copy_spacing_preserves_numbers_entities_and_urls(self):
        raw = '<p>Croissan&#x27;wich adds270kcal,22gprotein; totals1,060kcal in October2026.</p><a href="/item_299?q=25">View</a>'
        actual = content.spaced(raw)
        self.assertIn("Croissan&#x27;wich adds 270 kcal, 22 g protein; totals 1,060 kcal in October 2026.", actual)
        self.assertIn('href="/item_299?q=25"', actual)
        self.assertEqual(content.spaced(actual), actual)
        for article in content.ARTICLES:
            plain = unescape(re.sub('<[^>]+>', ' ', article['body_html']))
            self.assertNotRegex(plain, r'[A-Za-z]\d|\d[A-Za-z]')
            self.assertNotRegex(plain, r'\d, \d{3}\b')
            self.assertNotRegex(plain, r'&#')

    def test_missing_and_market_boundaries(self):
        kfc = content.get('GB', 'KFC', 'Fillet Burger')
        self.assertIsNone(kfc['f'])
        result = content.add('incomplete example', [kfc, content.get('GB', 'Greggs', 'Bacon Breakfast Baguette')], 'calculation test only')
        self.assertIsNone(result['f'])
        with self.assertRaises(AssertionError):
            content.add('invalid cross-market order', [kfc, content.get('US', 'Burger King', 'Small Hash Browns')], 'invalid')

    def test_wasabi_uses_reported_energy_and_calculated_macros(self):
        row = content.get('GB', 'Wasabi', 'Harmony set')
        self.assertEqual(row['cal'], 620)
        self.assertEqual(Decimal(str(row['p'])), Decimal('6.1') * Decimal('379') / Decimal('100'))
        self.assertEqual(Decimal(str(row['nativeNutrients']['salt'])), Decimal('1.25') * Decimal('379') / Decimal('100'))
        self.assertNotEqual(Decimal(str(row['cal'])), Decimal('164') * Decimal('379') / Decimal('100'))

    def test_hot_iced_builds_not_guessed_cream_subtraction(self):
        hot = content.get('GB', 'Starbucks', 'Pumpkin Spice Latte - skimmed milk · Grande')
        iced = content.get('GB', 'Starbucks', 'Iced Pumpkin Spice Latte - skimmed milk · Grande')
        self.assertIn('whipped cream', hot['ingredientDescription'].lower())
        self.assertNotIn('whipped cream', iced['ingredientDescription'].lower())
        self.assertEqual(hot['cal'] - iced['cal'], 64)
        self.assertIn('cannot be presented', next(a for a in content.ARTICLES if a['slug'].startswith('starbucks-uk-'))['body_html'])

    def test_internal_links_and_comparator_record_identity(self):
        for article in content.ARTICLES:
            links = [r['href'] for r in article['related']] + re.findall(r'href="([^"]+)"', article['body_html'])
            for href in links:
                href = unescape(href)
                parsed = urlsplit(href)
                if parsed.scheme:
                    continue
                target = ROOT / parsed.path.lstrip('/')
                if not target.suffix:
                    target /= 'index.html'
                self.assertTrue(target.exists(), (article['slug'], href))
                if parsed.path == '/compare-foods.html':
                    for item in parse_qs(parsed.query).get('item', []):
                        _, market, key = item.split(':', 2)
                        self.assertEqual(content.USED[key]['market'], market)

    def test_accessible_original_charts_and_public_copy(self):
        for article in content.ARTICLES:
            charts = re.findall(r'(<svg\b.*?</svg>)', article['body_html'], re.S)
            self.assertEqual(len(charts), 1)
            svg = ET.fromstring(charts[0])
            self.assertEqual(svg.get('role'), 'img')
            self.assertTrue(svg.get('aria-labelledby'))
            self.assertIsNotNone(svg.find('title'))
            self.assertNotIn('<image', charts[0])
            self.assertNotIn('<script', article['body_html'])
            self.assertNotIn('style=', article['body_html'])
            self.assertNotRegex(article['body_html'], r'\b(?:shell|timed out|fixture|commit|publisher|release check)\b')


if __name__ == '__main__':
    unittest.main()
