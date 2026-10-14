/* Automated renders of every public route, explicitly distinct from manual inspection. */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs'),out='docs/clarity-release-2026-10-14';
const routes=fs.readdirSync('.').filter(n=>n.endsWith('.html')).map(n=>n==='index.html'?'/':'/'+n);
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())walk(p);else if(e.name==='index.html')routes.push('/'+p.replaceAll(path.sep,'/').replace(/index.html$/,''));}}
for(const market of ['ca','mx','gb','ie','au','nz','jp'])walk(market+'/en');
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port,browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']}),checks=[];try{
 for(const theme of ['light','dark']){
  const context=await browser.newContext({viewport:{width:390,height:950},reducedMotion:'reduce'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const page=await context.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [390,1280]){await page.setViewportSize({width,height:950});let i=0;for(const route of routes.sort()){
   errors=[];const response=await page.goto(base+route,{waitUntil:'domcontentloaded'});await page.evaluate(()=>document.fonts.ready);const details=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel=canonical]')?.href,theme:document.documentElement.dataset.theme,sharedCSS:getComputedStyle(document.documentElement).getPropertyValue('--ink').trim(),immutableStyles:[...document.querySelectorAll('link[rel=stylesheet][data-source-path]')].every(n=>!!n.sheet)}));checks.push({route,width,requestedTheme:theme,status:response.status(),errors:[...errors],...details});if(++i%70===0)console.log('Rendered',theme,width,i,'/',routes.length);
  }}await context.close();
 }
 const failures=checks.filter(r=>r.status!==200||r.h1!==1||r.overflow||r.errors.length||r.theme!==r.requestedTheme||!r.sharedCSS||!r.immutableStyles);fs.writeFileSync(out+'/route-renders.json',JSON.stringify({verifiedAt:new Date().toISOString(),routes:routes.length,renders:checks,failures,inspection:'Automated rendered checks of every route; not manual visual review'},null,2));console.log(checks.length,'renders;',failures.length,'failures');if(failures.length){console.log(JSON.stringify(failures));process.exitCode=1;}
}finally{await browser.close();server.close()}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
