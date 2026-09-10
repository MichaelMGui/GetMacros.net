const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({channel:'msedge'});
 try{for(const theme of ['light','dark'])for(const file of ['index.html','restaurant-meal-finder.html','calculators.html','search.html']){
  const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'no-preference'});
  await page.addInitScript(t=>{localStorage.setItem('gm-theme',t);window.shifts=[];window.shiftSources=[];new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput){window.shifts.push(e.value);window.shiftSources.push(e.sources.map(s=>({node:s.node?.className,previous:s.previousRect,current:s.currentRect})));}}).observe({type:'layout-shift',buffered:true});},theme);
  await page.route('**/*',async r=>{
   const u=new URL(r.request().url());if(u.hostname!=='127.0.0.1'){await new Promise(resolve=>setTimeout(resolve,1800));return r.abort()}
   const file=path.resolve('.'+decodeURIComponent(u.pathname));
   if(!file.startsWith(process.cwd()+path.sep)||!fs.existsSync(file))return r.fulfill({status:404,body:''});
   const ext=path.extname(file);await new Promise(resolve=>setTimeout(resolve,ext==='.woff2'?900:ext==='.svg'?650:ext==='.js'?350:100));
   await r.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.woff2':'font/woff2'})[ext]||'application/octet-stream'});
  });
  await page.goto('http://127.0.0.1:4174/'+file,{waitUntil:'domcontentloaded'});
  const before=await page.locator('main h1').boundingBox();
  await page.waitForLoadState('load');await page.waitForTimeout(400);
  const after=await page.locator('main h1').boundingBox();
  assert.ok(Math.abs(before.y-after.y)<1&&Math.abs(before.height-after.height)<1,`${file}: heading moved after DOM ready`);
  const result=await page.evaluate(()=>({cls:window.shifts.reduce((a,b)=>a+b,0),sources:window.shiftSources,lateFade:document.querySelector('main').getAnimations().length}));
  assert.ok(result.cls<(file==='restaurant-meal-finder.html'?.03:.01),`${file} ${theme}: layout shift ${result.cls}`);
  assert.equal(result.lateFade,0,`${file}: late page fade`);
  console.log(theme,file,'CLS',result.cls.toFixed(4));if(result.cls>.02)console.log(JSON.stringify(result.sources));await page.close();
 }}finally{await browser.close()}
 console.log('PASS: delayed images, fonts, scripts and ad requests do not move headlines or replay page fades.');
})().catch(e=>{console.error(e);process.exitCode=1});
