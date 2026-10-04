/* Read-only verification of the actual GitHub Pages release, not local fixtures. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out='docs/playful-release-2026-10-04/live';fs.mkdirSync(out,{recursive:true});
const normalized=text=>text.replace(/\r\n/g,'\n');
const report={time:new Date().toISOString(),http:[],journeys:[],fixture:false,edgeTransformations:[]};
function decodeEmail(hex){
 assert.match(hex,/^(?:[0-9a-f]{2}){2,}$/i,'Invalid Cloudflare email encoding');
 const bytes=Buffer.from(hex,'hex');return Buffer.from([...bytes.subarray(1)].map(byte=>byte^bytes[0])).toString('utf8');
}
function productionText(text,route){
 const emails=[];let scriptCount=0;
 text=text.replace(/href="\/cdn-cgi\/l\/email-protection#([0-9a-f]+)"/gi,(_,hex)=>{const email=decodeEmail(hex);emails.push(email);return 'href="mailto:'+email+'"';});
 text=text.replace(/<span class="__cf_email__" data-cfemail="([0-9a-f]+)">\[email&#160;protected\]<\/span>/gi,(_,hex)=>{const email=decodeEmail(hex);emails.push(email);return email;});
 text=text.replace(/<script data-cfasync="false" src="\/cdn-cgi\/scripts\/[0-9a-f]+\/cloudflare-static\/email-decode\.min\.js"><\/script>/gi,()=>{scriptCount++;return '';});
 if(emails.length||scriptCount)report.edgeTransformations.push({route,emails:[...new Set(emails)],scriptCount,kind:'Cloudflare email protection; decoded values must exactly match source HTML'});
 return normalized(text);
}
function matchesCandidate(text,route){assert.ok(productionText(text,route)===normalized(fs.readFileSync(route||'index.html','utf8')),`${route||'/'} differs from candidate after only verified email-protection normalization`);}
async function get(route){const response=await fetch('https://getmacros.net/'+route,{signal:AbortSignal.timeout(20000),cache:'no-store'});return {status:response.status,text:await response.text()};}
(async()=>{
 const home=await get('index.html');assert.equal(home.status,200);matchesCandidate(home.text,'index.html');
 const routes=fs.readdirSync('.').filter(f=>f.endsWith('.html'));
 for(let i=0;i<routes.length;i+=4){await Promise.all(routes.slice(i,i+4).map(async route=>{const r=await get(route);assert.equal(r.status,200,route);matchesCandidate(r.text,route);report.http.push({route,status:r.status,contentMatches:true});}));if(i%40===0)console.log('Verified',Math.min(i+4,routes.length),'of',routes.length,'live pages');}
 for(const route of ['','sitemap.xml','css/publication.css','css/food-shelf.css','css/release-library.css','css/play-release.css','js/meal-data.js','js/meal-provenance.js','js/play-rules.js','images/food-characters.svg']){const r=await get(route);assert.equal(r.status,200,route);matchesCandidate(r.text,route);report.http.push({route,status:r.status,contentMatches:true});}
 for(const route of ['__getmacros_missing_release_check__.html','tools/build_playful_interface.py','docs/playful-release-2026-10-04/report.md']){const r=await get(route);assert.equal(r.status,404,route);report.http.push({route,status:404,excludedOrMissing:true});}
 const browser=await chromium.launch({channel:'msedge'});
 try{for(const theme of ['light','dark'])for(const width of [390,1440]){
  const page=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'}),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.addInitScript(t=>localStorage.setItem('gm-theme',t),theme);
  await page.goto('https://getmacros.net/');await page.evaluate(()=>document.fonts.ready);await page.locator('[data-launch-guide]').first().waitFor();assert.equal(await page.locator('.home-popular .meal-row').count(),4);assert.equal(await page.locator('html').getAttribute('data-theme'),theme);await page.locator('[data-launch-guide]').first().click();await page.locator('.guided-dialog[open]').waitFor();assert.equal(await page.locator('.guided-dialog input:checked').count(),0);await page.locator('[data-guide-close]').click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);await page.screenshot({path:path.join(out,`home-${theme}-${width}.png`),fullPage:true});
  await page.goto('https://getmacros.net/restaurant-meal-finder.html?chain=QDOBA&maxCal=800&minProtein=30');await page.locator('#meal-quiz[data-ready=true]').waitFor();assert.equal(await page.locator('input[name=maxCal]').inputValue(),'800');assert.equal(await page.locator('input[name=minProtein]').inputValue(),'30');assert.equal(await page.evaluate(()=>GetMacrosMeals.results(GM_MEALS,GetMacrosMeals.fromSearch(location.search,GM_MEALS)).every(m=>m.chain==='QDOBA'&&m.cal<=800&&m.p>=30)),true);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);await page.screenshot({path:path.join(out,`finder-${theme}-${width}.png`),fullPage:true});
  await page.goto('https://getmacros.net/contact.html');await page.locator('[data-copy-address]:not([disabled])').waitFor();await page.locator('.contact-address').filter({hasText:'getmacros.net@outlook.com'}).waitFor();assert.equal(await page.locator('.contact-address').getAttribute('href'),'mailto:getmacros.net@outlook.com');await page.evaluate(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async value=>window.__copiedAddress=value}}));await page.locator('[data-copy-address]').click();await page.locator('#contact-copy-status').filter({hasText:'Copied.'}).waitFor();assert.equal(await page.evaluate(()=>window.__copiedAddress),'getmacros.net@outlook.com');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);await page.screenshot({path:path.join(out,`contact-${theme}-${width}.png`),fullPage:true});
  assert.deepEqual(errors,[]);report.journeys.push({theme,width,homeQuiz:true,strictFilters:true,contactReadable:true,contactCopyHandler:true,clipboard:'mocked write only; no message sent',errors});await page.close();
 }}finally{await browser.close();}
 fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2));console.log('PASS actual production: '+routes.length+' matching pages (documented email-protection rewrites only), root/assets/sitemap,404/exclusions and4 theme/viewport journeys.');
})().catch(error=>{fs.writeFileSync(path.join(out,'failure.json'),JSON.stringify({...report,error:error.stack},null,2));console.error(error.message);process.exitCode=1;});
