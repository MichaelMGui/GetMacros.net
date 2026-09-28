const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{const report=[];for(const engine of [chromium,webkit]){
 const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark'])for(const width of [320,390,768,1024,1440]){
  process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(p);
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>Promise.reject(new Error('Unavailable'))}}));
  const go=q=>p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html'+q);
  await go('?minFiber=8&maxSodium=1500&complete=0');
  assert.ok(await p.locator('.meal-row').count()>0);
  assert.equal(await p.locator('.meal-row').evaluateAll(rows=>rows.every(r=>{const m=GM_MEALS[Number(r.dataset.mealId)];return m.f>=8&&m.na!==null&&m.na<=1500})),true);
  if(width<=800)await p.locator('[data-open-filters]').click();
  await p.locator('summary').filter({hasText:'More preferences'}).click();
  const sodium=p.locator('[name=maxSodium]');await sodium.fill('1');await sodium.dispatchEvent('change');
  assert.equal(await p.locator('.finder-empty').count(),1);assert.equal(await sodium.evaluate(e=>e===document.activeElement),true);
  await sodium.fill('1500');await sodium.dispatchEvent('change');assert.ok(await p.locator('.meal-row').count()>0);
  await sodium.fill('-1');await sodium.dispatchEvent('change');assert.equal(new URL(p.url()).searchParams.get('maxSodium'),'1500');
  await sodium.fill('1500');await sodium.dispatchEvent('change');
  if(width<=800){await p.keyboard.press('Escape');assert.equal(await p.locator('.filter-dialog').evaluate(e=>e.open),false);assert.equal(await p.locator('[data-open-filters]').evaluate(e=>e===document.activeElement),true);}
  await p.reload();assert.equal(await p.locator('[name=maxSodium]').inputValue(),'1500');
  await p.locator('[data-share]').click();assert.equal(await p.locator('[aria-label="Results link"]').inputValue(),p.url());
  await go('?chain=Chick-fil-A&goal=protein');
  assert.equal(await p.locator('.meal-row').evaluateAll(rows=>rows.every(r=>GM_MEALS[Number(r.dataset.mealId)].chain==='Chick-fil-A')),true);
  const sandwich=p.locator('.meal-row').filter({hasText:'Grilled Chicken Sandwich'});assert.match(await sandwich.innerText(),/206 g/);assert.match(await sandwich.innerText(),/11 g/);
  await p.locator('[data-compare]').nth(0).check();await p.locator('[data-compare]').nth(1).check();assert.equal(await p.locator('[data-compare]').nth(2).isDisabled(),true);
  await p.locator('[data-open-compare]').click();assert.equal(await p.locator('.compare-dialog tbody tr').count(),6);assert.match(await p.locator('.compare-dialog').innerText(),/Not verified/);
  await p.keyboard.press('Escape');assert.equal(await p.locator('.compare-dialog').evaluate(e=>e.open),false);
  await p.locator('[data-save]').first().click();assert.equal(await p.locator('[data-save]').first().getAttribute('aria-pressed'),'true');
  if(width<=800)await p.locator('[data-open-filters]').click();await p.locator('#finder-filters [type=reset]').click();assert.equal(new URL(p.url()).search,'');
  if(width<=800)await p.locator('[data-close-filters]').click();
  await go('?minFiber=999&maxSodium=-1');assert.equal(new URL(p.url()).search,'');
  await p.locator('[name=sort]').selectOption('protein');const protein=await p.locator('.meal-row').evaluateAll(rows=>rows.map(r=>GM_MEALS[Number(r.dataset.mealId)].p));assert.deepEqual(protein,[...protein].sort((a,b)=>b-a));
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);assert.deepEqual(errors,[]);
  report.push({engine:engine.name(),theme,width,status:'pass'});await p.close();console.log('PASS finder',engine.name(),theme,width);
 }}finally{await b.close();}
}fs.writeFileSync('docs/redesign/reset/finder-checks.json',JSON.stringify({scope:'Direct results, strict filters and unknown values, focus stability, invalid inputs, URL persistence, native modal dismissal, comparison, saving, reset and sorting',report},null,2));})().catch(e=>{console.error(e);process.exitCode=1});
