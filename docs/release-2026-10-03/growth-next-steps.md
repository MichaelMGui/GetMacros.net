# Growth priorities after this release

Prepared October 3, 2026. These are proposed next actions, not claimed results. No outreach, posts, purchases, account changes or advertising resubmission were performed by this work.

## Start with evidence rather than another redesign

The release creates a clearer product and more useful reference material. It does not establish that the site now ranks well, has repeat users or qualifies for advertising. Current Search Console and analytics exports were unavailable to this work. Earlier screenshots are historical context, not a current baseline.

Google’s [Search Console performance guidance](https://support.google.com/webmasters/answer/7576553?hl=en), inspected today, supports comparing queries, pages, countries, devices and date ranges. Obtain a fresh export after the live release is confirmed. Use completed periods and note that recent data may be preliminary. Avoid judging an entire site from a handful of daily impressions or a one-click CTR percentage.

## Priority order

| Priority | Useful next action | Evidence to keep | Decision it enables |
| --- | --- | --- | --- |
| 1 | Confirm the shipped build, representative working finder journeys and canonical indexable URLs. Inspect key pages in Search Console when authorized. | Release identifier, inspected URLs, actual errors and crawl dates. | Separates deployment/indexing failures from low search demand or weak rankings. |
| 2 | Export Search Console query/page pairs for equal completed periods, segmented by U.S. versus other countries and mobile versus desktop. | Clicks, impressions, CTR and position as reported, with dates and filters. | Identifies the actual pages gaining exposure and whether foreign-market intent is mismatched to U.S. menu data. |
| 3 | Observe a small number of real, willing people completing “find lunch,” “compare two meals” and “use a daily estimate to pick an order.” | Where each person hesitates, fails, misunderstands a portion or finds an unsupported nutrient. | Produces concrete usability changes before adding more content. Do not record sensitive calculator values. |
| 4 | Offer one focused reference to a small, relevant audience once outreach is authorized. | Exact destination, why that audience needs it, permission/channel rules and voluntary feedback. | Tests whether original utility attracts interest beyond broad “healthy fast food” queries. |
| 5 | Improve an existing page that has sustained relevant exposure, rather than publishing many keyword variants. | Original query/page export, changed summary/title/content, subsequent equal-period comparison. | Helps distinguish a clarity improvement from day-to-day noise. No ranking guarantee. |
| 6 | Maintain the most-used restaurant records and document material changes. | Official source edition, retrieval method, nutrient-specific verification and broken/changed records. | Makes returning to the product worthwhile and reduces stale comparisons. |

## A small launch package worth sharing

Choose one of these resources rather than promoting every new page at once. Their purpose is specific and can be demonstrated without broad health promises:

- **Protein density versus meal size:** `protein-density-fast-food.html` compares selected supported orders and explains why a small chicken serving and a whole bowl answer different questions. Its source-inspected selection is not an exhaustive “healthiest restaurants” league table.
- **What the database can and cannot answer:** `fast-food-nutrition-data-report.html` is a reference for coverage, missing values and provenance. It is a better credibility asset than claiming every restaurant number is current.
- **Raw or cooked weight:** `raw-vs-cooked-food-weight.html` offers a practical measured-batch workflow for meal preparation, with clearly hypothetical arithmetic rather than invented food data.
- **Bulk buying and waste:** `protein-cost-food-waste.html` shows when a larger package stops being cheaper per usable gram of protein. It supports the existing protein-cost calculator without creating a duplicate calculator page.

For each selected resource, prepare a short accurate summary, a readable screenshot of its original worked table and a link to the relevant tool. Label hypothetical examples as examples. Obtain permission before redistributing restaurant source data or imagery; attribution alone does not establish reuse rights.

Potential audiences are meal-prep readers, fitness coaches looking for portion explanations, food-budget communities and people discussing lunch options. These are audience hypotheses, not a researched contact list or endorsements. Read each venue’s current self-promotion rules and contact preferences before proposing a post. The owner should approve the concrete message and destination before anything is sent. No automated bulk pitches, paid-link offers or disguised personal recommendations.

## Measure usefulness with the product’s actual capabilities

The current `js/product-events.js` exposes a provider-free event interface for finder starts, quiz completion, applied filters, meal opens, comparisons, calculator completion, article-to-finder navigation and shares. These browser events are **not an analytics database or a measured growth dashboard**. Without an authorized collection system, they do not tell us totals, unique visitors or return frequency.

If measurement is later configured, keep it consistent with the privacy notice and consent requirements; collect only the minimum necessary product event information. Never attach age, body weight, health context, calculator input values, free-form search text or sensitive query parameters. Treat shares as actions taken, not proof that a recipient visited.

Useful questions are whether people reach a usable result, understand what is included, use comparison controls, follow a resource into the finder and voluntarily return to saved meals. Pageview inflation is not the goal. Qualitative feedback and confirmed bug reports remain useful when analytics access is unavailable.

## Keep search and advertising separate

Google’s [AdSense eligibility guidance](https://support.google.com/adsense/answer/9724?hl=en), inspected today, calls for original, useful content and policy compliance; it does not guarantee approval because a redesign or article count was completed. Its [publisher spam-policy guidance](https://support.google.com/publisherpolicies/answer/11035931?hl=en) also states that participating in advertising does not improve search ranking or queue pages for crawling.

Do not spend this release resubmitting the same application. Keep the provider-independent ad infrastructure inactive until there is a deliberate provider decision and compliant placement review. Work on genuine audience use and source quality first. No bot traffic, purchased clicks, artificial refreshes, copied articles or hundreds of nearly identical filter pages.

The sixteen qualitative query observations and the implemented query-to-page map are recorded in `seo-research.md`. They identify opportunities, not search-volume forecasts. Revisit that map when actual query/page evidence is available, preserving established URLs and improving the page that already serves an intent.
