(function(){
 'use strict';
 var ids=['ap','as','ag','bp','bs','bg'];
 function money(value,digits){return new Intl.NumberFormat(undefined,{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:digits||4}).format(value);}
 function update(){
  var valid=ids.every(function(id){var el=document.getElementById(id);return el.value!==''&&el.checkValidity()&&Number.isFinite(Number(el.value));});
  var v=function(id){return Number(document.getElementById(id).value);};
  var aTotal=v('as')*v('ag'),bTotal=v('bs')*v('bg');
  valid=valid&&aTotal>0&&bTotal>0;
  var a=valid?v('ap')/aTotal:0,b=valid?v('bp')/bTotal:0;
  document.getElementById('ra').textContent=valid?money(a)+'/g':'—';
  document.getElementById('rb').textContent=valid?money(b)+'/g':'—';
  document.getElementById('ra25').textContent=valid?money(a*25,2)+' per 25 g':'— per 25 g';
  document.getElementById('rb25').textContent=valid?money(b*25,2)+' per 25 g':'— per 25 g';
  document.getElementById('winner').textContent=!valid?'Fill in the price, servings and protein for both foods.':(Math.abs(a-b)<1e-10?'Both foods cost the same per gram of protein.':(a<b?'Food A':'Food B')+' gives you more protein for your money.');
 }
 ids.forEach(function(id){document.getElementById(id).addEventListener('input',update);});update();
}());
