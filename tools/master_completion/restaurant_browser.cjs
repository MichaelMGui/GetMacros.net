'use strict';
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir=path.resolve(__dirname,'../../docs/master-completion-2026-10-13/restaurant-sources');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']});
 const targets=[['quesada','https://quesada.ca/menu/'],['mcdonalds','https://www.mcdonalds.com/ca/en-ca/product/big-mac.html'],['wendys','https://order.wendys.com/ca/en/national/menu'],['kfc','https://www.kfc.ca/nutrition-allergen']];
 const all=[];
 for(const [name,url]of targets){
  const ctx=await browser.newContext({viewport:{width:1280,height:900}}),page=await ctx.newPage(),requests=[];
  page.on('response',async r=>{const u=r.url();if(/nutrition|nutritional|itemDetails|itemList|getProduct|allergen|api\/|menu\/get/i.test(u)){requests.push({url:u,status:r.status()});if(r.status()===200&&/json/i.test(r.headers()['content-type']||'')){try{await fs.writeFile(path.join(dir,name+'-response-'+requests.length+'.json'),await r.body());}catch{}}}});
  try{
   const r=await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});await page.waitForTimeout(2500);
   await fs.writeFile(path.join(dir,name+'-browser.html'),await page.content());await fs.writeFile(path.join(dir,name+'-browser.txt'),await page.locator('body').innerText());await page.screenshot({path:path.join(dir,name+'-browser.png'),fullPage:true});
   if(name==='quesada'){
    const link=page.getByRole('link',{name:'Nutrition',exact:true}).first();const pdfUrl=await link.getAttribute('href');console.log('Quesada linked',pdfUrl);
    const rr=await ctx.request.get(pdfUrl,{timeout:45000});if(rr.ok()){const b=await rr.body();await fs.writeFile(path.join(dir,'quesada-2026-08.pdf'),b);all.push({file:'quesada-2026-08.pdf',url:pdfUrl,status:rr.status(),retrievedAt:'2026-10-13',bytes:b.length,sha256:crypto.createHash('sha256').update(b).digest('hex')});}
   }
   all.push({name,url,status:r.status(),requests});console.log(name,r.status(),(await page.locator('body').innerText()).slice(0,450),requests.slice(-5));
  }catch(e){all.push({name,url,error:String(e)});console.log(name,String(e));}
  await fs.writeFile(path.join(dir,name+'-browser-requests.json'),JSON.stringify(requests,null,2));await ctx.close();
 }
 await fs.writeFile(path.join(dir,'browser-retrieval.json'),JSON.stringify(all,null,2));await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
