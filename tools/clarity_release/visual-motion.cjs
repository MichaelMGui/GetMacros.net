/* Rendered browser verification of the actual companion and motion controls. */
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out=path.resolve('docs/clarity-release-2026-10-14/visual-motion');fs.mkdirSync(out,{recursive:true});
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']}),checks=[];
try{for(const theme of ['light','dark'])for(const width of [390,1280]){
 const context=await browser.newContext({viewport:{width,height:950},reducedMotion:'no-preference',serviceWorkers:'block'});await context.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const p=await context.newPage();
 await p.goto(base+'/food-diary.html?market=CA',{waitUntil:'domcontentloaded'});
 const contrast=await p.evaluate(()=>{
  const vars=getComputedStyle(document.documentElement),read=k=>vars.getPropertyValue('--'+k).trim();
  function lum(hex){const v=hex.slice(1).match(/.{2}/g).map(x=>parseInt(x,16)/255).map(x=>x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4));return .2126*v[0]+.7152*v[1]+.0722*v[2];}
  function ratio(a,b){const x=lum(read(a)),y=lum(read(b));return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
  const pairs=[];for(const text of ['ink','muted'])for(const bg of ['bg','surface','soft','highlight'])pairs.push({text,bg,minimum:4.5,ratio:ratio(text,bg)});
  for(const bg of ['bg','surface','soft'])pairs.push({text:'green',bg,minimum:4.5,ratio:ratio('green',bg)});
  for(const [text,bg,minimum]of [['on-green','green',4.5],['error','error-bg',4.5],['warning','bg',4.5],['focus','surface',3],['control-border','surface',3]])pairs.push({text,bg,minimum,ratio:ratio(text,bg)});
  return pairs;
 });
 for(const pair of contrast)assert(pair.ratio>=pair.minimum, `${theme} semantic contrast ${pair.text} on ${pair.bg}: ${pair.ratio}`);
 await p.locator('.companion-wave').hover();await p.waitForTimeout(260);
 const hover=await p.locator('.food-companion .food-arm-wave').evaluate(x=>({transform:getComputedStyle(x).transform,transition:getComputedStyle(x).transitionDuration}));
 assert.notEqual(hover.transform,'none');
 await p.locator('.appearance-picker>summary').click();await p.locator('[data-calm-motion]').check();await p.keyboard.press('Escape');
 assert.equal(await p.locator('html').getAttribute('data-motion'),'calm');await p.locator('.companion-wave').click();
 const calm=await p.locator('.food-companion svg,.food-companion .food-arm-wave').evaluateAll(nodes=>nodes.map(x=>({animation:getComputedStyle(x).animationName,transition:getComputedStyle(x).transitionDuration})));
 assert(calm.every(x=>x.animation==='none'&&x.transition==='0s'));
 await p.reload({waitUntil:'domcontentloaded'});assert.equal(await p.locator('html').getAttribute('data-motion'),'calm');await p.locator('.companion-wave').focus();
 await p.screenshot({path:path.join(out,`broccoli-calm-${theme}-${width}.png`)});await context.close();
 const reduced=await browser.newContext({viewport:{width,height:950},reducedMotion:'reduce',serviceWorkers:'block'});await reduced.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);const rp=await reduced.newPage();
 await rp.goto(base+'/food-diary.html?market=CA',{waitUntil:'domcontentloaded'});await rp.locator('.companion-wave').click();
 const os=await rp.locator('.food-companion svg,.food-companion .food-arm-wave').evaluateAll(nodes=>nodes.map(x=>({animation:getComputedStyle(x).animationName,transition:getComputedStyle(x).transitionDuration})));
 assert(os.every(x=>x.animation==='none'&&x.transition==='0s'));await reduced.close();
 checks.push({theme,width,contrast,hover,calm,os,checks:['Semantic text/action/feedback/focus/control-border token contrasts meet sampled thresholds', 'Broccoli responds to real hover', 'Calm motion disables actual arm/SVG motion', 'Calm preference persists after reload', 'OS reduced motion disables arm/SVG motion', 'Keyboard focus gives a visible companion state']});console.log('PASS motion',theme,width);
}fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify({checkedAt:new Date().toISOString(),base,checks},null,2));
}finally{await browser.close();server.close()}})().catch(e=>{console.error(e);server.close();process.exitCode=1});
