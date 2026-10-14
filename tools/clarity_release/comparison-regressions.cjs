/* Original reviewer regressions against real local source records and native Edge.
 * No generators, source mutation, personal user data or fabricated nutrients.
 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const F=require('../../js/food-core.js'),C=require('../../js/food-comparison-state.js');
const orders=JSON.parse(fs.readFileSync('js/order-registry.json','utf8')).records;
const raw={
 ca:orders.find(r=>r.market==='CA'&&r.chain==='Triple O’s'&&r.name==='Chicken Bacon Cheddar'),
 mx:orders.find(r=>r.id==='MX|subway|1c5926505abe2837'),
 wrap:orders.find(r=>r.market==='CA'&&r.chain==='Triple O’s'&&r.name==='Loaded Breakfast Wrap')
};
assert(Object.values(raw).every(Boolean),'Required actual reviewed source records exist');
const records=Object.fromEntries(Object.entries(raw).map(([k,r])=>[k,F.restaurant(r)]));
const snapshots=Object.fromEntries(Object.entries(records).map(([k,r])=>[k,F.snapshot(r,1,'serving')]));
const checks=[];

async function missingShard(){
 const context={window:{GetMacrosFood:F},Map,Error,fetch:async url=>{
  const value=url==='/data/food-library/manifest.json'?{}:
   url==='/data/food-library/index.json'?[{id:'fdc:12345',shard:'00',name:'Unavailable indexed profile'}]:
   url==='/js/order-registry.json'?{records:[raw.mx]}:
   url==='/data/food-library/records/00.json'?[]:undefined;
  assert.notEqual(value,undefined,'Only expected same-origin fixture requests');
  return {ok:true,json:async()=>value};
 }};
 vm.runInNewContext(fs.readFileSync('js/food-library.js','utf8'),context);
 await assert.rejects(()=>context.window.GetMacrosLibrary.get('fdc:12345'),/unavailable in this source edition/);
 const current=await context.window.GetMacrosLibrary.get(records.mx.id);
 assert.equal(current.nutrients.cal,270);assert.equal(current.market,'MX');
 checks.push('Missing indexed shard record reports a friendly unavailable-edition error; cold restaurant lookup still succeeds.');
}

process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
(async()=>{
 await missingShard();if(!server.listening)await new Promise(resolve=>server.once('listening',resolve));
 const base=process.env.LIVE_BASE||'http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});
 try{for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:950},serviceWorkers:'block',reducedMotion:'reduce'});
  const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(error.message));
  try{
   // Review controls must carry both the numeric amount and exact measure.
   for(const [measure,quantity]of [['serving','2'],['g','125']]){
    await page.goto(base+'/food-library.html?'+new URLSearchParams({market:'CA',food:records.ca.id}));
    await page.locator('#food-review').waitFor({state:'visible'});
    await page.locator('#food-review [name=measure]').selectOption(measure);
    await page.locator('#food-review [name=quantity]').fill(quantity);
    const link=page.locator('[data-review-log]'),url=new URL(await link.getAttribute('href'),base);
    assert.equal(url.searchParams.get('quantity'),quantity);assert.equal(url.searchParams.get('measure'),measure);assert.equal(url.searchParams.get('market'),'CA');
    await page.locator('#food-review [name=quantity]').fill('0');
    assert.equal(await link.getAttribute('href'),null);assert.equal(await link.getAttribute('aria-disabled'),'true');assert.equal(await link.getAttribute('tabindex'),'-1');
    await page.locator('#food-review [name=quantity]').fill(quantity);await link.click();
    await page.locator('#food-review').waitFor({state:'visible'});
    assert.equal(await page.locator('#food-review [name=quantity]').inputValue(),quantity);
    assert.equal(await page.locator('#food-review [name=measure]').inputValue(),measure);
    assert.equal(await page.locator('#food-review [data-review-title]').innerText(),records.ca.name);
   }
   checks.push(width+'px: review → diary preserves serving/gram quantities, market and identity; invalid portion disables its link.');

   // Native deferred fetch reproduces the original hydration window.
   await page.goto(base+'/compare-foods.html');
   await page.evaluate(s=>localStorage.setItem('gm-reviewed-comparison-v1',JSON.stringify(s)),[snapshots.ca,snapshots.wrap]);
   let release;const gate=new Promise(resolve=>release=resolve);
   await page.route('**/assets/generated/js-order-registry*',async route=>{await gate;await route.continue();});
   await page.route('**/js/order-registry.json*',async route=>{await gate;await route.continue();});
   try{
    await page.goto(C.link([snapshots.mx,snapshots.wrap],'portions',base),{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.querySelector('[data-food-comparison]')?.hasAttribute('aria-busy'));
    assert(await page.locator('[data-food-compare-content]').isHidden());
    assert(await page.locator('[data-food-compare-basis]').isDisabled());
    assert(await page.locator('[data-food-compare-clear]').isDisabled());
    assert(await page.getByRole('button',{name:'Share comparison'}).isDisabled());
    assert(await page.getByRole('button',{name:'Download comparison card'}).isDisabled());
    // A separately loaded real grocery can resolve before the restaurant
    // response. Its review action must not create a selection that disappears.
    await page.getByText('Filter results',{exact:true}).click();
    await page.locator('[data-food-type]').selectOption('branded');
    await page.locator('[data-food-query]').fill('Kirkland macadamia');
    await page.locator('[data-food-search]').evaluate(form=>form.requestSubmit());
    await page.waitForFunction(()=>document.querySelector('[data-food-results] [data-food-id]'));
    await page.locator('[data-food-results] [data-food-id]').first().click();
    await page.locator('#food-review').waitFor({state:'visible'});
    assert((await page.locator('[data-review-title]').innerText()).includes('Macadamia'));
    const compare=page.locator('[data-review-compare]');
    if(!await compare.isDisabled()){
     await compare.click();
     assert(await page.locator('#food-review').isVisible(),'Pending comparison mutation is rejected before closing the review');
     assert((await page.locator('[data-review-error]').innerText()).length>0,'Pending comparison mutation provides useful feedback');
    }
    const retained=await page.evaluate(()=>JSON.parse(localStorage.getItem('gm-reviewed-comparison-v1')));
    assert.deepEqual(retained.map(s=>s.recordId),[records.ca.id,records.wrap.id],'Pending linked record resolution cannot silently overwrite a newly accepted grocery');
    await page.locator('[data-review-close]').click();
    release();await page.waitForFunction(()=>!document.querySelector('[data-food-comparison]')?.hasAttribute('aria-busy'));
   }finally{release();await page.unroute('**/assets/generated/js-order-registry*');await page.unroute('**/js/order-registry.json*');}
   assert(await page.locator('[data-food-compare-content]').isVisible());
   assert.equal(await page.locator('.food-comparison-identities article h3').first().innerText(),records.mx.name);
   assert.equal(await page.locator('.food-comparison-identities article h3').last().innerText(),records.wrap.name);
   let text=await page.locator('.food-comparison-identities').innerText();
   assert(!/\b1\s+1\s|official-table-reviewed|calculated-from-official-components|source-linked/.test(text),'Ordinary summary copy has no repeated quantity prefix or raw internal status');
   checks.push(width+'px: delayed deep-link hydration hides prior content, locks comparison controls and rejects independently loaded grocery additions, then exposes the correct linked market records.');

   // Simulate a concurrent state mutation while a source review is open.
   // The underlying real Remove event changes the slot; the edit must reject it.
   await page.locator('.comparison-food-actions').first().getByRole('button',{name:'Edit portion'}).click();
   await page.locator('#food-review [name=quantity]').fill('2');
   await page.locator('.comparison-food-actions').first().getByRole('button',{name:'Remove',exact:true}).evaluate(button=>button.click());
   await page.locator('[data-review-compare]').click();
   assert((await page.locator('[data-review-error]').innerText()).includes('comparison changed'));
   assert.equal(await page.locator('.food-comparison-identities article').count(),1);
   const kept=await page.evaluate(()=>JSON.parse(localStorage.getItem('gm-reviewed-comparison-v1')));
   assert.equal(kept[0].recordId,records.wrap.id);assert.equal(kept[0].quantity,1);
   await page.locator('[data-review-close]').click();
   checks.push(width+'px: stale edit detects a changed slot and cannot replace the surviving food.');

   await page.goto(base+'/compare-foods.html');
   await page.evaluate(s=>localStorage.setItem('gm-reviewed-comparison-v1',JSON.stringify(s)),[snapshots.ca,snapshots.mx]);
   await page.reload();await page.waitForFunction(()=>document.querySelector('[data-food-compare-content] table'));
   await page.locator('[data-food-compare-basis]').selectOption('100g');await page.reload();
   await page.waitForFunction(()=>document.querySelector('[data-food-compare-content] table'));
   assert.equal(await page.locator('[data-food-compare-basis]').inputValue(),'100g');
   assert.equal(await page.locator('table caption').innerText(),'Nutrition per 100 g of each source food');
   checks.push(width+'px: explicit 100 g comparison basis survives reload.');

   await page.goto(base+'/ca/en/restaurants/triple-os/');
   const action=page.getByRole('link',{name:'Search exact servings →'}),url=new URL(await action.getAttribute('href'),base);
   assert.equal(url.searchParams.get('market'),'CA');assert.equal(url.searchParams.get('type'),'restaurant');assert.equal(url.searchParams.get('q'),'Triple O’s');
   await action.click();await page.waitForFunction(()=>document.querySelector('[data-food-status]')?.textContent&&!/^Searching|^Loading/.test(document.querySelector('[data-food-status]').textContent));
   assert.equal(await page.locator('[data-food-type]').inputValue(),'restaurant');
   assert(await page.locator('[data-food-results] [data-food-id]').count()>0);
   assert((await page.locator('[data-food-results]').innerText()).includes('Triple O’s'));
   checks.push(width+'px: restaurant guide opens actual Canadian restaurant-food search results.');
   assert.deepEqual(errors,[]);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  }finally{await context.close();}
 }}finally{await browser.close();}
 console.log('PASS: '+checks.length+' reviewer regressions.');checks.forEach(check=>console.log('PASS '+check));
})().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>server.close());
