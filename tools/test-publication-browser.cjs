const fs=require('node:fs');
const assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 const browser=await chromium.launch({channel:'msedge'}),failures=[],results=[];
 const representatives=['index.html','restaurant-meal-finder.html','calculators.html','nutrition-label-comparison-tool.html','chipotle-healthy-meals-macros.html','articles.html','blog.html','contact.html','how-to-read-a-nutrition-label.html','budget-meal-builder.html','protein-value-calculator.html','recipe-macro-scaler.html','search.html'];
 const files=process.argv.includes('--all')?fs.readdirSync('.').filter(f=>f.endsWith('.html')):representatives;
 for(const theme of ['light','dark'])for(const width of [390,1280]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  process.env.GM_TEST_THEME=theme;await localAssets(page);
  for(const file of files){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   await page.goto('http://127.0.0.1:4174/'+file);await page.waitForTimeout(70);
   const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,styles:[...document.styleSheets].map(s=>s.href),h1:document.querySelector('h1')?.innerText,overflow:[...document.querySelectorAll('main *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+2&&!e.closest('.table-wrap,.table-scroll,.comparison-output')}).slice(0,6).map(e=>e.tagName+'.'+e.className)}));
   if(layout.scroll>width+1||errors.length||layout.styles.length!==1)failures.push({file,theme,width,...layout,errors});
   results.push({file,theme,width,bytes:fs.statSync(file).size});
   if(representatives.includes(file))await page.screenshot({path:`design/publication-${file}-${theme}-${width}.png`,fullPage:true});
   page.off('pageerror',listener);
  }await page.close();
 }
 await browser.close();fs.writeFileSync('design/publication-browser-results.json',JSON.stringify({checks:results.length,failures},null,2));console.log(JSON.stringify({checks:results.length,failures},null,2));assert.equal(failures.length,0);
})().catch(e=>{console.error(e);process.exitCode=1});
