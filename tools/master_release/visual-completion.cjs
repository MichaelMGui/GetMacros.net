/* Actual rendered QA for the master-completion audit. No fabricated food values. */
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict'), vm = require('node:vm');
const { chromium } = require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT = '0';
const server = require('../product_release/dev-server.cjs');
const stage = process.env.GM_VISUAL_STAGE || 'baseline';
const isFinal = stage.startsWith('final');
const out = path.resolve('docs/master-completion-2026-10-13/visual-' + stage);
fs.mkdirSync(out, { recursive: true });
const result = { checkedAt: new Date().toISOString(), renders: [], interactions: [], manualInspection: [] };
const scope = { window: {} }; vm.runInNewContext(fs.readFileSync('js/market-definitions.js', 'utf8'), scope);
const markets = scope.window.GM_MARKETS;
const widths = [320, 390, 768, 1280, 1440];
const routes = [
  ['US', '/'], ['CA', '/ca/en/'], ['MX', '/mx/en/'], ['AU', '/au/en/'],
  ['diary', '/food-diary.html?market=CA'], ['calculators', '/calculators.html?market=CA'],
  ['games', '/play.html?market=CA'], ['memory', '/play-market-memory.html?market=CA'],
  ['fruit', '/play-fruit-catch.html?market=CA'], ['plate', '/play-build-a-plate.html?market=CA'],
  ['restaurants', '/ca/en/restaurants/'], ['guide', '/ca/en/restaurants/pizza-nova/'],
  ['finder', '/ca/en/find-a-meal/?chain=Subway&maxCal=650'], ['article', '/how-to-log-food-portions.html']
];
async function capture(page, label, theme, width, fullPage = true) {
  await page.evaluate(() => document.fonts.ready);
  const screenshot = `${label}-${theme}-${width}.png`;
  await page.screenshot({ path: path.join(out, screenshot), fullPage });
  return screenshot;
}
(async () => {
  if (!server.listening) await new Promise(resolve => server.once('listening', resolve));
  const base = process.env.GM_VISUAL_BASE || 'http://127.0.0.1:' + server.address().port;
  result.base = base;
  const browser = await chromium.launch({ channel: 'msedge', headless: true, args: ['--no-proxy-server'] });
  try {
    let architecture;
    for (const theme of ['light', 'dark']) for (const width of widths) {
      const context = await browser.newContext({ viewport: { width, height: 950 }, colorScheme: theme, reducedMotion: 'reduce', serviceWorkers: 'block' });
      await context.addInitScript(t => {if (!localStorage.getItem('gm-theme')) localStorage.setItem('gm-theme', t)}, theme);
      const page = await context.newPage();
      for (const [label, route] of (process.env.GM_VISUAL_JOURNEYS_ONLY ? [] : routes)) {
        const errors = []; const onError = e => errors.push(e.message); page.on('pageerror', onError);
        const response = await page.goto(base + route, {waitUntil: 'domcontentloaded'});
        assert.equal(response.status(), 200, route);
        if (label === 'finder') await page.locator('.meal-row').first().waitFor();
        if (label === 'diary') await page.waitForFunction(() => window.GetMacrosFoodUI?.setDiaryDate);
        if (['memory', 'fruit', 'plate'].includes(label)) {
          await page.locator('[data-play-stage]').waitFor();
          await page.locator('[data-play-pause]').click(); assert.equal(await page.locator('[data-play-paused]').isVisible(),true);
          await page.locator('[data-play-resume]').click(); await page.locator('[data-play-restart]').click();
          assert.equal(await page.locator('[data-play-stage]').isVisible(),true);
        }
        await page.evaluate(() => document.fonts.ready);
        const state = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth + 1,
          theme: document.documentElement.dataset.theme,
          headings: document.querySelectorAll('h1').length,
          architecture: document.querySelector('[data-home-template]') ? [...document.querySelector('main').children].map(x => x.tagName + '.' + x.className) : null,
          country: document.querySelector('[data-country-name]')?.textContent,
          featuredMarkets: [...document.querySelectorAll('[data-record-market]')].map(x => x.dataset.recordMarket),
          featuredGeometry: [...document.querySelectorAll('.home-menu-card')].map(x => {
            const b = x.getBoundingClientRect(), n = x.querySelector('.home-menu-values'), a = x.querySelector('.home-menu-action');
            return {top:b.top,bottom:b.bottom,nutritionTop:n?.getBoundingClientRect().top,actionTop:a?.getBoundingClientRect().top};
          }),
          source: [...document.querySelectorAll('script[src],link[rel=stylesheet]')].map(x => x.getAttribute('src') || x.getAttribute('href'))
        }));
        assert.equal(state.overflow, false, `${label} ${theme} ${width} horizontal overflow`);
        assert.equal(state.theme, theme, `${label} theme`); assert.equal(state.headings, 1, `${label} primary heading`);
        assert.deepEqual(errors, [], `${label} runtime errors`);
        if (markets[label]) {
          assert.equal(state.country, markets[label].name); assert(state.featuredMarkets.every(m => m === label));
          if (architecture) assert.deepEqual(state.architecture, architecture); else architecture = state.architecture;
          const rows = [];
          for (const card of state.featuredGeometry) {let row = rows.find(r => Math.abs(r[0].top-card.top) <= 1); if(!row) rows.push(row=[]); row.push(card);}
          for (const row of rows) for (const key of ['bottom','nutritionTop','actionTop']) {
            const values = row.map(x=>x[key]).filter(x=>typeof x==='number');
            if (values.length>1) assert(Math.max(...values)-Math.min(...values)<=1.1, `${label} ${width} featured ${key} alignment`);
          }
        }
        const screenshot = await capture(page, label, theme, width);
        result.renders.push({ route, label, theme, width, screenshot, errors, ...state });
        page.off('pageerror', onError);
      }
      await page.goto(base + '/ca/en/', {waitUntil: 'domcontentloaded'});
      if (isFinal) assert.equal(await page.locator('.country-picker>summary').getAttribute('aria-label'), 'Restaurant country: Canada. Choose country');
      await page.locator('.country-picker>summary').click();
      const panel = await page.locator('.country-panel').boundingBox();
      assert(panel.x >= -1 && panel.x + panel.width <= width + 1, 'Country panel stays within viewport');
      await page.locator('[data-country-choice=CA]').focus(); await page.keyboard.press('ArrowDown');
      assert.equal(await page.evaluate(() => document.activeElement.dataset.countryChoice), 'MX');
      const countryShot = await capture(page, 'country-open', theme, width, false);
      await page.keyboard.press('Escape'); assert.equal(await page.locator('.country-picker').getAttribute('open'), null);
      await page.locator('.appearance-picker>summary').click();
      const appearanceBox = await page.locator('.appearance-panel').boundingBox();
      assert(appearanceBox.x >= -1 && appearanceBox.x + appearanceBox.width <= width + 1);
      const appearanceShot = await capture(page, 'appearance-open', theme, width, false);
      await page.keyboard.press('Escape');
      await page.locator('.appearance-picker>summary').click();
      const opposite = theme === 'light' ? 'dark' : 'light';
      await page.locator('[data-theme-choice=' + opposite + ']').focus(); await page.keyboard.press('Enter');
      assert.equal(await page.locator('html').getAttribute('data-theme'), opposite);
      assert.equal(await page.locator('[data-theme-choice=' + opposite + ']').getAttribute('aria-pressed'), 'true');
      await page.reload({waitUntil:'domcontentloaded'}); assert.equal(await page.locator('html').getAttribute('data-theme'), opposite);
      await page.locator('.appearance-picker>summary').click(); await page.locator('[data-theme-choice=' + theme + ']').click();
      await page.keyboard.press('Escape');
      await page.locator('.country-picker>summary').click(); await page.locator('[data-country-choice=MX]').click();
      await page.waitForURL('**/mx/en/'); assert.equal(await page.locator('[data-country-name]').textContent(), 'Mexico');
      await page.goto(base + '/food-library.html', {waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('[data-country-name]').textContent(), 'Mexico');
      if (isFinal) assert.equal(await page.locator('.country-picker>summary').getAttribute('aria-label'), 'Restaurant country: Mexico. Choose country');
      await page.goto(base + '/ca/en/', {waitUntil:'domcontentloaded'});
      assert.equal(await page.locator('[data-country-name]').textContent(), 'Canada');
      if (isFinal) assert.equal(await page.locator('.country-picker>summary').getAttribute('aria-label'), 'Restaurant country: Canada. Choose country');
      await page.locator('.language-picker>summary').click();
      const languageBox = await page.locator('.language-panel').boundingBox();
      assert(languageBox.x>=-1&&languageBox.x+languageBox.width<=width+1);
      const languageShot = await capture(page, 'language-open', theme, width, false);
      await page.keyboard.press('Escape');
      await page.locator('.nav-search>summary').click();
      const searchBox = await page.locator('.nav-search-panel').boundingBox();
      assert(searchBox.x>=-1&&searchBox.x+searchBox.width<=width+1);
      const headerSearchShot = await capture(page, 'header-search-open', theme, width, false);
      await page.locator('#quick-search').fill('unmatchedreleasequery20261013');
      await page.locator('.nav-search-panel [type=submit]').click();
      await page.waitForURL('**/search.html?*');
      assert.equal(new URL(page.url()).searchParams.get('market'),'CA');
      await page.getByText('No results.',{exact:false}).waitFor();
      if(isFinal) {
        assert.equal(await page.locator('#search-status').innerText(),'No results. Try another topic or “calorie calculator”.');
        assert.equal(await page.locator('.search-library-head').isVisible(),false);
      }
      const emptySearchShot = await capture(page, 'search-empty', theme, width, false);
      await page.locator('#site-search').fill('calorie calculator');
      await page.locator('.search-hit:not([hidden])').first().waitFor();
      assert.equal(await page.locator('.search-library-head').isVisible(),true);
      await page.locator('#search-clear').click();
      assert.equal(await page.locator('#site-search').inputValue(),'');
      await page.goto(base + '/ca/en/', {waitUntil:'domcontentloaded'});
      if (width < 1100) await page.locator('.nav-toggle').click();
      await page.locator('.nav-group-trigger').filter({ hasText: 'Learn' }).click();
      const navShot = await capture(page, 'navigation-open', theme, width, false);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      await page.keyboard.press('Escape');
      if (width < 1100 && await page.locator('.nav-toggle').getAttribute('aria-expanded') === 'true') await page.locator('.nav-toggle').click();
      // Real finder panel, source-food review and calculator result states.
      await page.goto(base + '/ca/en/find-a-meal/?chain=Subway&maxCal=650', {waitUntil: 'domcontentloaded'});
      await page.locator('.meal-row').first().waitFor();
      await page.locator('.country-picker>summary').click(); await page.locator('[data-country-choice=US]').click();
      await page.waitForURL('**/restaurant-meal-finder.html?*');
      assert(new URL(page.url()).searchParams.getAll('chain').includes('Subway')); assert.equal(new URL(page.url()).searchParams.get('maxCal'),'650');
      let incompleteShot;
      if (await page.locator('[data-allow-incomplete]').isVisible()) {
        assert.equal(await page.evaluate(()=>GM_MEALS.filter(m=>m.chain==='Subway'&&m.cal<=650).some(m=>!Number.isFinite(m.fat))),true);
        incompleteShot = await capture(page, 'country-missing-macros', theme, width, false);
        await page.locator('[data-allow-incomplete]').click();
        assert.equal(new URL(page.url()).searchParams.get('complete'),'0');
      }
      await page.locator('.meal-row').first().waitFor(); assert.equal(await page.evaluate(()=>GetMacrosMarket.current),'US');
      assert.equal(await page.evaluate(()=>GM_MEALS.every(m=>(m.market||m.country||'US')==='US')),true);
      assert.equal(await page.locator('.meal-row').evaluateAll(rows=>rows.every(x=>x.textContent.includes('Subway'))),true);
      await page.locator('.country-picker>summary').click(); await page.locator('[data-country-choice=CA]').click();
      await page.waitForURL('**/ca/en/find-a-meal/?*');
      assert(new URL(page.url()).searchParams.getAll('chain').includes('Subway')); assert.equal(new URL(page.url()).searchParams.get('maxCal'),'650');
      await page.locator('.meal-row').first().waitFor(); assert.equal(await page.evaluate(()=>GetMacrosMarket.current),'CA');
      assert.equal(await page.evaluate(()=>GM_MEALS.every(m=>(m.market||m.country||'US')==='CA')),true);
      // Restore the initial complete-macro preference for the filter calibration.
      await page.goto(base + '/ca/en/find-a-meal/?chain=Subway&maxCal=650', {waitUntil:'domcontentloaded'});
      await page.locator('.meal-row').first().waitFor();
      let filterShot;
      if (width < 1000) {
        await page.locator('[data-open-filters]').click();
        await page.locator('.filter-dialog[open]').waitFor();
        if (isFinal) {
          const fields = await page.locator('.filter-dialog .filter-primary input').evaluateAll(rows=>rows.map(x=>x.getBoundingClientRect().top));
          assert.equal(fields.length,2); assert(Math.abs(fields[0]-fields[1])<=1, 'Mobile calorie and protein input top edges align');
        }
        filterShot = await capture(page, 'filter-open', theme, width, false);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
        await page.keyboard.press('Escape');
        assert.equal(await page.locator('.filter-dialog').getAttribute('open'), null);
      }
      await page.goto(base + '/food-diary.html?market=CA', {waitUntil: 'domcontentloaded'});
      await page.locator('[data-meal-add=Breakfast]').click();
      await page.locator('[data-browse-food]').first().waitFor();
      const searchShot = await capture(page, 'food-search', theme, width, false);
      await page.locator('[data-browse-food]').first().click();
      await page.locator('#food-review[open]').waitFor();
      const reviewShot = await capture(page, 'food-review', theme, width, false);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      await page.locator('[data-review-save]').click();
      await page.locator('.diary-entry').first().waitFor();
      const loggedShot = await capture(page, 'diary-logged', theme, width);
      await page.getByRole('button', {name:'Preferences',exact:true}).click();
      const preferencesShot = await capture(page, 'diary-preferences', theme, width, false);
      await page.keyboard.press('Escape');
      await page.goto(base + '/calculators.html?market=CA', {waitUntil: 'domcontentloaded'});
      await page.locator('#age').fill('17'); await page.locator('[data-calc-next]').click();
      assert.equal(await page.locator('#macro-form').getAttribute('data-calc-step'), '0');
      assert.equal(await page.locator('#age').evaluate(x => x.checkValidity()), false);
      await page.locator('#age').fill('30'); await page.locator('[data-calc-next]').click();
      assert.equal(await page.locator('#macro-form').getAttribute('data-calc-step'), '1');
      await page.locator('[data-calc-next]').click();
      assert.equal(await page.locator('#macro-form').getAttribute('data-calc-step'), '2');
      await page.locator('#macro-form [type=submit]').click();
      await page.locator('#macro-results').waitFor();
      const resultShot = await capture(page, 'calculator-result', theme, width);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      result.interactions.push({ width, theme, countryShot, appearanceShot, languageShot, headerSearchShot, emptySearchShot, navShot, incompleteShot, filterShot, searchShot, reviewShot, loggedShot, preferencesShot, resultShot, checks: ['Country panel fits viewport', 'Country keyboard arrow and Escape', 'Appearance keyboard selection and reload persistence', 'Saved country on utility page; deliberately opened Canada URL overrides Mexico preference', 'Appearance and language open states fit', 'Header search retains country and renders a no-results state', 'Navigation open state has no horizontal overflow', 'Actual Subway restaurant and calorie filters survive Canada→US→Canada; unknown U.S. fat disclosed and never replaced with zero', 'Mobile filter open and Escape', 'Real reference-food selection, review, breakfast logging and private preferences', 'Calculator invalid input stays in correct group; three input groups and actual calculated result'] });
      await context.close(); console.log(`PASS master visual ${theme} ${width}`);
    }
    if (!process.env.GM_VISUAL_JOURNEYS_ONLY) for (const theme of ['light','dark']) {
      const context = await browser.newContext({viewport:{width:2592,height:1460},colorScheme:theme,reducedMotion:'reduce',serviceWorkers:'block'});
      await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
      const page = await context.newPage();
      const actual = [];
      for (const route of ['/', '/ca/en/']) {
        const p = await context.newPage(); await p.setViewportSize({width:1280,height:1400});
        await p.goto(base+route,{waitUntil:'domcontentloaded'});await p.locator('[data-home-template]').waitFor();await p.evaluate(()=>document.fonts.ready);
        actual.push((await p.screenshot()).toString('base64'));await p.close();
      }
      // Keep the site's frame protection intact. This private QA page presents
      // exact top-level screenshot pixels rather than trying to embed the app.
      await page.setContent('<style>body{margin:0;background:#f0f2eb;font:16px system-ui;color:#233c2c}main{display:flex;gap:16px;padding:8px}section{width:1280px}h2{font-size:18px;margin:8px 0}img{display:block;width:1280px;height:1400px}</style><main><section><h2>United States — actual top-level capture</h2><img src="data:image/png;base64,'+actual[0]+'"></section><section><h2>Canada — actual top-level capture</h2><img src="data:image/png;base64,'+actual[1]+'"></section></main>');
      const screenshot='homepage-comparison-'+theme+'.png';await page.screenshot({path:path.join(out,screenshot),fullPage:true});
      result.renders.push({theme,screenshot,type:'Private side-by-side presentation of exact top-level 1280px United States and Canada screenshot pixels; app framing protection unchanged'});
      await context.close();
    }
    result.status = 'pass';
    fs.writeFileSync(path.join(out, 'checks.json'), JSON.stringify(result, null, 2));
    console.log(`PASS ${result.renders.length} actual rendered page states and ${result.interactions.length} menu journeys`);
  } finally { await browser.close(); server.close(); }
})().catch(error => { result.status = 'fail'; result.error = error.stack; fs.writeFileSync(path.join(out, 'checks.json'), JSON.stringify(result, null, 2)); console.error(error); server.close(); process.exitCode = 1; });
