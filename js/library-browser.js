/* Progressive disclosure keeps every reading link in the document and works without JS. */
(function(){
'use strict';
var select=document.getElementById('reading-topic-select');
if(!select)return;
var groups=Array.from(document.querySelectorAll('[data-reading-topic]'));
var status=document.getElementById('reading-topic-status');
function show(id,announce,all){
 var active=groups.find(function(g){return g.id===id;})||groups[0];
 select.value=active.id;
 groups.forEach(function(g){
  g.hidden=g!==active;
  var links=Array.from(g.querySelectorAll('.library-read'));
  var visible=all?links.length:8;
  links.forEach(function(a,i){a.hidden=i>=visible;});
  var more=g.querySelector('[data-more-reads]');
  more.hidden=visible>=links.length;
  more.dataset.visible=String(visible);
 });
 if(announce)status.textContent=active.querySelector('h3').textContent+': '+active.querySelectorAll('.library-read').length+' reads.';
}
select.parentElement.hidden=false;
select.addEventListener('change',function(){show(select.value,true,false);});
groups.forEach(function(g){g.querySelector('[data-more-reads]').addEventListener('click',function(){
 var visible=Number(this.dataset.visible)+8;
 var links=Array.from(g.querySelectorAll('.library-read'));
 links.forEach(function(a,i){a.hidden=i>=visible;});
 this.dataset.visible=String(visible);
 if(visible>=links.length){this.hidden=true;links[Math.max(0,links.length-1)].focus();}
 status.textContent='Showing '+Math.min(visible,links.length)+' of '+links.length+' reads.';
});});
function hash(){var id=location.hash.slice(1);if(groups.some(function(g){return g.id===id;}))show(id,false,true);}
show(groups[0].id,false,false);hash();window.addEventListener('hashchange',hash);
})();
