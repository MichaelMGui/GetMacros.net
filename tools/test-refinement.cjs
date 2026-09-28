const fs=require('node:fs'),assert=require('node:assert/strict');
const{chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const{localAssets}=require('./browser-fixture.cjs');
(async()=>{
 const dir='docs/redesign/refinement';fs.mkdirSync(dir+'/states',{recursive:true});const report=[];
 for(const engine of [chromium,webkit]){
  const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});
  for(const theme of ['light','dark'])for(const width of [320,375,390,430,768,1440]){
   process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:960},reducedMotion:'reduce'});await localAssets(p);const errors=[];p.on('pageerror',e=>errors.push(e.message));
   await p.goto('http://127.0.0.1:4187/calculators.html');await p.evaluate(()=>document.fonts.ready);
   const rects=await p.locator('.single-macro-form .calc-submit').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return{top:r.top,height:r.height}}));
   if(width>640)assert.ok(Math.max(...rects.map(r=>r.top))-Math.min(...rects.map(r=>r.top))<2,'Single macro actions align');
   assert.ok(rects.every(r=>r.height>=48));
   for(const id of ['macro-form','protein-calc-form','fat-form','carb-calc-form'])await p.locator('#'+id).evaluate(f=>f.requestSubmit());
   for(const id of ['macro-results','protein-calc-results','fat-results','carb-calc-results']){assert.ok(await p.locator('#'+id).isVisible());assert.doesNotMatch(await p.locator('#'+id).innerText(),/NaN|Infinity/);}
   assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   if(engine===chromium&&[390,1440].includes(width))await p.screenshot({path:`${dir}/states/calculated-${theme}-${width}.png`,fullPage:true});
   await p.goto('http://127.0.0.1:4187/restaurant-meal-finder.html');
   if(width>640){const rows=await p.locator('.order-nutrition').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().top));for(let i=0;i<rows.length;i+=2)assert.ok(Math.abs(rows[i]-rows[i+1])<2,'Nutrition values align across result pairs');}
   if(width<=800)await p.locator('[data-open-filters]').click();
   await p.locator('.restaurant-picker summary').click();await p.locator('input[name=chain][value=Chipotle]').check();assert.match(await p.locator('.restaurant-picker summary').innerText(),/1 restaurant selected/);
   assert.ok(await p.locator('.restaurant-checks .restaurant-mark').count()===15);
   if(engine===chromium&&[390,1440].includes(width))await p.screenshot({path:`${dir}/states/filters-${theme}-${width}.png`});
   await p.locator('input[name=chain][value=Chipotle]').press('Escape');assert.equal(await p.locator('.restaurant-picker').getAttribute('open'),null);
   if(width<=800)await p.locator('[data-close-filters]').click();
   assert.equal(await p.locator('.order-identity>a').evaluateAll(es=>es.every(e=>e.textContent.trim()==='Chipotle')),true);
   await p.goto('http://127.0.0.1:4187/index.html');assert.equal(await p.locator('footer.market-footer').count(),1);assert.equal(await p.locator('.back-to-top').count(),0);
   if(width<=900)await p.locator('.nav-toggle').click();await p.locator('.nav-group-trigger').nth(1).click();
   if(engine===chromium&&[390,1440].includes(width))await p.screenshot({path:`${dir}/states/menu-${theme}-${width}.png`});
   assert.deepEqual(errors,[]);report.push({engine:engine.name(),theme,width,actionHeights:rects,status:'pass'});await p.close();
  }await b.close();
 }
 fs.writeFileSync(dir+'/geometry-and-interactions.json',JSON.stringify(report,null,2));console.log('PASS',report.length,'geometry, calculator results, restaurant filters, dismissal, footer and menu checks');
})().catch(e=>{console.error(e);process.exitCode=1});
