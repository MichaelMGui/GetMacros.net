"""Reconcile route evidence without pretending automated renders are visual review."""
from pathlib import Path
import csv, json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/clarity-release-2026-10-14'
render=json.loads((OUT/'route-renders.json').read_text(encoding='utf-8'))
assert render['routes']==363 and not render['failures'] and len(render['renders'])==1452
manual={
    '/':'U.S./Canada side-by-side light desktop; U.S. light mobile',
    '/ca/en/':'U.S./Canada side-by-side light desktop',
    '/food-diary.html':'Light mobile empty diary; food review and logged state',
    '/calculators.html':'Dark desktop inputs; light mobile calculated result',
    '/compare-foods.html':'Light/dark desktop; close-up of centered comparison marker',
    '/ca/en/find-a-meal/':'Dark mobile actual Subway results',
    '/read-and-watch.html':'Light desktop and mobile; dark mobile (character review)',
    '/ca/en/restaurants/triple-os/':'Light mobile source guide and complete-order tables',
    '/privacy.html':'Dark desktop; diary notice moved into the same reading column',
    '/sources.html':'Light mobile source-methodology reading layout',
    '/nutrition-label-comparison-tool.html':'Light desktop inputs and listed-portion result',
    '/tim-hortons-canada-protein-latte-vs-latte.html':'Light mobile (editorial review)',
    '/kirkland-canada-macadamia-vs-mixed-nuts.html':'Dark mobile source comparison and table reflow',
    '/guzman-y-gomez-australia-chicken-bowl-vs-burrito.html':'Light desktop (editorial review)',
    '/subway-turkey-breast-canada-vs-mexico.html':'Light mobile (editorial review)',
    '/play-market-memory.html':'320 px play/completion (character review)',
    '/play-garden-pipes.html':'Dark desktop completion (character review)',
    '/play-mascot-maker.html':'Dark mobile (character review)',
}
with (OUT/'coverage.csv').open(encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert len(rows)==363
for row in rows:
    row['functional_checks']='PASS automated 200 response, one H1, theme, stylesheet loading, runtime and document-overflow checks at 390/1280 in both themes; relevant journey evidence in release report'
    row['visual_checks']=('Manually opened rendered capture: '+manual[row['route']]) if row['route'] in manual else 'Individual route rendered automatically; not individually manually inspected. Shared family visual review described in release report.'
    if row['route']=='/ca/en/restaurants/pizza-nova/':row['remaining_blockers']='Official tracked data has calories only; no inferred core macros and excluded from macro-complete finder.'
with (OUT/'coverage.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
print('Reconciled 363 route rows;',len(manual),'explicit manual-review routes, other individual routes labelled automated only.')
