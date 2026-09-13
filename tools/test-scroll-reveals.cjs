const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});try{for(const theme of ['light','dark'])for(const width of [390,1440]){
process.env.GM_TEST_THEME=theme;const p=await browser.newPage({viewport:{width,height:844},hasTouch:width===390,reducedMotion:'no-preference'});await localAssets(p);
if(engine===chromium){const cdp=await p.context().newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});}
await p.addInitScript(()=>{window.textAnimations=[];const original=Element.prototype.animate;Element.prototype.animate=function(frames,options){if(this.matches('h1,h2,h3,p,.studio-reveal,.u-reveal'))textAnimations.push(this.tagName);return original.call(this,frames,options)}});
for(const file of ['index.html','protein.html','restaurant-meal-finder.html','calculators.html','articles.html','blog.html','about.html']){
await p.goto('http://127.0.0.1:4174/'+file);await p.waitForTimeout(180);
const result=await p.evaluate(async()=>{const headings=[...document.querySelectorAll('main h1,main h2')].filter(e=>e.getClientRects().length);const positions=headings.map(e=>e.getBoundingClientRect().top+scrollY);const header=document.querySelector('.site-header');const headerBox=header.getBoundingClientRect();let drift=0,headerDrift=0,hidden=0,scrollError=0,moving=0;
const max=document.documentElement.scrollHeight-innerHeight;let heightDrift=0;
for(const fraction of [0,.1,.25,.4,.7,1,.7,.25,0]){scrollTo({top:max*fraction,behavior:'instant'});await new Promise(requestAnimationFrame);scrollError=Math.max(scrollError,Math.abs(scrollY-Math.min(max,max*fraction)));headings.forEach((e,i)=>{drift=Math.max(drift,Math.abs(e.getBoundingClientRect().top+scrollY-positions[i]));if(Number(getComputedStyle(e).opacity)<.7)hidden++});const box=header.getBoundingClientRect();headerDrift=Math.max(headerDrift,Math.abs(box.height-headerBox.height),Math.abs(box.top-headerBox.top));moving=Math.max(moving,document.getAnimations().filter(a=>a.playState==='running'&&!('transitionProperty' in a)).length);heightDrift=Math.max(heightDrift,Math.abs(document.documentElement.scrollHeight-innerHeight-max))}
return{drift,headerDrift,hidden,scrollError,moving,heightDrift,events:textAnimations,overflow:document.documentElement.scrollWidth>innerWidth+1};});
assert.ok(result.drift<=6.1&&result.headerDrift<1,JSON.stringify({file,...result}));assert.equal(result.hidden,0);assert.ok(result.scrollError<2,JSON.stringify(result));assert.equal(result.heightDrift,0,JSON.stringify({file,...result}));assert.ok(result.moving<=4,JSON.stringify({file,...result}));await p.waitForTimeout(260);assert.equal(await p.evaluate(()=>document.getAnimations().filter(a=>a.playState==='running').length),0,'Entrances must finish, without background loops');assert.equal(result.overflow,false);
}
await p.emulateMedia({reducedMotion:'reduce'});await p.reload();assert.deepEqual(await p.evaluate(()=>textAnimations),[]);
console.log('PASS',engine.name(),theme,width,'seven pages: short reveals, stable layout and header, exact native scroll positions');await p.close();
}}finally{await browser.close()}}})().catch(e=>{console.error(e);process.exitCode=1});
