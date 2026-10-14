// Download only three primary source PDFs for private rechecking; no dataset import.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const out=path.resolve('docs/clarity-release-2026-10-14/editorial-source-evidence');
fs.mkdirSync(out,{recursive:true});
const list=[
 ['tim-hortons','https://cdn.sanity.io/files/czqk28jt/prod_th_ca/147e592c99c865b50aca61832fa8ce3975cb0da5.pdf'],
 ['new-york-fries','https://www.newyorkfries.com/_files/ugd/bdf8b6_4b1456a15baf4c13acd16438966d77e6.pdf'],
 ['subway-ca','https://media.subway.com/dam/urn:aaid:aem:c0ee4b37-9376-42de-b2d6-2a3ffaadecb1/original/as/CAN_Nutrition_ENG_6_11_26.pdf']
];
(async()=>{
 const checks=[];
 for(const [id,url] of list){
  try{const res=await fetch(url,{signal:AbortSignal.timeout(45000)});const buf=Buffer.from(await res.arrayBuffer());
   if(!res.ok||!buf.subarray(0,5).equals(Buffer.from('%PDF-')))throw new Error('Status '+res.status+'; response is not a PDF');
   fs.writeFileSync(path.join(out,id+'.pdf'),buf);checks.push({id,url,status:res.status,bytes:buf.length,sha256:crypto.createHash('sha256').update(buf).digest('hex'),method:'Current official PDF downloaded; source table inspection separate'});
  }catch(error){checks.push({id,url,error:error.message,method:'Current PDF unavailable through this request; retained dated evidence stays labelled'});}
 }
 fs.writeFileSync(path.join(out,'retrieval.json'),JSON.stringify({retrievedAt:new Date().toISOString(),checks},null,2));console.log(JSON.stringify(checks));
})();
