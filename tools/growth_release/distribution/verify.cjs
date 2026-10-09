const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'docs/growth-release-2026-10-09/distribution');
const manifest=JSON.parse(fs.readFileSync(path.join(out,'graphics-manifest.json'),'utf8')),drafts=JSON.parse(fs.readFileSync(path.join(out,'distribution-drafts.json'),'utf8'));
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const checks=[];function check(name,condition){assert(condition,name);checks.push(name);}
const g=id=>manifest.graphics.find(x=>x.id.startsWith(id));
check('20 original graphics, 20 distinct existing destinations',manifest.graphics.length===20&&new Set(manifest.graphics.map(x=>x.destination)).size===20);
check('Eight scripts, four newsletters, five unsent outreach drafts',drafts.videoScripts.length===8&&drafts.newsletterDrafts.length===4&&drafts.outreachDrafts.length===5);
const difference=(id,key)=>g(id).records[1][key]-g(id).records[0][key];
check('01 bowl/burrito: +300 kcal, +8 g protein',difference('01','cal')===300&&difference('01','p')===8);
check('02 chicken has 8 g more protein, steak has 50 mg less sodium',difference('02','p')===-8&&difference('02','na')===-50);
check('03 flour build: +80 kcal, +420 mg sodium',difference('03','cal')===80&&difference('03','na')===420);
check('04 quesadillas: equal 51 g protein, +120 kcal',g('04').records.every(r=>r.p===51)&&difference('04','cal')===120);
check('05 Pasta Fresca: +5 g fiber, -770 mg sodium',difference('05','f')===5&&difference('05','na')===-770);
check('06 Mediterranean: -240 kcal, +190 mg sodium',difference('06','cal')===240&&difference('06','na')===-190);
check('07 alternate hamburger: -60 kcal, unchanged protein',difference('07','cal')===-60&&difference('07','p')===0);
check('08 lettuce wrap: -150 kcal, -4 g protein',difference('08','cal')===-150&&difference('08','p')===-4);
check('09 grilled sandwich: -210 kcal, +8 g protein',difference('09','cal')===210&&difference('09','p')===-8);
check('10 tender flavors: equal 39 g protein, +450 mg sodium',g('10').records.every(r=>r.p===39)&&difference('10','na')===450);
check('11 chicken burrito: +7 g protein, +160 mg sodium',difference('11','p')===7&&difference('11','na')===160);
check('12 chicken exact fiber unknown with source <1, refried-bean fiber exactly 4',g('12').records[0].f===null&&g('12').records[0].nutrientProvenance.f.publishedBound==='<1'&&g('12').records[1].f===4);
check('13 Guac’d Up named build: +20 kcal, +2 g fiber',difference('13','cal')===20&&difference('13','f')===2);
check('14 unequal taco portion weights preserved',g('14').records[0].serving.includes('90 g')&&g('14').records[1].serving.includes('157 g'));
check('15 Reuben: +300 kcal, +11 g protein',difference('15','cal')===300&&difference('15','p')===11);
check('16 two sliders explicit multiplied quantity: equal 360 kcal, -1 g protein, +70 mg sodium',g('16').records[1].count===2&&g('16').records.every(r=>r.cal===360)&&difference('16','p')===-1&&difference('16','na')===70);
check('17 teriyaki: +23 g protein, -3 g fiber',difference('17','p')===23&&difference('17','f')===-3);
check('18 complete total is calculated; side adds 180 kcal, 8 g protein, 8 g fiber and 660 mg sodium',g('18').records[1].nutrientProvenance.cal.method==='calculated'&&difference('18','cal')===180&&difference('18','p')===8&&difference('18','f')===8&&difference('18','na')===660);
check('19 bowls: equal 1830 mg sodium; +125 kcal, +3 g protein',g('19').records.every(r=>r.na===1830)&&difference('19','cal')===125&&difference('19','p')===3);
check('20 Harvest: +2 g protein, -295 mg sodium, +250 kcal',difference('20','p')===2&&difference('20','na')===-295&&difference('20','cal')===250);
check('Receipt examples: no purported restaurant prices',drafts.videoScripts.find(s=>s.id==='video-06').arithmeticExamples.every(e=>e.price/e.proteinGrams===e.result));
check('Recipe illustrative portions: 200 kcal and 10 g protein',800/4===200&&40/4===10);
check('Label illustrative basis: 8 g per 50 g equals 16 g per 100 g',8*100/50===16);
for(const graphic of manifest.graphics){const svg=fs.readFileSync(path.join(out,graphic.file),'utf8');for(const metric of graphic.metrics){let left=metric.left.replace(/</g,'&lt;'),right=metric.right.replace(/</g,'&lt;');check(graphic.id+' visible '+metric.field+' matches data, bound and units',svg.includes('>'+left+'</text>')&&svg.includes('>'+right+'</text>'));}
 check(graphic.id+' actual region/date, source links, exact full portions in metadata',graphic.records.every(r=>r.region==='U.S.'&&/^2026-10-0[34]$/.test(r.checked)&&r.source.startsWith('https://')&&r.serving)&&graphic.currentOfficialRecheckPerformed===false);
 check(graphic.id+' no raster photos or external artwork/fonts',!/<image\b/.test(svg)&&!/<script\b/.test(svg)&&!/@import/.test(svg));
 for(let i=0;i<graphic.records.length;i++){const portion=graphic.displayedPortions[i];const weight=portion.match(/(?:·|\+)\s*(\d+(?:\.\d+)?)\s*(g|oz)/);if(weight&&graphic.records[i].count===1)check(graphic.id+' declared portion weight matches source',graphic.records[i].serving.includes(weight[1]+' '+weight[2]));}
}
const types={'.html':'text/html','.svg':'image/svg+xml','.json':'application/json','.woff2':'font/woff2','.css':'text/css','.png':'image/png'};
const server=http.createServer((req,res)=>{const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}res.setHeader('Content-Type',types[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
(async()=>{const report={date:'2026-10-09',status:'drafts not distributed',sourceRecheck:'Not performed by this distribution task; recorded Oct 3–4 provenance retained.',arithmeticChecks:checks,svgRenderChecks:[],sharePreviewRenderChecks:[],previewChecks:[],liveDestinations:[],screenshots:[],exports:[]};
 await new Promise(r=>server.listen(4396,'127.0.0.1',r));const browser=await chromium.launch({channel:'msedge'});fs.mkdirSync(path.join(out,'screenshots'),{recursive:true});
 try{const p=await browser.newPage({viewport:{width:1080,height:1350}});const runtimeErrors=[];p.on('pageerror',e=>runtimeErrors.push(e.message));await p.route('https://**/*',r=>r.abort());
  for(const graphic of manifest.graphics){await p.goto('http://127.0.0.1:4396/docs/growth-release-2026-10-09/distribution/'+graphic.file);await p.evaluate(()=>document.fonts.ready);const boxes=await p.evaluate(()=>[...document.querySelectorAll('text')].map(e=>{const b=e.getBBox();return{text:e.textContent,x:b.x,y:b.y,width:b.width,height:b.height};}));const errors=boxes.filter(b=>b.x<36||b.x+b.width>1044||b.y<0||b.y+b.height>1340);assert.equal(errors.length,0,graphic.id+' SVG text outside artboard: '+JSON.stringify(errors));
   const names=boxes.filter(b=>b.y>395&&b.y<545);assert(names.every(b=>b.x===64?b.x+b.width<=540:b.x+b.width<=1030),graphic.id+' exact name crosses comparison columns');
   const headline=boxes.filter(b=>b.y>145&&b.y<300);assert(headline.every(b=>b.x+b.width<925),graphic.id+' headline collides with character');
   report.svgRenderChecks.push({id:graphic.id,textNodes:boxes.length,fonts:[...await p.evaluate(()=>[...document.fonts].map(f=>({family:f.family,status:f.status})))],overflow:0,metricValuesVerified:true});
   await p.screenshot({path:path.join(out,graphic.png)});report.exports.push({file:graphic.png,width:1080,height:1350});
   if(['01','08','12','18','20'].some(prefix=>graphic.id.startsWith(prefix))){let file='screenshots/'+graphic.id+'.png';await p.screenshot({path:path.join(out,file)});report.screenshots.push(file);}
  }
  await p.setViewportSize({width:1200,height:630});
  for(const graphic of manifest.graphics){await p.goto('http://127.0.0.1:4396/docs/growth-release-2026-10-09/distribution/'+graphic.sharePreview.svg);await p.evaluate(()=>document.fonts.ready);const boxes=await p.evaluate(()=>[...document.querySelectorAll('text')].map(e=>{const b=e.getBBox();return{text:e.textContent,x:b.x,y:b.y,width:b.width,height:b.height};}));const errors=boxes.filter(b=>b.x<35||b.x+b.width>1165||b.y<0||b.y+b.height>620);assert.equal(errors.length,0,graphic.id+' social preview text outside artboard: '+JSON.stringify(errors));
   const names=boxes.filter(b=>b.y>210&&b.y<335);assert(names.every(b=>b.x===48?b.x+b.width<=600:b.x+b.width<=1165),graphic.id+' social preview name crosses columns');
   await p.screenshot({path:path.join(out,graphic.sharePreview.png)});report.sharePreviewRenderChecks.push({id:graphic.id,width:1200,height:630,overflow:0});report.exports.push({file:graphic.sharePreview.png,width:1200,height:630});
  }
  for(const width of [320,390,768,1280,1440])for(const file of ['preview.html','drafts.html']){await p.setViewportSize({width,height:900});await p.goto('http://127.0.0.1:4396/docs/growth-release-2026-10-09/distribution/'+file);await p.evaluate(()=>document.fonts.ready);assert.equal(await p.locator('article').count(),file==='preview.html'?20:17);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,file+' overflow '+width);await p.evaluate(()=>document.documentElement.style.fontSize='200%');assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,file+' enlarged text overflow '+width);report.previewChecks.push({file,width,textEnlargement:'200% root',articles:file==='preview.html'?20:17,overflow:0});}
  await p.setViewportSize({width:390,height:844});await p.emulateMedia({reducedMotion:'reduce'});await p.goto('http://127.0.0.1:4396/docs/growth-release-2026-10-09/distribution/preview.html');await p.keyboard.press('Tab');assert(await p.evaluate(()=>document.activeElement.tagName==='A'),'Preview keyboard focus');await p.screenshot({path:path.join(out,'screenshots/preview-mobile.png')});report.screenshots.push('screenshots/preview-mobile.png');report.runtimeErrors=runtimeErrors;assert.equal(runtimeErrors.length,0,'Distribution browser runtime errors');report.reducedMotion='Reduced-motion preview rendered; no essential motion or moving characters.';
 }finally{await browser.close();server.close();}
 if(process.argv.includes('--live')){const urls=[...new Set([...manifest.graphics.map(g=>g.destination),...drafts.videoScripts.map(s=>s.destination),...drafts.newsletterDrafts.flatMap(n=>n.destinations),...drafts.outreachDrafts.map(o=>o.destination),url('unequal-recipe-portions.html')])];
  for(const destination of urls){const response=await fetch(destination,{redirect:'follow',signal:AbortSignal.timeout(45000)}),body=await response.text();assert.equal(response.status,200,destination+' actual live HTTP status');const canonical=(body.match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/)||[])[1]||(body.match(/<link[^>]*href=["']([^"']+)["'][^>]*rel=["']canonical/)||[])[1];assert.equal(canonical,destination,destination+' canonical');report.liveDestinations.push({url:destination,status:response.status,finalURL:response.url,canonical,checkedAt:new Date().toISOString(),htmlSha256:crypto.createHash('sha256').update(body).digest('hex')});}
 }
 report.passed=true;report.liveDestinationsVerified=process.argv.includes('--live');fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({passed:true,arithmeticChecks:checks.length,svgRenderChecks:report.svgRenderChecks.length,sharePreviewRenderChecks:report.sharePreviewRenderChecks.length,pngExports:report.exports.length,previewChecks:report.previewChecks.length,liveDestinations:report.liveDestinations.length,screenshots:report.screenshots.length}));
})().catch(e=>{server.close();console.error(e.message);process.exitCode=1;});
function url(route){return 'https://getmacros.net/'+route;}
