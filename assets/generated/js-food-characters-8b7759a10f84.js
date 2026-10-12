/* Original SVG character enhancement; static art stays visible without JavaScript. */
(()=>{'use strict';
const sprite=new URL(document.querySelector('use[href*="food-characters.svg"]')?.getAttribute('href')?.split('#')[0]||'/images/food-characters.svg',location.href).href;
const characters=Object.freeze({potato:{name:'Potato',motion:'blink',greeting:'Hello!'},tomato:{name:'Tomato',motion:'nod',greeting:'Hi!'},steak:{name:'Steak',motion:'wave',greeting:'Hi!'},chicken:{name:'Chicken',motion:'nod',greeting:'Hello!'},salmon:{name:'Salmon',motion:'blink',greeting:'Hi!'},shrimp:{name:'Shrimp',motion:'leaf',greeting:'Hey!'},egg:{name:'Egg',motion:'blink',greeting:'Hello!'},tofu:{name:'Tofu',motion:'wave',greeting:'Hi!'},beans:{name:'Beans',motion:'nod',greeting:'Hey!'},apple:{name:'Apple',motion:'leaf',greeting:'Hi!'},banana:{name:'Banana',motion:'nod',greeting:'Hello!'},strawberry:{name:'Strawberry',motion:'leaf',greeting:'Hey!'},orange:{name:'Orange',motion:'leaf',greeting:'Hello!'},blueberry:{name:'Blueberry',motion:'blink',greeting:'Hi!'},avocado:{name:'Avocado',motion:'wave',greeting:'Hello!'},carrot:{name:'Carrot',motion:'leaf',greeting:'Hey!'},broccoli:{name:'Broccoli',motion:'leaf',greeting:'Hi!'},pear:{name:'Pear',motion:'leaf',greeting:'Hello!'}});
let serial=0,symbols;const poses=new WeakMap();
function inlineArt(svg,id){
 if(!symbols)symbols=fetch(sprite,{credentials:'same-origin'}).then(r=>{if(!r.ok)throw Error('Character artwork unavailable');return r.text();}).then(s=>new DOMParser().parseFromString(s,'image/svg+xml')).catch(()=>null);
 symbols.then(doc=>{const symbol=doc?.getElementById('food-'+id);if(symbol){svg.replaceChildren(...Array.from(symbol.childNodes,n=>document.importNode(n,true)));}});
}
function enhance(root=document){
 const hosts=[...(root.matches?.('[data-food-character]')?[root]:[]),...root.querySelectorAll('[data-food-character]')];
 hosts.forEach(host=>{
  if(host.dataset.foodReady)return;
  const id=host.dataset.foodCharacter,character=characters[id];if(!character)return;
  host.dataset.foodReady='true';host.classList.add('food-character');host.dataset.motion=character.motion;
  const interactive=host.dataset.interactive==='true';host.dataset.interactive=String(interactive);
  let svg=host.querySelector('svg');if(!svg){svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 160 160');const use=document.createElementNS('http://www.w3.org/2000/svg','use');use.setAttribute('href',sprite+'#food-'+id);svg.append(use);host.append(svg);}
  svg.classList.add('food-character-art');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');
  inlineArt(svg,id);
  if(!interactive){host.setAttribute('aria-hidden','true');return;}
  host.removeAttribute('aria-hidden');
  const button=document.createElement('button');button.type='button';button.className='food-character-trigger';button.setAttribute('aria-label',character.name+' character: show greeting');button.setAttribute('aria-expanded','false');svg.replaceWith(button);button.append(svg);
  const bubble=document.createElement('span');bubble.className='food-character-greeting';bubble.id='food-greeting-'+(++serial);bubble.setAttribute('role','tooltip');bubble.textContent=host.dataset.greeting||character.greeting;host.append(bubble);
  let hovered=false,pinned=false,suppressed=false;
  const show=()=>{if(suppressed)return;host.dataset.pose='greeting';host.classList.add('is-greeting');button.setAttribute('aria-expanded','true');button.setAttribute('aria-describedby',bubble.id);};
  const hide=()=>{host.dataset.pose='rest';host.classList.remove('is-greeting');button.setAttribute('aria-expanded','false');button.removeAttribute('aria-describedby');};
  poses.set(host,pose=>{pinned=pose==='greeting';suppressed=!pinned;if(pinned)show();else hide();});
  host.addEventListener('pointerenter',e=>{if(e.pointerType==='touch')return;hovered=true;show();});
  host.addEventListener('pointerleave',e=>{if(e.pointerType==='touch')return;hovered=false;suppressed=false;if(!pinned&&document.activeElement!==button)hide();});
  button.addEventListener('focus',()=>{suppressed=false;show();});
  button.addEventListener('blur',()=>{pinned=false;suppressed=false;if(!hovered)hide();});
  button.addEventListener('click',()=>{pinned=!pinned;suppressed=!pinned;if(pinned)show();else hide();});
  document.addEventListener('pointerdown',e=>{if(!host.contains(e.target)){pinned=false;if(!hovered){suppressed=true;hide();}}});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&host.classList.contains('is-greeting')){pinned=false;suppressed=true;hide();}});
  inlineArt(svg,id);if(host.dataset.pose==='greeting')poses.get(host)('greeting');
 });
}
function create(id,{interactive=false,size=112,greeting='',pose='rest'}={}){
 if(!characters[id])throw new RangeError('Unknown GetMacros food character: '+id);
 const host=document.createElement('span');host.dataset.foodCharacter=id;host.dataset.interactive=String(Boolean(interactive));host.dataset.pose=pose;host.style.setProperty('--food-size',Math.max(40,Math.min(240,Number(size)||112))+'px');if(greeting)host.dataset.greeting=String(greeting);enhance(host);return host;
}
function setPose(host,pose='rest'){if(!['rest','greeting'].includes(pose))throw new RangeError('Unsupported food character pose');poses.get(host)?.(pose);}
function respond(type,scope=document){if(document.documentElement.dataset.motion==='calm'||matchMedia('(prefers-reduced-motion: reduce)').matches)return;scope.querySelectorAll('.food-character').forEach(host=>{const b=host.getBoundingClientRect();if(b.top<innerHeight&&b.bottom>0){host.classList.remove('is-reacting');void host.offsetWidth;host.classList.add('is-reacting');setTimeout(()=>host.classList.remove('is-reacting'),700);}});}
window.GetMacrosCharacters=Object.freeze({characters,create,enhance,setPose,respond});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>enhance(),{once:true});else enhance();
})();
