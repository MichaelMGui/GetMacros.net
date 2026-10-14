"""Regression gates for the reviewed local serving expansion, not network tests."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from restaurant_ingest import build, identity, quantity, total, validate, CORE, FIELDS

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


class ReviewedLocalServings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.facts = json.loads((OUT / "restaurant_facts.json").read_text(encoding="utf-8"))
        cls.result = build(cls.facts)
        cls.rows = cls.result["records"]
        cls.by_name = {r["name"]: r for r in cls.rows}

    def test_precise_counts(self):
        self.assertEqual(self.result["counts"], {"newRecords": 40, "officialServingRecords": 37,
            "calculatedOrders": 3, "components": 3, "finderRecords": 37,
            "newRestaurants": 1, "groceryRecordsAdded": 0})
        self.assertEqual(len(self.rows), 40)

    def test_no_inherited_identity_collision(self):
        registry = json.loads((ROOT / "js/order-registry.json").read_text(encoding="utf-8"))["records"]
        additions = {r["id"] for r in self.rows}
        # Idempotent integration can already contain this exact release.
        prior = [r for r in registry if r.get("id") in additions]
        self.assertTrue(all(r["market"] == "CA" and r["restaurantId"] == "triple-os" for r in prior))
        self.assertEqual(len(additions), len(self.rows))

    def test_local_market_and_country_scope(self):
        for row in self.rows:
            self.assertEqual((row["market"], row["country"], row["region"]), ("CA", "CA", "CA"))
            self.assertEqual(row["restaurantMarketId"], "CA|triple-os")
            self.assertTrue(row["id"].startswith("CA|triple-os|"))
        wrong = copy.deepcopy(self.facts)
        wrong["market"] = "US"
        with self.assertRaises(ValueError):
            build(wrong)

    def test_edition_is_not_retrieval_or_invented_day(self):
        for row in self.rows:
            self.assertEqual(row["sourceDate"], "2025-06")
            self.assertEqual(row["sourceDatePrecision"], "month")
            self.assertEqual(row["retrievedAt"], "2026-10-14")
            self.assertEqual(row["checked"], "2026-10-14")
            self.assertNotEqual(row["sourceDate"], row["checked"])

    def test_native_units_and_no_inferred_density(self):
        for row in self.rows:
            self.assertEqual(row["units"]["cal"], "kcal")
            self.assertEqual(row["units"]["na"], "mg")
            self.assertEqual(row["units"]["p"], "g")
            self.assertEqual(row["conversions"], [])
            self.assertGreater(row["servingGrams"], 0)
        self.assertEqual(self.by_name["Iced Coffee - Small (12 oz)"]["servingGrams"], 188)
        self.assertEqual(self.by_name["Vanilla Milkshake - Small (12 oz)"]["servingGrams"], 390)

    def test_sauce_variants_are_published_not_guessed(self):
        original = self.by_name["Chicken Bacon Cheddar"]
        modified = self.by_name["Chicken Bacon Cheddar - Without Sauce"]
        self.assertEqual((original["cal"], modified["cal"]), (791, 567))
        self.assertEqual((original["p"], modified["p"]), (44, 44))
        self.assertNotEqual(original["id"], modified["id"])
        self.assertEqual(modified["verificationStatus"], "official-table-reviewed")
        self.assertEqual(modified["sourceModification"], "without sauce")
        self.assertNotIn("calculatedFrom", modified)

    def test_named_fries_are_independent_servings(self):
        kid = self.by_name["Fries - Kid’s (3 oz)"]
        regular = self.by_name["Fries - Regular (5 oz)"]
        large = self.by_name["Fries - Large (7 oz)"]
        self.assertEqual([r["servingGrams"] for r in (kid, regular, large)], [92, 155, 217])
        self.assertEqual([r["cal"] for r in (kid, regular, large)], [134, 239, 334])
        self.assertNotEqual(regular["cal"], kid["cal"] * 5 / 3)

    def test_complete_order_sums_every_supported_field(self):
        by_id = {r["id"]: r for r in self.rows}
        calculated = [r for r in self.rows if "calculatedFrom" in r]
        self.assertEqual(len(calculated), 3)
        for order in calculated:
            parts = [by_id[p["id"]] for p in order["calculatedFrom"]]
            for field in FIELDS:
                self.assertAlmostEqual(order[field], sum(p[field] for p in parts))
                self.assertEqual(order["nutrientProvenance"][field]["componentIds"], [p["id"] for p in parts])
            self.assertEqual(order["servingGrams"], sum(p["servingGrams"] for p in parts))
            self.assertIsNone(order["nativeNutrients"])
            self.assertEqual(order["verificationStatus"], "calculated-from-official-components")
            self.assertNotIn("separately published restaurant combo", order["calculation"])
        a = self.by_name["Sunny Start - Bacon - Without Sauce + Hashbrown"]
        self.assertEqual(a["cal"], 611)
        self.assertAlmostEqual(a["p"], 24.7)
        b = self.by_name["Chicken Bacon Cheddar - Without Sauce + Regular Fries"]
        self.assertEqual(b["cal"], 806)
        self.assertAlmostEqual(b["p"], 47.5)
        c = self.by_name["Dippin’ Chicken - 5 pieces + Regular Fries + Honey Mustard"]
        self.assertEqual(c["cal"], 914)
        self.assertAlmostEqual(c["p"], 38.5)

    def test_unknowns_propagate_per_nutrient(self):
        self.assertIsNone(quantity(None))
        self.assertIsNone(quantity(""))
        self.assertIsNone(total([{"p": 4}, {"p": None}], "p"))
        self.assertEqual(total([{"p": 4}, {"p": 0}], "p"), 4)
        self.assertIsNone(total([], "p"))
        facts = copy.deepcopy(self.facts)
        facts["rows"][0][facts["columns"].index("na")] = None
        changed = build(facts)
        self.assertIsNone(changed["records"][0]["na"])
        self.assertNotIn("na", changed["records"][0]["nutrientProvenance"])

    def test_source_zero_is_not_missing(self):
        sauce = self.by_name["Side Honey Mustard"]
        self.assertEqual(sauce["p"], 0)
        self.assertEqual(sauce["f"], 0)
        self.assertIn("p", sauce["nutrientProvenance"])
        self.assertTrue(sauce["macroComplete"])

    def test_invalid_quantities_fail(self):
        for value in (True, False, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                quantity(value)

    def test_contradictory_source_not_silently_corrected(self):
        r = copy.deepcopy(self.rows[0])
        r.update(cal=337, fat=2.7, c=31, p=5.7)
        with self.assertRaises(ValueError):
            validate(r)
        names = {r["name"] for r in self.rows}
        self.assertNotIn("Frappuccino - Regular (20 oz)", names)
        self.assertNotIn("Cajun Fries", names)
        self.assertNotIn("Impossible Burger", names)
        self.assertFalse(any("Milkshake - Regular" in name for name in names))

    def test_dips_not_finder_meals(self):
        for row in self.rows:
            self.assertEqual(row["finderSupported"], row["category"] not in ("component", "sauce") and all(row[k] is not None for k in CORE))
            if row["category"] == "sauce":
                self.assertFalse(row["finderSupported"])

    def test_presence_numbers_equal_records(self):
        p = self.result["presenceRelationships"][0]
        self.assertEqual(p["country"], "CA")
        self.assertEqual(p["presence"]["status"], "confirmed")
        self.assertEqual(p["trackedRecords"], len(self.rows))
        self.assertEqual(p["finderRecords"], sum(r["finderSupported"] for r in self.rows))
        self.assertEqual(p["calculatedOrders"], 3)
        self.assertEqual(p["completeMacroRecords"], 40)
        self.assertFalse(p["sourceRetrievalIsVerification"])

    def test_no_invented_ingredients_allergen_diet_or_micronutrients(self):
        for row in self.rows:
            self.assertIsNone(row["ingredients"])
            self.assertEqual(row["diet"], [])
            self.assertEqual(set(row["additionalNutrients"]), {"chol", "trans"})
            self.assertNotIn("price", row)
            self.assertNotIn("allergenSafe", row)

    def test_provenance_and_pinned_file_when_available(self):
        for row in self.rows:
            self.assertEqual(row["source"], self.facts["source"])
            self.assertEqual(len(row["sourceHash"]), 64)
            if not row.get("calculatedFrom"):
                self.assertIn(row["sourcePage"], (1, 2))
        pdf = ROOT / "docs/clarity-release-2026-10-14/data-sources/triple-nutrition.pdf"
        if pdf.exists():
            self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), self.facts["sourceHash"])

    def test_reproducible_output(self):
        published = json.loads((OUT / "restaurant_additions.json").read_text(encoding="utf-8"))
        self.assertEqual(published, self.result)
        self.assertEqual(identity("same", "1 serving"), identity("same", "1 serving"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
