/* Reference foods and the selected restaurant market load independently. */
(function(){'use strict';
 const root=window,F=root.GetMacrosFood,cache=new Map(),restaurantPools=new Map(),loads=new Map();
 let referenceReady,restaurantReady,brandedReady;
 const unavailable='Food data could not load. Try again when connected.';
 function marketFor(options={}){const value=String(options.market||root.GetMacrosMarket?.current||'US').toUpperCase();if(!/^[A-Z]{2}$/.test(value))throw Error('Choose a published restaurant country.');return value;}
 function warn(message){if(root.dispatchEvent&&root.CustomEvent)root.dispatchEvent(new root.CustomEvent('food-source-unavailable',{detail:{message}}));}
 async function branded(){if(root.GetMacrosBranded)return root.GetMacrosBranded;if(!brandedReady)brandedReady=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='/js/branded-foods.js';script.onload=()=>resolve(root.GetMacrosBranded);script.onerror=()=>{brandedReady=null;reject(Error('Branded food search could not load. Try a reference food.'));};document.head.append(script);});return brandedReady;}
 async function json(url){
  const response=await fetch(url,{cache:url.endsWith('/manifest.json')?'no-cache':'force-cache'});
  if(!response.ok)throw Error(unavailable);
  if(!/\.json\.gz(?:\?|$)/.test(url))return response.json();
  const bytes=new Uint8Array(await response.arrayBuffer());
  // A host may already have removed HTTP content encoding. Never decompress twice.
  if(bytes[0]!==31||bytes[1]!==139)return JSON.parse(new TextDecoder().decode(bytes));
  if(!root.DecompressionStream||!root.Response)throw Error('Compressed food lookup needs an updated browser. Your saved diary is unchanged.');
  return new root.Response(new root.Response(bytes).body.pipeThrough(new root.DecompressionStream('gzip'))).json();
 }
 async function references(){
  if(!referenceReady)referenceReady=Promise.all([json('/data/food-library/manifest.json'),json('/data/food-library/index.json')]).then(([manifest,index])=>({manifest,index:index.map(row=>({...row,search:F.text(row.name)}))})).catch(error=>{referenceReady=null;throw error;});
  return referenceReady;
 }
 async function restaurantManifest(){
  if(!restaurantReady)restaurantReady=json('/data/restaurant-foods/manifest.json').then(manifest=>{if(!manifest||!manifest.version||!manifest.markets)throw Error('Restaurant food sources are unavailable.');return manifest;}).catch(error=>{restaurantReady=null;throw error;});
  return restaurantReady;
 }
 async function restaurants(market){
  const manifest=await restaurantManifest(),source=manifest.markets[market];
  if(!source)return [];
  if(!Number.isInteger(source.count)||source.count<0||![market+'.json',market+'.json.gz'].includes(source.file))throw Error('This restaurant source version is unsupported.');
  const key=market+':'+manifest.version;
  if(!restaurantPools.has(key))restaurantPools.set(key,json('/data/restaurant-foods/'+source.file+'?v='+encodeURIComponent(manifest.version)).then(payload=>{
   const rows=Array.isArray(payload)?payload:payload.records;
   if(!Array.isArray(rows)||rows.length!==source.count||rows.some(row=>row.market!==market||row.country&&row.country!==market))throw Error('This restaurant country source is inconsistent. Search another source.');
   const converted=rows.map(F.restaurant);
   if(new Set(converted.map(row=>row.id)).size!==converted.length)throw Error('This restaurant source contains duplicate identities.');
   converted.forEach(row=>cache.set(row.id,row));
   return converted.map(row=>({id:row.id,name:row.name,type:row.type,category:row.category,market:row.market,search:F.text(row.name)}));
  }).catch(error=>{restaurantPools.delete(key);throw error;}));
  return restaurantPools.get(key);
 }
 async function reference(id,shard){
  if(!/^fdc:\d+$/.test(id)||!/^[a-f0-9]{2}$/.test(shard))throw Error('That reference food is unavailable. Search again.');
  if(cache.has(id))return cache.get(id);
  const key='shard:'+shard;
  if(!cache.has(key))cache.set(key,json('/data/food-library/records/'+shard+'.json').then(rows=>{rows.forEach(row=>{row.sourceUrl=row.sourceUrl||'https://fdc.nal.usda.gov/food-details/'+row.sourceRef+'/nutrients';cache.set(row.id,row);});return rows;}).catch(error=>{cache.delete(key);throw error;}));
  await cache.get(key);
  const record=cache.get(id);if(!record)throw Error('That reference food is unavailable. Search again.');return record;
 }
 async function load(options={}){
  const market=marketFor(options),onlyRestaurants=options.type==='restaurant',onlyReferences=['reference','foundation','legacy','prepared'].includes(options.type),key=market+':'+(onlyRestaurants?'restaurant':onlyReferences?'reference':'all');
  if(!loads.has(key))loads.set(key,(async()=>{
   const tasks=[onlyRestaurants?Promise.resolve(null):references(),onlyReferences?Promise.resolve([]):restaurants(market)];
   const [referenceResult,restaurantResult]=await Promise.allSettled(tasks);
   const failures=[referenceResult,restaurantResult].filter(result=>result.status==='rejected');
   if(failures.length){loads.delete(key);failures.forEach(()=>warn('A food source is temporarily unavailable. Results from available sources remain usable.'));}
   const referenceData=referenceResult.status==='fulfilled'?referenceResult.value:null;
   const local=restaurantResult.status==='fulfilled'?restaurantResult.value:[];
   if(onlyRestaurants&&restaurantResult.status==='rejected'||onlyReferences&&referenceResult.status==='rejected'||failures.length===2)throw Error(unavailable);
   return {manifest:referenceData?.manifest||null,index:[...(referenceData?.index||[]),...local]};
  })().catch(error=>{loads.delete(key);throw error;}));
  return loads.get(key);
 }
 async function get(id){
  const key=String(id);
  if(key.startsWith('branded:')||key.startsWith('cnf:'))return (await branded()).get(key);
  if(cache.has(key))return cache.get(key);
  if(key.startsWith('order:')){
   const match=/^order:([A-Z]{2}):.+$/.exec(key);
   if(!match)throw Error('That restaurant food is unavailable. Search again.');
   await restaurants(match[1]);
   if(!cache.has(key))throw Error('That restaurant food is unavailable in this country source. Search again.');
   return cache.get(key);
  }
  if(!/^fdc:\d+$/.test(key))throw Error('That food is unavailable. Search again.');
  const {index}=await references(),item=index.find(row=>row.id===key);
  if(!item)throw Error('That food is unavailable. Search again.');
  return reference(key,item.shard);
 }
 root.GetMacrosLibrary={load,get,reference,async sourceSummary(){return (await branded()).manifest();},async search(q,options={}){
  const scoped={...options,market:marketFor(options)},code=/^[\d\s-]{8,18}$/.test(String(q));
  let index=[],classicError;
  if(scoped.type!=='branded'&&!code){try{index=(await load(scoped)).index;}catch(error){classicError=error;warn('Reference or restaurant foods are unavailable. Available label sources can still be searched.');}}
  const classic=scoped.type==='branded'?[]:F.search(index,q,{...scoped,limit:scoped.limit||30});
  if(scoped.type&&!['branded','reference'].includes(scoped.type)){if(classicError)throw classicError;return classic;}
  let groceries=[],provider,labelError;
  try{provider=await branded();groceries=await provider.search(q,{...scoped,limit:100});}catch(error){labelError=error;if(scoped.type==='branded')throw error;warn(error.message);}
  if(classicError&&labelError)throw classicError;
  if(code)return groceries.slice(0,scoped.limit||30);
  const query=provider?.queryTokens(q).join(' ')||q;
  return F.search([...classic,...groceries],query,{...scoped,limit:scoped.limit||30});
 }};
})();
