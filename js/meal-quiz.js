/* Goal-first restaurant meal finder. */
(function () {
  "use strict";
  var meals = window.GM_MEALS || [];
  var T = window.GM_THRESHOLDS || { protein: 25, energy: 600, light: 400, fibre: 8, sodium: 600 };
  var root = document.getElementById("meal-quiz");
  if (!root || !meals.length) return;

  var chains = [];
  meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
  chains.sort();
  var STEPS = [
    { key: "goal", title: "What are you working toward?", multiple: true,
      hint: "Choose every goal that matters today. We rank for the combination, so high protein + bulking works together.",
      options: [["energy", "Bulking", T.energy + "+ calories", "↗"], ["light", "Cutting", T.light + " calories or fewer", "↘"], ["protein", "High protein", T.protein + "g protein or more", "P"], ["fibre", "High fibre", T.fibre + "g fibre or more", "F"], ["lowsodium", "Lower sodium", T.sodium + "mg sodium or fewer", "S"], ["balanced", "Balanced", "A practical middle-ground meal", "◎"]], none: "No specific goal" },
    { key: "size", title: "How much food do you want?", single: true,
      hint: "This adjusts the ranking. It never hides an otherwise strong match.",
      options: [["small", "Small", "Snack or light appetite", "S"], ["medium", "Medium", "A regular meal", "M"], ["large", "Large", "Hungry or higher-calorie day", "L"]], none: "Any portion size" },
    { key: "diet", title: "Any dietary needs?", multiple: true,
      hint: "These are strict filters. Select more than one only when every choice must apply.",
      options: [["vegetarian", "Vegetarian", "No meat or fish in the standard build", "V"], ["plant", "Plant-based", "No animal products in the standard build", "◆"], ["gluten", "Gluten-aware", "No gluten ingredient listed in the standard build", "G"]], none: "No dietary filter" },
    { key: "meal", title: "When are you ordering?", single: true,
      hint: "Breakfast menus are separated because availability changes by time of day.",
      options: [["main", "Lunch or dinner", "Use the main menu", "☀"], ["breakfast", "Breakfast", "Use breakfast items only", "◒"]], none: "Any time of day" },
    { key: "chain", title: "Where can you eat?", multiple: true, chainStep: true,
      hint: "Pick one or several restaurants, or search all " + chains.length + " chains.",
      options: chains.map(function (c) { return [c, c, "", c.charAt(0)]; }), none: "Search every restaurant" }
  ];
  var state = { goal: [], size: [], diet: [], meal: [], chain: [] };
  var step = 0, includeIncomplete = false, SAVED_KEY = "getmacros-saved-meals-v1", saved = readSaved();
  var GOAL_LABEL = { energy: "bulking", light: "cutting", protein: "high protein", fibre: "high fibre", lowsodium: "lower sodium", balanced: "balanced" };
  var DIET_LABEL = { vegetarian: "vegetarian", plant: "plant-based", gluten: "gluten-aware" };

  function esc(value) { return String(value).replace(/[&<>\"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '\"': "&quot;" }[c]; }); }
  function list(items) { return items.length < 2 ? (items[0] || "") : items.slice(0, -1).join(", ") + " and " + items[items.length - 1]; }
  function has(m, tag) { return m.t.indexOf(tag) !== -1; }
  function complete(m) { return m.cal !== null && m.p !== null && m.f !== null && m.na !== null; }
  function mealKey(m) { return m.chain + "||" + m.name; }
  function readSaved() { try { var value = JSON.parse(localStorage.getItem("getmacros-saved-meals-v1") || "[]"); return Array.isArray(value) ? value : []; } catch (error) { return []; } }
  function toggleSaved(key) { var i = saved.indexOf(key); if (i === -1) saved.push(key); else saved.splice(i, 1); try { localStorage.setItem(SAVED_KEY, JSON.stringify(saved)); } catch (error) {} updateSavedUi(); }
  function updateSavedUi() { root.querySelectorAll("[data-save]").forEach(function (button) { var active = saved.indexOf(button.dataset.save) !== -1; button.setAttribute("aria-pressed", String(active)); button.textContent = active ? "Saved ✓" : "Save meal"; }); }

  var qs = new URLSearchParams(location.search), deepLinked = false;
  STEPS.forEach(function (s) { var allowed = s.options.map(function (o) { return o[0]; }); qs.getAll(s.key).forEach(function (v) { if (allowed.indexOf(v) !== -1 && state[s.key].indexOf(v) === -1) { state[s.key].push(v); deepLinked = true; } }); });
  includeIncomplete = qs.get("complete") === "0";

  function eligible(m) {
    if (!includeIncomplete && !complete(m)) return false;
    if (state.meal.length && state.meal.indexOf(m.meal) === -1) return false;
    if (state.diet.length && !state.diet.every(function (d) { return m.diet.indexOf(d) !== -1; })) return false;
    if (state.chain.length && state.chain.indexOf(m.chain) === -1) return false;
    return true;
  }
  function score(m) {
    var value = state.size.length && m.size === state.size[0] ? 28 : 0;
    state.goal.forEach(function (g) { if (has(m, g)) value += 65; });
    if (m.p !== null) value += Math.min(m.p, 50) * 0.5;
    if (m.f !== null) value += Math.min(m.f, 15) * 0.5;
    if (m.p !== null && m.cal) value += (m.p / m.cal) * 100;
    if (!complete(m)) value -= 40;
    return value;
  }
  function matchCount(m) { return state.goal.filter(function (g) { return has(m, g); }).length; }
  function why(m) {
    if (!state.goal.length) return m.why;
    var hits = [], misses = [];
    state.goal.forEach(function (g) {
      if (has(m, g)) {
        if (g === "protein" && m.p !== null) hits.push(m.p + "g protein");
        else if ((g === "energy" || g === "light") && m.cal !== null) hits.push(m.cal + " calories");
        else if (g === "fibre" && m.f !== null) hits.push(m.f + "g fibre");
        else if (g === "lowsodium" && m.na !== null) hits.push(m.na.toLocaleString() + "mg sodium");
        else hits.push(GOAL_LABEL[g]);
      } else misses.push(GOAL_LABEL[g]);
    });
    var text = hits.length ? "Matches: " + list(hits) + "." : "";
    if (misses.length) text += (text ? " " : "") + "Trade-off: it does not meet " + list(misses) + ".";
    return text || m.why;
  }
  function metric(value, unit, label) { var shown = value === null ? "Not published" : value.toLocaleString() + unit; return '<span class="meal-metric' + (value === null ? " is-missing" : "") + '"><b>' + shown + "</b><small>" + label + "</small></span>"; }
  function card(m, top) {
    var key = mealKey(m), matches = matchCount(m);
    var badge = !state.goal.length ? "Good starting point" : matches === state.goal.length ? "Matches every goal" : "Matches " + matches + " of " + state.goal.length;
    return '<article class="meal-card' + (top ? " top-match" : "") + '"><div class="meal-card-top"><span class="meal-chain">' + esc(m.chain) + '</span><span class="meal-rank">' + badge + '</span></div><h3>' + esc(m.name) + '</h3><div class="meal-stats">' + metric(m.cal, "", "calories") + metric(m.p, "g", "protein") + metric(m.f, "g", "fibre") + metric(m.na, "mg", "sodium") + '</div><p class="meal-reason">' + esc(why(m)) + '</p><div class="meal-card-actions"><a class="meal-link" href="' + esc(m.url) + '">View restaurant guide →</a><button class="meal-save" type="button" data-save="' + esc(key) + '" aria-pressed="' + (saved.indexOf(key) !== -1) + '">' + (saved.indexOf(key) !== -1 ? "Saved ✓" : "Save meal") + '</button></div></article>';
  }
  function optionMarkup(s) {
    var type = s.single ? "radio" : "checkbox";
    return '<div class="quiz-options' + (s.chainStep ? " chain-options" : "") + '">' + s.options.map(function (o) {
      var checked = state[s.key].indexOf(o[0]) !== -1 ? " checked" : "";
      return '<label class="quiz-option"><input type="' + type + '" name="q-' + s.key + '" data-facet="' + s.key + '" value="' + esc(o[0]) + '"' + checked + '><span class="option-icon" aria-hidden="true">' + esc(o[3] || o[1].charAt(0)) + '</span><span class="option-copy"><b>' + esc(o[1]) + '</b>' + (o[2] ? '<small>' + esc(o[2]) + '</small>' : '') + '</span><span class="option-check" aria-hidden="true">✓</span></label>';
    }).join("") + '</div><button type="button" class="quiz-skip" data-clear="' + s.key + '">' + esc(s.none) + ' →</button>';
  }
  function renderStep() {
    var s = STEPS[step], conflict = s.key === "goal" && state.goal.indexOf("energy") !== -1 && state.goal.indexOf("light") !== -1;
    root.innerHTML = '<div class="quiz-card"><div class="quiz-progress-row"><span>Question ' + (step + 1) + ' of ' + STEPS.length + '</span><span>' + Math.round((step + 1) / STEPS.length * 100) + '%</span></div><div class="quiz-progress"><span style="width:' + ((step + 1) / STEPS.length * 100) + '%"></span></div><h2 tabindex="-1">' + esc(s.title) + '</h2><p class="quiz-hint">' + esc(s.hint) + '</p>' + optionMarkup(s) + (conflict ? '<p class="quiz-warn">Cutting and bulking point in opposite calorie directions. Keep both if you want; results will clearly show the trade-off.</p>' : '') + '<div class="quiz-nav">' + (step ? '<button type="button" class="btn btn-ghost" data-go="-1">Back</button>' : '<span></span>') + '<button type="button" class="btn btn-primary" data-go="1">' + (step === STEPS.length - 1 ? 'Show my matches' : 'Continue') + '</button></div></div>';
    root.querySelector("h2").focus({ preventScroll: true });
  }
  function summary(count) {
    var bits = [];
    if (state.goal.length) bits.push(list(state.goal.map(function (g) { return GOAL_LABEL[g]; })));
    if (state.size.length) bits.push(state.size[0] + " portion");
    if (state.diet.length) bits.push(list(state.diet.map(function (d) { return DIET_LABEL[d]; })));
    if (state.meal.length) bits.push(state.meal[0] === "breakfast" ? "breakfast" : "lunch or dinner");
    if (state.chain.length) bits.push(list(state.chain));
    return (bits.length ? "Best matches for " + list(bits) : "Best overall starting points") + ". " + count + " meals available.";
  }
  function renderResults() {
    var results = meals.filter(eligible).sort(function (a, b) { return score(b) - score(a); });
    var incompleteCount = meals.filter(function (m) { return !complete(m); }).length;
    if (!results.length) {
      root.innerHTML = '<div class="quiz-card empty-results"><span class="result-symbol">↺</span><h2 tabindex="-1">That combination is too narrow.</h2><p>Remove one restaurant or dietary filter and we can give you useful choices instead of filler.</p><button type="button" class="btn btn-primary" data-restart="1">Change my answers</button></div>';
      root.querySelector("h2").focus({ preventScroll: true }); syncUrl(); return;
    }
    var shown = results.slice(0, 8);
    root.innerHTML = '<div class="quiz-results"><div class="results-heading"><div><p class="eyebrow">Your shortlist</p><h2 tabindex="-1">Meals that fit your day</h2><p class="quiz-summary">' + esc(summary(results.length)) + '</p></div><button type="button" class="btn btn-ghost" data-restart="1">Edit answers</button></div><div class="data-quality"><span aria-hidden="true">✓</span><p><b>Complete nutrition is shown first.</b> By default, every result has calories, protein, fibre and sodium filled in.</p></div><div class="results-grid">' + shown.map(function (m, i) { return card(m, i === 0); }).join("") + '</div>' + (results.length > shown.length ? '<button type="button" class="btn btn-ghost results-more" data-more="1">Show ' + (results.length - shown.length) + ' more complete matches</button>' : '') + '<div class="result-controls"><label class="data-toggle"><input type="checkbox" data-incomplete="1"' + (includeIncomplete ? ' checked' : '') + '><span><b>Include meals with incomplete nutrition data</b><small>' + incompleteCount + ' meals are excluded by default because one or more figures are not published.</small></span></label><button type="button" class="btn btn-ghost" data-share="1">Share results</button></div></div>';
    root._rest = results.slice(8); root.querySelector("h2").focus({ preventScroll: true }); syncUrl(); updateSavedUi();
  }
  function syncUrl() { var url = new URL(location.href); url.search = ""; STEPS.forEach(function (s) { state[s.key].forEach(function (v) { url.searchParams.append(s.key, v); }); }); if (includeIncomplete) url.searchParams.set("complete", "0"); history.replaceState(null, "", url); }
  function shareResults(button) { var data = { title: "My GetMacros meal matches", text: "Fast-food options matched to my goals and preferences.", url: location.href }; if (navigator.share) { navigator.share(data).catch(function () {}); return; } if (navigator.clipboard) navigator.clipboard.writeText(data.url).then(function () { button.textContent = "Link copied ✓"; }); }

  root.addEventListener("change", function (e) {
    var el = e.target;
    if (el.dataset.incomplete) { includeIncomplete = el.checked; renderResults(); return; }
    if (!el.dataset.facet) return;
    var key = el.dataset.facet;
    if (el.type === "radio") state[key] = el.checked ? [el.value] : [];
    else { var i = state[key].indexOf(el.value); if (el.checked && i === -1) state[key].push(el.value); if (!el.checked && i !== -1) state[key].splice(i, 1); }
    if (key === "goal") renderStep();
  });
  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-go],[data-clear],[data-restart],[data-more],[data-save],[data-share]"); if (!t) return;
    if (t.dataset.save) toggleSaved(t.dataset.save);
    else if (t.dataset.share) shareResults(t);
    else if (t.dataset.clear) { state[t.dataset.clear] = []; step += 1; step >= STEPS.length ? renderResults() : renderStep(); }
    else if (t.dataset.go) { step += Number(t.dataset.go); step >= STEPS.length ? renderResults() : renderStep(); }
    else if (t.dataset.restart) { step = 0; renderStep(); }
    else if (t.dataset.more) { root.querySelector(".results-grid").insertAdjacentHTML("beforeend", root._rest.map(function (m) { return card(m, false); }).join("")); t.remove(); updateSavedUi(); }
  });
  deepLinked ? renderResults() : renderStep();
})();
