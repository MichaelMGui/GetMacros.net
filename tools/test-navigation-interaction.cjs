const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
try{for(const theme of ['light','dark'])for(const width of [320,768,1440]){
 process.env.GM_TEST_THEME=theme;const page=await browser.newPage({viewport:{width,height:900}});await localAssets(page);
 await page.goto('http://127.0.0.1:4174/index.html');
 await page.evaluate(()=>scrollTo({top:600,behavior:'instant'}));await page.waitForTimeout(150);const before=await page.evaluate(()=>scrollY);
 if(width<=900){const toggle=await page.locator('.nav-toggle').boundingBox();await page.mouse.click(toggle.x+toggle.width/2,toggle.y+toggle.height/2);}
 const trigger=page.locator('.nav-group-trigger').nth(1);await trigger.evaluate(e=>e.focus({preventScroll:true}));await trigger.press('ArrowDown');
 const options=page.locator('.nav-group').nth(1).locator('.nav-popover a');
 assert.equal(await options.first().evaluate(e=>e===document.activeElement),true);
 await page.keyboard.press('End');assert.equal(await options.last().evaluate(e=>e===document.activeElement),true);
 await page.keyboard.press('ArrowDown');assert.equal(await options.first().evaluate(e=>e===document.activeElement),true);
 await page.keyboard.press('Escape');assert.equal(await page.locator('.nav-group.is-open').count(),0);
 assert.ok(Math.abs(await page.evaluate(()=>scrollY)-before)<2,'Closing navigation must preserve scroll position: '+before+' to '+await page.evaluate(()=>scrollY));
 if(width<=900)await page.locator('.nav-toggle').click();
 for(let n=0;n<6;n++)await trigger.click({noWaitAfter:true});
 await page.waitForTimeout(300);assert.equal(await trigger.getAttribute('aria-expanded'),'false');
 await trigger.click();await page.waitForTimeout(300);assert.equal(await page.locator('.nav-group.is-open').count(),1);
 await options.first().click();await page.waitForURL('**/calculators.html');
 await page.goto('http://127.0.0.1:4174/search.html');
 const sizes=await page.locator('.search-start-tile').evaluateAll(es=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height,overflow:e.scrollWidth>e.clientWidth+1})));
 assert.equal(sizes.length,3);assert.ok(sizes.every(s=>Math.abs(s.w-sizes[0].w)<1&&Math.abs(s.h-sizes[0].h)<1&&!s.overflow),JSON.stringify(sizes));
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
 if(engine===webkit)await page.locator('.search-start').screenshot({path:`design/search-equal-${theme}-${width}.png`});
 await page.goto('http://127.0.0.1:4174/index.html');
 if(width===1440){const backgrounds=await page.locator('.home-art-caption span').evaluateAll(es=>es.map(e=>getComputedStyle(e).backgroundColor));assert.equal(new Set(backgrounds).size,1);assert.notEqual(backgrounds[0],'rgba(0, 0, 0, 0)');}
 if(theme==='dark'){const button=await page.locator('.home-text-link').evaluate(e=>({own:getComputedStyle(e).backgroundColor,parent:getComputedStyle(e.closest('.home-intro-grid')).backgroundColor}));assert.notEqual(button.own,button.parent);assert.notEqual(button.own,'rgba(0, 0, 0, 0)');}
 if(engine===webkit)await page.locator('.home-intro-grid').screenshot({path:`design/home-badges-${theme}-${width}.png`});
 await page.emulateMedia({reducedMotion:'reduce'});if(width<=900)await page.locator('.nav-toggle').click();await page.locator('.nav-group-trigger').first().click();assert.equal(await page.locator('.nav-group.is-open .nav-popover').evaluate(e=>e.getAnimations().length),0);
 console.log('PASS',engine.name(),theme,width,'keyboard, rapid taps, scroll retention, equal search cards and homepage highlights');await page.close();
}}finally{await browser.close();}}})().catch(error=>{console.error(error);process.exitCode=1});
