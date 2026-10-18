# GetMacros source-backed catalogue release — October 17, 2026

Deployment: LIVE and verified. Revision `059dc787961348c9d1d93c09446ee5f7eb5fa732`. Both hosted Site quality runs and GitHub Pages deployment passed. Ninety-seven actual production pages/assets/country shards match the release source; all 405 live HTML routes passed HTTP/title/canonical checks.

## Delivered data

- 558,856 added branded source profiles; 692,173 installed.
- USDA: 446,810 manufacturer-supplied branded source profiles; Open Food Facts: 245,359 market/source profiles from 241,432 source products; four separately sourced Canadian retailer records.
- 1,833 added restaurant records; 17 existing New Zealand Subway source refreshes; 3,582 installed records.
- 16 new source-backed comparison guides. The existing international coverage analysis was substantially updated.

A source profile is not a promise of a unique current shelf product. Historical source versions, national formulations and portions retain separate identities. Imported labels are not independently tested or automatically verified.

## Published market coverage

| Country | Tracked restaurant records | Restaurant brands | Branded source profiles |
| --- | ---: | ---: | ---: |
| United States | 894 | 26 | 518,472 |
| Canada | 647 | 13 | 46,954 |
| Mexico | 100 | 1 | 8,057 |
| United Kingdom | 456 | 3 | 67,041 |
| Ireland | 194 | 2 | 35,223 |
| Australia | 249 | 1 | 9,159 |
| New Zealand | 160 | 1 | 3,459 |
| Japan | 393 | 2 | 3,808 |
| France | 190 | 1 | 0 |
| India | 82 | 1 | 0 |
| Singapore | 57 | 1 | 0 |
| South Africa | 160 | 1 | 0 |

France, India, Singapore and South Africa are new restaurant markets. Their homepages, country selector and finders use the same shared architecture as the existing eight markets. India is limited to McDonald’s North & East India, operated by Connaught Plaza; other Indian franchise regions are not interchangeable.

## Product and engineering

The approved food-character design and private Breakfast/Lunch/Dinner/Snacks diary remain intact. New real records connect to existing search, portion review, favourites, logging and comparison. Burger King Canadian and U.S. standard servings use separate country datasets; the country comparison explicitly labels both countries and cites local ingredient statements.

Restaurant source records are now fetched as one small country partition, instead of a roughly 9 MB all-country registry. Grocery indexes remain partitioned by provider, market, token, barcode and record shard. Compressed source data is versioned and cached; no giant catalogue is embedded in application JavaScript. Source failure leaves other providers usable. Japanese voiced-kana brand queries are normalized consistently.

The price/protein tool now supports INR, SGD and ZAR for the new markets. It uses explicit user prices without invented prices, exchange rates or inventory. Source publication dates remain separate from retrieval dates, and missing nutrients stay unknown.

Principal changed components: `js/branded-foods.js`, `js/food-library.js`, `js/food-core.js`, `js/markets.js`, `js/market-definitions.js`, `js/order-share.js`, `sw.js`, market meal datasets, compressed restaurant/grocery source partitions, shared generated country pages, source provenance helpers and the late release integrator `tools/build_global_coverage_release.py`.

## Provenance and licensing

USDA April 2026 branded bulk data is the latest official bulk edition checked on October 17. It remains separately attributed CC0 data. The Open Food Facts October 13 snapshot retains ODbL/DbCL attribution, separate source/normalized exports and its normalizer. No product photography was copied. Canadian Nutrient File and USDA reference foods remain separately sourced. No MyFitnessPal database was scraped.

Saved official restaurant source responses/PDFs, exact hashes, source editions where available, units and arithmetic tests are retained under `restaurants/`. Direct source sodium takes priority over a separately rounded salt value; exact source zero is preserved; bounded/unknown values are not zero-filled.

## Search and publication

