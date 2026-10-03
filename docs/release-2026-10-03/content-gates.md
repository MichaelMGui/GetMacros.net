# Practical-resource publication gate

Date: 2026-10-03. Scope: **15 new practical resources** in `tools/release_explainers.json`. Existing page improvements and the other agent’s data collections are separate counts. No public HTML, templates, business logic, formulas or restaurant data were edited by this content subtask.

The payload has an intended question, distinct utility, direct answer, scoped source claims, useful internal links, unique metadata and original worked material for every entry. The examples are explicitly hypothetical; none is presented as a named food’s actual nutrition, a retail price, a restaurant customization, a diet prescription or a medical recommendation.

## Gate record

| Resource | Added value beyond existing pages | Source and arithmetic review |
| --- | --- | --- |
| Grams vs milliliters | Valid comparison paths; product-specific weight-to-volume boundary. | NIST definitions inspected. 20 ÷ 36 × 120 = 66.67 calories and 20 ÷ 36 × 30 = 16.67 mL. |
| Raw vs cooked weight | Alternative recording paths and actual batch yield rather than a universal multiplier. | USDA cooking-yield table inspected. Rice example: 150 ÷ 600 × 720 = 180 calories. |
| Drained weight | Distinguishes net contents, drained solids and label serving basis. | FDA guide’s packing/serving passages inspected. 120 ÷ 80 × 90 = 135; all 240 g = three servings. |
| Multi-serving packages | Inner packet versus outer box, plus whole-package double-counting check. | FDA serving guide inspected. Four packets × two servings × 110 = 880; 42 ÷ 28 × 140 = 210. |
| As packaged vs prepared | Adds a changed-preparation example to show the wrong-column error. | FDA prepared-column passages inspected. 150 + 75 = 225; alternative drink gives 230 calories and 8 g protein. |
| Label rounding | Illustrates precision limits without inventing a correction factor for a real food. | FDA rounding appendix inspected. 12 × 3 = 36; hypothetical unrounded 12.4 × 3 = 37.2. |
| Edible vs purchased | Uses edible yield in quantity and cost, distinct from raw/cooked preparation. | USDA Food Buying Guide inspected. 700 ÷ 1,000 = 70%; $8 ÷ 700 × 100 ≈ $1.14. |
| Unequal portions | Five different container shares reconcile to the complete batch. | Label serving principle cited. Container calories sum to 2,000 and protein to 100 g. Uniform distribution assumption explicit. |
| Mixed bowl | Separate denominators for four components, including measured sauce. | USDA data-type documentation inspected. 480 calories and 36.3 g protein; missing-value rule explicit. |
| Powder scoop | Distinguishes powder weight from protein grams and includes partial amounts. | FDA serving principle cited. 24 ÷ 32 × 24 = 18 g protein. No supplement advice. |
| Protein cost with waste | Original bulk-pack break-even analysis instead of repeating basic tool instructions. | FDA serving principle cited. $7 ÷ $0.05 = 140 g; 140 ÷ 160 = 87.5% use. Equal protein concentration assumption explicit. |
| Calculator-to-finder handoff | Distinguishes daily estimate, meal limits and sorting preferences; avoids sharing personal inputs. | FDA menu guidance inspected. Illustrative day sums to 2,100. Limits are user choices, not prescribed targets. |
| Complete-order comparison | Original ranking reversal and source/portion checklist. | FDA menu guidance inspected. Complete totals 720 versus 590; no actual chain figures implied. |
| Missing nutrients | Supported zero, partial subtotal and unknown value are distinct. | FDA written menu nutrition guidance inspected. 900 mg known subtotal does not establish a whole-order maximum. |
| Breakfast extras | Full-order protein and calorie tradeoffs; drink preparation check. | FDA menu guidance inspected. Totals 620/30 versus 490/26; figures explicitly hypothetical. |

## Source manifest

Each JSON entry contains `sourceURLs` and `claims` with a specific source URL. Public body links appear next to the factual principle they support. Original hypothetical arithmetic is not attributed to FDA or USDA as food data. The inspected sources are:

