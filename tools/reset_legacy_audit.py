"""List old presentation files only after verifying public HTML/JS references."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
public=list(root.glob('*.html'))+list((root/'js').glob('*.js'))
rows=[]
for p in (root/'css').glob('*.css'):
 if p.name=='publication.css':continue
 refs=[str(x.relative_to(root)) for x in public if 'css/'+p.name in x.read_text(encoding='utf-8')]
 rows.append({'file':str(p.relative_to(root)),'active_references':refs})
(root/'docs/redesign/reset/legacy-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows,indent=2))
