const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){
 const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark'])for(const width of [320,390,1440]){
  process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(p);
  await p.goto('http://127.0.0.1:4174/search.html');
  const pairs=await p.evaluate(()=>{
   const s=getComputedStyle(document.body),get=k=>s.getPropertyValue('--'+k).trim();
   const lum=hex=>{let value=hex.replace('#','');if(value.length===3)value=[...value].map(c=>c+c).join('');return value.match(/.{2}/g).map(n=>parseInt(n,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0)};
   return [...['leaf','blue','orange','berry'].map(k=>[k+'-fill',k+'-ink']),['button-fill','button-ink'],['quiet-surface','quiet-muted'],['quiet-paper','quiet-ink']].map(([a,b])=>{const l1=lum(get(a)),l2=lum(get(b));return{pair:a+'/'+b,ratio:(Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05)}});
  });
  for(const pair of pairs)assert.ok(pair.ratio>=4.5,`${theme} ${pair.pair}: ${pair.ratio}`);
  for(const svg of await p.locator('.colour-tile-art svg').all()){
   const box=await svg.boundingBox();assert.ok(box.width>=120&&box.height>=80,'Illustration fills its panel');
  }
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  await p.goto('http://127.0.0.1:4174/about.html');
  assert.equal(await p.locator('.clear-about-grid .colour-art').count(),3);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  await p.goto('http://127.0.0.1:4174/restaurant-meal-finder.html');
  const option=p.locator('.quiz-option').filter({has:p.locator('input[value="protein"]')});
  assert.equal(await option.locator('.option-check').evaluate(e=>getComputedStyle(e).color),'rgba(0, 0, 0, 0)','Unchecked options must not look selected');
  await option.click();assert.equal(await option.locator('input').isChecked(),true);
  assert.notEqual(await option.locator('.option-check').evaluate(e=>getComputedStyle(e).color),'rgba(0, 0, 0, 0)','Checked option needs visible confirmation');
  console.log('PASS',engine.name(),theme,width,'seven contrast pairs, illustration size and layout');await p.close();
 }}finally{await b.close()}
}})().catch(e=>{console.error(e);process.exitCode=1});
