"""Check coverage and discovery of the November follow-up against built pages."""

from collections import Counter
from html import unescape
from xml.etree import ElementTree

from build import ARTICLES, FOLLOWUP, FOLLOWUP_DATE, HOST, ROOT, SECTION_PAGES, public_articles
from normalize_calculator_layouts import Document


def main():
    released = public_articles()
    for index in (0, 1, 2, 3):
        assert len({row[index].casefold() for row in released}) == len(released), index
    assert len(ARTICLES) == 300
    assert len(FOLLOWUP) <= 150
    counts = Counter(row[0][1:3] for row in released[len(ARTICLES):])
    assert all(count <= 25 for count in counts.values())
    if len(FOLLOWUP) == 150:
        assert len(counts) == 6 and set(counts.values()) == {25}
    sitemap = Counter(node.text for node in ElementTree.parse(ROOT / 'sitemap.xml').findall('.//{*}loc'))
    search = (ROOT / 'search.html').read_text(encoding='utf-8')
    sections = [(ROOT / route).read_text(encoding='utf-8') for route in SECTION_PAGES]
    for record in FOLLOWUP.values():
        id_, _, route, title, summary, sources, scope = record['article']
        assert len(sources) == len(set(sources)) and sources
        assert summary and scope and len(record['table']) >= 4
        assert len(' '.join(record['copy']).split()) >= 92
        assert title in unescape(sections[int(id_[1:3]) - 1])
        assert f'href="/{route}"' in search
        assert sitemap[f'{HOST}/{route}'] == 1
        html = (ROOT / route).read_text(encoding='utf-8')
        assert f'Sources checked {FOLLOWUP_DATE}' in html
        assert record['table'][0] in unescape(html)
        doc = Document(html)
        headings = [node for node in doc.nodes if node['tag'] == 'h1']
        assert len(headings) == 1 and unescape(html[headings[0]['inner']:headings[0]['close']]) == title
        assert [n['attrs']['href'] for n in doc.nodes if n['attrs'].get('rel') == 'canonical'] == [f'{HOST}/{route}']
        linked = {unescape(node['attrs'].get('href', '')) for node in doc.nodes if node['tag'] == 'a'}
        assert set(sources) <= linked
        assert record['related'][0] in linked
    print(f'PASS {len(FOLLOWUP)} new guides and {len(ARTICLES)} original guides across six collections.')


if __name__ == '__main__':
    main()
