(function(){
 'use strict';
 var form=document.getElementById('compareForm'), basis=document.getElementById('compare-basis');
 var fields=['serv','cal','pro','fib','sug','sod'];
 var read=function(s){var food={name:document.getElementById('name'+s).value.trim()||'Food '+s};fields.forEach(function(k){var el=document.getElementById(k+s);food[k]=el.value.trim()===''?NaN:Number(el.value);});return food;};
 function valid(f){return fields.every(function(k){return Number.isFinite(f[k])&&f[k]>=(k==='serv'||k==='cal'?0.1:0);});}
 function render(event){
  if(event)event.preventDefault();
  var a=read('A'),b=read('B'),out=document.getElementById('results'),error=document.getElementById('error');
  if(!valid(a)||!valid(b)){error.textContent='Fill in both labels. Serving size and calories must be above zero; other nutrients can be zero.';out.hidden=true;return;}
  error.textContent='';out.hidden=false;
  document.getElementById('headA').textContent=a.name;document.getElementById('headB').textContent=b.name;
  var factor=function(f){return basis.value==='weight'?100/f.serv:basis.value==='calories'?100/f.cal:1;};
  var context=document.getElementById('comparison-note');
  if(context)context.textContent=basis.value==='weight'?'Both foods are shown for 100 g.':basis.value==='calories'?'Both foods are shown for 100 calories; the weights may differ.':'The label servings are '+a.serv+' g and '+b.serv+' g. Choose equal weight to compare the same amount.';
  var rows=[['serv','Portion','g'],['cal','Calories','kcal'],['pro','Protein','g'],['fib','Fiber','g'],['sug','Added sugar','g'],['sod','Sodium','mg']];
  document.getElementById('resultRows').innerHTML=rows.map(function(row){var digits=row[0]==='cal'||row[0]==='sod'?0:1;return '<tr><th scope="row">'+row[1]+'</th><td>'+(a[row[0]]*factor(a)).toFixed(digits)+' '+row[2]+'</td><td>'+(b[row[0]]*factor(b)).toFixed(digits)+' '+row[2]+'</td></tr>';}).join('');
 }
 form.addEventListener('submit',render);form.addEventListener('reset',function(){setTimeout(function(){basis.value='serving';render();},0);});
 form.addEventListener('input',function(){document.getElementById('results').hidden=true;});
 basis.addEventListener('change',render);render();
})();
