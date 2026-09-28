const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 const phase=process.argv[2]||'baseline',dir='docs/redesign/reset/'+phase;fs.mkdirSync(dir,{recursive:true});
 const browser=await chromium.launch({channel:'msedge'}),measurements=[];
 for(const theme of ['light','dark'])for(const width of [390,1440]){
 process.env.GM_TEST_THEME=theme;
 const page=await browser.newPage({viewport:{width,height:960}});await localAssets(page);
 for(const route of ['restaurant-meal-finder.html?goal=protein','index.html','calculators.html','chipotle-healthy-meals-macros.html','how-much-protein-can-your-body-absorb.html','search.html']){
 await page.goto('http://127.0.0.1:4174/'+route);await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:dir+'/'+route.split('?')[0]+'-'+theme+'-'+width+'.png',fullPage:true});
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:dir+'/'+route.split('?')[0]+'-'+theme+'-'+width+'-viewport.png'});
 measurements.push({route,theme,width,...await page.evaluate(()=>({domReady:performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd,bytes:performance.getEntriesByType('resource').reduce((n,r)=>n+r.decodedBodySize,0),elements:document.querySelectorAll('*').length,overflow:document.documentElement.scrollWidth>innerWidth+1}))});
 }await page.close();}
 await browser.close();fs.writeFileSync(dir+'/lab.json',JSON.stringify(measurements,null,2));console.log('Captured',measurements.length,'views in',dir);
})().catch(e=>{console.error(e);process.exitCode=1});
