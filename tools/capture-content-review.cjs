const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
const dir='docs/adsense-2026-09-28/screenshots';fs.mkdirSync(dir,{recursive:true});
const browser=await chromium.launch({channel:'msedge'});
try{for(const theme of ['light','dark'])for(const width of [390,1440]){
process.env.GM_TEST_THEME=theme;const page=await browser.newPage({viewport:{width,height:960}});await localAssets(page);
for(const name of ['chipotle-healthy-meals-macros.html','panera-healthy-meals-macros.html','taco-bell-healthy-meals-macros.html','body-recomposition-explained.html','sources.html']){
await page.goto('http://127.0.0.1:4187/'+name);await page.evaluate(()=>document.fonts.ready);
if(await page.locator('#ordering-comparison').count())await page.locator('#ordering-comparison').scrollIntoViewIfNeeded();
else await page.locator('main article, main .article-container').first().scrollIntoViewIfNeeded().catch(()=>{});
await page.screenshot({path:`${dir}/${name}-${theme}-${width}.png`});
}await page.close();}
}finally{await browser.close();}
console.log('20 content-review screenshots saved.');
})().catch(e=>{console.error(e);process.exitCode=1;});
