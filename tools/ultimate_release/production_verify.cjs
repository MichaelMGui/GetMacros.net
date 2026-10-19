/* Public HTTP verification only. No credentials, analytics or crawl submission. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'docs/ultimate-release-2026-10-19'),revision=process.argv[2];
assert(/^[a-f0-9]{40}$/.test(revision||''),'Pass the actual deployed commit SHA');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),htmlHash=b=>sha(b.toString('utf8').replaceAll('\r\n','\n')),headers={'User-Agent':'GetMacros-release-verification','Accept':'application/vnd.github+json'};
function matchHTML(actual,expected){
 const a=actual.toString('utf8').replaceAll('\r\n','\n'),b=expected.toString('utf8').replaceAll('\r\n','\n');
 if(a===b)return {matched:true,cloudflareSecurityAppendix:false};
 const end=b.lastIndexOf('</body>');if(end<0)return {matched:false,cloudflareSecurityAppendix:false};
 const head=b.slice(0,end),tail=b.slice(end);if(!a.startsWith(head)||!a.endsWith(tail))return {matched:false,cloudflareSecurityAppendix:false};
 const extra=a.slice(head.length,a.length-tail.length),script=extra.trim(),known=/^<script>[\s\S]*<\/script>$/.test(script)&&script.includes('__CF$cv$params')&&script.includes('/cdn-cgi/challenge-platform/')&&(script.match(/<script\b/g)||[]).length===1;
 return {matched:known,cloudflareSecurityAppendix:known,edgeAddedBytes:Buffer.byteLength(extra)};
}
async function get(url){const r=await fetch(url,{headers,signal:AbortSignal.timeout(45000)});return {url,status:r.status,headers:Object.fromEntries(r.headers),bytes:Buffer.from(await r.arrayBuffer())};}
async function api(s){const r=await get('https://api.github.com/repos/MichaelMGui/GetMacros.net/'+s);assert.equal(r.status,200,s);return JSON.parse(r.bytes);}
const localPath=route=>path.join(root,route==='/'?'index.html':route.replace(/^\//,'')+(route.endsWith('/')?'index.html':''));
(async()=>{
 const report={checkedAt:new Date().toISOString(),revision,refs:{},pages:[],assets:[],sitemap:null,indexing:'Not inspected/submitted; no authorized Search Console property',analytics:'No first-party analytics access',errors:[]};
 try{
  for(const branch of ['main','claude/getmacros-nutrition-site-1gfhsm']){const b=await api('branches/'+encodeURIComponent(branch));report.refs[branch]=b.commit.sha;assert.equal(b.commit.sha,revision,'Production ref differs');}
  const published=JSON.parse(fs.readFileSync(path.join(out,'publication-manifest.json'))),routes=[...new Set(['/',...['ca','mx','gb','ie','au','nz','jp','fr','in','sg','za'].map(c=>'/'+c+'/en/'),'/calculators.html','/food-diary.html','/restaurant-meal-finder.html','/compare-complete-restaurant-orders.html','/play.html',...published.map(r=>r.route)])];
  const queue=[...routes];await Promise.all(Array.from({length:4},async()=>{while(queue.length){const route=queue.shift(),r=await get('https://getmacros.net'+route+'?release='+revision.slice(0,12)),text=r.bytes.toString('utf8'),expected=fs.readFileSync(localPath(route)),canonical=text.match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/)?.[1],local=expected.toString('utf8').match(/<link[^>]*rel=["']canonical["'][^>]*href=["']([^"']+)/)?.[1];const row={route,status:r.status,canonical,expectedCanonical:local,byteHash:sha(r.bytes),expectedByteHash:sha(expected),sharedNavigation:text.includes('class="product-nav"'),comparisonBasis:'CRLF normalized for Git portability; complete reviewed HTML must match. A sole appended Cloudflare security script is reported separately,not removed from the website.',sourceMatched:matchHTML(r.bytes,expected).matched,edgeSecurityAppendix:matchHTML(r.bytes,expected)};report.pages.push(row);assert.equal(r.status,200,route);assert.equal(canonical,local,route+' canonical');assert(row.sharedNavigation,route+' shared nav');assert(row.sourceMatched,route+' HTML differs from reviewed output');}}));
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'assets/generated/manifest.json'))),critical=['css/publication.css','css/home-workspace.css','css/food-app.css','css/release-library.css','js/unified-v7.js','js/editorial-browser.js','js/liquid-motion.js','js/meal-guide.js','js/meal-finder.js','js/food-app.js','js/calculators.js','js/gb-meals.js'];
  for(const key of critical){const entry=manifest[key];assert(entry,'Missing asset '+key);const url=entry.url,r=await get('https://getmacros.net'+url);const expected=fs.readFileSync(path.join(root,url.replace(/^\//,'')));report.assets.push({key,url,status:r.status,sha256:sha(r.bytes),expectedSha256:sha(expected),bytes:r.bytes.length});assert.equal(r.status,200,key);assert.equal(sha(r.bytes),sha(expected),key+' immutable asset');}
  const sitemap=await get('https://getmacros.net/sitemap.xml?release='+revision.slice(0,12)),text=sitemap.bytes.toString('utf8');assert.equal(sitemap.status,200);for(const page of published)assert(text.includes('https://getmacros.net'+page.route),page.route+' sitemap');report.sitemap={http:sitemap.status,urls:[...text.matchAll(/<loc>/g)].length,publishedManifestLinksPresent:true,submitted:false};
  const missing=await get('https://getmacros.net/not-a-getmacros-route-'+revision.slice(0,8));assert.equal(missing.status,404,'Unknown route HTTP status');report.notFoundStatus=missing.status;
 }catch(e){report.errors.push(e.stack);process.exitCode=1;}
 fs.writeFileSync(path.join(out,'production-verification.json'),JSON.stringify(report,null,2));
 if(!report.errors.length){const p=path.join(out,'published-links.csv');fs.writeFileSync(p,fs.readFileSync(p,'utf8').replaceAll('Built and locally checked; production verification pending','Verified live HTTP200 and reviewed output hash; indexing unverified'));const s=path.join(out,'release-summary.json'),v=JSON.parse(fs.readFileSync(s));v.deployment={revision,status:'Verified production HTTP and immutable assets',verifiedPages:report.pages.length,indexing:'Unverified'};fs.writeFileSync(s,JSON.stringify(v,null,2));}
 console.log(JSON.stringify({revision,pages:report.pages.length,assets:report.assets.length,sitemap:report.sitemap,errors:report.errors}));
})().catch(e=>{console.error(e);process.exitCode=1;});
