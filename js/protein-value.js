(function(){
 'use strict';
 var ids=['ap','as','ag','bp','bs','bg'];
 function money(value){return new Intl.NumberFormat(undefined,{style:'currency',currency:'USD',minimumFractionDigits:2,maximumFractionDigits:4}).format(value);}
 function update(){
  var valid=ids.every(function(id){var el=document.getElementById(id);return el.value!==''&&el.checkValidity()&&Number.isFinite(Number(el.value));});
  var v=function(id){return Number(document.getElementById(id).value);};
  var aTotal=v('as')*v('ag'),bTotal=v('bs')*v('bg');
  valid=valid&&aTotal>0&&bTotal>0;
  var a=valid?v('ap')/aTotal:0,b=valid?v('bp')/bTotal:0;
  document.getElementById('ra').textContent=valid?money(a)+'/g':'—';
  document.getElementById('rb').textContent=valid?money(b)+'/g':'—';
  document.getElementById('ra25').textContent=valid?money(a*25)+' per 25 g':'— per 25 g';
  document.getElementById('rb25').textContent=valid?money(b*25)+' per 25 g':'— per 25 g';
  document.getElementById('winner').textContent=!valid?'Enter valid prices, serving counts and protein amounts for both foods.':(Math.abs(a-b)<1e-10?'Both foods cost the same per gram of protein.':(a<b?'Food A':'Food B')+' costs less per gram of protein in this comparison.')+' Price is one factor. Consider serving size, food preferences, allergies and the rest of the nutrition label too.';
 }
 ids.forEach(function(id){document.getElementById(id).addEventListener('input',update);});update();
}());
