"""Restore logical asset references before generators consume published HTML.

Immutable filenames belong to output. Legacy generators correctly remove and
reconcile logical modules; feeding them hash-named output duplicated modules.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
def restore():
    pages=list(ROOT.glob('*.html'))+list(ROOT.glob('*/en/**/index.html'))
    for page in pages:
        html=page.read_text(encoding='utf-8')
        html=re.sub(r'<script data-public-assets>.*?</script>','',html,flags=re.S)
        prefix='/' if '/en/' in page.relative_to(ROOT).as_posix() else ''
        def logical(match):
            tag=match[0]
            source=re.search(r'data-source-path="([^"]+)"',tag)
            if not source:return tag
            tag=re.sub(r'\sdata-source-path="[^"]+"','',tag)
            return re.sub(r'\b(href|src)="[^"]+"',lambda m:m[1]+'="'+prefix+source[1]+'"',tag,count=1)
        html=re.sub(r'<(?:link|script)\b[^>]*>',logical,html)
        seen=set()
        def unique(match):
            source=re.search(r'\bsrc="([^"]+)"',match[0])
            if not source:return match[0]
            key=source[1].split('?')[0].lstrip('/')
            if key in seen:return ''
            seen.add(key);return match[0]
        html=re.sub(r'<script\b[^>]*\bsrc="[^"]+"[^>]*>\s*</script>',unique,html)
        page.write_text(html,encoding='utf-8')
    print('Restored logical source assets for',len(pages),'public build inputs.')
if __name__=='__main__':restore()
