# GetMacros botanical rebuild — local delivery

Implemented in the existing repository on September 23, 2026. **Not committed, pushed or deployed.** No DNS, credentials, purchases or production settings were changed. The local Pages configuration excludes development folders when the next authorized Jekyll publication occurs.

## What changed

- Replaced the presentation system with fresh white/pale-green surfaces, leaf-green actions, restrained pollen-yellow details, Fraunces headings and Inter body text. Both fonts are local, with their existing license notices. A separate green night palette covers the retained dark theme.
- Rebuilt the homepage around a working meal-discovery form. Actual tracked orders, 83-order/15-chain counts, clear U.S. scope and direct restaurant links support that task. The photograph is labeled food inspiration, not an exact restaurant order.
- Added an original sprout identity, matching favicon/app icons and share artwork. Replaced active mixed SVG sprites with a consistent line system. Botanical details are decorative and do not intercept input.
- Applied distinct compositions to calculators, restaurant references, reading pages, editorial indexes, search, publisher/legal pages and the 404. Rebuilt navigation, mobile menus, forms, tables, disclosures, results and footer presentation.
- Added supported fiber/sodium limits to the finder, readable active preferences, shareable numeric filters, editable no-match states and a clipboard-denied sharing fallback. Unknown values remain unknown; filters do not treat them as zero. Comparison retains the order/serving context.
- Reworked calculator result hierarchy, units, input spacing and food-label comparison. Removed nutrition count-up animations: calculated values appear immediately. Formulas and source nutrition records were preserved.
- Removed 34 unused historical stylesheets after active-reference checks. All 73 public HTML documents load one replacement stylesheet. No active inline stylesheet or old icon sprite remains. Historical development sources and application/data scripts were preserved.
- Kept interactions quiet and immediate, with reduced-motion support and no scroll-reveal hiding. The back-to-top control sits in the footer instead of obscuring mobile content.

## Repository and route scope

This remains a static HTML/CSS/vanilla-JavaScript site with Python publication tooling; no framework migration or added runtime dependency. `tools/build_site.sh` is the supported build. `rebuild_publication.py` owns common structure and generated home/editorial sections; reviewed inner-page HTML remains source content. `botanical_presentation.py` reconciles page families. `stamp_assets.py` versions active assets. Calculator logic is in `js/calculators.js`, `macro-math.js` and focused tool scripts; restaurant records/provenance remain in their existing data files.

Inventory reconciled root HTML, the sitemap, internal links and tracked HTML files:

- **73 public documents / 74 addresses** including `/` and `/index.html`.
- 72 sitemap/indexable documents, 71 searchable resources; 404 stays non-indexable.
- All 15 restaurant guides are retained. Meal detail is an expanded result state, not a separate detail route. Editorial categories are index sections, not invented routes.
- Three tracked development previews (`design/Main.dc.html`, `Contrast.dc.html`, `Soft.dc.html`) are explicitly recorded as excluded development artifacts. `_config.yml` excludes `design`, `docs` and `tools` from Pages. Production behavior of that exclusion has not been verified because deployment is not authorized.

See `coverage.csv` for every route and the distinction between screenshot review and automated rendering. Every public address received automated checks. Representative page families and unusual layouts received visual inspection; this is **not a claim that every individual article was manually inspected in every theme and width**. No public route is knowingly left on the former design.

## Copy, content and SEO

See `copy-review.md`, `copy-corpus.json` and `duplicate-copy.json`. Authored copy was extracted and reviewed; weak generic restaurant copy, exaggerated wording, misleading empty/error copy and obsolete operational descriptions were corrected. Necessary source, serving, safety and missing-data disclosures remain. Existing bylines stay GetMacros; no qualifications or expert review were invented.

The duplicate report's 63 exact blocks and four near matches were reviewed rather than blindly deleted. They are retained navigation labels, source names, disclosures, dates and consistent order descriptions, or distinct Chipotle builds. No new mass-produced article collection was added.

Actual live research is recorded in `seo-research.md`, with query, date, sources, limitations and implemented responses. It includes current Google Search Central guidance and qualitative searches about healthy/high-protein fast food, numeric meal limits, official chain nutrition, macro calculators and protein cost. `query-to-page.csv` maps each public address to intent, supporting questions, distinct utility and next action. No search volumes, difficulty scores or traffic forecasts were invented; no current authenticated Search Console data was available.

Implementation emphasizes numerical filtering, complete orders, portion definitions, helpful comparisons, explicit sources and contextual next actions. Existing useful titles and descriptions were preserved, weak presentation copy was rewritten, and working internal navigation remains crawlable. Existing URLs, canonical decisions, verification files and legitimate integrations were retained. Filter combinations canonicalize to the finder rather than becoming separate indexable pages. No fabricated ratings, recipes or expert structured data was added. The serving-size article's new arithmetic example receives a substantive update date; restaurant/source dates were not automatically refreshed for the redesign.

## Verification performed

The build commands below passed using the bundled Python runtime (`python -X utf8` on Windows). There is no TypeScript or configured ESLint build in this static project.

