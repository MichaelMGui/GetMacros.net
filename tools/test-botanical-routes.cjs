const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 fs.mkdirSync('docs/redesign/screenshots',{recursive:true});
 const browser=await chromium.launch({channel:'msedge'}),results=[],failures=[];
 const files=['',...fs.readdirSync('.').filter(x=>x.endsWith('.html'))];
 for(const theme of ['light','dark'])for(const width of [320,390,768,1024,1440]){
  process.env.GM_TEST_THEME=theme;
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(page);
  for(const file of files){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   await page.goto('http://127.0.0.1:4174/'+file);await page.evaluate(()=>document.fonts.ready);
   const check=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,clippedHeaders:[...document.querySelectorAll("main header")].filter(e=>e.scrollHeight>e.clientHeight+2).map(e=>e.className),h1:document.querySelectorAll('main h1').length,design:document.body.dataset.design,styles:[...document.styleSheets].map(x=>x.href),brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),unlabelled:[...document.querySelectorAll('main input:not([type=hidden]), main select,main textarea')].filter(e=>!e.labels?.length&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')).map(e=>e.id)}));
   const row={file,theme,width,...check,errors};results.push(row);
   if(check.clippedHeaders.length||check.overflow||check.h1!==1||check.design!=='botanical'||check.styles.length!==1||check.brokenImages.length||check.unlabelled.length||errors.length)failures.push(row);
   if(width===390||width===1440)await page.screenshot({path:`docs/redesign/screenshots/${file||'root'}-${theme}-${width}.png`,fullPage:true});
   page.off('pageerror',listener);
  }
  await page.close();console.log('Rendered',theme,width,files.length,'routes');
 }
 await browser.close();fs.writeFileSync('docs/redesign/render-checks.json',JSON.stringify({checks:results.length,failures,results},null,2));console.log('Checks',results.length,'failures',failures);assert.equal(failures.length,0);
})().catch(e=>{console.error(e);process.exitCode=1});
