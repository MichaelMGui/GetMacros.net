"""Bundle contiguous shared style layers, preserving cascade order and CSS tokens."""
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {
    'core-bundle': ['unified-v7', 'theme-fix', 'editorial-v8', 'clean-v9'],
    'finish-bundle': ['tide', 'tide-motion', 'workspaces', 'site-refresh'],
}

def compact(css):
    # Strings stay byte-for-byte intact. Removing a comment leaves a space so
    # adjacent tokens cannot merge; whitespace remains inside calc() expressions.
    tokens = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|\s+', re.S)
    return tokens.sub(lambda m: m[0] if m[0][0] in '\"\'' else ' ', css).strip()

def restore(text):
    for name, sources in GROUPS.items():
        text = re.sub(r'<link rel="stylesheet" href="css/'+name+r'\.css(?:\?[^\"]*)?"[^>]*>',
                      ''.join('<link rel="stylesheet" href="css/'+s+'.css">' for s in sources), text)
    return text

def run():
    restoring = '--restore' in sys.argv
    saved = 0
    for name, sources in GROUPS.items():
        raw = '\n'.join((ROOT/'css'/f'{s}.css').read_text(encoding='utf-8') for s in sources)
        packed = compact(raw)+'\n'
        if not restoring:
            (ROOT/'css'/f'{name}.css').write_text(packed, encoding='utf-8')
            saved += len(raw.encode()) - len(packed.encode())
    count = 0
    for path in ROOT.glob('*.html'):
        text = restore(path.read_text(encoding='utf-8'))
        if not restoring:
            # Font preload doesn't participate in the style cascade.
            preload = re.search(r'<link rel="preload" href="fonts/manrope[^>]+>', text)
            if preload:
                text = text.replace(preload[0], '').replace('</head>', preload[0]+'</head>')
            for name, sources in GROUPS.items():
                pattern = r'\s*'.join(r'<link rel="stylesheet" href="css/'+re.escape(s)+r'\.css(?:\?[^\"]*)?">' for s in sources)
                replacement = '<link rel="stylesheet" href="css/'+name+'.css" data-sources="'+'|'.join('css/'+s+'.css' for s in sources)+'">'
                text, n = re.subn(pattern, replacement, text)
                if n != 1:
                    raise ValueError(f'{path.name}: {name} sources must be contiguous and occur once (found {n})')
        path.write_text(text, encoding='utf-8')
        count += 1
    print(f'{"Restored" if restoring else "Bundled"} shared styles on {count} pages; {saved:,} source bytes removed.')

if __name__ == '__main__':
    run()
