const assert=require('node:assert/strict');
const{chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const{localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){
 const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark'])for(const width of [320,390,768,1440]){
  process.env.GM_TEST_THEME=theme;const p=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});await localAssets(p);
  await p.goto('http://127.0.0.1:4174/index.html');
  for(const font of ['16px','20px']){
   await p.evaluate(size=>document.documentElement.style.fontSize=size,font);
   const boxes=await p.locator('.home-everyday-tool').evaluateAll(cards=>cards.map(card=>{
    const i=card.querySelector('.home-everyday-icon').getBoundingClientRect(),copy=card.querySelector(':scope>div').getBoundingClientRect(),c=card.getBoundingClientRect();
    return{gap:copy.left-i.right,within:copy.right<=c.right-10,iconInside:i.left>=c.left&&i.right<=c.right,title:card.querySelector('h3').textContent};
   }));
   assert.equal(boxes.length,3);
   for(const x of boxes){assert.ok(x.gap>=15,`${engine.name()} ${theme} ${width} ${font} ${x.title}: overlapping icon`);assert.ok(x.within&&x.iconInside)}
   assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  }
  await p.evaluate(()=>document.documentElement.style.fontSize='16px');
  await p.locator('.home-everyday-tool').first().evaluate(e=>scrollTo({top:scrollY+e.getBoundingClientRect().top-110,behavior:'instant'}));
  await p.screenshot({path:`design/palm-home-${engine.name()}-${theme}-${width}.png`});
  await p.goto('http://127.0.0.1:4174/calculators.html');
  const fills=await p.locator('.calc-welcome-macros .clear-icon').evaluateAll(es=>es.map(e=>getComputedStyle(e).backgroundColor));
  assert.deepEqual(fills,['rgba(0, 0, 0, 0)','rgba(0, 0, 0, 0)','rgba(0, 0, 0, 0)']);
  const colours=await p.locator('.calc-welcome-macros .clear-icon svg').evaluateAll(es=>es.map(e=>getComputedStyle(e).color));
  assert.equal(new Set(colours).size,3,'Macro symbols have distinct accent colours without coloured boxes');
  await p.screenshot({path:`design/palm-calculator-${engine.name()}-${theme}-${width}.png`});
  console.log('PASS',engine.name(),theme,width,'icon separation, larger text and coordinated calculator header');await p.close();
 }}finally{await browser.close()}
}})().catch(e=>{console.error(e);process.exitCode=1});
