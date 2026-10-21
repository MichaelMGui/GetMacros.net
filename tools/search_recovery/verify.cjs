/* Render evidence for the changed search landing pages; visits are synthetic. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out=path.resolve('docs/search-recovery-2026-10-21');
const routes=['/healthy-fast-food.html','/gb/en/collections/protein-meals/','/ca/en/find-a-meal/','/'];
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const local='http://127.0.0.1:'+server.address().port,browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});
const report={checkedAt:new Date().toISOString(),layouts:[],errors:[]};try{
 for(const phase of process.env.BASE_URL?['production']:['before','after'])for(const width of [390,1440]){
 const c=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block',reducedMotion:'reduce'});await c.addInitScript(()=>localStorage.setItem('gm-theme','light'));const p=await c.newPage();
 p.on('pageerror',e=>report.errors.push(e.message));
 for(const [i,route] of routes.entries()){
  const response=await p.goto((process.env.BASE_URL|| (phase==='before'?'https://getmacros.net':local))+route);assert.equal(response.status(),200);await p.evaluate(()=>document.fonts.ready);
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),route+' overflow');
  if(phase!=='before'){
   if(route.includes('protein-meals')){assert.equal(await p.locator('tbody tr').count(),12);assert(!await p.locator('main').innerText().then(x=>x.includes('Pizza Box 6 Pack')));assert.equal(await p.locator('tbody a').filter({hasText:'Official nutrition source'}).count(),12);}
   if(route.includes('find-a-meal')){assert.equal(await p.locator('#local-menu-heading').count(),1);assert(await p.locator('[data-meal-details]').count()>0);}
   if(route==='/')assert.equal(await p.locator('a[href="/healthy-fast-food.html"]').count()>0,true);
  }
  const directory=path.join(out,phase);fs.mkdirSync(directory,{recursive:true});await p.screenshot({path:path.join(directory,['us-guide','uk-portions','canada-finder','home'][i]+'-'+width+'.png'),fullPage:route.includes('protein-meals'),animations:'disabled'});
  report.layouts.push({phase,width,route,status:response.status(),overflow:false});
 }
 await c.close();}
 // Market isolation and ordinary live filter behavior are still controlled by
 // the existing engine; SEO context does not replace or relax it.
 const c=await browser.newContext({viewport:{width:390,height:844},serviceWorkers:'block'}),p=await c.newPage();
 await p.goto((process.env.BASE_URL||local)+'/ca/en/find-a-meal/?maxCal=500&minProtein=25');await p.locator('[data-meal-details]').first().waitFor();
 const rows=await p.evaluate(()=>window.GM_MEALS);assert(rows.every(r=>r.market==='CA'));
 const ids=await p.locator('[data-meal-details]').evaluateAll(buttons=>buttons.map(b=>Number(b.dataset.mealDetails)));assert(ids.length);assert(ids.every(i=>rows[i].cal<=500&&rows[i].p>=25));await c.close();
 assert.deepEqual(report.errors,[]);
 }catch(e){report.errors.push(e.stack);process.exitCode=1;}finally{fs.writeFileSync(path.join(out,process.env.BASE_URL?'production-browser.json':'browser.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({layouts:report.layouts.length,errors:report.errors}));await browser.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
