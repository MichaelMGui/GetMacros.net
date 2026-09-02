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
    var settings = math.GOALS[values.goal];
    var result = math.calculate({ sex: values.sex, age: age, weightKg: kg, heightCm: cm,
      activityMultiplier: activity, calorieAdjustment: settings.calorieAdjustment,
      proteinPerKg: settings.proteinPerKg, fatPercent: .3 });
    document.querySelector("#hc-calories").textContent = round(result.totalCals).toLocaleString();
    document.querySelector("#hc-protein").textContent = round(result.proteinG) + "g";
    document.querySelector("#hc-carbs").textContent = round(result.carbG) + "g";
    document.querySelector("#hc-fat").textContent = round(result.fatG) + "g";
    document.querySelector("#hc-context").textContent = text("bmrLabel", "BMR") + " " +
      round(result.bmr).toLocaleString() + " kcal · " + text("tdeeLabel", "estimated TDEE") + " " +
      round(result.tdee).toLocaleString() + " kcal · " + settings.label + ".";
    var output = document.querySelector("#hc-results");
    output.hidden = false;
  });
}());
