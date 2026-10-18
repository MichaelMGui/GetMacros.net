/* Bounded HTTP/metadata verification; these are not visual inspection claims. */
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'docs/global-coverage-2026-10-17');
const paths=fs.readdirSync(root).filter(p=>p.endsWith('.html'));
for(const name of fs.readdirSync(root)){if(/^[a-z]{2}$/.test(name)&&fs.existsSync(path.join(root,name,'en'))){for(const p of fs.readdirSync(path.join(root,name,'en'),{recursive:true}))if(p.endsWith('.html'))paths.push(name+'/en/'+p.replaceAll('\\','/'));}}
const hash=s=>crypto.createHash('sha256').update(s.replaceAll('\r\n','\n')).digest('hex');
const metadata=s=>({title:s.match(/<title>(.*?)<\/title>/s)?.[1],canonical:s.match(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"/)?.[1]});
(async()=>{
 const checked=[],failures=[];let cursor=0;
 await Promise.all(Array.from({length:6},async()=>{while(cursor<paths.length){const file=paths[cursor++],route=file==='index.html'?'/':file.endsWith('/index.html')?'/'+file.slice(0,-10):'/'+file,url='https://getmacros.net'+route;
  try{const response=await fetch(url,{headers:{'User-Agent':'GetMacros-release-route-check','Cache-Control':'no-cache'},signal:AbortSignal.timeout(30000)}),remote=await response.text(),local=fs.readFileSync(path.join(root,file),'utf8');assert.equal(response.status,200);assert.deepEqual(metadata(remote),metadata(local));checked.push({url,status:response.status,metadataMatch:true,bodyMatch:hash(remote)===hash(local)});}catch(error){failures.push({url,error:error.message});}
 }}));
 const missing=await fetch('https://getmacros.net/__getmacros_release_missing_20261017',{signal:AbortSignal.timeout(30000)});assert.equal(missing.status,404,'Unknown route must return real404');
 const result={checkedAt:new Date().toISOString(),pass:failures.length===0,checked:checked.length,expected:paths.length,bodyMatches:checked.filter(p=>p.bodyMatch).length,missingRouteStatus:missing.status,failures,routes:checked.sort((a,b)=>a.url.localeCompare(b.url)),scope:'HTTP and source metadata; not screenshot or accessibility inspection'};
 fs.writeFileSync(path.join(out,'production-all-routes.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,routes:undefined},null,2));assert.equal(failures.length,0);
})().catch(error=>{console.error(error);process.exitCode=1});
