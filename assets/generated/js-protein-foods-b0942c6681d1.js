(function(){
  'use strict';
  var root=document.querySelector('[data-protein-library]');if(!root)return;
  var search=root.querySelector('input'),group=root.querySelector('select'),cards=Array.from(root.querySelectorAll('.protein-food-card'));
  function update(){var q=search.value.trim().toLowerCase(),count=0;cards.forEach(function(card){card.hidden=!(card.dataset.foodName.toLowerCase().includes(q)&&(!group.value||group.value===card.dataset.foodGroup));if(!card.hidden)count++;});root.querySelector('.food-count').textContent=count+' food'+(count===1?'':'s');root.querySelector('.food-empty').hidden=count>0;}
  search.addEventListener('input',update);group.addEventListener('change',update);root.querySelector('.food-filter-controls').hidden=false;update();
}());
