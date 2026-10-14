# Mexican Subway portion correction — October 14, 2026

The release editorial audit found a 43 g Turkey Breast ingredient amount shown
as a complete six-inch sandwich. Both pages of the pinned official Mexican
November 2025 PDF were rendered and read during this correction audit.

[Official source](https://www.subway.com/v1v2/assets/es-mx/nutrition/documents/mexico-nutrition-112025-eng.pdf).
Pinned SHA-256: `80cf7369eaf6651d4d0efd4020d42eb65045752446fa0fd37eb637b8089c715b`.
The stored nutrition retrieval/review is October 11. The new classification
review is October 14; the source edition and numeric values were not redated.

## Cause and fix

The old importer treated any section header containing `6"` as a complete
sandwich section. It therefore misclassified the source’s Individual Meats
heading, which describes a portion used on a six-inch sub or salad. It also
reset the section at page breaks, losing the heading of two continued bread
rows. Desserts and sides were assigned the broad ingredient category.

`tools/product_release/subway_mexico.py` now explicitly classifies the reviewed
source sections. An unknown new heading fails closed. The Breads section
continues correctly onto page two. Separately listed meats, cheese, vegetables
and condiments remain ingredients, while actual desserts and sides have their
own categories. Each record includes its exact source group and an explicit
finder eligibility flag. All published IDs are retained; private historical
diary snapshots are not rewritten.

| Review result | Count |
| --- | ---: |
| Tracked source records retained | 93 |
| Categories corrected | 20 |
| Individual meats removed from complete-meal matching | 11 |
| Desserts given their correct food category | 6 |
| Sides given their correct food category | 3 |
| Continued bread labels recovered | 2 |
| Component names refined | 39 |
| Numeric nutrient values changed | 0 |
| Public IDs changed | 0 |
| Finder entries before → after | 53 → 51 |

The final category counts are 42 entrees, 42 components, six desserts and three
sides. Components can still be reviewed/logged as their named ingredient
quantity; they are not displayed as complete restaurant meals.

The two Turkey Breast identities make the distinction concrete:

| Record | Native portion | Calories | Protein | Eligibility |
| --- | ---: | ---: | ---: | --- |
| `MX\|subway\|1c5926505abe2837` | 205 g complete six-inch sub | 270 kcal | 15 g | Finder |
| `MX\|subway\|691a1d7272aeef35` | 43 g individual meat portion | 50 kcal | 5 g | Ingredient only |

No new menu records are counted for this correction. No missing nutrient became
zero, U.S. recipe was substituted, or calorie/macro value was inferred.

## Actual checks

Eleven Python tests passed:
`python -X utf8 tools/clarity_release/test_mexico_classification.py`.
They cover the two Turkey identities, every final category/count, page-break
continuations, source units/edition, public IDs, unchanged native quantities,
unknown headings, missing macros, and the full pinned source parse when its
private extraction is available. Small independent parser fixtures continue to
run when private research files are excluded from publication.

The full updated international importer was also dry-run against its pinned
local evidence with file writes captured in memory. All 734 country-scoped rows
exactly reproduced the committed-source fixture content; other markets had zero
changes. No public output or historical report was rewritten by that check.

Source fixture/importer changes are complete. Root integration must rebuild the
shared registry, market finder, source tables, comparisons, contextual articles
and search outputs, then exercise those pages in the browser before publication.
This subtask has not deployed or claimed those generated pages live.
