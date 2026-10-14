/* Actual production responses, not a preview or a build-success assumption. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const revision=process.argv[2],base='https://getmacros.net',out='docs/clarity-release-2026-10-14';
assert(/^[a-f0-9]{40}$/.test(revision),'Pass the exact published commit.');
const headers={'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'};
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const textHash=bytes=>hash(Buffer.from(bytes.toString('utf8').replace(/\r\n/g,'\n')));
function reverseEmailProtection(body,local){
 const expected=new Set([...local.toString('utf8').matchAll(/href="mailto:([^"?]+)(?:\?[^\"]*)?"/g)].map(match=>match[1]));
 function decode(hex){assert(/^(?:[a-f0-9]{2})+$/i.test(hex));const bytes=Buffer.from(hex,'hex'),key=bytes[0];const email=new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(bytes.subarray(1),value=>value^key));assert(expected.has(email),'Hosting protection must decode to an unchanged source email');return email;}
 let text=body.toString('utf8');
 text=text.replace(/href="\/cdn-cgi\/l\/email-protection#([a-f0-9]+)"/gi,(_,hex)=>'href="mailto:'+decode(hex)+'"');
 text=text.replace(/<span class="__cf_email__" data-cfemail="([a-f0-9]+)">[\s\S]*?<\/span>/gi,(_,hex)=>decode(hex));
 text=text.replace(/<script data-cfasync="false" src="\/cdn-cgi\/scripts\/[a-f0-9]+\/cloudflare-static\/email-decode\.min\.js"><\/script>/gi,'');
 return Buffer.from(text);
}
async function get(name){const response=await fetch(base+'/'+name+'?release='+revision,{headers,signal:AbortSignal.timeout(45000)});assert.equal(response.status,200,name+' HTTP status');return Buffer.from(await response.arrayBuffer());}
(async()=>{
 const response=await fetch('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=20',{headers,signal:AbortSignal.timeout(30000)});assert.equal(response.status,200,'workflow API');
 const jobs=await response.json(),actions=jobs.workflow_runs.map(row=>({name:row.name,status:row.status,conclusion:row.conclusion,url:row.html_url,branch:row.head_branch,headSha:row.head_sha}));
 assert(actions.some(row=>row.name==='Site quality'),'Site quality run must exist');assert(actions.some(row=>row.name==='pages build and deployment'),'Pages deployment must exist');
 assert(actions.every(row=>row.status==='completed'&&row.conclusion==='success'),'All revision workflows must have completed successfully: '+JSON.stringify(actions));
 const pages=fs.readdirSync('.').filter(name=>name.endsWith('.html'));
 function walk(folder){for(const item of fs.readdirSync(folder,{withFileTypes:true})){const file=path.join(folder,item.name);if(item.isDirectory())walk(file);else if(item.name==='index.html')pages.push(file.replaceAll(path.sep,'/'));}}
 for(const market of ['ca','mx','gb','ie','au','nz','jp'])walk(market+'/en');
 const assets=JSON.parse(fs.readFileSync('assets/generated/manifest.json','utf8'));
 // Search records are rendered in search.html; no separate JSON search route exists.
 const files=new Set([...pages,'assets/generated/manifest.json',...Object.values(assets).map(item=>item.url.slice(1)),'sitemap.xml','sw.js','data/restaurant-presence.json']);
 const catalogue=fs.readFileSync('food-diary.html','utf8').match(/data-diary-catalogue="([^"]+)"/)[1];files.add(catalogue.slice(1));
 for(const source of ['off','usda','cnf','retailer-ca'])files.add('data/branded-foods/'+source+'/manifest.json');
 for(const market of ['US','CA','MX','GB','IE','AU','NZ','JP'])for(const kind of ['markets','brands'])files.add('data/branded-foods/off/'+kind+'/'+market+'.json');
 for(const name of ['RIGHTS.txt','normalization.py','quarantined.json','records.ndjson.gz','source-records.ndjson.gz'])files.add('data/branded-foods/off/'+name);
 const off=JSON.parse(fs.readFileSync('data/branded-foods/off/manifest.json','utf8'));
 for(const directory of ['records','tokens','barcodes','index']){
  const entries=fs.readdirSync('data/branded-foods/off/'+directory).filter(file=>file.endsWith('.json')).sort();
  for(const index of [0,Math.floor(entries.length/2),entries.length-1])files.add('data/branded-foods/off/'+directory+'/'+entries[index]);
 }
 const report={revision,verifiedAt:new Date().toISOString(),production:base,actions,scope:'All public HTML, all active immutable assets, current catalogues/manifests/market indexes, complete OFF licensed archives and representative record/token/barcode/metadata shards. Remaining individual static shards validated locally, not individually fetched live.',sourceMatches:[]};
 const list=[...files];for(const file of list)assert(fs.existsSync(file),'Verification inventory must come from a real local source file: '+file);
 const concurrency=Math.min(6,Math.max(1,Number(process.env.GM_LIVE_CONCURRENCY)||6));report.concurrency=concurrency;
 let cursor=0;await Promise.all(Array.from({length:concurrency},async()=>{while(cursor<list.length){const name=list[cursor++],body=await get(name),local=fs.readFileSync(name),binary=name.endsWith('.gz'),emailProtection=!binary&&(body.includes('data-cfemail=')||body.includes('/cdn-cgi/l/email-protection#')),checked=emailProtection?reverseEmailProtection(body,local):body,actual=binary?hash(checked):textHash(checked),expected=binary?hash(local):textHash(local);assert.equal(actual,expected,name+' differs from reviewed source');report.sourceMatches.push({path:name,httpStatus:200,sha256:actual,rawResponseSha256:hash(body),comparison:emailProtection?'Exact source after reversing only hosting email protection; decoded email must match source':binary?'Exact binary bytes':'Exact UTF-8 source after Git line-ending normalization'});if(report.sourceMatches.length%100===0)console.log('Verified live files:',report.sourceMatches.length,'/',list.length);}}));
 const importer=JSON.parse(fs.readFileSync('docs/master-completion-2026-10-13/grocery-integrity.json','utf8'));
 report.counts={htmlPages:pages.length,verifiedFiles:files.size,OFFProfiles:off.profileCount,OFFSourceProducts:importer.sourceProductsChecked,OFFVersion:off.version};
 fs.writeFileSync(out+'/deployment-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify({pass:true,revision,...report.counts,actions}));
})().catch(error=>{console.error(error);process.exitCode=1});
