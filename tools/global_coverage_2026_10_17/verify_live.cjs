const fs=require('node:fs'),crypto=require('node:crypto'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const revision=process.argv[2];assert(/^[a-f0-9]{40}$/.test(revision||''));
const base='https://getmacros.net',out='docs/global-coverage-2026-10-17';
const headers={'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'};
const hash=(b,text=true)=>crypto.createHash('sha256').update(text?b.toString('utf8').replace(/\r\n/g,'\n'):b).digest('hex');
(async()=>{
 const response=await fetch('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=10',{headers});assert.equal(response.status,200);const {workflow_runs:runs}=await response.json();
 assert(runs.some(r=>r.name==='pages build and deployment'&&r.status==='completed'&&r.conclusion==='success'),'Production Pages deployment has not succeeded');
 assert(runs.some(r=>r.name==='Site quality'),'Missing quality workflow');assert(runs.every(r=>r.status==='completed'&&r.conclusion==='success'),JSON.stringify(runs.map(r=>({name:r.name,status:r.status,conclusion:r.conclusion}))));
 const integration=JSON.parse(fs.readFileSync(out+'/integration.json')),paths=new Map();
 for(const page of integration.pages)paths.set(page.path,page.route);
 for(const path of ['food-diary.html','food-library.html','grocery-food-coverage.html','sitemap.xml','sw.js','js/order-registry.json','data/restaurant-foods/manifest.json',...['off','usda','cnf','retailer-ca'].map(p=>'data/branded-foods/'+p+'/manifest.json')])paths.set(path,'/'+path);
 const assets=JSON.parse(fs.readFileSync('assets/generated/manifest.json'));for(const key of ['js/branded-foods.js','js/food-library.js','js/markets.js','js/market-definitions.js']){const path=assets[key].url.slice(1);paths.set(path,'/'+path);}
 const checked=[];for(const [path,route]of paths){const r=await fetch(base+route,{headers,signal:AbortSignal.timeout(30000)});assert.equal(r.status,200,route);const remote=Buffer.from(await r.arrayBuffer()),local=fs.readFileSync(path);assert.equal(hash(remote),hash(local),'Live source mismatch '+route);checked.push({url:base+route,path,status:200,sha256:hash(remote),cacheStatus:r.headers.get('cf-cache-status'),age:r.headers.get('age')});}
 const menus=JSON.parse(fs.readFileSync('data/restaurant-foods/manifest.json'));for(const [market,source]of Object.entries(menus.markets)){const path='data/restaurant-foods/'+source.file,url=base+'/'+path+'?v='+menus.version,r=await fetch(url,{headers,signal:AbortSignal.timeout(30000)});assert.equal(r.status,200,url);let bytes=Buffer.from(await r.arrayBuffer());if(bytes[0]===31&&bytes[1]===139)bytes=zlib.gunzipSync(bytes);const rows=JSON.parse(bytes);assert.equal(rows.length,source.count);assert(rows.every(x=>x.market===market));assert.deepEqual(rows,JSON.parse(zlib.gunzipSync(fs.readFileSync(path))));checked.push({url,path,status:200,records:rows.length,market});}
 const report={revision,checkedAt:new Date().toISOString(),pass:true,actions:runs.map(r=>({name:r.name,branch:r.head_branch,status:r.status,conclusion:r.conclusion,url:r.html_url})),sourceMatches:checked,indexing:'Deployment verified; Google indexing and traffic not measured.'};fs.writeFileSync(out+'/production-verification.json',JSON.stringify(report,null,2));
 console.log('PASS: '+checked.length+' actual production pages/assets/market shards match '+revision);
})().catch(e=>{console.error(e);process.exitCode=1});
