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
  var MacroMath = window.GMMacroMath;
  var LB_PER_KG = 2.2046226218;
  var IN_PER_CM = 0.3937007874;

  var ACTIVITY = {
    sedentary: { mult: 1.2, label: "Sedentary (little or no exercise)" },
    light: { mult: 1.375, label: "Lightly active (1-3 days/week)" },
    moderate: { mult: 1.55, label: "Moderately active (3-5 days/week)" },
    active: { mult: 1.725, label: "Very active (6-7 days/week)" },
    athlete: { mult: 1.9, label: "Athlete (2x/day or physical job + training)" }
  };

  var GOALS = MacroMath && MacroMath.GOALS ? MacroMath.GOALS : {
    lose: { calorieAdjustment: -.20, proteinPerKg: 1.8, label: "weight loss" },
    recomp: { calorieAdjustment: -.10, proteinPerKg: 2.0, label: "losing fat while building muscle" },
    maintain: { calorieAdjustment: 0, proteinPerKg: 1.6, label: "weight maintenance" },
    gain: { calorieAdjustment: .12, proteinPerKg: 2.0, label: "gaining weight while building muscle" }
  };

  function toKg(value, unit) {
    return MacroMath ? MacroMath.toKg(value, unit) : (unit === "lb" ? value / LB_PER_KG : value);
  }
  function toCm(value, unit, inches) {
    if (MacroMath) return MacroMath.toCm(value, unit, inches);
    if (unit === "ftin") {
      var totalIn = value * 12 + (inches || 0);
      return totalIn / IN_PER_CM;
    }
    return value;
  }

  function mifflinStJeor(sex, weightKg, heightCm, age) {
    if (MacroMath) return MacroMath.mifflinStJeor(sex, weightKg, heightCm, age);
    var base = 10 * weightKg + 6.25 * heightCm - 5 * age;
    return sex === "male" ? base + 5 : base - 161;
  }

  function fmt(n) {
    return Math.round(n).toLocaleString();
  }

  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function animateCount(el, target, suffix) {
    if (reduceMotion || !el) {
      if (el) el.textContent = fmt(target) + (suffix || "");
      return;
    }
    var start = performance.now();
    var duration = 700;
    function step(now) {
      var p = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(target * eased) + (suffix || "");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  function animateBars(container) {
    var bars = container.querySelectorAll("[data-target-width]");
    if (reduceMotion || document.documentElement.classList.contains('tide-motion-off')) {
      bars.forEach(function (bar) { bar.style.width = bar.getAttribute('data-target-width') + '%'; });
      return;
    }
    bars.forEach(function (b) {
      b.style.width = "0%";
    });
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        bars.forEach(function (b) {
          b.style.width = b.getAttribute("data-target-width") + "%";
        });
      });
    });
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
        var active = b.dataset.weightUnit === value || b.dataset.heightUnit === value;
        b.classList.toggle("active", active);
        b.setAttribute("aria-pressed", String(active));
      });
      return value;
    }

    weightUnitButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var input = document.getElementById("weight");
        var nextUnit = btn.dataset.weightUnit;
        if (nextUnit !== weightUnit && input.value !== "" && Number.isFinite(Number(input.value))) {
          var kg = toKg(Number(input.value), weightUnit);
          input.value = (nextUnit === "lb" ? kg * LB_PER_KG : kg).toFixed(1);
        }
        weightUnit = setUnitGroup(weightUnitButtons, btn.dataset.weightUnit);
        document.getElementById("weight-unit-label").textContent = weightUnit === "lb" ? "lb" : "kg";
      });
    });
    function setHeightUnit(unit) {
      if (unit !== heightUnit) {
        var feet = document.getElementById("height-ft"), inches = document.getElementById("height-in"), cm = document.getElementById("height-cm");
        if (unit === "cm" && feet.value !== "") cm.value = Math.round(toCm(Number(feet.value), "ftin", Number(inches.value)));
        else if (unit === "ftin" && cm.value !== "") {
          var totalInches = Math.round(Number(cm.value) * IN_PER_CM);
          feet.value = Math.floor(totalInches / 12);
          inches.value = totalInches % 12;
        }
      }
      heightUnit = setUnitGroup(heightUnitButtons, unit);
      var cmField = document.getElementById("height-cm-field");
      var feetField = document.getElementById("height-ftin-field");
      var useCm = heightUnit === "cm";
      cmField.hidden = !useCm;
      feetField.hidden = useCm;
      document.getElementById("height-cm").disabled = !useCm;
      document.getElementById("height-cm").required = useCm;
      document.getElementById("height-ft").disabled = useCm;
      document.getElementById("height-ft").required = !useCm;
      document.getElementById("height-in").disabled = useCm;
      heightUnitButtons.forEach(function (button) {
        button.setAttribute("aria-pressed", String(button.dataset.heightUnit === heightUnit));
      });
    }
    heightUnitButtons.forEach(function (btn) {
      btn.addEventListener("click", function () { setHeightUnit(btn.dataset.heightUnit); });
    });
    setHeightUnit("ftin");
    setUnitGroup(weightUnitButtons, "lb");

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
      var fatPercent = 0.3; // AMDR midpoint (20-35% of calories); adjust with the quick fat calculator below

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

      if (!age || age < 18 || age > 100 || !weightKg || weightKg < 30 || weightKg > 300 || !heightCm || heightCm < 120 || heightCm > 230) {
        errorBox.textContent = "Please double-check your inputs — age, weight, and height look out of range.";
        errorBox.hidden = false;
        return;
      }

      var goal = GOALS[goalKey];
      var calculated = MacroMath ? MacroMath.calculate({
        sex: sex, age: age, weightKg: weightKg, heightCm: heightCm,
        activityMultiplier: ACTIVITY[activityKey].mult,
        calorieAdjustment: goal.calorieAdjustment, proteinPerKg: goal.proteinPerKg,
        fatPercent: fatPercent
      }) : null;
      var bmr = calculated ? calculated.bmr : mifflinStJeor(sex, weightKg, heightCm, age);
      var tdee = calculated ? calculated.tdee : bmr * ACTIVITY[activityKey].mult;
      var totalCals = calculated ? calculated.totalCals : tdee * (1 + goal.calorieAdjustment);
      var proteinG = calculated ? calculated.proteinG : goal.proteinPerKg * weightKg;
      var proteinCals = calculated ? calculated.proteinCals : proteinG * 4;
      var fatCals = calculated ? calculated.fatCals : totalCals * fatPercent;
      var fatG = calculated ? calculated.fatG : fatCals / 9;
      var carbCals = calculated ? calculated.carbCals : totalCals - proteinCals - fatCals;

      if (carbCals < 0) {
        errorBox.textContent = "Your protein target alone exceeds your calorie target at this weight and goal. This is rare — double-check your weight and activity level.";
        errorBox.hidden = false;
        return;
      }
      var carbG = calculated ? calculated.carbG : carbCals / 4;

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
          '<div class="num" data-count="' + r.totalCals + '">' + fmt(r.totalCals) + '</div>' +
          '<div class="label">calories per day</div>' +
        '</div>' +
        '<div class="macro-bar" aria-hidden="true">' +
          '<span class="protein" data-target-width="' + pPct + '" style="width:0%"></span>' +
          '<span class="fat" data-target-width="' + fPct + '" style="width:0%"></span>' +
          '<span class="carbs" data-target-width="' + cPct + '" style="width:0%"></span>' +
        '</div>' +
        macroRow("protein", "Protein", r.proteinG, r.proteinCals, pPct) +
        macroRow("fat", "Fat", r.fatG, r.fatCals, fPct) +
        macroRow("carbs", "Carbohydrate", r.carbG, r.carbCals, cPct) +
        '<details class="work-result-note"><summary>How this estimate is calculated</summary><p>Estimated resting needs: ' + fmt(r.bmr) + ' calories. Estimated daily energy use, including activity: ' + fmt(r.tdee) + ' calories. Your selected goal adjusts the daily target.</p></details>';

      animateCount(results.querySelector(".num"), r.totalCals);
      results.querySelectorAll(".grams").forEach(function (el) {
        animateCount(el, parseFloat(el.getAttribute("data-count")), " g");
      });
      animateBars(results);
    }

    function macroRow(cls, label, grams, cals, pct) {
      return '<div class="macro-result-row">' +
        '<span><span class="dot ' + cls + '"></span>' + label + ' (' + pct + '%)</span>' +
        '<span class="amounts"><span class="grams" data-count="' + grams + '">' + fmt(grams) + ' g</span><br>' +
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

      var high = (cals * 0.35) / 9;
      out.innerHTML =
        '<div class="result-total">' +
          '<div class="num">' + fmt(low) + '&ndash;' + fmt(high) + ' g</div>' +
          '<div class="label">fat per day (20&ndash;35% of calories)</div>' +
        '</div>';
    });
  }

  // ---------- Standalone protein calculator ----------
  // Ranges match the reference table on how-much-protein-per-day.html:
  // RDA baseline 0.8 g/kg, generally active 1.2-1.6 g/kg (ISSN),
  // building/preserving muscle 1.6-2.2 g/kg.
  var pcForm = document.getElementById("protein-calc-form");
  if (pcForm) {
    var pcUnit = "lb";
    pcForm.querySelectorAll("[data-pc-unit]").forEach(function (btn) {
      btn.setAttribute('aria-pressed',String(btn.getAttribute('data-pc-unit')===pcUnit));
      btn.addEventListener("click", function () {
        var input=document.getElementById('protein-weight'),next=btn.getAttribute('data-pc-unit');
        if(next!==pcUnit&&input.value!==''&&Number.isFinite(Number(input.value))){
          var kg=toKg(Number(input.value),pcUnit);input.value=(next==='lb'?kg*LB_PER_KG:kg).toFixed(1);
        }
        pcForm.querySelectorAll("[data-pc-unit]").forEach(function (b) {
          b.classList.remove("active");
          b.setAttribute('aria-pressed','false');
        });
        btn.classList.add("active");
        btn.setAttribute('aria-pressed','true');
        pcUnit = btn.getAttribute("data-pc-unit");
        document.getElementById("protein-weight-unit").textContent = pcUnit;
      });
    });

    var PROTEIN_RANGES = {
      sedentary: [0.8, 0.8],
      active: [1.2, 1.6],
      muscle: [1.6, 2.2],
    };

    pcForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var errorBox = document.getElementById("protein-calc-error");
      errorBox.hidden = true;
      var out = document.getElementById("protein-calc-results");

      var weightRaw = parseFloat(document.getElementById("protein-weight").value);
      var weightKg = toKg(weightRaw, pcUnit);
      if (!weightKg || weightKg < 30 || weightKg > 300) {
        errorBox.textContent = "Enter a weight between " + (pcUnit === "lb" ? "66 and 660 lb" : "30 and 300 kg") + ".";
        errorBox.hidden = false;
        return;
      }

      var goal = document.getElementById("protein-goal").value;
      var r = PROTEIN_RANGES[goal];
      var lowG = r[0] * weightKg;
      var highG = r[1] * weightKg;

      out.classList.remove("empty");
      if (Math.abs(lowG - highG) < 0.5) {
        out.innerHTML =
          '<div class="result-total">' +
          '<div class="num">' + fmt(lowG) + " g</div>" +
          '<div class="label">protein / day &middot; ' + fmt(lowG * 4) + " cal</div>" +
          "</div>";
      } else {
        out.innerHTML =
          '<div class="result-total">' +
          '<div class="num">' + fmt(lowG) + "&ndash;" + fmt(highG) + " g</div>" +
          '<div class="label">protein / day &middot; ' + fmt(lowG * 4) + "&ndash;" + fmt(highG * 4) + " cal</div>" +
          "</div>";
      }
    });
  }

  // ---------- Standalone carbohydrate calculator ----------
  // AMDR for carbohydrate: 45-65% of total calories.
  var ccForm = document.getElementById("carb-calc-form");
  if (ccForm) {
    ccForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var errorBox = document.getElementById("carb-calc-error");
      errorBox.hidden = true;
      var out = document.getElementById("carb-calc-results");

      var cals = parseFloat(document.getElementById("carb-calories").value);
      if (!cals || cals < 800 || cals > 8000) {
        errorBox.textContent = "Enter a daily calorie target between 800 and 8,000.";
        errorBox.hidden = false;
        return;
      }

      var low = (cals * 0.45) / 4;

      var high = (cals * 0.65) / 4;
      out.classList.remove("empty");
      out.innerHTML =
        '<div class="result-total">' +
        '<div class="num">' + fmt(low) + "&ndash;" + fmt(high) + " g</div>" +
        '<div class="label">carbs per day (45&ndash;65% of calories)</div>' +
        "</div>";
    });
  }

  // A result must never silently describe inputs the visitor has changed.
  [['macro-form','macro-results'],['protein-calc-form','protein-calc-results'],['fat-form','fat-results'],['carb-calc-form','carb-calc-results']].forEach(function(pair){
    var form=document.getElementById(pair[0]),output=document.getElementById(pair[1]);
    if(!form||!output)return;
    function invalidate(){
      output.classList.add('empty');
      output.innerHTML='<p class="result-placeholder">Update your details, then calculate to see your current result.</p>';
    }
    form.addEventListener('input',invalidate);
    form.addEventListener('invalid',invalidate,true);
    form.querySelectorAll('[data-weight-unit],[data-height-unit],[data-pc-unit]').forEach(function(button){button.addEventListener('click',invalidate);});
  });
})();
