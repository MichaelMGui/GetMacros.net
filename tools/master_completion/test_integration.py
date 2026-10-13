"""Read the finished outputs; never run mutating generators during verification."""
from pathlib import Path
from collections import Counter
from html import unescape
import json, re, subprocess, unittest, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
FIELDS = ["cal", "p", "c", "fat"]


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def finder_supported(row):
    return (row.get("category") not in ["component", "sauce"]
            and row.get("finderSupported", True))


def route_source(route):
    path = ROOT / (route.strip("/") + "/index.html" if route.endswith("/") else route.lstrip("/"))
    return path.read_text(encoding="utf-8")


class CompletedRestaurantIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = read("js/order-registry.json")["records"]
        cls.additions = read("tools/master_completion/restaurant_records.json")["records"]
        cls.presence = read("data/restaurant-presence.json")["relationships"]
        cls.changes = read("tools/master_completion/restaurant_presence.json")
        cls.markets = json.loads(re.search(
            r"window.GM_MARKETS=(.*);",
            (ROOT / "js/market-definitions.js").read_text(encoding="utf-8"))[1])

    def test_all_reviewed_records_integrated_once(self):
        for r in self.additions:
            matched = [x for x in self.registry if x.get("id") == r["id"]]
            self.assertEqual(len(matched), 1, r["id"])
            for field in FIELDS + ["market", "country", "region", "serving", "servingGrams",
                                   "source", "sourceDate", "sourceHash", "sourceVersion",
                                   "additionalNutrients", "nutrientProvenance"]:
                self.assertEqual(matched[0].get(field), r.get(field), (r["name"], field))

    def test_country_dataset_and_finder_do_not_leak(self):
        ca = read("js/canada-meals.json")["records"]
        expected = [r for r in self.registry if r["market"] == "CA"]
        self.assertEqual(ca, expected)
        script = (ROOT / "js/canada-meals.js").read_text(encoding="utf-8")
        start = re.search(r"window.GM_MEALS\s*=\s*", script)
        self.assertIsNotNone(start, "Canadian finder has no serialized local meal array")
        finder, _ = json.JSONDecoder().raw_decode(script[start.end():])
        self.assertEqual(finder, [r for r in expected if finder_supported(r)])
        self.assertTrue(all(r["market"] == "CA" for r in finder))
        self.assertFalse(any(r.get("category") in ["component", "sauce"] for r in finder))
        self.assertFalse(any(r["chain"] == "Pizza Nova" for r in finder))
        self.assertEqual(sum(r["chain"] == "New York Fries" for r in finder), 19)

    def test_presence_counts_reflect_real_country_rows(self):
        self.assertEqual(len({r["id"] for r in self.presence}), len(self.presence))
        baseline = read("tools/master_release/restaurant_presence.json")["relationships"]
        expected_ids = {r["id"] for r in baseline + self.changes["relationships"]}
        self.assertEqual({r["id"] for r in self.presence}, expected_ids)
        for p in self.presence:
            rows = [r for r in self.registry
                    if r["market"] == p["country"] and r["chain"] == p["restaurantBrand"]]
            supported = [r for r in rows if finder_supported(r)]
            full = [r for r in rows if all(r.get(k) is not None for k in FIELDS)]
            calories_only = [r for r in rows if r.get("cal") is not None
                             and all(r.get(k) is None for k in ["p", "c", "fat"])]
            self.assertEqual(p["trackedRecords"], len(rows), p["id"])
            self.assertEqual(p["completeMacroRecords"], len(full), p["id"])
            self.assertEqual(p["finderRecords"], len(supported), p["id"])
            self.assertEqual(p["finderSupported"], bool(supported), p["id"])
            self.assertEqual(p["caloriesOnlyRecords"], len(calories_only), p["id"])
            self.assertEqual(p["calculatedOrders"], sum(bool(r.get("calculatedFrom")) for r in rows))

    def test_new_operating_presence_never_fakes_nutrition(self):
        by_id = {r["id"]: r for r in self.presence}
        for input_row in self.changes["relationships"]:
            published = by_id[input_row["id"]]
            self.assertEqual(published["country"], input_row["country"])
            self.assertEqual(published["presence"], input_row["presence"])
            self.assertEqual(published["trackedRecords"], 0)
            self.assertEqual(published["finderRecords"], 0)
            self.assertFalse(published["finderSupported"])
            self.assertFalse(published["nutritionAvailable"])
            self.assertEqual(published["nutritionSources"], [])
        for update in self.changes["updates"]:
            published = by_id[update["id"]]
            self.assertEqual(published["nutritionSourceStatus"], update["nutritionSourceStatus"])
            self.assertEqual(published["trackedRecords"], 0)
            self.assertFalse(published["finderSupported"])

    def test_new_york_fries_coverage_counts_and_source(self):
        nyf = next(p for p in self.presence if p["id"] == "CA|new-york-fries")
        self.assertEqual((nyf["trackedRecords"], nyf["completeMacroRecords"],
                          nyf["finderRecords"], nyf["calculatedOrders"]), (27, 27, 19, 2))
        self.assertTrue(nyf["nutritionAvailable"])
        self.assertEqual(nyf["nutritionSourceStatus"], "official-table-reviewed")
        self.assertEqual(nyf["nutritionSources"], [self.additions[0]["source"]])
        self.assertEqual(nyf["localMenuSource"], self.additions[0]["sourceParent"])
        self.assertIn("not a complete", nyf["limitations"])

    def test_world_index_uses_every_tracked_chain(self):
        html = route_source("/world-restaurant-menus.html")
        main = unescape(re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S)[1])
        countries = re.findall(r"<article>(.*?)</article>", main, re.S)
        self.assertEqual(len(countries), len(self.markets))
        for country, info in self.markets.items():
            block = next(x for x in countries if 'href="' + info["home"] + '"' in x)
            records = [r for r in self.registry if r["market"] == country]
            count = len([r for r in records if finder_supported(r)])
            self.assertIn(f"{len(records)} tracked servings; {count} finder entries.", block)
            for chain in {r["chain"] for r in records}:
                self.assertIn(chain, block, (country, chain))
            self.assertIn('href="' + info["restaurants"] + '"', block)
        canada = next(x for x in countries if 'href="/ca/en/"' in x)
        for chain in ["Subway", "Domino’s", "Pizza Nova", "New York Fries", "Booster Juice"]:
            self.assertIn(chain, canada)

    def test_directories_link_local_operations_honestly(self):
        for country, info in self.markets.items():
            if country in ["US", "CA"]:
                continue
            html = route_source(info["restaurants"])
            extra = re.search(r"<!-- presence-links:start -->(.*?)<!-- presence-links:end -->",
                              html, re.S)
            self.assertIsNotNone(extra, country)
            for row in self.changes["relationships"]:
                if row["country"] == country:
                    self.assertIn('href="' + row["officialCountryWebsite"] + '"', extra[1])
                    self.assertIn(row["restaurantBrand"], unescape(extra[1]))
            self.assertIn("another country", extra[1].lower())
        ca = unescape(route_source("/ca/en/restaurants/"))
        self.assertIn('href="/ca/en/restaurants/new-york-fries/"', ca)
        self.assertIn("27 tracked servings.", ca)
        self.assertIn("Operates in Canada. Local nutrition records are not yet available here.", ca)

    def test_guide_source_portions_and_seo_are_real(self):
        route = "/ca/en/restaurants/new-york-fries/"
        html = route_source(route)
        main = unescape(re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S)[1])
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", main)), 1)
        self.assertIn(self.additions[0]["source"], html)
        for term in ["August 20, 2026", "October 13, 2026", "910 kcal",
                     "28 g protein", "1,320 kcal", "33 g protein", "snack", "regular", "large"]:
            self.assertIn(term, main)
        for record in self.additions:
            self.assertIn(record["name"], main)
            self.assertIn(record["serving"], main)
        self.assertRegex(main, r"(?:(?:twice|two|2).{0,40}regular|regular.{0,40}(?:twice|two|2))")
        self.assertRegex(main, r"(?:(?:three|3).{0,40}large|large.{0,40}(?:three|3))")
        self.assertIn("not separately published", main)
        self.assertIn('rel="canonical" href="https://getmacros.net' + route + '"', html)
        self.assertNotRegex(html, r'<meta name="robots"[^>]*noindex')
        ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
        urls = [u.find(ns + "loc").text for u in ET.parse(ROOT / "sitemap.xml").getroot()]
        self.assertEqual(urls.count("https://getmacros.net" + route), 1)
        search = route_source("/search.html")
        self.assertIn('href="' + route + '"', search)

    def test_country_market_chain_definition_comes_from_actual_finder(self):
        ca = [r for r in self.registry if r["market"] == "CA" and finder_supported(r)]
        expected = sorted({r["chain"] for r in ca})
        self.assertEqual(self.markets["CA"]["chains"], expected)
        self.assertIn("New York Fries", expected)
        self.assertNotIn("McDonald’s", expected)
        self.assertNotIn("Freshii", expected)
        self.assertNotIn("Pizza Nova", expected)

    def test_restaurant_adapter_unit_conversion_and_country_search(self):
        result = subprocess.run(["node", str(HERE / "test_restaurant_adapter.cjs")],
                                cwd=ROOT, capture_output=True, encoding="utf-8", check=True)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "passed")
        self.assertGreaterEqual(report["checks"], 30)


if __name__ == "__main__":
    unittest.main(verbosity=2)
