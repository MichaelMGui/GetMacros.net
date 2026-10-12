/* Check actual deployed bytes and workflow state for the diary release. */
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto'),cp=require('node:child_process');
const revision=process.argv[2],previous=process.argv[3],base='https://getmacros.net';assert(/^[a-f0-9]{40}$/.test(revision)&&/^[a-f0-9]{40}$/.test(previous),'Pass exact current and previous deployment revisions.');
const out=process.argv[4]||'docs/diary-more-2026-10-12',headers={'User-Agent':'GetMacros-diary-release-verification','Cache-Control':'no-cache'};
const hash=s=>crypto.createHash('sha256').update(s.replace(/\r\n/g,'\n')).digest('hex');
async function read(name){const r=await fetch(base+'/'+name+'?release='+revision,{headers,signal:AbortSignal.timeout(30000)});assert.equal(r.status,200,name);return r.text();}
(async()=>{
 const jobs=await fetch('https://api.github.com/repos/MichaelMGui/GetMacros.net/actions/runs?head_sha='+revision+'&per_page=10',{headers,signal:AbortSignal.timeout(30000)}).then(r=>r.json());
 const actions=jobs.workflow_runs?.map(r=>({name:r.name,status:r.status,conclusion:r.conclusion,url:r.html_url,headSha:r.head_sha}))||[];
 console.log(JSON.stringify({revision,actions}));
 const html=await read('food-diary.html'),catalogue=html.match(/data-diary-catalogue="([^"]+)"/)?.[1];
 assert(catalogue,'New food diary has not reached production yet.');
 assert.equal(catalogue,fs.readFileSync('food-diary.html','utf8').match(/data-diary-catalogue="([^"]+)"/)[1]);
 const map=JSON.parse(fs.readFileSync('assets/generated/manifest.json','utf8'));
 const changed=cp.execFileSync('git',['diff','--name-only',previous,revision],{cwd:'docs/master-release-2026-10-12/publisher',encoding:'utf8'}).trim().split('\n');
 const pages=changed.filter(p=>p.endsWith('.html')&&!/^(?:docs|tools)\//.test(p));
 const files=[...new Set([...pages,'assets/generated/manifest.json',...Object.values(map).map(r=>r.url.slice(1)),catalogue.slice(1),'sw.js'])];
 const report={revision,previous,verifiedAt:new Date().toISOString(),production:base,actions,sourceMatches:[],countries:['US','CA','MX','GB','IE','AU','NZ','JP']};
 let cursor=0;await Promise.all(Array.from({length:4},async()=>{while(cursor<files.length){const name=files[cursor++],text=await read(name),expected=fs.readFileSync(name,'utf8');assert.equal(hash(text),hash(expected),name+' differs from reviewed source');report.sourceMatches.push({path:name,httpStatus:200,sha256:hash(text)});}}));
 const data=JSON.parse(await read(catalogue.slice(1)));assert.equal(data.foodCount,JSON.parse(fs.readFileSync('.'+catalogue,'utf8')).foodCount);assert.equal(data.groups.length,12);
 assert(html.includes('<meta name="robots" content="noindex,follow">'));report.counts={updatedHtmlPages:pages.length,verifiedFiles:files.length,browsableFoods:data.foodCount,groups:data.groups.length};
 fs.writeFileSync(out+'/deployment-verification.json',JSON.stringify(report,null,2));console.log('PASS live: '+pages.length+' updated pages and '+files.length+' files match reviewed source; '+data.foodCount+' shared browse foods.');
})().catch(e=>{console.error(e.message);process.exitCode=1});
