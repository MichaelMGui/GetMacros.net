const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const ids=['steak','chicken','salmon','shrimp','egg','tofu','beans','apple','banana','strawberry','orange','blueberry','avocado','carrot','broccoli','pear'];
const out=path.resolve('docs/release-2026-10-03/characters');fs.mkdirSync(out,{recursive:true});
const fixture=`<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/css/publication.css"><link rel="stylesheet" href="/tools/food-characters.css"><style>body{padding:24px}.character-fixture{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:24px;max-width:900px;margin:auto}.character-sample{text-align:center;min-width:0}.character-sample h2{font-size:16px;margin:8px 0}.fixture-title{font-size:28px;max-width:900px;margin:0 auto 24px}#after-character{display:block;margin:20px auto}</style><script defer src="/js/food-characters.js"></script></head><body><h1 class="fixture-title">The GetMacros food characters</h1><main class="character-fixture">${ids.map(id=>`<section class="character-sample"><span class="food-character" data-food-character="${id}" data-interactive="true"><svg viewBox="0 0 160 160" aria-hidden="true"><use href="/images/food-characters.svg#food-${id}"></use></svg></span><h2>${id[0].toUpperCase()+id.slice(1)}</h2></section>`).join('')}</main><button id="after-character">Continue</button></body></html>`;
(async()=>{const browser=await chromium.launch({channel:'msedge'});const reports=[];
for(const theme of ['light','dark'])for(const width of [320,390,768,1440]){
 const page=await browser.newPage({viewport:{width,height:1000},hasTouch:width<500});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',route=>{const u=new URL(route.request().url());if(u.hostname!=='127.0.0.1')return route.abort();if(u.pathname==='/__character-fixture')return route.fulfill({contentType:'text/html',body:fixture});const p=path.resolve('.'+decodeURIComponent(u.pathname));if(!p.startsWith(process.cwd()+path.sep)||!fs.existsSync(p))return route.fulfill({status:404,body:''});return route.fulfill({body:fs.readFileSync(p),contentType:{'.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.woff2':'font/woff2'}[path.extname(p)]||'text/plain'});});
 await page.goto('http://127.0.0.1:4187/__character-fixture');await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
 await page.waitForFunction(()=>document.querySelector('[data-food-character=steak] svg .food-arm-wave'));
 assert.equal(await page.locator('.food-character-trigger').count(),16);assert.equal(await page.evaluate(()=>Object.keys(GetMacrosCharacters.characters).length),16);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 const host=page.locator('[data-food-character=steak]'),button=host.locator('button'),bubble=host.locator('[role=tooltip]');
 const before=await host.boundingBox();await button.hover();await expectText(bubble,'Hi!');assert.equal(await button.getAttribute('aria-expanded'),'true');
 const after=await host.boundingBox();assert.equal(Math.round(before.height),Math.round(after.height));
 assert.equal(await host.evaluate(h=>h.querySelector('.food-arm-wave').getAnimations().length>0),true);
 await bubble.hover();assert.equal(await button.getAttribute('aria-expanded'),'true');
 await page.keyboard.press('Escape');assert.equal(await button.getAttribute('aria-expanded'),'false');
 await page.mouse.move(width-2,0);await button.focus();assert.equal(await button.getAttribute('aria-expanded'),'true');
 await page.keyboard.press('Escape');assert.equal(await button.getAttribute('aria-expanded'),'false');
 if(width<500)await button.tap();else await button.click();assert.equal(await button.getAttribute('aria-expanded'),'true');await page.locator('#after-character').click();assert.equal(await button.getAttribute('aria-expanded'),'false');
 await page.emulateMedia({reducedMotion:'reduce'});await button.focus();assert.equal(await button.getAttribute('aria-expanded'),'true');assert.equal(await host.evaluate(h=>h.getAnimations({subtree:true}).length),0);
 await page.keyboard.press('Escape');await page.locator('#after-character').focus();await page.screenshot({path:path.join(out,`gallery-${theme}-${width}.png`),fullPage:true});
 await page.emulateMedia({reducedMotion:'no-preference'});await button.focus();await page.waitForFunction(()=>getComputedStyle(document.querySelector('[data-food-character=steak] .food-character-greeting')).opacity==='1');await page.screenshot({path:path.join(out,`greeting-${theme}-${width}.png`),fullPage:true});
 const decorative=await page.evaluate(()=>{const node=GetMacrosCharacters.create('tofu');document.body.append(node);return{buttons:node.querySelectorAll('button').length,hidden:node.getAttribute('aria-hidden')};});assert.deepEqual(decorative,{buttons:0,hidden:'true'});
 assert.deepEqual(errors,[]);reports.push({theme,width,characters:16,layout:'pass',focus:'pass',hover:'pass',tapDismiss:'pass',reducedMotion:'pass',runtimeErrors:errors});await page.close();
}
await browser.close();fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify(reports,null,2));console.log(`${reports.length} theme/width combinations passed: all 16 characters, stable greeting layout, hover/focus/tap dismissal, reduced motion, decorative semantics, no overflow or runtime errors.`);
})().catch(e=>{console.error(e);process.exit(1)});
async function expectText(locator,text){assert.equal(await locator.textContent(),text);assert.equal(await locator.evaluate(e=>getComputedStyle(e).visibility),'visible');}
