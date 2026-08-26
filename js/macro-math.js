(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GMMacroMath = api;
}(typeof window !== "undefined" ? window : this, function () {
  "use strict";
  var LB_PER_KG = 2.2046226218;
  var IN_PER_CM = 0.3937007874;

  function toKg(value, unit) { return unit === "lb" ? value / LB_PER_KG : value; }
  function toCm(value, unit, inches) {
    if (unit === "ftin") return (value * 12 + (inches || 0)) / IN_PER_CM;
    if (unit === "in") return value / IN_PER_CM;
    return value;
  }
  function mifflinStJeor(sex, weightKg, heightCm, age) {
    var base = 10 * weightKg + 6.25 * heightCm - 5 * age;
    return sex === "male" ? base + 5 : base - 161;
  }
  function calculate(options) {
    var bmr = mifflinStJeor(options.sex, options.weightKg, options.heightCm, options.age);
    var tdee = bmr * options.activityMultiplier;
    var totalCals = tdee * (1 + options.calorieAdjustment);
    var proteinG = options.weightKg * options.proteinPerKg;
    var proteinCals = proteinG * 4;
    var fatCals = totalCals * (options.fatPercent || .3);
    var fatG = fatCals / 9;
    var carbCals = totalCals - proteinCals - fatCals;
    return { bmr: bmr, tdee: tdee, totalCals: totalCals, proteinG: proteinG,
      proteinCals: proteinCals, fatG: fatG, fatCals: fatCals,
      carbG: carbCals / 4, carbCals: carbCals };
  }
  return { toKg: toKg, toCm: toCm, mifflinStJeor: mifflinStJeor, calculate: calculate };
}));
