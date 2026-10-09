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
  const V=window.GetMacrosMealView;
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
  let expectedSnapshots=new URLSearchParams(location.search).getAll('snapshot').slice(0,3);
  savedOnly=new URLSearchParams(location.search).get('view')==='saved';
  function readState(){return E.fromSearch(location.search,meals);}
  function syncUrl(){const url=new URL(location.href);url.search=E.toSearch(state).toString();if(savedOnly)url.searchParams.set('view','saved');history.replaceState(null,'',url);}
  if(!root.querySelector("#finder-filters"))root.innerHTML=V.shell(meals,state,E,{savedOnly});
  let firstRender=true;
  const form=root.querySelector('#finder-filters'),resultList=root.querySelector('.results-grid'),filterDialog=root.querySelector('.filter-dialog'),compareDialog=root.querySelector('.compare-dialog');
  root.querySelector('[name=sort]').value=state.sort;
  function number(v,unit=''){return Number.isFinite(v)?v.toLocaleString()+(unit?' '+unit:''):'Not verified';}
  function mealRow(m){const id=meals.indexOf(m);return V.card(m,id,{saved:saved.includes(key(m)),selected:selected.includes(id),state});}
  function activeFilters(){
    root.querySelector('.restaurant-picker summary span').textContent=state.chain.length ? state.chain.length+' restaurant'+(state.chain.length===1?'':'s')+' selected' : 'Choose restaurants';
    let chips=[];
    Object.keys(facets).forEach(k=>state[k].forEach(v=>chips.push({k,v,label:facets[k].find(o=>o[0]===v)[1]})));
    Object.keys(limits).forEach(k=>{if(state[k]!==null)chips.push({k,v:'',label:limits[k][2]+': '+state[k]});});
    if(!state.complete)chips.push({k:'complete',v:'',label:'Items with missing macros included'});
    root.querySelector('.active-preferences').innerHTML=chips.map(c=>'<button type="button" data-remove="'+c.k+'" data-value="'+esc(c.v)+'" aria-label="Remove '+esc(c.label)+'">'+esc(c.label)+' <span aria-hidden="true">×</span></button>').join('');
    root.querySelector('[data-filter-count]').textContent=chips.length?'('+chips.length+')':'';
  }
  function render(){
    root.querySelector('.finder-complete-note')?.remove();
    const previous=new Map([...resultList.querySelectorAll('[data-meal-id]')].map(n=>[n.dataset.mealId,n.getBoundingClientRect()]));
    const results=E.results(meals,state).filter(m=>!savedOnly||saved.includes(key(m)));
    root.querySelector('[data-surprise]').disabled=!results.length;
    root.querySelector('.results-count').textContent=results.length+' '+(state.market==='CA'?'item':'meal')+(results.length===1?'':'s')+' match';
    const retain=firstRender&&!saved.length&&[...resultList.querySelectorAll("[data-meal-id]")].map(n=>Number(n.dataset.mealId)).join(",")===results.slice(0,visible).map(m=>meals.indexOf(m)).join(",");firstRender=false;
    if(!retain)resultList.innerHTML=results.length?results.slice(0,visible).map(mealRow).join(''):'<section class="finder-empty"><span data-food-character="pear" data-character-size="100" aria-hidden="true"></span><h2>'+ (savedOnly?'No saved meals match.':'No meals match these limits.')+'</h2><p>'+ (savedOnly?'Save an order with the Save meal button, or return to all meals.':'Your limits are unchanged. Remove an active filter above or choose different limits. Incomplete records need known values for any nutrient you filter.')+'</p><button type="button" data-reset>Clear filters</button></section>';
    if(!results.length&&state.complete){const partial=E.results(meals,{...state,complete:false}).filter(m=>!savedOnly||saved.includes(key(m)));if(partial.length)resultList.innerHTML='<section class="finder-empty"><h2>Matching orders have missing macros.</h2><p>'+partial.length+' order'+(partial.length===1?' meets':'s meet')+' your selected limits, but calories, protein, carbs or fat are incomplete. Known values still satisfy each nutrient limit. Unknown values stay labelled.</p><button type="button" data-allow-incomplete>Show these orders</button><button class="quiet-button" type="button" data-reset>Clear filters</button></section>';}
    root.querySelector('[data-more]').hidden=results.length<=visible;
    root.querySelector('[data-more]').textContent='Show '+Math.min(12,results.length-visible)+' more meals';
    if(document.documentElement.dataset.motion!=='calm'&&!matchMedia('(prefers-reduced-motion: reduce)').matches)resultList.querySelectorAll('[data-meal-id]').forEach(n=>{const old=previous.get(n.dataset.mealId),box=n.getBoundingClientRect();if(old&&box.top<innerHeight&&box.bottom>0&&(Math.abs(old.top-box.top)>2||Math.abs(old.left-box.left)>2))n.animate([{transform:'translate('+(old.left-box.left)+'px,'+(old.top-box.top)+'px)'},{transform:'none'}],{duration:280,easing:'cubic-bezier(.22,.8,.25,1)'});});
    activeFilters();syncUrl();updateTray();
    root.querySelector('[data-show-saved]').setAttribute('aria-pressed',savedOnly);
    root.querySelector('[data-browse]').setAttribute('aria-pressed',!savedOnly);
    root.querySelector('.home-all-results').href=(window.GetMacrosMarket?.route('finder')||'/restaurant-meal-finder.html')+(E.toSearch(state).toString()?'?'+E.toSearch(state):'');
    root.querySelector('.home-all-results').hidden=!root.hasAttribute('data-home-preview');
    window.GetMacrosCharacters?.enhance(root);
    root.querySelector('[data-share-status]').textContent='';
  }
  function controlsFromState(){
    Object.keys(facets).forEach(k=>form.querySelectorAll('input[name="'+k+'"]').forEach(el=>el.checked=state[k].includes(el.value)));
    Object.keys(limits).forEach(k=>form.elements[k].value=state[k]??'');
    if(form.elements.size)form.elements.size.value=state.size[0]||'';form.elements.incomplete.checked=!state.complete;
    root.querySelector('[name=sort]').value=state.sort;
  }
  function clear(){Object.keys(facets).forEach(k=>state[k]=[]);Object.keys(limits).forEach(k=>state[k]=null);state.complete=true;state.sort='match';savedOnly=false;visible=pageSize;controlsFromState();render();}
  function updateTray(){
    root.querySelector('.compare-tray').hidden=!selected.length;
    root.querySelector('[data-compare-count]').textContent=selected.length+' of 3 meals selected';
    root.querySelector('[data-open-compare]').disabled=selected.length<2;
    root.querySelectorAll('[data-compare]').forEach(el=>{el.checked=selected.includes(Number(el.dataset.compare));el.disabled=selected.length===3&&!el.checked;});
  }
  form.addEventListener('input',e=>{const el=e.target,k=el.name;if(!limits[k]||!el.validity.valid)return;const value=el.value===''?null:Number(el.value);if(state[k]===value)return;state[k]=value;visible=pageSize;render();track('filters_applied');});
  form.addEventListener('submit',e=>e.preventDefault());
  form.addEventListener('reset',e=>{e.preventDefault();clear();});
  root.addEventListener('change',e=>{
    const el=e.target,k=el.name;
    if(el.closest('.guided-dialog'))return;
    if(el.hasAttribute('data-compare')){const id=Number(el.dataset.compare);selected=el.checked?[...selected,id].slice(0,3):selected.filter(v=>v!==id);expectedSnapshots=[];updateTray();return;}
    if(limits[k]){if(!el.reportValidity())return;const value=el.value===''?null:Number(el.value);if(state[k]===value)return;state[k]=value;}
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
    if(el.hasAttribute('data-surprise')){const matches=E.results(meals,state).filter(m=>!savedOnly||saved.includes(key(m)));if(!matches.length)return;const rand=new Uint32Array(1);crypto.getRandomValues(rand);const at=rand[0]%matches.length,m=matches[at];visible=Math.max(visible,Math.ceil((at+1)/pageSize)*pageSize);render();const row=resultList.querySelector('[data-meal-id="'+meals.indexOf(m)+'"]');if(row){const details=row.querySelector('.meal-detail');details.open=true;details.querySelector('summary').focus();}}
    if(el.hasAttribute('data-reset'))clear();
    if(el.hasAttribute('data-allow-incomplete')){state.complete=false;controlsFromState();render();const count=root.querySelector('.results-count');count.tabIndex=-1;count.focus({preventScroll:true});}
    if(el.hasAttribute('data-remove')){const k=el.dataset.remove;if(facets[k])state[k]=state[k].filter(v=>v!==el.dataset.value);else if(k==='complete')state.complete=true;else state[k]=null;controlsFromState();render();root.querySelector('[name=sort]').focus({preventScroll:true});}
    if(el.hasAttribute('data-save')){const m=meals[Number(el.dataset.save)],id=key(m);const next=window.GetMacrosNotebook?.toggle(m);if(!next){root.querySelector('[data-share-status]').textContent='This browser could not save the order. Existing saves are unchanged.';return;}saved=next;el.innerHTML=V.icon('save')+'<span>'+(saved.includes(id)?'Saved':'Save')+'</span>';el.setAttribute('aria-label',(saved.includes(id)?'Unsave ':'Save ')+m.name);window.GetMacrosCompanion?.respond('saved');el.setAttribute('aria-pressed',saved.includes(id));if(savedOnly)render();}
    if(el.hasAttribute('data-open-filters')){filterDialog.append(form);filterDialog.showModal();}
    if(el.hasAttribute('data-close-filters'))filterDialog.close();
    if(el.hasAttribute('data-clear-compare')){selected=[];updateTray();}
    if(el.hasAttribute('data-open-compare')){
      const pair=selected.map(i=>meals[i]);track('comparison_used');
      root.querySelector('.comparison-output').innerHTML=GetMacrosOrderCore.comparisonTable(pair,expectedSnapshots)+'<div class="comparison-actions"><button type="button" class="btn" data-share-comparison>Share comparison</button><button type="button" data-print>Print comparison</button><a href="'+(state.market==='CA'?'/ca/en/tools/complete-order/#order-builder':'/compare-complete-restaurant-orders.html#order-builder')+'">Build an order</a></div><p data-comparison-status role="status"></p>';
      compareDialog.showModal();
    }
    if(el.hasAttribute('data-close-compare'))compareDialog.close();
    if(el.hasAttribute('data-print'))window.print();
    if(el.hasAttribute('data-share')||el.hasAttribute('data-share-comparison')){
      const url=new URL(window.GetMacrosMarket?.route('finder')||'/restaurant-meal-finder.html',location.origin);url.search=E.toSearch(state).toString();
      const comparison=el.hasAttribute('data-share-comparison');if(comparison)selected.forEach(i=>{url.searchParams.append('compare',key(meals[i]));if(window.GetMacrosOrderCore)url.searchParams.append('snapshot',GetMacrosOrderCore.version(meals[i]));});
      const status=root.querySelector(comparison?'[data-comparison-status]':'[data-share-status]');
      try{await navigator.clipboard.writeText(url.href);status.textContent=comparison?'Comparison link copied.':'Result link copied.';}catch{status.replaceChildren();const label=document.createElement('label');label.textContent='Copy this link';const input=document.createElement('input');input.readOnly=true;input.setAttribute("aria-label",comparison?"Comparison link":"Results link");input.value=url.href;label.append(input);status.append(label);input.focus();input.select();}track('share_action');
    }
  });
  filterDialog.addEventListener('close',()=>{root.querySelector('.finder-sidebar').append(form);root.querySelector('[data-open-filters]').focus({preventScroll:true});});
  const guided=window.GetMacrosGuide.mount(root,{meals,apply(draft){
    state=E.normalize(draft,meals);savedOnly=false;visible=pageSize;controlsFromState();render();
    const count=root.querySelector('.results-count');count.tabIndex=-1;count.focus();track('quiz_completed');
  }});
  function openGuide(){guided.open();track('finder_started');}
  const restaurantPicker=root.querySelector('.restaurant-picker');
  document.addEventListener('click',e=>{if(restaurantPicker.open&&!restaurantPicker.contains(e.target))restaurantPicker.open=false;});
  restaurantPicker.addEventListener('keydown',e=>{if(e.key==='Escape'&&restaurantPicker.open){e.preventDefault();e.stopPropagation();restaurantPicker.open=false;restaurantPicker.querySelector('summary').focus();}});
  compareDialog.addEventListener('close',()=>root.querySelector('[data-open-compare]').focus({preventScroll:true}));
  const mobile=matchMedia('(max-width: 800px)');mobile.addEventListener('change',e=>{if(!e.matches&&filterDialog.open)filterDialog.close();});
  addEventListener('popstate',()=>{state=readState();controlsFromState();visible=pageSize;render();});
  root.dataset.ready='true';controlsFromState();render();if(selected.length>=2)root.querySelector('[data-open-compare]').click();
})();
