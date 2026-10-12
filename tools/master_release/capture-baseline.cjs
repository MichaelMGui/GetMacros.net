const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const output='docs/master-release-2026-10-12/baseline';fs.mkdirSync(output,{recursive:true});
(async()=>{const browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});const checks=[];try{
 for(const theme of ['light','dark'])for(const width of [390,1440]){
  const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const page=await context.newPage();
  for(const route of ['/','/ca/en/','/mx/en/','/gb/en/','/world-restaurant-menus.html','/restaurant-meal-guides.html','/food-diary.html','/food-library.html','/calculators.html','/play.html']){
   const errors=[];page.removeAllListeners('pageerror');page.on('pageerror',e=>errors.push(e.message));const response=await page.goto('https://getmacros.net'+route);await page.evaluate(()=>document.fonts.ready);const name=route==='/'?'us-home':route.replace(/\W+/g,'-');await page.screenshot({path:path.join(output,name+'-'+theme+'-'+width+'.png'),fullPage:true});checks.push({route,theme,width,status:response.status(),errors,overflow:await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)});
  }await context.close();console.log('Baseline',theme,width);
 }fs.writeFileSync(output+'/checks.json',JSON.stringify({source:'Actual production, before this release; no interception',checks},null,2));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
