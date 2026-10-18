# Search, quiz and food-picker clarity — 18 October 2026

## Implemented

- Replaced the large blue search outline with a two-pixel green focus underline; keyboard focus remains visible. Other keyboard controls use a smaller brand-colored focus ring.
- Aligned food search fields and submit buttons to the same 48-pixel height. Header search controls also share one height.
- Replaced full rectangular select borders with a quiet underline across the shared interface, including the Learn topic selector. Native selection semantics remain intact.
- Rebuilt quiz choices as open illustrated rows. Restaurant choices use thin separators, readable labels and native checkboxes rather than outlined tiles. Search, multi-selection, mutually exclusive “Any restaurant”, back navigation and filtering are preserved.
- Rebuilt the food picker around a short heading, a readable meal selector, understated source tabs, one search row, and collapsed Filters/Categories controls. Breakfast no longer competes with three cramped radio tiles.
- Removed duplicated search labels and repeated selection instructions. Source-list summaries are shorter; source edition, historical status, nutrition, provenance and serving information remain in the food review.
- Fixed the browser dialog width limit at narrow sizes so all five source tabs fit at 320 pixels. Food results appear within the initial viewport.
- Removed the old competing picker/meal-choice CSS rather than adding another override stylesheet.

## Preserved

Nutrition records, calculator formulas, country-specific data, URLs, source disclosures, local diary privacy, favorites, saved orders, recipes, export/import and the existing food characters.

## Verification

- Supported build: `python tools/run_food_build.py` passed. The first sandboxed attempt could not create temporary fixtures; the rerun with temporary-file access passed.
- Repeatable integration: `python tools/product_release/test-generators.py` passed both builds with identical output.
- `node tools/check-interface-clarity.cjs` passed at 320, 390, 768, 1280 and 1440 CSS pixels in both themes. Checked search/button alignment, visible focus underline, all source tabs fitting, expanded filters/categories, portion review, Breakfast logging/reload, meal selection, keyboard tabs, full quiz progression, Learn topic selection, theme persistence and overflow on five additional shared-style routes. No browser runtime errors.
- Existing `node tools/master_release/check-diary-meals.cjs` passed ten theme/viewport combinations across eight sampled country contexts, checking all four meal groups, saved-source arithmetic, edit/move, undo, date/country persistence and unavailable nutrients. Updated obsolete selectors/assertions to match the current meal select and existing single-entry display; missing values are still explicitly tested.
- Nutrition/formula, food model, ingredient-comparison and diary-source regressions passed.
- Publication, internal-link and immutable-asset checks passed: 405 public HTML routes; 402 eligible sitemap pages. This is programmatic coverage, not a claim that every route was visually inspected.
- Actual screenshot review covered the mobile picker at 320/390, food review in both themes, mobile/desktop restaurant quiz, and desktop Learn selector. Browser screenshots are in `before/` and `after/` beside this report.

## Scope and limitations

Shared CSS and hashed asset references reach all public routes. Authored body changes are limited to the diary, food library and comparison workspace search markup. Data and article bodies are unchanged. Tests ran in Microsoft Edge on Windows; native iOS/Safari menus were not tested on a physical device. No accessibility-conformance claim is made.

Deployment: prepared for the established GitHub Pages workflow; exact published revision and production checks are recorded separately after deployment.
