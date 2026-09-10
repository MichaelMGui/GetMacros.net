/* The first question must work while quiz downloads are delayed. */
const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){
 const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark']){
  process.env.GM_TEST_THEME=theme;
  const p=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});await localAssets(p);
  let release;const gate=new Promise(r=>release=r);
  await p.route('**/js/meal-*.js*',async route=>{await gate;await route.fallback();});
  await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html',{waitUntil:'commit'});
  await p.locator('#meal-quiz h2').waitFor({state:'visible'});
  assert.equal(await p.locator('.quiz-option').count(),6);
  const original=await p.locator('.step-goal').innerText();
  await p.locator('label:has([data-facet="goal"][value="protein"])').click();
  await p.locator('[data-go="1"]').click();
  assert.ok(await p.locator('.quiz-load-note').isVisible());
  release();await p.waitForLoadState('domcontentloaded');
  await p.waitForFunction(()=>document.querySelector('#meal-quiz h2')?.textContent==='How much would you like to eat?');
  await p.locator('[data-go="-1"]').click();
  await p.waitForFunction(()=>document.querySelector('#meal-quiz h2')?.textContent==='What’s your goal?');
  assert.equal(await p.locator('[data-facet="goal"][value="protein"]').isChecked(),true);
  assert.equal(await p.locator('.step-goal').innerText(),original,'Static and runtime question copy must match');
  assert.equal(await p.locator('.quiz-load-note').count(),0);
  console.log('PASS',engine.name(),theme,'immediate question, preserved selection, queued Continue, matching runtime copy');await p.close();
 }}finally{await browser.close()}
}})().catch(e=>{console.error(e);process.exitCode=1});
