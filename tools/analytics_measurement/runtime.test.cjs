/* Privacy and delivery contracts. This test never contacts Google. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const code=fs.readFileSync(path.resolve(__dirname,'../../js/analytics.js'),'utf8');
const ID='G-MWXSWP6ZGY', KEY='gm-analytics-consent-v1';
function env(options={}) {
 const elements=new Map(), scripts=[], writes=[], events={};
 function element(name) {
  const e={hidden:true,open:false,checked:false,dataset:{},listeners:{},textContent:'',
   addEventListener(type,fn){this.listeners[type]=fn;},click(){this.listeners.click?.({target:this});},
   showModal(){this.open=true;},close(){this.open=false;},querySelector(s){return elements.get(s);}};
  elements.set(name,e);return e;
 }
 for(const name of ['[data-analytics-notice]','#analytics-preferences','[data-analytics-status]','[data-analytics-exclude]','[data-analytics-diagnostic]','[data-analytics-error]','[data-analytics-close]','preferences','allow','deny']) element(name);
 elements.get('allow').dataset.analyticsChoice='granted';elements.get('deny').dataset.analyticsChoice='denied';
 const store=new Map(options.stored ? [[KEY,JSON.stringify(options.stored)]]:[]);
 const location={hostname:'getmacros.net',origin:'https://getmacros.net',pathname:'/articles.html',search:'',hash:'',reload(){this.reloads=(this.reloads||0)+1;},...options.location};
 const document={body:{dataset:{analyticsPage:options.scope||'public'}},title:'Public title',referrer:'https://example.org/private?health=CANARY#notes',
  cookie:'_ga=one; _ga_MWXSWP6ZGY=two; diary=keep',head:{append:s=>scripts.push(s)},
  createElement:()=>({dataset:{}}),querySelector:s=>s==='link[rel="canonical"]'?{href:'https://getmacros.net/articles.html'}:s==='meta[property="og:title"]'?{content:'Static title'}:elements.get(s),
  addEventListener:(name,fn)=>{events['document:'+name]=fn;},
  querySelectorAll:s=>s==='[data-analytics-choice]'?[elements.get('allow'),elements.get('deny')]:s==='[data-analytics-preferences]'?[elements.get('preferences')]:[]};
 const localStorage={getItem:k=>{if(options.blockedStorage)throw Error();return store.get(k)||null;},setItem:(k,v)=>{if(options.blockedStorage)throw Error();writes.push(k);store.set(k,v);}};
 const context={document,location,localStorage,navigator:{webdriver:false,...options.navigator},URL,Date,console,addEventListener:(type,fn)=>{events[type]=fn;}};
 context.window=context;vm.createContext(context);
 const run=()=>vm.runInContext(code,context);run();
 return {context,document,elements,scripts,writes,events,location,run,commands:()=>Array.from(context.dataLayer||[],x=>Array.from(x))};
}
test('no Google script, data layer or storage write before consent, and denial stays off',()=>{
 const e=env();assert.equal(e.scripts.length,0);assert.equal(e.context.dataLayer,undefined);assert.deepEqual(e.writes,[]);
 assert.equal(e.elements.get('[data-analytics-notice]').hidden,false);
 e.elements.get('deny').click();assert.equal(e.scripts.length,0);assert.equal(e.context.dataLayer,undefined);
 const denied=env({stored:{choice:'denied',excluded:false}});assert.equal(denied.scripts.length,0);
});
test('explicit grant loads the verified property once with clean metadata and advertising denied',()=>{
 const e=env();e.elements.get('allow').click();e.elements.get('allow').click();e.run();
 assert.equal(e.scripts.length,1);assert.equal(e.scripts[0].src,'https://www.googletagmanager.com/gtag/js?id='+ID);
 assert.equal(e.scripts[0].referrerPolicy,'no-referrer');
 const commands=e.commands(), config=commands.find(x=>x[0]==='config');
 assert.equal(config[1],ID);assert.equal(config[2].send_page_view,false);
 assert.equal(config[2].allow_google_signals,false);assert.equal(config[2].allow_ad_personalization_signals,false);
 assert.equal(config[2].cookie_expires,7776000);
 const views=commands.filter(x=>x[0]==='event');assert.equal(views.length,1);assert.equal(views[0][1],'page_view');
 assert.equal(views[0][2].page_referrer,'https://example.org/');assert.equal(views[0][2].page_location,'https://getmacros.net/articles.html');
 assert.equal(views[0][2].page_title,'Static title');assert.ok(!JSON.stringify(commands).includes('CANARY'));
 assert.equal(commands[0][2].ad_storage,'denied');assert.equal(commands[0][2].ad_user_data,'denied');assert.equal(commands[0][2].ad_personalization,'denied');
});
test('saved consent works, while private tools, previews and automated browsers remain unmeasured',()=>{
 const stored={choice:'granted',excluded:false};assert.equal(env({stored}).scripts.length,1);
 for(const options of [{scope:'private'},{location:{hostname:'localhost'}},{location:{hostname:'preview.example'}},{navigator:{webdriver:true}},{navigator:{globalPrivacyControl:true}},{stored:{choice:'granted',excluded:true}}]) {
  const e=env({stored,...options});assert.equal(e.scripts.length,0,JSON.stringify(options));assert.equal(e.context.dataLayer,undefined);
 }
});
test('market, campaign and anchor URLs retain visits while discarding all parameter values',()=>{
 for(const location of [{search:'?market=CA'},{search:'?utm_source=google&utm_campaign=PRIVATE_CANARY'},{search:'?q=PRIVATE_CANARY',hash:'#PRIVATE_CANARY'}]) {
  const e=env({stored:{choice:'granted'},location});assert.equal(e.scripts.length,1);
  const commands=e.commands();assert.ok(!JSON.stringify(commands).includes('PRIVATE_CANARY'));
  const config=commands.find(c=>c[0]==='config');assert.equal(config[2].page_location,'https://getmacros.net/articles.html');
  assert.equal(config[2].gm_traffic_class,'standard');assert.equal(config[2].debug_mode,undefined);assert.equal(config[2].cookie_prefix,undefined);
  assert.equal(commands[0][2].analytics_storage,'granted');
 }
});
test('diagnostics use separate cookies, internal/debug markers and unmistakable report titles',()=>{
 const e=env({stored:{choice:'granted',diagnostic:true}});const config=e.commands().find(c=>c[0]==='config');
 assert.equal(config[2].cookie_prefix,'gm_qa');assert.equal(config[2].debug_mode,true);assert.equal(config[2].traffic_type,'internal');
 const view=e.commands().find(c=>c[0]==='event');assert.equal(view[2].gm_traffic_class,'diagnostic');assert.equal(view[2].page_title,'[Diagnostic] Static title');
 assert.equal(view[2].traffic_type,'internal');
 e.elements.get('[data-analytics-diagnostic]').checked=false;e.elements.get('allow').click();assert.equal(e.location.reloads,1);
});
test('trusted navigation clicks send only fixed categories, never URL/query/food values',()=>{
 const e=env({stored:{choice:'granted'}});
 const link={href:'https://getmacros.net/restaurant-meal-finder.html?chain=PRIVATE_CANARY&maxCal=PRIVATE_CANARY',closest:s=>s==='header'?{}:null};
 const event={isTrusted:true,button:0,target:{closest:()=>link}};
 e.events['document:click'](event);
 const click=e.commands().filter(c=>c[0]==='event').at(-1);assert.equal(click[1],'navigation_click');assert.equal(click[2].destination,'finder');assert.equal(click[2].link_area,'header');
 assert.ok(!JSON.stringify(click).includes('PRIVATE_CANARY'));assert.equal(click[2].link_url,undefined);
 const before=e.commands().length;e.events['document:click']({...event,isTrusted:false});assert.equal(e.commands().length,before);
 e.elements.get('deny').click();e.events['document:click'](event);assert.equal(e.commands().length,before);
});
test('unavailable storage does not silently grant permission',()=>{
 const e=env({blockedStorage:true});e.elements.get('allow').click();assert.equal(e.scripts.length,0);assert.ok(e.elements.get('[data-analytics-error]').textContent.includes('stays off'));
});
test('withdrawal disables the loaded property and unloads it without sending denied pings',()=>{
 const e=env({stored:{choice:'granted',excluded:false}}),before=e.commands().length;
 e.elements.get('deny').click();assert.equal(e.context['ga-disable-'+ID],true);assert.equal(e.location.reloads,1);assert.equal(e.commands().length,before);
 assert.ok(e.document.cookie.includes('Max-Age=0'));assert.ok(!e.document.cookie.startsWith('diary='));
});
test('browser exclusion and revocation in another tab stop measurement',()=>{
 const e=env({stored:{choice:'granted',excluded:false}});e.elements.get('[data-analytics-exclude]').checked=true;e.elements.get('allow').click();assert.equal(e.location.reloads,1);
 const other=env({stored:{choice:'granted',excluded:false}});other.events.storage({key:KEY,newValue:JSON.stringify({choice:'denied',excluded:false})});
 assert.equal(other.context['ga-disable-'+ID],true);assert.equal(other.location.reloads,1);
});
