# GetMacros submission review — September 9, 2026

The publisher name remains **GetMacros**. No personal qualifications or clinical review credentials have been invented.

## Content and search intent

- Rewrote 19 guides, policies and the restaurant-comparison article around a clear question or task. Removed repetitive appendices, unsupported guarantees and conflicting protein guidance.
- Kept short tool instructions short. Longer research articles retain their explanations and sources. There is no arbitrary minimum word count.
- Updated page titles, descriptions, search cards, feed summaries and relevant modification dates to match the final content.
- Used plain questions such as “How much protein do you need per day?” and “How many calories should I eat a day?” No keyword-volume or traffic forecasts are claimed; Search Console data was not available.
- Kept public contact, privacy, terms, editorial, corrections and accessibility information. Policy text describes the site's actual scope rather than claiming a medical review team.

This follows [Google's people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): answer the reader's question, support claims and avoid writing to a supposed preferred word count.

## Nutrition corrections

- Reviewed all 83 tracked restaurant records against linked official menu information. The source, review date and values are stored in `tools/restaurant-review.json`.
- Corrected stale figures, replaced obsolete examples, named included dressings and sides, and checked combined-order arithmetic.
- Removed incorrect dietary labels, including vegetarian Popeyes red beans and rice and plant-based CAVA Falafel Crunch.
- Current Taco Bell calories are confirmed; protein is confirmed for the Cantina Chicken Bowl. Other unconfirmed nutrients remain null. Missing values cannot qualify an order for a nutrient-dependent filter.
- CAVA figures are tied to the linked nutrition guide; the page explicitly asks readers to confirm seasonal builds and local availability.
- Rebuilt the 25-food protein comparison using specific USDA reference entries and one named product label. Portion figures and calorie comparisons now use the same underlying record. `tools/protein-food-review.json` preserves the references.
- Explained the protein RDA correctly, separated it from exercise ranges, checked worked macro arithmetic, and removed unsupported claims about guaranteed muscle gain or fixed scale-change timelines.

## Presentation and behavior

- Reviewed mobile, tablet and desktop layouts in light and dark themes.
- Added readable mobile rows to the reviewed article tables and made article buttons distinct.
- Restored article illustrations on mobile. Repeated restaurant rankings are expandable instead of lengthening every page with the same meals.
- Preserved calculator unit conversion, input validation, meal search, dietary filters, multiple goal selection, navigation, back-to-top and motion preferences.
- Shared styles remain bundled and cache-versioned. Removed unused home-calculator scripts from the homepage.

## Validation

- Complete isolated site rebuild and all Python build checks passed: 73 HTML pages, 72 indexable pages, 72 sitemap URLs and 71 searchable resources.
- Automated audits checked page overflow, clipped text, missing images and browser errors at 320, 768 and 1440 pixels in both themes.
- Text-contrast and ordinary-word-wrapping audits passed, with visual inspection of the revised articles and mobile comparisons.
- Edge and WebKit checks covered quiz flows, meal filters, all 83 browse entries, no-JavaScript meal access and restaurant matchers.
- Calculator checks covered conversions, BMR, TDEE, goal adjustments, macro energy balance, recipe scaling and protein-cost comparison. Mobile menu and motion controls passed.
- The AdSense publisher `ca-pub-2316153877942502` is present in the asynchronous script on every indexable page. The site validator also checks the publisher metadata and ads.txt.

## Submission boundary

These checks establish the work completed on the site; they do not constitute Google approval, an independent accessibility certification or clinical validation. Restaurant menus and labels can change. Google makes the AdSense approval decision, and the account's submission status was not inspected or changed during this review.
