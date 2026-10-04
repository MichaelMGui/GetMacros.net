# GetMacros — complete playful release, October 4, 2026

Implemented in the existing static repository. The working tree and checked-in generators are the implementation source; deployment status is recorded separately below. No DNS, billing, credentials or ad-provider configuration changed. Existing unrelated working-tree documentation was excluded from the implementation manifest.

## What changed

- One composed food-character homepage: a clear meal task, four real recorded portions, one guided quiz, restaurant discovery, compact tools, selected reading and Play. No stock meal photographs or implied exact-order photography.
- Original 18-ingredient cast, consistent faces and layered SVG art. Gentle visible-only reactions, keyboard/touch greetings, elastic selection and contained button motion. No scroll hijacking, hidden scroll text, continuous bouncing or number count-ups.
- Fresh warm-white/leaf-green day theme and deep green-neutral night theme. Self-hosted licensed Bricolage Grotesque display type with Inter body text. Consistent numeric hierarchy, quiet borders, open reading layouts and coherent icons.
- Finished desktop menus, keyboard dismissal and mobile modal navigation with background inertness and focus return. Theme/system preference and calm motion persist. Search groups are Restaurants, Calculators, Articles, Games and site information.
- Meal finder: quiet desktop sidebar/mobile filter sheet; active preferences, count, sorting, exact listed portions, readable calorie/protein hierarchy, expanded source-linked nutrition, no-match handling, compare/share/print, saved meals and filter-respecting Surprise me.
- One guided quiz plus direct browsing, both using the same engine. No preselected quiz answers; explicit resume, cancel and back behavior. Numeric limits are never silently relaxed. Unsupported values remain unknown rather than zero.
- Calculator hub rebuilt around daily estimates, kitchen portions, labels and planning. Macro calculator groups About you, Activity and Goal, with compact mode available; unchanged tested mathematics and unit conversions. A real editable portion example validates inputs. Valid results replace the waiting state.
- All 25 restaurant guides now have a purposeful header, supported calorie/protein handoff, two actual order previews, expandable comparisons/menus and specific serving/source limitations. Original category marks identify the entries; they are not restaurant logos or an affiliation claim.
- Learn uses three deliberate featured reads, a topic browser, eight reads initially and explicit Show more. Journal is a separate editorial selection, not a second identical article directory. All reading links remain crawlable in HTML.
- Local food shelf for meals, articles and games, accessible removal and storage-failure handling. Daily challenge uses the real seeded game library. Contextual nutrition terms live inside the existing macros guide; no additional thin glossary route.
- Trust, contact, accessibility, privacy, terms, sources, corrections and 404 share the same presentation. Contact facts/legal commitments are preserved. Publisher verification and ads.txt remain; advertising requests stay disabled pending a correctly authorized provider/consent setup.

## Content and data delivery

**117 genuinely new checked articles**, excluding all 73 previous article routes and 33 earlier resource pages. Approximately 32,000 authored words, distinct practical questions, individual worked examples, official sources and relevant next actions. Two overlapping drafts were rejected and replaced. The editorial gate passed 292 arithmetic cases,133 restaurant rows across 46 articles and 5 dataset snapshots.25 primary sources were inspected. No invented expert, rating, clinical endorsement or source review date.

**56 implemented games**, eight families, seven per family. Each has a distinct objective and rules, deterministic seeds, pause, restart, new puzzle, completion and keyboard/touch access.2240 rule solves and 224 actual rendered solves passed. These are compact untimed puzzles and creative activities; the coordination games are turn-based rather than reflex arcade games. Some word/clue banks are intentionally small. No accounts, sound requirements, multiplayer or global leaderboard.

**10 additional U.S. chains and 380 additional recorded orders:**53 Arby’s,47 SONIC,14 QDOBA,27 El Pollo Loco,60 Del Taco,22 Noodles & Company,23 Culver’s,122 Taco John’s,9 In-N-Out and 3 Raising Cane’s.378 use published rows; two are explicit individual-portion sums. A taco or slider stays one named portion; this count is not 380 combo lunches or a claim that 250 complete combination meals were added. Size/add-on/drink/dessert padding and contradictory rows were excluded.

Total dataset:463 orders /25 chains.411 have all six exact values;448 have the four finder values.421 records across 18 chains have at least some source inspection in the October 3–4 release.42 fat values and 15 fiber values remain unknown. A less-than bound stays unknown. Ingredient dietary filters are not allergy safety checks; no prices or geographic equivalence inferred.

Printed editions and retrieval dates remain separate. Culver’s source isJuly 2025. SONIC and Taco John’s exact edition dates are unestablished. In-N-Out official web/PDF text was inspected, but the direct local download returned a challenge. Source URLs, pages/rows and hashes are retained in the curated factual payload. Full copyrighted PDFs, screenshots and extracted layouts stay private; clean builds do not falsely claim to re-inspect unavailable PDFs.

## Coverage and verification

291 public HTML files plus the root alias: **292 routes**, including 404.290 canonical sitemap URLs,289 search resources. Three historical development previews are explicitly excluded from Pages publication. [Coverage inventory](coverage.csv) distinguishes individual scripted checks from representative manual visual review.

