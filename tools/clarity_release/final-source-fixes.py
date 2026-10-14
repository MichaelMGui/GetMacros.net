"""Reviewed source edits for the final comparison-loading and privacy checks."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
p = ROOT / 'js/food-portion-compare.js'
s = p.read_text(encoding='utf-8')
old = "addEventListener('click',()=>{try{const snapshot=UI.snapshot();"
new = "addEventListener('click',()=>{try{if(root.getAttribute('aria-busy')==='true')throw Error('The shared comparison is still loading. Add this food when it is ready.');const snapshot=UI.snapshot();"
if old in s:
    s = s.replace(old, new, 1)
    s = s.replace("root.querySelector('[data-food-compare-clear]').disabled=false;});}", "root.querySelector('[data-food-compare-clear]').disabled=false;document.dispatchEvent(new CustomEvent('food-comparison-ready'));});}")
    p.write_text(s, encoding='utf-8')
p = ROOT / 'js/food-app.js'
s = p.read_text(encoding='utf-8')
old = "form.querySelector('[data-review-'+key+']').disabled=false;}catch(e)"
new = "form.querySelector('[data-review-'+key+']').disabled=false;if(document.querySelector('[data-food-comparison][aria-busy=true]')){form.querySelector('[data-review-compare]').disabled=true;form.querySelector('[data-review-error]').textContent='The shared comparison is still loading. Add this food when it is ready.';}}catch(e)"
if old in s:
    s = s.replace(old, new, 1)
    s = s.replace("const snapshot=()=>F.snapshot", "document.addEventListener('food-comparison-ready',()=>{if(dialog.open)updatePreview();});\nconst snapshot=()=>F.snapshot", 1)
    p.write_text(s, encoding='utf-8')
p = ROOT / 'privacy.html'
s = p.read_text(encoding='utf-8')
marker = '<!-- clarity-comparison-privacy:start -->'
if marker not in s:
    s = s.replace('Last updated October 3, 2026.', 'Last updated October 14, 2026.', 1)
    anchor = '<h2 id="read-3">Shared meal-finder links</h2>'
    text = marker + '<p>Reviewed comparisons retain up to two public food records, portion amounts and the comparison basis in this browser’s local storage. Clear comparison removes those selections. Shared comparison links include the public food identifiers and selected portions; they do not include diary entries or private notes. Anyone receiving a link can see its portions, and the requested URL may appear in hosting logs.</p><!-- clarity-comparison-privacy:end -->'
    s = s.replace(anchor, text + anchor, 1)
    p.write_text(s, encoding='utf-8')
print('Final source fixes applied.')
p = ROOT / 'tools/playful-system.css'
s = p.read_text(encoding='utf-8').replace('grid-row:span 5;', 'grid-row:span 6;')
p.write_text(s, encoding='utf-8')
p = ROOT / 'js/meal-guide.js'
s = p.read_text(encoding='utf-8').replace("const country=meals[0]?.country==='CA'?'Canadian':'U.S.',", "const country=(window.GM_MARKETS||{})[meals[0]?.market||meals[0]?.country||window.GetMacrosMarket?.current||'US']?.name||'Selected country',")
s = s.replace("[window.GetMacrosMarket?.current||meals[0]?.market||meals[0]?.country||'US']", "[meals[0]?.market||meals[0]?.country||window.GetMacrosMarket?.current||'US']")
s = s.replace("const country=(window.GM_MARKETS||{})", "const country=()=>(window.GM_MARKETS||{})").replace('${country} menus.', '${country()} menus.')
p.write_text(s, encoding='utf-8')
p = ROOT / 'tools/product_release/test-food.cjs'
s = p.read_text(encoding='utf-8')
s = s.replace("assert.equal(registry.records.length,1400+additions.length+extra.length);", "const clarity=JSON.parse(fs.readFileSync('tools/clarity_release/restaurant_additions.json')).records;assert.equal(registry.records.length,1400+additions.length+extra.length+clarity.length);for(const r of clarity){const actual=registry.records.find(x=>x.id===r.id);assert(actual&&actual.market===r.market&&actual.name===r.name&&actual.cal===r.cal&&actual.p===r.p);}")
p.write_text(s, encoding='utf-8')
p = ROOT / 'js/diary-actions.js'
s = p.read_text(encoding='utf-8').replace("s.quantity+' '+s.portionLabel", "F.formatPortion(s)")
p.write_text(s, encoding='utf-8')
for name in ['baseline.cjs', 'refine_sources.py']:
    p = ROOT / 'tools/clarity_release' / name
    s = p.read_text(encoding='utf-8')
    p.write_text('\n'.join(line.rstrip() for line in s.rstrip().splitlines()) + '\n', encoding='utf-8')
