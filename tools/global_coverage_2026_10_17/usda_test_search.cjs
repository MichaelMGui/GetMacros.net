/* Run the real search adapter against source-backed U.S. grocery fixtures. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const sourceJSON=require('../source-json.cjs'),F=require('../../js/food-core.js');
const root=path.resolve(__dirname,'../..'),evidence=sourceJSON.read(path.join(root,'docs/global-coverage-2026-10-17/usda/query-fixtures.json'));
let bytes=0;const requests=[],events=[];
const context={crypto:require('node:crypto').webcrypto,TextEncoder,TextDecoder,Response,DecompressionStream,console,Map,Set,Promise,
 CustomEvent:class{constructor(type,options){this.type=type;this.detail=options?.detail;}},dispatchEvent:event=>events.push(event),
 fetch:async(url,options={})=>{requests.push({url:String(url),cache:options.cache});return sourceJSON.fileResponse(root,url,n=>bytes+=n);}};
context.window=context;vm.runInNewContext(fs.readFileSync(path.join(root,'js/branded-foods.js'),'utf8'),context);
const G=context.GetMacrosBranded,plain=value=>JSON.parse(JSON.stringify(value));

(async()=>{
 const state=await G.manifest({market:'US',type:'branded'}),usda=state.sources.find(source=>source.id==='usda');
 assert(usda?.manifest);assert.equal(usda.manifest.profileCount,446810);assert.equal(usda.manifest.version,evidence.sourceVersion);
 assert.equal(usda.manifest.jsonEncoding,'gzip');assert.equal(usda.manifest.recordShardPrefix,3);
 assert.equal(evidence.fixtures.length,18);assert.equal(new Set(evidence.fixtures.map(row=>row.id)).size,18);
 const results=[];let missingSnapshots=0,countryCases=0;
 for(const fixture of evidence.fixtures){
  const beforeBytes=bytes,beforeRequests=requests.length;
  const rows=await G.search(fixture.query,{market:'US',type:'branded',limit:100});
  assert(rows.some(row=>row.id===fixture.id),'name query missed '+fixture.id+': '+fixture.query);
  assert(rows.every(row=>row.market==='US'&&row.type==='branded'));
  assert.equal(new Set(rows.map(row=>row.id)).size,rows.length,'duplicate result IDs');
  const codeRows=await G.search(fixture.barcodeQuery,{market:'US',type:'branded',limit:100});
  assert(codeRows.some(row=>row.id===fixture.id),'barcode query missed '+fixture.id);
  const record=await G.get(fixture.id);
  assert.equal(record.market,fixture.market);assert.equal(record.market,'US');assert.equal(record.brand,fixture.brand);
  assert.equal(record.name,fixture.name);assert.equal(record.barcode,fixture.barcode);assert.equal(record.barcodeNormalized,fixture.barcodeNormalized);
  assert.deepEqual(plain(record.sourceServing),fixture.sourceServing);assert.deepEqual(plain(record.basis),fixture.basis);
  assert.equal(record.sourceChecked,null);assert.equal(record.license,'CC0-1.0');assert.equal(record.status,'manufacturer-label-imported');
  assert.equal(record.sourceVersionRank,1);assert.equal(record.sourceVersionRole,'latest-in-bulk');assert.equal(record.latestSourceId,record.id);
  const measure=record.basis.unit==='serving'?'serving':'source-serving',snapshot=F.snapshot(record,1,measure);
  assert.equal(F.validateSnapshot(snapshot),snapshot);
  const missing=F.fields.filter(field=>record.nutrients[field]===null);assert(missing.length,'fixture should exercise unknown nutrients');
  const scaled=F.scale(record,2,measure),restored=F.fromSnapshot(snapshot);
  for(const field of missing){assert.equal(snapshot.nutrients[field],null);assert.equal(scaled[field],null);assert.equal(restored.nutrients[field],null);}
  missingSnapshots++;
  if(record.sourceServing.unit==='ml'){assert.equal(record.portions.length,0);assert.throws(()=>F.scale(record,100,'g'));}
  const ca=await G.search(fixture.barcodeQuery,{market:'CA',type:'branded',limit:100});
  assert(ca.every(row=>row.market==='CA'&&row.id!==fixture.id),'Canadian query borrowed a U.S. label');countryCases++;
  results.push({label:fixture.label,query:fixture.query,id:fixture.id,nameHits:rows.length,barcodeHits:codeRows.length,bytes:bytes-beforeBytes,requests:requests.length-beforeRequests,unknownFields:missing.length});
 }
 // Query all supported markets without ever borrowing a U.S.-attributed row.
 for(const market of ['CA','MX','GB','IE','AU','NZ','JP']){
  const rows=await G.search(evidence.fixtures[0].barcodeQuery,{market,type:'branded',limit:100});
  assert(rows.every(row=>row.market===market&&!row.id.startsWith('branded:usda:2757603')));countryCases++;
 }
 const usdaRequests=requests.filter(request=>request.url.includes('/usda/'));
 assert(usdaRequests.some(request=>request.url.includes('/records/')&&request.url.includes('.json.gz?v='+evidence.sourceVersion)),'real gzip record transport was not exercised');
 for(const request of usdaRequests){
  if(request.url.endsWith('/manifest.json'))assert.equal(request.cache,'no-cache');
  else{assert(request.url.includes('.json.gz?v='+evidence.sourceVersion),'unversioned or uncompressed USDA body');assert.equal(request.cache,'force-cache');}
 }
 assert(!events.some(event=>event.type==='food-source-unavailable'),'a source failed during the real catalogue checks');
 const report={pass:true,sourceVersion:evidence.sourceVersion,realNameQueries:results.length,realBarcodeQueries:results.length,countryIsolationCases:countryCases,unknownNutrientSnapshots:missingSnapshots,actualGzipSourceRequests:usdaRequests.length,totalBytes:bytes,totalRequests:requests.length,results};
 fs.writeFileSync(path.join(root,'docs/global-coverage-2026-10-17/usda/runtime-search.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({...report,results:undefined},null,2));
})().catch(error=>{console.error(error);process.exitCode=1;});
