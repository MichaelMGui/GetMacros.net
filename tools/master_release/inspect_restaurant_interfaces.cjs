'use strict';
const fs=require('node:fs/promises'),path=require('node:path');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir=path.resolve(__dirname,'../../docs/master-release-2026-10-12/sources');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']});
 const targets=process.argv.includes('--pizza-pizza')?[['pizza-pizza','https://www.pizzapizza.ca/about-us/nutrition/small-pizza/']]:[['pizza-nova','https://pizzanova.com/nutrition'],['mcdonalds','https://www.mcdonalds.com/ca/en-ca/about-our-food/nutrition-calculator.html'],['kfc','https://www.kfc.ca/nutrition-allergen']];
 for(const [name,url] of targets){
  const ctx=await browser.newContext({viewport:{width:1280,height:900}}),page=await ctx.newPage(),requests=[];
  page.on('response',async r=>{const u=r.url();if(/itemList|itemDetails|getProduct|nutrit|allergen|food_information/i.test(u)){requests.push({url:u,status:r.status()});if(r.status()===200&&/json/i.test(r.headers()['content-type']||'')){try{const b=await r.body();await fs.writeFile(path.join(dir,name+'-response-'+requests.length+'.json'),b);}catch{}}}});
  try{await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});await page.waitForTimeout(3000);const text=await page.locator('body').innerText();await fs.writeFile(path.join(dir,name+'-rendered.txt'),text);await fs.writeFile(path.join(dir,name+'-rendered.html'),await page.content());await page.screenshot({path:path.join(dir,name+'-interface.png'),fullPage:true});if(name==='pizza-pizza')await page.locator('table').first().screenshot({path:path.join(dir,name+'-table.png')});console.log(name,text.slice(0,1700),requests.slice(-6));}catch(e){console.log(name,String(e));}
  await fs.writeFile(path.join(dir,name+'-requests.json'),JSON.stringify(requests,null,2));await ctx.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
