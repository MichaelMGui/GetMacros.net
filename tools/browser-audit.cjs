// Render all public pages in both themes on desktop and mobile. Run against
// the local preview; block third-party ads so the audit is reproducible.
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '..');
(async () => {
 const browser = await chromium.launch({channel:'msedge',headless:true});
 const findings=[];
 const pages=fs.readdirSync(root).filter(f=>f.endsWith('.html'));
 const examples=['index.html','calculators.html','restaurant-meal-finder.html','recipe-macro-scaler.html','articles.html','chipotle-healthy-meals-macros.html'];
 for (const width of [390,1440]) {
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
  await context.route('https://**/*',r=>r.abort());
  const page=await context.newPage();
  let errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const file of pages) {
   console.log(width,file);
   errors=[];
   await page.goto('http://127.0.0.1:4173/'+file,{waitUntil:'domcontentloaded'});
   console.log('loaded');
   for(const theme of ['light','dark']) {
    await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
    const issues=await page.evaluate(()=>{
     const w=document.documentElement.clientWidth;
     return {overflow:document.documentElement.scrollWidth>w+2,
      elements:[...document.querySelectorAll('main *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.right>w+3||r.left < -3)&&getComputedStyle(e).position!=='absolute'&&!e.closest('.table-scroll,.table-wrap,svg,[hidden]')}).slice(0,8).map(e=>e.tagName+'.'+e.className),
      h1:document.querySelectorAll('h1').length};
    });
    if(issues.overflow||errors.length||issues.h1!==1)findings.push({file,width,theme,...issues,errors:[...errors]});
    if(examples.includes(file))await page.screenshot({path:path.join(root,`design/${file.replace('.html','')}-${width}-${theme}.png`),fullPage:false});
   }
  }
  await context.close();
  console.log(`Audited ${pages.length} pages at ${width}px in both themes`);
 }
 fs.writeFileSync(path.join(root,'design/browser-audit.json'),JSON.stringify(findings,null,2));
 console.log(JSON.stringify(findings,null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
