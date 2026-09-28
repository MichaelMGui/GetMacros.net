# AdSense content and publication review — September 28, 2026

## What is known

The user reports another “low-value content” rejection. We cannot see Google's internal review or identify its exact deciding page. Public web retrieval showed the older homepage and five-question finder, while the checked-out working tree contained the unpublished Market interface. The remote main branch matched local HEAD before this release, so the missing update was in the working tree, not a remote merge conflict.

## Research actually performed

Read Google's current guidance on September 28, 2026:

- https://support.google.com/adsense/answer/7299563?hl=en — original, relevant content; clear navigation; meaningful contribution beyond external material.
- https://support.google.com/adsense/answer/12176698?hl=en — live, accessible pages and enough valuable content; request review after addressing issues.
- https://developers.google.com/search/docs/fundamentals/creating-helpful-content — people-first usefulness and originality. This is Search guidance, not an AdSense approval guarantee.

Opened the official Chick-fil-A grilled-nugget page, Chipotle nutrition calculator, Panda Express nutrition page and ISSN protein position stand. The Chick-fil-A page displayed 130 calories, 25 g protein, zero fiber and 440 mg sodium for its displayed serving. Chipotle's extracted calculator page did not expose useful nutrient values. These checks are not a fresh audit of all 83 records, and restaurant check dates were not advanced.

## Implemented content changes

1. Replaced repetitive goal-ranked cards on all 15 restaurant guides with a distinct ordering decision, two exact records, meaningful interpretation, portion caveats and direct source links. Examples include half versus whole salads, six-inch versus footlong, chicken alone versus chicken with a side, and incomplete Taco Bell data. Figures are generated from the same dataset as the finder and tested against it.
2. Refocused `body-recomposition-explained.html` on recording and interpreting progress. The separate calorie-deficit article retains the evidence discussion. Kept existing public anchors, citations and URL; labeled examples as hypothetical rather than firsthand testing.
3. Removed ten duplicate article contents menus. The primary contents menu remains.
4. Corrected the methods page: default “complete” means known calories, protein, fiber and sodium, not verified values for every nutrient. Explained preferences versus exclusion filters and comparison-writing dates versus data checks.
5. Preserved established URLs, source records, formulas, verification and advertising configuration. Updated sitemap modification dates only for the new substantive restaurant/methods/recomposition changes.
6. Included the previously implemented, tested Market interface in the publication release. No new visual direction was introduced.
7. Excluded development logs and root audit reports from GitHub Pages output, in addition to existing design/docs/tools exclusions.

`content-inventory.csv` records all 73 HTML pages and distinguishes editorial work from mechanical inventory. `repeated-paragraphs.json` found three long cross-page repeats: data-check disclosure, comparison-date disclosure and a specific meal composition shared with the homepage. Those are necessary context, not paragraphs to remove for artificial uniqueness. Word counts are inventory aids, not quality thresholds. This pass does not claim a line-by-line medical review of all retained articles or external plagiarism detection.

## Verification

- 1,036 route/theme/width checks: zero failures before the final minor table-caption adjustment; final rerun recorded in the release status below.
- 12 Chromium/WebKit publication journeys passed: navigation, calculators, unit conversions, invalid inputs, recipe/label tools, meal comparison/save, provenance and restaurant entry.
- Eight homepage/contact journeys passed. No email sent.
- New content tests verify all 15 comparison pairs against the dataset, retain missing values, reject duplicate contents blocks and preserve article anchors.
- Static validators pass: 73 HTML pages, 72 indexable pages, 72 sitemap URLs, 71 searchable resources and 3,754 internal links/anchors.
- Shared CSS is 54,312 bytes. This is an asset-size measurement, not a field performance score.
- Twenty viewport screenshots captured in `screenshots/`. Directly inspected Chipotle desktop/light, Taco Bell mobile/dark and recomposition mobile/light; corrected a clipped mobile table caption after inspection. Other screenshots are captures, not claimed manual inspections.
- `git diff --check` passed (line-ending notices only).

## Limits and next review

Approval is not guaranteed. No arbitrary article count, word count, traffic threshold or waiting period is claimed. No automatic AdSense review submission is performed. Before requesting another review, verify the deployed release is visible and exercise the finder on the live site. Some restaurant nutrient values and local availability remain unverified, visibly disclosed. Existing ad serving remains paused; publisher verification is retained. Do not describe this release as a fresh nutrition-data verification or full accessibility certification.

## Release status

Implementation and local validation completed; deployment and live verification are recorded separately after the push.
