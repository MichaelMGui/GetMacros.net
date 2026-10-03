# Restaurant-source inspection and query research

Inspection date: 2026-10-03. Nutrition scope: U.S. Search locale was not explicitly geolocated. This is a qualitative research record, not a keyword-volume, ranking, traffic or revenue forecast. The user's earlier Search Console photographs are historical observations, not an authorized live analytics connection.

## What was inspected

Official sources were opened and the relevant table or item text was read. `data-audited-patches.json` records exact order keys, source URLs, source-defined portions, per-nutrient values, published versus calculated provenance and retrieval dates. Forty-one existing records received at least a partial source inspection. Twenty-seven official ingredient entries support reproducible reference tables and combinations. No complete source PDFs or restaurant imagery are republished.

| Restaurant | Evidence actually inspected | Important date/access boundary | Release treatment |
|---|---|---|---|
| Sweetgreen | [Official nutrition table](https://www.sweetgreen.com/nutrition): five named bowls/salads, grams and all six nutrients | No publication date established | Published complete-recipe totals; exact gram serving retained |
| Panera | [Official U.S. PDF](https://www.panerabread.com/content/dam/panerabread/documents/c8-26-nutrition-guide.pdf): five exact half/whole/cup/bowl entries | Printed effective date September 2, 2026 | Totals and new fat values; no bread/side silently included |
| CAVA | [Accessible official PDF](https://assets.ctfassets.net/kugm9fp9ib18/3rkBCBV2gIGMu78AnqigQk/26f1d223147700d1c266d358b3678d3b/CAVA-Reg-GID-0425-Nutri_Allerg.pdf): four named recipes | Filename indicates April 2025; printed date not established. Current nutrition-page linkage could not be confirmed from the script shell | Retain explicit edition/access caveat. Do not call these a freshly issued 2026 menu |
| Chick-fil-A | Official dedicated item pages: eight/twelve nuggets, sandwich, club, wrap, Egg White Grill, Kale Crunch | Twelve-count page exposed four nutrients only. Exact side portions in two large combos were not reverified | Six fully inspected records plus one partial. Newly inspected collection sodium/fiber for twelve nuggets remain unknown; no inferred scaling |
| Popeyes | [Official U.S. PDF](https://plk-use1-prod.sites.rbictg.com/nutrition/PLK_Nutrition.pdf): three/five blackened tenders and regular red beans/rice | Search title suggested February 2023, but actual PDF is labeled September 2026 | Use the printed edition; calculated three-tender-plus-side sum is visibly distinct from published item totals |
| Panda Express | [Official live nutrition table](https://www.pandaexpress.com/nutritioninformation): exact full entree/base portions | No source publication date established. The Super Greens base is 10 oz and the separate entree entry is 3.5 oz | Seven tracked records corrected; component sums use full weights. Do not reuse older 275-calorie chicken or 130-calorie greens values |
| Starbucks | Official `/single/nutrition` search-result text for products 368, 371, 2122117 | Direct URLs returned empty script shells. Indexed official text showed the serving/nutrient fields | Indexed text inspection explicitly described; no claim that a live rendered table was checked |
| Chipotle | [U.S. ingredient PDF](https://www.chipotle.com/content/dam/chipotle/menu/nutrition/US-Nutrition-Facts-Paper-Menu-3-2025.pdf) plus [High Protein Menu announcement](https://newsroom.chipotle.com/2025-12-18-CHIPOTLE-UNVEILS-ITS-FIRST-EVER-HIGH-PROTEIN-MENU-FEATURING-A-NEW-SNACK-READY-HIGH-PROTEIN-CUP) | Ingredient PDF is printed October 2024 despite 2025 in its URL; menu announcement published December 18, 2025 | Preserve published menu calories/protein/fiber, calculate other nutrients from named components; half rice remains an explicit assumption |

Dedicated Chick-fil-A pages inspected:

- [Eight grilled nuggets](https://www.chick-fil-a.com/menu/entrees/grilled-nuggets)
- [Twelve grilled nuggets](https://www.chick-fil-a.com/menu/entrees/12-ct-grilled-nuggets)
- [Grilled Chicken Sandwich](https://www.chick-fil-a.com/menu/entrees/grilled-chicken-sandwich)
- [Grilled Chicken Club](https://www.chick-fil-a.com/menu/entrees/chick-fil-a-grilled-chicken-club-sandwich)
- [Cool Wrap](https://www.chick-fil-a.com/menu/entrees/chick-fil-a-cool-wrap)
- [Egg White Grill](https://www.chick-fil-a.com/menu/breakfast/egg-white-grill)
- [Kale Crunch](https://www.chick-fil-a.com/menu/sides/kale-crunch-side)

Starbucks indexed official nutrition sources:

- [Turkey bacon sandwich, product368](https://www.starbucks.com/menu/product/368/single/nutrition)
- [Spinach wrap, product371](https://www.starbucks.com/menu/product/371/single/nutrition)
- [Egg white bites, product2122117](https://www.starbucks.com/menu/product/2122117/single/nutrition)

## Search-intent research actually performed

Queries inspected on October 3, 2026:

| Query | Observed useful page types | Distinct GetMacros implementation |
|---|---|---|
| high protein fast food breakfast calories grilled chicken nutrition comparison | Ranked lists of grams of protein; some price/score columns | Four exact breakfast food servings, protein density alongside totals, no invented prices |
| fast food protein per calorie sodium comparison | Per-calorie rankings and nutrient tables | Transparent protein-per-100-calories arithmetic and separate protein-plus-sodium comparison; servings remain visible |
| Chipotle CAVA chicken bowl nutrition calories comparison | Custom ingredient comparisons and opinionated chain winners | Three exact builds, ingredient inventory, sodium/calorie tradeoff, explicit CAVA edition caveat |
| Panda Express Super Greens rice side calories portion 10 oz | Nutrition answers with different vintages and ambiguous base/entree portions | Official 10 oz base versus3.5 oz entree distinction and full rice/chow-mein base table |
| Official Chick-fil-A/Panda/Starbucks item nutrition queries | Dedicated official item pages and source tables | Item-specific citations and source-access status rather than a general unqualified check date |

Two competing page types were opened to understand intent and information structure, not as sources of restaurant facts or prose:

- [BowlMacros CAVA vs Chipotle comparison](https://bowlmacros.com/blog/cava-vs-chipotle-nutrition): ingredient tables and example builds serve a genuine comparison intent. Its winner framing and “calorie traps” language are not adopted. GetMacros keeps named recipes and quantified differences instead of food shame or a universal winner.
- [Fast Food Index breakfast comparison](https://fastfoodindex.com/high-protein-fast-food-breakfast/): ranked breakfasts, prices and scores show demand for immediate comparisons. GetMacros uses source-supported portions and nutrients only. Its prices/scores are not copied or treated as measured data.

The attempted FoodOutCalc page open failed; only the search snippet was available. It was not relied on for factual content. Searches for additional Wendy's, McDonald's and Subway U.S. details did not yield a sufficiently inspectable full source in this session. Some results were for other markets; those were rejected. A McDonald's Egg McMuffin page exposed calories but not the full nutrient fields needed here, so it did not become a new collection fact. These access limits are not evidence that the restaurants' values are wrong.

## Google primary guidance inspected

- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): original analysis and utility justify these resources. The implementation adds exact comparisons, reproducible arithmetic and defined scope rather than relying on article count.
- [Search spam policies](https://developers.google.com/search/docs/essentials/spam-policies): the scaled-content-abuse section was inspected. Several near-duplicate ideas were consolidated. There is no restaurant×keyword matrix, fabricated review authority or automatic translation expansion.
- [Faceted navigation guidance](https://developers.google.com/crawling/docs/faceted-navigation): curated pages are separate supported reference resources; arbitrary filter states are not automatically published as indexable landing pages. The parent integrator owns canonical/robots implementation.
- [FDA sodium labeling guidance](https://www.fda.gov/food/nutrition-education-resources-materials/sodium-your-diet): daily labeling reference versus serving quantity. The under1,000mg collection explicitly is not called a regulated low-sodium claim.

No keyword volume, difficulty, backlinks, competitor traffic, current Search Console rank, Google approval probability or revenue estimates were measured. The route-level query-to-intent map is `data-query-map.json`; source facts and calculations are in `data-publication-manifest.json`.

## Editorial and reuse boundaries

All comparisons use numerical facts transcribed from the inspected sources and original explanation. Source attribution does not establish a license to redistribute a complete database, source document or branded image. This batch does not publish source-document downloads or brand photography. A legal opinion on database rights or AdSense acceptance has not been obtained.

Existing ingredient/diet classifications are not newly certified by nutrient inspection. The vegetarian resource names that distinction and sends readers to current restaurant ingredients/allergen information. No allergy-safety, medical-outcome, current-price or universal-healthiest claims are introduced.
