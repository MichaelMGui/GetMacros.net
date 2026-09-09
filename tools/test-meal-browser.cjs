const assert = require('node:assert/strict');
const {chromium, webkit} = require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets} = require('./browser-fixture.cjs');

async function checkText(page) {
  const issues = await page.evaluate(() => {
    const problems = [];
    if (document.documentElement.scrollWidth > innerWidth + 1) problems.push('Page overflow');
    for (const box of document.querySelectorAll('.quiz-option,.browse-meal,.meal-card,.results-heading')) {
      if (!box.getClientRects().length) continue;
      const boundary = box.getBoundingClientRect();
      const walker = document.createTreeWalker(box, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const node = walker.currentNode;
        if (!node.textContent.trim() || !node.parentElement.getClientRects().length) continue;
        const range = document.createRange(); range.selectNodeContents(node);
        for (const rect of range.getClientRects()) {
          if (rect.width && (rect.left < boundary.left - 1 || rect.right > boundary.right + 1 || rect.top < boundary.top - 1 || rect.bottom > boundary.bottom + 1)) problems.push(node.textContent.trim());
        }
      }
    }
    return problems;
  });
  assert.deepEqual(issues, [], 'All text must fit its card');
}

(async () => {
  for (const engine of [chromium, webkit]) {
    const browser = await engine.launch(engine === chromium ? {channel:'msedge'} : {});
    try {
      for (const theme of ['light','dark']) for (const width of [320,390,1440]) {
        process.env.GM_TEST_THEME = theme;
        const page = await browser.newPage({viewport:{width,height:950}, reducedMotion:'reduce'});
        await localAssets(page);
        const errors = []; page.on('pageerror', e => errors.push(e.message));
        await page.goto('http://127.0.0.1:4174/restaurant-meal-finder.html');
        assert.equal(await page.locator('.quiz-data-note,.match-calc-link,.meal-list,.meal-jump').count(), 0);
        assert.equal(await page.locator('.meal-database-disclosure').getAttribute('open'), null);
        assert.equal(await page.locator('.quiz-option-any small').count(), 0);
        assert.match(await page.locator('[data-facet="goal"][value="light"]').locator('..').innerText(), /Weight loss/);
        assert.match(await page.locator('[data-facet="goal"][value="energy"]').locator('..').innerText(), /Weight gain/);
        await checkText(page);
        await page.locator('[data-facet="goal"][value="energy"]').locator('..').click();
        await page.locator('[data-facet="goal"][value="protein"]').locator('..').click();
        for (let i = 0; i < 5; i++) {
          if (i) await page.locator('.quiz-option-any input').locator('..').click();
          await checkText(page);
          await page.locator('.quiz-continue').click();
        }
        assert.equal(await page.locator('.results-heading h2').innerText(), 'Meals for weight gain + high protein');
        assert.equal(await page.locator('.quiz-summary').count(), 0);
        await checkText(page);
        await page.locator('.meal-database-disclosure>summary').click();
        assert.equal(await page.locator('.browse-meal').count(), 83);
        assert.equal(await page.locator('.browse-meal:visible').count(), 6);
        await checkText(page);
        for (const value of ['protein','light','energy','vegetarian','plant','breakfast','fibre','lowsodium']) {
          await page.selectOption('#browse-filter', value);
          const tags = await page.locator('.browse-meal:visible').evaluateAll(es => es.map(e => e.dataset.tags.split(' ')));
          assert.ok(tags.length > 0 && tags.every(t => t.includes(value)), value);
          await checkText(page);
        }
        await page.selectOption('#browse-filter','');
        await page.fill('#browse-query','Chipotle chicken');
        assert.ok(await page.locator('.browse-meal:visible').count() > 0);
        assert.ok((await page.locator('.browse-meal:visible').allTextContents()).every(t => /Chipotle/.test(t) && /chicken/i.test(t)));
        await page.fill('#browse-query','nothingmatchesxyz');
        assert.equal(await page.locator('.browse-meal:visible').count(), 0);
        assert.ok(await page.locator('.browse-empty').isVisible());
        await page.fill('#browse-query','');
        await page.locator('.browse-more').click();
        assert.equal(await page.locator('.browse-meal:visible').count(), 12);
        assert.equal(await page.locator('.browse-meal:visible h3').nth(6).evaluate(e => e === document.activeElement), true);
        while (await page.locator('.browse-more').isVisible()) await page.locator('.browse-more').click();
        assert.equal(await page.locator('.browse-meal:visible').count(), 83);
        await checkText(page);
        if (width === 390) {
          await page.selectOption('#browse-filter','');
          await page.locator('.meal-browser-controls').scrollIntoViewIfNeeded();
          await page.screenshot({path:`design/meal-browser-${engine.name()}-${theme}.png`});
          await page.locator('[data-restart]').click();
          await page.locator('#meal-quiz').scrollIntoViewIfNeeded();
          await page.screenshot({path:`design/quiz-clear-${engine.name()}-${theme}.png`});
        }
        assert.deepEqual(errors, []);
        await page.close();
        console.log('PASS',engine.name(),theme,width,'quiz, filters, search, 83 meals and text bounds');
      }
      const fallback = await browser.newPage({javaScriptEnabled:false, viewport:{width:390,height:950}});
      await localAssets(fallback);
      await fallback.goto('http://127.0.0.1:4174/restaurant-meal-finder.html');
      await fallback.locator('.meal-database-disclosure>summary').click();
      assert.equal(await fallback.locator('.browse-meal:visible').count(),83);
      assert.equal(await fallback.locator('.meal-browser-controls').isVisible(),false);
      await fallback.close();
      console.log('PASS',engine.name(),'all meals accessible without JavaScript');
    } finally { await browser.close(); }
  }
})().catch(e => {console.error(e);process.exitCode=1;});
