# Existing-market nutrition expansion — reviewed staging handoff

Reviewed October 18, 2026. Shared application files and deployment were not modified by this workstream. The parent release integrates and renders these records.

## Integration

`tools/flagship_release/markets_release_records.json` is the final combined artifact. It contains `records`, `updates`, `withdrawnIds`, `presenceUpserts`, `sources` and exact `counts`.

```python
import sys
sys.path.insert(0, 'tools/flagship_release')
import markets_integrate
registry = markets_integrate.integrate(registry)
```

The callable returns a new registry/list, preserves unrelated metadata/data, removes explicitly withdrawn staged IDs and is idempotent. It requires the 135 exact existing U.S. refresh IDs. It rejects unrelated or modified ID collisions, while allowing a valid earlier self-hashed version of this same source batch to be refreshed. The caller owns writing shared files, generating real guide pages, recomputing registry counts/search indices and deployment. `presence-upserts.json` is also available separately.

Do **not** rerun `markets_stage.py` against a registry that already contains this batch: its original-new-versus-refresh classification intentionally used the original checked-out registry. Source parser code and original two input artifacts remain available for maintenance. `markets_integrate.package(validate_against_current=False)` refreshes an already reviewed artifact without reclassifying it against a now-mutated application baseline.

## Final counts

- **1,967 new source portion records**, including three records with bounded/unknown core fields; no false zero substitutes.
- **Four calculated Canadian orders**, separately identified from restaurant-published totals.
- **135 refreshed existing U.S. Chick-fil-A portion records** with established IDs preserved.
- **1,971 total additions**, not 1,971 different meals or entire restaurant menus.
- 29 source captures with hashes in the combined source manifest.
- 20 newly missing U.S. breakfast portions. Canadian Chick-fil-A breakfast is explicitly unavailable in its official FAQ.

| Market | Chain | New source portions | Calculated orders |
|---|---|---:|---:|
| Canada | Chick-fil-A | 150 | 1 |
| Canada | Chipotle | 82 | 3 |
| United States | Chick-fil-A | 186 | 0 |
| Australia | Domino’s | 214 | 0 |
| Australia | Hungry Jack’s | 257 | 0 |
| New Zealand | Domino’s | 241 | 0 |
| New Zealand | Burger King | 60 | 0 |
| India | Domino’s | 185 | 0 |
| Singapore | Chick-fil-A | 62 | 0 |
| France | Burger King | 108 | 0 |
| Japan | KFC | 69 | 0 |
| Republic of Ireland | Zizzi | 353 | 0 |

U.K. data is owned by the independent U.K. workstream. South Africa received source/presence investigation but no numerical additions. **Mexico subsequently received38 calorie-only sizes in the separate third artifact described below.** Existing correct records, including Pizza Nova, are preserved.

The 759 explicit new source-family identities in the manifest are a partial product-family measure. Another 544 source portions have no distinct source-family field. Do not call portion counts product counts. Native combo/bundle rows remain published serving portions; the four calculated orders are separate GetMacros sums.

## Source scope and important distinctions

