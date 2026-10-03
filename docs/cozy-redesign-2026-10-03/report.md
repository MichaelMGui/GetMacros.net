# GetMacros kitchen companion release — October 3, 2026

## Implemented

The presentation has been rebuilt around a welcoming kitchen companion, rather than adding mascots to the previous design. Fresh and Harvest have independent light and night palettes, licensed Fraunces headings, Inter interface text, a compact header, an organized appearance menu, and a shared spacing/control system. All retained page families inherit the new system. The old `market-system.css` is no longer part of the public bundle.

The homepage now puts meal discovery, search, and a real source-backed order near the top. Original layered SVG artwork depicts a bunny with a bowl and a squirrel with a lunchbox. Character gestures are small and finite; offscreen/background animations pause. Calm motion and the device's reduced-motion preference disable optional movement. A snowman asset is reserved for future seasonal use and is not currently displayed.

The new four-step meal quiz presents one question at a time. Every new session starts blank. An unfinished draft is restored only through an explicit Resume action; Start fresh clears it. Restaurant and nutrient priorities support multiple choices; optional targets can remain blank. No-preference ranking now preserves catalogue order instead of applying an undisclosed protein boost. Hard limits remain strict, including no-match results and missing nutrients.

Meal rows retain included portions, readable nutrition, details and sources, saving, three-order comparison, sharing and print access. The daily macro calculator offers guided and compact views of the same form and formulas. Unit conversion precision was improved to avoid whole-centimetre rounding changing the estimate. Appearance changes preserve filters and saves.

Default finder results and calculator controls are now generated in the initial HTML, using the same data and meal engine. This removes the loading layout jumps measured in the first implementation. No artificial loading delay, new tracking service, ad-serving change or consent change was introduced.

## Reference and assets

Actually inspected: [CozyTonight homepage](https://cozytonight.com), its [tonight quiz](https://cozytonight.com/quiz/tonight), and its Cold appearance. Reference screenshots and observed text are under `reference/`. We borrowed the arched character composition, restrained rules, warm display typography, compact navigation and illustrated quiz rhythm.

The source CozyTonight project and source illustration files were unavailable in this workspace. The new `images/kitchen-companions.svg` is original repo-native artwork, not a claimed source transfer. Existing font licences remain in `fonts/`. Existing food imagery and its provenance were retained; a generic salad is explicitly labelled as inspiration rather than an exact restaurant order. No purchased assets or third-party image hotlinks were added.

## Coverage and verification

106 HTML files plus the root alias: **107 routes**. See [coverage.csv](coverage.csv), which distinguishes scripted rendering from visual review. Every route passed 20 combinations of two browser engines, two themes and five widths: **2,140 checks**, with **56 additional resilience checks**. Widths: 320, 390, 768, 1024 and 1440 CSS pixels. Additional Fresh/Harvest renders cover 21 representative routes in both themes at mobile/desktop widths. Body and secondary-text contrast checks, reduced-motion and touch tests passed (**169 checks**).

Direct viewport review covered the homepage, quiz, results and navigation. Actual screenshot crops were reviewed in contact sheets for all nine tools and representative restaurant, editorial, index, source, legal, contact and error layouts. This is not a claim of manual inspection of every page, every paragraph or every WCAG criterion.

Actual commands/results:

- `python tools/verify-companion-build.py`: two complete builds produced identical public HTML, CSS, search index and sitemap; all included static/data/math gates passed.
- `node tools/test-companion-routes.cjs --fast`: 2,140 route checks and 56 resilience checks; zero failures.
- `node tools/test-companion-journeys.cjs`: eight Edge/WebKit, mobile/desktop, light/dark journeys passed. Blank/resumed quiz, multi-select, optional targets, strict filters, no-match, compare, saving, sharing/print instrumentation, navigation, unit conversion and guided validation exercised.
- `node tools/test-companion-polish.cjs`: 169 appearance/contrast/touch/reduced-motion checks passed.
- `node tools/test-companion-engine.cjs`: 21 filtering, missing-value, URL, provenance and ranking checks passed.
- `node tools/test_macro_math.js`: conversion, BMR, TDEE, goal adjustment and macro energy checks passed.
- Static validation: 105 indexable routes and sitemap entries, 104 searchable resources, unique IDs, preserved verification files, valid source ordering, and 5,484 internal links/anchors passed.
- Content regressions: 15 comparisons, 33 distinct resources, 183 source-fact entries, 142 visible nutrition rows, 41 audited records and seven ingredient sums passed. Data and provenance files remain unchanged by this redesign.

Final screenshots: `final/home-viewport-*.png`, `final/quiz-*.png`, `final/navigation-*.png`, `final/results-viewport-*.png`, representative full-page files in `final/`, and comparison/calculator screenshots in `journeys/`. Before screenshots are in `reference/`. JSON evidence is stored alongside them.

## Performance

Three cold-cache runs per page before and after: local Edge, 390×844, 100 ms latency, 1.6 Mbps download and 4× CPU slowdown, uncompressed local server. Median largest-contentful-paint values:

| Page | Before | Final | Final layout shift |
| --- | ---: | ---: | ---: |
| Homepage | 1.804 s | 2.024 s | 0 in all three runs |
| Macro calculator | 1.292 s | 1.348 s | 0 in all three runs |
| Meal finder | 1.844 s | 2.076 s | 0 in all three runs |

The additional font and companion assets have a small loading cost. The first implementation's calculator/finder layout shifts were detected and corrected, rather than treating a build pass as sufficient. These are lab measurements, not real-user field data or an AdSense guarantee. See `performance-before.json`, `performance-after-fixed.json` and `asset-sizes.json`.

## Copy, SEO and limits

Task wording, quiz help, selected states and motion/privacy explanations were revised. Existing useful article copy, source records, U.S. scope, truthful review dates, accurate formulas and legal meaning were retained. Duplicate-copy reporting was rerun; shared labels, repeated source disclosures and similar ingredient lists are intentional, not indiscriminately rewritten. Existing URLs, metadata, canonicals, structured data, internal links, search resources and verification remain intact. No new live keyword research or traffic forecasts are claimed for this design release.

Remaining limits: no access to CozyTonight source assets; unknown restaurant values remain unverified; data review dates have not been advanced because the design changed; no exhaustive manual screen-reader audit, physical-device matrix or field-performance measurement. AdSense approval remains Google's decision.

## Published verification

Implementation commit: `7c5e890ca73dc9c6c392a46b886ba9cd2b72345d`. Published through the existing Pages branch, with both GitHub quality runs and the Pages deployment successful. The actual production check passed **107 exact route-body comparisons**, **11 text asset comparisons**, a real custom **404 response**, and **eight Fresh/Harvest × light/dark × mobile/desktop quiz/shared-filter journeys**. Only line endings and the existing Cloudflare email protection were normalized; the decoded contact address was verified unchanged.

See `deployment-checks.json`, `live-verification.json` and `final/live-home-*.png` / `final/live-quiz-*.png`. These are actual production checks and screenshots, separate from the local browser fixture and local lab measurements.
