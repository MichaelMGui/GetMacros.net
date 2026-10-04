# Official-source audit — October 4, 2026

This expansion uses actual nutrition rows, not menu-name estimates. Sources were
retrieved and inspected on October 4, 2026. Full URLs, resolved URLs, PDF SHA-256
and retrieval outcomes are recorded in `sources/retrieval-log.json`; row evidence
and page numbers accompany every record in `expansion-payload.json`.

| Chain | Additional orders | Exact printed edition used | Column/layout verification |
|---|---:|---|---|
| Arby’s | 53 | June 2026 effective date | 12 columns; serving grams precede calories; source page 1 rendered |
| SONIC | 47 | Cover says Summer 2026; filename says September 2026 | 10 nutrient columns; header and burger rows on page 3 rendered; optional triangle preserved as note |
| QDOBA | 14 | 2026; exact month/day not established from title | 13 columns including potassium; carbs and sodium order differs from other guides; ambiguous fat rows rendered and excluded |
| El Pollo Loco | 27 | Footer says valid September 2026 | 12 columns; portion ounces; dressing and dinner inclusions checked in rendered source |
| Del Taco | 60 | February 2026 | 11 columns; gram portion; first nutrition page rendered; explicit box sauce variants retained |
| Noodles & Company | 22 | Not established | Paired REG/SM columns; regular values taken from each pair; rendered header confirms mapping |
| Culver’s | 23 | July 2025 | 10 columns; rendered page 3 confirms nutrients and dinner/basket footnotes; older official edition acknowledged |
| Taco John’s | 122 | Not established | 10 columns; less-than bounds retained; impossible beef rice-bowl fiber visually confirmed and excluded |
| In-N-Out | 9 | January 2026 | Official landing’s linked PDF inspected with web tool; nine burger/explicit-modifier rows transcribed consistently from PDF |
| Raising Cane’s | 3 | August 2026 | Individual portions and sandwich inspected; two transparent sums; published combo mismatch is unresolved |

## Retrieval and row review

The source-header mappings were verified using actual PDF rendering/text, then all
selected rows were parsed into typed nutrient columns. Automated checks cover
every row: nonnegative values, fiber not exceeding carbohydrate, coherent units,
exact source identity, serving presence, source hash, duplicate identity, preserved
less-than bounds, and all calculated sums. Not every individual order was manually
visually compared digit by digit against a screenshot; the report does not claim
that. Candidate extraction is separate from the curated publication payload.

Arby’s/SONIC/Del Taco/Taco John’s menu-page portions do not establish a complete
combo with sides or drinks. A single taco or slider remains explicitly one listed
order. Noodles data uses regular portions only; paired small-column values are not
merged into the regular row. Ordinary serving-size duplicates, drinks, desserts,
stand-alone extra components and obviously incomplete protein-only portions were
not used to reach the target. Source menu categories and footnotes establish
regional/limited availability where identifiable; absence of such a note is not
a promise of availability.

PDF edition date and retrieval date are different fields. Unestablished printed
dates stay null. The site should show the retrieval date as source inspection,
not as a recipe change, firsthand tasting, expert review or restaurant endorsement.

## Quantified unknowns and conflicts

Ten new orders have an unknown exact fiber value. Eight are published less-than
amounts; two are calculated orders with at least one such component. The original
five incomplete GetMacros records are outside this append package. Incomplete rows
can still be inspected when the finder’s complete-data filter is off; numeric fiber
filters must not treat these unknowns as zero.

QDOBA’s two Quesabirria rows fail calorie/fat plausibility and are excluded. Taco
John’s Beef Fiesta Rice Bowl fails fiber/carbohydrate plausibility and is excluded.
Raising Cane’s combo/individual sum discrepancy is not explained away: the
calculated orders identify their exact individual portions and are not called the
published combos. Jimmy John’s, Potbelly and Shake Shack official source access
was insufficient; those chains were not counted as new coverage.

In-N-Out direct retrieval produced challenge HTML; only the successful web PDF
inspection supports its data. Culver’s current live nutrition page leads to a
Nutritionix service, while the retained official PDF is the July 2025 edition.
Neither is represented as a local snapshot of a newly changed 2026 recipe.

## Asset rights and scope

Nutrition-source PDFs are evidence stored under tools, excluded from public page
publishing. Their photos and logos are not licensed GetMacros artwork. New guides
use image-free reference compositions and the shared GetMacros interface. No
source restaurant photographs were copied into public image assets. No allergen
safety, menu price, Canadian substitution, or global menu equivalence is inferred.

The target after the actual source audit was 10 new chains and at least 250 useful
orders. The curated result exceeds the quantity target with 380 orders. This is
recorded-data coverage, not an estimate of traffic or a health recommendation.

The generator’s page checks are source/HTML checks. Final mobile/desktop guide
screenshots, theme interaction checks and overflow checks belong to the integrated
release QA and were not performed by this source generator.
