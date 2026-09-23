# Search research — botanical redesign

Research date: 2026-09-23. Queries were English and aimed at U.S. restaurant menus. The search service's physical locale was not verified. These are qualitative intent observations, not keyword-volume or ranking measurements. No current Search Console export or authenticated analytics access was available. Historical user screenshots are not treated as current performance data.

## Current primary guidance inspected

- [Helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): original utility and an identifiable purpose matter; arbitrary length and design-only date updates are not quality signals.
- [Search Essentials](https://developers.google.com/search/docs/essentials): use clear user vocabulary, meaningful titles and crawlable links. Eligibility does not guarantee indexing or traffic.
- [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies): avoid keyword stuffing, doorway variations and scaled pages without distinct value.
- [Structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) and [introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data): markup must describe visible, eligible content. No invented ratings, authors or recipe markup for restaurant comparisons.
- [Canonical consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls): preserve a consistent canonical destination for filter variants; canonicalization is not a reason to delete useful filtering.
- [WCAG 2.2 reference](https://www.w3.org/WAI/WCAG22/quickref/): used for keyboard, contrast, reflow, focus and target-size review. Automated tests alone do not certify conformance.

## Queries and observations

| Query | Sources inspected | Observation / useful opportunity | Implementation |
|---|---|---|---|
| healthy fast food high protein meals under 500 calories US | Search result excerpts for [EatMinMax](https://eatminmax.com/fast-food-under-500-calories) and [Atey20](https://www.atey20.com/goals/cutting); own healthy-fast-food result. EatMinMax direct open failed. | Results emphasize numerical thresholds and whole orders. Exact included items and missing values are more useful than unsupported “healthiest” claims. | Functional homepage entry, maximum calories/minimum protein controls, visible meal composition and per-order comparison. |
| Chipotle high protein nutrition calculator official | [Official calculator](https://www.chipotle.com/nutrition-calculator?restaurant=604), official newsroom search result | Intent depends on the exact bowl/build. Generic chain advice cannot substitute for ingredient and portion assumptions. | Preserve individual tracked builds, chain-specific pages and source links; remove repeated generic chain instructions. No new values inferred from search snippets. |
| macro calorie calculator daily protein targets | [Barbell Medicine calculator](https://www.barbellmedicine.com/resources/macronutrient-calculator/) opened | Visitors expect a usable calculator followed by methods and limits, not a long landing page before inputs. | Distinct calculator workspace, preserved units/formulas, explanations separated from the primary form. |
| healthy fast food low sodium meals US | Search result excerpts for [Healthline](https://www.healthline.com/nutrition/low-sodium-fast-food) and [Low Sodium Fast Food](https://lowsodiumfastfood.com/) | Specific mg limits are useful. “Low sodium” must not imply a meal is safe for a medical condition. | Added maximum sodium control with units, URL persistence and unknown-value exclusion; no medical-safety classification added. |
| Chick-fil-A high protein meals nutrition official | Search results for [official nutrition](https://www.chick-fil-a.com/nutrition-allergens) and [Dietary Preference Center](https://www.chick-fil-a.com/customer-support/our-food/nutrition-and-allergens/what-is-the-dietary-preference-center) | Official portions and included items should remain accessible alongside third-party comparisons. | Preserved official source links and U.S. coverage disclosure; retained verified figures and unknown fat values. |
| protein cost per gram calculator compare food labels servings | Search result excerpts for [Kalo](https://www.getkalohealth.com/tools/protein-cost-calculator) and own calculator | The useful task is comparing the user's actual package price and protein amount. Universal price claims are unreliable. | Preserve explicit package/serving inputs and per-gram output; improve tool hierarchy instead of generating price lists. |

Search-result excerpts are explicitly distinguished from pages opened. No competitor traffic, difficulty, search volume, backlinks or projected revenue were obtained or invented. No new nutrition claim was sourced solely from a competitor excerpt.

## Technical decisions

- Keep all 73 public HTML URLs, including the non-indexable 404. Existing inner-page filenames remain unchanged.
- Keep one canonical URL per page and the existing canonical policy for interactive finder parameters. Do not publish separate indexable pages for each filter combination.
- Preserve legitimate verification files and metadata, source links, existing reviewed dates and factual schema. Design edits do not constitute nutrition-data re-verification.
- Retain specific titles already matching their page intent. Avoid rewriting accurate labels merely to insert keywords.
- Use `query-to-page.csv` for the route-level intent, supporting questions, unique utility and next action. It is an editorial map, not measured keyword demand.
- Current validation checks internal links, canonical destinations, metadata and sitemap coverage. Local route tests cannot prove production HTTP status, DNS health or Google's selected canonical.

AdSense acceptance and search growth are outside the scope of any design or lab-test guarantee.
