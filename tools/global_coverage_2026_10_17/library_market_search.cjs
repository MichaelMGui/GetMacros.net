/* Real public source rows; isolated failures never publish invented records. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib');
const root=path.resolve(__dirname,'../..'),F=require(path.join(root,'js/food-core.js'));
const sourceJSON=require('../source-json.cjs'),registry=sourceJSON.read(path.join(root,'js/order-registry.json')).records;
const manifest=sourceJSON.read(path.join(root,'data/restaurant-foods/manifest.json'));
const code=fs.readFileSync(path.join(root,'js/food-library.js'),'utf8');
let checks=0;
const check=(condition,message)=>{assert(condition,message);checks++;};
function session({market='CA',failure,labelsFail=false,decoded=false}={}){
 const requests=[],events=[];let bytes=0;
 const context={GetMacrosFood:F,GetMacrosMarket:{current:market},TextEncoder,TextDecoder,Response,DecompressionStream,Uint8Array,Map,Set,Promise,console,
  CustomEvent:class{constructor(type,options){this.type=type;this.detail=options.detail;}},dispatchEvent:event=>events.push(event),
  GetMacrosBranded:{queryTokens:q=>F.text(q).split(' '),search:async()=>{if(labelsFail)throw Error('Label source unavailable');return [];},get:async()=>{throw Error('Not a restaurant source');}},
  fetch:async(url,options)=>{
   requests.push({url,options});
   if(failure){const result=await failure(url);if(result)return result;}
   const file=path.join(root,new URL(url,'https://getmacros.test').pathname);
   if(decoded&&file.endsWith('.gz')){const data=fs.readFileSync(file);bytes+=data.length;return new Response(zlib.gunzipSync(data));}
   return sourceJSON.fileResponse(root,url,n=>bytes+=n);
  }};
 context.window=context;vm.runInNewContext(code,context,{filename:'food-library.js'});
 return {api:context.GetMacrosLibrary,requests,events,get bytes(){return bytes;}};
}
const requestedMarkets=s=>s.requests.flatMap(({url})=>{const found=/\/restaurant-foods\/([A-Z]{2})\.json/.exec(url);return found?[found[1]]:[];});
const noRegistry=s=>check(!s.requests.some(({url})=>url.includes('order-registry')),'Full restaurant registry must never be fetched');
(async()=>{
 const ca=session(),loaded=await ca.api.load(),coldSelectedMarketBytes=ca.bytes;
 assert.deepEqual(Object.keys(loaded).sort(),['index','manifest']);
 assert.equal(loaded.index.filter(r=>r.type==='restaurant').length,manifest.markets.CA.count);
 check(loaded.index.every(r=>r.type!=='restaurant'||r.market==='CA'),'Default load follows current country');
 assert.deepEqual(requestedMarkets(ca),['CA']);noRegistry(ca);
 assert.equal(await ca.api.load({market:'CA'}),loaded);assert.equal(ca.requests.length,4);
 const caQuery=registry.find(r=>r.market==='CA'&&r.chain==='KFC').chain;
 const caRows=await ca.api.search(caQuery,{market:'CA',type:'restaurant'});
 check(caRows.length>0&&caRows.every(r=>r.market==='CA'),'Explicit CA search is isolated');
 const beforeUS=ca.requests.length,usRows=await ca.api.search('Panda Express',{market:'US',type:'restaurant'});
 check(usRows.length>0&&usRows.every(r=>r.market==='US'),'Market switching selects US records');
 assert.equal(ca.requests.length,beforeUS+1);assert.deepEqual(requestedMarkets(ca),['CA','US']);
 await ca.api.search('Panda Express',{market:'US',type:'restaurant'});assert.equal(ca.requests.length,beforeUS+1);
 for(const {url,options} of ca.requests.filter(r=>r.url.includes('/restaurant-foods/'))){
  if(url.endsWith('/manifest.json'))assert.equal(options.cache,'no-cache');
  else{assert.equal(new URL(url,'https://getmacros.test').searchParams.get('v'),manifest.version);assert.equal(options.cache,'force-cache');}
 }
 const concurrent=session();await Promise.all([concurrent.api.load({market:'CA'}),concurrent.api.load({market:'US'})]);
 assert.equal(concurrent.requests.filter(r=>r.url==='/data/restaurant-foods/manifest.json').length,1);
 assert.equal(concurrent.requests.filter(r=>r.url==='/data/food-library/index.json').length,1);
 assert.deepEqual(new Set(requestedMarkets(concurrent)),new Set(['CA','US']));noRegistry(concurrent);

 for(const market of Object.keys(manifest.markets)){
  const partition=sourceJSON.read(path.join(root,'data/restaurant-foods',manifest.markets[market].file));
  assert.deepEqual(Array.isArray(partition)?partition:partition.records,registry.filter(r=>r.market===market),market+' partition must preserve every registry source value');
  const raw=registry.find(r=>r.market===market),expected=F.restaurant(raw),cold=session({market:market==='CA'?'US':'CA'});
  const actual=await cold.api.get(expected.id);assert.deepEqual(actual,expected);
  assert.deepEqual(requestedMarkets(cold),[market]);assert.equal(cold.requests.length,2);
  check(!cold.requests.some(({url})=>url.includes('/data/food-library/')),'Cold order link needs no reference index');noRegistry(cold);
 }
 const partial=registry.find(r=>r.market==='CA'&&r.cal!==null&&r.fat===null),unknown=session();
 check(partial,'Real partial Canadian source exists');const partialRecord=await unknown.api.get(F.restaurant(partial).id);
 assert.equal(partialRecord.nutrients.fat,null);assert.equal(F.scale(partialRecord,2,'serving').fat,null);assert.equal(partialRecord.sourcePublished,partial.sourceDate||null);
 const referenceOnly=session();const oil=await referenceOnly.api.get('fdc:2710186');
 assert.equal(oil.id,'fdc:2710186');check(!referenceOnly.requests.some(({url})=>url.includes('/restaurant-foods/')),'Reference deep link loads no restaurant market');
 const explicitReference=session();await explicitReference.api.search('olive oil',{market:'CA',type:'foundation'});
 check(!explicitReference.requests.some(({url})=>url.includes('/restaurant-foods/')),'Reference-only search skips restaurant manifest');
 const directReference=session(),meta=sourceJSON.read(path.join(root,'data/food-library/index.json')).find(r=>r.id==='fdc:2710186');
 assert.equal((await directReference.api.reference(meta.id,meta.shard)).id,meta.id);assert.equal(directReference.requests.length,1);

 let blocked=true;
 const restaurantFailure=session({failure:url=>blocked&&url.includes('/CA.json.gz')?new Response('',{status:503}):null});
 const fallback=await restaurantFailure.api.load({market:'CA'});
 check(fallback.index.length>0&&!fallback.index.some(r=>r.type==='restaurant'),'Restaurant failure retains reference fallback');
 check(restaurantFailure.events.some(e=>e.type==='food-source-unavailable'),'Restaurant failure is visible');
 blocked=false;const recovered=await restaurantFailure.api.load({market:'CA'});
 check(recovered.index.some(r=>r.type==='restaurant'),'Failed market cache can retry');assert.deepEqual(requestedMarkets(restaurantFailure),['CA','CA']);noRegistry(restaurantFailure);
 const referenceFailure=session({failure:url=>url==='/data/food-library/index.json'?new Response('',{status:503}):null});
 const localFallback=await referenceFailure.api.load({market:'CA'});
 check(localFallback.index.length>0&&localFallback.index.every(r=>r.type==='restaurant'&&r.market==='CA'),'Reference failure retains selected local restaurants');
 const labelFailure=session({labelsFail:true}),fallbackOil=await labelFailure.api.search('olive oil',{market:'CA'});
 check(fallbackOil.some(r=>r.id==='fdc:2710186'),'Label-provider failure retains reference result');
 await assert.rejects(()=>labelFailure.api.search('Kirkland',{market:'CA',type:'branded'}),/unavailable/);
 const allFail=session({failure:()=>new Response('',{status:503}),labelsFail:true});
 await assert.rejects(()=>allFail.api.search('PRIVATE note',{market:'CA'}),/could not load/);
 check(!allFail.requests.some(({url})=>url.includes('PRIVATE')||url.includes('note')),'Private query text never enters source URLs');
 const absent=session(),absentData=await absent.api.load({market:'XX'});
 check(absentData.index.every(r=>r.type!=='restaurant'),'Unpublished country cannot borrow restaurant rows');assert.deepEqual(requestedMarkets(absent),[]);
 await assert.rejects(()=>absent.api.get('order:XX:unknown'),/unavailable/);await assert.rejects(()=>absent.api.load({market:'../US'}),/country/);
 await assert.rejects(()=>absent.api.get('order:CA:PRIVATE saved note'),/unavailable/);
 check(!absent.requests.some(({url})=>url.includes('PRIVATE')),'Record IDs never become source paths');
 const alreadyDecoded=session({decoded:true}),caRaw=registry.find(r=>r.market==='CA');
 assert.equal((await alreadyDecoded.api.get(F.restaurant(caRaw).id)).market,'CA');
 const mixedRows=registry.filter(r=>r.market==='CA').map((r,i)=>i?r:{...r,market:'US',country:'US'});
 const mixed=session({failure:url=>url.includes('/CA.json.gz')?new Response(JSON.stringify(mixedRows)):null});
 await assert.rejects(()=>mixed.api.get(F.restaurant(caRaw).id),/inconsistent/);
 const unsafe=session({failure:url=>url==='/data/restaurant-foods/manifest.json'?new Response(JSON.stringify({...manifest,markets:{CA:{count:1,file:'../US.json.gz'}}})):null});
 await assert.rejects(()=>unsafe.api.get(F.restaurant(caRaw).id),/unsupported/);assert.equal(unsafe.requests.length,1);
 console.log(JSON.stringify({pass:true,checks,markets:Object.keys(manifest.markets),coldSelectedMarketBytes,initialMarketShardBytes:fs.statSync(path.join(root,'data/restaurant-foods/CA.json.gz')).size,wholeRegistryBytes:fs.statSync(path.join(root,'js/order-registry.json')).size,noWholeRegistryRequests:true},null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
