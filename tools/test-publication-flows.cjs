const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 for(const engine of [chromium,webkit]){
 const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark'])for(const width of [320,768,1440]){
  process.env.GM_TEST_THEME=theme;const p=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(p);
  const errors=[],ads=[];p.on('pageerror',e=>errors.push(e.message));p.on('request',r=>{if(/googlesyndication|doubleclick/.test(r.url()))ads.push(r.url())});
  const go=f=>p.goto('http://127.0.0.1:4174/'+f);
  await go('index.html');
  if(width<901)await p.locator('.nav-toggle').click();
  await p.locator('.nav-group-trigger').nth(1).click();await p.locator('.nav-group.is-open a[href="calculators.html"]').click();await p.waitForURL('**/calculators.html');
  await p.locator('#macro-form').evaluate(e=>e.requestSubmit());assert.doesNotMatch(await p.locator('#macro-results').innerText(),/NaN|Infinity/);assert.equal(await p.locator('#macro-error').isVisible(),false);
  await p.locator('[data-weight-unit="kg"]').click();assert.ok(Math.abs(Number(await p.locator('#weight').inputValue())-77.1)<.1);
  await p.locator('[data-height-unit="cm"]').click();assert.equal(await p.locator('#height-cm').inputValue(),'175');
  await p.locator('#age').fill('0');await p.locator('#macro-form').evaluate(e=>e.requestSubmit());assert.equal(await p.locator('#age').evaluate(e=>e.validity.valid),false);
  await go('recipe-macro-scaler.html');assert.equal(await p.locator('#rCal').textContent(),'300');await p.selectOption('#recipe-mode','scale');assert.equal(await p.locator('#rCal').textContent(),'450');await p.fill('#orig','0');assert.equal(await p.locator('#rCal').textContent(),'—');
  await go('nutrition-label-comparison-tool.html');assert.equal(await p.locator('#resultRows tr').count(),6);await p.selectOption('#compare-basis','calories');assert.equal(await p.locator('#resultRows tr').nth(1).locator('td').first().textContent(),'100 kcal');await p.fill('#proA','');assert.equal(await p.locator('#results').isVisible(),false);
  await go('restaurant-meal-finder.html');await p.locator('.quiz-option:has([value="protein"])').click();for(let i=0;i<5;i++)await p.locator('.quiz-continue').click();assert.equal(await p.locator('.meal-card').count(),5);
  assert.doesNotMatch(await p.locator('#meal-quiz').innerText(),/undefined|NaN/);assert.match(await p.locator('.meal-card').first().innerText(),/carbs/);assert.match(await p.locator('.meal-card').first().innerText(),/fat/);
  assert.equal(await p.locator('.comparison-output tbody tr').count(),6);
  const picker=p.locator('[data-compare="1"]');await picker.locator('summary').click();await picker.locator('[data-compare-pick="0"]').click();assert.match(await p.locator('.comparison-output').innerText(),/two different/);
  await picker.locator('summary').click();await picker.locator('[data-compare-pick="2"]').click();assert.equal(await p.locator('.comparison-output tbody tr').count(),6);
  await p.locator('[data-save]').first().click();assert.match(await p.locator('[data-save]').first().innerText(),/Saved/);
  assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await p.locator('#meal-quiz').screenshot({path:`design/publication-results-${engine.name()}-${theme}-${width}.png`});
  await go('restaurant-meal-finder.html?goal=protein&chain=Chick-fil-A');await p.locator('.meal-card').first().waitFor();while(await p.locator('[data-more]').count())await p.locator('[data-more]').click();const sandwich=p.locator('.meal-card').filter({hasText:'Grilled Chicken Sandwich'});assert.match(await sandwich.innerText(),/206 g/);assert.match(await sandwich.innerText(),/11 g/);
  await go('chipotle-healthy-meals-macros.html');await p.locator('[data-chain-form] button[type=submit]').click();assert.ok(await p.locator('.chain-result-card').count()>0);
  await go('index.html');await p.locator('[data-theme-toggle]').click();assert.equal(await p.locator('html').getAttribute('data-theme'),theme==='light'?'dark':'light');
  assert.deepEqual(ads,[]);assert.deepEqual(errors,[]);console.log('PASS',engine.name(),theme,width,'navigation, conversions, invalid input, recipe, labels, quiz, comparison, save, provenance, chain finder, theme, no ads');await p.close();
 }}finally{await browser.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
