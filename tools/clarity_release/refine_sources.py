"""One-time reviewed source migration, safe to re-run; not a build-time override."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'js/meal-view.js';s=p.read_text(encoding='utf-8')
old='<span>Compare</span></label></div>'
new='<span>Compare</span></label><a class="text-action compare-workspace-link" href="/compare-foods.html?item=${encodeURIComponent(\'order:\'+(m.market||m.country||\'US\')+\':\'+(m.id||m.chain+\'||\'+m.name))}&amp;append=1">Compare portion</a></div>'
if old in s:s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=ROOT/'js/meal-finder.js';s=p.read_text(encoding='utf-8')
old="compareDialog.showModal();"
new="""const workspace=document.createElement('a');workspace.className='text-action';workspace.textContent='Open comparison workspace →';const link=new URL('/compare-foods.html',location.origin);link.searchParams.set('market',state.market);pair.forEach(m=>link.searchParams.append('item','order:'+(m.market||state.market)+':'+(m.id||m.chain+'||'+m.name)));workspace.href=link.href;root.querySelector('.comparison-actions').append(workspace);
      compareDialog.showModal();"""
if 'Open comparison workspace' not in s:s=s.replace(old,new);p.write_text(s,encoding='utf-8')
p=ROOT/'css/food-app.css';s=p.read_text(encoding='utf-8')
start=s.index('.food-comparison-identities{');end=s.index('.food-portion-comparison .table-wrap table',start)
replacement='''.food-comparison-identities{display:grid;grid-template-columns:minmax(0,1fr) 36px minmax(0,1fr);gap:20px;align-items:stretch;margin-block:28px}.food-comparison-identities:has(>article:only-child){grid-template-columns:minmax(0,1fr)}.food-comparison-identities>article{display:flex;flex-direction:column;min-width:0;padding:20px 0;border-block:1px solid var(--line)}.food-comparison-identities>article>span{font-size:.8rem;color:var(--muted);margin-bottom:12px}.food-comparison-identities h3{font-family:var(--display);font-size:clamp(1.15rem,2.4vw,1.65rem);line-height:1.25;overflow-wrap:anywhere;margin-bottom:12px}.food-comparison-identities p,.food-comparison-identities a{font-size:.83rem;line-height:1.6}.food-comparison-identities button{background:transparent;border:0;color:var(--green);padding:8px 0}.food-comparison-versus{align-self:center;justify-self:center;color:var(--muted);font-family:var(--display)}.comparison-food-actions{display:flex;align-items:center;flex-wrap:wrap;gap:4px 18px;margin-top:auto;padding-top:16px}.comparison-workspace .food-portion-comparison{margin-top:8px}.comparison-workspace .food-review-header{flex-wrap:wrap;gap:8px 14px}.comparison-workspace .food-review-header h2{margin-right:auto}.comparison-workspace .food-review-header button{font-size:.82rem}.comparison-add{padding-top:32px}.comparison-add h2{font-size:1.5rem}.comparison-more{display:flex;flex-wrap:wrap;gap:12px 28px;padding-block:26px}.comparison-more a{min-height:44px;display:flex;align-items:center}.food-comparison-identities+ .table-wrap td{font-variant-numeric:tabular-nums}.food-comparison-identities+ .table-wrap th:not(:first-child),.food-comparison-identities+ .table-wrap td{text-align:right}.food-comparison-identities+ .table-wrap th:first-child{width:40%}@media(max-width:550px){.food-comparison-identities{grid-template-columns:minmax(0,1fr);gap:0}.food-comparison-identities>article{padding-block:18px}.food-comparison-versus{padding-block:12px}.comparison-workspace .food-review-header h2{flex-basis:100%}.comparison-workspace .food-review-header button{min-height:44px;padding:8px 12px}.comparison-food-actions{gap:4px 14px}.comparison-more{flex-direction:column;gap:0}}'''
s=s[:start]+replacement+s[end:];p.write_text(s,encoding='utf-8')
p=ROOT/'tools/food-design.css';s=p.read_text(encoding='utf-8')
if '.home-compare-action{' not in s:s+='\n.home-compare-action{display:flex;align-items:center;min-height:44px;padding-block:8px;font-size:.8rem}.language-current-label{padding:10px;font-size:.75rem;color:var(--muted)}.contextual-tools{display:flex;flex-wrap:wrap;gap:12px 28px;padding-block:26px;border-top:1px solid var(--line)}.contextual-tools a{display:flex;align-items:center;min-height:44px}.compare-workspace-link{font-size:.75rem}.meal-actions{flex-wrap:wrap}\n';p.write_text(s,encoding='utf-8')
print('Source migration applied: source-based comparison links, centered identities, explicit tool paths.')
p=ROOT/'js/food-experience.js';s=p.read_text(encoding='utf-8')
start=s.find(" const ensemble=document.querySelector('.food-ensemble');")
if start>=0:
    end=s.index('portionExample();calculator();',start);s=s[:start]+' portionExample();calculator();'+s[end+len('portionExample();calculator();'):];p.write_text(s,encoding='utf-8')
p=ROOT/'css/markets.css';s=p.read_text(encoding='utf-8');needle='.language-picker{grid-column:3/5;grid-row:2;justify-self:end}'
if '.language-current-label{grid-column:3/5;' not in s:s=s.replace(needle,needle+'.language-current-label{grid-column:3/5;grid-row:2;justify-self:end;padding:4px 8px;min-height:36px;display:flex;align-items:center}');p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-portion-compare.js';s=p.read_text(encoding='utf-8')
if 'let editing=null' not in s:
    s=s.replace('let items=[];try{items=C.read(localStorage);}catch{}','let items=[];let editing=null;try{items=C.read(localStorage);}catch{}')
    s=s.replace("edit.addEventListener('click',()=>UI.review(F.fromSnapshot(s),{quantity:s.quantity,measure:s.measure}));","edit.addEventListener('click',()=>{editing={index:i,recordId:s.recordId};UI.review(F.fromSnapshot(s),{quantity:s.quantity,measure:s.measure});});")
    s=s.replace('items=C.add(items,snapshot);document.querySelector',"if(editing&&editing.recordId===snapshot.recordId){const next=[...items];next[editing.index]=snapshot;items=C.validate(next);}else items=C.add(items,snapshot);editing=null;document.querySelector")
    s=s.replace('render();\nconst params=',"document.querySelector('#food-review').addEventListener('close',()=>{editing=null;});render();\nconst params=")
    p.write_text(s,encoding='utf-8')

p=ROOT/'js/food-library.js';s=p.read_text(encoding='utf-8');s=s.replace('const {index}=await load();const item=index.find','const {index}=await load();if(cache.has(id))return cache.get(id);const item=index.find');p.write_text(s,encoding='utf-8')
for name in ['all-routes.cjs','performance.cjs']:
    p=ROOT/'tools/clarity_release'/name;s=p.read_text(encoding='utf-8').replace('docs/master-completion-2026-10-13','docs/clarity-release-2026-10-14')
    if name=='performance.cjs':s=s.replace('fe5db6432ca7857180dfa0ecbea1799ad149a764','a6a8b9da780915871c05df0fb5843226e00d76e5')
    p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-portion-compare.js';s=p.read_text(encoding='utf-8')
s=s.replace("s.quantity+' '+s.portionLabel","F.formatPortion(s)")
s=s.replace("s.status+' · '+(s.sourceOrigin||s.sourceId)","sourceStatus(s)+' · '+(s.sourceOrigin||s.sourceId)")
if 'function sourceStatus(s)' not in s:
    s=s.replace('function node(tag,text)',"function sourceStatus(s){if(s.sourceId?.startsWith('off-'))return 'Imported Open Food Facts record';if(s.status?.includes('calculated'))return 'Calculated from source values';if(s.status?.includes('retailer'))return 'Online retailer label';if(s.status?.includes('official'))return 'Official source record';return 'Source-linked portion';}\nfunction node(tag,text)")
if 'Source notes & attribution' not in s:
    s=s.replace("const actions=node('div');actions.className='comparison-food-actions';", "const notes=node('details');notes.append(node('summary','Source notes & attribution'));for(const value of [s.attribution,...(s.flags||[])].filter(Boolean))notes.append(node('p',value));notes.append(node('p','Source status: '+s.status+' · '+(s.sourceChecked?'Checked '+s.sourceChecked:'Check date unavailable')+(s.retrievedAt?' · Retrieved '+s.retrievedAt:'')));if(s.licenseUrl){const license=node('a',s.license||'Source license');license.href=s.licenseUrl;notes.append(license);}article.append(notes);const actions=node('div');actions.className='comparison-food-actions';")
p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-app.js';s=p.read_text(encoding='utf-8').replace("s.quantity+' '+s.portionLabel","F.formatPortion(s)");p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-app.js';s=p.read_text(encoding='utf-8')
if 'log.setAttribute' not in s:
    s=s.replace("const n=F.scale(selected,Number(form.elements.quantity.value),form.elements.measure.value);", "const n=F.scale(selected,Number(form.elements.quantity.value),form.elements.measure.value);const log=form.querySelector('[data-review-log]');log.href='/food-diary.html?'+new URLSearchParams({food:selected.id,market:definitions()[selected.market]?selected.market:market(),quantity:form.elements.quantity.value,measure:form.elements.measure.value});log.removeAttribute('aria-disabled');log.tabIndex=0;")
    s=s.replace("}catch(e){form.querySelector('[data-review-error]').textContent=e.message;", "}catch(e){const log=form.querySelector('[data-review-log]');log.removeAttribute('href');log.setAttribute('aria-disabled','true');log.tabIndex=-1;form.querySelector('[data-review-error]').textContent=e.message;")
if "publicParams.get('q')" not in s:
    s=s.replace("syncSource();search().catch(error);}}const linked=", "syncSource();search().catch(error);}else{const q=publicParams.get('q'),type=publicParams.get('type');if(q&&q.length<=150){query.value=q;if(['restaurant','branded','reference'].includes(type))root.querySelector('[data-food-type]').value=type;syncSource();search().catch(error);}}}const linked=")
p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-library.js';s=p.read_text(encoding='utf-8');s=s.replace('await cache.get(key);return cache.get(id);',"await cache.get(key);const record=cache.get(id);if(!record)throw Error('That food is unavailable in this source edition. Search for another record.');return record;");p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-portion-compare.js';s=p.read_text(encoding='utf-8')
if 'C.readBasis' not in s:
    s=s.replace("function persist(){try{C.write(localStorage,items);}","function persist(){try{C.write(localStorage,items);C.writeBasis(localStorage,basis.value);}")
    s=s.replace("basis.addEventListener('change',render);","basis.addEventListener('change',()=>{render();persist();});")
    s=s.replace("});render();\nconst params=","});basis.value=C.readBasis(localStorage);render();\nconst params=")
    s=s.replace("editing={index:i,recordId:s.recordId};","editing={index:i,recordId:s.recordId,identity:JSON.stringify([s.recordId,s.version,s.name,s.quantity,s.measure])};")
    s=s.replace("if(editing&&editing.recordId===snapshot.recordId){const next=", "if(editing&&editing.recordId===snapshot.recordId){const current=items[editing.index];if(!current||JSON.stringify([current.recordId,current.version,current.name,current.quantity,current.measure])!==editing.identity)throw Error('The comparison changed while you were reviewing. Close this review and choose the current food.');const next=")
    s=s.replace("}catch(e){status.textContent=e.message;}});", "}catch(e){status.textContent=e.message;document.querySelector('[data-review-error]').textContent=e.message;}});")
    s=s.replace("if(ids.length){status.textContent=", "if(ids.length){content.hidden=true;basis.disabled=true;share.disabled=true;download.disabled=true;root.querySelector('[data-food-compare-clear]').disabled=true;status.textContent=")
    s=s.replace("basis.value=params.get('basis')==='100g'?'100g':'portions';", "basis.value=params.has('basis')?(params.get('basis')==='100g'?'100g':'portions'):C.readBasis(localStorage);")
    s=s.replace(".finally(()=>root.removeAttribute('aria-busy'))", ".finally(()=>{root.removeAttribute('aria-busy');content.hidden=false;share.disabled=false;download.disabled=false;root.querySelector('[data-food-compare-clear]').disabled=false;})")
p.write_text(s,encoding='utf-8')
p=ROOT/'tools/build_clarity_release.py';s=p.read_text(encoding='utf-8').replace('food-library.html?market=CA&amp;brand=Triple+O%E2%80%99s','food-library.html?market=CA&amp;type=restaurant&amp;q=Triple+O%E2%80%99s');p.write_text(s,encoding='utf-8')
p=ROOT/'js/food-portion-compare.js';s=p.read_text(encoding='utf-8').replace("const countryName=code=>(window.GM_MARKETS||{})[code]?.name||code;", "const countryName=code=>(window.GM_MARKETS||{})[code]?.name||({'US-reference':'U.S. food-composition reference','CA-reference':'Canadian food-composition reference'}[code])||code;");p.write_text(s,encoding='utf-8')
