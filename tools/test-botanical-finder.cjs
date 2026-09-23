const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{let checks=0;for(const engine of [chromium,webkit]){const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});try{
for(const theme of ['light','dark'])for(const width of [320,390,768,1024,1440]){
 process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(p);
 await p.addInitScript(()=>{Object.defineProperty(navigator,'share',{configurable:true,value:undefined});Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>Promise.reject(new Error('Unavailable'))}});});
 await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html?minFiber=8&maxSodium=1500&complete=0');
 const matches=await p.locator('#meal-quiz').evaluate(e=>e._matches);assert.ok(matches.length>0);assert.ok(matches.every(m=>m.f!==null&&m.f>=8&&m.na!==null&&m.na<=1500));
 const sodium=p.locator('[data-max-sodium]');await sodium.focus();await sodium.fill('1');await sodium.dispatchEvent('change');assert.equal(await p.locator('.empty-results').count(),1);assert.equal(await sodium.evaluate(e=>e===document.activeElement),true);
 await sodium.fill('1500');await sodium.dispatchEvent('change');assert.equal(await p.locator('.meal-card').count()>0,true);assert.equal(new URL(p.url()).searchParams.get('maxSodium'),'1500');
 await p.reload();assert.equal(await sodium.inputValue(),'1500');assert.equal(await p.locator('[data-min-fiber]').inputValue(),'8');
 await p.locator('[data-share]').click();assert.equal(await p.locator('.share-link-field input').inputValue(),p.url());assert.equal(await p.locator('.share-link-field input').evaluate(e=>e===document.activeElement),true);
 await sodium.fill('-1');await sodium.dispatchEvent('change');assert.equal(await sodium.evaluate(e=>e.validity.valid),false);assert.equal(new URL(p.url()).searchParams.get('maxSodium'),'1500');
 await sodium.fill('1500');await sodium.dispatchEvent('change');
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 if(width===390||width===1440)await p.screenshot({path:`docs/redesign/screenshots/finder-results-${engine.name()}-${theme}-${width}.png`,fullPage:true});
 await p.locator('[data-reset]').click();assert.equal(new URL(p.url()).search,'');
 await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html?goal=protein&minFiber=999&maxSodium=-1');assert.equal(new URL(p.url()).searchParams.has('minFiber'),false);assert.equal(new URL(p.url()).searchParams.has('maxSodium'),false);
 await p.close();checks++;
}}finally{await b.close()}}fs.writeFileSync('docs/redesign/finder-checks.json',JSON.stringify({checks,engines:['Chromium','WebKit'],widths:[320,390,768,1024,1440],themes:['light','dark'],scope:'Numeric filters, null exclusion, invalid limits, URL reload, focus retention, reset and overflow',failures:[]},null,2));console.log('PASS',checks,'finder combinations');})().catch(e=>{console.error(e);process.exitCode=1});
