# Master release visual audit — 13 October 2026

The current food-character identity and shared homepage layout were inspected before making changes. This pass preserves the existing design; it does not count an arbitrary reskin as completion of the master brief.

## Actual baseline

The local public fixture served the active repository, including its real immutable assets, source data and calculator scripts. The initial Python fixture on port 4197 stalled during the finder request; the established Node public fixture resolved the server issue. That first failed harness run is not evidence of a production finder failure.

The successful fresh baseline is recorded in visual-baseline/checks.json:

- 140 actual route/theme/width renders: 14 routes at 320, 390, 768, 1280 and 1440 CSS pixels in both themes.
- US, Canada, Mexico and Australia homepage main-section structures were equal; featured records and displayed country names matched their market.
- All sampled renders had one main heading, no horizontal page overflow and no recorded JavaScript page errors.
- Ten open-country, appearance and navigation journeys passed at those widths and themes.

The separate visual-journey-baseline/checks.json records ten real product journeys, with screenshots of the mobile filter panel, food picker, selected food review, logged diary, preferences and calculator result. The food selection used the existing USDA oatmeal profile, not a mock nutrition object. Invalid age input stayed in the appropriate calculator group; valid inputs traversed all three groups and produced the real result.

These are representative renders and journeys, not a claim that every individual public article or every native device was manually inspected.

## Manual image review

The following actual screenshots were opened as images and reviewed. Long full-page captures can be scaled by the image viewer; review of those captures concerned composition rather than a line-by-line transcription of every table row.

| Surface | Images opened | Findings |
| --- | --- | --- |
| Shared homepages | US-light-1440, CA-light-320, CA-light-1280, MX-light-390, AU-dark-390 | Same hero, finder, featured meal, shortcut, notebook, editorial and play architecture. Country data varies honestly; the smaller Mexican and Australian selections do not create empty replacement modules. |
| Country and appearance | country-open-light-320, appearance-open-light-320, appearance-open-dark-390 | Full country names, original SVG flags, readable current selection, visible focus and bounded panels. Day/night buttons look actionable and have a selected treatment. |
| Navigation | navigation-open-light-320, navigation-open-dark-1280 | Clear mobile close action, grouped Learn destinations and readable desktop popover. No competing page decoration inside the menu. |
| Finder | finder-light-320, filter-open-light-320, filter-open-dark-390 | Dense order-first results, explicit portions and primary nutrition. A wrapped protein label caused the 320px filter inputs to misalign; this was selected for correction. |
| Diary initial and recorded | diary-light-320, diary-dark-390, diary-logged-light-390 | Four consistent meal groups, meaningful empty totals, primary Add food, secondary repeat/recipe/preferences actions and an unobstructed broccoli companion. |
| Food selection | food-search-light-320, food-review-light-320, food-review-dark-320 | Source and portion precede logging. Real nutrients are readable in both themes; additional details are disclosed progressively. Narrow picker tabs intentionally scroll within their strip. |
| Preferences | diary-preferences-dark-1440 | Clear privacy model and organized backup, storage and deletion sections. No installation or unfinished AI promotion. |
| Calculators | calculators-light-320, calculators-dark-1280, calculator-result-light-320, calculator-result-dark-390 | Proper field grouping, unit choices, restrained result hierarchy and visible adult-estimate limitations. The formula was not changed. |
| Restaurant directory and guide | restaurants-light-1440, guide-dark-390 | An open, aligned directory; unsupported local chains link to their official sites. Pizza Nova explicitly presents calorie-only slice information rather than pretending it has complete macros. |
| Editorial | article-light-768 | A readable column, direct ordered guidance, worked portion arithmetic and source/tool links without a generic card wrapper. |
| Games | fruit-light-320, memory-light-390, plate-dark-1280, games-dark-1440 | Orchard, illustrated memory and kitchen-puzzle treatments remain distinct. The directory groups game families rather than displaying all games at once. |

Names in the table refer to PNG files in visual-baseline or visual-journey-baseline. Baseline captures precede the focused source corrections below.

## Source corrections

1. tools/build_master_interface.py now gives the country trigger an accessible name containing its actual full selected country. The old static aria-label suppressed that visible selected name for screen readers.
2. js/markets.js updates the accessible name when a saved country is applied to a global utility page, while retaining explicit country URL precedence.
3. tools/food-design.css uses the existing mobile nutrition label rule as a flex column. The two inputs share a bottom edge when one label wraps, without a fixed pixel offset or new override sheet.
4. js/site-search.js removes the U.S.-specific Chipotle example from the shared no-results hint. The shorter alternative applies to every market.
5. The same search source hides the library heading when zero matches are available. It restores the heading when matching resources are shown and preserves the initial starting-points state when the query is cleared.

No font substitution, arbitrary palette change, character replacement or nutrition-data rewrite was made for this visual audit.

## Additional verification

tools/master_release/visual-completion.cjs includes final assertions for selected-country accessible names, explicit versus remembered country context, keyboard theme selection and reload persistence, featured-card geometry, mobile calorie/protein field alignment and game pause/resume/restart. It also presents exact top-level 1280px screenshots of the US and Canadian homepages side by side in both themes. The existing anti-framing protection prevented an earlier iframe comparison; that protection was preserved, and no fake or replacement page content is used.

The real Canada→US→Canada Subway journey preserves the restaurant and calorie limit. The U.S. source selection currently has missing fat values, so the browser test exercises the truthful missing-macro disclosure and its Show these orders action. It does not treat an intentional incomplete-data state as a failed country switch or fill the missing fat with zero.

tools/master_release/visual-motion.cjs verifies the actual broccoli hover response, persisted Calm motion setting and OS reduced-motion behavior. The shared CSS already provides a complete Calm motion opt-out; no separate diary override was needed.

The motion audit passed at 390 and 1280px in both themes. It also measured 16 semantic contrast combinations per theme from actual computed CSS variables: primary and secondary text against the four principal surfaces, action colors, action text, error feedback, warnings, focus and input borders. The sampled text combinations met 4.5:1 and focus/control borders met 3:1. This token check does not replace a full audit of every rendered element.

tools/master_release/visual-zoom.cjs passed 14 representative page renders and two country-menu states at a documented 200% page-zoom-equivalent setup: 640 CSS pixels rendered into 1280 device pixels. The diary, calculator and country-menu captures were opened and reviewed. This checks effective larger-text reflow; it is explicitly an emulation rather than a native browser chrome or text-only zoom certification.

Final integrated-asset verification passed and is recorded in visual-final/checks.json: 140 sampled route/theme/width render states, ten expanded product/control journeys and two side-by-side homepage comparison images. The final journey checks include the corrected 320px filter alignment, current-country accessible labels, remembered versus explicit markets, theme keyboard/reload persistence, language/search popovers, search empty/matched/cleared states, compatible Subway country filters, truthful missing-macro disclosure, real food review/logging, diary preferences and calculator validation/results. The three sampled game families also passed pause, resume and restart checks at every sampled width/theme combination.

The final corrected filter-sheet captures, language and search panels, empty search, missing-macro disclosure, food review, country picker and both side-by-side homepage comparisons were opened as images. The US/Canada compositions and featured nutrient/action alignment remain consistent. No active CSS reset or nutrition formula change was required.

Broader all-route, formula, data-integrity, grocery search and deployment verification remain separate release checks. This document does not claim full screen-reader certification, real-device coverage or field performance measurements.
