/* Restaurant meal finder.
 *
 * Replaces a four-step wizard that allowed exactly one goal. Filters are now
 * multi-select and combine, so "high protein" AND "higher calorie" is a real
 * query rather than a compromise, and results update as you toggle instead of
 * hiding behind a submit button.
 */
(function () {
  "use strict";

  var meals = window.GM_MEALS || [];
  var root = document.getElementById("finder");
  if (!root || !meals.length) return;

  var GOALS = [
    ["protein", "More protein", "25 g or more"],
    ["light", "Lighter meal", "About 400 kcal or under"],
    ["energy", "Higher calorie", "600 kcal or more, for bulking days"],
    ["fibre", "More fibre", "5 g or more"],
    ["lowsodium", "Lower sodium", "About 600 mg or under"],
    ["balanced", "Balanced", "No single extreme"]
  ];
  var DIETS = [
    ["vegetarian", "Vegetarian", "No meat or fish"],
    ["plant", "Plant-based", "No animal products"],
    ["gluten", "Gluten-aware", "No gluten ingredient in the standard build"],
    ["breakfast", "Breakfast", "Served as a breakfast item"]
  ];
  var SIZES = [["small", "Small"], ["medium", "Medium"], ["large", "Large"]];

  var chains = [];
  meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
  chains.sort();

  var state = { goal: [], diet: [], size: [], chain: [], sort: "match", complete: false };

  // Deep links from the hub page still work: ?goal=protein&goal=fibre&diet=plant
  // Only values the UI actually offers are accepted. A hand-edited or stale
  // link with an unknown value is ignored rather than filtered on, so a bad
  // URL cannot leave a visitor staring at an empty page they cannot explain.
  var ALLOWED = {
    goal: GOALS.map(function (g) { return g[0]; }),
    diet: DIETS.map(function (d) { return d[0]; }),
    size: SIZES.map(function (s) { return s[0]; }),
    chain: chains
  };
  var qs = new URLSearchParams(location.search);
  ["goal", "diet", "size", "chain"].forEach(function (key) {
    qs.getAll(key).forEach(function (v) {
      if (ALLOWED[key].indexOf(v) !== -1 && state[key].indexOf(v) === -1) state[key].push(v);
    });
  });

  function chipGroup(name, items, legend, hint) {
    return '<fieldset class="filter-group"><legend>' + legend + "</legend>" +
      (hint ? '<p class="filter-hint">' + hint + "</p>" : "") +
      '<div class="chip-row">' + items.map(function (it) {
        var val = it[0], label = it[1], sub = it[2];
        return '<label class="chip"><input type="checkbox" data-facet="' + name +
          '" value="' + val + '"><span><b>' + label + "</b>" +
          (sub ? "<small>" + sub + "</small>" : "") + "</span></label>";
      }).join("") + "</div></fieldset>";
  }

  root.innerHTML =
    '<div class="finder-layout">' +
      '<form class="finder-filters" id="finder-filters" aria-label="Filter meals">' +
        '<div class="filters-head"><h2>Filter</h2>' +
          '<button type="button" class="link-btn" id="reset-filters">Reset</button></div>' +
        chipGroup("goal", GOALS, "What matters for this meal?", "Pick as many as you like &mdash; they stack.") +
        chipGroup("diet", DIETS, "Any requirements?", "") +
        chipGroup("size", SIZES, "Portion size", "") +
        chipGroup("chain", chains.map(function (c) { return [c, c, ""]; }), "Restaurants", "Leave empty for all " + chains.length + ".") +
        '<label class="switch-row"><input type="checkbox" id="complete-only">' +
          "<span>Only meals with complete published numbers</span></label>" +
      "</form>" +
      '<div class="finder-results">' +
        '<div class="results-bar">' +
          '<p id="result-count" role="status"></p>' +
          '<label class="sort-row">Sort' +
            '<select id="sort-by">' +
              '<option value="match">Best match</option>' +
              '<option value="protein">Most protein</option>' +
              '<option value="calories-asc">Fewest calories</option>' +
              '<option value="calories-desc">Most calories</option>' +
              '<option value="fibre">Most fibre</option>' +
              '<option value="sodium">Lowest sodium</option>' +
            "</select></label>" +
        "</div>" +
        '<div id="active-filters" class="active-filters"></div>' +
        '<div id="results" class="results-grid"></div>' +
      "</div>" +
    "</div>";

  var resultsEl = document.getElementById("results");
  var countEl = document.getElementById("result-count");
  var activeEl = document.getElementById("active-filters");
  var sortEl = document.getElementById("sort-by");
  var completeEl = document.getElementById("complete-only");

  function has(m, tag) { return m.t.indexOf(tag) !== -1; }

  function matches(m) {
    // Goals are OR within the group: picking protein and energy shows meals
    // that satisfy either, which is what "high protein AND bulk" means in
    // practice on a menu this size.
    if (state.goal.length && !state.goal.some(function (g) { return has(m, g); })) return false;
    // Requirements are AND: vegetarian plus gluten-aware must satisfy both.
    if (state.diet.length && !state.diet.every(function (d) { return has(m, d); })) return false;
    if (state.size.length && state.size.indexOf(m.size) === -1) return false;
    if (state.chain.length && state.chain.indexOf(m.chain) === -1) return false;
    if (state.complete && (m.p === null || m.cal === null || m.na === null)) return false;
    return true;
  }

  function score(m) {
    var s = 0;
    state.goal.forEach(function (g) { if (has(m, g)) s += 40; });
    state.diet.forEach(function (d) { if (has(m, d)) s += 15; });
    if (m.p !== null) s += Math.min(m.p, 50) / 2;
    if (m.f !== null) s += Math.min(m.f, 15);
    if (m.p !== null && m.cal) s += (m.p / m.cal) * 120;   // protein density
    if (m.na === null || m.p === null) s -= 6;             // prefer known numbers
    return s;
  }

  function sortFns(a, b) {
    var v = sortEl.value;
    var num = function (x, key, fallback) { return x[key] === null ? fallback : x[key]; };
    if (v === "protein") return num(b, "p", -1) - num(a, "p", -1);
    if (v === "calories-asc") return num(a, "cal", 1e9) - num(b, "cal", 1e9);
    if (v === "calories-desc") return num(b, "cal", -1) - num(a, "cal", -1);
    if (v === "fibre") return num(b, "f", -1) - num(a, "f", -1);
    if (v === "sodium") return num(a, "na", 1e9) - num(b, "na", 1e9);
    return score(b) - score(a);
  }

  function stat(value, unit, label) {
    return "<span><b>" + (value === null ? "&mdash;" : value.toLocaleString() + unit) +
      "</b>" + label + "</span>";
  }

  function card(m) {
    var tags = m.t.filter(function (t) { return t !== "balanced"; }).slice(0, 3)
      .map(function (t) {
        var names = { protein: "High protein", light: "Lighter", energy: "Higher calorie",
                      fibre: "High fibre", lowsodium: "Lower sodium", vegetarian: "Vegetarian",
                      plant: "Plant-based", gluten: "Gluten-aware", breakfast: "Breakfast" };
        return '<span class="meal-tag">' + (names[t] || t) + "</span>";
      }).join("");
    return '<article class="meal-card">' +
      '<div class="meal-card-top"><span class="meal-chain">' + m.chain + "</span>" + tags + "</div>" +
      "<h3>" + m.name + "</h3>" +
      '<div class="meal-stats">' +
        stat(m.cal, "", "kcal") + stat(m.p, "g", "protein") +
        stat(m.f, "g", "fibre") + stat(m.na, "mg", "sodium") +
      "</div>" +
      "<p>" + m.why + "</p>" +
      '<a class="meal-link" href="' + m.url + '">See the ' + m.chain + " guide &rarr;</a>" +
      "</article>";
  }

  function label(facet, value) {
    if (facet === "goal") {
      var g = GOALS.filter(function (x) { return x[0] === value; })[0];
      return g ? g[1] : value;
    }
    if (facet === "diet") {
      var d = DIETS.filter(function (x) { return x[0] === value; })[0];
      return d ? d[1] : value;
    }
    if (facet === "size") return value.charAt(0).toUpperCase() + value.slice(1);
    return value;
  }

  function renderActive() {
    var pills = [];
    ["goal", "diet", "size", "chain"].forEach(function (facet) {
      state[facet].forEach(function (v) {
        pills.push('<button type="button" class="active-pill" data-facet="' + facet +
          '" data-value="' + v.replace(/"/g, "&quot;") + '">' + label(facet, v) +
          ' <span aria-hidden="true">&times;</span><span class="sr-only">Remove filter</span></button>');
      });
    });
    if (state.complete) {
      pills.push('<button type="button" class="active-pill" data-facet="complete" data-value="1">' +
        'Complete numbers <span aria-hidden="true">&times;</span></button>');
    }
    activeEl.innerHTML = pills.join("");
  }

  function render() {
    var list = meals.filter(matches).sort(sortFns);
    countEl.innerHTML = list.length
      ? "<strong>" + list.length + "</strong> of " + meals.length + " meals match"
      : "<strong>No exact match.</strong> Try removing a filter.";
    resultsEl.innerHTML = list.length
      ? list.map(card).join("")
      : '<div class="empty-state"><p>Nothing matches every filter at once. ' +
        'Requirements like vegetarian and gluten-aware have to all be met, so the ' +
        'combination can run out quickly.</p>' +
        '<button type="button" class="btn btn-primary" id="clear-empty">Clear filters</button></div>';
    renderActive();

    var url = new URL(location.href);
    url.search = "";
    ["goal", "diet", "size", "chain"].forEach(function (f) {
      state[f].forEach(function (v) { url.searchParams.append(f, v); });
    });
    history.replaceState(null, "", url);
  }

  root.addEventListener("change", function (e) {
    var el = e.target;
    if (el.dataset && el.dataset.facet) {
      var facet = el.dataset.facet, v = el.value, arr = state[facet];
      var i = arr.indexOf(v);
      if (el.checked && i === -1) arr.push(v);
      if (!el.checked && i !== -1) arr.splice(i, 1);
      render();
    } else if (el.id === "sort-by") {
      render();
    } else if (el.id === "complete-only") {
      state.complete = el.checked;
      render();
    }
  });

  function clearAll() {
    state.goal = []; state.diet = []; state.size = []; state.chain = []; state.complete = false;
    root.querySelectorAll('input[type="checkbox"]').forEach(function (c) { c.checked = false; });
    render();
  }

  root.addEventListener("click", function (e) {
    var pill = e.target.closest(".active-pill");
    if (pill) {
      var facet = pill.dataset.facet;
      if (facet === "complete") {
        state.complete = false;
        completeEl.checked = false;
      } else {
        var v = pill.dataset.value, i = state[facet].indexOf(v);
        if (i !== -1) state[facet].splice(i, 1);
        var box = root.querySelector('input[data-facet="' + facet + '"][value="' + CSS.escape(v) + '"]');
        if (box) box.checked = false;
      }
      render();
      return;
    }
    if (e.target.id === "reset-filters" || e.target.id === "clear-empty") clearAll();
  });

  // Reflect any deep-linked filters in the checkboxes before the first render.
  root.querySelectorAll('input[data-facet]').forEach(function (box) {
    if (state[box.dataset.facet].indexOf(box.value) !== -1) box.checked = true;
  });

  render();
})();
