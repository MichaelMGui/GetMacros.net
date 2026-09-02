/* Goal-first restaurant meal finder. */
(function () {
  "use strict";
  var meals = window.GM_MEALS || [];
  var T = window.GM_THRESHOLDS || { protein: 25, energy: 600, light: 400, fibre: 8, sodium: 600 };
  var root = document.getElementById("meal-quiz");
  if (!root || !meals.length) return;

  // Keep step changes accessible without moving the page. Focusing a newly
  // inserted heading can still scroll the viewport in iOS Safari even when
  // preventScroll is requested, which made Continue feel unpredictable.
  var announcer = document.createElement("p");
  announcer.className = "sr-only quiz-announcer";
  announcer.setAttribute("aria-live", "polite");
  announcer.setAttribute("aria-atomic", "true");
  root.parentNode.insertBefore(announcer, root);
  function announce(message) { announcer.textContent = message; }

  // Product-first order: begin with chains that combine broad familiarity with
  // the strongest range of complete meals in this dataset. This is an interface
  // priority, not a claim about national sales or a universal restaurant rank.
  // Anything new falls in after these, alphabetically.
  var CHAIN_RANK = [
    "Chipotle", "McDonald's", "Wendy's", "Chick-fil-A", "Taco Bell",
    "Subway", "Panda Express", "Starbucks", "Panera", "CAVA",
    "Sweetgreen", "Jersey Mike's", "KFC", "Popeyes", "Dunkin'"
  ];
  // Each chain gets a tile in its own signature colour. These are initials, not
  // brand logos: we have no licence to redistribute another company's mark, and
  // third-party media republished without rights is exactly what an ad review
  // flags. The initials and the colour still make a chain findable at a glance.
  var CHAIN_TONE = {
    "McDonald's": "#ffe9c2", "Starbucks": "#d8ece0", "Chick-fil-A": "#ffe0d8",
    "Taco Bell": "#ece2f5", "Wendy's": "#ffdcd6", "Dunkin'": "#ffe2f0",
    "Subway": "#e4f3d8", "Chipotle": "#e8e0d8", "Popeyes": "#ffe6cc",
    "KFC": "#ffdada", "Panera": "#e9f0d6", "Panda Express": "#ffe0e0",
    "Jersey Mike's": "#dbe8f5", "Sweetgreen": "#dcf2dd", "CAVA": "#e2efe9"
  };
  // The data spells these with a typographic apostrophe (McDonald’s) while the
  // lists above use a straight one, so a raw lookup missed exactly the four
  // best-known chains and dropped them to the bottom of the step.
  function chainKey(name) { return String(name).replace(/[\u2018\u2019\u02bc]/g, "'"); }
  // Derived initials collide -- Chick-fil-A and Chipotle both reduce to "CH" --
  // so the chains we carry get theirs stated.
  var CHAIN_INITIALS = {
    "McDonald's": "MC", "Starbucks": "SB", "Chick-fil-A": "CF", "Taco Bell": "TB",
    "Wendy's": "WE", "Dunkin'": "DK", "Subway": "SW", "Chipotle": "CP",
    "Popeyes": "PY", "KFC": "KF", "Panera": "PN", "Panda Express": "PX",
    "Jersey Mike's": "JM", "Sweetgreen": "SG", "CAVA": "CV"
  };
  function chainInitials(name) {
    var known = CHAIN_INITIALS[chainKey(name)];
    if (known) return known;
    var words = String(name).replace(/[^A-Za-z' ]/g, "").split(/\s+/).filter(Boolean);
    if (words.length > 1) return (words[0][0] + words[1][0]).toUpperCase();
    return String(name).replace(/[^A-Za-z]/g, "").slice(0, 2).toUpperCase();
  }
  var chains = [];
  meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
  chains.sort(function (a, b) {
    var ra = CHAIN_RANK.indexOf(chainKey(a)), rb = CHAIN_RANK.indexOf(chainKey(b));
    if (ra === -1 && rb === -1) return a.localeCompare(b);
    if (ra === -1) return 1;
    if (rb === -1) return -1;
    return ra - rb;
  });
  var STEPS = [
    { key: "goal", title: "What do you want from this meal?", multiple: true,
      hint: "Pick as many as apply. We rank for the combination, so high protein and bulking work together.",
      options: [["energy", "Bulking", T.energy + "+ calories", "trendUp"], ["light", "Cutting", "250–" + T.light + " calories with at least 15 g protein", "trendDown"], ["protein", "High protein", T.protein + " g protein or more", "protein"], ["fibre", "High fiber", T.fibre + " g fiber or more", "leaf"], ["lowsodium", "Lower sodium", T.sodium + " mg or fewer on substantial meals", "drop"], ["balanced", "Balanced", "A practical middle-ground meal", "balance"]], none: ["No specific goal", "Show strong all-around starting points", "spark"] },
    { key: "size", title: "How big should the meal be?", single: true,
      hint: "This nudges the ranking. It never hides an otherwise strong match.",
      options: [["small", "Small", "Snack or light appetite", "portionSmall"], ["medium", "Medium", "A regular meal", "portionMedium"], ["large", "Large", "Hungry or higher-calorie day", "portionLarge"]], none: ["Any portion size", "Do not use portion size as a ranking signal", "layers"] },
    { key: "diet", title: "Anything you need to avoid?", multiple: true,
      hint: "These are strict filters. Choose more than one only when every one must apply.",
      options: [["vegetarian", "Vegetarian", "No meat or fish in the standard build", "leaf"], ["plant", "Plant-based", "No animal products in the standard build", "sprout"], ["gluten", "Gluten-aware", "No gluten ingredient listed in the standard build", "grain"]], none: ["No dietary filter", "Include every standard menu build", "all"] },
    { key: "meal", title: "Breakfast, or later in the day?", single: true,
      hint: "Breakfast menus are separated because availability changes by time of day.",
      options: [["main", "Lunch or dinner", "Use the main menu", "sun"], ["breakfast", "Breakfast", "Use breakfast items only", "sunrise"]], none: ["Any time of day", "Search breakfast and main menus", "clock"] },
    { key: "chain", title: "Which restaurants can you get to?", multiple: true, chainStep: true,
      hint: "Choose the ones nearby, or search all " + chains.length + " chains.",
      options: chains.map(function (c) { return [c, c, "", "chain"]; }), none: ["Search every restaurant", "Compare all " + chains.length + " restaurants", "map"] }
  ];
  var state = { goal: [], size: [], diet: [], meal: [], chain: [] };
  var noPreference = { goal: false, size: false, diet: false, meal: false, chain: false };
  var step = 0, includeIncomplete = false, SAVED_KEY = "getmacros-saved-meals-v1", saved = readSaved();
  var GOAL_LABEL = { energy: "bulking", light: "cutting", protein: "high protein", fibre: "high fiber", lowsodium: "lower sodium", balanced: "balanced" };
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
        else if (g === "fibre" && m.f !== null) hits.push(m.f + "g fiber");
        else if (g === "lowsodium" && m.na !== null) hits.push(m.na.toLocaleString() + "mg sodium");
        else hits.push(GOAL_LABEL[g]);
      } else misses.push(GOAL_LABEL[g]);
    });
    var text = hits.length ? "Matches: " + list(hits) + "." : "";
    if (misses.length) text += (text ? " " : "") + "Trade-off: it does not meet " + list(misses) + ".";
    return text || m.why;
  }
  function metric(value, unit, label) { var shown = value === null ? "Not published" : value.toLocaleString() + unit; return '<span class="meal-metric' + (value === null ? " is-missing" : "") + '"><b>' + shown + "</b><small>" + label + "</small></span>"; }
  function iconSvg(name, fallback) {
    var paths = {
      trendUp: '<path d="M5 17l5-5 3 3 6-7M14 8h5v5"/>', trendDown: '<path d="M5 7l5 5 3-3 6 7M14 16h5v-5"/>',
      protein: '<path d="M7 5v14M17 5v14M4 9h3m10 0h3M4 15h3m10 0h3M9 8v8m6-8v8"/>', leaf: '<path d="M19 4C11 4 6 8 6 14c0 3 2 5 5 5 6 0 8-7 8-15Z"/><path d="M5 20c2-5 5-8 10-11"/>',
      sprout: '<path d="M12 20v-8M12 13C8 13 5 10 5 6c4 0 7 2 7 6M12 15c0-4 3-7 7-7 0 4-3 7-7 7"/>', grain: '<path d="M12 21V5M12 8c-3 0-5-2-5-5 3 0 5 2 5 5Zm0 5c-3 0-5-2-5-5 3 0 5 2 5 5Zm0 5c-3 0-5-2-5-5 3 0 5 2 5 5Zm0-10c3 0 5-2 5-5-3 0-5 2-5 5Zm0 5c3 0 5-2 5-5-3 0-5 2-5 5Zm0 5c3 0 5-2 5-5-3 0-5 2-5 5Z"/>',
      drop: '<path d="M12 3s6 7 6 12a6 6 0 0 1-12 0c0-5 6-12 6-12Z"/><path d="M9 16c.5 1.2 1.5 2 3 2"/>', balance: '<path d="M12 4v16M6 7h12M7 7l-3 6h6L7 7Zm10 0-3 6h6l-3-6ZM8 20h8"/>',
      portionSmall: '<circle cx="12" cy="12" r="4"/>', portionMedium: '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2"/>', portionLarge: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/>',
      layers: '<path d="m4 9 8-4 8 4-8 4-8-4Zm0 4 8 4 8-4M4 17l8 4 8-4"/>', sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M2 12h2m16 0h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
      sunrise: '<path d="M4 18h16M6 14a6 6 0 0 1 12 0M12 3v3M4.5 7.5 7 10m12.5-2.5L17 10"/>', clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', map: '<path d="m4 6 5-2 6 2 5-2v14l-5 2-6-2-5 2V6Zm5-2v14m6-12v14"/>', all: '<path d="M5 7h14M5 12h14M5 17h14"/>', spark: '<path d="m12 3 1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3Z"/>'
    };
    if (name === "chain") return '<span class="chain-letter" aria-hidden="true">' + esc(fallback.charAt(0)) + '</span>';
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (paths[name] || paths.spark) + '</svg>';
  }
  function card(m, top) {
    var key = mealKey(m), matches = matchCount(m);
    var badge = !state.goal.length ? "Good starting point" : matches === state.goal.length ? "Matches every goal" : "Matches " + matches + " of " + state.goal.length;
    return '<article class="meal-card' + (top ? " top-match" : "") + '"><div class="meal-card-top"><span class="meal-chain">' + esc(m.chain) + '</span><span class="meal-rank">' + badge + '</span></div><h3>' + esc(m.name) + '</h3><div class="meal-stats">' + metric(m.cal, "", "calories") + metric(m.p, "g", "protein") + metric(m.f, "g", "fiber") + metric(m.na, "mg", "sodium") + '</div><p class="meal-reason">' + esc(why(m)) + '</p><div class="meal-card-actions"><a class="meal-link" href="' + esc(m.url) + '">View restaurant guide →</a><button class="meal-save" type="button" data-save="' + esc(key) + '" aria-pressed="' + (saved.indexOf(key) !== -1) + '">' + (saved.indexOf(key) !== -1 ? "Saved ✓" : "Save meal") + '</button></div></article>';
  }
  function optionMarkup(s) {
    var type = s.single ? "radio" : "checkbox";
    var none = s.none;
    var noPreferenceOption = '<label class="quiz-option quiz-option-any"><input type="' + type + '" name="q-' + s.key + '" data-any="' + s.key + '" value=""' + (noPreference[s.key] ? ' checked' : '') + '><span class="option-icon">' + iconSvg(none[2], none[0]) + '</span><span class="option-copy"><b>' + esc(none[0]) + '</b><small>' + esc(none[1]) + '</small></span><span class="option-check" aria-hidden="true">✓</span></label>';
    var choices = s.options.map(function (o) {
      var checked = state[s.key].indexOf(o[0]) !== -1 ? " checked" : "";
      var mark = s.chainStep
        ? '<span class="option-icon option-chain-mark" style="--chain-tone:' + (CHAIN_TONE[chainKey(o[0])] || '#e3efe8') + '" aria-hidden="true">' + esc(chainInitials(o[0])) + '</span>'
        : '<span class="option-icon">' + iconSvg(o[3], o[1]) + '</span>';
      return '<label class="quiz-option"><input type="' + type + '" name="q-' + s.key + '" data-facet="' + s.key + '" value="' + esc(o[0]) + '"' + checked + '>' + mark + '<span class="option-copy"><b>' + esc(o[1]) + '</b>' + (o[2] ? '<small>' + esc(o[2]) + '</small>' : '') + '</span><span class="option-check" aria-hidden="true">✓</span></label>';
    }).join("");
    return '<div class="quiz-options step-' + s.key + (s.chainStep ? " chain-options" : "") + '">' + noPreferenceOption + choices + '</div>';
  }
  // The card used to be rebuilt with innerHTML on every tap in the goal step,
  // purely so the cutting/bulking warning could appear. Rebuilding replays the
  // .quiz-card entrance animation -- a 0.62s fade and slide of the whole card
  // -- so picking an option looked like the page reloading, and it also threw
  // focus back to the heading on every tap. Both of those are fixed by
  // updating the one paragraph that actually changes.
  function syncConflict() {
    var card = root.querySelector(".quiz-card");
    if (!card) return;
    var s = STEPS[step];
    var conflict = s.key === "goal"
      && state.goal.indexOf("energy") !== -1 && state.goal.indexOf("light") !== -1;
    var warn = card.querySelector(".quiz-warn");
    if (conflict && !warn) {
      warn = document.createElement("p");
      warn.className = "quiz-warn";
      warn.textContent = "Cutting and bulking point in opposite calorie directions."
        + " Keep both if you want; results will clearly show the trade-off.";
      card.insertBefore(warn, card.querySelector(".quiz-nav"));
    } else if (!conflict && warn) {
      warn.parentNode.removeChild(warn);
    }
  }
  function renderStep() {
    var s = STEPS[step], conflict = s.key === "goal" && state.goal.indexOf("energy") !== -1 && state.goal.indexOf("light") !== -1;
    root.innerHTML = '<div class="quiz-card"><div class="quiz-progress-row"><span>Question ' + (step + 1) + ' of ' + STEPS.length + '</span><span>' + Math.round((step + 1) / STEPS.length * 100) + '%</span></div><div class="quiz-progress"><span style="width:' + ((step + 1) / STEPS.length * 100) + '%"></span></div><h2 tabindex="-1">' + esc(s.title) + '</h2><p class="quiz-hint">' + esc(s.hint) + ' Skip a question and we treat it as no preference.</p>' + optionMarkup(s) + (conflict ? '<p class="quiz-warn">Cutting and bulking point in opposite calorie directions. Keep both if you want; results will clearly show the trade-off.</p>' : '') + '<div class="quiz-nav">' + (step ? '<button type="button" class="btn btn-ghost quiz-back" data-go="-1">Back</button>' : '') + '<button type="button" class="btn btn-primary quiz-continue" data-go="1">' + (step === STEPS.length - 1 ? 'Show my matches' : 'Continue') + '</button></div></div>';
    announce("Question " + (step + 1) + " of " + STEPS.length + ": " + s.title);
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
      announce("No meals match that exact combination. Change an answer to continue."); syncUrl(); return;
    }
    var shown = results.slice(0, 5);
    root.innerHTML = '<div class="quiz-results"><div class="results-heading"><div><p class="eyebrow">Your five best matches</p><h2 tabindex="-1">Meals that fit your day</h2><p class="quiz-summary">' + esc(summary(results.length)) + '</p></div><button type="button" class="btn btn-ghost" data-restart="1">Edit answers</button></div><div class="data-quality"><span aria-hidden="true">✓</span><p><b>Complete nutrition only by default.</b> Every result shown has calories, protein, fiber and sodium filled in.</p></div><div class="results-grid">' + shown.map(function (m, i) { return card(m, i === 0); }).join("") + '</div>' + (results.length > shown.length ? '<button type="button" class="btn btn-ghost results-more" data-more="1">See 3 more meals</button>' : '') + '<div class="result-controls"><label class="data-toggle"><input type="checkbox" data-incomplete="1"' + (includeIncomplete ? ' checked' : '') + '><span><b>Include meals with incomplete nutrition data</b><small>' + incompleteCount + ' meals are excluded by default because one or more figures are not published.</small></span></label><button type="button" class="btn btn-ghost" data-share="1">Share results</button></div></div>';
    root._rest = results.slice(5); announce(summary(results.length)); syncUrl(); updateSavedUi();
  }
  function syncUrl() { var url = new URL(location.href); url.search = ""; STEPS.forEach(function (s) { state[s.key].forEach(function (v) { url.searchParams.append(s.key, v); }); }); if (includeIncomplete) url.searchParams.set("complete", "0"); history.replaceState(null, "", url); }
  function shareResults(button) { var data = { title: "My GetMacros meal matches", text: "Fast-food options matched to my goals and preferences.", url: location.href }; if (navigator.share) { navigator.share(data).catch(function () {}); return; } if (navigator.clipboard) navigator.clipboard.writeText(data.url).then(function () { button.textContent = "Link copied ✓"; }); }

  // A question change is the one moment when moving the viewport is helpful:
  // the old card can be taller than the next card on a phone. Reposition only
  // after an explicit Back/Continue/Edit tap, never after loading or selecting
  // an answer.
  function showCurrentQuestion() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        var header = document.querySelector(".site-header");
        var headerHeight = header ? header.getBoundingClientRect().height : 0;
        var top = window.scrollY + root.getBoundingClientRect().top - headerHeight - 12;
        window.scrollTo({ top: Math.max(0, top), left: 0, behavior: reducedMotion() ? "auto" : "smooth" });
      });
    });
  }

  root.addEventListener("change", function (e) {
    var el = e.target;
    var required = root.querySelector(".quiz-required"); if (required) required.hidden = true;
    if (el.dataset.incomplete) { includeIncomplete = el.checked; renderResults(); return; }
    if (el.dataset.any) {
      var anyKey = el.dataset.any;
      state[anyKey] = [];
      noPreference[anyKey] = el.checked;
      // Uncheck the real choices directly. Re-rendering the card to achieve
      // this was the other source of the reload flash.
      var inputs = root.querySelectorAll('[data-facet="' + anyKey + '"]');
      for (var i = 0; i < inputs.length; i++) inputs[i].checked = false;
      syncConflict();
      return;
    }
    if (!el.dataset.facet) return;
    var key = el.dataset.facet;
    noPreference[key] = false;
    if (el.type === "radio") state[key] = el.checked ? [el.value] : [];
    else { var i = state[key].indexOf(el.value); if (el.checked && i === -1) state[key].push(el.value); if (!el.checked && i !== -1) state[key].splice(i, 1); }
    var any = root.querySelector('[data-any="' + key + '"]'); if (any) any.checked = false;
    if (key === "goal") syncConflict();
  });
  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-go],[data-restart],[data-more],[data-save],[data-share]"); if (!t) return;
    if (t.dataset.save) toggleSaved(t.dataset.save);
    else if (t.dataset.share) shareResults(t);
    else if (t.dataset.go) {
      var direction = Number(t.dataset.go);
      var activeStep = STEPS[step];
      // Leaving a question blank means the same thing as picking its
      // no-preference option, so Continue advances either way. Refusing to
      // move made the button look broken on a phone: the tap did nothing
      // visible, and the explanation sat above the fold.
      if (direction > 0 && !state[activeStep.key].length) {
        noPreference[activeStep.key] = true;
      }
      step += direction; step >= STEPS.length ? renderResults() : renderStep();
      showCurrentQuestion();
    }
    else if (t.dataset.restart) { step = 0; renderStep(); showCurrentQuestion(); }
    else if (t.dataset.more) {
      var next = root._rest.splice(0, 3);
      root.querySelector(".results-grid").insertAdjacentHTML("beforeend", next.map(function (m) { return card(m, false); }).join(""));
      if (!root._rest.length) t.remove();
      else t.textContent = "See " + Math.min(3, root._rest.length) + " more meal" + (root._rest.length === 1 ? "" : "s");
      updateSavedUi();
    }
  });
  function reducedMotion() { return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches; }
  deepLinked ? renderResults() : renderStep();
})();
