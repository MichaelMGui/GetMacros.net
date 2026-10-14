"""Prevent ingredient quantities becoming complete Mexican Subway meals."""
from collections import Counter
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/product_release"))
from subway_mexico import normalize, section


def heading(text):
    return [text] + [None] * 10


def cells(name, grams, cal, protein, fat=1, carbs=5):
    return [name, str(grams), str(cal), "0", str(fat), "0", "440", str(carbs), "0", "1", str(protein)]


class MexicanSectionRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [r for r in json.loads((ROOT / "tools/product_release/menu-records.json").read_text(encoding="utf-8"))["records"] if r["market"] == "MX"]
        cls.by_id = {r["id"]: r for r in cls.records}

    def test_individual_meat_is_not_sandwich(self):
        self.assertEqual(section('Individual Meats (amount on 6" sub or salad)'), "meats")
        r = self.by_id["MX|subway|691a1d7272aeef35"]
        self.assertEqual(r["category"], "component")
        self.assertFalse(r["finderSupported"])
        self.assertEqual((r["servingGrams"], r["cal"], r["p"]), (43, 50, 5))
        self.assertIn("Individual meat portion", r["name"])
        self.assertIn("not a complete sandwich", r["notes"])

    def test_true_complete_turkey_identity_preserved(self):
        r = self.by_id["MX|subway|1c5926505abe2837"]
        self.assertEqual(r["name"], "6-inch sub — Turkey Breast")
        self.assertEqual(r["category"], "entree")
        self.assertTrue(r["finderSupported"])
        self.assertEqual((r["servingGrams"], r["cal"], r["p"]), (205, 270, 15))
        self.assertEqual(r["sourcePage"], 1)

    def test_all_source_sections_and_count(self):
        self.assertEqual(len(self.records), 93)
        self.assertEqual(Counter(r["category"] for r in self.records), {"entree": 42, "component": 42, "dessert": 6, "side": 3})
        self.assertEqual(sum(r["finderSupported"] for r in self.records), 51)
        self.assertEqual(len({r["id"] for r in self.records}), 93)
        self.assertEqual(sum(r["sourceGroup"].startswith("Individual Meats") for r in self.records), 11)
        self.assertTrue(all(r["category"] == "component" for r in self.records if r["sourceGroup"].startswith("Individual Meats")))

    def test_page_two_breads_keep_source_section_and_existing_ids(self):
        breads = [r for r in self.records if r["sourcePage"] == 2 and r["sourceGroup"] == "Breads"]
        self.assertEqual(len(breads), 2)
        self.assertEqual({r["id"] for r in breads}, {"MX|subway|858588332d0788dc", "MX|subway|5f42676c7a642f72"})
        self.assertTrue(all(r["name"].startswith("Breads — ") and r["category"] == "component" for r in breads))

    def test_desserts_and_sides_are_exact_food_servings(self):
        for r in self.records:
            if r["sourceGroup"] in ("Desserts", "Sides"):
                self.assertIn(r["category"], ("dessert", "side"))
                self.assertTrue(r["finderSupported"])
                self.assertIn("1 named", r["serving"])

    def test_condiment_mention_does_not_make_it_a_sub(self):
        for header in ('Sandwich Condiments and Toppings (amount on 6-inch sandwich)',
                       'Vegetables (amount on 6-inch sandwich)', 'Cheese (amount on 6-inch sandwich)'):
            key = section(header)
            self.assertIn(key, ("condiments", "vegetables", "cheese"))
        self.assertTrue(all(r["category"] == "component" for r in self.records if r["sourceGroup"].startswith(("Sandwich Condiments", "Vegetables", "Cheese"))))

    def test_pure_parser_preserves_legacy_ids_but_not_wrong_labels(self):
        p = [{"page": 1, "tables": [[heading('6" Sandwiches Double values for approximate footlong nutrition values.'), cells('Turkey Breast', 205, 270, 15), heading('Breads'), cells('6" Italian (White)', 71, 190, 7)]]},
             {"page": 2, "tables": [[cells('6" Parmesan Oregano', 74, 200, 7), heading('Individual Meats (amount on 6" sub or salad)'), cells('Turkey Breast', 43, 50, 5), heading('Desserts'), cells('Chocolate Chip Cookie', 45, 220, 2)]]}]
        r = normalize(p)
        self.assertEqual(r[0]["id"], "MX|subway|1c5926505abe2837")
        self.assertEqual(r[2]["sourceGroup"], "Breads")
        self.assertEqual(r[2]["id"], "MX|subway|858588332d0788dc")
        self.assertEqual(r[3]["id"], "MX|subway|691a1d7272aeef35")
        self.assertEqual(r[3]["category"], "component")
        self.assertEqual(r[4]["category"], "dessert")

    def test_unknown_heading_fails_closed(self):
        p = [{"page": 1, "tables": [[heading('6" Sandwiches'), cells('Known', 100, 200, 10), heading('Unreviewed new food family'), cells('Unknown', 43, 50, 5)]]}]
        with self.assertRaises(ValueError):
            normalize(p)

    def test_missing_macros_disable_finder(self):
        c = cells('Turkey Breast', 205, 270, 15)
        c[10] = None
        r = normalize([{"page": 1, "tables": [[heading('6" Sandwiches'), c]]}])[0]
        self.assertIsNone(r["values"]["p"])
        self.assertFalse(r["finderSupported"])

    def test_values_country_source_and_old_nutrition_review_preserved(self):
        for r in self.records:
            self.assertEqual(r["market"], "MX")
            self.assertEqual(r["country"], "MX")
            self.assertEqual(r["sourceHash"], "80cf7369eaf6651d4d0efd4020d42eb65045752446fa0fd37eb637b8089c715b")
            self.assertEqual(r["sourceDate"], "2025-11")
            self.assertEqual(r["checked"], "2026-10-11")
            self.assertEqual(r["classificationReviewedAt"], "2026-10-14")
            self.assertEqual(r["units"]["na"], "mg")
            for field in ("cal", "p", "c", "fat", "f", "na", "sugar", "sat"):
                self.assertEqual(r[field], r["nativeNutrients"][field])

    def test_full_pinned_source_parse_if_present(self):
        p = ROOT / "docs/global-product-release-2026-10-11/sources/subway-mexico-extracted.json"
        if p.exists():
            source = normalize(json.loads(p.read_text(encoding="utf-8")))
            self.assertEqual({r["id"] for r in source}, set(self.by_id))
            for row in source:
                saved = self.by_id[row["id"]]
                for key in ("name", "serving", "category", "finderSupported", "sourceGroup"):
                    self.assertEqual(saved[key], row[key])


if __name__ == "__main__":
    unittest.main(verbosity=2)
