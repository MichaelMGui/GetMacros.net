/* Fresh unauthenticated browser only; no account cookies or profiles are used. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'docs/analytics-2026-10-23');
const ID='G-MWXSWP6ZGY',key='gm-analytics-consent-v1';
const analyticsAsset=JSON.parse(fs.readFileSync(path.join(root,'assets/generated/manifest.json'),'utf8'))['js/analytics.js'].url;
const mime={'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png','.webp':'image/webp'};
const results={synthetic:true,checks:[],screenshots:[],googleTagDownloads:[],collectorResponses:[],errors:[]};
let activeBrowser;
async function main(){
 const browser=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']});
 activeBrowser=browser;
 let allowGoogle=false;
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:390,height:844}});
 // Test the consent UI in a synthetic browser while preventing automatic traffic.
 await context.addInitScript(()=>Object.defineProperty(navigator,'webdriver',{get:()=>false}));
 await context.route('**/*',async route=>{
  const u=new URL(route.request().url());
  if(u.hostname==='getmacros.net'){
   let name=decodeURIComponent(u.pathname);if(name.endsWith('/'))name+='index.html';
   const file=path.resolve(root,'.'+name);
   if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile())return route.fulfill({status:404,body:'Not found'});
   let body=fs.readFileSync(file);
   if(allowGoogle && (u.pathname==='/js/analytics.js'||u.pathname===analyticsAsset)){
    // One explicitly labeled debug/internal smoke event, never an audience claim.
    body=Buffer.from(body.toString().replace('send_page_view: false,','send_page_view: false, debug_mode: true, traffic_type: "internal",').replace("{ send_to: id }","{ send_to: id, debug_mode: true, traffic_type: 'internal' }"));
   }
   return route.fulfill({status:200,contentType:mime[path.extname(file)]||'application/octet-stream',body});
  }
  if(allowGoogle && u.hostname==='www.googletagmanager.com'){
   const response=await route.fetch();results.googleTagDownloads.push({status:response.status(),url:u.origin+u.pathname});return route.fulfill({response});
  }
  if(allowGoogle && /^(www|region1)\.google-analytics\.com$/.test(u.hostname)&&u.pathname==='/g/collect'){
   const request=route.request(),query=new URLSearchParams(u.search),post=request.postData()||'';
   assert.equal(query.get('tid'),ID);
   assert.ok(![u.href,post].join(' ').includes('PRIVATE_CANARY'));
   if (!(query.get('_dbg')==='1'||query.get('ep.debug_mode')==='true'||post.includes('_dbg=1')||post.includes('ep.debug_mode=true'))) {
    results.errors.push('Blocked non-debug request: '+JSON.stringify({event:query.get('en'),keys:[...query.keys()],debug:query.get('ep.debug_mode'),internal:query.get('ep.traffic_type')}));
    return route.abort();
   }
   const response=await route.fetch();
   // Keep only nonidentifying test evidence; never record client IDs/cookies.
   results.collectorResponses.push({status:response.status(),event:query.get('en')||'batched',measurementID:query.get('tid'),debug:true,trafficType:query.get('tt')||query.get('ep.traffic_type'),page:query.get('dl')});
   return route.fulfill({response});
  }
  return route.abort();
 });
 let googleRequests=0;
 context.on('request',r=>{if(/google-analytics\.com|googletagmanager\.com/.test(r.url()))googleRequests++;});
 const page=await context.newPage();
 page.on('pageerror',e=>results.errors.push(e.message));
 page.on('console',m=>{if(m.type()==='error'&&m.text().includes('Content Security Policy'))results.errors.push(m.text());});
 await page.goto('https://getmacros.net/',{waitUntil:'networkidle'});
 await page.getByRole('button',{name:'Allow analytics',exact:true}).first().waitFor({state:'visible'});
 assert.equal(googleRequests,0);results.checks.push('No Google request before consent.');
 for(const theme of ['light','citrus','berry','dark']){
  await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
  const colors=await page.locator('[data-analytics-notice]').evaluate(e=>({text:getComputedStyle(e).color,bg:getComputedStyle(e).backgroundColor}));
  assert.notEqual(colors.text,colors.bg);
 }
 await page.evaluate(()=>document.documentElement.dataset.theme='light');
 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:900});
  const rect=await page.locator('[data-analytics-notice]').boundingBox();assert.ok(rect.x>=0&&rect.x+rect.width<=width+1);
 }
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(out,'consent-mobile.png')});results.screenshots.push('consent-mobile.png');
 await page.getByRole('button',{name:'No thanks',exact:true}).first().click();
 assert.equal(googleRequests,0);
 await page.reload({waitUntil:'networkidle'});assert.equal(await page.locator('[data-analytics-notice]').isVisible(),false);assert.equal(googleRequests,0);
 await page.locator('[data-analytics-footer]').click();assert.equal(await page.locator('#analytics-preferences').isVisible(),true);
 await page.keyboard.press('Escape');assert.equal(await page.locator('#analytics-preferences').isVisible(),false);assert.equal(await page.locator('[data-analytics-footer]').evaluate(e=>e===document.activeElement),true);
 results.checks.push('Decline persists; preferences support keyboard dismissal and focus return; notice fits four widths and four themes.');
 // Mocked loader: consent exercises actual DOM without sending traffic.
 await page.locator('[data-analytics-footer]').click();await page.locator('#analytics-preferences [data-analytics-choice=granted]').click();
 await page.waitForTimeout(200);
 const commands=await page.evaluate(()=>window.dataLayer.map(a=>Array.from(a)));
 assert.equal(commands.filter(c=>c[0]==='event'&&c[1]==='page_view').length,1);
 await page.goto('https://getmacros.net/food-diary.html',{waitUntil:'networkidle'});
 assert.equal(await page.evaluate(()=>!!window.dataLayer),false);
 await page.screenshot({path:path.join(out,'private-diary-mobile.png')});results.screenshots.push('private-diary-mobile.png');
 await page.goto('https://getmacros.net/?q=PRIVATE_CANARY#PRIVATE_CANARY',{waitUntil:'networkidle'});
 assert.equal(await page.evaluate(()=>!!window.dataLayer),false);
 results.checks.push('Saved consent does not initialize GA4 on diary or query/fragment URLs.');
 // Fresh context has no diary data. One real Google tag/collector smoke test.
 allowGoogle=true;
 await page.goto('https://getmacros.net/articles.html',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>document.cookie.includes('_ga'));
 await page.waitForTimeout(1800);
 assert.ok(results.googleTagDownloads.some(r=>r.status===200));
 assert.ok(results.collectorResponses.some(r=>r.status===204));
 assert.equal(results.collectorResponses.filter(r=>r.event==='page_view').length,1);
 await page.setViewportSize({width:1440,height:900});
 await page.locator('[data-analytics-footer]').click();
 await page.locator('#analytics-preferences').evaluate(e=>Promise.all(e.getAnimations().map(a=>a.finished)));
 await page.screenshot({path:path.join(out,'preferences-desktop.png')});results.screenshots.push('preferences-desktop.png');
 await page.locator('#analytics-preferences [data-analytics-choice=denied]').click();
 await page.waitForLoadState('networkidle');
 assert.equal(await page.evaluate(()=>document.cookie.split(';').some(c=>/^\s*_ga(?:_|=)/.test(c))),false);
 results.checks.push('Google tag returned 200; collector accepted exactly one debug/internal page_view with 204. Revocation clears GA cookies.');
 assert.deepEqual(results.errors,[]);
 await context.close();await browser.close();
}
main().then(()=>{fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(results,null,2)+'\n');console.log(JSON.stringify(results,null,2));}).catch(async e=>{results.errors.push(e.stack);fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(results,null,2)+'\n');console.error(e);if(activeBrowser)await activeBrowser.close();process.exitCode=1;});
