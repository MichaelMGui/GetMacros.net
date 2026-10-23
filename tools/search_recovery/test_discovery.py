"""Regressions for explicit editorial relationships and local crawl paths."""
import hashlib
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from search_recovery.discovery import ROOT, RELATED, HOME_STORIES, story, markets, html_path, append_before_main_end, section
from normalize_calculator_layouts import Document


class DiscoveryTests(unittest.TestCase):
    def test_owned_sections_replace_even_without_surrounding_comments(self):
        key='directory-order-guides'
        body=section(key,'Compare orders',[('/healthy-fast-food.html','Compare food')])
        without_comments=re.sub(r'<!--.*?-->','',body,flags=re.S)
        page='<html><body><main><span id="'+key+'"></span>'+without_comments+without_comments+'</main></body></html>'
        repaired=append_before_main_end(page,key,body)
        self.assertEqual(repaired.count('id="'+key+'"'),1)
        self.assertEqual(append_before_main_end(repaired,key,body),repaired)

    def test_every_release_article_has_a_relevant_contextual_parent(self):
        published={r['route'] for r in json.loads((ROOT/'docs/ultimate-release-2026-10-19/publication-manifest.json').read_text(encoding='utf-8'))}
        connected={story(slug)[0] for slugs in RELATED.values() for slug in slugs}
        self.assertEqual(len(published),29)
        self.assertTrue(published <= connected, published-connected)
        for parent,slugs in RELATED.items():
            text=(ROOT/html_path(parent)).read_text(encoding='utf-8')
            main=next(n for n in Document(text).nodes if n['tag']=='main')
            body=text[main['inner']:main['close']]
            self.assertEqual(body.count('id="related-order-guides"'),1,parent)
            for slug in slugs:self.assertIn('href="'+story(slug)[0]+'"',body,parent)

    def test_every_country_has_visible_local_nutrition_links(self):
        for code,info in markets().items():
            text=(ROOT/html_path(info['home'])).read_text(encoding='utf-8')
            nav=next(n for n in Document(text).nodes if n['tag']=='nav' and n['attrs'].get('aria-label')=='Local nutrition tables')
            self.assertNotIn('hidden',nav['attrs'])
            urls=re.findall(r'href="([^"]+)"',text[nav['inner']:nav['close']])
            self.assertGreaterEqual(len(urls),1,code)
            self.assertLessEqual(len(urls),4,code)
            for url in urls:
                self.assertTrue((ROOT/html_path(url)).is_file(),url)
                self.assertNotIn('?',url)
                if code!='US':self.assertTrue(url.startswith('/'+code.lower()+'/en/'),url)

    def test_homepage_stories_are_local_and_keep_shared_structure(self):
        for code,slugs in HOME_STORIES.items():
            text=(ROOT/html_path(markets()[code]['home'])).read_text(encoding='utf-8')
            for cls in ('home-reading-layout','reading-feature','reading-links'):
                self.assertEqual(len([n for n in Document(text).nodes if cls in n['attrs'].get('class','').split()]),1,code)
            section=next(n for n in Document(text).nodes if 'home-reading' in n['attrs'].get('class','').split())
            body=text[section['inner']:section['close']]
            for slug in slugs:self.assertIn('href="'+story(slug)[0]+'"',body,code)
        ca=(ROOT/'ca/en/index.html').read_text(encoding='utf-8')
        self.assertNotIn('href="/burger-king-us-breakfast-hash-browns-order.html"',ca)

    def test_metadata_dates_and_canonicals_are_consistent(self):
        report=json.loads((ROOT/'docs/search-discovery-2026-10-23/implementation.json').read_text(encoding='utf-8'))
        sitemap={n.find('{*}loc').text:n.find('{*}lastmod').text for n in ET.parse(ROOT/'sitemap.xml').getroot()}
        for route in report['routes']:
            text=(ROOT/html_path(route)).read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'<h1\b',text)),1,route)
            self.assertIn('rel="canonical" href="https://getmacros.net'+route+'"',text,route)
            self.assertNotRegex(text,r'<meta[^>]*name="robots"[^>]*content="[^"]*noindex')
            self.assertEqual(sitemap['https://getmacros.net'+route],'2026-10-23',route)
        self.assertEqual(report['newPublicPages'],0)
        self.assertEqual(report['nutritionRecordsChanged'],0)
        text=(ROOT/'nutrition-label-comparison-tool.html').read_text(encoding='utf-8')
        self.assertIn('<h1>Compare nutrition facts</h1>',text)
        self.assertIn('id="compareForm"',text)
        self.assertIn('160 vs. 210 calories',text)

    def test_link_manifest_has_no_broken_or_noncanonical_destinations(self):
        report=json.loads((ROOT/'docs/search-discovery-2026-10-23/implementation.json').read_text(encoding='utf-8'))
        for link in report['links']:
            self.assertTrue((ROOT/html_path(link['from'])).is_file(),link)
            text=(ROOT/html_path(link['to'])).read_text(encoding='utf-8')
            self.assertIn('rel="canonical" href="https://getmacros.net'+link['to']+'"',text,link)
            self.assertNotRegex(text,r'<meta[^>]*name="robots"[^>]*content="[^"]*noindex')


if __name__=='__main__':unittest.main()