Current Google Search Central helpful-content, multi-regional, localized-version and faceted-navigation guidance was inspected. Actual qualitative queries and observations are recorded in `seo-research.json`; keyword demand metrics were not invented. Country guides and comparisons have crawlable tables, official sources, unique metadata, relevant internal links and canonical routes. Reciprocal regional annotations are limited to genuine country counterparts. Search/filter/barcode states do not create indexable page factories.

The full rebuilt static site currently has 405 HTML routes, 402 sitemap/indexable URLs and 30,861 checked internal links/anchors. The same heading on shared country homepages is intentional. The sitemap is publication metadata, not evidence of Google indexing. No Search Console or analytics access was available for measured search clicks, rankings, acquisition or the reported visitor increase.

## Actual verification

The complete local build, source tests and browser evidence are in `followup-build.log`, `ci-command-results.json`, the exact publishing-checkout logs in `publisher-ci/results.json`, `browser-results.json`, and `restaurants/newmarkets/browser-results.json`. Both fresh hosted CI runs and final production source-hash verification passed. All 405 live HTML routes have passed HTTP, title and canonical checks; 402 bodies match local source exactly. Contact, corrections and terms are modified by Cloudflare email protection. Browser checks cover new grocery search, serving review, Breakfast persistence after reload, separate Canadian/U.S. Burger King Lunch logs, country table labels, country selection and representative pages at 320, 390, 768, 1280 and 1440 CSS pixels. Both theme treatments and keyboard country-menu behaviour were exercised in the new-market browser suite. No full WCAG compliance or field-performance claim is made.

Screenshots: `screenshots/` and `restaurants/newmarkets/screenshots/`. The route inventory distinguishes script checks from actual browser renders and selected visual screenshot review; individual pages without visual review are not labelled visually inspected.

## Exact remaining gaps

- This is not every grocery item, warehouse inventory or restaurant menu in the world. No authoritative exhaustive global catalogue was available. Some source products are historical, not currently stocked.
- Official Canadian McDonald’s nutrition panels returned HTTP 403 here. No U.S. substitute or old unlinked PDF was published as current Canadian data.
- Mexico: current McDonald’s numeric panels were inaccessible; the inspected Burger King feed includes test content, unconfirmed local membership and contradictory serving/macronutrient values. All 78 complete CMS objects remain withheld. See `restaurants/mexico-supplement/source-quality.md` and its seven tests. The 100 previously accepted Subway Mexico records were preserved.
- The four newly supported restaurant markets have no published native branded grocery partition yet; their local menus and common reference foods work.
- Open Food Facts records with ambiguous gram/millilitre bases or contradictory values remain excluded; imported data is not labelled independently verified.
- USDA source-quality notes retain 1,341 profiles with source sugar/carbohydrate warnings, 1,859 marked discontinued by the source and 10,007 missing/unsupported barcode warnings. These are source profiles, not 692,173 independently checked current products; flags remain available in portion-review source details. See `grocery-quality-notes.json`.
- French product names are preserved, but reviewed French interface/content routes are not claimed.
- No backend/AI service, accounts or cloud synchronization was configured or invented. Diary data remains local and private; unfinished AI/install promotion remains removed.
- Production deployment, Google crawling/indexing, traffic and ad approval are distinct states. No rankings, visits, income or indexing outcome is guaranteed.

## Live evidence

See `published-pages.csv` for exact verified live curated URLs, `market-chain-coverage.csv` for all 53 actual country/restaurant selections, `production-verification.json` for 97 matching release resources and `production-all-routes.json` for all 405 live HTML checks. Production browser reports record 11 main-product journeys/check groups plus 75 new-market checks, with no runtime/HTTP failures.

The initial hosted failures were fixed rather than suppressed: three source-proof fixtures were added to the publication scope, and an optional offline HTML parser import was moved into ingestion-only functions. The affected fifteen tests also pass with Python site packages disabled (`python -S`). No nutrition values were changed to obtain passing tests.
