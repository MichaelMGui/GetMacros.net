/* Progressive enhancement: one list, simple filters, six meals at a time. */
(function () {
  'use strict';
  var root = document.querySelector('[data-meal-browser]');
  if (!root) return;
  var grid = root.querySelector('.browse-meal-grid');
  var cards = Array.from(grid.children);
  var query = root.querySelector('#browse-query');
  var filter = root.querySelector('#browse-filter');
  var more = root.querySelector('.browse-more');
  var status = root.querySelector('.browse-status');
  var limit = 6;
  function revealAfterAction(element) {
    var header = document.querySelector('.site-header');
    var clearance = header ? header.getBoundingClientRect().height + 24 : 24;
    window.scrollTo({top: Math.max(0, window.scrollY + element.getBoundingClientRect().top - clearance), behavior: 'auto'});
  }
  function normalize(text) { return text.toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ').trim(); }
  function update(append) {
    var terms = normalize(query.value).split(' ').filter(Boolean);
    var tag = filter.value;
    var matched = cards.filter(function (card) {
      return (!tag || card.dataset.tags.split(' ').indexOf(tag) !== -1) &&
        terms.every(function (word) { return normalize(card.dataset.search).indexOf(word) !== -1; });
    });
    var sort = {protein: ['protein', -1], light: ['calories', 1], energy: ['calories', -1], fibre: ['fiber', -1], lowsodium: ['sodium', 1]}[tag];
    if (sort) matched.sort(function (a, b) { return (Number(a.dataset[sort[0]]) - Number(b.dataset[sort[0]])) * sort[1]; });
    var firstNew = matched[limit - 6];
    cards.forEach(function (card) { card.hidden = true; });
    matched.forEach(function (card, i) { grid.appendChild(card); card.hidden = i >= limit; });
    status.textContent = matched.length ? Math.min(limit, matched.length) + ' of ' + matched.length + ' meals' : 'No matching meals';
    more.hidden = matched.length <= limit;
    root.querySelector('.browse-empty').hidden = !!matched.length;
    if (append && firstNew) {
      var heading = firstNew.querySelector('h3');
      heading.tabIndex = -1;
      heading.focus({preventScroll: true});
      revealAfterAction(firstNew);
    }
  }
  function reset() { limit = 6; update(false); }
  query.addEventListener('input', reset);
  filter.addEventListener('change', reset);
  more.addEventListener('click', function () { limit += 6; update(true); });
  root.querySelector('.meal-browser-controls').hidden = false;
  status.hidden = false;
  // Preserve older links to a ranked list as a filter on the new browser.
  var oldLists = {'highest-protein-fast-food':'protein','fast-food-under-400-calories':'light','high-calorie-fast-food':'energy','vegetarian-fast-food':'vegetarian','plant-based-fast-food':'plant','healthy-fast-food-breakfast':'breakfast','highest-fibre-fast-food':'fibre','lowest-sodium-fast-food':'lowsodium'};
  function restoreHash() {
    var tag = oldLists[location.hash.slice(1)];
    if (tag) {
      filter.value = tag;
      root.closest('details').open = true;
      reset();
      revealAfterAction(root.closest('details'));
    }
  }
  reset();
  restoreHash();
  window.addEventListener('hashchange', restoreHash);
}());
