# GetMacros global product release — October 11, 2026

This release extends the existing product and food-character identity. It does not claim to cover every food, country, restaurant or current menu. The implementation revision **f08ae38b8463f6fede91b3e14bd7d35e5700ea4b** is live through the existing GitHub Pages workflow. Pages deployment and both Site quality jobs succeeded. `deployment-verification.json` records 341 actual live HTTP route checks, matching public asset hashes, 338 sitemap pages and private paths returning 404. `verified-live-links.csv` contains all 39 new routes plus the substantially extended existing raw/cooked guide. Sitemap submission and indexing were not verified.

## Delivered implementation

- General food library: **13,578 reference profiles**, from USDA Foundation, SR Legacy and FNDDS editions. Records include preparation, per-100-g values, available source household weights, up to 30 nutrient fields and provenance. An absent value stays unknown. The full database is split into lazy-loaded shards instead of being loaded on the homepage.
- Private food diary: local IndexedDB entries, portion review, date/meal/note editing, favorites, recent portions, recipe yields, known daily subtotals, available micronutrients, removal/undo, export, validated atomic import and deletion. Saved source snapshots are retained even when public data changes. No account or cloud synchronization is claimed.
- Installable web-app foundation: manifest, explicit update control and public-resource offline cache. Cached food profiles and the diary work offline; private entries, notes, photos and recordings are not put into the shared resource cache. Native iOS/Android apps and store releases were not built.
- Positive optional food companion: accessories celebrate notebook use. No missed-day punishment, physique judgment or health grade.
- Country browsing: United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan. Explicit country URLs take priority over saved preferences. Compatible nutrient limits survive switching; incompatible restaurants/orders are cleared with a notice. Country and interface language remain separate. Only the English interface is published; original Japanese menu names are retained.
- **734 additional market-specific menu records**, producing **1,400 total registry records**. These represent **668 distinct new source rows** because the official UK/Republic of Ireland Subway edition supports 66 rows in each market. Do not count that shared edition as independently researched twice.
- Ingredient/component comparison across countries and continents: named components, exact portions, source editions, nutrition, missing formulation information, shareable identifiers and source-version warnings. Differences mean “only named in this source,” not proof of ingredient absence or allergy safety. Not all menus publish full ingredient formulations.
- Country-aware exact-order and complete-order tools, local-price protein-value currencies, saved order sharing and search. Non-U.S. finders say “items” because supported drink records are included.
- Navigation integration across all public pages, both existing themes, coherent controls, short interactions, reduced-motion behavior and narrow-screen table scrolling. The successful existing illustrations, fonts, calculator formulas and URLs are preserved.

## Data scope

New records: UK Greggs 271, UK Subway 66, Ireland Subway 66, Australia Guzman y Gomez 15 standard mild builds, Mexico Subway 93 items/components, New Zealand Subway 17 standard six-inch builds and Japan McDonald’s 206 items.

Source documents were retrieved and relevant layouts inspected. Published numeric facts and named components were transcribed, with source hashes/pages/editions and calculations recorded. This is source verification, not laboratory analysis or a full local-availability audit.

- Food editions: USDA Foundation April 2026; SR Legacy final 2018; FNDDS 2021–2023, released October 2024. Historical profiles are labeled rather than represented as measurements of today’s exact meal.
- Restaurant editions: Greggs September 2026; Subway UK/ROI September 2026, Mexico November 2025 and NZ October 2025; GYG Australia March 2026; Japan’s official online table retrieved October 11, 2026.
- Salt-equivalent conversions and native kilojoules are distinguishable from published sodium/calorie fields. Ambiguous Greggs g/ml columns do not receive invented gram conversions. Source bounds and unavailable nutrients remain unknown.
- Three USDA sugar/carbohydrate inconsistencies are flagged rather than silently repaired. Forty pre-existing U.S. records still lack verified fat values. Canada’s contradictory A&W Mango Shake record remains withheld; McDonald’s Canada remains a research gap.
- Mexico McDonald’s, Indian and Singaporean attempted sources did not yield adequate publishable evidence. Those markets/chains were not substituted with U.S. data.

## Content, licensing and SEO

Two new editorial resources are published: diet-label/evidence guidance and Read & Watch. The established raw-versus-cooked guide gains five source-linked weighed examples. Existing factual article bodies and dates were otherwise preserved; this release does not claim a complete new editorial re-verification of all old articles.

The diet guide distinguishes NHS guidance, Mediterranean guidance, controlled DASH evidence and the limitations of the self-selected carnivore survey. No clinician/dietitian review is fabricated. The resource shelf has three publisher/institution-checked resources, honest streaming limitations and no reproduced covers. Creator recommendations remain pending review.

`seo-research.md` records actual current primary guidance and qualitative search observations. `query-to-page.csv` maps 37 new public intents. Descriptive metadata, source links, crawlable country pages, reciprocal region annotations for genuine equivalents, canonical URLs and a published-only sitemap were implemented. No keyword-volume, ranking or traffic forecast was invented.

