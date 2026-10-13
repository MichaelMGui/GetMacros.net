# GetMacros master completion release — October 13, 2026

This audit found that the October 12 production releases had already implemented much of the exact brief. This release preserves that design and completes concrete gaps in international coverage, grocery lookup, source quality, accessibility and publication. It does not claim every restaurant or grocery product in the world is covered.

## Implemented and preserved

One shared homepage architecture remains in use for all eight supported markets: United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan. Actual country servings, destinations and shortcuts change; design, characters, navigation, typography, themes, meal discovery and supporting modules remain shared. The existing four featured cards, restrained accent edges, clearly clickable restaurant shortcuts, larger broccoli, original artwork and seven game presentation families are preserved.

Focused interface corrections include the country selector’s full selected-country accessible name, aligned calorie/protein inputs at 320 px, country-neutral no-result search guidance, hiding an empty search section, and a comparison header and three-column nutrition table that fit narrow screens. The brand navigator shows six useful links per country, with additional brands under a native disclosure rather than repeating long caveats. Existing country links take precedence over saved preferences. Compatible Subway and calorie filters survive Canada-to-U.S. navigation; incomplete U.S. macros lead to an honest missing-data disclosure.

The shared diary retains Breakfast, Lunch, Dinner and Snacks in every country. Its 9,905 common reference choices, 12 browse groups, raw/cooked choices, date controls, reviewed portions, recent foods, favorites, recipes, exact saved orders, repeat-meal review and private export/import remain functional. Installation and unfinished AI/photo/voice promotion remain absent.

Packaged lookup now has actual international branded records, source-specific country postings before bounded candidate selection, scoped manifest loading and graceful per-source failure. A precise U.S. search passes the unchanged 2.5 MB / fewer-than-60-request gate: 2,020,833 bytes and 49 requests. Exact barcode lookup bypasses unrelated ingredient/menu inventories.

Duplicate-looking versions of the same country/package identifier are grouped for review; their nutrient values are never fused. Different named flavors, countries and package sizes remain separate. Source attribution and licensing survive favorites, recent portions, recipes, repeated meals, private backups and downloaded comparison cards. Restaurant micronutrients are exposed only when an available source field has the exact supported unit.

New public resources:

- /grocery-food-coverage.html — a real country/brand navigator generated from available product records, with source quality, licensing and inventory limits.
- /ca/en/restaurants/new-york-fries/ — a distinct Canadian serving guide, size comparisons, exact extras and two explicitly calculated complete orders.

The Canadian finder/directory, six other country directories, world menu index, food-library navigation, source/portion guides and shared search were substantively updated. Established routes, formulas, legal meaning and integrations are preserved.

## Actual data counts

| Source or change | Count | What it means |
|---|---:|---|
| New Open Food Facts market-label profiles | 96,451 | 94,620 source product records; community imports, not independent package verification |
| OFF profiles with all four core macros | 95,180 | Available source calories/protein/carbs/fat, not a quality endorsement |
| OFF profiles with some core fields missing | 1,271 | Unknown fields remain null |
| OFF volume-serving profiles | 10,526 | No invented mL-to-g conversion |
| Source products quarantined | 21 | Conflicting zero-energy/macro values or unresolved label rounding; no corrected calories invented |
| New Canadian New York Fries records | 27 | 25 official named servings, two calculated orders |
| New Canadian finder entries | 19 | Components and sauces excluded; four inherited sauces removed, for a net increase of 15 |
| Restaurant registry after integration | 1,709 | Tracked records, including components; not full live menus |
| Canadian registry / finder | 383 / 281 | Four inherited sauce entries were removed from meal discovery |
| Country–restaurant presence relationships | 74 | 17 additional confirmed relationships; source access and finder support remain separate |
| Total branded label profiles | 133,317 | Existing 36,862 USDA labels and four retailer labels plus the new OFF partition |
| Reference profiles retained | 19,571 | 13,578 USDA references plus 5,993 Canadian Nutrient File references |

New OFF market counts: CA 46,950; US 17,106; GB 24,206; IE 3,975; AU 1,856; MX 1,743; NZ 423; JP 192. These are source-attributed markets, not independently audited national formulations, retail availability or inventory.