- `python tools/run_food_build.py`: build, route/data/metadata gates,291 pages,290 sitemap URLs,14409 internal links/anchors passed;117 editorial gates and 15 expansion/provenance tests passed.
- `node tools/test_macro_math.js`: conversions, energy formula, activity/goal adjustment and macro energy balance passed.
- `node tools/test-companion-engine.cjs`:21 strict filtering/unknown-value/ranking/share-state checks passed.
- `node tools/test-meal-view.cjs`: units, real zero, unknowns, portions, source escaping and factual reasons passed.
- `python tools/test-release-content.py`:33 previous distinct resources,183 source fact entries,142 visible rows,41 earlier audited records and 7 ingredient sums passed.
- `node tools/play_release/test-rules.cjs`:2240 deterministic solves across 56 rules passed. `tools/play_release/test-browser.cjs`:224 rendered solves passed. Agent responsive evidence includes 1140 additional game renders and touch/keyboard/reduced-motion/persistence checks.
- `node tools/test-playful-routes.cjs --fast`: **7008 rendered route/viewport checks** in Edge and WebKit, both themes at 320/390/768/1024/1280/1440. Zero final failures.144 representative resilience states cover doubled root text, open menu/keyboard dismissal, missing images, no-script navigation and first-frame/theme persistence. Later changed glossary routes were explicitly retested; semantic asset-only cache stamps changed afterward.
- `node tools/test-playful-journeys.cjs`:8 configurations passed quiz, resume/back/cancel, strict shareable filters, saved meals, three-meal comparison/share/print, mobile Escape, calculator validation/unit conversion and replacement of the waiting state.
- `node tools/test-playful-features.cjs`:12 configurations passed greetings, mobile focus/inertness, live arithmetic, glossary, topic pagination/hash links, restaurant filter handoff, shelf persistence/removal, search/no-result and strict Surprise behavior.
- `node tools/check-playful-contrast.cjs`:44 semantic text/action/focus/control pairs passed in both themes. This is a token check, not a WCAG certification or a manual screen-reader audit.
- Clean baseline archive plus the explicit implementation manifest rebuilt without private PDFs or untracked historical helpers. All public HTML/CSS/JS matched after text line-ending normalization. Cache stamps now remain stable between Windows and Linux while changing for real asset edits.

No unsupported framework lint/type-check command was invented; the project is static HTML/Python generators/JavaScript. Actual source checks and existing tests were run.

## Actual screenshots and visual review

Baseline: `before/`; final full-page captures: `final/` (42 representative routes, both themes at 390/1440, plus greeting, quiz and open menus). Calculator/compare journey states: `journeys/`.52 editorial sample checks cover 13 tracks in both themes/mobile/desktop; table screenshots show narrow and wide behavior. All 56 game playfields were captured under the separate play-release evidence folder.

Full QA captures remain in the local workspace; selected representative screenshots and machine reports are included in the release documentation. Manual review covered family compositions, mobile contact sheets, desktop homepage/results, dark menus, old/new restaurant guides, calculator result states and representative article tables/game families. Every individual route was rendered programmatically. This does **not** claim a manual full-body review of all 291 pages or every possible screen-reader/browser/state combination.

Fixed issues found through rendering include 200% text overflow, compressed article table columns, restaurant title-spacing, stale old source-count copy, oversized library grids, mobile menu focus and a waiting panel that remained above valid calculator results. Actual screenshots, not mockups, are retained.

## Search and copy work

[SEO research](seo-research.md) records inspected Google helpful-content/Search Essentials/spam/JavaScript/faceted-navigation/page-experience/structured-data guidance and two qualitative live search-intent investigations. [Query-to-page map](query-to-page.csv) records each route’s actual task; individual 117 article intents come from their editorial manifest, not invented keyword volume.

Applied descriptive titles, meaningful headings, current summaries, relevant source/tool links, crawlable static reading/restaurant links and deliberate base canonicals. Established URLs were retained. Seeds/filter combinations are not separate sitemap pages. Structured data describes visible articles without fabricated authors, reviews, recipe classifications or ratings. New substantive publication dates areOctober 4; historical nutrition-source dates remain historical.

The raw whole-site duplication report includes necessary shared serving/source/disclosure language. It was reviewed rather than indiscriminately rewritten. New authored paragraphs/reader intents were separately gated. No connected current Search Console export, rankings, volumes, difficulty or traffic forecasts are claimed.

## Performance

Local Edge 390×844, cold cache,100 ms latency,1.6 Mbps download,4×CPU slowdown; three runs per page. This server transfers assets uncompressed, with no production CDN or field-data claim.

| Page | Baseline median LCP | Release median LCP | Release median CLS |
|---|---:|---:|---:|
| Home |1.860 s|1.808 s|0|
| Macro calculator |1.448 s|1.468 s|0.000801|
| Meal finder |2.112 s|2.552 s|0.000132|

The final samples showed no long-task time above 50 ms. These numbers are lab observations, not a guarantee of real-user smoothness. The finder downloads a 5.6×larger dataset with full serving/source facts, so its cold-load median increased. Provenance interning reduced the bundle by roughly 104 KB; the homepage no longer loads its unnecessary 135 KB source-notes bundle, and static restaurant guides no longer download either data bundle. No artificial delays or scroll-driven paragraph entrances remain.

## Remaining limits

No fabricated completeness: not every recorded order is a full lunch combo; some source editions are old or uncertain, and missing values remain unknown. Games are compact untimed experiences. No current field Core Web Vitals/Search Console access, certified accessibility assessment, clinician review of all historic content, or AdSense approval guarantee. Third-party source accessibility/local availability can change. Saved content remains local and can be removed by browser storage clearing.

All public families use the new active system; no known blocking layout/runtime/test failure remains. Historical inactive authoring assets remain preserved outside active page references. Deployment and post-release HTTP verification are reported separately; local checks alone are not proof of production status.
