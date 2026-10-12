'use strict';
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'docs/master-release-2026-10-12/sources');
(async()=>{
 const cfg=JSON.parse(await fs.readFile(path.join(dir,'mcdonalds-calculator-config.json'),'utf8'));
 const categories=JSON.parse(cfg['data-product-data']).categoryList;
 const ids=[...new Set(categories.flatMap(c=>c.productId))];
 const params=new URLSearchParams({country:'CA',language:'en',showLiveData:'true',nutrient_req:'Y',item:ids.map(i=>i+'()-').join('')});
 const sources=[['mcdonalds-ca-items.json','https://www.mcdonalds.com/dnaapp/itemList?'+params.toString()],['pizzanova-page.js','https://pizzanova.com/_next/static/chunks/pages/%5B...slug%5D-787076fe69a9256d.js'],['pizzanova-app.js','https://pizzanova.com/_next/static/chunks/pages/_app-447b2694eac64ddf.js']];
 const report=[];
 for(const [file,url] of sources){try{
  const r=await fetch(url,{signal:AbortSignal.timeout(60000)});if(!r.ok)throw Error('HTTP '+r.status);const b=Buffer.from(await r.arrayBuffer());await fs.writeFile(path.join(dir,file),b);report.push({file,url,sha256:crypto.createHash('sha256').update(b).digest('hex'),bytes:b.length,retrieved:'2026-10-12'});
 }catch(e){report.push({file,url,error:String(e)});}}
 await fs.writeFile(path.join(dir,'dynamic-retrieval.json'),JSON.stringify(report,null,2));console.log(report.map(r=>({file:r.file,bytes:r.bytes,error:r.error})));console.log('Official calculator listed '+ids.length+' unique IDs');
})().catch(e=>{console.error(e);process.exitCode=1;});
