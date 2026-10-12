# Shared diary continuation — October 12, 2026

This release continues the food-log work while preserving the existing visual identity, sources and private diary schema.

## Implemented

- Expanded the shared browse collection from 1,200 to 9,905 existing source profiles. This is 8,705 additional browsable choices, not newly measured nutrition records. Twelve groups remain, with common source-identified foods near the top. Oats, potatoes, juice and peanut butter have more useful group placement.
- Added raw/cooked preparation filtering based on explicit words in source descriptions. Ambiguous descriptions remain in All preparations. Name A–Z now sorts browse results too. The selected food group is remembered per meal for the current page session.
- Added Previous day, Next day and Today controls using calendar arithmetic that does not shift dates across daylight-saving changes.
- Added a reviewed Repeat meal action. Choose the source date/meal and destination date/meal; inspect foods, portions, countries and energy before confirming. Notes are left out unless explicitly selected.
- Copies preserve the complete saved source snapshot, including quantities, units, source version, country, provenance, true zeros and unavailable nutrients. They do not fetch current menus or substitute another market's record.
- Batch copies use one native IndexedDB transaction. Invalid snapshots are rejected before insertion; retry IDs are stable; controls guard against duplicate submissions and source-loading races.
- Diary entries display in saved-time order. Copy IDs preserve the reviewed order inside a batch.
- Companion updates now read up to three distinct date keys rather than exporting every private entry, recipe and favorite on each day render. No IndexedDB version change or existing-data migration is required.
- The existing green day/night themes, food character, familiar controls, formulas, URLs and country-specific menu data are retained.

## Actual verification

The full existing build and route/link/metadata pipeline passed: 348 HTML routes, 345 canonical sitemap pages and 344 searchable resources. The unchanged warning about identical headings on equivalent country homepages remains.

The browse integrity test checks every exposed ID, name, type, shard and 100 g source basis against existing indexes and profile files. Nutrient computations, null handling, snapshot validation, source-specific search and original calculator tests remain covered by the existing build/tests.

The new check-diary-more.cjs runs native IndexedDB and real source profiles in both themes at 320, 390, 768, 1280 and 1440 px. Checks include empty repeat state, daylight-saving dates, preparation filters, sorting, group retention, exact Canadian/reference snapshot copies, rapid double-submit, corrupt-batch rejection, stable retry IDs, optional notes, duplicate-meal warning, date/country persistence, export validation and overflow/runtime errors.

Existing check-diary.cjs exercises source review, saved portions, editing, favorites, keyboard tabs, recipes, removal/undo and backup merging/rejection at the same five widths in both themes. Existing check-diary-meals.cjs checks shared browsing and the four meal sections across all eight published markets.

The real upgrade test starts from deployed revision e1fc7893d4985dfb3ae21466e13689d15296a504, preserves the private entry exactly and checks the new worker, styled diary, shared food catalogue, recent portions and repeat review offline.

Actual local screenshots: docs/diary-more-2026-10-12/browser/preparation-*.png, repeat-*.png and copied-*.png. The baseline source checkpoint is baseline.zip with hashes in baseline.json. Production verification is recorded separately after deployment.

## Limits

The expanded collection consists of existing USDA composition references, including historical and reference-recipe editions, rather than exact measurements of a visitor's plate. Their source descriptions and source dates remain visible. Local restaurant/package sources still depend on the selected market. No new restaurant records, market launches, authors, nutrition claims, translations or indexable landing pages were invented for this diary release.

The diary remains private to this browser, with export/import and loaded-data offline support. There is no account sync or connected AI/photo analysis. No traffic, indexing, AdSense or medical outcome claim is made.
