const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
let browser;
(async()=>{browser=await chromium.launch({channel:'msedge',headless:true});
 const posts=['best-fast-food-restaurants-for-your-goals.html','how-much-protein-can-your-body-absorb.html','are-diet-drinks-bad-for-you.html','does-creatine-cause-hair-loss.html','calories-vs-macros-what-matters-more.html'];
 for(const width of [390,1440]){
  const p=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});await p.route('https://**/*',r=>r.abort());
  for(const file of ['blog.html',...posts]){
   await p.goto('http://127.0.0.1:4174/'+file,{waitUntil:'load'});
   if(file!=='blog.html'){
    assert.equal(await p.locator('.journal-contents').count(),1);
    await p.locator('.journal-contents summary').click();
    assert.equal(await p.locator('.journal-contents a').evaluateAll(es=>es.every(e=>document.getElementById(e.hash.slice(1)))),true);
    await p.locator('.journal-contents summary').click();
    assert.match(await p.locator('.blog-meta').first().innerText(),/Updated September 8, 2026/);
   }
   for(const theme of ['light','dark']){
    await p.evaluate(t=>document.documentElement.dataset.theme=t,theme);
    assert.ok(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),file+' '+width+' '+theme);
    await p.screenshot({path:'design/journal-'+file.replace('.html','')+'-'+width+'-'+theme+'.png',fullPage:true});
   }
  }
  await p.close();console.log('PASS journal: six pages at '+width+'px, both themes, article links and dates');
 }
 const p=await browser.newPage();await p.route('https://**/*',r=>r.abort());
 for(const file of fs.readdirSync('.').filter(f=>f.endsWith('-macros.html')&&fs.readFileSync(f,'utf8').includes('data-chain-form'))){
  await p.goto('http://127.0.0.1:4174/'+file,{waitUntil:'load'});await p.locator('[data-chain-form]').evaluate(f=>f.requestSubmit());
  assert.ok(await p.locator('.chain-result-card').count()>0,file);assert.doesNotMatch(await p.locator('[data-chain-results]').innerText(),/NaN|undefined/);
 }
 console.log('PASS all chain-specific default meal matches');
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>{if(browser)await browser.close()});
