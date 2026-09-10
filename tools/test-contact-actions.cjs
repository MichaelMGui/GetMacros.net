const assert=require('node:assert/strict');
const {chromium,webkit}=require('C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {localAssets}=require('./browser-fixture.cjs');
(async()=>{for(const engine of [chromium,webkit]){const b=await engine.launch(engine===chromium?{channel:'msedge'}:{});try{for(const theme of ['light','dark']){
 process.env.GM_TEST_THEME=theme;const p=await b.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});await localAssets(p);
 await p.addInitScript(()=>Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.copiedContactText=text;}}}));
 await p.goto('http://127.0.0.1:4174/contact.html');
 assert.ok((await p.locator('.site-header').boundingBox()).y<2,'No invisible graphic above navigation');
 for(const [topic,subject] of [['problem','Something to fix on GetMacros'],['idea','An idea for GetMacros']]){
  await p.locator('[data-contact-topic="'+topic+'"]').click();assert.equal(await p.locator('#contact-topic').inputValue(),topic);
  assert.equal(await p.locator('#contact-message').evaluate(e=>e===document.activeElement),true);
  await p.locator('#contact-message').fill('A page & button problem\nPlease check the link.');
  for(const provider of ['gmail','outlook']){
   const link=p.locator('#contact-form [data-webmail="'+provider+'"]');const url=new URL(await link.getAttribute('href'));
   assert.equal(url.hostname,provider==='gmail'?'mail.google.com':'outlook.live.com');assert.equal(url.searchParams.get('to'),'getmacros.net@outlook.com');assert.equal(url.searchParams.get(provider==='gmail'?'su':'subject'),subject);assert.equal(url.searchParams.get('body'),'A page & button problem\nPlease check the link.');assert.equal(await link.getAttribute('target'),'_blank');
  }
  const draft=new URL(await p.locator('#contact-email-draft').getAttribute('href'));
  assert.equal(draft.protocol,'mailto:');assert.equal(draft.pathname,'getmacros.net@outlook.com');assert.equal(draft.searchParams.get('subject'),subject);
  assert.equal(draft.searchParams.get('body'),'A page & button problem\nPlease check the link.');
  await p.locator('[data-copy-message]').click();assert.ok((await p.evaluate(()=>window.copiedContactText)).includes(subject));
 }
 for(const provider of ['gmail','outlook']){
  await p.context().route(provider==='gmail'?'https://mail.google.com/**':'https://outlook.live.com/**',route=>route.fulfill({contentType:'text/html',body:'<title>Mail draft test</title>'}));
  const popupEvent=p.waitForEvent('popup');await p.locator('#contact-form [data-webmail="'+provider+'"]').click();const popup=await popupEvent;await popup.waitForLoadState();assert.equal(new URL(popup.url()).searchParams.get('to'),'getmacros.net@outlook.com');await popup.close();
 }
 await p.locator('[data-copy-address]').click();assert.equal(await p.evaluate(()=>window.copiedContactText),'getmacros.net@outlook.com');
 await p.evaluate(()=>navigator.clipboard.writeText=async()=>{throw Error('denied')});await p.locator('[data-copy-message]').click();
 assert.ok(await p.locator('#contact-copy-fallback').isVisible());assert.ok((await p.locator('#contact-copy-text').inputValue()).includes('To: getmacros.net@outlook.com'));
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 await p.screenshot({path:`design/contact-working-${engine.name()}-${theme}.png`});
 console.log('PASS',engine.name(),theme,'contact topics, draft URL, copy and denied-clipboard fallback');await p.close();
 }}finally{await b.close()}}})().catch(e=>{console.error(e);process.exitCode=1});
