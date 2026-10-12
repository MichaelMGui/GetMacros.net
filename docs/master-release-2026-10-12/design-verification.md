# Shared international interface verification

Implementation date: October 12, 2026. This report covers the interface subtask, not the full database/content/deployment release.

## What changed

- `tools/build_master_interface.py` is the single late homepage generator. United States, Canada, Mexico, United Kingdom, Ireland, Australia, New Zealand and Japan use the same hero, direct meal-entry form, featured-menu composition, local restaurant shortcuts, diary/tool area, reading area and play area. It reads the final order registry, rather than copying U.S. examples across countries.
- Featured cards retain exact named source servings, calories and protein. Portion, source edition, additional nutrient-source links, limitations and secondary macros are available in a disclosure. Unknown secondary nutrients stay unknown. Four cards use a quiet upper accent and aligned nutrition/action tracks.
- Existing SVG food characters and licensed Bricolage/Inter font files remain. No new image dependency, animation package, stock photo or restaurant-logo rights claim was added.
- Country selection is a crawlable list of links with original SVG flags and full readable country names. Selected state, Arrow Up/Down, Home/End, Escape focus return, outside dismissal, explicit preference persistence and responsive scrolling are implemented. Country search appears only when more than 12 supported markets exist. Language is separate and accurately exposes English only.
- Appearance is visibly interactive: sun/moon trigger, labeled Light/Dark choices, active state, persisted choice, system preference support and calm motion. Obsolete appearance declarations were removed from their source in `tools/food-design.css`.
- Navigation switches to its existing mobile screen at 1100px so full country names do not compress the desktop links. The Learn panel has grouped topics rather than a long, flat list of every site resource. Footer wordmark no longer breaks on tablet.
- Existing 56 playable games have coordinated number, kitchen, orchard, memory, logic, word and studio treatments. Original lightweight `images/game-family-motifs.svg` artwork is paired with each game's existing food character. Memory backs, orchard scenes, kitchen frames, precise puzzle frames and studio surfaces differ deliberately. Scoring, controls, pause, restart and deterministic puzzle rules were not rewritten.
- Homepage direct entry does not download the complete restaurant registry, meal datasets or food database. Controls remain usable through native form/link navigation without optional animation.

## Baseline actually reviewed

The root release's actual-production baseline images were read: `baseline/us-home-light-1440.png` and `baseline/-ca-en--light-390.png`. They showed a character/product-led U.S. homepage and a different, table-first Canadian guide composition. The new shared generator replaces that structural divergence.

## Tests actually run

- `python -X utf8 tools/test_master_homepages.py`: PASS. Eight shared section structures, exact market/record nutrient values, local finder actions, country links, both appearance choices and canonical URLs.
- `node --check js/markets.js` and `node --check js/unified-v7.js`: PASS.
- `node tools/international/test-markets.cjs`: PASS. Existing Canadian source fields, order arithmetic, market isolation, missing-value behavior, source versions, private share exclusion and finder/builder agreement.
- `node tools/play_release/test-rules.cjs`: PASS. 2,240 deterministic solvable cases across 56 existing rules, including invalid inputs, overlap, repeated tiles, completion and pause guards.
- `node tools/test-master-interface.cjs`: PASS. 108 rendered interfaces: all eight homepages at 320, 390, 768, 1280 and 1440px in both themes; games directory and six representative individual games at 390/1440 in both themes. Checks covered runtime errors, overflow, shared architecture, current country, local record identity and URLs. Four complete country/navigation/theme/finder journeys exercised keyboard selection/Escape, explicit country URL precedence, stored preference, persisted theme, local GET filters, open desktop/mobile navigation, game pause/resume/restart and reduced motion.
- `node tools/master-calibrate-details.cjs`: PASS. 50 additional renders on five representative/outlier markets and five widths in both themes, measuring nutrient baselines, card heights, action alignment, intact footer wordmark, no page overflow and opening source disclosures.

The browser used actual local static HTML and files at `http://127.0.0.1:4189`, with Edge, service workers blocked and reduced motion. No response interception substituted a different site. Windows sandbox browser-profile errors required approved unsandboxed browser execution. The first test harness incorrectly reset theme storage on every navigation; the harness was corrected to set only absent preferences, then rerun successfully.

## Actual screenshots and visual inspection

Captured files: `design-final/*.png`; automated render results: `design-final/checks.json`; explicit alignment measurements: `design-final/alignment-checks.json`. The automated screenshots are not all claimed as manual visual inspections.

Manually inspected screenshots include:

