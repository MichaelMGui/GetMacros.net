# Homepage and diary — October 17, 2026

This pass changes the shared homepage composition and private food diary. It does not add markets, restaurant values, grocery imports, AI logging, or new articles.

## Implemented

- One masthead, original food-character stage, and integrated calorie/protein finder bar across the eight existing market homepages. Local records and destinations remain local.
- Open featured-order layout with aligned nutrition and source disclosure, restrained brand accents, and real view/compare links.
- Diary header with a clear Add food action, compact day navigation, one meal workspace and a daily-overview sidebar. Breakfast, lunch, dinner and snacks remain the same in every market.
- Mobile logged meals appear before the overview. A one-food meal no longer repeats its nutrients as a second meal-total block.
- Compact accessible meal choices, source tabs, and native collapsed category browsing in food search. Existing source filters, recent foods, favorites, recipes, saved orders, review, export/import and local storage remain.
- Broccoli is approximately 27% larger on desktop and 22% on mobile. Existing wave and celebration interactions remain; reduced-motion preferences are respected.
- Homepage-only styling is isolated from the shared stylesheet, which remains below its existing 70 KB budget. Immutable assets and offline-worker references are regenerated.

## Evidence

`before/`: four actual baseline screenshots, homepage and diary at 390 and 1280 CSS pixels.

`after/`: 30 automated rendered states: U.S. homepage, Canadian homepage and diary at 320, 390, 768, 1280 and 1440 pixels in both themes. No page overflow or runtime errors were found. These checks do not mean every screenshot was manually inspected.

Manually inspected: homepage at mobile and desktop widths, empty and filled diary at mobile and desktop widths, and food search/review in both themes. Actual images are in `after/` and `journeys/`.

`journeys/`: four complete workflows at 390 and 1280 in both themes, including keyboard opening/Escape/focus return, food search, portion review, favorite, breakfast logging, reload persistence, edit, removal/undo, date navigation, export and Canadian homepage-to-finder state.

Additional checks: eight-market shared-home structure and exact records; private diary hooks and category disclosure; nutrition/unknown-value computations and backup integrity; unchanged calculator arithmetic; asset cache tests; route/link/source metadata checks in the production build.

The initial restricted Windows build reached its final fixture tests and encountered sandbox temporary-directory permissions. The staged build is validated separately outside that restriction. Deployment and final staged-build status are recorded in the accompanying JSON reports.

## Limits

No claim of a complete accessibility audit, physical-device/Safari testing, field performance improvements, search ranking gains, or completion of the larger international/data release. Existing data, formulas, URLs, sources and private-diary storage are preserved.

## Final source-build result

The complete staged production build passed outside the restricted Windows fixture sandbox. All 494 compared public pages, active assets, manifests and the offline worker matched the reviewed application exactly. The earlier additional food, generator, country and integration suites also passed; their first output comparison identified the corrected stylesheet-link placement. A repeated regional/template/asset cycle now preserves all eight homepage files byte-for-byte.
