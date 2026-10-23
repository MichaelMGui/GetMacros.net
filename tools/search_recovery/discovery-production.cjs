/* Public crawl checks only; synthetic requests are not independent visitors. */
const fs=require('node:fs'),assert=require('node:assert/strict');
const revision=process.argv[2],out='docs/search-discovery-2026-10-23',base='https://getmacros.net';
assert.match(revision||'',/^[a-f0-9]{40}$/);
const plan=JSON.parse(fs.readFileSync(out+'/implementation.json'));
const report={checkedAt:new Date().toISOString(),revision,syntheticRequests:true,workflows:[],pages:[],errors:[]};
const get=(url,redirect='follow')=>fetch(url,{redirect,headers:{'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'},signal:AbortSignal.timeout(40000)});
function links(html){return [...html.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(m=>new URL(m[1].replaceAll('&amp;','&'),base)).filter(u=>u.origin===base).map(u=>u.pathname);}
(async()=>{try{
 for(const branch of ['main','claude/getmacros-nutrition-site-1gfhsm']){const r=await get('https://api.github.com/repos/MichaelMGui/GetMacros.net/branches/'+encodeURIComponent(branch)+'?checked='+Date.now());assert.equal(r.status,200);assert.equal((await r.json()).commit.sha,revision);}
 const r=await get('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=10&checked='+Date.now());assert.equal(r.status,200);
 report.workflows=(await r.json()).workflow_runs.map(x=>({name:x.name,status:x.status,conclusion:x.conclusion,url:x.html_url}));
 assert(report.workflows.some(x=>x.name==='pages build and deployment'&&x.conclusion==='success'),'Wait for successful Pages deployment');
 const sm=await get(base+'/sitemap.xml');assert.equal(sm.status,200);const sitemap=await sm.text();
 const queue=[...plan.routes];
 await Promise.all(Array.from({length:3},async()=>{while(queue.length){const route=queue.shift(),r=await get(base+route,'manual'),html=await r.text();
  assert.equal(r.status,200,route);assert(html.includes('rel="canonical" href="'+base+route+'"'),route+' canonical');
  assert(!/<meta[^>]*name="robots"[^>]*content="[^"]*noindex/i.test(html),route+' noindex');
  assert(!/noindex/i.test(r.headers.get('x-robots-tag')||''),route+' X-Robots-Tag');
  assert(sitemap.includes('<loc>'+base+route+'</loc>'),route+' sitemap');
  const found=links(html),expected=plan.links.filter(x=>x.from===route);
  for(const link of expected)assert(found.includes(link.to),route+' missing '+link.to);
  const row={route,status:r.status,canonical:base+route,contextLinksChecked:expected.length};
  if(route==='/nutrition-label-comparison-tool.html')assert(html.includes('<h1>Compare nutrition facts</h1>'));
  report.pages.push(row);
 }}));
 // The historical 5xx example is retired. A real 404 after HTTPS redirection
 // is appropriate; never redirect this unrelated article to the homepage.
 const old=await get('http://getmacros.net/why-nutrition-studies-contradict-each-other.html');
 report.retiredExample={status:old.status,url:old.url};assert.equal(old.status,404);
 const p=await get(base+'/food-diary.html');assert.equal(p.status,200);assert((await p.text()).includes('content="noindex,follow"'));
 const robots=await get(base+'/robots.txt');assert.equal(robots.status,200);assert((await robots.text()).includes('Sitemap: '+base+'/sitemap.xml'));
 }catch(e){report.errors.push(e.stack);process.exitCode=1;}
 report.pages.sort((a,b)=>a.route.localeCompare(b.route));fs.writeFileSync(out+'/production.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({pages:report.pages.length,linksChecked:report.pages.reduce((s,r)=>s+r.contextLinksChecked,0),workflows:report.workflows,retiredExample:report.retiredExample,errors:report.errors},null,2));
})().catch(e=>{console.error(e);process.exitCode=1;});
