const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 for(const engine of [chromium,webkit]){
  const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
  try{for(const theme of ['light','dark']){
   process.env.GM_TEST_THEME=theme;
   const page=await browser.newPage({viewport:{width:320,height:844},reducedMotion:'reduce'});
   await localAssets(page);
   await page.goto('http://127.0.0.1:4174/calculators.html');
   assert.equal(await page.locator('.clarity-library .clear-tool-card:visible').count(),4);
   await page.locator('.clarity-more summary').click();
   assert.equal(await page.locator('.clarity-library .clear-tool-card:visible').count(),8);
   await page.goto('http://127.0.0.1:4174/search.html');
   for(const [query,url] of [['recipe calculator','recipe-macro-scaler.html'],['sweat rate calculator','sweat-rate-calculator.html'],['compare nutrition labels','nutrition-label-comparison-tool.html']]){
    await page.fill('#site-search',query);
    assert.equal(await page.locator('.search-hit[href="'+url+'"]').isVisible(),true,query);
   }
   await page.goto('http://127.0.0.1:4174/protein-value-calculator.html');
   assert.equal(await page.locator('#ra25').textContent(),'$1.16');
   assert.equal(await page.locator('#rb25').textContent(),'$2.22');
   await page.goto('http://127.0.0.1:4174/nutrition-label-comparison-tool.html');
   assert.match(await page.locator('#comparison-note').textContent(),/40 g and 55 g/);
   await page.selectOption('#compare-basis','weight');
   assert.match(await page.locator('#comparison-note').textContent(),/Both foods.*100 g/);
   assert.deepEqual(await page.locator('#resultRows tr').nth(1).locator('td').allTextContents(),['400 kcal','382 kcal']);
   await page.selectOption('#compare-basis','calories');
   assert.deepEqual(await page.locator('#resultRows tr').nth(1).locator('td').allTextContents(),['100 kcal','100 kcal']);
   await page.fill('#calA','');await page.locator('#compareForm button[type=submit]').click();
   assert.equal(await page.locator('#results').isVisible(),false);
   assert.ok(await page.locator('#error').textContent());
   await page.fill('#calA','160');await page.locator('#compareForm button[type=submit]').click();
   assert.equal(await page.locator('#results').isVisible(),true);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
   console.log('PASS',engine.name(),theme,'tool discovery, price amounts, comparison bases and invalid-input recovery');
   await page.close();
  }}finally{await browser.close()}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
