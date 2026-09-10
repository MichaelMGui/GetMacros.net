const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
const pages=['index.html','calculators.html','healthy-fast-food.html','chipotle-healthy-meals-macros.html','restaurant-meal-finder.html','budget-meal-builder.html','are-diet-drinks-bad-for-you.html','carbohydrate-label-portion-tool.html','recipe-macro-scaler.html','high-protein-foods-list.html','contact.html'];
(async()=>{for(const engine of [chromium,webkit]){const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});try{
 for(const theme of ['light','dark'])for(const width of [320,390,1440]){process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});await localAssets(p);
  for(const file of pages){await p.goto('http://127.0.0.1:4174/'+file);await p.locator('details').evaluateAll(es=>es.forEach(e=>e.open=true));
   const faults=await p.locator('main details>summary,footer details>summary').evaluateAll(es=>es.flatMap(e=>{
    const r=e.getBoundingClientRect(),s=getComputedStyle(e),a=getComputedStyle(e,'::after'),d=e.parentElement.getBoundingClientRect();
    return r.width<1||r.right>d.right+1||e.scrollWidth>e.clientWidth+1||a.width!=='34px'||a.display==='none'||parseFloat(s.paddingRight)<48?[{text:e.textContent.trim(),width:r.width,scroll:e.scrollWidth,chevron:a.width,padding:s.paddingRight}]:[];
   }));assert.deepEqual(faults,[],`${engine.name()} ${theme} ${width} ${file}: summary layout`);
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,`${file}: page overflow`);
   if(file==='calculators.html'){
    const d=p.locator('.clarity-more'),s=d.locator(':scope>summary');await s.focus();await p.keyboard.press('Enter');assert.equal(await d.evaluate(e=>e.open),false);await p.keyboard.press('Space');assert.equal(await d.evaluate(e=>e.open),true);
    const cards=d.locator('.clear-tool-card');assert.equal(await cards.count(),4);
    assert.equal(new Set(await cards.locator('svg').evaluateAll(es=>es.map(e=>e.innerHTML))).size,4,'Each additional tool has its own illustration');
    await d.screenshot({path:`design/disclosures-${engine.name()}-${theme}-${width}.png`});
   }
  }console.log('PASS',engine.name(),theme,width,'all disclosure families, expanded layouts and keyboard toggling');await p.close();
 }
}finally{await b.close()}}})().catch(e=>{console.error(e);process.exitCode=1});
