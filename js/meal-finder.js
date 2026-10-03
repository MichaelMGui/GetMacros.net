/* Meal discovery: filters remain mounted while results change. Guided discovery and direct browsing use the same engine. */
(function () {
  'use strict';
  const root = document.getElementById('meal-quiz');
  if (!root) return;
  const meals = window.GM_MEALS || [], T = window.GM_THRESHOLDS, E=window.GetMacrosMeals;
  const track=name=>window.GetMacrosEvents?.emit(name);
  if (!meals.length || !T || !E) {
    root.innerHTML='<p role="alert">The meal finder could not load. <a href="restaurant-meal-finder.html">Try again</a> or use the restaurant list below.</p>';
    return;
  }
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const restaurantMarks={"CAVA":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 11h18a9 9 0 0 1-18 0Zm4 9h10M7 8c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5\"/></svg></span>","Chick-fil-A":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M8 15c-4-2-4-7-1-10s8-3 10 0 1 7-3 9l-3 1-4 4a2 2 0 1 1-3-3l4-1Zm3-8 3-1\"/></svg></span>","Chipotle":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 11h18a9 9 0 0 1-18 0Zm4 9h10M7 8c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5\"/></svg></span>","Dunkin’":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M5 8h12v9a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V8Zm12 1h2a3 3 0 0 1 0 6h-2M8 5V2m5 3V2M3 22h17\"/></svg></span>","Jersey Mike’s":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m4 10 10-6a4 4 0 0 1 5 6L9 17a4 4 0 0 1-5-7Zm0 5 1 4a4 4 0 0 0 5 1l10-7 1-4M9 7l3 2m2-5 3 2M6 13l3 1 3-3 3 1 3-3\"/></svg></span>","KFC":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M8 15c-4-2-4-7-1-10s8-3 10 0 1 7-3 9l-3 1-4 4a2 2 0 1 1-3-3l4-1Zm3-8 3-1\"/></svg></span>","McDonald’s":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 9c0-4 4-6 9-6s9 2 9 6H3Zm0 6h18v2a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-2Zm0-3 4 1 5-1 5 1 4-1M8 6h.01M12 5h.01M16 6h.01\"/></svg></span>","Panda Express":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 11h18a9 9 0 0 1-18 0Zm4 9h10M7 8c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5m5 5c-2-2 2-3 0-5\"/></svg></span>","Panera":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m4 10 10-6a4 4 0 0 1 5 6L9 17a4 4 0 0 1-5-7Zm0 5 1 4a4 4 0 0 0 5 1l10-7 1-4M9 7l3 2m2-5 3 2M6 13l3 1 3-3 3 1 3-3\"/></svg></span>","Popeyes":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M8 15c-4-2-4-7-1-10s8-3 10 0 1 7-3 9l-3 1-4 4a2 2 0 1 1-3-3l4-1Zm3-8 3-1\"/></svg></span>","Starbucks":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M5 8h12v9a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V8Zm12 1h2a3 3 0 0 1 0 6h-2M8 5V2m5 3V2M3 22h17\"/></svg></span>","Subway":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"m4 10 10-6a4 4 0 0 1 5 6L9 17a4 4 0 0 1-5-7Zm0 5 1 4a4 4 0 0 0 5 1l10-7 1-4M9 7l3 2m2-5 3 2M6 13l3 1 3-3 3 1 3-3\"/></svg></span>","Sweetgreen":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M5 16C2 6 13 3 20 4c0 9-4 16-12 14m-4 3L16 9m-7 7V9m4 3h5\"/></svg></span>","Taco Bell":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 19a9 9 0 0 1 18 0H3Zm3-2 2-2 3 1 3-2 3 2m-9-5 1 1m5-2 1 1\"/></svg></span>","Wendy’s":"<span class=\"restaurant-mark\" aria-hidden=\"true\"><svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M3 9c0-4 4-6 9-6s9 2 9 6H3Zm0 6h18v2a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3v-2Zm0-3 4 1 5-1 5 1 4-1M8 6h.01M12 5h.01M16 6h.01\"/></svg></span>"};
  function restaurantMark(chain){return restaurantMarks[chain]||"";}
  const chains = [...new Set(meals.map(m=>m.chain))].sort((a,b)=>a.localeCompare(b));
  const facets = {
    goal:[['protein','More protein'],['light','Fewer calories'],['energy','A bigger meal'],['fibre','More fiber'],['lowsodium','Less sodium']],
    chain:chains.map(c=>[c,c]),
    diet:[['vegetarian','Vegetarian'],['plant','Plant-based']],
    meal:[['main','Lunch / dinner'],['breakfast','Breakfast']],
    size:[['small','Small'],['medium','Regular'],['large','Large']]
  };
  const limits=E.limits;
  const pageSize=root.hasAttribute('data-home-preview')?4:12;
  let visible=pageSize,selected=[],saved=[],savedOnly=false;
  try {const s=JSON.parse(localStorage.getItem('getmacros-saved-meals-v1')||'[]');if(Array.isArray(s))saved=s;}catch(e){}
  const key=E.key,complete=E.complete;
  let state=E.fromSearch(location.search,meals);
  selected=new URLSearchParams(location.search).getAll('compare').map(k=>meals.findIndex(m=>key(m)===k)).filter(i=>i>=0).slice(0,3);
  savedOnly=new URLSearchParams(location.search).get('view')==='saved';
  function readState(){return E.fromSearch(location.search,meals);}
  function syncUrl(){const url=new URL(location.href);url.search=E.toSearch(state).toString();if(savedOnly)url.searchParams.set('view','saved');history.replaceState(null,'',url);}
  function choices(k){return facets[k].map(([v,label])=>'<label class="finder-choice"><input type="checkbox" name="'+k+'" value="'+esc(v)+'"'+(state[k].includes(v)?' checked':'')+'>'+(k==='chain'?restaurantMark(v):'')+'<span>'+esc(label)+'</span></label>').join('');}
  function field(k){return '<label>'+limits[k][2]+'<input type="number" name="'+k+'" min="'+limits[k][0]+'" max="'+limits[k][1]+'" step="1" inputmode="numeric" placeholder="Any" value="'+(state[k]??'')+'"></label>';}
  root.innerHTML=`<div class="discovery-paths"><div><h2>Find your next order</h2><p>Use a few questions or go straight to the meals.</p></div><div class="discovery-path-actions"><button type="button" class="btn btn-primary" data-open-guide>Help me choose</button><button type="button" class="btn" data-browse aria-pressed="true">Browse meals</button><button type="button" class="quiet-button" data-show-saved aria-pressed="${savedOnly}">Saved meals</button></div></div><div class="discovery-product"><div class="finder-sidebar filter-deck"><form id="finder-filters"><div class="filter-panel-head"><h2>Filter meals</h2><button type="button" data-close-filters>Done</button></div><div class="filter-primary"><fieldset><legend>Nutrition limits</legend>${field('maxCal')}${field('minProtein')}</fieldset><details class="restaurant-picker"><summary><span>Choose restaurants</span></summary><div class="restaurant-checks">${choices('chain')}</div></details></div><details class="filter-more"><summary>More preferences </summary><div class="filter-expanded"><fieldset><legend>Bring these meals to the top</legend>${choices('goal')}<p class="filter-note">Preferences change the order. Nutrition limits exclude meals.</p></fieldset><fieldset><legend>Food &amp; meal time</legend>${choices('diet')}${choices('meal')}<p class="filter-note">Ingredient preferences are not allergy-safety checks. Ask the restaurant.</p></fieldset><fieldset><legend>Other nutrients</legend>${field('minFiber')}${field('maxSodium')}<label>Preferred size<select name="size"><option value="">Any size</option>${facets.size.map(([v,l])=>'<option value="'+v+'"'+(state.size[0]===v?' selected':'')+'>'+l+'</option>').join('')}</select></label><label class="finder-choice"><input type="checkbox" name="incomplete"${!state.complete?' checked':''}><span>Include incomplete records</span></label></fieldset></div></details><div class="filter-reset"><button type="reset" class="quiet-button">Reset filters</button></div></form></div><div class="finder-results"><div class="finder-toolbar"><div><p class="results-count" role="status" aria-live="polite"></p></div><button type="button" class="filter-launch" data-open-filters>Adjust filters <span data-filter-count></span></button><label class="sort-label">Order by<select name="sort"><option value="match">Preference order</option><option value="calories">Lowest calories</option><option value="protein">Most protein</option></select></label></div><div class="active-preferences" aria-label="Active filters"></div><div class="results-grid"></div><button type="button" class="btn results-more" data-more>Show more meals</button><div class="finder-end"><a class="btn home-all-results" href="restaurant-meal-finder.html">Browse all matching meals</a><p>U.S. menu data. Portions, sauces and local recipes may change the numbers. <a href="sources.html">About our data</a></p><button type="button" data-share>Share results</button><button type="button" data-print>Print meals</button><p data-share-status role="status"></p></div></div></div><div class="compare-tray" hidden><span data-compare-count></span><button type="button" class="btn btn-primary" data-open-compare>Compare meals</button><button type="button" data-clear-compare>Clear</button></div><dialog class="compare-dialog" aria-labelledby="compare-title"><div class="dialog-heading"><h2 id="compare-title">Your meals, side by side</h2><button type="button" data-close-compare>Close</button></div><div class="comparison-output" tabindex="0" role="region" aria-label="Meal comparison"></div></dialog><dialog class="filter-dialog" aria-label="Meal filters"></dialog><dialog class="guided-dialog" aria-labelledby="guide-title"></dialog>`;
  const form=root.querySelector('#finder-filters'),resultList=root.querySelector('.results-grid'),filterDialog=root.querySelector('.filter-dialog'),compareDialog=root.querySelector('.compare-dialog');
  root.querySelector('[name=sort]').value=state.sort;
  function number(v,unit=''){return Number.isFinite(v)?v.toLocaleString()+(unit?' '+unit:''):'Not verified';}
  function provenanceNote(m){
    if(!m.nutrientProvenance)return '';
    return '<ul class="nutrient-provenance">'+[['cal','Calories'],['p','Protein'],['c','Carbs'],['fat','Fat'],['f','Fiber'],['na','Sodium']].map(([k,label])=>{const r=m.nutrientProvenance[k];if(!r)return '';return '<li>'+label+': '+esc(r.method==='calculated'?'sum of listed components':'published')+' · '+esc(r.retrieved||m.checked)+(r.status?' · '+esc(r.status):'')+'</li>';}).join('')+'</ul>';
  }
  function mealRow(m){
    const id=meals.indexOf(m);
    return `<article class="order-ticket meal-row" data-meal-id="${id}">
      <header class="order-identity"><a href="${esc(m.url)}">${restaurantMark(m.chain)}<span>${esc(m.chain)}</span></a><button type="button" data-save="${id}" aria-pressed="${saved.includes(key(m))}">${saved.includes(key(m))?'Saved':'Save meal'}</button></header>
      <div class="order-heading"><h2>${esc(m.name.replace('High-protein bulking order: ',''))}</h2><p>${esc(m.serving||'1 listed order')} · ${esc(m.region||'U.S.')} menu</p></div>
      <dl class="order-nutrition meal-numbers"><div class="order-major"><dt>Calories</dt><dd>${number(m.cal)}</dd></div><div class="order-major"><dt>Protein</dt><dd>${number(m.p,'g')}</dd></div><div><dt>Carbs</dt><dd>${number(m.c,'g')}</dd></div><div><dt>Fat</dt><dd class="${!Number.isFinite(m.fat)?'unknown':''}">${number(m.fat,'g')}</dd></div></dl>
      <div class="order-included"><p>${esc(m.why)}</p>${matchNote(m)}</div>
      <footer class="order-actions"><details><summary>Details &amp; source</summary><p>Fiber: ${number(m.f,'g')} · Sodium: ${number(m.na,'mg')}.</p><p>Extras are separate unless listed above. Unverified values are not zero.</p>${m.source?'<p><a href="'+esc(m.source)+'">Official nutrition source</a> · Source inspected '+esc(m.checked)+'. '+esc(m.notes||'')+'</p>':'<p>Source details are unavailable.</p>'}${provenanceNote(m)}<a href="${esc(m.url)}">Restaurant menu</a></details><label class="compare-choice"><input type="checkbox" data-compare="${id}"${selected.includes(id)?' checked':''}>Compare meal</label></footer>
    </article>`;
  }
  function matchNote(m){const notes=[];if(state.maxCal!==null)notes.push('Within your calorie limit');if(state.minProtein!==null)notes.push('Meets your protein minimum');if(state.minFiber!==null)notes.push('Meets your fiber minimum');if(state.maxSodium!==null)notes.push('Within your sodium limit');return notes.length?'<p class="match-facts">'+notes.map(esc).join(' · ')+'</p>':'';}
  function activeFilters(){
    root.querySelector('.restaurant-picker summary span').textContent=state.chain.length ? state.chain.length+' restaurant'+(state.chain.length===1?'':'s')+' selected' : 'Choose restaurants';
    let chips=[];
    Object.keys(facets).forEach(k=>state[k].forEach(v=>chips.push({k,v,label:facets[k].find(o=>o[0]===v)[1]})));
    Object.keys(limits).forEach(k=>{if(state[k]!==null)chips.push({k,v:'',label:limits[k][2]+': '+state[k]});});
    if(!state.complete)chips.push({k:'complete',v:'',label:'Incomplete records included'});
    root.querySelector('.active-preferences').innerHTML=chips.map(c=>'<button type="button" data-remove="'+c.k+'" data-value="'+esc(c.v)+'" aria-label="Remove '+esc(c.label)+'">'+esc(c.label)+' <span aria-hidden="true">×</span></button>').join('');
    root.querySelector('[data-filter-count]').textContent=chips.length?'('+chips.length+')':'';
  }
  function render(){
    root.querySelector('.finder-complete-note')?.remove();
    const results=E.results(meals,state).filter(m=>!savedOnly||saved.includes(key(m)));
    root.querySelector('.results-count').textContent=results.length+' meal'+(results.length===1?'':'s')+' match';
    resultList.innerHTML=results.length?results.slice(0,visible).map(mealRow).join(''):'<section class="finder-empty"><span data-food-character="pear" data-character-size="100" aria-hidden="true"></span><h2>'+ (savedOnly?'No saved meals match.':'No meals match these limits.')+'</h2><p>'+ (savedOnly?'Save an order with the Save meal button, or return to all meals.':'Your limits are unchanged. Remove an active filter above or choose different limits. Incomplete records need known values for any nutrient you filter.')+'</p><button type="button" data-reset>Clear filters</button></section>';
    root.querySelector('[data-more]').hidden=results.length<=visible;
    root.querySelector('[data-more]').textContent='Show '+Math.min(12,results.length-visible)+' more meals';
    activeFilters();syncUrl();updateTray();
    root.querySelector('[data-show-saved]').setAttribute('aria-pressed',savedOnly);
    root.querySelector('[data-browse]').setAttribute('aria-pressed',!savedOnly);
    root.querySelector('.home-all-results').href='restaurant-meal-finder.html'+(E.toSearch(state).toString()?'?'+E.toSearch(state):'');
    root.querySelector('.home-all-results').hidden=!root.hasAttribute('data-home-preview');
    window.GetMacrosCharacters?.enhance(root);
    root.querySelector('[data-share-status]').textContent='';
  }
  function controlsFromState(){
    Object.keys(facets).forEach(k=>form.querySelectorAll('input[name="'+k+'"]').forEach(el=>el.checked=state[k].includes(el.value)));
    Object.keys(limits).forEach(k=>form.elements[k].value=state[k]??'');
    form.elements.size.value=state.size[0]||'';form.elements.incomplete.checked=!state.complete;
    root.querySelector('[name=sort]').value=state.sort;
  }
  function clear(){Object.keys(facets).forEach(k=>state[k]=[]);Object.keys(limits).forEach(k=>state[k]=null);state.complete=true;state.sort='match';savedOnly=false;visible=pageSize;controlsFromState();render();}
  function updateTray(){
    root.querySelector('.compare-tray').hidden=!selected.length;
    root.querySelector('[data-compare-count]').textContent=selected.length+' of 3 meals selected';
    root.querySelector('[data-open-compare]').disabled=selected.length<2;
    root.querySelectorAll('[data-compare]').forEach(el=>{el.checked=selected.includes(Number(el.dataset.compare));el.disabled=selected.length===3&&!el.checked;});
  }
  form.addEventListener('submit',e=>e.preventDefault());
  form.addEventListener('reset',e=>{e.preventDefault();clear();});
  root.addEventListener('change',e=>{
    const el=e.target,k=el.name;
    if(el.closest('.guided-dialog'))return;
    if(el.hasAttribute('data-compare')){const id=Number(el.dataset.compare);selected=el.checked?[...selected,id].slice(0,3):selected.filter(v=>v!==id);updateTray();return;}
    if(limits[k]){if(!el.reportValidity())return;state[k]=el.value===''?null:Number(el.value);}
    else if(k==='sort')state.sort=el.value;
    else if(k==='incomplete')state.complete=!el.checked;
    else if(k==='size')state.size=el.value?[el.value]:[];
    else if(facets[k])state[k]=Array.from(form.querySelectorAll('input[name="'+k+'"]:checked'),n=>n.value);
    else return;
    visible=pageSize;render();track('filters_applied');
  });
  root.addEventListener('click',async e=>{
    const el=e.target.closest('button');if(!el)return;
    if(el.hasAttribute('data-open-guide'))openGuide();
    if(el.hasAttribute('data-browse')){savedOnly=false;render();root.querySelector('[name=sort]').focus();track('finder_started');}
    if(el.hasAttribute('data-show-saved')){savedOnly=!savedOnly;render();track('finder_started');}
    if(el.hasAttribute('data-more')){visible+=12;render();}
    if(el.hasAttribute('data-reset'))clear();
    if(el.hasAttribute('data-remove')){const k=el.dataset.remove;if(facets[k])state[k]=state[k].filter(v=>v!==el.dataset.value);else if(k==='complete')state.complete=true;else state[k]=null;controlsFromState();render();root.querySelector('[name=sort]').focus({preventScroll:true});}
    if(el.hasAttribute('data-save')){const m=meals[Number(el.dataset.save)],id=key(m);saved=saved.includes(id)?saved.filter(v=>v!==id):[...saved,id];try{localStorage.setItem('getmacros-saved-meals-v1',JSON.stringify(saved));}catch(e){}el.textContent=saved.includes(id)?'Saved':'Save meal';el.setAttribute('aria-pressed',saved.includes(id));if(savedOnly)render();}
    if(el.hasAttribute('data-open-filters')){filterDialog.append(form);filterDialog.showModal();}
    if(el.hasAttribute('data-close-filters'))filterDialog.close();
    if(el.hasAttribute('data-clear-compare')){selected=[];updateTray();}
    if(el.hasAttribute('data-open-compare')){
      const pair=selected.map(i=>meals[i]);track('comparison_used');
      root.querySelector('.comparison-output').innerHTML='<table><caption>Per listed order. Unknown values are not zero.</caption><thead><tr><td>Nutrient</td>'+pair.map(m=>'<th scope="col">'+esc(m.chain)+'<strong>'+esc(m.name)+'</strong><small>'+esc(m.serving||'1 listed order')+' · '+esc(m.region||'U.S.')+'</small></th>').join('')+'</tr></thead><tbody>'+[['cal','Calories',''],['p','Protein','g'],['c','Carbs','g'],['fat','Fat','g'],['f','Fiber','g'],['na','Sodium','mg']].map(([k,l,u])=>'<tr><th scope="row">'+l+'</th>'+pair.map(m=>'<td>'+number(m[k],u)+'</td>').join('')+'</tr>').join('')+'</tbody></table><div class="comparison-notes">'+pair.map(m=>'<div><h3>'+esc(m.chain)+'</h3><p>'+esc(m.why)+'</p>'+(m.source?'<a href="'+esc(m.source)+'">Official source</a>':'')+'</div>').join('')+'</div><div class="comparison-actions"><button type="button" class="btn" data-share-comparison>Share comparison</button><button type="button" data-print>Print comparison</button></div><p data-comparison-status role="status"></p>';
      compareDialog.showModal();
    }
    if(el.hasAttribute('data-close-compare'))compareDialog.close();
    if(el.hasAttribute('data-print'))window.print();
    if(el.hasAttribute('data-share')||el.hasAttribute('data-share-comparison')){
      const url=new URL('restaurant-meal-finder.html',location.href);url.search=E.toSearch(state).toString();
      const comparison=el.hasAttribute('data-share-comparison');if(comparison)selected.forEach(i=>url.searchParams.append('compare',key(meals[i])));
      const status=root.querySelector(comparison?'[data-comparison-status]':'[data-share-status]');
      try{await navigator.clipboard.writeText(url.href);status.textContent=comparison?'Comparison link copied.':'Result link copied.';}catch{status.replaceChildren();const label=document.createElement('label');label.textContent='Copy this link';const input=document.createElement('input');input.readOnly=true;input.setAttribute("aria-label",comparison?"Comparison link":"Results link");input.value=url.href;label.append(input);status.append(label);input.focus();input.select();}track('share_action');
    }
  });
  filterDialog.addEventListener('close',()=>{root.querySelector('.finder-sidebar').append(form);root.querySelector('[data-open-filters]').focus({preventScroll:true});});
  const guide=root.querySelector('.guided-dialog');let guideStep=0,guideReturn=null;
  const guideNames=['Priorities','Restaurants','Nutrition limits','Meal preferences'];
  function guideFields(){return `<div class="dialog-heading"><h2 id="guide-title">Help me choose</h2><button type="button" data-guide-close>Close</button></div><div class="guided-intro"><span data-food-character="avocado" data-character-size="90" aria-hidden="true"></span><p>Four short steps. Optional choices can stay blank.</p></div><ol class="guided-progress">${guideNames.map((name,i)=>'<li data-guide-progress="'+i+'"><span>'+(i+1)+'</span>'+name+'</li>').join('')}</ol><form id="guided-form"><fieldset data-guide-step="0"><legend tabindex="-1">What matters most?</legend><p>These preferences change the order of your matches. Set firm limits in step 3.</p><div class="guided-choices">${choices('goal')}</div></fieldset><fieldset data-guide-step="1" hidden><legend tabindex="-1">Where would you like to eat?</legend><p>Choose one or more. Leave all unselected for any restaurant.</p><div class="guided-restaurants">${choices('chain')}</div></fieldset><fieldset data-guide-step="2" hidden><legend tabindex="-1">Any calorie or protein limits?</legend><p>Leave either blank if you have no limit. Your limits will be kept exactly.</p><div class="guided-limits">${field('maxCal')}${field('minProtein')}</div></fieldset><fieldset data-guide-step="3" hidden><legend tabindex="-1">Anything else?</legend><p>Optional ingredient and meal choices. These are not allergy checks.</p><div class="guided-choices">${choices('diet')}${choices('meal')}</div><div class="guided-limits">${field('minFiber')}${field('maxSodium')}</div><label class="finder-choice"><input type="checkbox" name="incomplete"${!state.complete?' checked':''}><span>Include records with missing nutrients</span></label></fieldset><p class="guide-validation" role="alert"></p><div class="guide-actions"><button type="button" data-guide-back>Back</button><button type="button" class="quiet-button" data-guide-skip>Skip this step</button><button type="submit" class="btn btn-primary" data-guide-next>Next</button></div></form>`;}
  function openGuide(){guideReturn=document.activeElement;guideStep=0;guide.innerHTML=guideFields();guide.showModal();window.GetMacrosCharacters?.enhance(guide);paintGuide(false);track('finder_started');}
  function paintGuide(focus=true){guide.querySelectorAll('[data-guide-step]').forEach((f,i)=>f.hidden=i!==guideStep);guide.querySelectorAll('[data-guide-progress]').forEach((li,i)=>{li.classList.toggle('is-current',i===guideStep);if(i===guideStep)li.setAttribute('aria-current','step');else li.removeAttribute('aria-current');});guide.querySelector('[data-guide-back]').hidden=guideStep===0;guide.querySelector('[data-guide-next]').textContent=guideStep===3?'Show my meals':'Next';guide.querySelector('[data-guide-skip]').textContent=guideStep===3?'Use these choices':'Skip this step';guide.querySelector('.guide-validation').textContent='';if(focus)guide.querySelector('[data-guide-step="'+guideStep+'"] legend').focus({preventScroll:true});}
  function advanceGuide(){const current=guide.querySelector('[data-guide-step="'+guideStep+'"]');const invalid=[...current.querySelectorAll('input')].find(i=>!i.checkValidity());if(invalid){guide.querySelector('.guide-validation').textContent='Check '+(invalid.closest('label')?.textContent.trim()||'this value')+'. Use the allowed range or leave it blank.';invalid.reportValidity();invalid.focus();return;}if(guideStep<3){guideStep++;paintGuide();return;}
    const guidedForm=guide.querySelector('form'),data=new FormData(guidedForm),draft={sort:state.sort,complete:!data.has('incomplete')};Object.keys(facets).forEach(k=>draft[k]=data.getAll(k));draft.size=state.size;Object.keys(limits).forEach(k=>draft[k]=data.get(k));state=E.normalize(draft,meals);savedOnly=false;visible=pageSize;controlsFromState();render();guide.close();root.querySelector('[name=sort]').focus({preventScroll:true});const note=document.createElement('p');note.className='finder-complete-note';note.innerHTML='<span data-food-character="orange" aria-hidden="true"></span><span>Your choices are applied. Compare the portions below.</span>';root.querySelector('.finder-toolbar').after(note);window.GetMacrosCharacters?.enhance(note);track('quiz_completed');
  }
  guide.addEventListener('submit',e=>{e.preventDefault();advanceGuide();});
  guide.addEventListener('click',e=>{const button=e.target.closest('button');if(!button)return;if(button.hasAttribute('data-guide-close'))guide.close();if(button.hasAttribute('data-guide-back')){guideStep=Math.max(0,guideStep-1);paintGuide();}if(button.hasAttribute('data-guide-skip'))advanceGuide();});
  guide.addEventListener('close',()=>{if(guideReturn?.isConnected&&document.activeElement===document.body)guideReturn.focus({preventScroll:true});});
  const restaurantPicker=root.querySelector('.restaurant-picker');
  document.addEventListener('click',e=>{if(restaurantPicker.open&&!restaurantPicker.contains(e.target))restaurantPicker.open=false;});
  restaurantPicker.addEventListener('keydown',e=>{if(e.key==='Escape'&&restaurantPicker.open){e.preventDefault();e.stopPropagation();restaurantPicker.open=false;restaurantPicker.querySelector('summary').focus();}});
  compareDialog.addEventListener('close',()=>root.querySelector('[data-open-compare]').focus({preventScroll:true}));
  const mobile=matchMedia('(max-width: 800px)');mobile.addEventListener('change',e=>{if(!e.matches&&filterDialog.open)filterDialog.close();});
  addEventListener('popstate',()=>{state=readState();controlsFromState();visible=pageSize;render();});
  root.dataset.ready='true';render();if(selected.length>=2)root.querySelector('[data-open-compare]').click();
})();