| Command | Result / scope |
|---|---|
| `python tools/rebuild_publication.py` + `python tools/stamp_assets.py` | 73 documents rebuilt and active assets versioned; subsequent rebuild checked for idempotence |
| `python tools/validate_site.py` | 73 documents, 72 indexable/sitemap URLs, 71 searchable resources |
| `python tools/test_publication.py` | One active stylesheet, unique IDs, page headings, theme controls, verification and provenance order |
| `python tools/test_search_visibility.py` | 3,876 internal links/anchors and meal-source labels |
| `node tools/test_macro_math.js` | Conversions, BMR, TDEE, goal adjustments and macro energy balance |
| `node tools/test-publication-flows.cjs` | Chromium/WebKit, both themes, 320/768/1440: navigation, unit changes, invalid input, recipe/label tools, quiz, comparison, saving, sources and theme |
| `node tools/test-focused-calculators.cjs` | Four focused tools; valid/error/reset/unit/missing-value cases in both engines/themes at 320/390/1440 |
| `node tools/test-botanical-finder.cjs` | 20 engine/theme/width combinations: limits, missing-data exclusion, invalid URL state, reload, focus retention, reset and denied-clipboard fallback |
| `node tools/test-contact-actions.cjs` | Topic/draft URLs and copy fallback; no email was sent |
| `node tools/test-meal-ideas.cjs` | Filters, counts, details, responsive layout and no-JavaScript content |
| `node tools/test-editorial-discovery.cjs` | Home-to-finder numeric choices, empty/reset states and source identity across intermediate widths |
| `node tools/test-publication-accessibility.cjs` | Core rendered contrast, skip link, keyboard menus/Escape, search and preference reset |
| `python tools/test-botanical-palette.py` | 32 text/action/control-border/error/focus color pairs meet their 4.5:1 or 3:1 target |
| `node tools/test-botanical-resilience.cjs` | 22 representative page/theme text-size checks at 200%; no-JS navigation, missing-image resilience and theme storage |
| `node tools/test-botanical-routes.cjs` | **740 checks**: 74 addresses × 320/390/768/1024/1440 × both themes; zero detected overflow, clipped headers, missing main headings, unlabeled inputs, broken loaded images or runtime errors |
| `node tools/capture-botanical-states.cjs` | Home, open navigation, calculated results and no-match screenshots; footer shortcut focus/scroll and immediate numeric output |

Historical test scripts for retired multi-stylesheet generators are not the supported publication pipeline. The active validator was updated to check scroll stability against `publication.css` rather than deleted, unused CSS. Tests were not suppressed to hide functional failures.

Visual QA found and fixed actual issues: constrained article headers, dense comparison results, inline calculator totals, insufficient input-border contrast, meal-idea images overlapping text, concatenated restaurant counts, and narrow reference tables. Final screenshots are under `screenshots/`; `visual-review.json` names the inspected representatives. `baseline/` preserves the available earlier captures. Merely capturing a screenshot is not counted as manual review.

## Performance

`performance-before.json` measures the previous committed source (`6a7bc2341d401ea21467410bfe7f934e67db356d`) from a temporary `git archive`. `performance-after.json` measures the new local source. Both use Edge, 390×844, cold cache, 100 ms latency, 1.6 Mbps download, 4× CPU slowdown and three runs per page. External requests are blocked. `performance-summary.json` contains the medians.

The new mobile homepage avoids downloading its hidden secondary photograph. It improved LCP substantially in this lab. The calculator and finder carry the additional display font and changed presentation; their LCP is slightly slower than the baseline. All nine after-runs had zero measured CLS and zero measured long-task blocking in the observation window. These are local load measurements, **not field Core Web Vitals, INP, Lighthouse certification or an AdSense speed requirement**. Production CDN, consent and advertising costs are not included.

## Remaining limits and release checks

- No production push/deployment occurred. Public `getmacros.net` may still show the previous version. Production HTTP status/redirect behavior, CDN caching, development-folder exclusions and domain settings need a post-deployment check.
- Representative visual review plus all-route automated coverage is recorded honestly; a manual review of every individual article at every size was not performed. Real-device iOS/Android and assistive-technology testing remain outside the completed browser checks. This is not a claim of full WCAG conformance.
- This pass did not re-verify every restaurant nutrient value against today's menus or medically review every source. Existing uncertainty and source dates remain visible. No unknown values were filled with estimates.
- Existing ad serving was already paused before this task and remains paused. Publisher ownership/ads.txt are preserved. Consent/CMP account configuration must be verified before advertising is re-enabled. No AdSense approval guarantee is made.
- Photo and font provenance are documented in `images/README.md`; no paid assets were purchased. Historic unreferenced illustrations are preserved without a new blanket licensing claim.
- Clipboard fallback was exercised; native device share sheets, installed mail clients and actual email delivery require device/account checks. No test sent a message.

The implementation and local checks are ready for review. Deployment is a separate authorized step.
