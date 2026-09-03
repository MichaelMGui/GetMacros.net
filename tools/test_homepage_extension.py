"""Source regression checks for the homepage extension (not browser QA)."""
from pathlib import Path
import re
from extend_homepage import extend, ROOT

text = (ROOT / 'index.html').read_text(encoding='utf-8')
assert extend(extend(text)) == extend(text)
assert text.count('homepage-extension:start') == 1
block = text.split('<!-- homepage-extension:start -->')[1].split('<!-- homepage-extension:end -->')[0]
assert len(re.findall(r'<details\b', block)) == 4
assert len(re.findall(r'class="home-everyday-tool"', block)) == 3
for href in re.findall(r'href="([^"]+)"', block):
    target = href.split('?')[0].split('#')[0]
    assert (ROOT / target).is_file(), target
assert text.index('home-launcher') < text.index('homepage-extension:start')
assert text.index('css/clean-v9.css') < text.index('css/home-extension.css')
css = (ROOT / 'css/home-extension.css').read_text(encoding='utf-8')
assert css.count('{') == css.count('}')
assert 'max-width:760px' in css and 'prefers-reduced-motion:no-preference' in css
print('PASS: three tool links, four disclosures, existing destinations, repeatable extension and responsive styles.')
print('Added section words:', len(re.sub('<[^>]+>', ' ', block).split()))
