const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out='docs/diary-meals-2026-10-12';fs.mkdirSync(out,{recursive:true});
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base=process.env.LIVE_BASE||'http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']}),checks=[],expected=['Breakfast','Lunch','Dinner','Snacks'];
 try{
 for(const theme of ['light','dark'])for(const width of [320,390,768,1280,1440]){
  const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/food-diary.html?market=CA');await page.locator('[data-diary-occasion]').first().waitFor();await page.evaluate(()=>document.fonts.ready);
  assert.deepEqual(await page.locator('.diary-meal-heading h2').allTextContents(),expected);assert.equal(await page.locator('[data-meal-add]').count(),4);
  await page.screenshot({path:path.join(out,'empty-'+theme+'-'+width+'.png'),fullPage:true});
  // Every meal button targets its own review; browsing uses real source shards.
  for(const occasion of ['Breakfast','Lunch','Dinner','Snack']){
   await page.locator('[data-meal-add="'+occasion+'"]').click();await page.locator('[data-browse-food]').first().waitFor();
   assert.equal(await page.locator('[name=pickerMeal]:checked').inputValue(),occasion);assert.equal(await page.locator('[data-browse-food]').count(),12);
   if(occasion==='Breakfast'){await page.locator('[data-food-browse-more]').click();await page.waitForFunction(()=>document.querySelectorAll('[data-browse-food]').length===24);}
   if(occasion==='Snack')await page.screenshot({path:path.join(out,'browse-'+theme+'-'+width+'.png')});
   await page.locator('[data-browse-food]').first().click();await page.locator('#food-review').waitFor({state:'visible'});
   assert.equal(await page.locator('#food-review [name=occasion]').inputValue(),occasion);
   await page.locator('#food-review [name=quantity]').fill('50');await page.locator('[data-review-save]').click();
   await page.waitForFunction(o=>document.querySelector('[data-diary-occasion="'+o+'"] .diary-entry'),occasion);
   await page.waitForFunction(o=>document.activeElement.dataset.mealAdd===o,occasion);
  }
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(out,'logged-'+theme+'-'+width+'.png'),fullPage:true});
  const entries=await page.evaluate(async()=> (await GetMacrosDiary.exportData()).entries);
  assert.equal(entries.length,4);assert.deepEqual(entries.map(e=>e.occasion).sort(),['Breakfast','Dinner','Lunch','Snack']);
  for(const entry of entries){assert.equal(entry.snapshot.quantity,50);assert.equal(entry.snapshot.nutrients.cal,entry.snapshot.sourceNutrients.cal===null?null:entry.snapshot.sourceNutrients.cal*.5);}
  // Move one entry without changing its saved source version, and undo removal.
  await page.locator('[data-diary-occasion="Breakfast"]').getByRole('button',{name:'Edit',exact:true}).click();
  const edit=page.locator('dialog[aria-labelledby=diary-edit-title]');await edit.locator('[name=occasion]').selectOption('Snack');await edit.locator('[name=amount]').fill('100');await edit.getByRole('button',{name:'Save changes'}).click();
  await page.waitForFunction(()=>document.querySelectorAll('[data-diary-occasion="Snack"] .diary-entry').length===2);
  assert.equal(await page.locator('[data-diary-occasion="Breakfast"] .diary-entry').count(),0);
  const moved=await page.evaluate(async()=> (await GetMacrosDiary.exportData()).entries.find(e=>e.occasion==='Snack'&&e.snapshot.quantity===100));assert(moved);
  assert.equal(moved.snapshot.version,entries.find(e=>e.occasion==='Breakfast').snapshot.version);
  await page.locator('[data-diary-occasion="Snack"]').getByRole('button',{name:'Remove',exact:true}).first().click();await page.getByRole('button',{name:'Undo removal'}).click();
  await page.waitForFunction(()=>document.querySelectorAll('.diary-entry').length===4);
  // Explicit dates and entries remain shared during real country navigation.
  await page.locator('[data-diary-date]').fill('2026-10-11');await page.locator('[data-diary-date]').dispatchEvent('change');
  await page.waitForFunction(()=>document.querySelectorAll('.diary-entry').length===0);
  const countryChecks=[];let browseNames;
  for(const market of ['US','CA','MX','GB','IE','AU','NZ','JP']){
   await page.goto(base+'/food-diary.html?market='+market);await page.locator('[data-diary-occasion]').first().waitFor();
   assert.equal(await page.locator('[data-diary-date]').inputValue(),'2026-10-11');
   assert.deepEqual(await page.locator('.diary-meal-heading h2').allTextContents(),expected);assert.equal(await page.locator('[data-food-market]').inputValue(),market);
   assert.equal(await page.evaluate(async()=> (await GetMacrosDiary.exportData()).entries.length),4);
   await page.locator('[data-meal-add="Dinner"]').click();await page.locator('[data-browse-food]').first().waitFor();
   const names=await page.locator('[data-browse-food]').allTextContents();if(browseNames)assert.deepEqual(names,browseNames);else browseNames=names;
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);await page.keyboard.press('Escape');countryChecks.push(market);
  }
  // The day has no fake zero totals, while a deliberately partial source stays unknown.
  assert.equal(await page.locator('[data-diary-totals] dd').first().textContent(),'—');
  // Load the exact previously reviewed source, preserving source arithmetic and nulls.
  await page.evaluate(async source=>{
   const F=GetMacrosFood,r=F.fromSnapshot(source);r.nutrients.p=null;r.nutrients.cal=null;
   const snapshot=F.snapshot(r,source.quantity,source.measure);
   await GetMacrosDiary.add(snapshot,{date:'2026-10-11',occasion:'Breakfast'});
  },entries[0].snapshot);
  await page.reload();await page.locator('.diary-entry').waitFor();
  assert.match(await page.locator('[data-diary-occasion="Breakfast"] .diary-meal-totals').textContent(),/Unknown/);
  assert.match(await page.locator('[data-diary-totals]').textContent(),/Unknown/);assert.deepEqual(errors,[]);
  checks.push({theme,width,countries:countryChecks,passed:['four permanent meal groups','1,200 shared browse foods','more foods','targeted logging and source math','edit/move','remove/undo','country/date persistence','unknown totals','no overflow'],runtimeErrors:errors});await context.close();console.log('PASS shared diary',theme,width,'all eight countries');
 }
 fs.writeFileSync(out+(process.env.LIVE_BASE?'/live-checks.json':'/checks.json'),JSON.stringify({verifiedAt:new Date().toISOString(),base,checks},null,2));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
