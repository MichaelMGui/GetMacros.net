(function(){
 'use strict';
 var controls=document.querySelector('.meal-idea-filters');if(!controls)return;
 var cards=Array.from(document.querySelectorAll('.meal-idea'));
 controls.hidden=false;
 controls.addEventListener('click',function(event){
  var button=event.target.closest('[data-meal-filter]');if(!button)return;
  var filter=button.dataset.mealFilter,count=0;
  cards.forEach(function(card){card.hidden=filter!=='all'&&!card.dataset.mealTags.split(' ').includes(filter);if(!card.hidden)count++;});
  controls.querySelectorAll('button').forEach(function(item){item.setAttribute('aria-pressed',String(item===button));});
  document.querySelector('.meal-idea-status').textContent=count+' meal ideas';
 });
}());
