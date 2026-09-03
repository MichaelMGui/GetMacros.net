"""Keep the homepage extension intact after legacy page generators run."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def extend(text):
    block = (ROOT / 'tools/homepage-extension.inc').read_text(encoding='utf-8').strip()
    text = re.sub(r'<!-- homepage-extension:start -->.*?<!-- homepage-extension:end -->\s*', '', text, flags=re.S)
    anchor = '<section class="gm6-learning">'
    if text.count(anchor) != 1:
        raise ValueError('Expected exactly one homepage guides section')
    text = text.replace(anchor, block + '\n' + anchor, 1)
    if 'css/home-extension.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="css/home-extension.css"></head>', 1)
    return text

if __name__ == '__main__':
    path = ROOT / 'index.html'
    path.write_text(extend(path.read_text(encoding='utf-8')), encoding='utf-8')
    print('Homepage extended with everyday tools and meal-finder questions')
