# Canadian restaurant expansion — research and limits

Research and source retrieval: October 12, 2026 (America/Toronto). Numeric source-table review is an inspection of published figures and their layout, not independent laboratory testing, local inventory verification or dietitian review.

## Implemented data

The pinned `tools/master_release/restaurant_records.json` adds 282 Canadian records from six operating chains: Subway 85, Domino’s 46, Mary Brown’s 48, Booster Juice 48, Pizza Pizza 16, Pizza Nova 39. Of those, 243 contain calories, protein, carbohydrate and fat. Domino’s has 43 size-specific components and three calculated exact slice builds; these are distinguished from direct restaurant-reported orders. Pizza Nova’s 39 entries contain calories only and do not support macro-constrained matching.

The presence matrix has 57 country–chain relationships across the eight already published markets, including 25 researched Canadian chains. It distinguishes local operating presence, a located nutrition resource, actual tracked records and supported finder records. A location page does not validate nutrient data. Chains that began in another country are included when an official local operating page confirms their Canadian presence.

## Official sources used

| Chain | Current official entry point | Exact numeric source | Edition and reviewed scope |
|---|---|---|---|
| Subway | [Canadian nutrition page](https://www.subway.com/en-ca/menunutrition/nutrition?MenuCategoryId=684&ProductId=8753) | [Canadian PDF linked by that page](https://media.subway.com/dam/urn:aaid:aem:c0ee4b37-9376-42de-b2d6-2a3ffaadecb1/original/as/CAN_Nutrition_ENG_6_11_26.pdf) | Printed June 2026. Pages 1–2 visually reviewed. Standard sandwiches, wraps, salads, power bowls and breakfast; ingredients/modifiers on later pages not imported. |
| Domino’s | [Canadian store directory](https://pizza.dominos.ca/) | [Official Canadian nutrition guide](https://www.dominos.ca/assets/build/market/CA/_en/pdf/Canadian-Nutrition-Guide-Final-Secure.pdf) | Printed August 2025, currently served from the Canadian site. Page 5 visually reviewed: SMALL hand-tossed component amounts for one-sixth pizza. Other crust/size tables not imported. |
| Mary Brown’s | [Current Canadian menu](https://marybrowns.com/menu/) | [Actual menu download link](https://marybrowns.com/wp-content/uploads/Mary-Browns-Allergen-and-Nutritionals-July-2026.pdf) | July 2026 filename edition, not a claimed printed verification date. Page 1 visually reviewed. Clear single portions only. |
| Booster Juice | [Canadian official FAQ/footer](https://boosterjuice.com/en-ca/a/faq) | [September 2026 guide linked by current footer](https://cdn.shopify.com/s/files/1/0673/9371/6482/files/2026-09-NutritionGuide-ENG.pdf?v=1788534813) | Printed September 2026. Pages 1–2 visually reviewed. Named regular/snack smoothies and 475 mL Mix’rs. The other two pages are not imported. |
| Pizza Pizza | [Small pizza nutrition](https://www.pizzapizza.ca/about-us/nutrition/small-pizza/) | Same primary HTML table | Exact small subgroup: one-sixth of 10-inch pizza. Pepperoni row has a March 12, 2026 update label; undated rows are not assigned that date. Blank products excluded. |
| Pizza Nova | [Actual rendered official nutrition interface](https://pizzanova.com/nutrition) | Explicit IN-STORE SLICES listing | Publication date unavailable. 39 exact one-slice calorie listings. Protein/carbs/fat and gram weights absent. Signature size table calorie denominator not assumed. |

Source snapshots, SHA-256 hashes, extraction artifacts and source screenshots are kept privately under `docs/master-release-2026-10-12/sources/`. Production consumes the pinned JSON, never live source retrieval. The raw sources and third-party scripts are research evidence, not public assets. Website sessions, unrelated environment fields and analytics URLs are not product data and must not be published.

## Problems caught rather than guessed

- Mary Brown’s large Taters lists 437.0 g fat for a 354 g portion. It is withheld, not decimal-corrected.
- Mary Brown’s multi-serving buckets and large sides have unclear total-order denominator. They are withheld rather than multiplied speculatively.
- Mary Brown’s two spicy-tender rows have sodium above 5,000 mg; held for clarification. The restaurant has not been contacted.
- Pizza Pizza’s English small-pizza source has saturated-fat cells such as 35 g alongside 8 g total fat. The contradictory field remains null, retaining its raw source value. Calories and other consistent core fields remain available.
- Booster Juice PDF table extraction drops alternating product names and clips last rows. The importer uses calibrated full text lines checked against the actual page pixels, preserving each product and size. It does not forward-fill a different regular drink’s name.
- Millilitres are volume. They are not converted to grams without a source density.
- Pizza Nova signature recipe calorie denominator is unclear in the retrieved table. Only the explicit one-slice in-store entries are imported. No protein or fat values are inferred from pizza in another database.
- Domino’s changes cheese quantities between a cheese-only pizza and a pizza with toppings. The exact three builds apply that rule.

## Canadian operating chains addressed without fabricated menus

The matrix includes McDonald’s, Burger King, Chipotle, Subway, Domino’s, Pizza Nova, Tim Hortons, A&W Canada, Harvey’s, Wendy’s, KFC, Popeyes, Pizza Pizza, Starbucks, Dairy Queen, Taco Bell, Five Guys, Mary Brown’s, Mucho Burrito, Quesada, Osmow’s, Pita Pit, Booster Juice, New York Fries and Freshii. Each has its own official presence URL and observation in the payload.

McDonald’s current public Canadian calculator uses `/dnaapp/itemList` and lists 186 unique menu IDs in its HTML. Ordinary public API retrieval returned 403, and its normal browser page also returned Access Denied. No challenge bypass was attempted. Its old stage/QA PDFs were not used as current nutrition.

KFC’s current Canadian nutrition page was retrieved as a shell, but the actual browser attempt failed with HTTP/2 protocol error. An older Canadian 2025 PDF was found in search; it was not substituted for verified current data. Wendy’s Canadian interface was located, but exact local product records remain unreviewed. Burger King, Popeyes, Starbucks, Dairy Queen and Taco Bell require country-specific item/size review. Chipotle’s Canadian component PDF and current customizations need a reconciled edition; no U.S. bowl values are copied. Five Guys’ older Canadian ingredient guide needs current-edition validation. Mucho Burrito’s Canadian calculator, Quesada’s ingredient guide, Osmow’s historical tables, Pita Pit, New York Fries and Freshii remain in the source-validation queue.

No new country is enabled just because a chain is known there. This release’s new numeric records are Canadian only. Existing eight-market selections are preserved.

## Rights and maintenance

Public restaurant nutrition facts are recorded as factual values with source attribution. This is not a claim that the restaurants license their PDFs, brand marks, photographs, design or copy under an open licence. None of those assets are republished, and no partnership or endorsement is claimed. The source files remain private evidence. Future wholesale collection or licensed API access needs a separate rights review.

Refresh sources deliberately: retrieve, compare editions/hashes, inspect relevant page layouts, flag changed serving assumptions, run arithmetic/integrity gates, then publish reviewed snapshots. Do not automatically stamp nutrition as reviewed because a design build ran. Preserve source versions in existing diary snapshots.

## Integration

`tools/build_master_restaurants.py` exposes `build(page)` for the shared late renderer and creates six substantive local guides plus `data/restaurant-presence.json`. The root integrator owns registry merging, country availability, navigation, sitemap/search registration and production/browser QA. No protected `.git` writes or music-platform changes are made by this module.

Test command: `python tools/master_release/test_restaurants.py` (use bundled Python in this workspace). The gates check local identity, source provenance, unknown macros, contradictory fields, drink volume, exact component sums, distinguishable recipe builds, operating presence versus finder support, and guide usefulness.
