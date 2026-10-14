/* Two reviewed source portions, kept locally. No diary entries or notes. */
(function(root,factory){const api=factory(typeof module==='object'?require('./food-core.js'):root.GetMacrosFood);if(typeof module==='object'&&module.exports)module.exports=api;else root.GetMacrosFoodComparison=api;})(typeof window==='undefined'?globalThis:window,function(F){'use strict';
 const storageKey='gm-reviewed-comparison-v1';
 function validate(items){if(!Array.isArray(items)||items.length>2)throw Error('Choose up to two portions.');return items.map(s=>{F.validateSnapshot(s);if(s.type==='recipe'||!s.recordId.match(/^(fdc:|cnf:|branded:|order:)/))throw Error('Only public food records can be shared here.');return JSON.parse(JSON.stringify(s));});}
 function add(items,s){validate([s]);const key=x=>[x.recordId,x.version,x.quantity,x.measure].join('|');const next=validate(items).filter(x=>key(x)!==key(s));if(next.length===2)next.shift();return [...next,s];}
 function link(items,basis='portions',base='https://getmacros.net'){items=validate(items);const url=new URL('/compare-foods.html',base);items.forEach(s=>{url.searchParams.append('item',s.recordId);url.searchParams.append('version',s.version);url.searchParams.append('quantity',s.quantity);url.searchParams.append('measure',s.measure);});url.searchParams.set('basis',basis==='100g'?'100g':'portions');return url.href;}
 function read(storage){try{return validate(JSON.parse(storage.getItem(storageKey)||'[]'));}catch{return [];}}
 function write(storage,items){const safe=validate(items);storage.setItem(storageKey,JSON.stringify(safe));return safe;}
 function readBasis(storage){try{return storage.getItem(storageKey+'-basis')==='100g'?'100g':'portions';}catch{return 'portions';}}
 function writeBasis(storage,value){storage.setItem(storageKey+'-basis',value==='100g'?'100g':'portions');}
 return {validate,add,link,read,write,readBasis,writeBasis,storageKey};
});
