'use strict';
// Ordinary public-source retrieval only. No auth, challenge bypass or API keys.
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..');
const dir=path.join(root,'docs/master-release-2026-10-12/sources');
const sources=[
 ['subway-ca.pdf','https://media.subway.com/dam/urn:aaid:aem:c0ee4b37-9376-42de-b2d6-2a3ffaadecb1/original/as/CAN_Nutrition_ENG_6_11_26.pdf'],
 ['dominos-ca.pdf','https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf'],
 ['pizzanova.html','https://pizzanova.com/'],
 ['mcdonalds-ca.html','https://www.mcdonalds.com/ca/en-ca/about-our-food/nutrition-calculator.html'],
 ['mcdonalds-ca-bigmac.html','https://www.mcdonalds.com/ca/en-ca/product/big-mac.html'],
 ['pizza-pizza-small.html','https://www.pizzapizza.ca/about-us/nutrition/small/'],
 ['kfc-ca.html','https://www.kfc.ca/nutrition-and-allergy-info'],
 ['wendys-ca.html','https://order.wendys.com/ca/en/national/menu'],
 ['mcdonalds-calculator.js','https://www.mcdonalds.com/etc.clientlibs/mcdonalds/clientlibs/clientlib-site-nutrition-calculator.lc-bdc0c6258eeb128cdd18d55f458b3f77-lc.min.js'],
 ['mcdonalds-global.js','https://www.mcdonalds.com/etc.clientlibs/mcdonalds/clientlibs/clientlib-site-global.lc-a6a5997afbd6e081248849fe87a34bf7-lc.min.js'],
 ['kfc-main.js','https://www.kfc.ca/static/js/main.0d027e66.chunk.js'],
 ['pizzanova-www.html','https://www.pizzanova.com/'],
 ['pizzanova-nutrition.html','https://pizzanova.com/nutrition/'],
 ['pizza-pizza-medium.html','https://www.pizzapizza.ca/about-us/nutrition/medium-pizza/'],
 ['marybrowns-july2026.pdf','https://marybrowns.com/wp-content/uploads/Mary-Browns-Allergen-and-Nutritionals-July-2026.pdf'],
 ['booster-sept2026.pdf','https://cdn.shopify.com/s/files/1/0673/9371/6482/files/2026-09-NutritionGuide-ENG.pdf?v=1788534813']
];
(async()=>{
 await fs.mkdir(dir,{recursive:true});let prior=[];try{prior=JSON.parse(await fs.readFile(path.join(dir,'restaurant-retrieval.json'),'utf8'));}catch{}
 const selected=process.argv.includes('--latest')?sources.slice(-2):process.argv.includes('--followup')?sources.slice(8):sources;
 const result=await Promise.allSettled(selected.map(async([file,url])=>{
  const r=await fetch(url,{signal:AbortSignal.timeout(45000),headers:{'User-Agent':'GetMacros public nutrition source review/1.0'}});
  if(!r.ok)throw Error('HTTP '+r.status);const b=Buffer.from(await r.arrayBuffer());if(b.length>15000000)throw Error('size limit');
  await fs.writeFile(path.join(dir,file),b);return {file,url,finalUrl:r.url,bytes:b.length,retrieved:'2026-10-12',sha256:crypto.createHash('sha256').update(b).digest('hex')};
 }));
 const latest=result.map((r,i)=>r.status==='fulfilled'?r.value:{file:selected[i][0],url:selected[i][1],error:String(r.reason)});
 const report=[...prior.filter(r=>!selected.some(s=>s[0]===r.file)),...latest];
 await fs.writeFile(path.join(dir,'restaurant-retrieval.json'),JSON.stringify(report,null,2));report.forEach(r=>console.log(JSON.stringify(r)));
})().catch(e=>{console.error(e);process.exitCode=1;});