- [NIST SI units: volume](https://www.nist.gov/pml/owm/si-units-volume).
- [NIST definitions of base units](https://www.nist.gov/si-redefinition/definitions-si-base-units).
- [FDA serving size](https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label).
- [FDA label interpretation](https://www.fda.gov/food/nutrition-facts-label/how-understand-and-use-nutrition-facts-label).
- [FDA Food Labeling Guide](https://www.fda.gov/media/81606/download), inspected for drained weight, prepared-column definitions and rounding. It is an older guide; the batch does not publish obsolete label layouts, historical Daily Values or a comprehensive current legal labeling standard.
- [FDA current industry resources](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/industry-resources-changes-nutrition-facts-label), inspected as the contemporary label-resource context.
- [FDA calories on menus](https://www.fda.gov/food/nutrition-education-resources-materials/calories-menu).
- [USDA cooking yields](https://www.ars.usda.gov/ARSUserFiles/80400525/data/retn/usda_cookingyields_meatpoultry.pdf), inspected for variable preparation yields, not copied typical conversion assumptions.
- [USDA Food Buying Guide Appendix B](https://foodbuyingguide.fns.usda.gov/Appendix/ResourceAppendixB), inspected for as-purchased versus edible portions.
- [USDA FoodData Central documentation](https://fdc.nal.usda.gov/data-documentation/), redirected from the earlier .html URL and inspected for food-data types.

## Checks actually completed

- Parsed all 15 JSON entries successfully and checked unique slugs.
- Checked internal body links resolve to an existing root page or another release explainer.
- Checked every entry has sources and mapped source claims; every claim URL appears in that entry’s source list.
- Checked there is no H1 inside article body output, leaving the generated page’s H1 as the sole page title.
- Parsed all body HTML with a tag-stack check: every body is balanced. All 15 contain worked tables and useful related links. An exact authored-paragraph scan found no duplicated paragraphs within this batch.
- Recalculated worked examples programmatically, including portion totals and break-even math.
- Reviewed introductions, examples and limitations for unsupported nutrition recommendations, invented branded values and unnecessary repetition.
- Inspected existing broad label, recipe, budget and serving guides when choosing focused additions. Rejected a separate dry-rice page and a duplicate basic protein-cost page.
- Added column scope to table headings. All nutrition comparisons retain units and portion bases in text or table cells.
- Checked the actual food-comparison form: it uses gram serving weights and offers per-serving, equal-weight and equal-calorie views. The grams/mL article explicitly says not to enter mL in a grams field, and the mixed-bowl article does not promise a custom-portion or automatic ingredient-summing feature.

## Integration gate still required

Integration update, October 3: the parent release has generated all 33 routes and completed static metadata/link/source tests and the 2,140 route-render matrix. The historical subtask checklist below describes what was handed to integration; final results and exact human-inspection boundaries are now in `release-report.md`, `content-tests.json`, and `release-manifest.csv`. This is not an independent medical-review status.

These are content payload checks, not rendered-page checks. The release integrator must generate the static routes and verify:

1. One clear H1, unique title/description, self-canonical, correct publication date and accurate visible Article metadata.
2. Crawlable inclusion in the relevant guide/editorial index, sitemap and search source; no orphan pages.
3. Mobile and dark-theme table behavior, readable link styles, heading wrapping and no overflow.
4. Actual tool behavior referenced by the copy, including strict limits and unknown fields.
5. Broken links across the completed batch; external-source existence is checked by inspected fetches, not a fabricated all-link pass.
6. Duplicate-content review across the combined dataset and practical batches.

`editorialStatus` deliberately says generated-page verification is pending integration. Do not change that wording to a blanket “verified” until actual route and browser checks have run. The new publication date is October 3; existing restaurant verification dates must remain their actual dates.

No expert credentials, independent medical review or AdSense approval claim is made. No deployment was performed by this subtask.
