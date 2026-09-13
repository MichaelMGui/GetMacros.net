const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
function run(reduced){
const events={},animations=[],values=new Map();
const element=()=>({style:{},classList:{toggle(){},add(){}},setAttribute(){},append(){},remove(){},getBoundingClientRect(){return{left:0,top:0,width:100,height:40}},addEventListener(name,fn){events[name]=fn},animate(){const a={cancelled:false,cancel(){this.cancelled=true},finished:new Promise(()=>{})};animations.push(a);return a}});
const button=element(),preference={matches:reduced,addEventListener(name,fn){this.change=fn}};
vm.runInNewContext(fs.readFileSync('js/tide-motion.js','utf8'),{window:{},document:{documentElement:element(),createElement:()=>button,querySelector:()=>element(),addEventListener(name,fn){events['document:'+name]=fn}},matchMedia:q=>q.includes('reduced')?preference:{matches:true},localStorage:{getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v)},setTimeout});
const target={closest:()=>button};const pointer=(pointerType,x=10)=>events['document:pointerdown']({target,pointerId:1,pointerType,clientX:x,clientY:10});
pointer('touch');assert.equal(animations.length,0,'Swiping from a button must not start an animation');
events['document:pointermove']({pointerId:1,clientX:100,clientY:10});events['document:pointerup']({target,pointerId:1,clientX:10,clientY:10});assert.equal(animations.length,0);pointer('touch');events['document:pointerup']({target,pointerId:1,clientX:10,clientY:10});assert.equal(animations.length,reduced?0:1);
if(!reduced){events.click();assert.equal(values.get('gm-motion'),'paused');assert.ok(animations[0].cancelled);pointer('mouse');assert.equal(animations.length,1);events.click();assert.equal(values.get('gm-motion'),'enabled');preference.matches=true;preference.change();pointer('mouse');assert.equal(animations.length,1)}else assert.equal(button.disabled,true);
}
run(false);run(true);console.log('PASS: swipes stay native, tap feedback, pause cancellation and reduced-motion preference.');
