/* Real public-site integration: no intercepted requests or local fixture. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base='https://getmacros.net',out='docs/global-product-release-2026-10-11/production';fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']}),results=[];try{
 for(const theme of ['light','dark'])for(const width of [390,1440]){
  const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/food-library.html');await page.locator('[data-food-query]').fill('olive oil');await page.locator('[data-food-search]').evaluate(f=>f.requestSubmit());await page.locator('.food-search-row').first().waitFor();
  await page.locator('.food-search-row').first().click();await page.locator('#food-review').waitFor({state:'visible'});assert((await page.locator('[data-review-link]').getAttribute('href')).startsWith('https://fdc.nal.usda.gov/food-details/'));assert(/^(Olive oil$|Oil, olive)/.test(await page.locator('[data-review-title]').innerText()));await page.screenshot({path:path.join(out,'library-portion-'+theme+'-'+width+'.png'),fullPage:true});await page.locator('[data-review-close]').click();
  await page.goto(base+'/food-diary.html');assert(await page.locator('[data-diary-date]').isVisible());assert.equal(await page.evaluate(()=>GetMacrosAppConfig.aiEnabled),false);await page.screenshot({path:path.join(out,'diary-'+theme+'-'+width+'.png'),fullPage:true});
  const pair=new URL(base+'/compare-menu-ingredients-worldwide.html');pair.searchParams.set('country1','GB');pair.searchParams.set('country2','NZ');pair.searchParams.set('item1','GB|subway|b4264d560fa0bb8a');pair.searchParams.set('item2','NZ|subway|116ff4314b0bea4c');
  await page.goto(pair.href);await page.getByRole('button',{name:'Copy comparison link'}).waitFor();await page.waitForFunction(()=>!document.querySelector('.ingredient-overview+ .food-actions button').disabled);
  assert((await page.locator('.ingredient-overview').innerText()).includes('Only named'));assert((await page.locator('[data-ingredient-content]').first().innerText()).includes('198 g'));assert((await page.locator('[data-ingredient-content]').nth(1).innerText()).includes('236 g'));await page.screenshot({path:path.join(out,'ingredient-comparison-'+theme+'-'+width+'.png'),fullPage:true});
  await page.goto(base+'/gb/en/find-a-meal/?maxCal=650');assert.equal(await page.evaluate(()=>GetMacrosMarket.current),'GB');await page.locator('.meal-row').first().waitFor();await page.screenshot({path:path.join(out,'uk-finder-'+theme+'-'+width+'.png'),fullPage:true});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);assert.deepEqual(errors,[]);
  results.push({theme,width,base,passed:['live source lookup and portion dialog','live local diary; AI disabled truthfully','Europe/Oceania documented components and serving weights','live UK finder','no runtime errors'],overflow:false});await context.close();console.log('Production journeys passed',theme,width);
 }
 fs.writeFileSync(out+'/checks.json',JSON.stringify({verifiedAt:new Date().toISOString(),results},null,2));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
