"""Check semantic color pairs, not a substitute for rendered accessibility review."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
css=(root/'css/publication.css').read_text(encoding='utf-8')
def luminance(h):
 if len(h)==4:h='#'+''.join(c*2 for c in h[1:])
 values=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
 return sum(v*w for v,w in zip(values,[.2126,.7152,.0722]))
rows=[]
for theme,selector in [('light',':root'),('dark','html[data-theme=dark]')]:
 block=re.search(re.escape(selector)+r'\{([^}]+)',css)[1]
 colors=dict(re.findall(r'--([\w-]+):(#[\da-fA-F]+)',block))
 pairs=[(fg,bg,4.5) for fg in ['ink','muted','green'] for bg in ['bg','surface','soft']]
 pairs += [('on-green','green',4.5),('control-border','surface',3),('control-border','soft',3),('error','error-bg',4.5)]
 pairs += [('focus',bg,3) for bg in ['bg','surface','soft']]
 for fg,bg,target in pairs:
  a,b=sorted([luminance(colors[fg]),luminance(colors[bg])]);ratio=(b+.05)/(a+.05)
  rows.append(dict(theme=theme,foreground=fg,background=bg,ratio=round(ratio,2),target=target,passed=ratio>=target))
(root/'docs/redesign/palette-contrast.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
assert all(r['passed'] for r in rows),[r for r in rows if not r['passed']]
print('PASS',len(rows),'semantic text, action, control-border, error and focus contrast pairs')
