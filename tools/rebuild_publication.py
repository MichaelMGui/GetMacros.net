"""Final, repeatable publication presentation. Preserve page URLs and tool hooks.

Reviewed HTML is the source for inner pages. Historical redesign generators are
retired. This pass owns the homepage, examples, stylesheet and advertising state.
"""
from pathlib import Path
from html import escape
import json,re
from normalize_calculator_layouts import Document
from publication_examples import EXAMPLES

ROOT=Path(__file__).resolve().parents[1]
LOGO='<svg viewBox="0 0 36 36" fill="none" aria-hidden="true"><circle cx="18" cy="18" r="14" stroke="currentColor" stroke-width="2.5"/><path d="M18 4v28M18 18h14" stroke="currentColor" stroke-width="2.5"/><path d="M8 18c0-5 3-8 6-8v16c-3 0-6-3-6-8Z" fill="currentColor"/></svg>'

def replace_node(text,node,replacement):return text[:node['start']]+replacement+text[node['end']:]

def run():
 for path in ROOT.glob('*.html'):
  text=path.read_text(encoding='utf-8')
  if path.name=='index.html':
   doc=Document(text);main=next(n for n in doc.nodes if n['tag']=='main')
   text=replace_node(text,main,(ROOT/'tools/publication-home.inc').read_text(encoding='utf-8'))
  if path.name in EXAMPLES and 'id="worked-comparison"' not in text:
   doc=Document(text)
   candidates=[n for n in doc.nodes if 'article-container' in n['attrs'].get('class','').split()]
   if candidates:
    n=candidates[0]
    text=text[:n['inner']]+EXAMPLES[path.name]+text[n['inner']:]
    text=text.replace('Updated September 9, 2026','Updated September 22, 2026')
    text=re.sub(r'("dateModified"\s*:\s*")[^"]+',r'\g<1>2026-09-22',text)
  # Remove obsolete presentation at the source, not behind a second cascade.
  text=re.sub(r'<style\b[^>]*>.*?</style>','',text,flags=re.S)
  text=re.sub(r'<link\b(?=[^>]*rel="stylesheet")[^>]*>','',text)
  text=re.sub(r'<link\b(?=[^>]*rel="preload")(?=[^>]*as="font")[^>]*>','',text)
  text=re.sub(r'<link\b[^>]*rel="preconnect"[^>]*href="https://pagead2\.googlesyndication\.com"[^>]*>','',text)
  text=text.replace('</head>','<link rel="stylesheet" href="css/publication.css"><link rel="preload" href="fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="fonts/inter-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin></head>')
  # Publisher verification is retained. Ad serving awaits account-side CMP
  # verification; a home-made banner would not meet Google's CMP requirement.
  text=re.sub(r'<script\b[^>]*src="https://pagead2\.googlesyndication\.com/[^>]*>.*?</script>','',text,flags=re.S)
  text=re.sub(r'<script\b[^>]*src="js/(?:main|lang|tide-motion|polish|site-motion|studio-v6|atelier-v5|calculator-suite)\.js[^>]*>.*?</script>','',text,flags=re.S)
  text=re.sub(r'(<body\b[^>]*?)\sdata-ads="[^"]*"',r'\1',text)
  text=re.sub(r'(<body\b[^>]*?)\sdata-publication="[^"]*"',r'\1',text)
  text=re.sub(r'<body\b', '<body data-ads="off" data-publication="2026-09"',text,count=1)
  # Presentational inline styles were remnants of older generated templates.
  text=re.sub(r'\sstyle="[^"]*"','',text)
  doc=Document(text)
  edits=[]
  for n in doc.nodes:
   if 'brand-mark' in n['attrs'].get('class','').split(): edits.append((n['inner'],n['close'],LOGO))
  for a,b,value in reversed(edits):text=text[:a]+value+text[b:]
  text=text.replace('How I write the guides','Editorial policy')
  if path.name=='privacy.html':
   text=re.sub(r'<p>This site integrates Google AdSense\..*?</p>','<p>GetMacros has applied to Google AdSense. Publisher ownership verification remains on the site, but advertising scripts are currently paused. No Google ad requests are made by the site code. Before enabling ads, we will configure the required consent controls, verify their behavior and update this notice.</p><p>If advertising is enabled later, Google and its partners may use cookies or similar technologies. See <a href="https://policies.google.com/technologies/partner-sites">how Google uses information from sites that use its services</a> and <a href="https://myadcenter.google.com">Google’s advertising controls</a>.</p>',text,flags=re.S)
  # Clarify the educational scope next to the full macro form.
  if path.name=='calculators.html' and 'publication-calculator-note' not in text:
   text=text.replace('<form class="calc-form" id="macro-form">','<form class="calc-form" id="macro-form"><p class="clarity-hint publication-calculator-note">Adult estimates, not a prescription. Uses Mifflin–St Jeor resting energy, an activity multiplier and your chosen goal. <a href="sources.html">Formula and limitations</a>.</p>')
  # Attach provenance before any meal consumer executes. All unknown fat
  # values remain null; f in the historical dataset explicitly means fiber.
  if 'js/meal-data.js' in text:
   text=re.sub(r'<script[^>]+src="js/meal-provenance.js[^>]*>.*?</script>','',text,flags=re.S)
   text=re.sub(r'(<script[^>]+src="js/meal-data\.js[^>]*>\s*</script>)',r'\1<script src="js/meal-provenance.js" defer></script>',text)
  # Keep every retained article's factual body and current verification date.
  text=re.sub(r'\n{3,}','\n\n',text)
  path.write_text(text,encoding='utf-8')
 records=json.loads((ROOT/'tools/restaurant-review.json').read_text(encoding='utf-8'))
 metadata={r['chain']+'||'+r['name']:{'source':r['source'],'checked':r['checked'],'region':'U.S.','serving':'1 listed order','fat':None} for r in records}
 metadata['Chick-fil-A||Grilled Chicken Sandwich'].update(fat=11,serving='1 sandwich (206 g)',checked='2026-09-22',source='https://www.chick-fil-a.com/nutrition-allergens')
 script='/* Source records; missing fat is not estimated from calories. */\n(function(){var records='+json.dumps(metadata,ensure_ascii=False,separators=(',',':'))+'; (window.GM_MEALS||[]).forEach(function(m){var r=records[m.chain+"||"+m.name];if(r)Object.assign(m,r);});})();\n'
 (ROOT/'js/meal-provenance.js').write_text(script,encoding='utf-8')
 sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
 for name in [*EXAMPLES,'','calculators.html','restaurant-meal-finder.html','privacy.html']:
  url='https://getmacros.net/'+name
  sitemap=re.sub(r'(<loc>'+re.escape(url)+r'</loc><lastmod>)[^<]+',r'\g<1>2026-09-22',sitemap)
 (ROOT/'sitemap.xml').write_text(sitemap,encoding='utf-8')
 print('Publication layout applied to all retained pages; publisher verification retained, ad requests paused.')

if __name__=='__main__':run()
