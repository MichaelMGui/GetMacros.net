"""Fetch tiny local illustrations before scrolling reaches them.

They keep their declared dimensions and use low priority, so the main image,
styles, and fonts still come first. Larger images retain native lazy loading.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def optimize(text):
    def image(match):
        tag = match[0]
        source = re.search(r'src="(images/[^"?]+\.svg)(?:\?[^\"]*)?"', tag)
        if not source or 'loading="lazy"' not in tag:
            return tag
        path = ROOT / source[1]
        if not path.is_file() or path.stat().st_size > 16384:
            return tag
        tag = tag.replace('loading="lazy"', 'loading="eager"')
        if 'fetchpriority=' not in tag:
            tag = tag.replace('<img', '<img fetchpriority="low"', 1)
        return tag
    return re.sub(r'<img\b[^>]*>', image, text)

if __name__ == '__main__':
    changed = 0
    for path in ROOT.glob('*.html'):
        original = path.read_text(encoding='utf-8')
        result = optimize(original)
        if result != original:
            path.write_text(result, encoding='utf-8')
            changed += 1
    print(f'Prepared small illustrations for scrolling on {changed} pages.')
