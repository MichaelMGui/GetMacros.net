# GetMacros master international release — October 12, 2026

## Implemented product changes

The eight supported homepages now share one product-led composition, using that country's actual records and finder destinations: United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan. No flag-only market was launched.

Country controls use original SVG flags, full names, crawlable links, keyboard movement, Escape/focus return and remembered explicit preferences. Deliberately opened country URLs take precedence. Language remains separate and honestly offers English only. Appearance has labeled day/night choices and persistence.

Today's food, totals and Add food lead the rebuilt diary. One picker provides Search, Recent, Favorites, Recipes and Saved orders. Every food is reviewed with its market, source, quantity and supported unit before logging. Editing, remove/undo, recipe yields and private import/export remain functional. Preferences holds backup, deletion and offline information. Installation promotion and unfinished photo/voice/AI entry points were removed. No backend or paid AI provider was provisioned.

Food search supports names, brands, barcodes, aliases and bounded typo matching. Reference foods, packaged labels and restaurant records are distinguished. Label dates and dataset editions are separate. Unsupported densities never turn millilitres into grams, unknown nutrients stay unknown, and a Canadian search does not borrow U.S. products.

Packaged-food and barcode searches skip unrelated reference and restaurant inventories. Cold-load source checks verify this rather than merely measuring the isolated grocery adapter.

Reviewed foods can be compared on named portions or source-supported 100 g weights. Downloadable SVG cards include markets, units, source editions/URLs and applicable Canadian attribution. The existing country ingredient comparator retains source-listed components and warnings about differing servings; matching names do not establish identical recipes.

The broccoli is approximately 25% larger on mobile and desktop, with original expressions and brief action feedback. It does not punish missed logging or assign a health score. Existing food artwork and licensed Bricolage/Inter files are retained. No misleading stock restaurant photography or new animation dependency was added.

Menus, featured meals, source disclosures, native controls, calculator errors and responsive alignment were refined. Restaurant shortcuts are recognisable actions. The existing 56 games have seven coordinated presentation families and original SVG motifs; rules and scoring remain intact. 116 obsolete presentation fragments were removed from source styles. Compiled shared CSS is 69,303 bytes, below the unchanged 70 KB gate.

## Data and new publication

| Addition | Count | Qualification |
|---|---:|---|
| Canadian restaurant records | 282 | Six additional chains, exact source serving definitions |
| New records with all four core macros | 243 | Includes components and three explicitly calculated Domino's builds |
| New calorie-only records | 39 | Pizza Nova in-store slices, excluded from macro finder |
| USDA branded records | 36,862 | 35,755 U.S.; 1,107 New Zealand; manufacturer labels, not independent current-package audits |
| Reviewed Canadian retailer labels | 4 | Kirkland nuts, peanut butter and yogurt; no invented barcodes |
| Canadian Nutrient File references | 5,993 | Health Canada 2026 reference edition; not branded products |

The original 13,578 USDA reference profiles remain. Total branded catalogue: 36,866. New grocery/reference rows: 42,859. Restaurant registry: 1,682 records. Canada has 356 total records and 266 usable finder entries; components and incomplete core macros are excluded. These are tracked selections, not audited complete menus or live store inventory.

Six new guides: Subway Canada (85 records), Domino's Canada (46), Mary Brown's (48), Booster Juice (48), Pizza Pizza (16) and Pizza Nova (39). One new guide explains portions, barcodes, recipes, missing nutrients and private backups. The Canadian directory distinguishes 25 confirmed chain presences from local nutrition coverage and finder readiness. The full presence matrix contains 57 country/chain relationships.

Subway recipes and different same-name builds stay distinct. Domino's totals sum named small-pizza components, with rounding and slice assumptions. Ambiguous Mary Brown's large portions and implausible rows are withheld. Contradictory Pizza Pizza saturated-fat values stay null. Pizza Nova's in-store slice basis is explicit; its signature-pizza denominator remains unresolved.

USDA is separately distributed with CC0 attribution. CNF has Open Government Licence—Canada attribution. Four Costco Business Centre label observations have their own rights/limits file; no retailer photos or wholesale catalogue was copied. Open Food Facts research hit 503 failures; requests stopped and no OFF records were imported. Raw ZIPs, PDFs, snapshots, source interfaces and private data are excluded from production.

## Copy and SEO

The shared homes replace repeated discovery introductions with one finder entry and useful local meals, tools, reading and play. Diary and Canadian guides use task-specific writing and serving explanations. Source/privacy wording no longer exposes internal release language.

The automated main-content audit covers 348 routes: 110 repeated groups, zero flagged internal-project phrases. Largest repeats are legitimate worked-example disclosures, game instructions and source/geography limitations; they were retained deliberately. This is targeted editorial review and automated auditing, not a claim that every old article was rewritten.

Actual current research is retained in restaurant-seo-research.md, restaurant-research.md and grocery-source-research.txt. It covers Google guidance on helpful content, spam, regional/localized versions, facets and titles; actual Canadian queries and competing page types; official menus and grocery licensing. No keyword volumes, competitor traffic or forecasts were invented.

