const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
  for(const engine of [chromium,webkit]){
    const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
    try{
      for(const theme of ['light','dark'])for(const width of [320,390,1440]){
        process.env.GM_TEST_THEME=theme;
        const page=await browser.newPage({viewport:{width,height:844},reducedMotion:'no-preference'});
        await localAssets(page);
        await page.goto('http://127.0.0.1:4174/restaurant-meal-finder.html');
        for(let step=0;step<5;step++){
          const next=page.locator('[data-go="1"]');
          await next.scrollIntoViewIfNeeded();
          await page.waitForTimeout(120);
          await page.evaluate(()=>{window.motionSamples=[];window.recordMotion=true;function sample(){window.motionSamples.push({y:scrollY,t:performance.now()});if(window.recordMotion)requestAnimationFrame(sample)}sample()});
          await next.click();
          await page.waitForFunction(()=>!document.querySelector('#meal-quiz [disabled]'));
          await page.waitForTimeout(250);
          const check=await page.evaluate(()=>{
            window.recordMotion=false;
            const heading=document.querySelector('#meal-quiz h2').getBoundingClientRect();
            const header=document.querySelector('.site-header').getBoundingClientRect();
            // Measure elapsed stability, not a frame count: throttled browsers
            // may produce fewer than ten frames during the settled period.
            const tail=window.motionSamples.filter(x=>x.t>=performance.now()-200).map(x=>x.y);
            tail.push(scrollY);
            return {visible:heading.top>=header.bottom && heading.bottom<innerHeight,drift:Math.max(...tail)-Math.min(...tail),overflow:document.documentElement.scrollWidth>innerWidth+1};
          });
          assert.ok(check.visible,`${engine.name()} ${theme} ${width} question ${step+2}: heading hidden`);
          assert.ok(check.drift<=1,`${engine.name()} ${theme} ${width} question ${step+2} still bouncing: ${JSON.stringify(check)}`);
          assert.equal(check.overflow,false);
        }
        await page.locator('[data-restart]').click();
        await page.waitForFunction(()=>document.querySelector('#meal-quiz h2')?.textContent.includes('goal'));
        await page.waitForTimeout(300);
        assert.equal(await page.locator('.quiz-progress-row').textContent(),'Question 1 of 5');
        await page.close();
      }
    }finally{await browser.close()}
  }
  console.log('PASS: active-motion quiz transitions, visible headings, stable scrolling and restart across Edge/WebKit, 320/390/1440, light/dark.');
})().catch(e=>{console.error(e);process.exitCode=1});
