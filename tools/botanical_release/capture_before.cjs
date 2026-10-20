/* Baseline of the actual current static application, before presentation edits. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
process.env.PORT='0';const server=require('../product_release/dev-server.cjs');
const out=path.resolve('docs/botanical-release-2026-10-20');let browser;
(async()=>{if(!server.listening)await new Promise(r=>server.once('listening',r));const base='http://127.0.0.1:'+server.address().port;
 browser=await chromium.launch({channel:'msedge',args:['--no-proxy-server']});
 const errors=[],shots=[],routes=['/','/ca/en/','/restaurant-meal-finder.html','/calculators.html','/food-diary.html','/restaurant-meal-guides.html','/articles.html','/fage-plain-greek-yogurt-0-2-5-percent.html','/compare-foods.html'];
 for(const width of [390,1440]){const c=await browser.newContext({viewport:{width,height:width===390?844:1000},serviceWorkers:'block'});await c.addInitScript(()=>localStorage.setItem('gm-theme','light'));const p=await c.newPage();p.on('pageerror',e=>errors.push({url:p.url(),error:e.message}));
  async function shot(name){await p.evaluate(()=>document.fonts.ready);const file=name+'-'+width+'.png';await p.screenshot({path:path.join(out,'before',file),animations:'disabled'});shots.push(file);}
  for(const route of routes){await p.goto(base+route);if(route==='/food-diary.html')await p.locator('[data-meal-add=Breakfast]').waitFor();await shot(route==='/'?'home':route.replaceAll('/','-').replace(/^-|\.html|-$|/g,''));}
  await p.goto(base+'/');await p.locator('.home-quiz-action').click();await p.locator('input[name=meal][value=any]').check();await p.locator('[data-guide-next]').click();await shot('restaurant-quiz');await p.keyboard.press('Escape');
  await p.goto(base+'/food-diary.html');await p.locator('[data-meal-add=Breakfast]').click();await p.locator('[data-browse-food]').first().waitFor();await shot('add-food');await c.close();
 }
 const manifest=JSON.parse(fs.readFileSync('assets/generated/manifest.json'));
 fs.writeFileSync(path.join(out,'baseline.json'),JSON.stringify({date:new Date().toISOString(),revision:'abd9ebd199039eaa03f3896c8750b6115249e52e',routes,shots,errors,assetManifestSha256:crypto.createHash('sha256').update(JSON.stringify(manifest)).digest('hex')},null,2));console.log(JSON.stringify({screenshots:shots.length,errors}));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>{await browser?.close();server.close()});
