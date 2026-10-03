const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),cp=require('child_process'),{localAssets}=require('./browser-fixture.cjs');
(async()=>{const browser=await chromium.launch({channel:'msedge'});const out='docs/release-2026-10-03/baseline';fs.mkdirSync(out,{recursive:true});
const original=cp.execFileSync('git',['show','HEAD:js/meal-finder.js']);
for(const theme of ['light','dark'])for(const width of [390,1440]){
 const page=await browser.newPage({viewport:{width,height:1000}});await localAssets(page);await page.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
 await page.route('**/js/meal-finder.js*',r=>r.fulfill({body:original,contentType:'text/javascript'}));
 for(const route of ['index.html','restaurant-meal-finder.html','calculators.html','how-to-read-a-nutrition-label.html']){await page.goto('http://127.0.0.1:4174/'+route);await page.screenshot({path:out+'/'+theme+'-'+width+'-'+route+'.png',fullPage:true});}await page.close();
}await browser.close();console.log('16 baseline screenshots: current committed presentation, original finder runtime; external requests blocked.');})();
