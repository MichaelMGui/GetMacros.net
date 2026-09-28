const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{
 const phase=process.argv[2]||'before',dir='docs/redesign/refinement/'+phase;fs.mkdirSync(dir,{recursive:true});
 const b=await chromium.launch({channel:'msedge'});
 for(const theme of ['light','dark'])for(const width of [390,1440]){
  process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:960}});await localAssets(p);
  const files=process.env.GM_SECONDARY?['articles.html','protein-value-calculator.html','recipe-macro-scaler.html','sodium-label-comparison-tool.html','budget-meal-builder.html','sources.html','about.html','privacy.html','404.html','healthy-fast-food.html']:['index.html','restaurant-meal-finder.html','calculators.html','nutrition-label-comparison-tool.html','restaurant-meal-guides.html','chipotle-healthy-meals-macros.html','blog.html','how-much-protein-per-day.html','contact.html','search.html'];
  for(const file of files){
   await p.goto('http://127.0.0.1:4187/'+file);await p.evaluate(async()=>{await document.fonts.ready;for(const image of document.images){image.loading='eager';try{await image.decode()}catch{}}});
   await p.screenshot({path:`${dir}/${file}-${theme}-${width}.png`,fullPage:true});
  }await p.close();
 }await b.close();console.log('40 screenshots:',dir);
})().catch(e=>{console.error(e);process.exitCode=1});
