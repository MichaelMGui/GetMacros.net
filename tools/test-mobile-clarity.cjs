const assert = require('node:assert/strict');
const {chromium, webkit} = require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async () => {
 for (const engine of ['webkit', 'edge']) {
  const browser = await (engine === 'webkit' ? webkit.launch() : chromium.launch({channel:'msedge'}));
  try {
   for (const theme of ['light','dark']) {
    process.env.GM_TEST_THEME=theme;
    const page=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
    await require('./browser-fixture.cjs').localAssets(page);
    const go=async file=>{await page.goto('http://127.0.0.1:4174/'+file);await page.evaluate(()=>document.fonts.ready);};
    await go('restaurant-meal-finder.html');
    assert.equal(await page.locator('input[data-facet="goal"][value="balanced"]').count(),0);
    for(const goal of ['energy','protein'])await page.locator('label').filter({has:page.locator('input[data-facet="goal"][value="'+goal+'"]')}).click();
    for(let i=0;i<5;i++)await page.locator('.quiz-continue').click();
    assert.equal(await page.locator('.results-heading h2').innerText(),'Meals for bulking + high protein');
    assert.ok(await page.locator('.results-grid > *').count()>0);
    await page.locator('.results-heading').scrollIntoViewIfNeeded();
    await page.screenshot({path:`design/clarity-${engine}-${theme}-results.png`});
    await page.locator('.result-options summary').click();
    assert.equal(await page.locator('.result-options').getAttribute('open'),'');
    await page.locator('[data-restart]').click();
    assert.ok(await page.locator('.quiz-continue').isVisible());
    await go('calculators.html');
    assert.equal(await page.locator('#adult-scope').getAttribute('open'),null);
    assert.equal(await page.locator('#carb-calc-results').isVisible(),false);
    await page.locator('#carb-calc-form button').click();
    assert.ok(await page.locator('#carb-calc-results').isVisible());
    assert.match(await page.locator('#carb-calc-results').innerText(),/248/);
    await page.locator('.macro-carbs').scrollIntoViewIfNeeded();
    await page.screenshot({path:`design/clarity-${engine}-${theme}-calculator.png`});
    await page.locator('.nav-toggle').click();
    await page.getByRole('button',{name:'Tools',exact:true}).click();
    assert.ok(await page.locator('.nav-group').filter({has:page.getByRole('button',{name:'Tools',exact:true})}).locator('.nav-popover a').first().isVisible());
    await page.screenshot({path:`design/clarity-${engine}-${theme}-menu.png`});
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.nav-toggle').getAttribute('aria-expanded'),'false');
    await go('articles.html');
    assert.ok(await page.locator('.guide-card').first().evaluate(e=>parseFloat(getComputedStyle(e).paddingLeft)>=20));
    await page.locator('.guide-grid').first().scrollIntoViewIfNeeded();
    await page.screenshot({path:`design/clarity-${engine}-${theme}-articles.png`});
    await go('healthy-fast-food.html');
    await page.locator('.chain-card').last().scrollIntoViewIfNeeded();
    await page.waitForTimeout(300);
    assert.equal(await page.locator('.directory-logo').evaluateAll(es=>es.filter(e=>e.complete&&!e.naturalWidth).length),0);
    await page.locator('.ranking-disclosure summary').first().click();
    assert.equal(await page.locator('.ranking-disclosure').first().getAttribute('open'),'');
    assert.equal(await page.locator('.ranking-more').count(),0);
    assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    // Card text must stay inside its containing card, including long meal names.
    for(const file of ['articles.html','healthy-fast-food.html','index.html']) {
     await page.setViewportSize({width:320,height:844});
     await go(file);
     const outside=await page.locator('.guide-card,.chain-card,.home-launch-card,.home-decision').evaluateAll(cards=>cards.flatMap(card=>{
      const box=card.getBoundingClientRect();
      return [...card.querySelectorAll('h2,h3,p,strong,b')].filter(el=>{const r=el.getBoundingClientRect();return r.width>0&&(r.left<box.left-1||r.right>box.right+1||r.bottom>box.bottom+1);}).map(el=>el.textContent);
     }));
     assert.deepEqual(outside,[],file+' card text must stay inside its card');
     assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),file+' must fit 320px');
    }
    await page.close();
    console.log('PASS',engine,theme,'quiz, calculator, navigation, article cards and restaurant directory');
   }
  } finally {await browser.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
