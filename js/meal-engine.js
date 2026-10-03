/* One filtering/ranking implementation for browsing, guided choices and links. */
(function(global){'use strict';
const limits={maxCal:[150,2500,'Maximum calories'],minProtein:[0,200,'Minimum protein (g)'],minFiber:[0,50,'Minimum fiber (g)'],maxSodium:[0,10000,'Maximum sodium (mg)']};
const facets={goal:['protein','light','energy','fibre','lowsodium'],diet:['vegetarian','plant'],meal:['main','breakfast'],size:['small','medium','large']};
const complete=m=>['cal','p','f','na'].every(k=>Number.isFinite(m[k]));
const key=m=>m.chain+'||'+m.name;
function normalize(input={},meals=[]){
const options={...facets,chain:[...new Set(meals.map(m=>m.chain))]};const s={sort:['match','calories','protein'].includes(input.sort)?input.sort:'match',complete:input.complete!==false};
for(const [k,values] of Object.entries(options))s[k]=[...new Set((Array.isArray(input[k])?input[k]:[]).filter(v=>values.includes(v)))];
for(const [k,[min,max]] of Object.entries(limits)){const value=input[k],n=Number(value);s[k]=value!==null&&value!==undefined&&value!==''&&Number.isFinite(n)&&n>=min&&n<=max?n:null;}
return s;
}
function fromSearch(search,meals){const q=new URLSearchParams(search),input={complete:q.get('complete')!=='0',sort:q.get('sort')};for(const k of [...Object.keys(facets),'chain'])input[k]=q.getAll(k);for(const k of Object.keys(limits))input[k]=q.get(k);return normalize(input,meals);}
function toSearch(s){const q=new URLSearchParams();for(const k of [...Object.keys(facets),'chain'])s[k].forEach(v=>q.append(k,v));for(const k of Object.keys(limits))if(s[k]!==null)q.set(k,s[k]);if(!s.complete)q.set('complete','0');if(s.sort!=='match')q.set('sort',s.sort);return q;}
function eligible(m,s){
if(s.complete&&!complete(m))return false;
if(s.chain.length&&!s.chain.includes(m.chain)||s.meal.length&&!s.meal.includes(m.meal))return false;
if(!s.diet.every(d=>(m.diet||[]).includes(d)))return false;
return [['maxCal','cal',false],['minProtein','p',true],['minFiber','f',true],['maxSodium','na',false]].every(([k,n,min])=>s[k]===null||Number.isFinite(m[n])&&(min?m[n]>=s[k]:m[n]<=s[k]));
}
function score(m,s){let n=s.size.length&&m.size===s.size[0]?28:0;s.goal.forEach(g=>{if((m.t||[]).includes(g))n+=65;});if(Number.isFinite(m.p))n+=Math.min(m.p,50)*.5;if(Number.isFinite(m.f))n+=Math.min(m.f,15)*.5;if(Number.isFinite(m.p)&&m.cal)n+=m.p/m.cal*100;if(!complete(m))n-=40;return n;}
function results(meals,s){return meals.filter(m=>eligible(m,s)).sort((a,b)=>s.sort==='calories'?(a.cal??Infinity)-(b.cal??Infinity)||score(b,s)-score(a,s):s.sort==='protein'?(b.p??-Infinity)-(a.p??-Infinity)||score(b,s)-score(a,s):score(b,s)-score(a,s));}
const api={limits,facets,complete,key,normalize,fromSearch,toSearch,eligible,score,results};global.GetMacrosMeals=api;if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
