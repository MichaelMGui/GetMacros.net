const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('../browser-fixture.cjs');
const samples=[
 ['macro','equal-calories-different-macros-menu.html'],
 ['labels','sugar-lines-do-not-add.html'],
 ['protein','protein-serving-count-day-not-prescription.html'],
 ['fiber','qdoba-vegan-bowl-fiber-tradeoff.html'],
 ['ordering','cross-chain-melt-sandwich-orders.html'],
 ['breakfast','arbys-breakfast-bread-format.html'],
 ['lunch','noodles-mac-protein-not-simple-add-on.html'],
 ['restaurant','culvers-dinner-name-side-footnote.html'],
 ['cross-restaurant','three-count-tacos-not-three-equal-meals.html'],
 ['calculator','calculator-height-feet-inches-not-decimal.html'],
 ['recipe','recipe-combined-batches-not-average-serving.html'],
 ['budget','protein-value-price-range-overlap.html'],
 ['dataset','menu-average-chain-weighting.html']
];
(async()=>{
 const dir='docs/playful-release-2026-10-04/editorial/screenshots';fs.mkdirSync(dir,{recursive:true});
 const browser=await chromium.launch({channel:'msedge'}),results=[],failures=[];
 try{
 for(const theme of ['light','dark'])for(const width of [390,1440]){
  process.env.GM_TEST_THEME=theme;
  const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce'});await localAssets(page);
  for(const [track,route] of samples){
   const errors=[];const errorListener=e=>errors.push(e.message);page.on('pageerror',errorListener);
   await page.goto('https://127.0.0.1:4187/'+route);await page.evaluate(()=>document.fonts.ready);
   const state=await page.evaluate(()=>({
    scrollWidth:document.documentElement.scrollWidth,width:innerWidth,theme:document.documentElement.dataset.theme,
    h1:document.querySelectorAll('h1').length,main:document.querySelectorAll('main').length,
    missingImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),
    tableRegions:[...document.querySelectorAll('.table-wrap')].map(e=>({labeled:!!e.getAttribute('aria-label'),focusable:e.tabIndex===0,scrolls:e.scrollWidth>e.clientWidth,columns:e.querySelectorAll('thead th').length,tableWidth:e.querySelector('table')?.getBoundingClientRect().width,regionWidth:e.clientWidth})),
    articleParagraphs:document.querySelectorAll('article p').length,
    overflow:[...document.querySelectorAll('main *')].filter(e=>{let r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+2&&!e.closest('.table-wrap,.table-scroll')}).slice(0,8).map(e=>e.tagName+'.'+e.className)
   }));
   const record={track,route,theme,width,...state,errors};results.push(record);
   if(state.scrollWidth>width+1||state.h1!==1||state.main!==1||errors.length||state.missingImages.length||state.tableRegions.some(r=>!r.labeled||!r.focusable||(r.columns<=2&&r.scrolls)||(r.columns>=4&&width===390&&r.tableWidth<700)))failures.push(record);
   await page.screenshot({path:`${dir}/${track}-${theme}-${width}-top.png`});
   if(await page.locator('main .table-wrap').count()){
    await page.locator('main .table-wrap').first().scrollIntoViewIfNeeded();
    await page.screenshot({path:`${dir}/${track}-${theme}-${width}-table.png`});
    await page.locator('main .table-wrap').first().focus();
    await page.keyboard.press('ArrowRight');
   }
   await page.locator('main .resource-sources').scrollIntoViewIfNeeded();
   await page.screenshot({path:`${dir}/${track}-${theme}-${width}-sources.png`});
   page.off('pageerror',errorListener);
  }
  await page.close();
 }
 }finally{await browser.close();}
 fs.writeFileSync('docs/playful-release-2026-10-04/editorial/browser-review.json',JSON.stringify({checks:results.length,results,failures,method:'Playwright Edge using repository asset interception, not a live server or field measurement.',visualReview:'Screenshots captured; manual image review recorded separately.'},null,2));
 console.log(JSON.stringify({checks:results.length,failures},null,2));
 if(failures.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
