/* Real production HTTP checks, distinct from local fixtures and indexing. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const out='docs/global-product-release-2026-10-11',revision=process.argv[2];
assert(/^[a-f0-9]{40}$/.test(revision),'Pass the actual deployed Git revision.');
const base='https://getmacros.net',headers={'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'};
async function read(url){const response=await fetch(url,{headers,signal:AbortSignal.timeout(25000)});return{status:response.status,url:response.url,text:await response.text()};}
const hash=s=>crypto.createHash('sha256').update(s.replace(/\r\n/g,'\n')).digest('hex');
(async()=>{
 const report={revision,verifiedAt:new Date().toISOString(),production:base,assets:[],routes:[],privatePaths:[],searchConsole:'No authorized access; submission, crawling, indexing and search clicks unverified'};
 const assets=['data/food-library/manifest.json','data/food-library/index.json','js/order-registry.json','js/app-config.js','js/ingredient-comparison.js','js/food-core.js','js/food-app.js','css/food-app.css','site.webmanifest','sw.js','sitemap.xml'];
 for(const asset of assets){const r=await read(base+'/'+asset+'?release='+revision);const expected=fs.readFileSync(asset,'utf8');assert.equal(r.status,200,asset+' HTTP status');assert.equal(hash(r.text),hash(expected),asset+' has not reached the verified release');report.assets.push({path:asset,status:r.status,sha256:hash(r.text)});}
 const manifest=JSON.parse((await read(base+'/data/food-library/manifest.json?release='+revision)).text),registry=JSON.parse((await read(base+'/js/order-registry.json?release='+revision)).text);
 assert.equal(manifest.profileCount,13578);assert.equal(registry.records.length,1400);assert.equal(registry.markets.length,8);
 const routes=[...new Set(JSON.parse(fs.readFileSync(out+'/route-renders.json','utf8')).renders.map(r=>r.route))];let cursor=0;
 await Promise.all(Array.from({length:4},async()=>{while(cursor<routes.length){const route=routes[cursor++],r=await read(base+route+'?release='+revision);const canonical=r.text.match(/<link rel="canonical" href="([^"]+)"/i)?.[1]||null,robots=r.text.match(/<meta name="robots" content="([^"]+)"/i)?.[1]||'indexable default';report.routes.push({route,status:r.status,canonical,robots,h1Count:(r.text.match(/<h1\b/gi)||[]).length});}}));
 for(const r of report.routes){assert.equal(r.status,200,r.route+' live HTTP status');assert.equal(r.h1Count,1,r.route+' live heading');assert(r.canonical?.startsWith(base+'/'),r.route+' live canonical');}
 for(const route of ['/server/index.cjs','/tools/product_release/menu-records.json','/docs/global-product-release-2026-10-11/sources/japan.html']){const r=await read(base+route+'?release='+revision);report.privatePaths.push({route,status:r.status});assert.equal(r.status,404,route+' must not be published');}
 const sitemap=(await read(base+'/sitemap.xml?release='+revision)).text;assert.equal((sitemap.match(/<loc>/g)||[]).length,338);assert(!sitemap.includes('/food-diary.html')&&!sitemap.includes('/offline.html'));
 assert(report.routes.find(r=>r.route==='/food-diary.html').robots.includes('noindex'));
 report.counts={foodProfiles:manifest.profileCount,restaurantRecords:registry.records.length,markets:registry.markets,checkedPublicRoutes:report.routes.length,sitemapPages:338};
 const response=await fetch('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=10',{headers:{...headers,Accept:'application/vnd.github+json'},signal:AbortSignal.timeout(25000)});
 report.actionsHttpStatus=response.status;if(response.ok){const data=await response.json();report.actions=data.workflow_runs.map(r=>({name:r.name,status:r.status,conclusion:r.conclusion,url:r.html_url,headSha:r.head_sha}));}
 fs.writeFileSync(out+'/deployment-verification.json',JSON.stringify(report,null,2));
 const newPages=JSON.parse(fs.readFileSync(out+'/published-manifest.json','utf8')),extra={route:'/raw-vs-cooked-food-weight.html',market:'global',kind:'improved article',indexable:true};
 const csv=['type,url,country,http_status,canonical,indexing_directive,live_verified_at,revision'];
 const quote=s=>'"'+String(s).replaceAll('"','""')+'"';
 for(const page of [...newPages,extra]){const r=report.routes.find(r=>r.route===page.route);assert(r);csv.push([page.kind,base+page.route,page.market,r.status,r.canonical,r.robots,report.verifiedAt,revision].map(quote).join(','));}
 fs.writeFileSync(out+'/verified-live-links.csv',csv.join('\n')+'\n');
 console.log('PASS live release:',report.routes.length,'routes;',manifest.profileCount,'food profiles;',registry.records.length,'market records; private paths 404.');
 console.log(JSON.stringify(report.actions||{actionsUnavailable:report.actionsHttpStatus}));
})().catch(error=>{console.error(error.message);process.exitCode=1;});
