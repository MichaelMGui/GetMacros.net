# GetMacros product, content and growth release

Release date: October 3, 2026. The existing Market green identity is preserved. This release improves the working product and source-backed content rather than restarting its art direction.

## Implemented

- One shared filtering/ranking engine powers direct browsing and a four-step guided finder. Back preserves answers; optional questions can be skipped; cancel does not change the current browse state. Calorie, protein, fiber and sodium limits remain strict, including no-match states. Soft priorities affect ranking rather than silently imposing hard limits.
- Results identify the exact tracked order, included portion, U.S. market, calories, protein and other available nutrients. Unknown values remain unavailable. Source access and nutrient-specific inspection dates distinguish published numbers, ingredient sums and older retained fields.
- Compare two or three meals, including serving definitions, six aligned nutrient rows and source links. Shareable state is restricted to supported meal preferences and order identifiers. Saved meals stay in this browser. Comparison print output is supplied; denied clipboard access offers a manual link.
- Menus, wrapped labels, controls, tables, headings and focus states were reconciled in both existing themes. Narrow article headings use the full available width; mobile sorting remains readable at increased text size; wide nutrition tables scroll within their own region. Print controls are excluded from comparison output.
- Sixteen original lightweight SVG food characters provide brief hover, focus or tap feedback. The steak says “Hi!”; dismissal and reduced-motion behavior are tested. Artwork has reserved space, does not hide text, and survives disabled scripts as static artwork.
- The homepage retains immediate meal discovery, factual dataset counts and the existing licensed food photograph, explicitly described as a general illustration rather than a photographed restaurant order. Navigation and the resource library group destinations by task. No manufactured loading delays, scroll hijacking or number count-up was added.

## Routes and content

The release covers **106 root HTML files plus the root homepage alias: 107 public routes**. `release-manifest.csv` records route-specific implementation, source boundaries and verification. There are 105 indexable routes in the sitemap, 104 search entries and a non-indexable 404. Development fixtures, screenshots, reports and launch drafts are excluded from GitHub Pages.

**33 new resources** were implemented: 18 distinct dataset comparisons/references and 15 practical guides with original worked examples. These are separate from the **15 existing restaurant guides** synchronized to central data and **six existing editorial pages** receiving targeted substantive copy or numerical improvements. Other retained pages received shared presentation, navigation and copy auditing; their factual bodies were not all rewritten or medically reverified.

The comparison resources contain **142 visible comparison-table rows**. The database report additionally uses 41 source-inspected input records for aggregate coverage statements; those 41 are not another 41 visible comparison rows. Seven ingredient sums are reproducible in `data-derived-calculations.json`. Examples in the practical guides are explicitly illustrative, with FDA/USDA/NIST sources where appropriate.

Excluded content ideas include a thin wraps ranking, duplicate generic chicken-sandwich/plant-salad lists, a separate dry-rice article, a duplicate basic protein-cost guide and unverified large Chick-fil-A combinations. They did not add distinct supported utility or lacked fresh source evidence. Existing URLs and useful retained content remain intact.

The existing-page duplicate audit scans 73 original tracked routes. Repeated comparison paragraphs were removed from all 15 restaurant guides. Four generic conclusion headings became specific summaries. Necessary portion definitions, units and shared disclosures were retained. Exact and near-copy reports are available in `copy-audit.json`; this automated scan is not a claim of independent editorial or medical review of every sentence.

## Source and asset boundaries

41 of 83 tracked orders across eight chains received source-inspected patches. The remaining 42 records retain their existing inspection dates. Fields not reverified do not acquire a fresh date merely because the design changed.

- Chick-fil-A 12-count grilled nuggets: calories, protein, carbohydrate and fat were checked; fiber and sodium retain September 9 provenance.
- Starbucks: official indexed nutrition text was inspected; the direct page returned an unrendered shell. This distinction remains recorded.
- CAVA: the accessible official April-2025-named document was inspected, but its current live menu linkage and a printed publication date could not be established. Comparisons disclose this limit.
- Chipotle: published high-protein menu values and ingredient-derived fields have separate sources/methods. Ingredient document age and half-rice assumptions are disclosed.
- Panda Express: a full 10-ounce Super Greens side is distinguished from the smaller entree measurement; affected orders and guide comparisons were corrected.

