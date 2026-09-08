(function(){
 'use strict';
 var form=document.getElementById('builder'),output=document.getElementById('output');
 var rules=[
  {name:'Grain bowl',base:/Rice|Couscous/,protein:/beans|Lentils|Eggs|fish|Tofu/,produce:/vegetables|tomatoes/,flavor:/Oil|Salsa|Herbs|Peanut sauce/,method:'Cook the grain as directed. Prepare the protein and vegetables separately, then layer them over the grain. Finish with your selected seasoning or sauce.'},
  {name:'Pantry pasta',base:/Pasta/,protein:/beans|fish|Tofu|Lentils/,produce:/tomatoes|vegetables/,flavor:/Tomato sauce|Oil|Herbs|Cheese/,method:'Cook and drain the pasta. Warm the protein and vegetables in a separate pan, combine with the pasta, then add your selected sauce or seasoning.'},
  {name:'Loaded potato',base:/Potatoes/,protein:/beans|Eggs|fish|Tofu/,produce:/vegetables|tomatoes/,flavor:/Salsa|Cheese|Oil|Herbs/,method:'Bake or microwave the potato until tender. Split it open and add the prepared protein and vegetables. Finish with a topping you selected.'},
  {name:'Toast or wrap',base:/Bread/,protein:/beans|Eggs|fish|Tofu/,produce:/vegetables|tomatoes/,flavor:/Salsa|Cheese|Oil|Herbs/,method:'Use bread for toast, a tortilla for a wrap, or crackers for an open plate. Add the prepared protein, vegetables and a suitable topping. The format depends on which item you have.'},
  {name:'Fruit and nut oats',base:/Oats/,protein:/Peanut or seed butter/,produce:/fruit|applesauce/,flavor:null,method:'Cook oats with water according to the package directions. Stir in the nut or seed butter and add fruit. Adjust the water to get the texture you like.'},
  {name:'Savory oats',base:/Oats/,protein:/Eggs|Tofu/,produce:/vegetables|tomatoes/,flavor:/Herbs|Cheese|Oil/,method:'Cook oats with water. Prepare the egg or tofu and vegetables separately, then add them to the oats with your selected seasoning.'},
  {name:'Fruit and nut toast',base:/Bread/,protein:/Peanut or seed butter/,produce:/fruit|applesauce/,flavor:null,method:'Spread nut or seed butter on bread or crackers and serve with the fruit. If your selection is tortillas, fold it into a simple wrap.'}
 ];
 function add(tag,text,host){var el=document.createElement(tag);el.textContent=text;host.appendChild(el);return el;}
 function render(event){
  if(event)event.preventDefault();
  var selected={};form.querySelectorAll('fieldset').forEach(function(f){selected[f.dataset.group]=Array.from(f.querySelectorAll('input:checked')).map(function(x){return x.value;});});
  output.replaceChildren();add('h2','Your meal ideas',output);
  if(!Object.values(selected).flat().length){add('p','Select ingredients you have, then choose Build meals. We will match a meal format to your ingredients.',output);return;}
  var matches=rules.map(function(rule){
   var parts={},missing=[];
   [['grain','base'],['protein','protein'],['produce','produce'],['flavor','flavor']].forEach(function(pair){var pattern=rule[pair[1]];if(!pattern)return;parts[pair[0]]=(selected[pair[0]]||[]).find(function(item){return pattern.test(item);});if(!parts[pair[0]]&&pair[0]!=='flavor')missing.push(pair[0]);});
   return {rule:rule,parts:parts,missing:missing,count:Object.values(parts).filter(Boolean).length};
  }).filter(function(m){return m.count>0;}).sort(function(a,b){return a.missing.length-b.missing.length||b.count-a.count;}).slice(0,3);
  matches.forEach(function(m){
   var card=document.createElement('article');card.className='meal-card';output.appendChild(card);
   add('h3',m.rule.name,card);add('p',m.missing.length?'A starting idea — needs '+m.missing.length+' more ingredient '+(m.missing.length===1?'role.':'roles.'):'Your selected ingredients cover the base, protein and produce.',card);
   add('p','Use what you selected: '+Object.values(m.parts).filter(Boolean).join(' + ')+'.',card);
   if(m.missing.length){var role={grain:'base',protein:'protein',produce:'produce'};add('p','To complete this idea, add: '+m.missing.map(function(key){return Array.from(form.querySelectorAll('fieldset[data-group='+key+'] input')).map(function(input){return input.value;}).find(function(value){return m.rule[role[key]].test(value);});}).join(' + ')+'. These additions are not in your selected ingredients.',card);}
   add('p',m.rule.method,card);
  });
  add('p','These are flexible meal ideas, not priced recipes or calculated nutrition totals. Check package cooking instructions and adapt portions and ingredients to your needs.',output);
  var button=add('button','Print meal ideas',output);button.type='button';button.className='btn btn-outline';button.addEventListener('click',function(){window.print();});
 }
 form.addEventListener('submit',render);form.addEventListener('reset',function(){setTimeout(render,0);});
}());
