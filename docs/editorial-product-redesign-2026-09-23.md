# GetMacros product-led redesign — 23 September 2026

## Release

GetMacros now leads with an interactive fast-food meal search. The shared navigation groups the principal jobs—find a meal, explore restaurants, use calculators, and learn—and every retained page uses the same header and footer. The visual system uses warm neutral surfaces, dark leafy green, restrained tomato and citrus accents, a readable sans serif for controls and a serif for editorial headings. The homepage replaces generic feature cards with a working preference form, three sourced example orders, a searchable 15-restaurant directory, a calculator preview, concise guidance and a transparent data note. The five existing journal posts have a magazine-style landing page with topic navigation and licensed, credited food photography. Existing article bodies and useful URLs remain intact.

The meal finder now accepts a shareable maximum-calorie value and minimum-protein value alongside the established goal and restaurant choices. Results can be sorted by match, calories or protein; controls have an empty state and reset. The search page searches tracked meal names and restaurants as well as its existing page index. No unknown nutrition value is converted to zero or inferred from another metric. Missing fat remains unverified in all but one recorded order.

Calculator formulas, their error handling and unit conversions are unchanged. Restaurant pages keep their official source links, dates and tracked meals, with a clearer introduction to the page's finder. The canonical sitemap continues to list 72 indexable pages. Shared navigation, semantic sections, metadata and crawlable links support the existing URL architecture rather than introducing an unverified route migration.

## Verification

- Clean staged build, HTML/sitemap/internal-link checks and publication checks passed: 73 HTML pages, 72 indexable pages, 72 sitemap entries and 71 searchable pages.
- Homepage-to-finder, numeric filters, empty state, reset, restaurant identity and overflow passed in Chromium and WebKit, both themes, at 320, 375, 390, 430, 768, 1024, 1280, 1440 and 1920 pixels.
- 52 representative screenshot/layout checks passed. Existing navigation, conversion, recipe, label, quiz, comparison, save, provenance, chain finder, theme, focused calculator, contact and meal-idea browser tests passed. Macro math tests passed.
- Keyboard/menu, focus, preference reset and core contrast checks passed; these checks are not a complete WCAG 2.2 AA audit.
- Local Edge lab test at 390 pixels, cold cache, throttled download and fourfold CPU slowdown: median LCP approximately 1.99 seconds on home, 1.12 seconds on calculators and 1.48 seconds on the meal finder. Recorded CLS was zero in those nine local runs. These are lab observations, not field Core Web Vitals or measured INP.

## Limits and human follow-up

The restaurant dataset is U.S.-focused. Menu composition, prices, nutrition, portions and availability can change; visitors should check the official restaurant source before ordering. Fat is missing for most tracked orders and remains marked unknown. Dietary/allergen filters cannot responsibly be added until there is verified item-level data. The licensed general food photograph is credited and is explicitly not presented as a pictured restaurant order. Previously written health articles were preserved rather than issued a new medical-review claim; a qualified human content and source review remains valuable.

AdSense publisher verification and `ads.txt` remain, while ad loading stays paused pending account-side certified consent configuration and verification. This release does not guarantee AdSense approval, rankings or Core Web Vitals in the field.
