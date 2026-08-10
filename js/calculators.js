// GetMacros.net calculators
// Formulas used (see /sources.html for full citations):
//  - BMR: Mifflin-St Jeor equation (Mifflin et al., Am J Clin Nutr, 1990)
//  - TDEE: BMR x activity multiplier (Physical Activity Level factors,
//    Dietary Reference Intakes for Energy, National Academies)
//  - Protein target: g per kg body weight, informed by the ISSN Position
//    Stand on protein and exercise (1.4-2.0 g/kg for active individuals)
//  - Fat target: % of total calories within the AMDR (20-35% of calories)
//  - Carbohydrate target: remaining calories after protein and fat

(function () {
  var LB_PER_KG = 2.2046226218;
  var IN_PER_CM = 0.3937007874;

  var ACTIVITY = {
    sedentary: { mult: 1.2, label: "Sedentary (little or no exercise)" },
    light: { mult: 1.375, label: "Lightly active (1-3 days/week)" },
    moderate: { mult: 1.55, label: "Moderately active (3-5 days/week)" },
    active: { mult: 1.725, label: "Very active (6-7 days/week)" },
    athlete: { mult: 1.9, label: "Athlete (2x/day or physical job + training)" }
  };

  var GOALS = {
    lose: { calAdj: -0.2, proteinPerKg: 1.8, label: "Lose fat" },
    maintain: { calAdj: 0, proteinPerKg: 1.6, label: "Maintain weight" },
    gain: { calAdj: 0.12, proteinPerKg: 2.0, label: "Build muscle" }
  };

  function toKg(value, unit) {
    return unit === "lb" ? value / LB_PER_KG : value;
  }
  function toCm(value, unit, inches) {
    if (unit === "ftin") {
      var totalIn = value * 12 + (inches || 0);
      return totalIn / IN_PER_CM;
    }
    return value;
  }

  function mifflinStJeor(sex, weightKg, heightCm, age) {
    var base = 10 * weightKg + 6.25 * heightCm - 5 * age;
    return sex === "male" ? base + 5 : base - 161;
  }

  function fmt(n) {
    return Math.round(n).toLocaleString();
  }

  // ---------- Main macro calculator ----------
  var macroForm = document.getElementById("macro-form");
  if (macroForm) {
    var weightUnitButtons = macroForm.querySelectorAll("[data-weight-unit]");
    var heightUnitButtons = macroForm.querySelectorAll("[data-height-unit]");
    var weightUnit = "lb";
    var heightUnit = "ftin";

    function setUnitGroup(buttons, value, current) {
      buttons.forEach(function (b) {
        b.classList.toggle("active", b.dataset.weightUnit === value || b.dataset.heightUnit === value);
      });
      return value;
    }

    weightUnitButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        weightUnit = setUnitGroup(weightUnitButtons, btn.dataset.weightUnit);
        document.getElementById("weight-unit-label").textContent = weightUnit === "lb" ? "lb" : "kg";
      });
    });
    heightUnitButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        heightUnit = setUnitGroup(heightUnitButtons, btn.dataset.heightUnit);
        document.getElementById("height-cm-field").hidden = heightUnit !== "cm";
        document.getElementById("height-ftin-field").hidden = heightUnit !== "ftin";
      });
    });

    macroForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var errorBox = document.getElementById("macro-error");
      errorBox.hidden = true;
      errorBox.textContent = "";

      var sex = macroForm.elements["sex"].value;
      var age = parseFloat(macroForm.elements["age"].value);
      var weightRaw = parseFloat(macroForm.elements["weight"].value);
      var activityKey = macroForm.elements["activity"].value;
      var goalKey = macroForm.elements["goal"].value;
      var fatPercent = parseFloat(macroForm.elements["fatpercent"].value) / 100;

      var heightCm;
      if (heightUnit === "cm") {
        heightCm = toCm(parseFloat(macroForm.elements["height_cm"].value), "cm");
      } else {
        heightCm = toCm(
          parseFloat(macroForm.elements["height_ft"].value),
          "ftin",
          parseFloat(macroForm.elements["height_in"].value || 0)
        );
      }
      var weightKg = toKg(weightRaw, weightUnit);

      if (!age || age < 14 || age > 100 || !weightKg || weightKg < 30 || weightKg > 300 || !heightCm || heightCm < 120 || heightCm > 230) {
        errorBox.textContent = "Please double-check your inputs — age, weight, and height look out of range.";
        errorBox.hidden = false;
        return;
      }

      var bmr = mifflinStJeor(sex, weightKg, heightCm, age);
      var tdee = bmr * ACTIVITY[activityKey].mult;
      var goal = GOALS[goalKey];
      var totalCals = tdee * (1 + goal.calAdj);

      var proteinG = goal.proteinPerKg * weightKg;
      var proteinCals = proteinG * 4;
      var fatCals = totalCals * fatPercent;
      var fatG = fatCals / 9;
      var carbCals = totalCals - proteinCals - fatCals;

      if (carbCals < 0) {
        errorBox.textContent = "At this fat percentage and calorie level, protein alone exceeds your target calories. Try lowering the fat percentage.";
        errorBox.hidden = false;
        return;
      }
      var carbG = carbCals / 4;

      renderMacroResults({
        bmr: bmr,
        tdee: tdee,
        totalCals: totalCals,
        proteinG: proteinG,
        proteinCals: proteinCals,
        fatG: fatG,
        fatCals: fatCals,
        carbG: carbG,
        carbCals: carbCals
      });
    });

    function renderMacroResults(r) {
      var results = document.getElementById("macro-results");
      results.classList.remove("empty");
      var pPct = Math.round((r.proteinCals / r.totalCals) * 100);
      var fPct = Math.round((r.fatCals / r.totalCals) * 100);
      var cPct = 100 - pPct - fPct;

      results.innerHTML =
        '<div class="result-total">' +
          '<div class="num">' + fmt(r.totalCals) + '</div>' +
          '<div class="label">calories / day &middot; BMR ' + fmt(r.bmr) + ' &middot; TDEE ' + fmt(r.tdee) + '</div>' +
        '</div>' +
        '<div class="macro-bar" aria-hidden="true">' +
          '<span class="protein" style="width:' + pPct + '%"></span>' +
          '<span class="fat" style="width:' + fPct + '%"></span>' +
          '<span class="carbs" style="width:' + cPct + '%"></span>' +
        '</div>' +
        macroRow("protein", "Protein", r.proteinG, r.proteinCals, pPct) +
        macroRow("fat", "Fat", r.fatG, r.fatCals, fPct) +
        macroRow("carbs", "Carbohydrate", r.carbG, r.carbCals, cPct);
    }

    function macroRow(cls, label, grams, cals, pct) {
      return '<div class="macro-result-row">' +
        '<span><span class="dot ' + cls + '"></span>' + label + ' (' + pct + '%)</span>' +
        '<span class="amounts"><span class="grams">' + fmt(grams) + ' g</span><br>' +
        '<span class="cals">' + fmt(cals) + ' cal</span></span>' +
        '</div>';
    }
  }

  // ---------- Quick fat calculator ----------
  var fatForm = document.getElementById("fat-form");
  if (fatForm) {
    fatForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var cals = parseFloat(fatForm.elements["calories"].value);
      var out = document.getElementById("fat-results");
      var errorBox = document.getElementById("fat-error");
      errorBox.hidden = true;

      if (!cals || cals < 800 || cals > 8000) {
        errorBox.textContent = "Enter a daily calorie target between 800 and 8,000.";
        errorBox.hidden = false;
        return;
      }
      out.classList.remove("empty");
      var low = (cals * 0.2) / 9;
      var mid = (cals * 0.275) / 9;
      var high = (cals * 0.35) / 9;
      out.innerHTML =
        '<div class="result-total">' +
          '<div class="num">' + fmt(low) + '&ndash;' + fmt(high) + ' g</div>' +
          '<div class="label">recommended fat per day (20&ndash;35% of calories)</div>' +
        '</div>' +
        '<div class="macro-result-row"><span>Lower bound (20%)</span><span class="amounts"><span class="grams">' + fmt(low) + ' g</span><br><span class="cals">' + fmt(cals * 0.2) + ' cal</span></span></div>' +
        '<div class="macro-result-row"><span>Typical (27.5%)</span><span class="amounts"><span class="grams">' + fmt(mid) + ' g</span><br><span class="cals">' + fmt(cals * 0.275) + ' cal</span></span></div>' +
        '<div class="macro-result-row"><span>Upper bound (35%)</span><span class="amounts"><span class="grams">' + fmt(high) + ' g</span><br><span class="cals">' + fmt(cals * 0.35) + ' cal</span></span></div>';
    });
  }
})();
