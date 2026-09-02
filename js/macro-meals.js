/* Macros first, then the meals that fit them.
 *
 * Two stages on one page. Stage one works out daily targets from Mifflin-St
 * Jeor. Stage two divides those targets into a single meal's share and ranks
 * real restaurant items against that share, so the answer is "this fits the
 * numbers you just calculated", not "this is generically healthy".
 *
 * The formulas match js/home-calculator.js exactly -- same equation, same
 * activity multipliers, same goal adjustments and protein targets. Two pages
 * that ask for the same details must not report different numbers.
 */
(function () {
  "use strict";

  var meals = window.GM_MEALS || [];
  var math = window.GMMacroMath;
  var root = document.getElementById("macro-meals");
  if (!root || !meals.length) return;

  var GOALS = math && math.GOALS ? math.GOALS : {
    lose: { calorieAdjustment: -.20, proteinPerKg: 1.8, label: "weight loss" },
    recomp: { calorieAdjustment: -.10, proteinPerKg: 2.0, label: "losing fat while building muscle" },
    maintain: { calorieAdjustment: 0, proteinPerKg: 1.6, label: "weight maintenance" },
    gain: { calorieAdjustment: .12, proteinPerKg: 2.0, label: "gaining weight while building muscle" }
  };

  var state = { targets: null, meal: "lunch", diet: [], chain: [], filtersOpen: false };

  // How a day's targets split across eating occasions. Three meals plus a
  // snack is the pattern most people actually eat, so a "meal" is not simply
  // a third of the day.
  var SHARE = {
    breakfast: { of: 0.25, label: "breakfast" },
    lunch:     { of: 0.30, label: "lunch" },
    dinner:    { of: 0.35, label: "dinner" },
    snack:     { of: 0.15, label: "a snack" }
  };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function calc(v) {
    var kg = math ? math.toKg(v.weight, v.unit === "metric" ? "kg" : "lb")
      : (v.unit === "metric" ? v.weight : v.weight * 0.45359237);
    var cm = math ? math.toCm(v.height, v.unit === "metric" ? "cm" : "in")
      : (v.unit === "metric" ? v.height : v.height * 2.54);
    if (!(kg > 0 && cm > 0 && v.age > 0)) return null;
    var g = GOALS[v.goal];
    var result = math ? math.calculate({
      sex: v.sex, age: v.age, weightKg: kg, heightCm: cm,
      activityMultiplier: v.activity, calorieAdjustment: g.calorieAdjustment,
      proteinPerKg: g.proteinPerKg, fatPercent: .3
    }) : null;
    var bmr = result ? result.bmr : 10 * kg + 6.25 * cm - 5 * v.age + (v.sex === "male" ? 5 : -161);
    var tdee = result ? result.tdee : bmr * v.activity;
    var cal = result ? result.totalCals : tdee * (1 + g.calorieAdjustment);
    var protein = result ? result.proteinG : kg * g.proteinPerKg;
    var fat = result ? result.fatG : cal * 0.3 / 9;
    var carbs = result ? Math.max(0, result.carbG) : Math.max(0, (cal - protein * 4 - fat * 9) / 4);
    return {
      bmr: Math.round(bmr), tdee: Math.round(tdee), cal: Math.round(cal),
      protein: Math.round(protein), fat: Math.round(fat), carbs: Math.round(carbs),
      goal: g.label
    };
  }

  function perMeal() {
    var s = SHARE[state.meal], t = state.targets;
    return {
      label: s.label,
      cal: Math.round(t.cal * s.of),
      protein: Math.round(t.protein * s.of),
      pct: Math.round(s.of * 100)
    };
  }

  /* How well one item fits this meal's share. */
  function fit(m, target) {
    if (m.cal === null) return null;
    var calRatio = m.cal / target.cal;               // 1.0 is exactly on budget
    var proteinRatio = m.p === null ? 0 : m.p / target.protein;

    // Going over the calorie share costs more than coming in under it: under
    // budget you can add a side, over budget you cannot un-eat it.
    var calScore = calRatio <= 1
      ? 100 - (1 - calRatio) * 55
      : 100 - (calRatio - 1) * 130;
    var proteinScore = Math.min(proteinRatio, 1.4) / 1.4 * 100;
    var score = calScore * 0.55 + proteinScore * 0.45;
    if (m.p === null) score -= 12;                   // unverifiable is not a win
    return { score: score, calRatio: calRatio, proteinRatio: proteinRatio };
  }

  function eligible(m) {
    if (state.diet.length && !state.diet.every(function (d) {
      return m.diet.indexOf(d) !== -1;
    })) return false;
    if (state.chain.length && state.chain.indexOf(m.chain) === -1) return false;
    if (state.meal === "breakfast" && m.meal !== "breakfast") return false;
    if (state.meal !== "breakfast" && state.meal !== "snack" && m.meal === "breakfast") return false;
    return true;
  }

  function verdict(f, target, m) {
    var over = f.calRatio > 1.15, under = f.calRatio < 0.6;
    var lowP = f.proteinRatio < 0.7;
    if (over) return "About " + Math.round((f.calRatio - 1) * 100) + "% over your " +
      target.label + " calories. Workable if the rest of the day is lighter.";
    if (under) return "Well under the " + target.cal.toLocaleString() +
      " kcal you have for " + target.label + ", so there is room for a side.";
    if (lowP && m.p !== null) return "Lands in your calorie range, but " + m.p +
      " g protein is short of the " + target.protein + " g this meal should carry.";
    return "Fits your " + target.label + " numbers: " + m.cal.toLocaleString() +
      " of " + target.cal.toLocaleString() + " kcal, with " +
      (m.p === null ? "protein not published" : m.p + " g protein against a " + target.protein + " g target") + ".";
  }

  function bar(value, of, cls) {
    var pct = of ? Math.min(value / of * 100, 145) : 0;
    return '<div class="fitbar"><div class="fitbar-fill ' + cls +
      '" style="width:' + Math.min(pct, 100) + '%"></div>' +
      (pct > 100 ? '<div class="fitbar-over" style="width:' + Math.min(pct - 100, 45) + '%"></div>' : "") +
      "</div>";
  }

  function card(m, f, target, top) {
    return '<article class="meal-card' + (top ? " top-match" : "") + '">' +
      '<div class="meal-card-top"><span class="meal-chain">' + esc(m.chain) + "</span>" +
      (top ? '<span class="meal-rank is-full">Best fit</span>' : "") + "</div>" +
      "<h3>" + esc(m.name) + "</h3>" +
      '<div class="fitrow"><span>Calories</span><b>' + m.cal.toLocaleString() +
        " / " + target.cal.toLocaleString() + "</b></div>" + bar(m.cal, target.cal, "is-cal") +
      '<div class="fitrow"><span>Protein</span><b>' +
        (m.p === null ? "&mdash;" : m.p + " / " + target.protein + " g") + "</b></div>" +
        bar(m.p || 0, target.protein, "is-pro") +
      "<p>" + esc(verdict(f, target, m)) + "</p>" +
      '<a class="meal-link" href="' + esc(m.url) + '">' + esc(m.chain) + " guide &rarr;</a>" +
      "</article>";
  }

  function renderForm(err) {
    root.innerHTML =
      '<form class="mm-form" id="mm-form" novalidate>' +
        '<h2>Step 1 &mdash; your numbers</h2>' +
        '<p class="mm-hint">Mifflin-St Jeor, the same equation used across the site. ' +
          "Nothing is sent anywhere; the maths runs in your browser.</p>" +
        '<div class="mm-grid">' +
          '<label>Units<select name="unit"><option value="imperial">lb / in</option>' +
            '<option value="metric">kg / cm</option></select></label>' +
          '<label>Age<input name="age" type="number" inputmode="numeric" min="14" max="100" value="30"></label>' +
          '<label>Sex for the equation<select name="sex">' +
            '<option value="female">Female</option><option value="male">Male</option></select></label>' +
          '<label>Weight<input name="weight" type="number" inputmode="decimal" min="1" value="165"></label>' +
          '<label>Height<input name="height" type="number" inputmode="decimal" min="1" value="68"></label>' +
          '<label>Activity<select name="activity">' +
            '<option value="1.2">Mostly sitting</option>' +
            '<option value="1.375">Light, 1&ndash;3 days a week</option>' +
            '<option value="1.55" selected>Moderate, 3&ndash;5 days</option>' +
            '<option value="1.725">Hard, 6&ndash;7 days</option>' +
            '<option value="1.9">Very hard, or a physical job</option></select></label>' +
          '<label>Goal<select name="goal">' +
            '<option value="lose">Lose weight</option>' +
            '<option value="recomp">Lose fat + build muscle</option>' +
            '<option value="maintain" selected>Maintain weight</option>' +
            '<option value="gain">Gain weight + build muscle</option></select></label>' +
        "</div>" +
        (err ? '<p class="mm-err" role="alert">' + esc(err) + "</p>" : "") +
        '<button class="btn btn-primary mm-go" type="submit">Get my macros</button>' +
      "</form>";
  }

  function renderResults() {
    var t = state.targets, target = perMeal();
    var pool = meals.filter(eligible)
      .map(function (m) { return { m: m, f: fit(m, target) }; })
      .filter(function (x) { return x.f; });
    pool.sort(function (a, b) { return b.f.score - a.f.score; });

    var chains = [];
    meals.forEach(function (m) { if (chains.indexOf(m.chain) === -1) chains.push(m.chain); });
    chains.sort();

    root.innerHTML =
      '<section class="mm-targets" aria-labelledby="mm-targets-h">' +
        '<h2 id="mm-targets-h" tabindex="-1">Your daily targets</h2>' +
        '<div class="mm-numbers">' +
          '<div class="mm-num is-cal"><b>' + t.cal.toLocaleString() + "</b><span>calories</span></div>" +
          '<div class="mm-num is-pro"><b>' + t.protein + "g</b><span>protein</span></div>" +
          '<div class="mm-num is-carb"><b>' + t.carbs + "g</b><span>carbs</span></div>" +
          '<div class="mm-num is-fat"><b>' + t.fat + "g</b><span>fat</span></div>" +
        "</div>" +
        '<p class="mm-hint">BMR ' + t.bmr.toLocaleString() + " kcal, estimated daily burn " +
          t.tdee.toLocaleString() + " kcal, adjusted for " + t.goal + ". " +
          '<button type="button" class="link-btn" data-edit="1">Change my details</button></p>' +
      "</section>" +
      '<section class="mm-picker" aria-labelledby="mm-picker-h">' +
        '<h2 id="mm-picker-h">Step 2 &mdash; which meal are you buying?</h2>' +
        '<p class="mm-hint">A day splits unevenly across eating occasions, so a meal is not ' +
          "simply a third of your target. This is the share we match against.</p>" +
        '<div class="mm-chips">' +
          Object.keys(SHARE).map(function (k) {
            return '<button type="button" class="mm-chip' + (state.meal === k ? " is-on" : "") +
              '" data-meal="' + k + '"><b>' + esc(SHARE[k].label.replace("a ", "")) +
              "</b><small>" + Math.round(SHARE[k].of * 100) + "% of the day</small></button>";
          }).join("") +
        "</div>" +
        '<p class="mm-budget">Your ' + target.label + " budget: <b>" +
          target.cal.toLocaleString() + " kcal</b> and <b>" + target.protein +
          " g protein</b>.</p>" +
        '<details class="mm-filters"' + (state.filtersOpen ? " open" : "") +
          '><summary>Dietary needs and restaurants</summary>' +
          '<div class="mm-chips">' +
            [["vegetarian", "Vegetarian"], ["plant", "Plant-based"], ["gluten", "No gluten"]]
              .map(function (d) {
                return '<button type="button" class="mm-chip' +
                  (state.diet.indexOf(d[0]) !== -1 ? " is-on" : "") +
                  '" data-diet="' + d[0] + '"><b>' + d[1] + "</b></button>";
              }).join("") +
          "</div><div class='mm-chips'>" +
            chains.map(function (c) {
              return '<button type="button" class="mm-chip' +
                (state.chain.indexOf(c) !== -1 ? " is-on" : "") +
                '" data-chain="' + esc(c) + '"><b>' + esc(c) + "</b></button>";
            }).join("") +
          "</div></details>" +
      "</section>" +
      '<section class="mm-results" aria-labelledby="mm-results-h" aria-live="polite">' +
        '<h2 id="mm-results-h">Meals that fit that</h2>' +
        (pool.length
          ? '<p class="mm-hint">' + pool.length + " item" + (pool.length === 1 ? "" : "s") +
            " ranked by how closely they land on your " + target.label + " numbers.</p>" +
            '<div class="results-grid">' +
              pool.slice(0, 6).map(function (x, i) {
                return card(x.m, x.f, target, i === 0);
              }).join("") +
            "</div>" +
            (pool.length > 6 ? '<button type="button" class="btn btn-ghost" data-more="1">' +
              "Show the other " + (pool.length - 6) + "</button>" : "")
          : '<p class="quiz-warn">Nothing on the menu matches those restrictions for ' +
            esc(target.label) + ". Loosening one usually opens it back up.</p>") +
      "</section>";
    root._rest = pool.slice(6);
    root._target = target;
  }

  root.addEventListener("submit", function (e) {
    e.preventDefault();
    var fd = new FormData(e.target);
    var v = {
      unit: fd.get("unit"), sex: fd.get("sex"),
      age: parseFloat(fd.get("age")), weight: parseFloat(fd.get("weight")),
      height: parseFloat(fd.get("height")), activity: parseFloat(fd.get("activity")),
      goal: fd.get("goal")
    };
    var t = calc(v);
    if (!t) { renderForm("Check the age, weight and height boxes — one of them is empty or zero."); return; }
    state.targets = t;
    renderResults();
  });

  root.addEventListener("toggle", function (e) {
    if (e.target.classList.contains("mm-filters")) state.filtersOpen = e.target.open;
  }, true);

  root.addEventListener("click", function (e) {
    var t = e.target.closest("[data-meal],[data-diet],[data-chain],[data-more],[data-edit]");
    if (!t) return;
    if (t.dataset.edit) { renderForm(); return; }
    if (t.dataset.more) {
      root.querySelector(".results-grid").insertAdjacentHTML("beforeend",
        (root._rest || []).map(function (x) {
          return card(x.m, x.f, root._target, false);
        }).join(""));
      t.remove();
      return;
    }
    if (t.dataset.meal) state.meal = t.dataset.meal;
    if (t.dataset.diet) {
      var i = state.diet.indexOf(t.dataset.diet);
      if (i === -1) state.diet.push(t.dataset.diet); else state.diet.splice(i, 1);
    }
    if (t.dataset.chain) {
      var j = state.chain.indexOf(t.dataset.chain);
      if (j === -1) state.chain.push(t.dataset.chain); else state.chain.splice(j, 1);
    }
    renderResults();
  });

  renderForm();
})();
