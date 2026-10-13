/* Actual production responses, not a preview or a build-success assumption. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const revision=process.argv[2],base='https://getmacros.net',out='docs/master-completion-2026-10-13';
assert(/^[a-f0-9]{40}$/.test(revision),'Pass the exact published commit.');
const headers={'User-Agent':'GetMacros-release-verification','Cache-Control':'no-cache'};
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const textHash=bytes=>hash(Buffer.from(bytes.toString('utf8').replace(/\r\n/g,'\n')));
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
 const files=new Set([...pages,'assets/generated/manifest.json',...Object.values(assets).map(item=>item.url.slice(1)),'sitemap.xml','sw.js','js/search-index.json','data/restaurant-presence.json']);
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
 const list=[...files];let cursor=0;await Promise.all(Array.from({length:6},async()=>{while(cursor<list.length){const name=list[cursor++],body=await get(name),local=fs.readFileSync(name),binary=name.endsWith('.gz'),actual=binary?hash(body):textHash(body),expected=binary?hash(local):textHash(local);assert.equal(actual,expected,name+' differs from reviewed source');report.sourceMatches.push({path:name,httpStatus:200,sha256:actual});if(report.sourceMatches.length%100===0)console.log('Verified live files:',report.sourceMatches.length,'/',list.length);}}));
 const importer=JSON.parse(fs.readFileSync(out+'/grocery-integrity.json','utf8'));
 report.counts={htmlPages:pages.length,verifiedFiles:files.size,OFFProfiles:off.profileCount,OFFSourceProducts:importer.sourceProductsChecked,OFFVersion:off.version};
 fs.writeFileSync(out+'/deployment-verification.json',JSON.stringify(report,null,2));console.log(JSON.stringify({pass:true,revision,...report.counts,actions}));
})().catch(error=>{console.error(error);process.exitCode=1});