Applied changes include distinct titles and answers, useful serving comparisons, source trails, local tool links, search entries and sitemap inclusion. Only genuine country home/finder/directory equivalents receive reciprocal regional annotations. Inherited homepage alternates were removed from games and general articles. Existing URLs remain. Filters and private diary states do not create indexed page explosions.

Public scope: 348 HTML routes, 345 canonical sitemap pages, 344 searchable resources. Diary/offline pages stay intentionally noindex. No authorized Search Console or analytics data were available: the earlier visitor increase, submissions, crawling, indexing and traffic impact remain unverified.

## Actual verification

Actual previous-production baseline: 40 screens in baseline/, with representative screens read. Active local files governed implementation. baseline-source.zip is a reversible source checkpoint. Root protected Git and unrelated music-platform work were preserved.

- Full build: tools/run_food_build.py. Isolated Git-index build: tools/master_release/clean-build.py; final result in clean-source-check.json. Tests were not deleted or thresholds raised.
- The final isolated build passed with zero public-file differences against the tested application. Immutable source hashes, module uniqueness and genuine reciprocal country annotations passed three additional asset/SEO checks.
- Existing 17 quality commands passed (quality-final.log): calculator math, filtering, growth tools, food arithmetic, publication, metadata/links, eligible content and asset checks.
- New gates: 11 restaurant tests, 7 import-boundary tests, eight homepage/source checks, 26 real-source search checks, and integrity inspection of every one of the 42,859 new rows. All 671,425 absent nutrient fields remain null.
- 2,240 deterministic game-rule cases passed. Backend tests used an injected provider over real local HTTP; this does not establish a live AI service.
- All 348 routes automatically rendered at 390/1280 in both themes: 1,392 checks of HTTP, heading, theme, loaded CSS, runtime errors and overflow. This is not manual viewing of every page.
- Design calibration: 108 homepage/game renders, four country/theme/navigation/finder journeys, 50 alignment renders, 60 additional surface renders and 60 calculator/source/search/menu journeys. Screens in design-final/ and surfaces-final/. Manual views are recorded in design-verification.md.
- Diary: ten theme/width journeys at 320, 390, 768, 1280 and 1440 px, covering portions, persistence, edits, favorites, keyboard tabs, dismissal, undo, recipes and invalid/idempotent imports. Evidence: diary/checks.json.
- Foods: ten theme/width journeys covering actual Canadian labels, U.S. barcode lookup, market separation, reference portions, comparison downloads and prohibited unsupported mL-to-g conversion. Evidence: products/checks.json.
- Upgrade: test-upgrade.cjs serves prior Git revision 93e873b20f6332ce03beaaa79a467f4259b9020b and current files on one real origin. Immutable filenames bypass stale caches, update checks avoid browser throttling, matching assets are precached, private entries survive and styled offline use passes. No forced reload discards input.

Initial failures were investigated: missing active files in the export, table/preload assertions, the old-worker offline gap, duplicate build-output modules/preloads, inappropriate inherited hreflang and accumulating meal-data whitespace. Transient Windows file-write failures were rerun/resumed with validation. Failed attempts are not represented as passing checks.

performance-lab.json is an actual same-desktop before/after comparison of five page types: cold browser contexts, warm unthrottled loopback files, reduced motion, three samples. Homepage decoded resources decreased from about 387 KB to 239 KB; median local load was about 150 ms before and 102 ms after in that run. Canada's richer homepage loads more than its old table-first page. These are limited lab observations, not field Core Web Vitals, Lighthouse scores or guarantees.

coverage.csv distinguishes manual representative viewing from automated checks by route. Root additionally read the upgraded light390 diary, dark1440 Canadian brand results and a rendered downloaded comparison card. Screens are actual renders, not mockups.

## Deployment and precise limitations

The existing approved GitHub workflow is used through an isolated checkout. Production evidence is recorded in deployment-verification.json, verified-live-links.csv and production/checks.json. Only real verified production URLs are described as live. Docs/tools/server/source downloads must return 404 publicly.

Remaining:

- Broad Canadian supermarket/Costco labels beyond four reviewed products. President's Choice, No Name and Canadian Great Value were not populated using U.S. values.
- McDonald's Canada source extraction returned 403; a KFC source failed. Confirmed local presence does not enable their Canadian macro finder. Unsupported chains show official local links and unavailable coverage.
- Mary Brown's flagged large servings and Pizza Nova's signature-pizza denominator; exact source issues remain in restaurant-import-review.json.
- Reviewed translations, additional qualified markets, native app distribution, cloud sync/accounts, photo/voice logging and production AI.
- Authorized analytics/Search Console, real-device testing, comprehensive screen-reader review and field performance. Concrete keyboard, focus, reduced-motion and responsive checks are not WCAG certification.
- No ads account, paid provider, credentials, DNS, CozyTonight, unrelated infrastructure, outreach or external promotion was changed.

This expands supported utility without claiming every world menu, guaranteed search traffic, AdSense approval or income.
