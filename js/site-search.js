(function () {
  var q=document.getElementById('site-search'),
      hits=[].slice.call(document.querySelectorAll('.search-hit')),
      groups=[].slice.call(document.querySelectorAll('[data-group]')),
      status=document.getElementById('search-status'),
      toggle=document.getElementById('search-results-toggle'),
      startBlock=document.getElementById('search-start'),
      libraryHeading=document.querySelector('.search-library-head'),
      limit=12, expanded=false;
  function words(value) {
    var aliases={calories:'calorie',macros:'macro',carbs:'carbohydrate',carb:'carbohydrate',bulking:'gain',cutting:'loss',restaurants:'restaurant'};
    var stop=['a','an','the','at','for','to','of','in','on','and','or','how','many','much','should','i','my','do','can','what','is','are','with','eat'];
    return (value.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(function(t){return stop.indexOf(t)<0;}).map(function(t){return aliases[t]||t;});
  }
  function run() {
    var terms=words(q.value), searching=!!q.value.trim(), matched=0;
    var ranked=hits.map(function(hit){
      var hay=words(hit.dataset.search).join(' '),title=words(hit.querySelector('.search-hit-name').textContent).join(' ');
      return {hit:hit,match:terms.every(function(t){return hay.indexOf(t)>-1;}),score:terms.reduce(function(sum,t){return sum+(title.indexOf(t)>-1?5:0);},0)+(title===terms.join(' ')?10:0)};
    }).filter(function(item){return item.match;}).sort(function(a,b){return b.score-a.score;});
    var visible=ranked.slice(0,expanded?ranked.length:limit).map(function(item){return item.hit;});
    var sortedGroups=groups.slice().sort(function(a,b){
      function score(group){var best=ranked.find(function(item){return group.contains(item.hit);});return best?best.score:-1;}
      return searching?score(b)-score(a):0;
    });
    sortedGroups.forEach(function(group){group.parentNode.insertBefore(group,document.querySelector('.search-results-actions'));});
    groups.forEach(function(group){
      var live=0;
      [].slice.call(group.querySelectorAll('.search-hit')).forEach(function(hit){
        var hay=words(hit.dataset.search).join(' ');
        var match=terms.every(function(t){return hay.indexOf(t)>-1;});
        hit.hidden=!(searching?(match&&visible.indexOf(hit)>-1):expanded);
        if(match)live++;
      });
      matched+=live;
      group.hidden=searching?!group.querySelector('.search-hit:not([hidden])'):!expanded;
      group.querySelector('[data-count]').textContent=live;
      var more=group.querySelector('[data-more]');if(more)more.hidden=true;
    });
    startBlock.hidden=searching||expanded;
    libraryHeading.hidden=!searching&&!expanded;
    status.textContent=searching?(matched?(matched>limit&&!expanded?'Top '+limit+' of ':'')+matched+' result'+(matched===1?'':'s')+' for “'+q.value.trim()+'”':'No results. Try “protein”, “Chipotle” or “calorie calculator”.'):(expanded?'Browse all '+hits.length+' resources':'Try a topic below, or choose a starting point.');
    toggle.hidden=searching&&matched<=limit;
    toggle.setAttribute('aria-expanded',String(expanded));
    toggle.textContent=searching?(expanded?'Show top results':'Show all '+matched+' results'):(expanded?'Back to starting points':'Browse all topics');
    document.getElementById('search-clear').hidden=!searching;
  }
  q.addEventListener('input',function(){expanded=false;run();});
  toggle.addEventListener('click',function(){expanded=!expanded;run();});
  document.getElementById('search-clear').addEventListener('click',function(){q.value='';expanded=false;run();q.focus();});
  document.querySelectorAll('[data-search-query]').forEach(function(button){button.addEventListener('click',function(){q.value=button.dataset.searchQuery;expanded=false;run();q.focus();});});
  var initial=new URLSearchParams(location.search).get('q');if(initial)q.value=initial;
  run();
})();
