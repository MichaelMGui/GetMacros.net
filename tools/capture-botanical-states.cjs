const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{const b=await chromium.launch({channel:'msedge'});try{
 for(const theme of ['light','dark'])for(const width of [390,1440]){
  process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:950},reducedMotion:'no-preference'});await localAssets(p);
  const capture=async name=>p.screenshot({path:`docs/redesign/screenshots/state-${name}-${theme}-${width}.png`});
  await p.goto('http://127.0.0.1:4174/');await p.evaluate(()=>document.fonts.ready);if(width>640)await p.locator('.garden-food img').evaluate(e=>e.decode());await capture('home');
  if(width===390)await p.locator('.nav-toggle').click();
  await p.locator('.nav-group-trigger').nth(1).click();await capture('navigation');await p.keyboard.press('Escape');
  await p.goto('http://127.0.0.1:4174/calculators.html');await p.locator('#macro-form').evaluate(e=>e.requestSubmit());const number=await p.locator('#macro-results .num').innerText();await p.evaluate(()=>new Promise(requestAnimationFrame));assert.equal(await p.locator('#macro-results .num').innerText(),number,'Calculated numbers must not count up');await p.locator('#macro-results').scrollIntoViewIfNeeded();await capture('macro-results');
  await p.locator('.back-to-top').click();assert.equal(await p.locator('main h1').evaluate(e=>e===document.activeElement),true);await p.waitForFunction(()=>scrollY===0);
  await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html?maxCal=150&minProtein=200');await capture('no-meals');
  await p.close();
 }
 console.log('PASS: 16 state screenshots; footer shortcut returns focus and scroll to the heading in both themes and widths.');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
