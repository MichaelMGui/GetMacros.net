/* A compact, restaurant-only matcher used inside every chain guide. */
(function () {
  "use strict";

  var meals = window.GM_MEALS || [];
  var roots = document.querySelectorAll("[data-chain-finder]");
  if (!roots.length || !meals.length) return;

  function key(value) {
    return String(value || "").replace(/[\u2018\u2019\u02bc]/g, "'").toLowerCase();
  }
  function esc(value) {
    return String(value).replace(/[&<>\"]/g, function (character) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '\"': "&quot;" }[character];
    });
  }
  function complete(meal) {
    return meal.cal !== null && meal.p !== null && meal.f !== null && meal.na !== null;
  }
  function value(number) {
    return number === null ? null : Number(number);
  }
  function score(meal, goal, size) {
    var calories = value(meal.cal), protein = value(meal.p), fibre = value(meal.f), sodium = value(meal.na);
    var result = complete(meal) ? 18 : -18;
    if (size && meal.size === size) result += 35;
    if (protein !== null) result += Math.min(protein, 60) * 0.45;
    if (calories && protein !== null) result += protein / calories * 100;

    if (goal === "protein") result += protein === null ? -80 : protein * 2.6;
    else if (goal === "light") {
      result += calories === null ? -80 : Math.max(-100, 90 - Math.abs(calories - 375) * 0.22);
      if (protein !== null) result += protein * 1.25;
    } else if (goal === "energy") {
      result += calories === null ? -80 : Math.min(calories, 1100) * 0.13;
      if (protein !== null) result += protein * 1.2;
    } else if (goal === "fibre") result += fibre === null ? -90 : fibre * 8;
    else if (goal === "lowsodium") {
      result += sodium === null ? -120 : Math.max(-80, 95 - sodium * 0.07);
      if (calories !== null && calories < 220) result -= 45;
    } else {
      if (calories !== null) result += Math.max(-40, 45 - Math.abs(calories - 525) * 0.08);
      if (fibre !== null) result += Math.min(fibre, 15) * 2;
    }
    return result;
  }
  function explanation(meal, goal) {
    var cal = meal.cal === null ? "calories not published" : meal.cal.toLocaleString() + " calories";
    var protein = meal.p === null ? "protein not published" : meal.p.toLocaleString() + " g protein";
    if (goal === "protein") return protein + " in a " + cal + " order.";
    if (goal === "light") return cal + " with " + protein + "; ranked against other substantial orders here.";
    if (goal === "energy") return cal + " and " + protein + " for a larger-appetite option.";
    if (goal === "fibre") return (meal.f === null ? "Fiber is not published" : meal.f.toLocaleString() + " g fiber") + ", with " + protein + ".";
    if (goal === "lowsodium") return (meal.na === null ? "Sodium is not published" : meal.na.toLocaleString() + " mg sodium") + "; compare the full nutrition row before ordering.";
    return cal + ", " + protein + (meal.f === null ? "." : " and " + meal.f.toLocaleString() + " g fiber.");
  }
  function metric(number, unit, label) {
    var shown = number === null ? "Not listed" : Number(number).toLocaleString() + unit;
    return '<span class="chain-result-metric' + (number === null ? ' is-missing' : '') + '"><b>' + shown + '</b><small>' + label + '</small></span>';
  }
  function card(meal, index, goal) {
    return '<article class="chain-result-card' + (index === 0 ? ' is-best' : '') + '"><div class="chain-result-top"><span>' + (index === 0 ? 'Closest match' : 'Also fits') + '</span><b>0' + (index + 1) + '</b></div><h3>' + esc(meal.name) + '</h3><div class="chain-result-metrics">' + metric(meal.cal, '', 'calories') + metric(meal.p, 'g', 'protein') + metric(meal.f, 'g', 'fiber') + metric(meal.na, 'mg', 'sodium') + '</div><p>' + esc(explanation(meal, goal)) + '</p></article>';
  }

  roots.forEach(function (root) {
    var chain = root.getAttribute("data-chain") || "this restaurant";
    var form = root.querySelector("[data-chain-form]");
    var output = root.querySelector("[data-chain-results]");
    var chainMeals = meals.filter(function (meal) { return key(meal.chain) === key(chain); });
    if (!form || !output || !chainMeals.length) return;

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = new FormData(form);
      var goal = data.get("chain-goal") || "balanced";
      var size = data.get("chain-size") || "";
      var diet = data.get("chain-diet") || "";
      var results = chainMeals.filter(function (meal) {
        return !diet || (meal.diet || []).indexOf(diet) !== -1;
      }).sort(function (a, b) { return score(b, goal, size) - score(a, goal, size); });

      if (!results.length) {
        output.innerHTML = '<div class="chain-empty"><h3>No standard build here matches that dietary filter.</h3><p>Try removing the filter. Then confirm ingredients and cross-contact directly with ' + esc(chain) + '.</p></div>';
      } else {
        var shown = results.slice(0, 3);
        output.innerHTML = '<div class="chain-results-head"><div><p class="eyebrow">Your ' + esc(chain) + ' matches</p><h3>' + (shown.length === 1 ? 'The closest meal in this guide' : 'The three closest meals in this guide') + '</h3></div><p>Rankings compare only the standard builds tracked on this page. Check the live menu before ordering.</p></div><div class="chain-result-grid">' + shown.map(function (meal, index) { return card(meal, index, goal); }).join("") + '</div>';
      }
      output.hidden = false;
    });
  });
})();
