/* Ordinary public HTTP checks, never authenticated account access. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),revision=process.argv[2];
assert(/^[a-f0-9]{40}$/.test(revision||''));
const report={checkedAt:new Date().toISOString(),revision,syntheticRequests:true,pages:[],assets:[],workflows:[],errors:[]};
const get=url=>fetch(url,{headers:{'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'},signal:AbortSignal.timeout(30000)});
const normalize=b=>b.toString().replaceAll('\r\n','\n');
async function main(){
 for(const branch of ['main','claude/getmacros-nutrition-site-1gfhsm']){
  const r=await get('https://api.github.com/repos/MichaelMGui/GetMacros.net/branches/'+encodeURIComponent(branch)+'?checked='+Date.now());assert.equal(r.status,200);
  assert.equal((await r.json()).commit.sha,revision);
 }
 const r=await get('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=10&checked='+Date.now());assert.equal(r.status,200);
 report.workflows=(await r.json()).workflow_runs.map(x=>({id:x.id,name:x.name,branch:x.head_branch,status:x.status,conclusion:x.conclusion,url:x.html_url}));
 const deployment=report.workflows.find(x=>x.name==='pages build and deployment');
 // Never negatively cache an immutable asset by checking before publication.
 assert.ok(deployment&&deployment.status==='completed'&&deployment.conclusion==='success','Wait for Pages deployment before requesting new asset URLs.');
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'assets/generated/manifest.json')));
 for(const source of ['js/analytics.js','css/analytics-consent.css']){
  const asset=manifest[source],response=await get('https://getmacros.net'+asset.url);assert.equal(response.status,200,asset.url);
  const text=normalize(await response.text()),expected=normalize(fs.readFileSync(path.join(root,source)));
  assert.equal(text,expected,source+' live differs');
  report.assets.push({source,url:asset.url,status:response.status,sha256:crypto.createHash('sha256').update(text).digest('hex')});
 }
 for(const [route,scope] of [['/','public'],['/ca/en/','public'],['/articles.html','public'],['/privacy.html','public'],['/food-diary.html','private'],['/calculators.html','private'],['/restaurant-meal-finder.html','private']]){
  const response=await get('https://getmacros.net'+route),text=await response.text();assert.equal(response.status,200,route);
  assert.ok(text.includes('data-analytics-page="'+scope+'"'),route+' scope');
  assert.ok(text.includes(manifest['js/analytics.js'].url),route+' stale script');
  assert.equal((text.match(/id="analytics-preferences"/g)||[]).length,1,route+' dialog');
  assert.ok(text.includes('data-analytics-footer'),route+' footer');
  assert.ok(!text.includes('src="https://www.googletagmanager.com'),route+' must not eagerly load Google');
  if(route==='/privacy.html'){assert.ok(text.includes('after you choose Allow analytics'));assert.ok(!text.includes('does not load Google Analytics 4'));}
  if(route==='/food-diary.html')assert.ok(text.includes('content="noindex,follow"'));
  report.pages.push({route,status:response.status,scope,reviewedTag:true});
 }
}
main().catch(e=>{report.errors.push(e.stack);process.exitCode=1;}).finally(()=>{
 fs.writeFileSync(path.join(root,'docs/analytics-2026-10-23/production.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
});
