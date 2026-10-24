const assert=require('node:assert/strict'),test=require('node:test'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),api=require('../../js/article-tools.js');
const model=slug=>JSON.parse(fs.readFileSync(path.join(root,slug+'.html'),'utf8').match(/<script type="application\/json" data-tool-model>(.*?)<\/script>/s)[1]);
test('a 200 g bowl scales the three exact FAGE US products',()=>{
 const m=model('fage-plain-greek-yogurt-0-2-5-percent'),r=api.scale(m.rows,200,m.baseGrams,m.fields);
 assert.equal(api.format(r[0].cal),'105.9');assert.equal(api.format(r[0].p),'21.2');assert.equal(api.format(r[1].p),'20');assert.equal(api.format(r[2].cal),'188.2');
});
test('Australian dry pasta uses its own source panel and weight',()=>{
 const m=model('barilla-australia-protein-plus-vs-spaghetti'),r=api.scale(m.rows,80,m.baseGrams,m.fields);
 assert.equal(api.format(r[0].cal),'287.2');assert.equal(r[0].p,16);assert.equal(api.format(r[1].cal),'291.2');assert.equal(api.format(r[1].p),'10.2');
});
test('Greggs bacon baguette plus regular latte totals only those components',()=>{
 const m=model('greggs-breakfast-baguette-calories-protein'),r=api.sum([m.mains[1],m.drinks[1]],m.fields);
 assert.equal(r.cal,576);assert.equal(r.p,33.8);assert.equal(r.c,69);assert.equal(r.fat,17.3);
 assert.equal(m.market,'GB');assert(m.mains.every(r=>r.market==='GB'));
});
test('Canadian sandwich, separate hash brown and black coffee are counted once',()=>{
 const m=model('tim-hortons-canada-breakfast-muffin-biscuit-wrap'),r=api.sum([m.mains[0],m.side,m.drinks[0]],m.fields);
 assert.deepEqual([r.cal,r.p,r.c,r.fat],[394,15,42,18]);assert.equal(m.market,'CA');
});
test('missing nutrients stay unknown, including a partially known total',()=>{
 const fields=[{key:'p'}];assert.equal(api.sum([{p:12},{p:null}],fields).p,null);
 assert.equal(api.scale([{name:'Partial',p:null}],200,100,fields)[0].p,null);
 assert.equal(api.format(null),'Not reported');assert.equal(api.sum([{p:0},{p:0}],fields).p,0);
});
test('invalid weights, invalid choices and cross-country sums fail explicitly',()=>{
 for(const grams of [-1,0,NaN,Infinity,2001])assert.throws(()=>api.scale([{p:2}],grams,100,[{key:'p'}]));
 assert.throws(()=>api.sum([],[{key:'p'}]));assert.throws(()=>api.sum([undefined],[{key:'p'}]));
 assert.throws(()=>api.sum([{market:'US',p:2},{market:'CA',p:3}],[{key:'p'}]),/same country/);
});
test('article tools do not store or transmit the visitor’s portion choices',()=>{
 const source=fs.readFileSync(path.join(root,'js/article-tools.js'),'utf8');
 assert(!/fetch\(|XMLHttpRequest|localStorage|sessionStorage|gtag\(|sendBeacon|location\./.test(source));
});
