/* Real candidate HTML render checks. No fake source responses or generated foods. */
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const manifest=JSON.parse(fs.readFileSync('docs/clarity-release-2026-10-14/editorial-manifest.json','utf8'));
const out=path.resolve('docs/clarity-release-2026-10-14/editorial-screenshots');fs.mkdirSync(out,{recursive:true});
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const capture=new Set(['/tim-hortons-canada-protein-latte-vs-latte.html','/guzman-y-gomez-australia-chicken-bowl-vs-burrito.html','/kirkland-canada-macadamia-vs-mixed-nuts.html','/international-menu-data-coverage-explained.html','/how-to-calculate-recipe-nutrition.html']);
(async()=>{
 if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port;
 const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});const checks=[];
 try{
  for(const theme of ['light','dark']){
   const context=await browser.newContext({serviceWorkers:'block',reducedMotion:'reduce'});await context.addInitScript(t=>{localStorage.setItem('gm-theme',t)},theme);
   const page=await context.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));
   for(const width of [320,390,768,1280,1440]){
    await page.setViewportSize({width,height:960});
    for(const row of [...manifest.routes,...manifest.improvements]){
     errors=[];const response=await page.goto(base+row.route,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
     const detail=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,theme:document.documentElement.dataset.theme,firstAnswer:document.querySelector('article.release-article>p:not(.submission-byline)')?.textContent,tableScroll:[...document.querySelectorAll('main .table-wrap')].every(n=>n.clientWidth<=innerWidth+1)}));
     assert.equal(response.status(),200,row.route);assert.equal(detail.overflow,false,row.route+' '+width);assert.equal(detail.h1,1,row.route);assert.equal(detail.theme,theme);assert.equal(detail.tableScroll,true,row.route);assert.deepEqual(errors,[],row.route+' runtime errors');
     if(capture.has(row.route)&&[390,1280].includes(width))await page.screenshot({path:path.join(out,row.route.slice(1).replace('.html','')+'-'+theme+'-'+width+'.png'),fullPage:true});
     checks.push({route:row.route,theme,width,status:response.status(),...detail,runtimeErrors:errors,inspection:'automated browser render; not a manual visual claim'});
    }
   }
   await context.close();
  }
 }finally{await browser.close();await new Promise(r=>server.close(r));}
 fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({checkedAt:new Date().toISOString(),checks,manuallyInspected:[]},null,2));console.log(checks.length+' actual article render states passed; screenshots '+out);
})().catch(e=>{console.error(e);server.close();process.exit(1)});
