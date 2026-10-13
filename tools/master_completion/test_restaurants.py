"""Independent gates for the newly reviewed Canadian restaurant source selection."""
from pathlib import Path
import hashlib, importlib.util, json, math, unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("restaurant_ingest", HERE / "restaurant_ingest.py")
ingest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ingest)


class RestaurantCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = ingest.build()
        cls.records = cls.result["records"]
        cls.named = {r["name"]: r for r in cls.records}

    def test_exact_country_and_no_prior_collision(self):
        prior = json.loads((HERE.parents[1] / "js/order-registry.json").read_text(encoding="utf-8"))
        prior_by_id = {r["id"]: r for r in prior["records"] if r.get("id")}
        self.assertEqual(len(self.records), 27)
        self.assertEqual(len({r["id"] for r in self.records}), 27)
        for r in self.records:
            self.assertTrue(r["id"].startswith("CA|new-york-fries|"))
            self.assertEqual([r["market"], r["country"], r["region"]], ["CA"] * 3)
            if r["id"] in prior_by_id:
                # The gate also runs after integration: the same identity may
                # recur, but it must not mean a different serving or market.
                existing = prior_by_id[r["id"]]
                for key in ["market", "chain", "name", "serving"] + ingest.FIELDS:
                    self.assertEqual(existing.get(key), r.get(key))

    def test_reviewed_source_rows_not_us_substitutions(self):
        fries = self.named["Fries, Snack"]
        self.assertEqual([fries[k] for k in ["servingGrams", "cal", "p", "c", "fat", "na"]],
                         [170, 490, 6, 61, 25, 50])
        poutine = self.named["Classic Poutine, Regular"]
        self.assertEqual([poutine[k] for k in ["servingGrams", "cal", "p", "c", "fat"]],
                         [600, 1420, 39, 132, 81])
        self.assertNotIn("us.newyorkfries", fries["source"])

    def test_order_arithmetic_named_parts(self):
        snack = self.named["Hot dog with bun + snack fries"]
        regular = self.named["Hot dog with bun + regular fries"]
        self.assertEqual([snack[k] for k in ["servingGrams", "cal", "p", "c", "fat", "f", "na"]],
                         [354, 910, 28, 100, 45, 7, 1420])
        self.assertEqual([regular[k] for k in ["cal", "p", "c", "fat"]], [1320, 33, 150, 66])
        by_id = {r["id"]: r for r in self.records}
        for row in [snack, regular]:
            self.assertEqual(row["verificationStatus"], "calculated-from-official-components")
            parts = [by_id[x["id"]] for x in row["calculatedFrom"]]
            self.assertEqual(ingest.sum_nutrients(parts), {k: row[k] for k in ingest.FIELDS})
            self.assertEqual([x["quantity"] for x in row["calculatedFrom"]], [1, 1])

    def test_unknown_not_zero_or_known_subtotal(self):
        a = {k: 2 for k in ingest.FIELDS}
        b = {k: 0 for k in ingest.FIELDS}
        b["na"] = None
        values = ingest.sum_nutrients([a, b])
        self.assertIsNone(values["na"])
        self.assertEqual(values["cal"], 2)
        self.assertTrue(all(v is None for v in ingest.sum_nutrients([]).values()))
        self.assertIsNone(ingest.quantity(""))
        self.assertIsNone(ingest.quantity(None))
        self.assertEqual(ingest.quantity(0), 0)
        for invalid in [-1, True, math.inf, math.nan, "unknown"]:
            with self.assertRaises((ValueError, TypeError)):
                ingest.quantity(invalid)

    def test_source_dates_and_provenance(self):
        for r in self.records:
            self.assertEqual(r["sourceDate"], "2026-08-20")
            self.assertEqual(r["retrievedAt"], "2026-10-13")
            self.assertIn("Printed", r["sourceDateProvenance"])
            self.assertEqual(len(r["sourceHash"]), 64)
            self.assertEqual(r["units"], {"cal": "kcal", "p": "g", "c": "g", "fat": "g",
                                         "f": "g", "na": "mg", "sugar": "g", "sat": "g"})
            self.assertEqual(set(r["nutrientProvenance"]), set(ingest.FIELDS))
        pdf = HERE.parents[1] / "docs/master-completion-2026-10-13/restaurant-sources/nyf-current.pdf"
        if pdf.exists():
            self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), self.result["source"]["sourceHash"])

    def test_extras_serving_rules_are_not_complete_orders(self):
        components = [r for r in self.records if r["category"] == "component"]
        self.assertEqual(len(components), 8)
        for r in components:
            self.assertFalse(r["finderSupported"])
            self.assertTrue(r["macroComplete"])
            self.assertEqual(r["servingRules"], {"snack": 1, "regular": 2, "large": 3,
                                               "appliesTo": "extra ingredient amount only"})
        self.assertEqual(self.named["Cheese Curds"]["servingGrams"], 28)
        self.assertEqual(self.named["Cheese Curds"]["sourceServing"], "1/2 scoop for snack-size poutine")

    def test_tags_do_not_share_mutable_arrays(self):
        ids = [id(r["t"]) for r in self.records]
        self.assertEqual(len(set(ids)), len(ids))
        for r in self.records:
            self.assertEqual(len(r["t"]), len(set(r["t"])))

    def test_no_unreviewed_other_chains_or_allergen_claims(self):
        self.assertEqual({r["chain"] for r in self.records}, {"New York Fries"})
        for r in self.records:
            self.assertEqual(r["diet"], [])
            self.assertNotIn("allergens", r)
            self.assertTrue(all(math.isfinite(r[k]) and r[k] >= 0 for k in ingest.FIELDS))

    def test_presence_does_not_enable_unreviewed_menus(self):
        matrix = json.loads((HERE / "restaurant_presence.json").read_text(encoding="utf-8"))
        prior = json.loads((HERE.parent / "master_release/restaurant_presence.json").read_text(encoding="utf-8"))
        prior_ids = {r["id"] for r in prior["relationships"]}
        new = matrix["relationships"]
        self.assertEqual(len(new), 17)
        self.assertEqual(len({r["id"] for r in new}), len(new))
        self.assertEqual(len(matrix["updates"]), 6)
        for row in new:
            self.assertNotIn(row["id"], prior_ids)
            self.assertIn(row["country"], {"US", "CA", "MX", "GB", "IE", "AU", "NZ", "JP"})
            self.assertEqual(row["presence"]["status"], "confirmed")
            self.assertEqual(row["presence"]["checkedAt"], "2026-10-13")
            self.assertTrue(row["presence"]["evidenceUrl"].startswith("https://"))
            self.assertFalse(row["finderSupported"])
            self.assertFalse(row["nutritionAvailable"])
            self.assertEqual(row["trackedRecords"], 0)
        for row in matrix["updates"]:
            self.assertIn(row["id"], prior_ids)
            self.assertNotIn("finderSupported", row)
            self.assertNotIn("presence", row)


if __name__ == "__main__":
    unittest.main()
