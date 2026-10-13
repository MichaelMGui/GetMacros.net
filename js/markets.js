/* Country is a menu market; language is a separate reviewed-content preference. */
(function(){'use strict';
const definitions=window.GM_MARKETS||{US:{name:'United States',home:'/',finder:'/restaurant-meal-finder.html',restaurants:'/restaurant-meal-guides.html',collection:'/healthy-fast-food.html',chains:null,currency:'USD'},CA:{name:'Canada',home:'/ca/en/',finder:'/ca/en/find-a-meal/',restaurants:'/ca/en/restaurants/',collection:'/ca/en/collections/protein-meals/',chains:['A&W Canada','Harvey’s','Tim Hortons'],currency:'CAD'}};
const stored=()=>{try{return localStorage.getItem('gm-market-v1')}catch{return null}};
const pathMarket=Object.keys(definitions).find(k=>k!=='US'&&location.pathname.startsWith('/'+k.toLowerCase()+'/en/'))||(document.documentElement.dataset.marketScope==='US'?'US':null);
const requested=new URLSearchParams(location.search).get('market');
const current=pathMarket||(definitions[requested]?requested:definitions[stored()]?stored():'US');
function persist(value){try{localStorage.setItem('gm-market-v1',value);localStorage.setItem('gm-language-v1','en')}catch{}}
function route(kind,value=current){return definitions[value][kind]}
function switchURL(value,url=new URL(location.href)){
 const old=definitions[current],next=definitions[value],isFinder=location.pathname===old.finder;
 if(isFinder)url.pathname=next.finder;
 else if(location.pathname===old.home||location.pathname==='/index.html')url.pathname=next.home;
 else if(location.pathname===old.restaurants)url.pathname=next.restaurants;
 else if(pathMarket){url.pathname=next.home;for(const k of ['chain','size','diet','item','compare','snapshot'])url.searchParams.delete(k);url.searchParams.set('marketChanged','page');}
 else url.searchParams.set('market',value);
 let cleared=false;
 if(isFinder){url.searchParams.delete('market');const chains=url.searchParams.getAll('chain'),compatible=next.chains?chains.filter(c=>next.chains.includes(c)):[];if(chains.length!==compatible.length){url.searchParams.delete('chain');compatible.forEach(c=>url.searchParams.append('chain',c));cleared=true;}
 for(const key of ['compare','snapshot','item','diet',...(value!=='US'?['size']:[])])if(url.searchParams.has(key)){url.searchParams.delete(key);cleared=true;}
 if(cleared)url.searchParams.set('marketChanged','1');}
 return url;
}
document.documentElement.dataset.currentMarket=current;
window.GetMacrosMarket=Object.freeze({current,definitions,route,switchURL});
function init(){document.querySelectorAll('[data-current-market-label]').forEach(n=>n.textContent='© 2026 GetMacros · '+definitions[current].name+' menus');document.querySelectorAll('[data-country-select]').forEach(select=>select.value=current);document.querySelectorAll('[data-country-name]').forEach(n=>n.textContent=definitions[current].name);document.querySelectorAll('.country-picker>summary').forEach(n=>n.setAttribute('aria-label','Restaurant country: '+definitions[current].name+'. Choose country'));document.querySelectorAll('[data-country-flag]').forEach(n=>{const generic=n.querySelector('[data-market-flag]');if(generic)generic.setAttribute("href","/images/market-flags.svg#flag-"+current);else{n.querySelector('[data-flag-us]').hidden=current!=='US';n.querySelector('[data-flag-ca]').hidden=current!=='CA';}});
 document.querySelectorAll('[data-market-route]').forEach(a=>a.href=route(a.dataset.marketRoute));
 document.querySelectorAll('[data-market-context]').forEach(a=>{const url=new URL(a.href,location.href);url.searchParams.set('market',current);a.href=url.href;});
 document.querySelectorAll('.nav-search-panel').forEach(form=>{if(form.tagName!=='FORM')return;let input=form.querySelector('[name=market]');if(!input){input=document.createElement('input');input.type='hidden';input.name='market';form.append(input);}input.value=current;});
 document.querySelectorAll('[data-market-only]').forEach(a=>a.hidden=a.dataset.marketOnly!==current);
 if(current==='CA'){const hint=document.querySelector('[data-search-query=Chipotle]');if(hint){hint.dataset.searchQuery='Tim Hortons';hint.textContent='Tim Hortons';}const search=document.querySelector('#site-search');if(search)search.placeholder='Try protein latte or breakfast';}
 const pickers=[...document.querySelectorAll('.country-picker,.language-picker,.appearance-picker,.nav-search')];
 pickers.forEach(p=>p.addEventListener('toggle',()=>{if(p.open)pickers.filter(x=>x!==p).forEach(x=>x.open=false)}));
 document.addEventListener('click',e=>pickers.forEach(p=>{if(p.open&&!p.contains(e.target))p.open=false}));
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){const p=pickers.find(x=>x.open);if(p){e.preventDefault();p.open=false;p.querySelector('summary').focus();}}});
 document.querySelectorAll('[data-country-form]').forEach(form=>form.addEventListener('submit',e=>{e.preventDefault();const value=form.querySelector('[data-country-select]').value;persist(value);if(value===current){form.closest('details').open=false;form.closest('details').querySelector('summary').focus();return;}location.assign(switchURL(value).href);}));
 const choices=[...document.querySelectorAll('[data-country-choice]')];
 choices.forEach(a=>{
  const value=a.dataset.countryChoice;
  if(!definitions[value])return;
  a.href=switchURL(value).href;
  if(value===current)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');
  a.addEventListener('click',e=>{
   // Links remain crawlable and support opening a deliberate country in a tab.
   if(e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0)return;
   persist(value);
   if(value===current){e.preventDefault();const picker=a.closest('details');picker.open=false;picker.querySelector('summary').focus();}
  });
 });
 const countryPanel=document.querySelector('.country-panel');
 countryPanel?.addEventListener('keydown',e=>{
  const shown=choices.filter(a=>!a.closest('li').hidden),index=shown.indexOf(document.activeElement);
  if(index<0)return;
  const next=e.key==='ArrowDown'?(index+1)%shown.length:e.key==='ArrowUp'?(index-1+shown.length)%shown.length:e.key==='Home'?0:e.key==='End'?shown.length-1:null;
  if(next!==null){e.preventDefault();shown[next].focus();}
 });
 const countrySearch=document.querySelector('[data-country-search]');
 if(countrySearch&&choices.length>12){countrySearch.closest('label').hidden=false;countrySearch.addEventListener('input',()=>{const q=countrySearch.value.trim().toLocaleLowerCase();choices.forEach(a=>a.closest('li').hidden=!definitions[a.dataset.countryChoice].name.toLocaleLowerCase().includes(q));});}
 if(new URLSearchParams(location.search).has('marketChanged')){const n=document.createElement('p');n.className='market-notice';n.setAttribute('role','status');n.textContent=new URLSearchParams(location.search).get('marketChanged')==='page'?'Country changed. This restaurant or exact order is not published in the selected market, so its selection was cleared. Browse the available local menus below.':'Country changed. Restaurant, comparison or ingredient selections that do not apply here were cleared. Compatible nutrient limits and meal preferences were kept.';const quiz=document.querySelector('#meal-quiz');if(quiz)quiz.before(n);else document.querySelector('main')?.prepend(n);const url=new URL(location.href);url.searchParams.delete('marketChanged');history.replaceState(null,'',url);}
 const currency=document.querySelector('#receipt-currency');if(currency&&!currency.dataset.userSet&&[...currency.options].some(o=>o.value===definitions[current].currency))currency.value=definitions[current].currency;currency?.addEventListener('change',()=>currency.dataset.userSet='true');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
