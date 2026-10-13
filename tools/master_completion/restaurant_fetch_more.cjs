'use strict';
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const dir=path.resolve(__dirname,'../../docs/master-completion-2026-10-13/restaurant-sources');
const targets=[
 ['nyf-current.pdf','https://www.newyorkfries.com/_files/ugd/bdf8b6_4b1456a15baf4c13acd16438966d77e6.pdf'],
 ['nyf-source.html','https://www.newyorkfries.com/fries'],
 ['nyf-privacy.html','https://www.newyorkfries.com/privacy-policy'],
 ['pita-pit-current.pdf','https://pitapit.ca/wp-content/uploads/2026/08/Pita-Pit-Nutritionals-Allergen-Guide-Aug-2026-1.pdf'],
 ['pita-pit-terms.html','https://pitapit.ca/terms-of-use/'],
 ['dq-ca-source.html','https://www.dairyqueen.com/en-ca/nutrition/food-treats/'],
 ['quesada-www.pdf','https://www.quesada.ca/wp-content/uploads/2026/08/Nutritional-Information_Quesada_regular-portions_AUG2026_EN.pdf']
];
(async()=>{
 const report=[];
 for(const[file,url]of targets){try{const r=await fetch(url,{signal:AbortSignal.timeout(25000)}),b=Buffer.from(await r.arrayBuffer());if(r.ok)await fs.writeFile(path.join(dir,file),b);report.push({file,url,finalUrl:r.url,status:r.status,bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex'),retrievedAt:'2026-10-13'});console.log(file,r.status,b.length)}catch(e){report.push({file,url,error:String(e),retrievedAt:'2026-10-13'});console.log(file,String(e));}}
 await fs.writeFile(path.join(dir,'retrieval-more.json'),JSON.stringify(report,null,2)+'\n');
})().catch(e=>{console.error(e);process.exitCode=1});