The source wire format shares repeated provenance objects, reducing its payload from 67,207 to 37,555 bytes without removing fields. Python and JavaScript tests confirm the full provenance expands correctly, including partial dates. No whole restaurant PDF or raw third-party dataset is redistributed. Attribution is not a jurisdiction-wide certification of numerical-data reuse rights. No new restaurant logo license or exact-order photograph is claimed. New character and launch artwork is original SVG.

## Search and responsible growth

Current research actually performed is recorded in `seo-research.md` and `source-notes-research.md`: eight requested Google primary guidance pages, 16 qualitative English queries, primary nutrition documents and additional accessibility/performance guidance. Locale was not authenticated or country-personalized; food data is U.S.-specific. Current Search Console/analytics exports were unavailable. Older user screenshots are historical context, not this release's traffic baseline.

Implemented changes include distinct task-based titles, headings and summaries for the new resources; crawlable resource-library links and useful tool handoffs; self-canonicals; truthful publication dates; supported visible Article metadata; updated search previews; corrected existing numerical comparisons; and sitemap inclusion. Arbitrary finder parameter states remain outside the sitemap. No invented reviews, keyword metrics, authority claims or mass restaurant-keyword variants were added.

`query-to-page.csv` maps real page purposes and next actions, distinguishing qualitative research from purpose-based mapping. `growth-next-steps.md` prioritizes fresh query/page evidence and real usability feedback. Two original sourced comparison graphics and accurate posting drafts are in `launch/`; no outreach, posting, purchase or account change was performed.

Provider-free product events expose eight action names as local browser events. They do not send raw quiz values, calculator inputs, query text, identifiers or network analytics. They provide a future measurement boundary, not collected growth data.

## Advertising

The provider-independent placement layer is **disabled**, without an ad provider or configured consent manager. Optional after-content placements are hidden with no blank gap while disabled. Mock tests cover denied/unknown/granted consent, reserved pending space, fill, no-fill, rejection, timeout, stale responses and disable behavior. No provider script or automatic serving ads were enabled. This is infrastructure readiness, not legal consent certification or AdSense approval. No reapplication was submitted.

## Verification actually completed

Static build commands are defined in `tools/build_site.sh`. This is a static HTML/vanilla JavaScript project; there is no application framework build, configured linter or TypeScript check to claim. Changed JavaScript passes Node syntax checks.

| Check | Actual result |
| --- | --- |
| Complete build and regeneration | Passed twice; 143 HTML/CSS/JS outputs identical across consecutive builds |
| `validate_site.py`, `test_publication.py`, `test_search_visibility.py` | 106 HTML, 105 sitemap routes, 104 search entries, 5,350 internal links/anchors; single 65,327-byte owned stylesheet after line-ending normalization |
| `test-content-value.py`, `test-release-content.py` | 15 restaurant comparisons, 33 new resources, source/portion fields, seven ingredient sums and lossless provenance passed |
| `test-release-engine.cjs` | 20/20, including strict limits, missing values, URL round-trip, ranking and actual production metadata expansion |
| `test_macro_math.js` | Formula, unit conversion, goal and energy-balance checks passed |
| `test-release-routes.cjs` | 2,140 route renders and 56 resilience checks passed: Chromium/WebKit, both themes, 320/390/768/1024/1440 CSS pixels |
| `test-release-journeys.cjs` | 8/8 engine/theme/width configurations: guided keyboard flow, back/skip/cancel, strict results, saves, share fallback, comparison and mocked advertising |
| `test-food-characters.cjs` | Eight configurations passed, including dismissal and reduced motion |
| `test-focused-calculators.cjs` | 48 page flows across 12 engine/theme/width configurations: sodium, carbs, timeline and sweat examples/errors/reset/conversions |
| `test-publication-flows.cjs` | 12 configurations: navigation, macro/recipe/label workflows, meals, comparison, source and theme |
| `test-meal-ideas.cjs` | 16 configurations plus no-JS six-meal content, category/ingredient filtering and expanded detail |
| `test-browser-tools.cjs`, `test-market-flows.cjs` | Existing tool, navigation, home and contact journeys passed; no email was sent |
| `test-publication-accessibility.cjs` | Representative contrast, visible keyboard focus, menu dismissal, search/no-match and filter reset passed |
| `test-release-presentation.cjs` | Two launch graphics within canvas; actual three-meal print rendering/PDF passed |

