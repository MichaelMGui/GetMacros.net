const assert=require('node:assert/strict');
const fs=require('node:fs');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
let browser;
(async()=>{
 browser=await chromium.launch({channel:'msedge',headless:true});
 const p=await browser.newPage({viewport:{width:390,height:900},reducedMotion:'reduce'});
 await require('./browser-fixture.cjs').localAssets(p);
 const goto=f=>p.goto('http://127.0.0.1:4173/'+f,{waitUntil:'load'});
 await goto('restaurant-meal-finder.html');
 await p.locator('label').filter({has:p.locator('input[data-facet="goal"][value="protein"]')}).click();
 for(let i=0;i<5;i++)await p.locator('.quiz-continue').click();
 assert.ok(await p.locator('.results-grid > *').count()>0);
 const firstCount=await p.locator('.results-grid > *').count();
 if(await p.locator('[data-more]').count()) {await p.locator('[data-more]').click();assert.ok(await p.locator('.results-grid > *').count()>firstCount);}
 assert.doesNotMatch(await p.locator('#meal-quiz').innerText(),/NaN|undefined/);
 await p.locator('[data-restart]').click();assert.ok(await p.locator('.quiz-continue').isVisible());
 console.log('PASS meal finder: high protein, all five steps, more results, edit answers');
 const forms=['nutrition-label-comparison-tool.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','sweat-rate-calculator.html'];
 const report=[];
 for(const file of forms){
  await goto(file);
  const form=p.locator('main form').first();
  const fields=await form.locator('input').evaluateAll(es=>es.map(e=>({id:e.id,value:e.value,type:e.type,min:e.min})));
  const fixtures={
   'sodium-label-comparison-tool.html':{am:'400',as:'1.5',bm:'500',bs:'1'},
   'carbohydrate-label-portion-tool.html':{c:'30',s:'1.5',f:'4',a:'6'},
   'sweat-rate-calculator.html':{before:'80',after:'79',drink:'500',urine:'0',time:'60'}
  };
  for(const [id,value] of Object.entries(fixtures[file]||{}))await p.fill('#'+id,value);
  const valid=await form.evaluate(f=>f.checkValidity());
  if(valid){await form.evaluate(f=>f.requestSubmit());}
  const output=p.locator('#out,#result,#results').first();
  report.push({file,fields,valid,output:await output.innerText()});
  const expected={'sodium-label-comparison-tool.html':/600 mg/,'carbohydrate-label-portion-tool.html':/45.0 g/,'sweat-rate-calculator.html':/1.50 L/};if(expected[file])assert.match(await output.innerText(),expected[file]);
  if(valid){assert.ok((await output.innerText()).trim().length>0);assert.doesNotMatch(await output.innerText(),/NaN|Infinity|undefined/);}
  console.log(file,valid?'PASS default calculation':'Needs filled input test');
 }
 fs.writeFileSync('design/tool-flow-audit.json',JSON.stringify(report,null,2));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>{if(browser)await browser.close()});