The new Canadian serving selection uses the official New York Fries August 20, 2026 edition, retrieved and visually checked October 13. Extra topping servings follow the source’s snack ×1, regular ×2 and large ×3 rules; the base fries/poutine sizes keep their separately reported values.

## Licensing and coverage limits

USDA CC0, Canadian Nutrient File Open Government Licence—Canada, factual retailer curation and Open Food Facts ODbL/DbCL remain separate source partitions. OFF attribution, free normalized/source exports, the normalization algorithm and share-alike notices are published. No product imagery, contributor data or proprietary food-app database was copied. Image rights remain separate; no OFF package photos were imported.

The database is sharded rather than bundled into a giant JavaScript catalogue. The largest new label shard is approximately 225 KB. Search loads a bounded relevant subset; country/brand lists derive from actual records. Source names can be sparse, package versions can be old, and community market tags are not independent local-package audits. Visitors still need to match their current label.

Freshii and Pita Pit bulk imports are withheld because their current terms require permissions or restrict this reuse. Their official local sources remain linked. McDonald’s Canada, KFC, Quesada and Wendy’s have documented source-access/interface or verification gaps; no U.S. macros were substituted. Pizza Nova remains calorie-only; its unresolved made-to-order denominator was not guessed.

No additional restaurant market was launched solely from a flag or locator. No native app, account synchronization or live AI service was provisioned. Private diary data stays in the browser; raw food logs, notes and calculator inputs are not sent to advertising providers.

## Research and SEO

Current Google guidance on helpful content, spam, regional/localized sites, facets and titles was actually inspected. Canadian restaurant and grocery queries, official serving resources and competing source-page types were reviewed. Details and URLs are in seo-research.md, grocery-research.md and restaurant-research.md.

Implemented changes include useful page titles/answers, country-specific servings, source trails, brand links, directory links, a complete canonical sitemap and shared search coverage. Genuine regional home/finder/directory counterparts have reciprocal self-inclusive annotations. General guides and games remain global; no unsupported French translation is declared. Brand/filter parameters use the library’s clean canonical and do not enter the sitemap. Diary/offline/error routes remain intentionally noindex.

Two inherited source notes written as internal editorial instructions now state concise visitor-facing limitations. Their uncertainty and nutrition values were preserved. Shared legitimate disclosures remain; there was no indiscriminate article deletion or mass publication of barcode/keyword pages.

No authorized current Search Console/analytics access exists in this task. The earlier visitor increase, users versus sessions/bots, current CTR, indexing, crawling and traffic effects remain unmeasured. Sitemap publication is not a claim of submission or indexing.

## Verification evidence

The complete supported application build passed. An isolated Git-index check also caught and corrected two reproducibility defects: UTF-8 reads now remain correct under Windows child processes, and the reviewed menu catalogue is synchronized with its public download during the build. The final isolated check results are recorded below. The final public scope is 350 HTML routes, 347 indexable/canonical sitemap pages and 346 searchable resources. The identical headline on the eight shared homepages is an intentional unchanged warning.

Commands include tools/run_food_build.py; tools/validate_site.py; tools/test_asset_stamps.py; tools/master_release/test-branded-search.cjs; tools/master_release/test-branded-integrity.cjs; tools/master_completion/grocery_test_off.py; grocery_integrity_off.py; grocery-search-off.cjs; test_restaurants.py; test_integration.py; test_restaurant_adapter.cjs; test-source-ui.cjs; and existing calculator/filter/food/game quality commands.

The whole-source tests inspect every published profile, null field, token/barcode/country posting and source export. The OFF integrity test recomputes normalized records from the retained licensed source subset. They test source arithmetic and identity, not physical food chemistry.

Actual automated route evidence: route-renders.json records 1,400 renders across every route at 390 and 1280 px in both themes, with zero recorded failures. Individual manual review is limited to the representative/outlier images named in visual-review.md. coverage.csv explicitly distinguishes those from automated-only route checks.

Representative browser evidence is retained under visual-baseline/, visual-final/, visual-journey-baseline/, visual-motion/, visual-zoom/, products/ and upgrade/. The checks exercise menus, preferences, filters, missing macros, valid/invalid calculator inputs, true zero versus missing data, units, private logging, favorites/recent/repeats/backups, country changes, reduced motion and downloaded source cards. Widths: 320, 390, 768, 1280 and 1440 px. Side-by-side homepage images are composites of exact top-level captures; site anti-framing protection was preserved.

