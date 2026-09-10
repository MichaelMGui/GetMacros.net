"""Verify bundle contents and ordered provenance on every output page."""
from bundle_styles import ROOT, GROUPS, OPTIONAL, compact, restore
import re
for name, sources in GROUPS.items():
    expected = compact('\n'.join((ROOT/'css'/f'{s}.css').read_text(encoding='utf-8') for s in sources))+'\n'
    assert (ROOT/'css'/f'{name}.css').read_text(encoding='utf-8') == expected, name+' is stale'
    for path in ROOT.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        if name in OPTIONAL and not re.search(r'href="css/'+name+r'\.css\?', text):
            assert all(re.search(r'href="css/'+s+r'\.css\?', text) for s in sources), path.name
            continue
        assert len(re.findall(r'href="css/'+name+r'\.css\?', text)) == 1, path.name
        assert 'data-sources="'+'|'.join('css/'+s+'.css' for s in sources)+'"' in text, path.name
        for source in sources:
            assert not re.search(r'href="css/'+source+r'\.css', text), path.name+' duplicates '+source
        expanded = restore(text)
        positions = [expanded.index('href="css/'+s+'.css') for s in sources]
        assert positions == sorted(positions), path.name
assert compact('a/**/b { content: " a  b "; width:calc(100% - 2px); }') == 'a b { content: " a  b "; width:calc(100% - 2px); }'
print('Shared bundles preserve CSS tokens, source order and one copy of each layer on all pages.')
