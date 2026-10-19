/* Contract tests for the existing provider-free events and disabled ad adapter. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');

class Element{
 constructor(){this.hidden=false;this.dataset={adPlacement:'article-after-content'};this.children=[];this.attributes={};}
 replaceChildren(...children){this.children=children;}
 removeAttribute(name){delete this.attributes[name];if(name==='data-ad-state')delete this.dataset.adState;}
 append(...children){this.children.push(...children);}
}
function environment(){
 const slot=new Element(),listeners=new Map(),events=[];
 const document={querySelectorAll:s=>s==='[data-ad-placement]'?[slot]:[],createElement:()=>new Element(),
  addEventListener:(name,fn)=>listeners.set(name,fn),querySelector:()=>null,dispatchEvent:e=>events.push(e)};
 const context={document,HTMLElement:Element,setTimeout,clearTimeout,CustomEvent:class{constructor(type,options){this.type=type;Object.assign(this,options);}}};
 context.window=context;vm.createContext(context);return {context,slot,listeners,events};
}
function load(env,name){vm.runInContext(fs.readFileSync(path.join(root,'js',name),'utf8'),env.context,{filename:name});}
const settle=()=>new Promise(resolve=>setImmediate(resolve));

test('advertising never invokes an adapter by default, while disabled, or without affirmative consent',async()=>{
 const e=environment();let calls=0;load(e,'ad-placements.js');
 assert.equal(e.slot.hidden,true);assert.equal(e.slot.children.length,0);
 e.context.GetMacrosAdvertising.configure({adapter:()=>{calls++;return new Element();}});await settle();assert.equal(calls,0);
 e.context.GetMacrosAdvertising.configure({enabled:true,consent:'denied'});await settle();assert.equal(calls,0);
 e.context.GetMacrosAdvertising.configure({consent:'unknown'});await settle();assert.equal(calls,0);
 assert.equal(e.slot.hidden,true);
});
test('authorized ad adapter receives only placement and revoking consent removes its output',async()=>{
 const e=environment();let payload;load(e,'ad-placements.js');
 e.context.GetMacrosAdvertising.configure({enabled:true,consent:'granted',adapter:data=>{payload=data;return new Element();}});
 await settle();assert.equal(e.slot.dataset.adState,'filled');assert.equal(e.slot.hidden,false);
 assert.deepEqual(Object.keys(payload),['placement']);assert.equal(payload.placement,'article-after-content');
 e.context.GetMacrosAdvertising.configure({consent:'denied'});await settle();assert.equal(e.slot.hidden,true);assert.equal(e.slot.children.length,0);
});
test('a pending response cannot refill an ad slot after advertising is disabled',async()=>{
 const e=environment();let resolve;load(e,'ad-placements.js');
 e.context.GetMacrosAdvertising.configure({enabled:true,consent:'granted',adapter:()=>new Promise(r=>resolve=r)});
 e.context.GetMacrosAdvertising.disable();resolve(new Element());await settle();assert.equal(e.slot.hidden,true);assert.equal(e.slot.children.length,0);
});
test('provider-free product events discard unknown events and never include caller data',()=>{
 const e=environment();load(e,'product-events.js');
 e.context.GetMacrosEvents.emit('food_diary', {note:'private',weight:70});assert.equal(e.events.length,0);
 e.context.GetMacrosEvents.emit('calculator_completed',{weight:70,calories:2000});assert.equal(e.events.length,1);
 assert.equal(e.events[0].type,'getmacros:product-event');assert.deepEqual(Object.keys(e.events[0].detail),['name','version']);
 assert.equal(e.events[0].detail.name,'calculator_completed');assert.equal(e.events[0].detail.version,1);
});
