'use strict';
// Research-only snapshots; builds consume reviewed, pinned numeric records.
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'docs/master-completion-2026-10-13/restaurant-sources');
const targets=[
 ['freshii-menu.html','https://freshii.com/menu/'],
 ['freshii-2026-09.pdf','https://freshii.com/wp-content/uploads/2026/09/Freshii-Nutritionals-and-Allergens-Guide-EN-092026.pdf'],
 ['quesada-menu.html','https://quesada.ca/menu/'],
 ['quesada-2026-08.pdf','https://quesada.ca/wp-content/uploads/2026/08/Nutritional-Information_Quesada_regular-portions_AUG2026_EN.pdf'],
 ['mcdonalds-ca-bigmac.html','https://www.mcdonalds.com/ca/en-ca/product/big-mac.html'],
 ['mcdonalds-ca-item.json','https://www.mcdonalds.com/dnaapp/itemDetails?country=CA&language=en&showLiveData=true&item=200154&nutrient_req=Y'],
 ['kfc-ca.html','https://www.kfc.ca/nutrition-allergen']
];
(async()=>{
 await fs.mkdir(dir,{recursive:true});const report=[];
 for(const [file,url]of targets){
  try{const r=await fetch(url,{signal:AbortSignal.timeout(45000),headers:{'User-Agent':'GetMacros-source-review/1.0 (+https://getmacros.net/sources.html)'}});const b=Buffer.from(await r.arrayBuffer());
   const row={file,url,finalUrl:r.url,status:r.status,retrievedAt:'2026-10-13',bytes:b.length,contentType:r.headers.get('content-type'),sha256:crypto.createHash('sha256').update(b).digest('hex')};
   if(r.ok)await fs.writeFile(path.join(dir,file),b);report.push(row);console.log(file,r.status,b.length);
  }catch(e){report.push({file,url,error:String(e),retrievedAt:'2026-10-13'});console.log(file,String(e));}
 }
 await fs.writeFile(path.join(dir,'retrieval.json'),JSON.stringify(report,null,2)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1});
