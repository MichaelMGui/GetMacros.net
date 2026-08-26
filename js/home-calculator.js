(function () {
  "use strict";
  var form = document.querySelector("#home-macro-form");
  var math = window.GMMacroMath;
  if (!form || !math) return;
  function round(value) { return Math.round(value); }
  function text(key, fallback) { return form.dataset[key] || fallback; }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var values = Object.fromEntries(new FormData(form));
    var age = Number(values.age);
    var kg = math.toKg(Number(values.weight), "lb");
    var cm = math.toCm(Number(values.height), "in");
    var activity = Number(values.activity);
    var error = document.querySelector("#hc-error");
    if (age < 14 || age > 100 || kg < 30 || kg > 300 || cm < 120 || cm > 230) {
      error.textContent = text("errText", "Please check the age, weight and height entries.");
      error.hidden = false;
      return;
    }
    error.hidden = true;
    var settings = {
      lose: { adjustment: -.2, protein: 1.8, label: text("goalLose", "gradual fat loss") },
      maintain: { adjustment: 0, protein: 1.6, label: text("goalMaintain", "maintenance") },
      gain: { adjustment: .12, protein: 2, label: text("goalGain", "muscle gain") }
    }[values.goal];
    var result = math.calculate({ sex: values.sex, age: age, weightKg: kg, heightCm: cm,
      activityMultiplier: activity, calorieAdjustment: settings.adjustment,
      proteinPerKg: settings.protein, fatPercent: .3 });
    document.querySelector("#hc-calories").textContent = round(result.totalCals).toLocaleString();
    document.querySelector("#hc-protein").textContent = round(result.proteinG) + "g";
    document.querySelector("#hc-carbs").textContent = round(result.carbG) + "g";
    document.querySelector("#hc-fat").textContent = round(result.fatG) + "g";
    document.querySelector("#hc-context").textContent = text("bmrLabel", "BMR") + " " +
      round(result.bmr).toLocaleString() + " kcal · " + text("tdeeLabel", "estimated TDEE") + " " +
      round(result.tdee).toLocaleString() + " kcal · " + settings.label + ".";
    var output = document.querySelector("#hc-results");
    output.hidden = false;
    output.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
}());