There are **341 public HTML routes, 338 indexable canonical pages and 337 search resources**. The diary and offline utility are noindex; personal filters and food profiles do not produce thousands of indexed URLs. General articles remain global rather than false country/language alternates.

USDA data is public-domain/CC0. Original flags and distribution SVGs were created in the repository. Restaurant facts link to official sources; original source PDFs, raw downloads and internal research reports are excluded from Pages. `source-rights-and-queue.md` records other national databases researched but not yet imported.

Four original comparison graphics, four short-video scripts, two newsletter drafts and two outreach drafts are prepared in `distribution/` and `distribution-drafts.md`. Nothing was posted or sent externally.

## Verification actually performed

- Complete build in the root workspace and isolated publication checkout; publication/link/metadata/content/source validators passed.
- Clean staged-source export build passed without untracked inputs. Evaluated meal arrays match in every field and order; five differences are equivalent JavaScript serialization and its dependent asset/cache hashes. `clean-source-check.json` records that distinction.
- Repeat-integration regression passed. It protects the app manifest/shortcuts and unique currency options from being reset or duplicated by later builds.
- `tools/product_release/run-checks.py`: 17 commands passed, covering existing formulas, filters, order tools, country isolation, content, metadata, search, source checks and asset stamps.
- `tools/restaurant_release/test_expansion.py`: 15 tests passed.
- `tools/product_release/test-food.cjs`: 11 checks passed for source portion math, null propagation, recipe yields, snapshot validation, exports, search relevance and market isolation. Live QA identified the olive-oil ranking issue; ingredient matches now rank before dishes containing the ingredient.
- `node --test server/test/service.test.cjs`: three service tests passed, including actual local HTTP requests with injected provider responses. These are not live AI quality evaluations.
- `tools/product_release/test-image.cjs`: actual Sharp decode/resize/metadata-removal validation passed on a synthetic image. This is not food recognition testing.
- Semantic contrast checker: 44 token-pair checks passed. This is not a claim of complete WCAG certification.
- All-route rendered checks: **682 renders**, each of 341 routes at 390 and 1280 CSS px. A genuine search `insertBefore` runtime error was found, corrected and the failed routes rerendered successfully. Original failure evidence is retained.
- Representative product checks: **80 renders**, eight page families, light/dark at 320, 390, 768, 1280 and 1440 px. Overflow/runtime checks passed; real diary edit/favorite/recipe/import/delete and offline journeys passed.
- Additional journeys: four light/dark mobile/desktop runs covering country switching, retained limits, empty/typo search, exact-order tools, ingredient-link restoration, source-version warnings, local photo preview with no disabled-service API request, navigation dismissal and reduced-motion settings.

Actual files: `route-renders.json`, `test-results.json`, `final/checks.json`, `journey-checks.json` and `final/*.png`. `coverage.csv` distinguishes automated rendering from manual screenshot inspection. Not every route was manually inspected. Representative old and new page families were reviewed as screenshots.

Real production browser verification passed in light/dark at 390/1440 px: live source lookup and portion review, the private diary with AI truthfully disabled, UK/NZ named components and 198 g/236 g serving definitions, and the UK finder. There was no request interception or local fixture. Sixteen actual screenshots and four journey results are in `production/`. The mobile light comparison, desktop dark comparison and mobile light source-portion dialog were manually reviewed. Production visits here are QA, not evidence of traffic growth.

The first production check also exposed an omitted `.webmanifest` in the explicit publication file list. The publisher now includes it, preserving the reviewed app colors, scope and shortcuts on the actual static deployment.

Local warm-search timing is lab-only and not a real-user metric or Lighthouse score. There is no authorized analytics or Search Console export/connector, so the reported visitor increase, acquisition sources, field performance, submitted/indexed counts and receiving-clicks remain unverified. Sitemap inclusion is not indexing.

## AI activation and remaining work

The repository now contains an actual separate Node 24 backend and browser text/photo/push-to-talk adapter: source lookup, structured candidate IDs, deterministic source calculations, draft review, explicit submission consent, image processing, origin/session controls, request deduplication, persistent daily request quotas and sanitized errors. It stores no diary, private description, photo or recording body.

**It is not connected to production.** GitHub Pages cannot execute the backend. `js/app-config.js` deliberately remains `aiEnabled: false` with no endpoint. The owner must authorize a backend host and spend cap, configure secrets privately and review the actual provider retention/consent configuration. No credentials, hosting purchase, DNS change or paid API activation was performed. `store: false` is not a promise of zero provider retention.

Before activation: install the pinned server dependencies on the approved host, validate proxy/IP/HTTPS configuration, set and test persistent quotas, evaluate actual text/photo/voice accuracy and ambiguity handling, measure cost/latency, review privacy notices, and run production integration tests. The prepared adapter must not be described as working live recognition before these checks occur.

Other remaining limitations: no cloud sync/accounts or native app; no real iOS/Android hardware testing; no full screen-reader/manual accessibility certification; incomplete ingredients and optional nutrients in some menus; unreviewed language translations; additional national databases/countries in the research queue; creator recommendations and health-sensitive expert review pending. The interface explicitly labels these limits rather than presenting unsupported features as complete.
