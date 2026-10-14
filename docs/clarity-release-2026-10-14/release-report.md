# GetMacros clarity, character, content and growth release

Release date: October 14, 2026. Publication status is recorded separately in `deployment-verification.json`; a build or preview is not proof of production publication.

## Implemented product and presentation

- Every one of the 363 discovered public HTML routes receives the reconciled navigation: Find a meal, Restaurants, Compare, Log food, Calculators and Learn. Immediate menus expose the food library, saved orders, sources, Play and Read & Watch. `feature-discovery.csv` maps the entry points.
- Eight country homepages use the existing shared architecture with their own source records. Country controls retain flags and full names. English is a truthful current-language label; the unsupported language dropdown is removed. No new country, translation or IP redirect is claimed.
- Featured homepage cards have separate, aligned View order and Compare portion actions, a restrained upper edge accent, readable numbers and source disclosures. Native subgrid now reserves six rows for the six content groups. Missing U.S. comparison links were repaired by reconciling stable registry and homepage identities. Restaurant shortcuts retain the existing clickable treatment.
- `/compare-foods.html` is a real destination using the existing portion arithmetic. Two reviewed public source records retain market, edition, quantity and unit. Users can edit or remove a portion, compare listed portions or a supported 100 g basis, log the exact amount, share a public-only link and download an attributed SVG comparison card. Unknown nutrients remain unknown; millilitres are not treated as grams. Private recipes and notes are excluded from public comparison links.
- Comparison choices and basis persist locally. Deep links resolve cold source records without nonexistent shard requests. Controls cannot mutate an unfinished shared-link load; stale edits cannot overwrite a changed slot. Invalid portions disable the Log link. Source versions and licences remain available in a readable disclosure. The comparison indicator is independently centered between balanced columns.
- The diary opens around its date and Add food action, followed by Breakfast, Lunch, Dinner and Snacks. Zero totals are hidden until foods are actually logged, and repetitive empty-meal paragraphs are removed. Existing favorites, recent foods, recipes, repeat meals, historical snapshots, editing, undo and backup controls are preserved. The same food collection remains available in every country. Unsupported installation and AI promotion remain absent.
- Calculators open into their input workspace rather than an empty decorative result panel. Their three input groups, units, validation, formulas and result explanations remain working. Supporting tasks use compact purpose-based lists. The meal quiz labels its actual country and retains choices on Back; it starts without preselected answers.
- The original food cast is preserved. All 18 declared gestures have matching SVG layers; Steak's greeting arm is visible above its body, and the broccoli companion has keyboard/touch feedback. Automatic repeated homepage greeting is removed. Purposeful motion remains, with Calm and operating-system reduced-motion behavior.
- Existing 56 games retain their scoring/rules and seven family identities. Headers and instructions are quieter; restart, pause, completion focus and announcements are repaired. No new game count is used as a success claim.
- Read & Watch has clear titles, creator identity, edition/source information, accurate availability and task links. Its graphics are original native SVG rather than copied posters. The PBS archive is labelled as unavailable for online streaming. No video is downloaded or republished.

## Data and countries

Published markets remain United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan. Coverage is a tracked selection, not a complete audited menu or current local inventory.

| Measure | Actual result |
|---|---:|
| New Canadian Triple O's records | 40 |
| Official named servings within that addition | 37 |
| Transparently calculated complete orders | 3 |
| New finder-eligible entries | 37 |
| New restaurant-country relationship | 1 |
| Current central restaurant records | 1,749 |
| Canadian records / finder entries | 423 / 318 |
| Corrected Mexican Subway categories | 20 |
| Clearer Mexican Subway names | 39 |
| New grocery imports in this release | 0 |

Triple O's figures were read from the official currently linked June 2025 edition. Retrieval/review on October 14 does not make it a 2026 menu. Sauce components remain distinct. Contradictory large-shake, Impossible, Cajun Fries and Frappuccino source values were withheld. `data-research.md`, `data-verification.json` and `data-records.csv` contain the source trail and limitations.

All 93 Mexican Subway record IDs and numerical values are retained. Eleven individual meat components are no longer represented as complete sandwiches; six desserts and three sides receive their actual categories. The parser preserves source section headings across page breaks. Historical private diary snapshots are not silently rewritten. A person who previously logged a mislabelled Mexican component should review that historical entry deliberately; see `data-mexico-corrections.md`.

The existing grocery/reference catalogue is preserved: 96,451 Open Food Facts market profiles from 94,620 source products, 36,862 USDA branded records, four reviewed Canadian retailer labels, 5,993 Canadian Nutrient File references and 13,578 USDA references. That is 152,888 profiles, not 152,888 unique foods or independently current verified packages. Imported community/manufacturer data is not retailer inventory. ODbL/DbCL source partitions, attribution, normalization and licensed archives remain separate and intact. No MyFitnessPal data was copied.

## Copy, content and SEO

Eleven distinct new articles and ten substantive additions to established articles cover named restaurant decisions, country differences, drinks, grocery labels, serving calculations, recipe logging and source interpretation. The eleven new pages fit the existing Learn categories. They contain visible answers, named portions, source-backed comparison tables, appropriate next actions and readable limitations. `editorial-manifest.json` and `editorial-pages.csv` preserve intent/source details; `live-links.csv` records actual publication verification separately.

Interface repetition removed includes the duplicate diary introduction and empty messages, empty calculator waiting panel, repeated homepage notebook/play slogans, unsupported language-menu explanation and raw comparison status enums. Necessary units, licensing text, source dates and substantive disclosures remain. The duplicate-copy report distinguishes legitimate shared notes from weak repetition; no indiscriminate article deletion or URL consolidation was performed.

