"""Reader utility, provenance, metadata and repeat-generation regressions."""
from pathlib import Path
import hashlib,json,re,sys,unittest,xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from search_recovery.article_tools import ROOT,SLUGS,DATE,label_rows,breakfast_model,apply,CONTEXT_LINKS
from normalize_calculator_layouts import Document

class ArticleTools(unittest.TestCase):
    def test_all_five_preserve_canonical_sources_and_original_publication(self):
        for slug,(title,h1,description) in SLUGS.items():
            text=(ROOT/(slug+'.html')).read_text(encoding='utf-8')
            self.assertEqual(len(re.findall(r'<h1\b',text)),1)
            self.assertIn('<h1>'+h1+'</h1>',text)
            self.assertIn('href="https://getmacros.net/'+slug+'.html"',text)
            self.assertIn('id="article-sources"',text)
            self.assertEqual(text.count('id="article-tool"'),1)
            self.assertIn('href="#article-tool"',text)
            schema=[json.loads(text[n['inner']:n['close']]) for n in Document(text).nodes if n['tag']=='script' and n['attrs'].get('type')=='application/ld+json']
            article=next(s for s in schema if s.get('@type')=='Article')
            self.assertEqual(article['datePublished'],'2026-10-19');self.assertEqual(article['dateModified'],DATE)
            self.assertNotIn('content="noindex',text)
    def test_models_use_retained_local_sources(self):
        greggs=breakfast_model('greggs-');tim=breakfast_model('tim-hortons-')
        self.assertEqual(len(greggs['mains']),4);self.assertEqual(len(tim['mains']),6)
        for model in [greggs,tim]:
            rows=model['mains']+model['drinks']+([model['side']] if model['side'] else [])
            self.assertEqual({r['market'] for r in rows},{model['market']})
            self.assertEqual(len({r['id'] for r in rows}),len(rows))
            self.assertEqual(len({r['source'] for r in rows}),1)
        self.assertEqual(label_rows('fage-plain-greek-yogurt-0-2-5-percent')['baseGrams'],170)
        self.assertEqual(label_rows('barilla-australia-protein-plus-vs-spaghetti')['rows'][0]['p'],20)
    def test_barcode_is_a_real_manual_lookup_and_retains_leading_zeroes(self):
        text=(ROOT/'barcode-food-search-label-check.html').read_text(encoding='utf-8');d=Document(text)
        form=next(n for n in d.nodes if n['tag']=='form' and n['attrs'].get('action')=='/food-library.html')
        self.assertEqual(form['attrs']['method'],'get')
        input=next(n for n in d.nodes if n['attrs'].get('id')=='article-barcode')
        self.assertEqual(input['attrs']['type'],'search');self.assertEqual(input['attrs']['name'],'q')
        self.assertIn('no camera needed',text)
    def test_contextual_links_and_source_only_fallback(self):
        for parent,links in CONTEXT_LINKS.items():
            text=(ROOT/parent).read_text(encoding='utf-8')
            self.assertEqual(text.count('id="worked-portion-tools"'),1)
            for slug,_ in links:self.assertIn('/'+slug+'.html',text)
        for slug in SLUGS:
            text=(ROOT/(slug+'.html')).read_text(encoding='utf-8')
            if not slug.startswith('barcode-'):
                self.assertIn('<form hidden>',text)
                self.assertRegex(text,r'data-tool-results[^>]*><table>')
    def test_repeat_generation_is_stable_and_does_not_touch_catalogs(self):
        files=[ROOT/(slug+'.html') for slug in SLUGS]+[ROOT/p for p in CONTEXT_LINKS]+[ROOT/'articles.html',ROOT/'sitemap.xml']
        catalogs=[ROOT/'js/order-registry.json',ROOT/'data/food-library/manifest.json']
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        catalog_before=[sha(p) for p in catalogs]
        apply();before=[sha(p) for p in files];apply()
        self.assertEqual(before,[sha(p) for p in files]);self.assertEqual(catalog_before,[sha(p) for p in catalogs])

if __name__=='__main__':unittest.main()
