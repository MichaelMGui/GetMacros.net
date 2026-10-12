/* Reviewed repeats and day navigation, entirely in private browser storage. */
(function(){'use strict';
 const root=document.querySelector('[data-food-app="diary"]');if(!root)return;
 const F=window.GetMacrosFood,S=window.GetMacrosDiary,UI=window.GetMacrosFoodUI;
 const date=root.querySelector('[data-diary-date]'),dialog=root.querySelector('#diary-repeat'),form=dialog.querySelector('form');
 const source=form.elements.source,sourceDate=form.elements.sourceDate,targetDate=form.elements.targetDate,targetMeal=form.elements.targetMeal;
 const preview=form.querySelector('[data-repeat-preview]'),status=form.querySelector('[data-repeat-status]'),save=form.querySelector('[data-repeat-save]');
 const meals=[['Breakfast','Breakfast'],['Lunch','Lunch'],['Dinner','Dinner'],['Snack','Snacks']];
 let sources=[],reviewed=[],operationId,loadId=0,previousFocus,sourceLoading=false,saving=false;
 const label=value=>meals.find(m=>m[0]===value)?.[1]||value;
 function element(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;}
 function fail(e){status.textContent=e.message||'The meal could not be copied. Try again.';status.dataset.error='true';save.disabled=true;if(!dialog.open){const message=root.querySelector('[data-diary-status]');message.textContent=status.textContent;message.dataset.error='true';}}
 function warn(){const same=sourceDate.value===targetDate.value&&source.value===targetMeal.value,n=form.querySelector('[data-repeat-warning]');n.hidden=!same;n.textContent='This is the same date and meal. Copying adds another set of these foods.';}
 function paint(){
  reviewed=sources.filter(e=>e.occasion===source.value).map(e=>JSON.parse(JSON.stringify(e)));preview.replaceChildren();status.textContent='';delete status.dataset.error;warn();
  save.disabled=sourceLoading||saving||!reviewed.length||reviewed.length>100;save.textContent=reviewed.length?'Copy '+reviewed.length+' '+(reviewed.length===1?'food':'foods'):'Copy meal';
  if(!reviewed.length){preview.append(element('p','No foods logged for this meal. Choose another date or meal.'));return;}
  if(reviewed.length>100){fail(Error('Choose a meal with up to 100 foods.'));return;}
  const heading=element('h3',reviewed.length+' saved '+(reviewed.length===1?'portion':'portions')),list=element('ul');
  for(const entry of reviewed){const row=element('li'),s=entry.snapshot;row.append(element('span',s.name),element('small',s.quantity+' '+s.portionLabel+(s.market&&!['US-reference','CA-reference','personal'].includes(s.market)?' · '+(window.GetMacrosMarket.definitions[s.market]?.name||s.market):'')));list.append(row);}
  const total=F.sum(reviewed.map(e=>e.snapshot.nutrients)).cal;
  const description=total.missing===total.count?'Calories unavailable':new Intl.NumberFormat('en',{maximumFractionDigits:1}).format(total.missing?total.subtotal:total.value)+' kcal'+(total.missing?' known subtotal · '+total.missing+' unavailable':' logged');
  preview.append(heading,element('p',description),list);
 }
 async function loadSource(preferred){
  const id=++loadId;sourceLoading=true;sources=[];reviewed=[];source.disabled=true;save.disabled=true;status.textContent='Loading saved foods…';delete status.dataset.error;preview.replaceChildren();
  try{const selectedDate=F.date(sourceDate.value),rows=await S.list(selectedDate);if(id!==loadId||selectedDate!==sourceDate.value)return;
   sources=rows;sourceLoading=false;const kept=preferred||source.value;source.replaceChildren();
   for(const [value,name]of meals){const count=rows.filter(e=>e.occasion===value).length;source.append(new Option(name+' · '+count+' '+(count===1?'food':'foods'),value));}
   source.value=preferred&&!rows.some(e=>e.occasion===preferred)?rows[0]?.occasion||preferred:kept&&meals.some(m=>m[0]===kept)?kept:rows[0]?.occasion||'Lunch';paint();
  }catch(e){if(id===loadId){sources=[];reviewed=[];fail(e);}}
  finally{if(id===loadId){sourceLoading=false;source.disabled=saving;}}
 }
 async function open(){
  if(saving){root.querySelector('[data-diary-status]').textContent='Finishing the meal copy…';return;}
  const id=++loadId;previousFocus=document.activeElement;operationId=crypto.randomUUID();form.reset();targetDate.value=F.date(date.value);
  targetMeal.value=root.querySelector('[name=pickerMeal]:checked')?.value||'Lunch';
  if(!dialog.open)dialog.showModal();save.disabled=true;status.textContent='Loading saved foods…';delete status.dataset.error;
  try{const last=await S.lastLoggedDate(date.value);if(id!==loadId||!dialog.open)return;sourceDate.value=last||date.value;await loadSource(targetMeal.value);if(dialog.open&&(document.activeElement===form.querySelector('[data-repeat-close]')||document.activeElement===sourceDate))sourceDate.focus({preventScroll:true});}catch(e){fail(e);}
 }
 async function shiftDay(delta){
  const value=F.date(date.value),next=new Date(value+'T12:00:00Z');next.setUTCDate(next.getUTCDate()+delta);return UI.setDiaryDate(next.toISOString().slice(0,10));
 }
 root.querySelector('[data-diary-previous]').addEventListener('click',()=>shiftDay(-1).catch(e=>root.querySelector('[data-diary-status]').textContent=e.message));
 root.querySelector('[data-diary-next]').addEventListener('click',()=>shiftDay(1).catch(e=>root.querySelector('[data-diary-status]').textContent=e.message));
 root.querySelector('[data-diary-today]').addEventListener('click',()=>UI.setDiaryDate(F.today()).catch(e=>root.querySelector('[data-diary-status]').textContent=e.message));
 root.querySelector('[data-repeat-open]').addEventListener('click',()=>open().catch(fail));
 form.querySelector('[data-repeat-close]').addEventListener('click',()=>dialog.close());
 dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
 dialog.addEventListener('close',()=>{loadId++;if((document.activeElement===document.body||dialog.contains(document.activeElement))&&previousFocus?.isConnected)previousFocus.focus({preventScroll:true});});
 sourceDate.addEventListener('change',()=>loadSource().catch(fail));source.addEventListener('change',paint);targetDate.addEventListener('change',warn);targetMeal.addEventListener('change',warn);
 form.addEventListener('submit',async e=>{
  e.preventDefault();if(save.disabled||sourceLoading||saving)return;saving=true;save.disabled=true;const destinationDate=targetDate.value,destinationMeal=targetMeal.value;
  const copyNotes=form.elements.copyNotes.checked,controls=[...form.elements].filter(n=>n!==form.querySelector('[data-repeat-close]'));
  controls.forEach(n=>n.disabled=true);
  save.textContent='Copying…';status.textContent='Saving this meal…';delete status.dataset.error;
  try{const rows=await S.copyMeal(reviewed,{date:destinationDate,occasion:destinationMeal,copyNotes,operationId});
   dialog.close();await UI.setDiaryDate(destinationDate);root.querySelector('[data-repeat-open]').focus({preventScroll:true});
   root.querySelector('[data-diary-status]').textContent='Copied '+rows.length+' '+(rows.length===1?'food':'foods')+' to '+label(destinationMeal)+' on '+destinationDate+'. Saved in this browser.';
  }catch(e){fail(e);}
  finally{saving=false;controls.forEach(n=>n.disabled=false);save.disabled=sourceLoading||!reviewed.length||reviewed.length>100;save.textContent=reviewed.length?'Copy '+reviewed.length+' '+(reviewed.length===1?'food':'foods'):'Copy meal';}
 });
})();
