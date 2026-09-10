const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
const cases=[['sodium-label-comparison-tool.html','450','500'],['carbohydrate-label-portion-tool.html','48','6'],['weight-goal-timeline-calculator.html','27','weeks'],['sweat-rate-calculator.html','1.00','L/hour']];
(async()=>{for(const engine of [chromium,webkit]){const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});try{for(const theme of ['light','dark'])for(const width of [320,390,1440]){
 process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});await localAssets(p);const errors=[];p.on('pageerror',e=>errors.push(e.message));
 for(const [file,a,z] of cases){await p.goto('http://127.0.0.1:4174/'+file);assert.equal(await p.locator('body').evaluate(e=>e.classList.contains('calculator-suite')),false);
  if(width===390||width===1440)await p.screenshot({path:`design/focused-${engine.name()}-${theme}-${width}-${file}.png`});
  await p.locator('[data-example]').click();const result=p.locator('.focused-result');await result.waitFor({state:'visible'});
  assert.ok((await result.innerText()).includes(a));assert.ok((await result.innerText()).includes(z));assert.equal(await p.locator('.focused-empty').isVisible(),false);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,file+' horizontal overflow');
  await result.screenshot({path:`design/focused-result-${engine.name()}-${theme}-${width}-${file}.png`});
  if(file.startsWith('sodium')){await p.locator('#an').fill('<img src=x onerror=alert(1)>');await p.locator('button[type=submit]').click();assert.equal(await result.locator('img').count(),0);assert.ok((await result.innerText()).includes('<img src=x'));}
  if(file.startsWith('carbohydrate')){await p.locator('.focused-optional summary').click();await p.locator('#f').fill('');await p.locator('#a').fill('');await p.locator('button[type=submit]').click();assert.equal(await result.locator('.focused-metric').count(),1,'Unentered optional nutrients are not reported as zero');await p.locator('#f').fill('40');await p.locator('button[type=submit]').click();assert.match(await p.locator('.focused-error').innerText(),/Fiber cannot/);}
  if(file.startsWith('weight')){assert.equal(await result.locator('.focused-milestones li').count(),4);await p.locator('#wg-unit').selectOption('kg');assert.ok(Math.abs(Number(await p.locator('#wg-current').inputValue())-90.72)<.01);await p.locator('#wg-goal').fill(await p.locator('#wg-current').inputValue());await p.locator('button[type=submit]').click();assert.match(await p.locator('.focused-error').innerText(),/same/);}
  if(file.startsWith('sweat')){await p.locator('#drink').fill('0');await p.locator('#after').fill('71');await p.locator('button[type=submit]').click();assert.match(await p.locator('.focused-error').innerText(),/fluid gain/);}
  await p.locator('button[type=reset]').click();assert.equal(await result.isVisible(),false);assert.equal(await p.locator('.focused-empty').isVisible(),true);
 }
 assert.deepEqual(errors,[]);console.log('PASS',engine.name(),theme,width,'four calculator flows, errors, reset, units and layout');await p.close();
}}finally{await b.close()}}})().catch(e=>{console.error(e);process.exitCode=1});
