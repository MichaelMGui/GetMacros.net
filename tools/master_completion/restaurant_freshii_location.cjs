'use strict';
const fs=require('node:fs/promises'),path=require('node:path');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir=path.resolve(__dirname,'../../docs/master-completion-2026-10-13/restaurant-sources');
(async()=>{
 const b=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']}),c=await b.newContext({viewport:{width:1280,height:900}}),p=await c.newPage(),requests=[],pending=[];
 p.on('response',r=>{const u=r.url();if(u.startsWith('https://orders.freshii.com')&&!u.includes('/api/guest')&&/json/i.test(r.headers()['content-type']||'')){const index=requests.length;requests.push({url:u.split('?')[0],status:r.status()});pending.push((async()=>{try{const body=await r.body();if(r.status()===200)await fs.writeFile(path.join(dir,'freshii-location-response-'+index+'.json'),body)}catch{}})());}});
 try{await p.goto('https://orders.freshii.com/4722/flow/pickup',{waitUntil:'domcontentloaded',timeout:45000});await p.waitForTimeout(7000);await fs.writeFile(path.join(dir,'freshii-location.txt'),await p.locator('body').innerText());await fs.writeFile(path.join(dir,'freshii-location.html'),await p.content());await p.screenshot({path:path.join(dir,'freshii-location.png'),fullPage:true});console.log((await p.locator('body').innerText()).slice(0,6500));}catch(e){console.log(String(e));}
 await Promise.allSettled(pending);await fs.writeFile(path.join(dir,'freshii-location-requests.json'),JSON.stringify(requests,null,2));console.log(requests);await b.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
