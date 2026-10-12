/* Limited source-label comparison, not formulation or allergen equivalence. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.GetMacrosIngredientCompare=api;})(typeof window==='undefined'?globalThis:window,function(){'use strict';
 const plurals={cucumbers:'cucumber',onions:'onion',tomatoes:'tomato',carrots:'carrot'};
 function key(value){const label=String(value).normalize('NFKC').toLocaleLowerCase('en').trim().replace(/\s+/g,' ');return plurals[label]||label;}
 function compare(left,right){const a=new Map(left.map(value=>[key(value),value])),b=new Map(right.map(value=>[key(value),value]));return{matching:[...a].filter(([k])=>b.has(k)).map(([k,value])=>({left:value,right:b.get(k)})),onlyLeft:[...a].filter(([k])=>!b.has(k)).map(([,value])=>value),onlyRight:[...b].filter(([k])=>!a.has(k)).map(([,value])=>value)};}
 return{key,compare};
});