Every route was rendered programmatically. **70 human visual-inspection records**, including four final production views, identify the exact screen region, width and theme viewed in `routes/visual-inspection.json` and `parent-visual-inspection.json`. They cover all page families and unusual layouts; they do not mean every individual page was manually read. Increased root text size, failed images, no-JS navigation, first-frame theme persistence and open menus are included in resilience tests. No full assistive-technology audit, physical-device survey, OS text-zoom certification or independent medical review was performed.

Screenshots: `baseline/` holds before views; `routes/screenshots/` holds individual route views; `journeys/` holds guided quiz and comparison screens; `calculator-flows/` holds result workflows; `presentation/comparison-print.png` and `.pdf` show print output. Selected representative screenshots are committed; the complete larger screenshot matrix remains in the local workspace.

## Performance: lab measurements, not field data

Three cold-cache runs per page used local Edge at 390×844, 100 ms latency, 1.6 Mbps download and fourfold CPU slowdown. The median results were:

| Page | Before / after LCP | Before / after CLS | Before / after long-task excess |
| --- | --- | --- | --- |
| Homepage | 1,544 / 1,804 ms | 0.000417 / 0.000299 | 90 / 23 ms |
| Macro calculator | 1,236 / 1,280 ms | 0 / 0 | 0 / 0 ms |
| Meal finder | 1,776 / 1,840 ms | 0 / 0 | 62 / 45 ms |

The release adds functional payload: homepage transferred bytes increased from 205,552 to 280,739, and finder bytes from 208,754 to 258,212 in this fixture. It is **not universally faster**: homepage median LCP is 260 ms slower while long-task excess and layout shift improved. These representative lab measurements precede small final typography/table/print corrections. They do not measure field INP, production CDN performance or actual-user Core Web Vitals. Raw reports are `performance-before.json` and `performance-after.json`.

## Deployment and remaining limitations

**Published and verified at https://getmacros.net/.** Release commit `b88a9e319c0ac6ee330df1fee288787493b1b33f` was pushed without force to `main` and the configured Pages source `claude/getmacros-nutrition-site-1gfhsm`. Both GitHub quality jobs and the Pages deployment succeeded. A documentation-only follow-up records these final checks; public product assets remain those of the tested release.

Actual production checks passed for all 107 public routes, ten release assets, three negative routes (missing page and excluded development files return 404), and four Edge browser configurations: 390/1440 pixels in light/dark. Production HTML and assets match the release after line-ending normalization. Three email-containing pages undergo the existing Cloudflare email-protection transformation; the verifier decodes its exact generated markup, verifies the original address, and removes only its specific decoder script for origin comparison. The contact address was also verified visibly decoded in the real browser. No Cloudflare, DNS or security setting was changed.

The production journeys exercised home results and artwork, strict finder limits, guided back/cancel, two-meal comparison, new resources, calculator presentation, theme persistence, overflow and runtime errors. No ad requests occurred. Evidence is in `live-verification.json`; production screenshots are in `live/`. Existing laboratory and wider Chromium/WebKit checks remain separately reported. Current production field performance and real-user growth remain unmeasured.

No known local implementation failures remain in the recorded checks. Remaining boundaries are source freshness/access listed above, absent current traffic/field data, an unconfigured ad provider/consent system, incomplete independent medical/legal/assistive-technology review, and no guaranteed search ranking, revenue or advertising approval. Unrelated pre-existing workspace changes were excluded from the release.
