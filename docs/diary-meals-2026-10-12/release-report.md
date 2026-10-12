# Shared food diary — October 12, 2026

The public diary keeps one layout and one private notebook across all eight supported restaurant markets: United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan. Country selection changes the available restaurant and packaged-food sources; it does not hide entries or replace a logged food's source country.

## Implemented

- Breakfast, Lunch, Dinner and Snacks remain visible on every date, including empty dates. Each has its own Add food action, food count and truthful nutrient totals.
- Food review inherits the meal chosen in the diary. Native radio buttons allow changing it in the picker; editing can move an existing entry between meals.
- A shared browse catalogue exposes 1,200 existing source food profiles in 12 groups: breakfast grains, eggs/dairy, starches, meat/seafood, plant proteins, fruit, vegetables, prepared meals, snacks/chocolate, nuts, drinks and sauces/oils. Show more expands the list in batches of 12.
- Browse selections load the exact source shard and retain preparation, serving, nutrition provenance and missing values. Vague NFS/unspecified entries and named-chain reference foods are excluded from this curated browse subset.
- Explicit diary dates persist within the browsing session when changing countries. Saved foods, favorites, recipe yield calculations, notes and backups keep the existing local storage schema. Historical Snack entries display as Snacks.
- Empty days show a dash; completely missing nutrients show Unknown; partially known totals identify the known subtotal and missing entries. Actual source zero values remain zero.
- Dialog dismissal avoids stealing focus from a subsequent keyboard action. Source links for reviewed Canadian retailer products now open the matching diary review.
- The matching shared catalogue and icon sprite are included in the versioned offline shell. The real previous release can upgrade while preserving private snapshots; previously loaded profiles and recent saved portions remain available offline.

## Verification

Full existing build: python -X utf8 tools/run_food_build.py passed. Route/link/metadata checks covered 348 public HTML files, 345 sitemap pages and 344 searchable resources. The pre-existing warning about identical home headings across eight country homepages remains; these are equivalent market entry pages.

The new test-diary-meals.cjs checks all 1,200 browse identities against source indexes and shards, preparation types, 100 g basis, portion arithmetic, null handling, bounded one-shard loading and offline catalogue inclusion.

Existing food computation, branded source search and macro arithmetic tests passed. The complete existing diary browser suite passed in both themes at 320, 390, 768, 1280 and 1440 px: source review, persistence, editing, favorites, keyboard tabs, dismissal, removal/undo, recipes, backup merging and corrupt-import rejection.

The new check-diary-meals.cjs exercises each meal's Add action, source arithmetic, editing/moving, undo, date retention, all eight countries, common browse content, unknown totals and page overflow at the same five widths in both themes. Actual local screenshots are in docs/diary-meals-2026-10-12: empty-*.png, logged-*.png and browse-*.png.

The new test-diary-upgrade.cjs installs the real prior deployment on one local origin, saves a food, upgrades to the new worker, compares private entries exactly and verifies styled offline diary, shared browsing and recent portion review.

Production publication and verification are recorded separately after deployment. Local checks alone are not a claim that this release is live.

## Scope and limits

The 1,200 items are newly browsable choices from existing source-backed profiles, not 1,200 newly measured or newly researched nutrition records. General reference foods are available worldwide, while their USDA source identity and preparation assumptions remain visible. Canadian reference profiles and local menu/package records remain searchable through their appropriate sources.

There are no new market launches or invented package/menu records in this task. Country coverage is limited to the eight published markets; language remains reviewed English. The diary is stored in this browser, with export/import, and has no account or cross-device sync. New profiles may require a connection. No AI/photo estimates, medical conclusions, indexing or traffic claims are made.
