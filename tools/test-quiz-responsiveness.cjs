const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 for(const engine of [chromium,webkit]){
  const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
  try{for(const theme of ['light','dark'])for(const width of [320,390,1440]){
   process.env.GM_TEST_THEME=theme;
   const p=await browser.newPage({viewport:{width,height:844},reducedMotion:'no-preference'});
   await localAssets(p);
   if(engine===chromium){const cdp=await p.context().newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});}
   await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html');
   const errors=[];p.on('pageerror',e=>errors.push(e.message));
   const timings=[];
   for(let i=0;i<5;i++){
    await p.locator('[data-go="1"]').scrollIntoViewIfNeeded();
    const result=await p.evaluate(()=>{
     const root=document.getElementById('meal-quiz'),before=root.querySelector('h2').textContent;
     const start=performance.now();root.querySelector('[data-go="1"]').click();
     const heading=root.querySelector('h2'),rect=heading.getBoundingClientRect();
     return {ms:performance.now()-start,changed:before!==heading.textContent,disabled:!!root.querySelector('[data-go]:disabled'),focused:document.activeElement===heading,top:rect.top,header:document.querySelector('.site-header').getBoundingClientRect().bottom,opacity:getComputedStyle(heading).opacity};
    });
    assert.ok(result.changed,'The same click must render the next question, without an outgoing animation wait');
    assert.ok(!result.disabled&&result.focused,'New controls must be usable immediately, with the question focused');
    assert.equal(result.opacity,'1');assert.ok(result.top>=result.header&&result.top<700,JSON.stringify(result));
    timings.push(Math.round(result.ms));
   }
   assert.ok(await p.locator('.results-heading').isVisible());
   await p.locator('[data-restart]').focus();await p.keyboard.press('Enter');
   assert.ok(await p.locator('[data-go="1"]').isEnabled());
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
   assert.deepEqual(errors,[]);
   console.log('PASS',engine.name(),theme,width,'synchronous question changes (ms)',timings.join(','));
   await p.close();
  }}finally{await browser.close()}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
