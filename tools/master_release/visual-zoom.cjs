/* 200% page-zoom-equivalent reflow: 640 CSS px rendered into 1280 device px.
   This is an emulation, not a claim of native browser chrome or text-only zoom. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out=path.resolve('docs/master-completion-2026-10-13/visual-zoom');fs.mkdirSync(out,{recursive:true});
const routes=[['US','/'],['CA','/ca/en/'],['diary','/food-diary.html?market=CA'],['finder','/ca/en/find-a-meal/?chain=Subway'],['calculator','/calculators.html'],['article','/how-to-log-food-portions.html'],['game','/play-market-memory.html']];
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port,browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']}),checks=[];
try{for(const theme of ['light','dark']){
const context=await browser.newContext({viewport:{width:640,height:475},deviceScaleFactor:2,colorScheme:theme,reducedMotion:'reduce',serviceWorkers:'block'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const p=await context.newPage();
for(const[label,route]of routes){const errors=[];const listener=e=>errors.push(e.message);p.on('pageerror',listener);await p.goto(base+route,{waitUntil:'domcontentloaded'});await p.evaluate(()=>document.fonts.ready);
if(label==='finder')await p.locator('.meal-row').first().waitFor();if(label==='diary')await p.waitForFunction(()=>window.GetMacrosFoodUI?.setDiaryDate);if(label==='game')await p.locator('[data-play-stage]').waitFor();
assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);assert.deepEqual(errors,[]);const screenshot=label+'-'+theme+'-200pc-equivalent.png';await p.screenshot({path:path.join(out,screenshot)});checks.push({theme,route,screenshot,cssViewport:{width:640,height:475},deviceScaleFactor:2,errors});p.off('pageerror',listener);}
await p.goto(base+'/ca/en/',{waitUntil:'domcontentloaded'});await p.locator('.country-picker>summary').click();const b=await p.locator('.country-panel').boundingBox();assert(b.x>=-1&&b.x+b.width<=641);await p.screenshot({path:path.join(out,'country-'+theme+'-200pc-equivalent.png')});await p.keyboard.press('Escape');assert.equal(await p.locator('.country-picker').getAttribute('open'),null);await context.close();console.log('PASS emulated 200% page zoom',theme);
}fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({checkedAt:new Date().toISOString(),base,method:'640 CSS px at device scale factor 2 emulates 1280-device-pixel viewport at 200% page zoom; does not certify native browser chrome or text-only zoom.',checks},null,2));
}finally{await browser.close();server.close()}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
