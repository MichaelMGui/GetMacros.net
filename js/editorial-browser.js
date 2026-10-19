/* The complete link collection is crawlable HTML; filtering is a local enhancement. */
(()=>{'use strict';const root=document.querySelector('.reader-library');if(!root)return;
const groups=[...root.querySelectorAll('[data-reader-group]')],query=root.querySelector('[data-reader-search]'),status=root.querySelector('[data-reader-status]'),choices=[...root.querySelectorAll('[data-reader-topic]')];let topic='all';
const counts=new WeakMap();groups.forEach(g=>{counts.set(g,4);g.querySelector('[data-reader-more]').addEventListener('click',()=>{counts.set(g,counts.get(g)+8);render();});});
function render(){const term=query.value.trim().normalize('NFKD').replace(/\p{Diacritic}/gu,'').toLowerCase();let total=0;groups.forEach(g=>{const stories=[...g.querySelectorAll('.reader-story')],matches=stories.filter(a=>!term||a.textContent.normalize('NFKD').replace(/\p{Diacritic}/gu,'').toLowerCase().includes(term)),inTopic=topic==='all'||topic===g.id,limit=term?Infinity:counts.get(g);g.hidden=!inTopic||!matches.length;stories.forEach(a=>a.hidden=!matches.includes(a)||matches.indexOf(a)>=limit);g.querySelector('[data-reader-more]').hidden=!inTopic||matches.length<=limit;if(inTopic)total+=matches.length;});choices.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.readerTopic===topic)));status.textContent=term?total+' matching '+(total===1?'story':'stories'):'';root.querySelector('[data-reader-empty]').hidden=total>0;}
choices.forEach(b=>b.addEventListener('click',()=>{topic=b.dataset.readerTopic;render();window.GetMacrosMotion?.feedback(b);}));query.addEventListener('input',render);
function hash(){if(groups.some(g=>g.id===location.hash.slice(1))){topic=location.hash.slice(1);render();}}
addEventListener('hashchange',hash);hash();render();
})();