- **Chick-fil-A Canada/U.S.:** current country nutrition HTML plus embedded WordPress table data. Parent defaults are excluded when named sub-portions exist. Duplicate source categories merge. Canadian versus U.S. sandwiches, sauces, drinks and quantities remain distinct. Gallons and catering are excluded from ordinary meal-finder eligibility. [Canadian nutrition](https://www.chick-fil-a.ca/nutrition-allergens), [U.S. nutrition](https://www.chick-fil-a.com/nutrition-allergens).
- **Chipotle Canada:** [official PDF](https://www.chipotle.ca/content/dam/chipotle/menu/nutrition/CA-Nutrition-Facts-Paper-Menu-3-2025.pdf) prints **CAN OCT 24**, despite its filename. Preserve that historical edition. Millilitres are not grams; `<1` is a bound, not zero or exact one. Individual components and alcoholic drinks are not finder meals. Three explicit bowls sum only the named Canadian portions.
- **Domino’s Australia/New Zealand:** [AU](https://www.dominos.com.au/menu/nutritional-information), [NZ](https://www.dominos.co.nz/menu/nutritional-information). Full numeric product/variant cards were processed. Pizza values are per slice; Mini has four source slices, New Yorker six where printed, other source counts retained. Missing kcal is explicitly converted from kJ. Different crusts and markets remain separate.
- **Hungry Jack’s Australia:** all 18 linked nutrition-category PDFs from the [official nutrition index](https://www.hungryjacks.com.au/nutrition-info). Category overlap collapses; conflicting equal-edition values are withheld; latest identified editions win only for the same named weight. Native per-100g values remain separate from per-serving values. Missing per-serving sodium remains unknown, even when a per-100g field exists. Family bundles are not ordinary one-person finder meals.
- **Domino’s India:** [official Indian menu](https://www.dominos.co.in/menu/nutritional-information), only active named variants with explicit nutritional elements. No gram weight, slice count or values copied from a different crust. Pizza Mania Chicken Sausage is labeled separately from the main Non-Veg Pizza product with the same short name.
- **Burger King New Zealand:** [official guide](https://bknzpublic.z8.web.core.windows.net/nutritionalguide/nutritionalguide.pdf), July 29, 2026. Core and limited-time per-serving rows; internal energy/sugar contradictions withheld.
- **Chick-fil-A Singapore:** [official local nutrition](https://www.chick-fil-a.com.sg/nutrition-allergens/) and linked November 2025 guide. Separate treat and drink NutriGrade placeholder columns handled. Newer 2026 additions without values are not fabricated. Contradictory lemonade sugar/carbohydrate rows are withheld.
- **Burger King France:** [current official menu](https://www.burgerking.fr/carte), only reachable category-linked products. French child portions labeled separately. Historical/unlinked/internal products excluded; theoretical menus are not inferred. Salt is explicitly converted to sodium. Four ambiguous Baby burger IDs withdrawn after independent audit.
- **KFC Japan:** [current official food-information index](https://www.kfc.co.jp/food_information) and linked September 11, 2026 PDF. Japanese pages only; equivalent English pages are not counted again. S/M/L drink labels are not gram weights. Source sodium is retained rather than recomputed from rounded salt. Dashes remain unknown.
- **Zizzi Ireland:** explicit [ROI/Belfast Autumn 2026 V2 guide](https://cdn.sanity.io/files/ysupxjc9/production/b0dfaa87024a45cbd51b09372d4c53a4e26fd898.pdf/ZIZZI-ROI.BEL-NUTRITION-GUIDE_SEP2026_V2.pdf), September 28 edition, paired with [current Dublin restaurants](https://www.zizzi.co.uk/italian-restaurants/ireland/dublin). Rustica and Classic pizzas have distinct labels/identities; extras, Bambini portions, mocktails and coffee retain their source groups. Alcohol pages excluded. Does not assert every combined ROI/Belfast guide product is available at every Republic of Ireland branch.

No exact meal photographs or licensed restaurant photography were acquired in this data workstream. Captured source images/PDF renderings are review evidence, not approved public food assets.

## Independent-audit corrections

- Canadian Buddy Fruits: official product description says **90 g**, nutrition table **100 g**. `servingGrams=null`, both reported masses preserved in `portionConflict`, named-container nutrients unchanged, no scaling. The fruit-based composed order is withheld. This is a fruit-puree pouch, **not** a Fruit Cup.
- New Zealand Domino’s Salted Caramel Chocolate Mousse: source sugar 35.2 g exceeds carbohydrate 33.8 g. Withdrawn, not numerically corrected.
- French Baby Whopper/Big King: four current linked IDs have the same names/context but materially different nutrient totals without clear portion qualifiers. All four withheld pending source clarification, rather than guessing which row is correct.
- India Chicken Sausage duplicates resolved through explicit Pizza Mania versus main-menu identity, not nutrient averaging.
- French children’s Hamburger/Cheeseburger remain distinct from adult products.

`withdrawnIds` explicitly removes the five earlier staged NZ/French IDs on repeat integration. `extra-withheld.json` contains 103 rejected source rows/variants with reasons. `withheld.json` separately records the Canadian fruit-order issue. Neither file represents invented substitute records.

## Presence matrix and exact remaining gaps

`country-restaurant-matrix.json` / `.csv` cover **17 global candidates × all 12 existing markets**, plus other existing/new tracked chains: 255 relationships in the integrated registry snapshot. Every row has a disposition.53 have a current explicit reviewed confirmation,91 retain earlier confirmed evidence/dates,110 remain **unconfirmed**, and one is an announcement whose opening date has passed without separate current-operation confirmation. Unconfirmed never means absent. The 126 retrieval attempts produced 88 captures and 38 errors; successful retrieval is not automatically operating verification.

- **Mexico Chipotle:** July 13, 2026 [official announcement](https://ir.chipotle.com/2026-07-13-CHIPOTLE-ENTERS-MEXICO-WITH-FIRST-RESTAURANT-IN-NUEVO-LEON) announces July 16 Nuevo León opening. Blanket absence language would be stale. No current local macro panel was verified. `chipotle-mexico-copy-review.json` records the exact scan; no actual current public blanket absence sentence was found. Adjacent unrelated article links are not a false absence claim.
- **Mexico:** Starbucks official product pages expose calories by size but not complete macros.38 named-size servings are supplied separately as calories-only data. Several other official sites returned403, TLS errors, timeouts or app-only data. Existing Mexican records remain; foreign formulas are not copied.
- **Canada:** McDonald’s current menu retrieval returned403; Wendy’s client menu did not expose numeric local rows without further ordering flow; Shake Shack’s current Canadian locations/menu were confirmed but no usable complete nutrient panel was exposed; Popeyes returned an unusable compressed/error response. No fabricated Canadian breakfast or U.S. substitution.
- **South Africa Burger King:** current nutrition explorer and legacy public nutrition view failed to expose usable numerical tables in fresh browser sessions. Official FAQ remains operating/source evidence.
- **South Africa Nando’s:** public menu snapshot contains483 product definitions,65 nutrient-bearing definitions. It declares Energy `CALORIES` and Sodium `GRAMS` but e.g. a60g PERinaise dip has972 energy,20g fat and713 sodium. Those may be kJ/mg, but converting by plausibility alone is unsafe. All65 withheld pending explicit unit clarification; source and blocker captured. Glycaemic carbohydrate also requires a separate basis.
- **Ireland:** a Tim Hortons document labeled UK & Ireland does not establish Republic of Ireland operation when the current finder lists only England/Scotland/Wales/Northern Ireland. Likewise Caffè Nero `en_IE` document is explicitly Northern Ireland. No ROI import from either.
- **UK Chick-fil-A:** current directory includes Northern Ireland branches. Hamilton Scotland is announced for October29,2026 and is still future on this review date. **Singapore** directory lists Bugis+ and Millenia Walk; this is operating evidence distinct from dated nutrition coverage.
- No claim that every major chain or every current menu is complete. The matrix states unresolved sources individually rather than presenting directory links as completed menus.

## Verification actually performed

`python -X utf8 tools/flagship_release/markets_test.py`: **14 tests passed**. Covers source hashes and reproducible versions; market identity; local CFA values and breakfast; pouch conflict; component sums/null propagation; bounded values; pizza slice units; SG category alignment; Irish portion variants; catering eligibility; explicit audit withdrawals; immutable/idempotent integration; all204 candidate dispositions.

Read-only PDF review images actually rendered/inspected: `sources/chipotle-ca-nutrition-page.png`, `hjs-au-01-review.png`, `hjs-au-02-review.png`, `bk-nz-review.png`, `cfa-sg-review.png`, `kfc-jp-review.png`, `zizzi-ie-review.png`. These are representative source-page inspections, **not** every source PDF page or rendered GetMacros page. Source extraction covers the stated scopes; frontend/mobile/both-theme QA belongs to integrated parent verification. No invented live URL, deployment, image-rights or complete-menu claims.

## Final separate Mexican calories-only addition

`tools/flagship_release/markets_mexico_calories.json` is a separate production artifact for38 explicitly named Mexican Starbucks drink sizes across11 source product identities. Count it **separately from the1,967 source portions in the combined artifact**. It carries `records`, empty `updates`/`withdrawnIds`, `presenceUpserts`, two source captures/hashes and exact counts. The parent integrates it as a third batch and renders `/mx/en/restaurants/starbucks/` with clearly calories-only presentation.

Eight sized records have source-reported0kcal; every protein/carbohydrate/fat/fibre/sodium/sugar/saturated-fat value remains `null`, including those eight. No size volume, custom milk/syrup, serving weight or other-market nutrient value is inferred. `macroComplete=false`, `coverageStatus=calories-only`; `finderSupported=true` permits incomplete-data browsing while explicit nutrient limits must still reject unknown values. Two unsized espresso products are deferred. This is hot-drink category coverage, not the entire Starbucks menu.

The generator and independent38-size literal regression fixture are `tools/flagship_release/markets_mexico_calories.py`. Five tests pass: every named source size; known zero versus unknown macros; country/portion/units; capture hashes/reproducible versions; and independent Latte item-page match(120/150/200kcal). Source register: `mexico-calories-source-register.json`. The country matrix now records38 calorie-only and zero complete-macro Mexican Starbucks records.
