const fs=require('node:fs'),assert=require('node:assert/strict');
const{chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');const{localAssets}=require('./browser-fixture.cjs');
(async()=>{const b=await chromium.launch({channel:'msedge'}),report=[];try{
 const files=['',...fs.readdirSync('.').filter(f=>f.endsWith('.html'))];
 for(const theme of ['light','dark']){process.env.GM_TEST_THEME=theme;const p=await b.newPage();await localAssets(p);let errors=[];p.on('pageerror',e=>errors.push(e.message));
 for(const file of files){errors=[];await p.goto('http://127.0.0.1:4187/'+file);await p.evaluate(()=>document.fonts.ready);
  for(const width of [320,375,390,430,768,1024,1440]){await p.setViewportSize({width,height:960});const r=await p.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('main h1').length,footers:document.querySelectorAll('.market-footer').length,styles:document.styleSheets.length,unlabelled:[...document.querySelectorAll('main input:not([type=hidden]),main select,main textarea')].filter(e=>!e.labels?.length&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')).map(e=>e.id),oldMarks:document.querySelectorAll('img[src*="restaurant-marks"],img[src*="restaurant-logos"],.restaurant-initial,.back-to-top').length}));report.push({file,theme,width,...r,errors:[...errors]});}
 }await p.close();console.log('Checked',theme,files.length,'routes at seven widths');}
 }finally{await b.close()}const failures=report.filter(r=>r.overflow||r.h1!==1||r.footers!==1||r.styles!==1||r.unlabelled.length||r.oldMarks||r.errors.length);fs.writeFileSync('docs/redesign/refinement/routes.json',JSON.stringify({checks:report.length,failures,results:report},null,2));console.log(report.length,'checks,',failures.length,'failures');assert.deepEqual(failures,[]);
})().catch(e=>{console.error(e);process.exitCode=1});
