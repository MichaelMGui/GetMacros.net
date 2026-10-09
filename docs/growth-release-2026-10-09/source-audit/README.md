# Current official menu-source audit — 9 October 2026

This is an independent bounded source review. The requested `GetMacros_Content_Release_2026-10-08.zip` was unavailable, so its 28 menu snapshots, 20 article drafts and 80 briefs have **not** been read, approved or reconstructed.

## What was actually verified

The complete current U.S. [Chick-fil-A nutrition interface](https://www.chick-fil-a.com/nutrition-allergens) was retrieved as a full HTTP 200 HTML response, not a search excerpt. Its public interface state contains the same nutrition rows displayed in the page. The private source file has SHA-256 `3b0b9d4a6937b78ba2d774cc3ed6407b89964fd1756e23dc20a3dbb0779cc429`.

Microsoft Edge then opened that official URL without request interception, anti-bot workarounds, or a fixture. Every selected parent/variant row was made visible using the site's actual expansion controls. All 11 printed cells in each of 135 selected rows matched the curated catalogue exactly. `browser-verification.json` records those checks; the screenshots show the named portion rows. These are source-verification screenshots, not GetMacros design screenshots.

The imported catalogue has **129 additional distinct named menu records** and **6 reverified existing records**. The existing meal finder has 463 records and was not rewritten by this audit. Combining the 129 additions with that baseline provides 592 distinct selectable records, provided the six baseline keys are merged rather than counted again. This is not a claim of 592 full meals or 129 new complete lunch combos.

| Additional records | Count |
| --- | ---: |
| Breakfast recipes | 24 |
| Entrees and published counts | 18 |
| Sides and named sizes | 15 |
| Treats | 14 |
| Drinks and published named recipes/sizes | 43 |
| Sauce packets | 8 |
| Dressing packets | 7 |
| **Total newly recorded** | **129** |

The six existing records rechecked were 8-count Grilled Nuggets, 12-count Grilled Nuggets, Grilled Chicken Sandwich, Egg White Grill, Kale Crunch Side and Cool Wrap. Their existing calories, protein, carbohydrates, fiber and sodium were not changed. The new catalogue also retains their current portion weights, fat and total sugar. `correctedOldRecords` remains zero; source reinspection is not a numeric correction.

## Serving questions resolved

The full interface's named Fruit Cup variants are Small **107 g / 60 kcal**, Medium **125 g / 70 kcal**, and Large **215 g / 120 kcal**. The generic product page's 70 kcal panel therefore matches the 125 g Medium table row; the generic parent is not counted as a fourth size. [Official Fruit Cup product page](https://www.chick-fil-a.com/menu/sides/fruit-cup).

Kale Crunch is **112 g / 170 kcal**, with **4 g protein, 13 g carbohydrate, 12 g fat, 4 g fiber and 250 mg sodium**. Its official description and ingredients include vinaigrette and roasted almonds. A tray or almond-free build is not substituted. [Official Kale Crunch product page](https://www.chick-fil-a.com/menu/sides/kale-crunch-side).

The Grilled Chicken Sandwich is a current **206 g / 390 kcal** published row. The official product page confirms its numbers, but does not settle a sauce-free build: the prose recommends Honey Roasted BBQ while the ingredient list appends that sauce's ingredients. The separate sauce row is **12 g / 60 kcal**, yet subtracting that packet from the sandwich would be an unsupported customization. The catalogue explicitly flags this ambiguity. [Sandwich product page](https://www.chick-fil-a.com/menu/entrees/grilled-chicken-sandwich) and [separate sauce product page](https://www.chick-fil-a.com/menu/sauces/honey-roasted-bbq-sauce).

The Cool Wrap product page currently publishes **660 kcal** and includes Avocado Lime Ranch Dressing in its ingredient list. The catalogue retains that published build and warns against adding the same suggested dressing again. [Official Cool Wrap product page](https://www.chick-fil-a.com/menu/entrees/chick-fil-a-cool-wrap).

## Unresolved or intentionally excluded

- Plain Iced Coffee conflicts within the current interface. The Drinks row is **661 g / 200 kcal / 34 g total sugar**; the Coffee variant is **624 g / 110 kcal / 10 g total sugar**. The Coffee parent has yet another 672 g / 260 kcal default, matching the named Caramel build. All ambiguous plain/default rows are excluded. Named Vanilla, Mocha and Caramel variant rows remain exact published recipes; no size or sweetener substitution is inferred.
- Salad/Side Salad suggested-dressing assumptions, generic Club default substitutions, kid meal labels, gallon/catering rows and isolated toppings were excluded from this release. Existing named standalone rows were not duplicated by the generic parent or by a second source category.
- Starbucks Protein Milk/Cold Foam/Latte exact current build panels are **not verified by this audit**. Marketing protein ranges and search excerpts were not turned into fixed nutrient values. The absent package prevents review of its capture assumptions.
- McDonald's Canadian/U.S. packaged records are **not verified or imported by this audit**. Countries are not treated as interchangeable.
- The national table does not establish a recipe edition date. `sourceDate` and edition date remain null; `checkedAt` is the actual review date. That date is not a product launch date or an expert review date.
- Added sugar is not published in the selected table columns and remains null in every record. Total sugar is retained as total sugar. No-added-sugar, zero-sugar, allergen-safety or dietary classification is inferred.

## Integration and reproducibility

Source of truth: `tools/growth_release/menu-records.json`. Runtime copy: `js/order-catalogue.json`. Both JSON payloads are equivalent; the runtime file is compact. Existing-record entries have `baselineKey` matching the original `chain||name`, so a tool can enrich the existing choice without duplicating it. Lower-case category values are `breakfast`, `entree`, `side`, `treat`, `drink`, `sauce`, and `dressing`.

`tools/growth_release/review-source.py --validate` checks unique names/IDs, source/country/portion identity, numeric and null types, bounds, raw printed values, exact fruit sizes, Kale fat, Diet Lemonade total sugar, baseline keys and public-copy parity. When the private HTML is available it also verifies its hash and each exact source row. Without that private snapshot, it explicitly reports curated schema verification rather than claiming a fresh source retrieval. Browser source checks are historical evidence dated 9 October 2026 and are not silently rerun during a production build.

Nutrition totals should sum published portions, preserving unknowns and warnings. Do not force calories to equal 4/4/9 macro arithmetic: these are separately rounded restaurant values. Do not multiply a gallon label's per-cup values or infer fluid ounces from gram weights. This data describes U.S. national standard recipes and may differ by location, season or preparation; it is not an allergy-safety resource.