Current Google Search Central Starter Guide, helpful-content guidance, spam policies, JavaScript SEO and multi-regional guidance were read. Focused query research used actual search results and official sources. Two official office-hours transcripts were read; one SEO Made Easy video description was reviewed only. Videos were not claimed as watched. `editorial-research.md` records sources, October 14 research dates, intent overlap and concrete implementation.

New articles are static HTML with source tables and real href links, self-canonicals and truthful Article/BreadcrumbList data. New comparison and Triple O's routes have distinct purposes. New/updated pages have descriptive titles, summaries and contextual tool links. All eight genuinely equivalent finder pages retain reciprocal regional annotations. No invented French version, filter-indexing explosion, fake rating, recipe markup or traffic forecast was added. Sitemap contains 360 eligible canonical URLs; search contains 359 resources. Shared homepage H1 wording is an intentional eight-country architecture warning, not a concealed validation error.

## Verification and screenshots

The exact commands and exit codes for the staged isolated build are recorded in `clean-source-check.json` and `clean-source-build.log`. The root build log is `full-build.log`. Tests cover calculator arithmetic/units, source and market separation, null handling, search, branded grouping and barcodes, storage/backup integrity, restaurant parsing, source attribution, asset stamps, idempotence and editorial arithmetic.

Actual browser evidence includes:

- `route-renders.json`: 1,452 automated render checks across all 363 public routes, 390/1280 px and both themes; no status, heading, overflow, theme, stylesheet or runtime failures. This is not individual manual inspection of every page.
- `visual-final/checks.json`: 212 representative page/menu states, five widths (320, 390, 768, 1280, 1440), both themes, plus ten country/navigation/search/diary/calculator journeys. Side-by-side U.S./Canada screenshots use exact rendered pixels.
- `workflows/checks.json`: ten complete comparison, portion editing, linked logging, edit/remove/undo and navigation journeys across five widths and both themes.
- `comparison-regressions.log`: eleven independent reviewer gates, including delayed source loading, invalid quantities, stale edits, preserved comparison basis and restaurant search entry.
- `geometry/checks.json`: four country homepages and the comparison marker at five widths in both themes; actions do not overlap and the marker is visibly centered.
- `journey-extras/checks.json`: twenty journeys covering all eight country quizzes/saved orders, worked-example article → calculator → finder, and diary favorite/repeat/export/import/corrupt-backup rejection.
- `editorial-screenshots/checks.json`: 210 actual renders of all 21 changed article routes. `editorial-link-journeys.json`: six fresh article-to-comparison journeys.
- `character-media-final/checks.json`: 90 media/character renders and interaction checks. `character-game-final/checks.json`: 224 complete keyboard game journeys plus four untimed memory-focus checks. Existing deterministic game rules: 2,240 checks.
- `visual-motion/checks.json`: sampled semantic text/action/feedback/control/focus contrasts, companion hover and Calm/OS reduced motion. `visual-zoom/checks.json`: 200% page-zoom-equivalent reflow, explicitly emulated rather than native browser/text-only certification.

Manually opened final captures include U.S./Canada desktop parity, mobile diary, desktop dark calculator, desktop comparison and a close-up of its centered marker, mobile navigation, calculator result, finder, Read & Watch and Triple O's guide. The editorial/character reports identify their additional actual manual reviews. Final review found and fixed featured-action overlap that automated route checks had not detected.

`performance-lab.json` records three samples after warmup for five representative routes on the same Edge desktop, cold contexts, reduced motion and unthrottled loopback. It measures navigation/paint timing, bytes and brief observed layout shifts. It is not Lighthouse, field Core Web Vitals or proof of real-user performance. Initial catalogue shards remain demand-loaded.

## Measurement, privacy and remaining limits

An authorized read-only Cloudflare view was inspected. The apparent visitor increase cannot be attributed to human Google traffic: release-verification and Headless Edge agents represented approximately 76% of observed requests. Requests, visits and the overview's Unique Visitors metric are different measures. The aggregate baseline is saved privately in `analytics-baseline.md` and is excluded from publication. No account identifiers or individual visitor data are included in the public report.

Search Console queries, clicks, CTR, landing-page trends, indexed status and field performance are unavailable through the current authorized access. The release does not claim sitemap submission, indexing or search growth. Existing provider-free product events remain local; no new analytics SDK or advertising provider was installed. Diary entries, body inputs and private notes are not added to events or comparison links. Ads remain disabled. Privacy text now describes local comparison storage and the portions included in public links.

Remaining exact limits: Pizza Nova still has calories-only coverage and is excluded from macro-complete finder results; several Canadian chains remain operations-only or source/rights blocked; official source contradictions remain withheld; some Canadian Subway source-edition confirmation and coffee customizations remain unsupported; grocery coverage is not complete inventory. There is no configured AI backend, photo/voice logging, native app, account or cross-device sync, and these are not promoted as working. No reviewed French interface was manufactured. No clinical, legal/licensing opinion, Safari/physical-device or full screen-reader certification is claimed. Existing photos/artwork were not relabelled as exact restaurant meals. DNS, billing and credentials were not changed.

The root checkout and inherited unrelated work were preserved. Publication uses the existing writable isolated Git publisher and authorized non-force workflow. Production revision, successful workflows, exact response hashes and final real-site browser journeys are recorded after deployment, rather than inferred from this report.
