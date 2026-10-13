'use strict';
const fs=require('node:fs/promises'),path=require('node:path'),crypto=require('node:crypto');
const {chromium}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const dir=path.resolve(__dirname,'../../docs/master-completion-2026-10-13/restaurant-sources');
(async()=>{
 const b=await chromium.launch({channel:'msedge',headless:true,args:['--no-proxy-server']}),c=await b.newContext({viewport:{width:1280,height:1000}}),p=await c.newPage(),responses=[];
 p.on('response',async r=>{const u=r.url();if(u.startsWith('https://order.wendys.com')&&!/\.(?:png|svg|webp|woff|css|js)(?:\?|$)/.test(u)){const type=r.headers()['content-type']||'';responses.push({url:u,status:r.status(),type});if(r.status()===200){try{const body=await r.body();const id=responses.length;await fs.writeFile(path.join(dir,'wendys-detail-response-'+id+'.txt'),body)}catch{}}}});
 await p.goto('https://order.wendys.com/ca/en/national/menu/combos/daves-single',{waitUntil:'domcontentloaded',timeout:45000});await p.waitForTimeout(2500);
 console.log('buttons',await p.getByRole('button').allTextContents());console.log('body',(await p.locator('body').innerText()).slice(-2500));
 const nut=p.getByText('Nutrition',{exact:true}).first();if(await nut.count()){await nut.click();await p.waitForTimeout(1000);}
 await fs.writeFile(path.join(dir,'wendys-detail.html'),await p.content());await fs.writeFile(path.join(dir,'wendys-detail.txt'),await p.locator('body').innerText());await p.screenshot({path:path.join(dir,'wendys-detail.png'),fullPage:true});await fs.writeFile(path.join(dir,'wendys-detail-requests.json'),JSON.stringify(responses,null,2));console.log('nutrition',(await p.locator('body').innerText()).slice(-5500));await b.close();
})().catch(e=>{console.error(e);process.exitCode=1});
