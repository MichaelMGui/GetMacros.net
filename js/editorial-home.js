/* Homepage discovery. No nutrition inputs are sent to analytics. */
(function(){
  var filter=document.getElementById('home-restaurant-filter');
  if(filter){
    var links=[].slice.call(document.querySelectorAll('[data-chain-name]'));
    var empty=document.getElementById('restaurant-empty');
    filter.addEventListener('input',function(){var term=filter.value.trim().toLocaleLowerCase();var shown=0;links.forEach(function(link){var match=link.dataset.chainName.toLocaleLowerCase().includes(term);link.hidden=!match;if(match)shown++;});empty.hidden=shown>0;});
  }
  var form=document.querySelector('.discovery-form');
  if(form){form.addEventListener('submit',function(){window.dispatchEvent(new CustomEvent('gm:meal_finder_started'));});}
})();
