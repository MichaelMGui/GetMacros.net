const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){
 const browser=await engine.launch(engine===chromium?{channel:'msedge'}:{});
 try{for(const theme of ['light','dark'])for(const width of [390,1440]){
  process.env.GM_TEST_THEME=theme;
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await localAssets(page);
  await page.goto('http://127.0.0.1:4174/index.html');
  if(width<900)await page.locator('.nav-toggle').click();
  const triggers=page.locator('.nav-group-trigger');
  for(let i=0;i<await triggers.count();i++){
   await triggers.nth(i).click();
   await page.waitForFunction(()=>[...document.querySelectorAll('.nav-group.is-open .nav-popover')].every(e=>getComputedStyle(e).opacity==='1'));
   const issues=await page.locator('#primary-navigation').evaluate(root=>{
    const rgb=s=>(s.match(/[\d.]+/g)||[]).map(Number);
    const lum=c=>c.slice(0,3).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
    const issues=[];
    for(const e of root.querySelectorAll('a,button,strong,small')){
     if(!e.getClientRects().length||![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;
     let visible=true,bg=[255,255,255],parents=[];
     for(let p=e;p;p=p.parentElement)parents.push(p);
     for(const p of parents.reverse()){
      const s=getComputedStyle(p);if(s.visibility==='hidden'||+s.opacity===0)visible=false;
      const c=rgb(s.backgroundColor),a=c[3]??1;if(c.length>=3)bg=c.slice(0,3).map((v,i)=>v*a+bg[i]*(1-a));
     }
     if(!visible)continue;
     const s=getComputedStyle(e),fg=rgb(s.webkitTextFillColor||s.color);
     const ratio=(Math.max(lum(fg),lum(bg))+.05)/(Math.min(lum(fg),lum(bg))+.05);
     if(ratio<4.5)issues.push({text:e.textContent.trim(),ratio});
    }return issues;
   });
   assert.deepEqual(issues,[],`${engine.name()} ${theme} ${width} menu ${i}`);
  }
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
  await page.screenshot({path:`design/navigation-${engine.name()}-${theme}-${width}.png`});
  console.log('PASS',engine.name(),theme,width,'navigation contrast');await page.close();
 }}finally{await browser.close();}
}})().catch(e=>{console.error(e);process.exitCode=1});
