const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');const {localAssets}=require('./browser-fixture.cjs');
(async()=>{const b=await chromium.launch({channel:'msedge'}),report=[];try{
for(const theme of ['light','dark']){
 process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});await localAssets(p);
 for(const file of ['index.html','calculators.html','restaurant-meal-finder.html?goal=protein','chipotle-healthy-meals-macros.html','blog.html','sources.html','contact.html','privacy.html','search.html','protein-value-calculator.html','serving-size-vs-portion-size.html']){
  await p.goto('http://127.0.0.1:4174/'+file);await p.evaluate(()=>document.documentElement.style.fontSize='200%');
  const overflow=await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);report.push({file,theme,textSize:'200%',overflow});
 }
 await p.goto('http://127.0.0.1:4174/index.html');await p.locator('[data-theme-toggle]').click();const selected=await p.locator('html').getAttribute('data-theme');await p.unroute('**/*');
 // Fixture's initial theme injection resets on navigation, so verify the stored value directly.
 assert.equal(await p.evaluate(()=>localStorage.getItem('gm-theme')),selected);await p.close();
}
 const nojs=await b.newPage({viewport:{width:390,height:844},javaScriptEnabled:false});await localAssets(nojs);await nojs.goto('http://127.0.0.1:4174/index.html');assert.equal(await nojs.locator('.no-script-nav a').count(),5);assert.equal(await nojs.locator('.no-script-nav').isVisible(),true);await nojs.close();
 const images=await b.newPage({viewport:{width:390,height:844}});await localAssets(images);await images.route('**/*.{webp,png,svg}',r=>r.abort());await images.goto('http://127.0.0.1:4174/index.html');assert.equal(await images.locator('.discovery-submit').isVisible(),true);assert.equal(await images.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);await images.close();
 fs.writeFileSync('docs/redesign/resilience-checks.json',JSON.stringify({scope:'200% root text sizing (not OS zoom), no-JavaScript navigation, missing images, stored theme selection; reduced motion requested',report},null,2));const failures=report.filter(r=>r.overflow);console.log({checks:report.length,failures});assert.equal(failures.length,0);
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