- U.S. light 1440 and 320; Canada light 1440 and 390 (same architecture compared); Mexico dark 1440; Japan light 390; Australia dark 1280; United Kingdom dark 768.
- Country dropdown light 390; appearance dropdown dark 390; Learn panel light 1440.
- Games directory light 390; Market Memory dark 1440; Fruit Catch light 390; Plate Art dark 390; Garden Glide light 1440.
- Canadian portion/source disclosure light 390.

Two visual defects found during inspection were corrected: the long fourth Australian meal title shifted its nutrition/action baselines, and the tablet footer broke the GetMacros wordmark. Both were then rerendered and inspected; the additional measured alignment checks passed.

## Limits

This subtask does not claim every individual game was manually visually inspected, WCAG certification, real-user performance measurements, native-device testing or production deployment. The root release owns full route testing, calculator/diary verification, imported restaurant/branded coverage, content research and production publication. This interface pass enables no unverified country or translated language. Source menus remain document snapshots, not a live inventory or full-menu audit.

## Final integrated-surface calibration

After the root integrated the expanded Canadian registry and six guides, `node tools/master-calibrate-surfaces.cjs` passed 60 additional actual renders and 60 journeys. Routes: calculator hub, Canadian restaurant directory, Subway Canada, Pizza Nova Canada, Canadian-context search, and the new food library. Every route was rendered at 320, 390, 768, 1280 and 1440px in both themes. Screenshots and checks are in `surfaces-final/`.

The calculator journeys verified native age validation, all three guided groups, a concrete 80kg/180cm/30-year-old male/moderate/maintenance calculation (2,759 kcal, 128g protein), pound/feet/inch conversions and equivalent resubmission, and an out-of-range weight error. Canadian search included the local Subway guide and excluded the U.S. counterpart, including a no-results query. Library journeys used an actual Canadian Subway record, doubled its portion, opened source details, and checked Escape focus restoration. Subway's full 85-row table disclosure was exercised; Pizza Nova's complete 39 calorie rows were compared with the source JSON.

Manual inspection found and corrected additional real gaps:

- The new Canadian directory had no active styling for its presence rows. It now uses open, aligned two-column entries on desktop and one-column entries on mobile, while retaining clear coverage limitations and official-site links.
- Subway's caption started outside the narrow table viewport. The caption now aligns left and wraps within the visible width; section headings have space below tables.
- Pizza Nova displayed five columns of repeated unavailable macros. Its presentation now has Item/portion and Calories columns, retaining every source calorie and explicitly stating that the other nutrients are unavailable, not zero. The registry is unchanged.
- A later food stylesheet initially forced the calorie-only table to 650px, keeping calories offscreen. The specific table subtype now overrides that width without `!important`; actual browser measurement at 390px is 354px, with both columns visible. The final suite explicitly checks this geometry at every tested width.
- Calculator custom errors previously looked like ordinary text. Existing error tokens now distinguish the error, and the late generator adds alert semantics to existing error-message containers.
- The root corrected food-control background shorthand to preserve the shared native-select chevron. The final source-review screenshot shows the unit dropdown clearly.

Final manual views additionally include the integrated calculator result light390, invalid state dark390/1440, directory light1440, Subway guide dark390, Pizza Nova light390 (including its visible calorie column), Canadian search dark390, source review dark390, and mobile calculator navigation light320.

The first immediate library-review test timed out while results were transitioning; a stable-result isolated reproduction succeeded. The harness then waited for the real search busy state to clear and reran the complete suite successfully. The original failure was not described as a passing check.

`tools/master-calibrate-details.cjs` was rerun after integration: PASS50 alignment/source-disclosure renders. `tools/test_master_homepages.py` was also rerun against the new Canadian registry: PASS8 country templates and exact local featured-record values.

## Legacy cleanup and stylesheet budget

`tools/master-audit-css.py` checks final sitemap/private HTML, every JavaScript module, SVG artwork and the active master homepage generator. Following review, 116 obsolete selector fragments were removed at their source: superseded homepage cards/quiz/tool sections, old directory-strip and journal compositions, and unused prior-library/meal-browser presentation. Fallback homepage alternatives, active controls, all dynamic states, source notes, error treatments and reduced-motion rules were retained. Exact removals are in `legacy-css-removed.json`.

The established CSS compiler was retained. `css/publication.css` is **69,303 bytes**, down from 75,994, and remains below the existing 70,000-byte gate. The gate was not raised. `python -X utf8 tools/test_publication.py` passed for the final 348-route inventory, including the stylesheet budget, unique IDs, shared controls, source ordering and preserved verification/integration files.
