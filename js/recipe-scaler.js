(function () {
 'use strict';
 var inputs=['orig','nextServ','cal','pro','carb','fat'];
 var outputs=['rCal','rPro','rCarb','rFat'];
 var mode=document.getElementById('recipe-mode');
 var note=document.getElementById('factor');
 function update() {
  var valid=inputs.every(function(id){var el=document.getElementById(id);return el.value.trim()!==''&&el.checkValidity()&&Number.isFinite(Number(el.value));});
  if(!valid){outputs.forEach(function(id){document.getElementById(id).textContent='—';});note.textContent='Enter valid nutrition values and a serving count greater than zero to see your result.';return;}
  var original=Number(document.getElementById('orig').value),next=Number(document.getElementById('nextServ').value);
  var scale=mode.value==='scale';
  var factor=scale?1:original/next;
  outputs.forEach(function(id,index){var value=Number(document.getElementById(inputs[index+2]).value)*factor;document.getElementById(id).textContent=index===0?Math.round(value).toLocaleString():value.toFixed(1);});
  note.textContent=scale?'Multiply every ingredient by '+(next/original).toFixed(2)+'× to make '+next+' servings of the original size. Nutrition per serving stays the same.':'Keep the ingredients unchanged. Divide the original batch into '+next+' equal portions; each contains '+(original/next).toFixed(2)+'× the original serving’s nutrition.';
 }
 inputs.forEach(function(id){document.getElementById(id).addEventListener('input',update);});
 mode.addEventListener('change',update);update();
}());
