const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('../browser-fixture.cjs'),catalogue=require('./catalogue.json');
const output=path.resolve('docs/play-release-2026-10-04');fs.mkdirSync(output,{recursive:true});
const results=[],errors=[];let browser;
async function action(page,a){
 if(a.type==='input'){await page.locator(`[data-play-input="${a.index}"]`).fill(String(a.value));return;}
 if(a.type==='pair'){await page.locator(`[data-play-pair="${a.row}"]`).selectOption(String(a.index));return;}
 if(a.type==='custom'){await page.locator(`[data-play-custom="${a.key}"]`).selectOption(String(a.value));return;}
 if(a.type==='count'){let state=await page.evaluate(()=>GetMacrosPlay.getState());const delta=a.value-state.counts[a.index];for(let j=0;j<Math.abs(delta);j++)await page.locator(`[data-play-focus="${delta>0?'more':'less'}-${a.index}"]`).click();return;}
 const serialized=JSON.stringify(a);const b=page.locator('[data-play-action]').filter({has:undefined});let found=false;
 for(let i=0;i<await b.count();i++){if(await b.nth(i).getAttribute('data-play-action')===serialized){await b.nth(i).click();found=true;break;}}
 if(!found)throw Error('Missing rendered control '+serialized);
}
(async()=>{try{browser=await chromium.launch({channel:'msedge',headless:true});
for(const theme of ['light','dark'])for(const width of [390,1440]){
 const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'}),page=await context.newPage();await localAssets(page);await page.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);page.on('pageerror',e=>errors.push({theme,width,message:e.message}));
 for(const [id,title,cat]of catalogue){await page.goto('https://127.0.0.1:4187/play-'+id+'.html?seed=17');await page.waitForFunction(()=>window.GetMacrosPlay);let state=await page.evaluate(()=>GetMacrosPlay.getState());assert(!state.blocked,id+' blocked');
 await page.locator('[data-play-pause]').click();assert(await page.locator('[data-play-stage]').isHidden(),id+' pause');await page.locator('[data-play-resume]').click();
 if(['serving-size-detective','fruit-catch','pantry-pack','food-crossword','market-memory','mascot-maker','macro-grid','garden-pipes'].includes(id))await page.screenshot({path:path.join(output,`${id}-${theme}-${width}.png`),fullPage:true});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert(!overflow,id+' horizontal overflow '+width);
 for(const a of state.solution){await action(page,a);const current=await page.evaluate(()=>GetMacrosPlay.getState());assert(!current.error,`${id}: ${current.error} after ${JSON.stringify(a)}`);}
 assert(await page.evaluate(()=>GetMacrosPlay.getState().done),id+' not completed');await page.locator('[data-play-restart]').click();assert(!await page.evaluate(()=>GetMacrosPlay.getState().done),id+' not reset');assert.equal(await page.evaluate(()=>GetMacrosPlay.getState().seed),17,'reset changed seed');await page.locator('[data-play-new]').first().click();assert.equal(await page.evaluate(()=>GetMacrosPlay.getState().seed),18,'new did not change seed');
 results.push({id,title,category:cat,theme,width,solved:true,pause:true,restart:true,newPuzzle:true,overflow:false});
 }
 await page.goto('https://127.0.0.1:4187/play.html');await page.screenshot({path:path.join(output,`directory-${theme}-${width}.png`),fullPage:true});await page.locator('.play-directory-nav a').last().click();assert(await page.locator('#advanced-puzzles').getAttribute('open')!==null,'category navigation did not open');await context.close();
}
assert.equal(errors.length,0,JSON.stringify(errors));fs.writeFileSync(path.join(output,'browser-checks.json'),JSON.stringify({results,errors},null,2));console.log(`PASS: ${results.length} rendered game solutions, pause/restart/new-seed and overflow checks; ${errors.length} runtime errors.`);
}finally{if(browser)await browser.close();}})().catch(e=>{fs.writeFileSync(path.join(output,'browser-failure.json'),JSON.stringify({error:e.stack,results,errors},null,2));console.error(e);process.exitCode=1;});
