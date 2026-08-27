"use strict";
const assert = require("node:assert/strict");
const math = require("../js/macro-math.js");

function close(actual, expected, tolerance, label) {
  assert.ok(Math.abs(actual - expected) <= tolerance, `${label}: ${actual} vs ${expected}`);
}
const kg = math.toKg(170, "lb");
const cm = math.toCm(69, "in");
close(kg, 77.1107, .001, "pounds to kilograms");
close(cm, 175.26, .001, "inches to centimeters");
close(math.toCm(5, "ftin", 9), cm, .001, "feet/inches and inches agree");
const result = math.calculate({ sex: "male", age: 30, weightKg: kg, heightCm: cm,
  activityMultiplier: 1.55, calorieAdjustment: 0, proteinPerKg: 1.6, fatPercent: .3 });
close(result.bmr, 1721.482, .01, "Mifflin-St Jeor BMR");
close(result.tdee, 2668.297, .01, "activity-adjusted TDEE");
close(result.proteinG, 123.377, .01, "protein grams");
close(result.fatG, 88.943, .02, "fat grams");
close(result.proteinCals + result.fatCals + result.carbCals, result.totalCals, .0001, "macro energy balance");
const cut = math.calculate({ sex: "male", age: 30, weightKg: kg, heightCm: cm,
  activityMultiplier: 1.55, calorieAdjustment: -.2, proteinPerKg: 1.8, fatPercent: .3 });
const bulk = math.calculate({ sex: "male", age: 30, weightKg: kg, heightCm: cm,
  activityMultiplier: 1.55, calorieAdjustment: .12, proteinPerKg: 2, fatPercent: .3 });
const recomp = math.calculate({ sex: "male", age: 30, weightKg: kg, heightCm: cm,
  activityMultiplier: 1.55, calorieAdjustment: math.GOALS.recomp.calorieAdjustment,
  proteinPerKg: math.GOALS.recomp.proteinPerKg, fatPercent: .3 });
close(cut.totalCals, result.tdee * .8, .0001, "cut target");
close(bulk.totalCals, result.tdee * 1.12, .0001, "bulk target");
close(recomp.totalCals, result.tdee * .9, .0001, "recomposition target");
assert.equal(math.GOALS.gain.label, "gaining weight while building muscle");
assert.ok(cut.carbCals >= 0 && recomp.carbCals >= 0 && bulk.carbCals >= 0,
  "valid example has non-negative carbohydrate remainder");
console.log("PASS: conversions, BMR, TDEE, goal adjustments and macro energy balance.");
