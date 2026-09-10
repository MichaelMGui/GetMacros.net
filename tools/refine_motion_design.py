"""Keep the final visual identity and above-fold asset loading repeatable."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
# A divided dinner plate makes the food/macros connection at small sizes.
MARK = '''<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="13" fill="#fff9ee"/><path d="M16 6a10 10 0 0 0 0 20Z" fill="#318454"/><path d="M18 6.2V15h8a10 10 0 0 0-8-8.8Z" fill="#d49254"/><path d="M18 17v8.8a10 10 0 0 0 8-8.8Z" fill="#4e8797"/></svg>'''

def run():
    for path in ROOT.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'(?:<!--journal-revision:start-->)+', '<!--journal-revision:start-->', text)
        text = re.sub(r'(<span class="brand-mark"[^>]*>)\s*<svg\b[^>]*>.*?</svg>', lambda m: m[1]+MARK, text, flags=re.S)
        # Reserve space for the quiz before its script arrives. Both scripts
        # stay ordered but no longer block parsing the meal library/footer.
        text = re.sub(r'(<script src="js/meal-(?:data|quiz)\.js[^" ]*")(?: defer)?(></script>)', r'\1 defer\2', text)
        text = text.replace('<h1>Find healthy fast-food meals</h1>', '<h1>Find healthy fast food meals</h1>')
        text = text.replace('Healthy fast-food meals.<br><em>Find your fit.</em>', 'Healthy fast food.<br><em>Find your meal.</em>')
        # Only the main illustration needs priority; lower artwork stays lazy.
        text = re.sub(r'<img src="images/meal-play.svg"[^>]*>', lambda m: m[0][:-1].replace(' fetchpriority="high"', '')+' fetchpriority="high">', text)
        path.write_text(text, encoding='utf-8')
    (ROOT/'favicon.svg').write_text(MARK.replace('viewBox=', 'xmlns="http://www.w3.org/2000/svg" viewBox=',1),encoding='utf-8')
    print('Applied plate identity, clear meal-finder title and ordered deferred quiz scripts.')

if __name__ == '__main__':
    run()
