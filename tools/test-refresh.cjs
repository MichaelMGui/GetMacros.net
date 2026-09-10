const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 for(const engine of ['edge','webkit']){
  const b=await(engine==='edge'?chromium.launch({channel:'msedge'}):webkit.launch());
  try{
   for(const theme of ['light','dark']){
    process.env.GM_TEST_THEME=theme;
    const p=await b.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await require('./browser-fixture.cjs').localAssets(p);
    const go=async f=>{await p.goto('http://127.0.0.1:4174/'+f);await p.evaluate(()=>document.fonts.ready);};
    const chains=fs.readdirSync('.').filter(f=>f.endsWith('.html')&&fs.readFileSync(f,'utf8').includes('data-chain-finder'));
    for(const file of chains){
     await go(file);
     const pick=v=>p.locator('label').filter({has:p.locator('input[name="chain-goal"][value="'+v+'"]')});
     await pick('energy').click();await pick('protein').click();
     assert.equal(await p.locator('input[name="chain-goal"]:checked').count(),2);
     await p.locator('[data-chain-form] button[type="submit"]').click();
     assert.match(await p.locator('[data-chain-results]').innerText(),/Meals for (high protein \+ weight gain|weight gain \+ high protein)/);
     assert.ok(await p.locator('.chain-result-card').count()>0);
     await pick('balanced').click();
     assert.equal(await p.locator('input[name="chain-goal"]:checked').count(),1);
     assert.equal(await p.locator('[data-chain-results]').isVisible(),false);
     if(file==='taco-bell-healthy-meals-macros.html'){
      await pick('fibre').click();
      await p.locator('[data-chain-form] button[type="submit"]').click();
      assert.equal(await p.locator('.chain-result-card').count(),0,'Unknown fiber must not be ranked as a match');
      assert.match(await p.locator('[data-chain-results]').innerText(),/No meals match/);
      await pick('protein').click();await pick('fibre').click();
      await p.locator('[data-chain-form] button[type="submit"]').click();
      assert.equal(await p.locator('.chain-result-card').count(),1);
      assert.match(await p.locator('.chain-result-card').innerText(),/Cantina Chicken Bowl/);
     }
    }
    await go('high-protein-foods-list.html');
    assert.equal(await p.locator('.protein-food-card:visible').count(),25);
    await p.fill('#protein-food-search','yogurt');assert.ok(await p.locator('.protein-food-card:visible').count()>0);
    await p.selectOption('#protein-food-group','plant');assert.equal(await p.locator('.protein-food-card:visible').count(),0);
    assert.ok(await p.locator('.food-empty').isVisible());
    await p.fill('#protein-food-search','');assert.ok(await p.locator('.protein-food-card:visible').count()>0);
    await p.locator('.food-reference summary').click();assert.equal(await p.locator('table:visible').count(),2);
    await p.evaluate(()=>window.scrollTo(0,2000));await p.locator('.back-to-top').waitFor({state:'visible'});
    await p.locator('.back-to-top').click();await p.waitForFunction(()=>window.scrollY<5);
    assert.equal(await p.evaluate(()=>document.activeElement.tagName),'H1');
    for(const f of ['about.html','contact.html','calculators.html','sodium-label-comparison-tool.html','protein-value-calculator.html','sweat-rate-calculator.html']){
     await go(f);assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
     if(engine==='edge')await p.screenshot({path:'design/refresh-final-'+f.replace('.html','')+'-'+theme+'.png',fullPage:true});
    }
    await p.setViewportSize({width:1440,height:1000});await go('calculators.html');
    const boxes=await p.locator('.single-macro-card').evaluateAll(els=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width};}));
    assert.equal(boxes.length,3);assert.ok(Math.abs(boxes[0].y-boxes[2].y)<2);assert.ok(boxes[0].x<boxes[1].x&&boxes[1].x<boxes[2].x);
    for(const card of await p.locator('.single-macro-card').all()){
     assert.ok(await card.locator('input[type="number"]').first().evaluate(e=>e.getBoundingClientRect().width>100));
     await card.locator('button[type="submit"]').click();
     assert.ok(await card.locator('.single-macro-result').isVisible());
     assert.doesNotMatch(await card.locator('.single-macro-result').innerText(),/NaN|Infinity/);
    }
    await p.locator('#single-macro-calculators').scrollIntoViewIfNeeded();
    if(engine==='edge')await p.screenshot({path:'design/refresh-three-'+theme+'.png'});
    await p.close();console.log('PASS refresh',engine,theme,chains.length,'restaurant finders, food filtering, back-to-top and three-column calculators');
   }
  }finally{await b.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
