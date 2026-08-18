/* Guided fast-food meal quiz.
 *
 * Four questions, asked one at a time, then a ranked answer that explains
 * itself in terms of what the person actually said. Every question is
 * multi-select: "high protein" and "it's a big day" are a normal combination,
 * and an earlier single-choice version forced people to drop one of them.
 *
 * Scoring treats goals as preferences rather than hard filters, so answering
 * more questions sharpens the ranking instead of emptying the page. Only the
 * requirements in step 2 (vegetarian, gluten-aware, ...) actually exclude
 * meals, because those are the answers where a wrong result is not a
 * compromise but a meal someone cannot eat.
 */
(function () {
  "use strict";

  var meals = window.GM_MEALS || [];
  var root = document.getElementById("meal-quiz");
  if (!root || !meals.length) return;

  var chains = [];
  meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
  chains.sort();

  var STEPS = [
    {
      key: "goal",
      title: "What is this meal for?",
      hint: "Pick as many as are true. They stack — protein and a big day is a normal answer.",
      options: [
        ["protein", "I'm training", "Protein first — lifting, or holding on to muscle"],
        ["energy", "It's a big day", "Real fuel, not a small salad"],
        ["light", "Something lighter", "I want to eat and still feel light after"],
        ["fibre", "I want to stay full", "Fibre, so it lasts more than an hour"],
        ["lowsodium", "I'm watching sodium", "Lower published sodium where it's known"],
        ["balanced", "Nothing extreme", "Just a solid, ordinary meal"]
      ]
    },
    {
      key: "diet",
      title: "Anything we need to work around?",
      hint: "These ones we treat as hard rules, not preferences.",
      none: "Nothing to work around",
      options: [
        ["vegetarian", "Vegetarian", "No meat or fish"],
        ["plant", "Plant-based", "No animal products"],
        ["gluten", "Gluten-aware", "No gluten ingredient in the standard build"],
        ["breakfast", "Breakfast", "Served on the breakfast menu"]
      ]
    },
    {
      key: "size",
      title: "How hungry are you, honestly?",
      hint: "This shifts the ranking rather than cutting anything out.",
      none: "Doesn't matter",
      options: [
        ["small", "Barely", "Something small, or a side"],
        ["medium", "Normal hungry", "A regular meal"],
        ["large", "Properly hungry", "A full, substantial plate"]
      ]
    },
    {
      key: "chain",
      title: "Where are you eating?",
      hint: "Leave it open and we'll look across all " + chains.length + ".",
      none: "Anywhere is fine",
      options: chains.map(function (c) { return [c, c, ""]; })
    }
  ];

  var GOAL_LABEL = {
    protein: "more protein", energy: "a bigger, higher-calorie meal",
    light: "something lighter", fibre: "something filling",
    lowsodium: "lower sodium", balanced: "nothing extreme"
  };
  var DIET_LABEL = {
    vegetarian: "vegetarian", plant: "plant-based",
    gluten: "gluten-aware", breakfast: "breakfast"
  };
  var SIZE_LABEL = { small: "small", medium: "normal-sized", large: "large" };

  var state = { goal: [], diet: [], size: [], chain: [] };
  var step = 0;

  // A shared link should reopen on the answers it was shared with.
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

  /* Requirements exclude. Everything else only reorders. */
  function eligible(m) {
    if (state.diet.length && !state.diet.every(function (d) { return has(m, d); })) return false;
    if (state.chain.length && state.chain.indexOf(m.chain) === -1) return false;
    return true;
  }

  function score(m) {
    var s = 0;
    state.goal.forEach(function (g) { if (has(m, g)) s += 45; });
    if (state.size.indexOf(m.size) !== -1) s += 30;
    if (m.p !== null) s += Math.min(m.p, 50) / 2;
    if (m.f !== null) s += Math.min(m.f, 15);
    if (m.p !== null && m.cal) s += (m.p / m.cal) * 120;
    // A meal we cannot fully describe is a weaker recommendation than one we can.
    if (m.na === null || m.p === null) s -= 6;
    return s;
  }

  /* Explain the match using the person's own answers and this meal's numbers. */
  function why(m) {
    var bits = [];
    state.goal.forEach(function (g) {
      if (!has(m, g)) return;
      if (g === "protein" && m.p !== null) bits.push(m.p + " g of protein");
      else if (g === "energy" && m.cal !== null) bits.push(m.cal + " kcal to work with");
      else if (g === "light" && m.cal !== null) bits.push("only " + m.cal + " kcal");
      else if (g === "fibre" && m.f !== null) bits.push(m.f + " g of fibre");
      else if (g === "lowsodium" && m.na !== null) bits.push(m.na.toLocaleString() + " mg sodium");
      else bits.push(GOAL_LABEL[g]);
    });
    if (state.size.indexOf(m.size) !== -1) bits.push("a " + SIZE_LABEL[m.size] + " portion");

    if (!bits.length) return m.why;
    var list = bits.length === 1 ? bits[0]
      : bits.slice(0, -1).join(", ") + " and " + bits[bits.length - 1];
    return "You asked for " + answerPhrase() + ". This one brings " + list + ".";
  }

  function answerPhrase() {
    var parts = state.goal.map(function (g) { return GOAL_LABEL[g]; });
    if (!parts.length) parts.push("a solid option");
    return parts.length === 1 ? parts[0]
      : parts.slice(0, -1).join(", ") + " and " + parts[parts.length - 1];
  }

  function summary(n) {
    var s = "Looking for " + answerPhrase();
    if (state.diet.length) {
      s += ", " + state.diet.map(function (d) { return DIET_LABEL[d]; }).join(" and ");
    }
    if (state.size.length === 1) s += ", " + SIZE_LABEL[state.size[0]] + " portion";
    if (state.chain.length) s += ", at " + state.chain.join(" or ");
    // Only step 2 and the restaurant choice actually exclude anything, so
    // "N meals fit" is only true when one of those is set. Otherwise every
    // meal is still on the table and we have simply put them in order.
    var excluded = state.diet.length || state.chain.length;
    return s + " — " + (excluded
      ? n + (n === 1 ? " meal fits." : " meals fit.")
      : "all " + n + " ranked, closest first.");
  }

  function stat(value, unit, label) {
    return "<span><b>" + (value === null ? "&mdash;" : value.toLocaleString() + unit) +
      "</b>" + label + "</span>";
  }

  function card(m, top) {
    return '<article class="meal-card' + (top ? " top-match" : "") + '">' +
      '<div class="meal-card-top"><span class="meal-chain">' + esc(m.chain) + "</span>" +
      (top ? '<span class="meal-rank">Best match</span>' : "") + "</div>" +
      "<h3>" + esc(m.name) + "</h3>" +
      '<div class="meal-stats">' +
        stat(m.cal, "", "kcal") + stat(m.p, "g", "protein") +
        stat(m.f, "g", "fibre") + stat(m.na, "mg", "sodium") +
      "</div>" +
      "<p>" + esc(why(m)) + "</p>" +
      '<a class="meal-link" href="' + esc(m.url) + '">See the ' + esc(m.chain) +
      " guide &rarr;</a></article>";
  }

  function optionMarkup(s) {
    var multi = s.options.map(function (o) {
      return '<label class="quiz-chip"><input type="checkbox" data-facet="' + s.key +
        '" value="' + esc(o[0]) + '"' +
        (state[s.key].indexOf(o[0]) !== -1 ? " checked" : "") +
        '><span><b>' + esc(o[1]) + "</b>" +
        (o[2] ? "<small>" + esc(o[2]) + "</small>" : "") + "</span></label>";
    }).join("");
    var none = s.none
      ? '<button type="button" class="quiz-skip" data-clear="' + s.key + '">' +
        esc(s.none) + "</button>"
      : "";
    return '<div class="quiz-chips">' + multi + "</div>" + none;
  }

  function renderStep() {
    var s = STEPS[step];
    root.innerHTML =
      '<div class="quiz-card">' +
        '<div class="quiz-progress"><div class="quiz-bar" style="width:' +
          ((step + 1) / STEPS.length * 100) + '%"></div></div>' +
        '<p class="quiz-count">Question ' + (step + 1) + " of " + STEPS.length + "</p>" +
        "<h2>" + esc(s.title) + "</h2>" +
        '<p class="quiz-hint">' + s.hint + "</p>" +
        optionMarkup(s) +
        '<div class="quiz-nav">' +
          (step > 0 ? '<button type="button" class="btn btn-ghost" data-go="-1">Back</button>' : "") +
          '<button type="button" class="btn btn-primary" data-go="1">' +
            (step === STEPS.length - 1 ? "Show my meals" : "Next") + "</button>" +
        "</div>" +
      "</div>";
    var h = root.querySelector("h2");
    if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
  }

  function renderResults() {
    var list = meals.filter(eligible).sort(function (a, b) { return score(b) - score(a); });

    if (!list.length) {
      root.innerHTML =
        '<div class="quiz-card"><h2 tabindex="-1">Nothing matches all of that.</h2>' +
        '<p class="quiz-hint">The requirements in question two have to all be met at once, ' +
        'and that combination runs out fast on a fast-food menu. Loosening one usually opens it up.</p>' +
        '<div class="quiz-nav"><button type="button" class="btn btn-primary" data-restart="1">' +
        "Change my answers</button></div></div>";
      root.querySelector("h2").focus({ preventScroll: true });
      syncUrl();
      return;
    }

    var rest = list.slice(1, 7);
    root.innerHTML =
      '<div class="quiz-results">' +
        '<h2 tabindex="-1">Here is what fits.</h2>' +
        '<p class="quiz-summary">' + esc(summary(list.length)) + "</p>" +
        '<div class="results-grid">' + card(list[0], true) +
          rest.map(function (m) { return card(m, false); }).join("") + "</div>" +
        (list.length > 7
          ? '<button type="button" class="btn btn-ghost" data-more="1">Show the other ' +
            (list.length - 7) + " that fit</button>"
          : "") +
        '<div class="quiz-nav quiz-nav-end">' +
          '<button type="button" class="btn btn-ghost" data-restart="1">Change my answers</button>' +
        "</div>" +
      "</div>";
    root.querySelector("h2").focus({ preventScroll: true });
    root._rest = list.slice(7);
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

  root.addEventListener("change", function (e) {
    var el = e.target;
    if (!el.dataset || !el.dataset.facet) return;
    var arr = state[el.dataset.facet], i = arr.indexOf(el.value);
    if (el.checked && i === -1) arr.push(el.value);
    if (!el.checked && i !== -1) arr.splice(i, 1);
  });

  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-go],[data-clear],[data-restart],[data-more]");
    if (!t) return;

    if (t.dataset.clear) {
      state[t.dataset.clear] = [];
      root.querySelectorAll('input[data-facet="' + t.dataset.clear + '"]')
        .forEach(function (c) { c.checked = false; });
      step++;
      if (step >= STEPS.length) renderResults(); else renderStep();
      return;
    }
    if (t.dataset.go) {
      step += Number(t.dataset.go);
      if (step >= STEPS.length) renderResults();
      else renderStep();
      return;
    }
    if (t.dataset.restart) {
      step = 0;
      renderStep();
      return;
    }
    if (t.dataset.more) {
      var grid = root.querySelector(".results-grid");
      grid.insertAdjacentHTML("beforeend",
        (root._rest || []).map(function (m) { return card(m, false); }).join(""));
      t.remove();
    }
  });

  // A shared or bookmarked link lands straight on its answers.
  if (deepLinked) renderResults(); else renderStep();
})();
