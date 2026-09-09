const assert=require('node:assert/strict'),fs=require('node:fs');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
async function check(page){
 const issues=await page.evaluate(()=>{
  const issues=[];
  if(document.documentElement.scrollWidth>innerWidth+2)issues.push('Page overflows');
  for(const box of document.querySelectorAll('.chain-choice-grid label,.chain-result-card,.pick-card,.ranking-list li')){
   if(!box.getClientRects().length)continue;
   const bound=box.getBoundingClientRect();
   const walker=document.createTreeWalker(box,NodeFilter.SHOW_TEXT);
   while(walker.nextNode()){
    const node=walker.currentNode;
    if(node.parentElement.closest('svg,script,style')||!node.parentElement.getClientRects().length)continue;
    const whole=document.createRange();whole.selectNodeContents(node);
    if([...whole.getClientRects()].some(r=>r.width&&(r.left<bound.left-2||r.right>bound.right+2)))issues.push('Outside card: '+node.textContent.trim());
    for(const match of node.textContent.matchAll(/\b[A-Za-z]{5,20}\b/g)){
     const range=document.createRange();range.setStart(node,match.index);range.setEnd(node,match.index+match[0].length);
     const rects=[...range.getClientRects()].filter(r=>r.width&&r.height);
     if(rects.some(r=>Math.abs(r.top-rects[0].top)>3))issues.push('Split word: '+match[0]);
    }
   }
  }
  if(innerWidth<=540)for(const label of document.querySelectorAll('.chain-goals b')){
   const range=document.createRange();range.selectNodeContents(label);
   if([...range.getClientRects()].length>1)issues.push('Cramped goal label: '+label.textContent);
  }
  return issues;
 });
 assert.deepEqual(issues,[],page.url());
}
(async()=>{
 for(const engine of ['edge','webkit']){
  const browser=await(engine==='edge'?chromium.launch({channel:'msedge'}):webkit.launch());
  try{
   for(const theme of ['light','dark'])for(const width of [320,768,1440]){
    process.env.GM_TEST_THEME=theme;
    const p=await browser.newPage({viewport:{width,height:950},reducedMotion:'reduce'});await localAssets(p);
    const all=fs.readdirSync('.').filter(f=>f.endsWith('.html')&&fs.readFileSync(f,'utf8').includes('data-chain-finder'));
    const files=engine==='edge'?all:all.filter(f=>/chipotle|jersey-mikes|panda-express/.test(f));
    for(const file of files){
     await p.goto('http://127.0.0.1:4174/'+file);
     for(const goal of ['protein','energy'])await p.locator('label').filter({has:p.locator('input[name="chain-goal"][value="'+goal+'"]')}).click();
     await p.locator('[data-chain-form] button[type="submit"]').click();
     assert.ok(await p.locator('.chain-result-card').count()>0);await check(p);
    }
    await p.goto('http://127.0.0.1:4174/healthy-fast-food.html');
    for(const summary of await p.locator('.ranking-disclosure summary').all())await summary.click();
    await check(p);await p.close();console.log('PASS Eat Out layout',engine,theme,width,files.length,'restaurant pages and all rankings');
   }
  }finally{await browser.close();}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
