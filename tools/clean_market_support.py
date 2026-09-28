from pathlib import Path
import re,json
p=Path('tools/market-system.css');s=p.read_text(encoding='utf-8').replace('.page-intro-content h1{','.page-intro-content{min-width:0}.page-intro-content h1{',1);p.write_text(s,encoding='utf-8')
corpus='\n'.join(p.read_text(encoding='utf-8') for p in [*Path('.').glob('*.html'),*Path('js').glob('*.js')])
p=Path('tools/market-content.css');s=p.read_text(encoding='utf-8');removed=[]
def clean(m):
 selector=m[1].strip()
 if '@' in selector or '/*' in selector:return m[0]
 parts=selector.split(',')
 classes=[re.match(r'\.([a-zA-Z][\w-]*)',part.strip()) for part in parts]
 if classes and all(c and c[1] not in corpus for c in classes):removed.append(selector);return ''
 return m[0]
s=re.sub(r'([^{}]+)\{([^{}]*)\}',clean,s);p.write_text(s,encoding='utf-8')
Path('docs/redesign/reset/removed-content-selectors.json').write_text(json.dumps(removed,indent=2),encoding='utf-8');print('Removed',len(removed),'unreferenced support rules')
