// Article-to-workspace integration against real local source records.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const cases=[
 ['/tim-hortons-canada-protein-latte-vs-latte.html',['Latte - Medium','Protein Latte - Medium'],'portions'],
 ['/subway-turkey-breast-canada-vs-mexico.html',['Turkey Breast','Mexico'],'portions'],
 ['/kirkland-canada-macadamia-vs-mixed-nuts.html',['Macadamia Nuts','Unsalted Mixed Nuts'],'100g']
];
(async()=>{
 if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});const checks=[];
 try{
  for(const theme of ['light','dark'])for(const [route,names,basis] of cases){
   const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',reducedMotion:'reduce'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(base+route,{waitUntil:'networkidle'});
   const action=page.locator('main a[href^="/compare-foods.html?"]').first();await action.click();await page.waitForURL('**/compare-foods.html?**');
   await page.waitForFunction(names=>names.every(n=>document.querySelector('[data-food-compare-content]')?.textContent.includes(n)),names,{timeout:30000});
   assert.equal(await page.locator('[data-food-compare-basis]').inputValue(),basis);assert.deepEqual(errors,[]);
   const content=await page.locator('[data-food-compare-content]').innerText();assert(!/NaN|undefined/.test(content));
   const url=new URL(page.url());assert.equal(url.searchParams.getAll('item').length,2);assert(!url.searchParams.has('note'));
   const shot=path.resolve('docs/clarity-release-2026-10-14/editorial-screenshots/journey-'+route.slice(1).replace('.html','')+'-'+theme+'.png');await page.screenshot({path:shot,fullPage:true});
   checks.push({route,theme,names,basis,href:page.url().replace(base,'https://getmacros.net'),status:'pass',runtimeErrors:errors,screenshot:shot});await context.close();
  }
 }finally{await browser.close();await new Promise(r=>server.close(r));}
 fs.writeFileSync('docs/clarity-release-2026-10-14/editorial-link-journeys.json',JSON.stringify({checkedAt:new Date().toISOString(),checks},null,2));console.log('PASS: '+checks.length+' native article-to-comparison journeys.');
})().catch(e=>{console.error(e);server.close();process.exit(1)});
