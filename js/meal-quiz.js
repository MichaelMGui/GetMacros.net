/* Guided fast-food meal quiz.
 *
 * Four questions, each with one job:
 *
 *   1. occasion    - breakfast or a main meal. This is when you are eating,
 *                    which is why it is its own question. An earlier version
 *                    listed "breakfast" among vegetarian and gluten-aware,
 *                    filing a time of day as something people cannot eat.
 *   2. restriction - the only answers that actually remove meals, because a
 *                    wrong result here is not a compromise, it is a meal
 *                    someone cannot order.
 *   3. priority    - what you want out of it. Multi-select and additive: these
 *                    reorder the list rather than cutting it down, so a fourth
 *                    answer sharpens the ranking instead of emptying the page.
 *   4. place       - where you are. Skippable, and skipping is the default.
 *
 * Option labels carry the actual thresholds ("25 g or more"), read from
 * GM_THRESHOLDS, which is the same source the tags are derived from. A label
 * cannot promise a number the data does not apply.
 */
(function () {
  "use strict";

  var meals = window.GM_MEALS || [];
  var T = window.GM_THRESHOLDS || {};
  var root = document.getElementById("meal-quiz");
  if (!root || !meals.length) return;

  var chains = [];
  meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
  chains.sort();

  var STEPS = [
    {
      key: "meal", single: true,
      title: "What meal is this?",
      hint: "Breakfast menus are a different set of items at most chains.",
      options: [
        ["main", "Lunch or dinner", "The main menu"],
        ["breakfast", "Breakfast", "Breakfast menu only"]
      ],
      none: "Either is fine"
    },
    {
      key: "diet",
      title: "Anything you don't eat?",
      hint: "These are the only answers that rule meals out. Everything else just changes the order.",
      options: [
        ["vegetarian", "No meat or fish", "Vegetarian"],
        ["plant", "No animal products", "Plant-based"],
        ["gluten", "No gluten", "No gluten ingredient in the standard build"]
      ],
      none: "Nothing to avoid"
    },
    {
      key: "goal",
      title: "What do you want out of it?",
      hint: "Pick as many as apply. These rank the list rather than cut it down.",
      options: [
        ["protein", "High protein", T.protein + " g or more"],
        ["energy", "A big meal", T.energy + " kcal or more"],
        ["light", "Something light", T.light + " kcal or less"],
        ["fibre", "Filling", T.fibre + " g fibre or more"],
        ["lowsodium", "Lower sodium", T.sodium + " mg or less"],
        ["balanced", "Nothing extreme", "A normal-sized meal with real protein"]
      ],
      none: "No preference"
    },
    {
      key: "chain",
      title: "Where are you eating?",
      hint: "Skip this and we look across all " + chains.length + " chains.",
      options: chains.map(function (c) { return [c, c, ""]; }),
      none: "Anywhere"
    }
  ];

  // Answers that cannot both be satisfied by one meal.
  var CONFLICTS = [
    ["light", "energy", "A meal cannot be both under " + T.light + " kcal and over " +
      T.energy + ". We will show the best of each rather than pretend."]
  ];

  var GOAL_LABEL = {
    protein: "high protein", energy: "a big meal", light: "something light",
    fibre: "something filling", lowsodium: "lower sodium", balanced: "nothing extreme"
  };
  var DIET_LABEL = { vegetarian: "vegetarian", plant: "plant-based", gluten: "gluten-free" };

  var state = { meal: [], diet: [], goal: [], chain: [] };
  var step = 0;

  var qs = new URLSearchParams(location.search);
  var deepLinked = false;
  STEPS.forEach(function (s) {
    var allowed = s.options.map(function (o) { return o[0]; });
    qs.getAll(s.key).forEach(function (v) {
      if (allowed.indexOf(v) !== -1 && state[s.key].indexOf(v) === -1) {
        state[s.key].push(v);
        deepLinked = true;
      }
    });
  });

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function has(m, tag) { return m.t.indexOf(tag) !== -1; }
  function list(a) {
    return a.length < 2 ? (a[0] || "") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1];
  }

  /* Only restrictions, occasion and place remove anything. */
  function eligible(m) {
    if (state.meal.length && state.meal.indexOf(m.meal) === -1) return false;
    if (state.diet.length && !state.diet.every(function (d) {
      return m.diet.indexOf(d) !== -1;
    })) return false;
    if (state.chain.length && state.chain.indexOf(m.chain) === -1) return false;
    return true;
  }

  function score(m) {
    var s = 0;
    state.goal.forEach(function (g) { if (has(m, g)) s += 50; });
    if (m.p !== null) s += Math.min(m.p, 50) / 2;
    if (m.f !== null) s += Math.min(m.f, 15);
    if (m.p !== null && m.cal) s += (m.p / m.cal) * 120;
    if (m.na === null || m.p === null) s -= 6;
    return s;
  }

  function metRatio(m) {
    if (!state.goal.length) return 1;
    var met = state.goal.filter(function (g) { return has(m, g); }).length;
    return met / state.goal.length;
  }

  /* Say what this meal delivers, and say plainly what it misses. */
  function why(m) {
    var met = [], missed = [];
    state.goal.forEach(function (g) {
      if (has(m, g)) {
        if (g === "protein" && m.p !== null) met.push(m.p + " g protein");
        else if (g === "energy" && m.cal !== null) met.push(m.cal + " kcal");
        else if (g === "light" && m.cal !== null) met.push("just " + m.cal + " kcal");
        else if (g === "fibre" && m.f !== null) met.push(m.f + " g fibre");
        else if (g === "lowsodium" && m.na !== null) met.push(m.na.toLocaleString() + " mg sodium");
        else met.push(GOAL_LABEL[g]);
      } else {
        missed.push(GOAL_LABEL[g]);
      }
    });
    if (!met.length && !missed.length) return m.why;

    var s = met.length ? "Gives you " + list(met) + "." : "";
    if (missed.length) {
      s += (s ? " " : "") + "Does not hit " + list(missed) + ".";
    }
    return s || m.why;
  }

  function activeConflicts() {
    return CONFLICTS.filter(function (c) {
      return state.goal.indexOf(c[0]) !== -1 && state.goal.indexOf(c[1]) !== -1;
    });
  }

  function summary(n, relaxed) {
    var bits = [];
    if (state.meal.length === 1) bits.push(state.meal[0] === "breakfast" ? "breakfast" : "a main meal");
    if (state.diet.length) bits.push(list(state.diet.map(function (d) { return DIET_LABEL[d]; })));
    if (state.goal.length) bits.push(list(state.goal.map(function (g) { return GOAL_LABEL[g]; })));
    if (state.chain.length) bits.push("at " + list(state.chain));

    if (!bits.length) return "No answers given. All " + n + " meals, best first.";
    var head = "You asked for " + list(bits) + ".";
    if (relaxed) return head + " Nothing hits that, so here is the closest we have.";
    return head + " " + n + (n === 1 ? " meal fits" : " meals fit") + ".";
  }

  function stat(v, unit, label) {
    return "<span><b>" + (v === null ? "&mdash;" : v.toLocaleString() + unit) +
      "</b>" + label + "</span>";
  }

  function card(m, top) {
    var ratio = metRatio(m);
    var badge = !state.goal.length ? ""
      : ratio === 1 ? '<span class="meal-rank is-full">Matches everything</span>'
      : '<span class="meal-rank is-part">Matches ' +
        state.goal.filter(function (g) { return has(m, g); }).length +
        " of " + state.goal.length + "</span>";
    return '<article class="meal-card' + (top ? " top-match" : "") + '">' +
      '<div class="meal-card-top"><span class="meal-chain">' + esc(m.chain) + "</span>" +
      badge + "</div><h3>" + esc(m.name) + "</h3>" +
      '<div class="meal-stats">' + stat(m.cal, "", "kcal") + stat(m.p, "g", "protein") +
        stat(m.f, "g", "fibre") + stat(m.na, "mg", "sodium") + "</div>" +
      "<p>" + esc(why(m)) + "</p>" +
      '<a class="meal-link" href="' + esc(m.url) + '">' + esc(m.chain) +
      " guide &rarr;</a></article>";
  }

  function optionMarkup(s) {
    var type = s.single ? "radio" : "checkbox";
    return '<div class="quiz-chips">' + s.options.map(function (o) {
      return '<label class="quiz-chip"><input type="' + type + '" name="q-' + s.key +
        '" data-facet="' + s.key + '" value="' + esc(o[0]) + '"' +
        (state[s.key].indexOf(o[0]) !== -1 ? " checked" : "") +
        '><span><b>' + esc(o[1]) + "</b>" +
        (o[2] ? "<small>" + esc(o[2]) + "</small>" : "") + "</span></label>";
    }).join("") + "</div>" +
    '<button type="button" class="quiz-skip" data-clear="' + s.key + '">' +
      esc(s.none) + "</button>";
  }

  function renderStep() {
    var s = STEPS[step];
    var warn = s.key === "goal" ? activeConflicts() : [];
    root.innerHTML =
      '<div class="quiz-card">' +
        '<div class="quiz-progress"><div class="quiz-bar" style="width:' +
          ((step + 1) / STEPS.length * 100) + '%"></div></div>' +
        '<p class="quiz-count">Question ' + (step + 1) + " of " + STEPS.length + "</p>" +
        "<h2>" + esc(s.title) + "</h2>" +
        '<p class="quiz-hint">' + esc(s.hint) + "</p>" +
        optionMarkup(s) +
        (warn.length ? '<p class="quiz-warn">' + esc(warn[0][2]) + "</p>" : "") +
        '<div class="quiz-nav">' +
          (step > 0 ? '<button type="button" class="btn btn-ghost" data-go="-1">Back</button>' : "") +
          '<button type="button" class="btn btn-primary" data-go="1">' +
            (step === STEPS.length - 1 ? "See my meals" : "Next") + "</button>" +
        "</div></div>";
    focusHeading();
  }

  function focusHeading() {
    var h = root.querySelector("h2");
    if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  }

  function renderResults() {
    var all = meals.filter(eligible);
    all.sort(function (a, b) { return score(b) - score(a); });

    if (!all.length) {
      root.innerHTML =
        '<div class="quiz-card"><h2>Nothing matches all of that.</h2>' +
        '<p class="quiz-hint">The answers to the first two questions have to all be ' +
        'met at once, and that combination runs out quickly on a fast-food menu. ' +
        'Loosening one usually opens it back up.</p>' +
        '<div class="quiz-nav"><button type="button" class="btn btn-primary" ' +
        'data-restart="1">Change my answers</button></div></div>';
      focusHeading();
      syncUrl();
      return;
    }

    // A meal that satisfies none of the stated priorities is not a result, it
    // is filler. Keep only meals that hit at least one, and fall back to the
    // full eligible list only when nothing hits anything.
    var hits = all.filter(function (m) { return metRatio(m) > 0; });
    var relaxed = state.goal.length > 0 && hits.length === 0;
    var results = state.goal.length && hits.length ? hits : all;

    // Say so plainly when no single meal satisfies every priority at once.
    var perfect = results.filter(function (m) { return metRatio(m) === 1; });
    var note = "";
    if (state.goal.length && !perfect.length) {
      note = '<p class="quiz-warn">' + (state.goal.length === 1
        ? "Nothing on this list reaches " + esc(GOAL_LABEL[state.goal[0]]) +
          ". These are the closest, and each card says what it misses."
        : "No single meal hits all " + state.goal.length +
          " at once. These come closest, and each card says what it misses.") +
        "</p>";
    }

    var shown = results.slice(0, 6);
    root.innerHTML =
      '<div class="quiz-results"><h2>Here is what fits.</h2>' +
        '<p class="quiz-summary">' + esc(summary(results.length, relaxed)) + "</p>" + note +
        '<div class="results-grid">' +
          card(shown[0], true) +
          shown.slice(1).map(function (m) { return card(m, false); }).join("") +
        "</div>" +
        (results.length > 6
          ? '<button type="button" class="btn btn-ghost" data-more="1">Show the other ' +
            (results.length - 6) + "</button>"
          : "") +
        '<div class="quiz-nav quiz-nav-end">' +
          '<button type="button" class="btn btn-ghost" data-restart="1">Change my answers</button>' +
        "</div></div>";
    focusHeading();
    root._rest = results.slice(6);
    syncUrl();
  }

  function syncUrl() {
    var url = new URL(location.href);
    url.search = "";
    STEPS.forEach(function (s) {
      state[s.key].forEach(function (v) { url.searchParams.append(s.key, v); });
    });
    history.replaceState(null, "", url);
  }

  function advance(delta) {
    step += delta;
    if (step >= STEPS.length) renderResults();
    else renderStep();
  }

  root.addEventListener("change", function (e) {
    var el = e.target;
    if (!el.dataset || !el.dataset.facet) return;
    var key = el.dataset.facet;
    if (el.type === "radio") {
      state[key] = el.checked ? [el.value] : [];
    } else {
      var arr = state[key], i = arr.indexOf(el.value);
      if (el.checked && i === -1) arr.push(el.value);
      if (!el.checked && i !== -1) arr.splice(i, 1);
    }
    // Re-render the step only where the answer changes what the step shows.
    if (key === "goal") {
      var warn = root.querySelector(".quiz-warn");
      var conflict = activeConflicts();
      if (conflict.length && !warn) renderStep();
      else if (!conflict.length && warn) warn.remove();
    }
  });

  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-go],[data-clear],[data-restart],[data-more]");
    if (!t) return;
    if (t.dataset.clear) {
      state[t.dataset.clear] = [];
      root.querySelectorAll('input[data-facet="' + t.dataset.clear + '"]')
        .forEach(function (c) { c.checked = false; });
      advance(1);
    } else if (t.dataset.go) {
      advance(Number(t.dataset.go));
    } else if (t.dataset.restart) {
      step = 0;
      renderStep();
    } else if (t.dataset.more) {
      root.querySelector(".results-grid").insertAdjacentHTML("beforeend",
        (root._rest || []).map(function (m) { return card(m, false); }).join(""));
      t.remove();
    }
  });

  if (deepLinked) renderResults(); else renderStep();
})();
