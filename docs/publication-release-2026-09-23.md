# GetMacros publication rebuild — 23 September 2026

## What changed

- All 73 retained HTML pages now share one 33 KB stylesheet, replacing overlapping historical styles and late stylesheet injection. The build no longer reruns retired redesign generators over reviewed pages.
- A new homepage uses licensed food photography, restrained green and warm neutral colours, editorial typography, restaurant navigation, focused tool links and a visible explanation of the data.
- Calculator forms, meal results, comparison pickers, search, guides, contact and mobile navigation use coherent light and dark layouts. Keyboard focus and reduced-motion preferences remain supported.
- Five existing guides gained original worked examples: calorie estimates, reading labels, serving sizes, protein cost and complete restaurant orders. Hypothetical numbers are identified as examples. No new keyword pages, invented credentials or blanket date refreshes.
- Meal results now show calories, protein, carbs and fat, plus the region, portion description, record date and official source. Missing values are explicitly unverified; the historical `f` field is fiber, not fat. One sandwich's fat and weighed portion were verified against Chick-fil-A's official nutrition source. The other missing fat values have not been guessed.
- Added a preference reset alongside editable answers. Retained 72 sitemap URLs and checked internal destinations and anchors.

Representative pages: [Home](https://getmacros.net/), [meal finder](https://getmacros.net/restaurant-meal-finder.html), [calculators](https://getmacros.net/calculators.html), [label guide](https://getmacros.net/how-to-read-a-nutrition-label.html), [contact](https://getmacros.net/contact.html).

## Confirmed fixes and AdSense limitations

The owner reported “low quality content.” That category does not identify Google's particular objections. The audit independently found competing presentation layers, incomplete macro display and unconditional advertising requests. Those delivery/display issues are addressed; worked examples and clearer source context improve editorial usefulness. None of this establishes that Google will approve the site.

Publisher verification and the supplied `ads.txt` record are retained. Google ad loading is paused, and the privacy notice reflects that state. Browser tests observed no Google ad requests from the site code. A certified consent-management configuration cannot be verified or configured without the owner's advertising account access. Do not restore ad loading before the applicable consent configuration is tested.

Owner/account work: verify the publisher and seller record against the AdSense account; configure an appropriate Google-certified CMP where required; check any Cloudflare-injected analytics and regional behaviour; inspect the full rejection notice for additional details. No complete rights clearance of all historical, unused assets is claimed. The new photograph has a recorded licence and credit.

## Tests and measurements

- 292 page checks: all 73 pages at 390 and 1280 pixels in both themes; no document overflow, script errors or extra stylesheets.
- Representative screenshots reviewed across the homepage, search, articles, blog, meal finder, meal ideas, calculators and contact. Follow-up layout checks cover corrected search and comparison controls.
- Chromium and WebKit, 320/768/1440 pixels, both themes: navigation, calculator conversions and invalid age, recipe scaling/zero portions, label comparison, quiz, six-row meal comparisons, saved meals, provenance, restaurant finder and theme switching.
- Four focused calculators: examples, invalid inputs, reset and unit switching in both browsers, both themes, 320/390/1440 pixels. Macro formula and energy-balance tests pass.
- Contact topics, draft URLs, copying and denied-clipboard fallback pass in both browsers/themes. Tests do not send email.
- Meal idea filters, text fit and no-JavaScript content pass in both browsers; search matching/empty results and preference reset pass.
- Core colour contrast: body text 11.67:1 light / 13.34:1 dark; secondary text 5.96:1 / 9.27:1; primary action 7.91:1 / 7.66:1. Skip link and keyboard menu/escape checks pass. This is not a complete WCAG conformance certification.
- Clean staged rebuild, publication validation, sitemap and internal-link checks pass. Source files and deployment remain static HTML, so essential editorial content is crawlable without JavaScript.

Local mobile performance: Edge, 390×844, cold cache, 100 ms latency, 1.6 Mbps download, fourfold CPU slowdown, three runs per page. Median largest-content paint: homepage **1.916 s**, calculators **1.036 s**, meal finder **1.400 s**. Layout shift was 0 for home/calculators and 0.000064 for meal finder; observed load-time long-task blocking was 0 ms. These are local laboratory measurements, not production CrUX, measured interaction latency or an AdSense threshold. Raw results are in `publication-performance.json`.

## Content and traffic priorities

1. Complete official-source macro and portion verification for the most-used restaurant orders. Prefer fewer thoroughly documented comparisons over hundreds of new pages. Missing fat coverage remains a concrete data improvement opportunity.
2. Use current Search Console query/page exports to choose existing pages with relevant impressions. The old screenshots suggest healthy fast-food and protein questions; they are not current keyword-volume evidence. Separate U.S. and UK intent rather than applying U.S. values to UK searches.
3. Expand the strongest restaurant guides with checked complete-order comparisons: entree, sauce, side and drink; document substitutions and regional limitations. Link each comparison to the working finder and relevant label/portion guide.
4. Measure changes over comparable 28-day periods. Track relevant impressions, clicks, queries and tool use. Keep page titles descriptive; avoid keyword stuffing, mass publishing, purchased traffic or repeated cosmetic rebuilds as a growth strategy.
5. Seek qualified editorial review for consequential nutrition claims where feasible, and credit it only after it actually occurs. Keep ownership, corrections and sourcing easy to find.

## Next AdSense review

Check the deployed site and account-side items above, confirm the exact rejection requirements have been addressed, then use the review option shown in AdSense. Keep the ownership verification available. A successful sitemap submission or passing performance test does not imply AdSense approval. Do not promise a review date, approval, rankings or traffic.
