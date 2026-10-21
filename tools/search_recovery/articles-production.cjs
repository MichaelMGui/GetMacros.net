/* Public crawl checks; these requests are synthetic verification traffic. */
const fs=require('fs'), assert=require('assert/strict');
const origin='https://getmacros.net';
const rows=JSON.parse(fs.readFileSync('docs/ultimate-release-2026-10-19/publication-manifest.json','utf8'));
assert.equal(rows.length,29);
const report={checkedAt:new Date().toISOString(),requestsAreSynthetic:true,articles:[],errors:[]};
async function read(route){const r=await fetch(origin+route,{redirect:'manual',headers:{'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'},signal:AbortSignal.timeout(40000)});return {r,text:await r.text()};}
function links(text,route){return [...text.matchAll(/<a\b[^>]*\bhref="([^"]+)"/g)].map(m=>new URL(m[1].replaceAll('&amp;','&'),origin+route)).filter(u=>u.origin===origin).map(u=>u.pathname);}
(async()=>{try{
 const [sitemap,home,index,robots]=await Promise.all(['/sitemap.xml','/','/articles.html','/robots.txt'].map(read));
 for(const p of [sitemap,home,index,robots])assert.equal(p.r.status,200);
 assert(links(home.text,'/').includes('/articles.html'),'Homepage must link to article index');
 assert(robots.text.includes('Sitemap: '+origin+'/sitemap.xml'));
 const indexLinks=links(index.text,'/articles.html');
 const queue=[...rows];
 await Promise.all(Array.from({length:3},async()=>{while(queue.length){const row=queue.shift(),url=origin+row.route,{r,text}=await read(row.route);
  const schemas=[...text.matchAll(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map(m=>JSON.parse(m[1]));
  const canonical=text.match(/<link[^>]*rel="canonical"[^>]*href="([^"]+)"/)?.[1];
  const item={url,status:r.status,canonical,indexable:!/<meta[^>]*name="robots"[^>]*content="[^"]*noindex/i.test(text)&&!/(?:^|[ ,])noindex\b/i.test(r.headers.get('x-robots-tag')||''),inSitemap:sitemap.text.includes('<loc>'+url+'</loc>'),linkedFromArticleIndex:indexLinks.includes(row.route),depthFromHome:2,h1Count:(text.match(/<h1\b/g)||[]).length,hasRenderedArticle:text.includes('class="editorial-story"'),hasSourcePanel:text.includes('id="article-sources"'),articleSchema:schemas.some(s=>s['@type']==='Article'&&s.mainEntityOfPage===url),title:text.match(/<title>(.*?)<\/title>/s)?.[1]};
  report.articles.push(item);
  assert.equal(item.status,200,url);assert.equal(canonical,url);for(const key of ['indexable','inSitemap','linkedFromArticleIndex','hasRenderedArticle','hasSourcePanel','articleSchema'])assert.equal(item[key],true,url+' '+key);assert.equal(item.h1Count,1,url);
 }}));
 report.articles.sort((a,b)=>a.url.localeCompare(b.url));
 assert.equal(new Set(report.articles.map(p=>p.title)).size,29,'Duplicate article titles');
 }catch(e){report.errors.push(e.stack);process.exitCode=1;}
 fs.writeFileSync('docs/search-recovery-2026-10-21/articles-production.json',JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({checked:report.articles.length,errors:report.errors}));
})().catch(e=>{console.error(e);process.exitCode=1});
