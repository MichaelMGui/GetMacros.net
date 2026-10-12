/* Native IndexedDB, real source files and rendered controls; no mocked nutrition. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out='docs/diary-more-2026-10-12'+(process.env.LIVE_BASE?'/production':'/browser');fs.mkdirSync(out,{recursive:true});
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base=process.env.LIVE_BASE||'http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']}),checks=[];
 try{for(const theme of ['light','dark'])for(const width of [320,390,768,1280,1440]){
  const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce',timezoneId:'America/Toronto'});
  await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/food-diary.html?market=CA');await page.waitForFunction(()=>GetMacrosFoodUI?.setDiaryDate&&GetMacrosDiary?.copyMeal);
  await page.getByRole('button',{name:'Repeat meal',exact:true}).click();const repeat=page.locator('#diary-repeat');
  await repeat.getByText('No foods logged for this meal.',{exact:false}).waitFor();assert.equal(await repeat.locator('[data-repeat-save]').isDisabled(),true);await page.keyboard.press('Escape');
  // Day navigation uses calendar arithmetic even across local daylight-saving changes.
  await page.evaluate(()=>GetMacrosFoodUI.setDiaryDate('2026-03-08'));await page.getByRole('button',{name:'Next day',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('[data-diary-date]').value==='2026-03-09');await page.getByRole('button',{name:'Previous day',exact:true}).click();
  await page.waitForFunction(()=>document.querySelector('[data-diary-date]').value==='2026-03-08');await page.getByRole('button',{name:'Today',exact:true}).click();
  assert.equal(await page.locator('[data-diary-date]').inputValue(),await page.evaluate(()=>GetMacrosFood.today()));
  // Browse remains small and loads the actual profile only after selection.
  await page.locator('[data-meal-add=Breakfast]').click();await page.locator('[data-browse-food]').first().waitFor();
  assert.equal(await page.locator('[data-browse-food]').count(),12);assert((await page.locator('[data-food-browse-caption]').innerText()).includes('9,905'));
  await page.locator('[data-food-browse-group]').selectOption('protein');await page.locator('[data-food-browse-preparation]').selectOption('raw');
  await page.waitForFunction(()=>document.querySelectorAll('[data-browse-food]').length===12&&Array.from(document.querySelectorAll('[data-browse-food]')).every(r=>/\braw\b/i.test(r.firstChild.textContent)));
  const rawNames=await page.locator('[data-browse-food]').evaluateAll(rows=>rows.map(r=>r.firstChild.textContent));assert.equal(rawNames.length,12);
  assert(rawNames.every(n=>/\braw\b/i.test(n)&&!/\b(cooked|roasted|baked|grilled|boiled|steamed|fried|poached|stewed|microwaved)\b/i.test(n)));
  await page.locator('[data-food-browse-preparation]').selectOption('cooked');await page.waitForFunction(()=>document.querySelectorAll('[data-browse-food]').length===12&&Array.from(document.querySelectorAll('[data-browse-food]')).every(r=>/\b(cooked|roasted|baked|grilled|boiled|steamed|fried|poached|stewed|microwaved)\b/i.test(r.firstChild.textContent)));
  const cookedNames=await page.locator('[data-browse-food]').evaluateAll(rows=>rows.map(r=>r.firstChild.textContent));assert.equal(cookedNames.length,12);
  await page.getByText('Filter results',{exact:true}).click();await page.locator('[data-food-sort]').selectOption('name');await page.waitForFunction(()=>{const n=Array.from(document.querySelectorAll('[data-browse-food]')).map(r=>r.firstChild.textContent);return n.every((v,i)=>!i||n[i-1].localeCompare(v)<=0)});
  await page.screenshot({path:path.join(out,'preparation-'+theme+'-'+width+'.png')});await page.keyboard.press('Escape');
  await page.locator('[data-meal-add=Breakfast]').click();assert.equal(await page.locator('[data-food-browse-group]').inputValue(),'protein');await page.keyboard.press('Escape');
  // Two real source portions, including a Canadian package, form the saved meal.
  const originals=await page.evaluate(async()=>{
   const F=GetMacrosFood,L=GetMacrosLibrary,S=GetMacrosDiary;
   const egg=await L.reference('fdc:173424','10'),caRows=await L.search('Kirkland',{market:'CA',type:'branded'}),product=await L.get(caRows.find(r=>r.name.includes('Yogurt')).id);
   const a=await S.add(F.snapshot(egg,70,'g'),{date:'2026-03-08',occasion:'Lunch',note:'Private source note'});
   const b=await S.add(F.snapshot(product,1,'source-serving'),{date:'2026-03-08',occasion:'Lunch'});
   return [a,b];
  });
  assert.equal(originals[1].snapshot.market,'CA');await page.evaluate(()=>GetMacrosFoodUI.setDiaryDate('2026-03-09'));
  await page.getByRole('button',{name:'Repeat meal',exact:true}).click();await repeat.locator('[data-repeat-preview] li').first().waitFor();
  assert.equal(await repeat.locator('[name=sourceDate]').inputValue(),'2026-03-08');assert.equal(await repeat.locator('[name=source]').inputValue(),'Lunch');
  assert.equal(await repeat.locator('[data-repeat-preview] li').count(),2);assert((await repeat.locator('[data-repeat-preview]').textContent()).includes('Canada'));
  await repeat.locator('[name=targetMeal]').selectOption('Dinner');
  await page.screenshot({path:path.join(out,'repeat-'+theme+'-'+width+'.png')});
  // A rapid second submission must not duplicate a confirmed copy.
  await repeat.locator('form').evaluate(f=>{f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));});
  await page.waitForFunction(async()=> (await GetMacrosDiary.list('2026-03-09')).length===2);
  const copies=await page.evaluate(()=>GetMacrosDiary.list('2026-03-09'));assert(copies.every(e=>e.occasion==='Dinner'&&e.note===''));
  copies.forEach(entry=>{const original=originals.find(r=>r.snapshot.recordId===entry.snapshot.recordId);assert(original);assert.deepEqual(entry.snapshot,original.snapshot);assert.deepEqual(entry.copiedFrom,{date:'2026-03-08',occasion:'Lunch'});assert.notEqual(entry.id,original.id)});
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:path.join(out,'copied-'+theme+'-'+width+'.png'),fullPage:true});
  // Invalid batches cannot partly insert, and a retried operation has stable IDs.
  const integrity=await page.evaluate(async rows=>{
   const S=GetMacrosDiary;const bad=structuredClone(rows);bad[1].snapshot.nutrients.cal=0;let rejected=false;
   try{await S.copyMeal(bad,{date:'2026-03-10',occasion:'Snack',operationId:'invalid-copy'})}catch{rejected=true}
   const empty=(await S.list('2026-03-10')).length;
   await S.copyMeal(rows,{date:'2026-03-11',occasion:'Breakfast',operationId:'repeat-idempotence',copyNotes:true});
   await S.copyMeal(rows,{date:'2026-03-11',occasion:'Breakfast',operationId:'repeat-idempotence',copyNotes:true});
   return {dayCount:await S.loggedDayCount(3),rejected,empty,count:(await S.list('2026-03-11')).length,notes:(await S.list('2026-03-11')).map(r=>r.note),originals:await S.list('2026-03-08'),last:await S.lastLoggedDate('2026-03-10')};
  },originals);
  assert.equal(integrity.dayCount,3);assert.equal(integrity.rejected,true);assert.equal(integrity.empty,0);assert.equal(integrity.count,2);assert(integrity.notes.includes('Private source note'));assert.deepEqual(integrity.originals.sort((a,b)=>a.id.localeCompare(b.id)),originals.sort((a,b)=>a.id.localeCompare(b.id)));assert.equal(integrity.last,'2026-03-09');
  // Explicit notes are available through the actual review, and same-meal copies warn.
  await page.getByRole('button',{name:'Repeat meal',exact:true}).click();await repeat.locator('[data-repeat-preview] li').first().waitFor();
  await repeat.locator('[name=sourceDate]').fill('2026-03-08');await repeat.locator('[name=sourceDate]').dispatchEvent('change');await repeat.locator('[name=source]').selectOption('Lunch');
  await repeat.locator('[name=targetDate]').fill('2026-03-08');await repeat.locator('[name=targetDate]').dispatchEvent('change');await repeat.locator('[name=targetMeal]').selectOption('Lunch');
  assert.equal(await repeat.locator('[data-repeat-warning]').isVisible(),true);
  await repeat.locator('[name=targetDate]').fill('2026-03-12');await repeat.locator('[name=targetDate]').dispatchEvent('change');await repeat.locator('[name=copyNotes]').check();await repeat.locator('[data-repeat-save]').click();
  await page.waitForFunction(async()=> (await GetMacrosDiary.list('2026-03-12')).length===2);assert((await page.evaluate(()=>GetMacrosDiary.list('2026-03-12'))).some(r=>r.note==='Private source note'));
  await page.goto(base+'/food-diary.html?market=JP');await page.locator('.diary-entry').first().waitFor();assert.equal(await page.locator('[data-diary-date]').inputValue(),'2026-03-12');assert.equal(await page.locator('.diary-entry').count(),2);
  assert((await page.locator('.food-entry-portion').allTextContents()).some(t=>t.includes('Canada')));assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  const exported=await page.evaluate(()=>GetMacrosDiary.exportData());await page.evaluate(data=>GetMacrosFood.validateExport(data),exported);
  assert.deepEqual(errors,[]);checks.push({theme,width,catalogueCount:9905,checks:['empty repeat state','day controls and daylight-saving date','raw/cooked preparations','alphabetical browse','remembered group','exact source and country copy','double-submit','invalid-batch rejection','retry IDs','optional private notes','same-meal warning','date/country persistence','export integrity','no overflow or runtime errors']});
  await context.close();console.log('PASS expanded diary',theme,width);
 }fs.writeFileSync(out+'/checks.json',JSON.stringify({verifiedAt:new Date().toISOString(),base,checks},null,2));
 }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