The real deployment-upgrade test starts from fe5db6432ca7857180dfa0ecbea1799ad149a764 and preserves private entries and source snapshots, including offline access. No storage schema migration was required.

performance-lab.json contains same-desktop, unthrottled loopback before/after measurements against that actual revision: three samples after warmup on five page types. Resource sizes remain bounded on initial pages; diary bytes increased by roughly 5.4 KB. These are lab observations, not Lighthouse scores, field Core Web Vitals or a traffic forecast.

Source checkpoint: baseline-source.zip, baseline.json and the immutable previous production revision. Root protected Git and inherited unrelated work were preserved. The isolated approved publisher is used for staging/deployment.

## Definition-of-done reconciliation

Parts 1–3: active-source inventory, shared market architecture and full-name accessible country control implemented and tested. Parts 4–5: sourced presence matrix and maintainable local-serving ingestion delivered, with explicit permission/interface gaps. Parts 6–7: one organized private diary, bounded branded lookup and real portion/repeat workflows delivered. Parts 8–10: source-separated grocery pipeline, genuine branded coverage, identity/portion rules and source rights delivered; complete retailer inventory is not claimed.

Parts 11–12: unfinished promotion remains removed; larger original broccoli and purposeful accessible feedback retained. Parts 13–20: coherent compositions, alignment, menus, appearance, featured cards, shortcuts and game families are retained and verified; focused source corrections address actual discovered defects. Parts 21–24: actual research, useful new/updated resources, regional technical SEO and return-use features delivered without traffic or volume claims. Parts 25–27: private data separation and recorded route/browser/data/functional checks delivered, within the stated screen-reader, real-device and field-measurement limits. Part 28: stages reconciled into one application, without fabricated records to fill external coverage gaps.

Remaining exact restrictions: the withheld source/permission cases listed above, current-package verification of community imports, sparse historical product naming, reviewed translations/new unsupported markets, live analytics/Search Console access, native devices/full screen-reader assessment and field performance data. These remain visible limits rather than broad claims that every item in the brief is unrestricted or perfectly complete.

Deployment revision, workflow conclusions, live byte verification and final browser outcomes are appended after the authorized publication checks finish.


Local final refinement evidence: the ten native grocery/diary journeys passed again after the narrow comparison and brand-navigator changes. All 1,400 route renders passed again on the final presentation. The service-worker upgrade/offline check passed again with the current immutable assets. Source imports retain the 21-item quarantine ledger across two subset reruns; 17 importer boundary tests and the full 96,451-profile source recomputation passed.


Final isolated publication check: the complete build and 22 further quality commands passed (23 commands total), with zero public-file differences between the staged source rebuild and the reviewed application. No inherited untracked inputs were used. The staged public tree is 829,158,631 bytes before Pages packaging; the largest individual file is the 29,275,131-byte licensed normalized export. Full results are in clean-source-check.json, clean-source-build.log and artifact-size.json.


Final coverage-counter correction: the 129 additional U.S. Chick-fil-A logging/builder catalogue entries are explicitly excluded from the primary meal-finder count. They remain searchable/loggable, with unchanged nutrition and sources. The actual U.S. finder has 463 rows (11 Chick-fil-A); its broader registry has 592 rows (140 Chick-fil-A). Twelve output integration tests execute the actual eight market data assets and verify total and per-chain presence counters. Actual finder counts: US 463; CA 281; MX 53; GB 327; IE 66; AU 15; NZ 17; JP 206. The original comprehensive passing check is retained as clean-source-full-check.json and clean-source-full-build.log; the final scoped correction receives a full application rebuild plus focused integration, food and idempotency checks, and the full production CI workflow.


The final source-capability correction passed the complete application build plus four focused regression commands, with zero public-file differences (clean-source-check.json). All eight actual finder arrays and their per-chain coverage counters pass the 12-test integration suite. Production licensed gzip exports match their exact binary SHA-256; text distributions have exactly matching UTF-8 contents after Git line-ending normalization.
