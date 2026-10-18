const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..'),serveRoot=process.env.GM_SOURCE_ROOT||root,out=path.join(root,'docs/interface-clarity-2026-10-18');
const baseline=process.argv.includes('--baseline'),shots=path.join(out,baseline?'before':'after');fs.mkdirSync(shots,{recursive:true});
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.gz':'application/gzip'};
const server=http.createServer((req,res)=>{let file=path.resolve(serveRoot,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(file!==serveRoot&&!file.startsWith(serveRoot+path.sep)){res.writeHead(403).end();return;}if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');if(!fs.existsSync(file)){res.writeHead(404).end();return;}res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
let browser;
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=process.env.GM_TEST_BASE||'http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});const context=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'}),page=await context.newPage();
 const errors=[],checks=[];page.on('pageerror',e=>errors.push(e.message));
 await context.addInitScript(()=>{localStorage.setItem('gm-theme','dark');if(document.documentElement)document.documentElement.dataset.theme='dark';});
 const shot=async name=>{await page.evaluate(async()=>{document.documentElement.dataset.theme='dark';await document.fonts.ready;await Promise.all(document.getAnimations().filter(a=>a.effect?.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>{})));});await page.screenshot({path:path.join(shots,name+'.png')});};
 await page.goto(base+'/food-diary.html');await page.locator('[data-meal-add=Breakfast]').click();await page.locator('[data-browse-food]').first().waitFor();
 await shot('diary-mobile-dark');
 await page.setViewportSize({width:1280,height:950});await page.goto(base+'/articles.html');await page.locator('#reading-topic-select').selectOption({label:'Coffee & Drinks'});await page.locator('.reading-topic-choice').scrollIntoViewIfNeeded();await shot('learn-desktop-dark');
 await page.goto(base+'/restaurant-meal-finder.html');
 const trigger=page.locator('[data-open-guide]').first();await trigger.click();await page.locator('[data-guide-step="0"] input[value="any"]').check();await page.locator('[data-guide-next]').click();await shot('quiz-restaurants-desktop-dark');
 if(!baseline){
  for(const theme of ['light','dark'])for(const width of [320,390,768,1280,1440]){
   const c=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block',reducedMotion:'reduce'});
   await c.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const p=await c.newPage();p.on('pageerror',e=>errors.push(e.message));
   const fits=async label=>assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1&&[...document.querySelectorAll('dialog[open]')].every(d=>d.scrollWidth<=d.clientWidth+1)),label+' overflow '+width+' '+theme);
   await p.goto(base+'/food-diary.html');await p.locator('[data-meal-add="Breakfast"]').click();await p.locator('[data-browse-food]').first().waitFor();
   assert.equal(await p.locator('select[name=pickerMeal]').inputValue(),'Breakfast');
   const q=p.locator('[data-food-query]'),submit=p.locator('[data-food-search] button[type=submit]'),a=await q.boundingBox(),b=await submit.boundingBox();
   assert(Math.abs(a.y-b.y)<=1&&Math.abs(a.height-b.height)<=1,'Search field/button alignment');
   assert((await p.locator('[data-browse-food]').first().boundingBox()).y<410,'First food visible without scrolling');
   await q.focus();assert.equal(await q.evaluate(e=>getComputedStyle(e).outlineStyle),'none','No surrounding search focus rectangle');
   assert.notEqual(await q.evaluate(e=>getComputedStyle(e).boxShadow),'none','Search retains a visible focus underline');
   await fits('Picker');assert(await p.locator('.food-picker-tabs').evaluate(e=>e.scrollWidth<=e.clientWidth+1),'All source tabs fit '+JSON.stringify(await p.locator('.food-picker-tabs').evaluate(e=>({width:e.clientWidth,scroll:e.scrollWidth,gap:getComputedStyle(e).gap,buttons:[...e.children].map(b=>[b.textContent,b.getBoundingClientRect().width,getComputedStyle(b).padding,getComputedStyle(b).fontSize])}))));
   await p.locator('.food-search-options summary').click();await fits('Expanded filters');
   await p.locator('.food-search-options summary').click();await p.locator('[data-food-browse-controls] summary').click();await fits('Expanded categories');await p.locator('[data-food-browse-controls] summary').click();
   await p.screenshot({path:path.join(shots,`picker-${theme}-${width}.png`)});
   await q.fill('rice');await p.waitForFunction(()=>document.querySelector('[data-food-status]').textContent.includes('results'));
   await p.locator('[data-food-results] .food-search-row').first().click();await p.locator('#food-review[open]').waitFor();
   assert.equal(await p.locator('#food-review [name=occasion]').inputValue(),'Breakfast');await fits('Portion review');
   if(width===390)await p.screenshot({path:path.join(shots,`review-${theme}-${width}.png`)});
   await p.locator('[data-review-save]').click();await p.locator('[data-diary-occasion="Breakfast"] .diary-entry').waitFor();await p.reload();await p.locator('[data-diary-occasion="Breakfast"] .diary-entry').waitFor();
   await p.locator('[data-meal-add="Dinner"]').click();await p.locator('select[name=pickerMeal]').selectOption('Snack');assert.equal(await p.locator('select[name=pickerMeal]').inputValue(),'Snack');
   await p.locator('[data-food-tab=recent]').click();await p.locator('[data-food-tab=recent]').press('ArrowRight');assert.equal(await p.locator('[data-food-tab=favorites]').getAttribute('aria-selected'),'true');await p.keyboard.press('Escape');
   await p.goto(base+'/restaurant-meal-finder.html');await p.locator('[data-open-guide]').first().click();assert.equal(await p.locator('.guided-dialog input:checked').count(),0);
   await p.locator('[data-guide-step="0"] input[value="any"]').check();await p.locator('[data-guide-next]').click();
   const restaurant=p.locator('[data-guide-search]');await restaurant.fill('kfc');await p.locator('.guided-dialog [name=chain][value=KFC]').check();await restaurant.fill('');assert.equal(await p.locator('.guided-dialog [name=chain][value=KFC]').isChecked(),true);
   assert.equal(await p.locator('.guided-restaurants .guide-answer').first().evaluate(e=>getComputedStyle(e).borderLeftWidth),'0px');
   await p.locator('.guided-dialog [name=chain][value=any]').check();assert.equal(await p.locator('.guided-dialog [name=chain][value=KFC]').isChecked(),false);await fits('Restaurant quiz');
   if([320,390,1440].includes(width))await p.screenshot({path:path.join(shots,`quiz-${theme}-${width}.png`)});
   await p.locator('[data-guide-next]').click();await p.locator('.guided-dialog [name=goal][value=protein]').check();await p.locator('[data-guide-next]').click();await p.locator('[data-guide-next]').click();await p.locator('.results-grid article').first().waitFor();await fits('Quiz results');
   await p.goto(base+'/articles.html');await p.locator('#reading-topic-select').selectOption({label:'Coffee & Drinks'});assert.equal(await p.locator('#reading-topic-select').evaluate(e=>getComputedStyle(e).borderLeftWidth),'0px');await fits('Learn topic');
   for(const route of ['/','/ca/en/','/food-library.html','/calculators.html','/how-to-read-a-nutrition-label.html']){await p.goto(base+route);await p.locator('main').waitFor();await fits(route);}
   assert.equal(await p.evaluate(()=>document.documentElement.dataset.theme),theme,'Theme persists across routes');
   checks.push(`${theme} ${width}px: aligned search, unclipped meal selector, filters, categories, portions, logging/reload, tabs, quiz selection/results, Learn and five shared-style routes`);
   await c.close();
  }
 }
 assert.equal(errors.length,0,errors.join('\n'));fs.writeFileSync(path.join(out,baseline?'baseline.json':'browser-results.json'),JSON.stringify({base,checks,runtimeErrors:errors,screenshots:fs.readdirSync(shots)},null,2));console.log(JSON.stringify({base,checks,screenshots:shots}));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();server.close();});
