/* The additional calculators share one input/result lifecycle and no HTML string inputs. */
(() => {
 'use strict';
 const form=document.querySelector('[data-focused-calculator]');if(!form)return;
 const kind=form.dataset.focusedCalculator,$=id=>document.getElementById(id);
 const panel=form.parentElement.querySelector('.tool-output'),out=panel.querySelector('.focused-result'),empty=panel.querySelector('.focused-empty'),error=form.querySelector('.focused-error');
 const num=id=>Number($(id).value),fmt=(n,d=1)=>n.toLocaleString(undefined,{maximumFractionDigits:d});
 const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;};
 function metric(label,value,unit,note){const e=node('div',undefined,'focused-metric');e.append(node('span',label));const strong=node('strong',value);if(unit)strong.append(node('small',' '+unit));e.append(strong);if(note)e.append(node('small',note));return e;}
 function grid(...items){const g=node('div',undefined,'focused-metrics');g.append(...items);return g;}
 const paragraph=(text,cls)=>node('p',text,cls);
 function clear(){out.hidden=true;out.replaceChildren();empty.hidden=false;error.hidden=true;}
 function fail(message){clear();error.textContent=message;error.hidden=false;}
 function show(...items){error.hidden=true;out.replaceChildren(...items);out.hidden=false;empty.hidden=true;
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches||document.documentElement.classList.contains('tide-motion-off');
  // Results sit directly after the form on phones; never move the viewport on calculation.
  out.focus({preventScroll:true});
  if(!reduced&&out.animate)out.animate([{opacity:.6,translate:'0 5px'},{opacity:1,translate:'0 0'}],{duration:200,easing:'ease-out'});
 }
 function calculate(){
  if(!form.reportValidity())return;
  if([...form.querySelectorAll('input[type=number]')].some(e=>e.value!==''&&!Number.isFinite(Number(e.value))))return fail('Check the numbers and try again.');
  if(kind==='sodium'){
   const a=num('am')*num('as'),b=num('bm')*num('bs'),an=$('an').value.trim()||'Food 1',bn=$('bn').value.trim()||'Food 2';
   const verdict=a===b?'Both portions have the same amount of sodium.':`${a<b?an:bn} has ${fmt(Math.abs(a-b),0)} mg less sodium in the portion you entered.`;
   show(grid(metric(an,fmt(a,0),'mg',`${fmt(a/2300*100,0)}% Daily Value`),metric(bn,fmt(b,0),'mg',`${fmt(b/2300*100,0)}% Daily Value`)),paragraph(verdict,'focused-verdict'),paragraph('The Daily Value is a label reference, not a personal target.','focused-hint'));
  }else if(kind==='carbs'){
   const c=num('c'),s=num('s'),fiber=$('f').value!=='',sugar=$('a').value!=='';
   if(fiber&&num('f')>c)return fail('Fiber cannot be higher than total carbs on the same label.');
   if(sugar&&num('a')>c)return fail('Added sugar cannot be higher than total carbs on the same label.');
   const items=[metric('Total carbs in your portion',fmt(c*s),'g'),paragraph(`${fmt(c)} g per serving × ${fmt(s,2)} servings`,'focused-equation')];
   const extras=[];if(fiber)extras.push(metric('Fiber',fmt(num('f')*s),'g'));if(sugar)extras.push(metric('Added sugar',fmt(num('a')*s),'g'));if(extras.length)items.push(grid(...extras));
   show(...items);
  }else if(kind==='sweat'){
   const factor=$('unit').value==='lb'?.45359237:1,mass=(num('before')-num('after'))*factor,drinks=num('drink')/1000,urine=num('urine')/1000,hours=num('time')/60,loss=mass+drinks-urine;
   if(loss<0)return fail('These numbers imply fluid gain. Check your weights, units and drinks, including wet clothing or food during the workout.');
   const rate=loss/hours;
   show(metric('Estimated sweat rate',rate.toFixed(2),'L/hour'),grid(metric('Total fluid lost',fmt(loss,2),'L'),metric('In US fluid ounces',fmt(rate*33.814,0),'fl oz/hour')),paragraph(`${fmt(mass,2)} kg weight change + ${fmt(drinks,2)} L drunk − ${fmt(urine,2)} L urine, over ${fmt(hours,2)} hours.`,'focused-equation'),paragraph('An estimate for this workout, not a target to replace every drop during exercise.','focused-hint'));
  }else if(kind==='timeline'){
   const current=num('wg-current'),goal=num('wg-goal'),pace=num('wg-rate')/100,unit=$('wg-unit').value;
   if(current===goal)return fail('Your current and goal weights are the same. Enter a different goal to estimate a timeline.');
   const losing=goal<current,difference=Math.abs(current-goal),sign=losing?-1:1;let weight=current,weeks=0,next=0;const milestones=[];
   while(Math.abs(weight-goal)>1e-8&&weeks<2000){weight+=sign*Math.min(weight*pace,Math.abs(weight-goal));weeks++;
    while(next<4&&Math.abs(weight-current)+1e-8>=difference*(next+1)/4){milestones.push({weight:current+sign*difference*(next+1)/4,weeks});next++;}
   }
   if(weeks===2000)return fail('This goal is beyond the calculator’s range. Check the weights and weekly pace.');
   const date=w=>{const d=new Date();d.setDate(d.getDate()+w*7);return d.toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'});};
   const list=node('ol',undefined,'focused-milestones');milestones.forEach((m,i)=>{const li=node('li');li.append(node('span',i===3?'Goal weight':`${(i+1)*25}% of the way`),node('strong',`${fmt(m.weight)} ${unit}`),node('time',date(m.weeks)));list.append(li);});
   const math=node('details',undefined,'focused-math');math.append(node('summary','See the calorie calculation'));
   const calories=Math.round(current*(unit==='lb'?.45359237:1)*pace*7700/7);
   math.append(paragraph(`The first week works out to about ${fmt(calories,0)} calories ${losing?'below':'above'} maintenance per day, using 7,700 calories per kilogram. This simplified math is not a personal calorie target.`));
   show(metric('Estimated time',String(weeks),weeks===1?'week':'weeks'),paragraph(`Around ${date(weeks)}, if the chosen pace stayed consistent.`,'focused-verdict'),node('h3','Milestones'),list,math);
  }
 }
 form.addEventListener('submit',e=>{e.preventDefault();calculate();});
 form.addEventListener('input',clear);form.addEventListener('change',clear);
 form.addEventListener('reset',()=>{clear();queueMicrotask(()=>{if(unitControl){previousUnit=unitControl.value;updateUnits();}});});
 const unitControl=kind==='timeline'?$('wg-unit'):kind==='sweat'?$('unit'):null;
 let previousUnit=unitControl?.value;
 function updateUnits(){if(!unitControl)return;const ids=kind==='timeline'?['wg-current','wg-goal']:['before','after'];ids.forEach(id=>{const input=$(id);input.nextElementSibling.textContent=unitControl.value;input.setAttribute('aria-label',input.closest('label').querySelector(':scope>span').textContent+' ('+unitControl.value+')');});}
 unitControl?.addEventListener('change',()=>{const factor=unitControl.value==='kg'?.45359237:1/.45359237;const ids=kind==='timeline'?['wg-current','wg-goal']:['before','after'];if(previousUnit!==unitControl.value)ids.forEach(id=>{if($(id).value!=='')$(id).value=(num(id)*factor).toFixed(2);});previousUnit=unitControl.value;updateUnits();});
 form.querySelector('[data-example]').addEventListener('click',()=>{const values=JSON.parse(form.dataset.exampleValues);Object.entries(values).forEach(([id,value])=>{$(id).value=value;});previousUnit=unitControl?.value;updateUnits();form.requestSubmit();});
})();
