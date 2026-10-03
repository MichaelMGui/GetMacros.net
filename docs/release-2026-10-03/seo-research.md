# Search research for the October 3 release

Research date: **2026-10-03**, using the client’s America/Toronto date. Browser search results were not personalized to an authenticated Google account or a specified country. Queries were in English. Nutrition-source scope is stated separately; the restaurant product uses U.S. menu data.

This file records qualitative observations, not search volume, keyword difficulty, ranking measurements or a traffic forecast. No current authorized Search Console export or analytics account was accessed by this content work. The historic screenshots in the conversation are not current measurement data.

## Current primary search guidance inspected

All eight URLs requested in the brief were opened successfully. The final faceted-navigation URL is on Google’s crawling documentation site rather than the older Search documentation path.

| Primary source | Finding applied to this release |
| --- | --- |
| [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) | Descriptive unique titles, useful links and readable content help discovery. There is no magic word count or automatic first-place technique. Maintain established URLs and write titles for their actual task. |
| [Helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | Original analysis and utility matter. Our new pages have specific worked examples or dataset comparisons; broad existing intents stay with their established page. The publication batch is not a ranking requirement. |
| [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies) | Avoid keyword stuffing, doorway variations and scaled content without added value. Do not turn every combination of restaurant, nutrient and calorie limit into an indexable page. |
| [Page experience](https://developers.google.com/search/docs/appearance/page-experience) | Assess mobile readability, security, intrusive overlays and advertising alongside Core Web Vitals. A good lab score cannot guarantee rankings. |
| [Structured-data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) | Markup must accurately represent visible content. Use article or page metadata where appropriate; no invented reviews, medical reviewers or recipe markup for restaurant comparisons. |
| [AI features and websites](https://developers.google.com/search/docs/appearance/ai-features) | Normal Search fundamentals still apply. No special AI file or schema is required, and eligibility does not guarantee appearance. Preserve visible textual explanations and crawlable links. |
| [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) | Crawling, rendering and indexing are distinct. Initial static article text, meaningful links and canonicals must exist independently of optional interface scripts. A runtime loading state alone does not diagnose indexing failure. |
| [Managing faceted navigation](https://developers.google.com/crawling/docs/faceted-navigation) | Unbounded filter URLs can waste crawling. Keep arbitrary finder states outside the sitemap, canonicalize deliberately, and give curated pages distinct visible analysis. Do not combine robots blocking with a noindex that a blocked crawler cannot read. |

These findings informed the content payload and integration instructions. The parent release implementation owns the actual sitemap, robots, canonical, structured-data, navigation and rendering checks; this document does not assert that unrun checks passed.

### Additional implementation guidance inspected by the release integrator

On October 3, the integrator also opened [AdSense pages readiness](https://support.google.com/adsense/answer/7299563?hl=en), [Core Web Vitals](https://web.dev/articles/vitals), [layout-shift optimization](https://web.dev/articles/optimize-cls), [W3C hover/focus content](https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html) and [W3C animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html). These support original useful content rather than an approval-by-page-count claim, explicit separation of lab results from field measurements, reserved artwork space, dismissible character greetings and reduced-motion behavior. Animation guidance includes a beyond-AA criterion; its use is not a claim that the entire site satisfies WCAG. The actual implementation and test evidence are recorded in `release-report.md`; advertising remains disabled and unconfigured.

## Search-intent observations

Searches were run with the exact queries below. Linked sources identify inspected material or an observed result. A result-only observation is explicitly labeled. Third-party pages were used to understand page types, never as verified nutrition data or copied wording.

| Query | Observed intent and source | Existing destination or gap | Release action and rationale |
| --- | --- | --- | --- |
| nutrition label grams vs ml serving size compare | Unit mismatch and serving conversion questions; [FDA serving sizes](https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label) inspected. | Broad label guide exists; gram-to-volume boundary lacks a focused explanation. | New grams-vs-milliliters page with a same-product conversion example and explicit prohibition on unsupported conversions. High priority: prevents a calculator-input error. |
| raw cooked weight nutrition tracking USDA | Food state and cooking yield, rather than a new daily macro target; [USDA cooking-yield table](https://www.ars.usda.gov/ARSUserFiles/80400525/data/retn/usda_cookingyields_meatpoultry.pdf) inspected. | Recipe guide exists, but matching raw/cooked state needs a narrow workflow. | New raw-vs-cooked page with a measured rice-batch example; reject a separate dry-rice page to avoid splitting this answer. |
| nutrition label drained weight canned food FDA | Serving basis of canned solids versus liquid; [FDA guide](https://www.fda.gov/media/81606/download), drained-weight and serving sections inspected. | Existing label guide is general. | New drained-weight resource. No universal sodium-reduction or drained conversion claims. |
| high protein fast food breakfast drink calories | Lists of chain orders and protein/calorie rankings appeared, including [Fast Food Index](https://www.fastfoodindex.com/high-protein-fast-food-breakfast/) as a search-result description only; its page fetch failed. | Dunkin’ and Starbucks guides already cover tracked orders. | Dataset agent supplies numerical breakfast comparison; this batch explains the full drink/side order. Do not duplicate a generic top-ten list. |
| site.fda.gov nutrition label prepared as packaged servings container rounding | Official label-basis guidance; [FDA guide](https://www.fda.gov/media/81606/download) inspected. | General label reading and recipe guides exist. | Prepared-column and package-count examples solve different errors: double counting ingredients versus choosing the wrong packaging multiplier. |
| site.usda.gov cooking yield raw cooked weight rice | Food-yield purchasing/preparation guidance; [USDA Food Buying Guide Appendix B](https://foodbuyingguide.fns.usda.gov/Appendix/ResourceAppendixB) inspected. | Cooked-yield examples can live in raw/cooked resource. | Publish a separate edible-versus-purchased explanation only because bones, peel and discarded materials answer a distinct cost/portion question. |
| protein powder scoop serving weight nutrition label | Scoop count versus label gram weight appeared in questions and label examples; official [FDA serving guide](https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label) inspected for the serving principle. | Daily protein target and protein-cost tools exist; scoop mass is separate. | New partial-scoop calculation, with no supplement recommendation. |
| macro calculator calories restaurant meal target | Discovery tools and reverse searches appeared. [Restaurant Nutrition Calculator](https://restaurantnutritioncalc.com/) inspected: chain-specific builders are a common page type. | Daily calculator and meal finder exist, but the handoff lacks an explanation. | New daily-versus-meal handoff page. Links pass no age, body weight or other sensitive calculator inputs. |
| food label serving size whole package calories | Package versus serving arithmetic; [FDA serving guide](https://www.fda.gov/food/nutrition-facts-label/serving-size-nutrition-facts-label) inspected. | Serving-versus-portion article already explains the broad distinction. | New nested packet/outer-box worked example and a warning against multiplying the package column twice. |
| protein cost per gram calculator food | Calculator results appeared, including GetMacros and [CalcHive](https://calchive.org/tools/nutrition/protein-cost-calculator/). CalcHive’s page fetch failed, so only its result description was observed. | Existing protein-value calculator already serves the main intent. | Keep existing URL and tool. New supporting resource covers bulk-pack waste and a break-even use rate, not another basic protein-price calculator. |
| calculate macros unequal recipe portions | Recipe tools and weight-based meal-prep examples; [Macro & Meals recipe guide](https://macroandmeals.com/blog/how-to-calculate-macros-in-a-recipe/) opened. | Existing recipe scaler divides equal servings. | New unequal-weight workflow with totals that sum back to the batch and an uneven-mixing limitation. |
| nutrition label as packaged vs as prepared | Mixed-column and added-ingredient questions; [FDA guide](https://www.fda.gov/media/81606/download) inspected. | Broad recipe content does not make milk double-counting obvious. | A worked cereal example compares exact prepared directions with a different added drink. |
| healthy fast food meals calories protein | Search results included meal-discovery products and ranked-list pages, including [GetMacros](https://getmacros.net/restaurant-meal-finder.html) and [MenuCal](https://foodoutcalc.com/healthiest-fast-food) result descriptions. | Existing healthy-fast-food guide and finder serve the broad intent. | Improve those established routes. Curated dataset pages should state their selection criteria instead of adopting unsupported universal “healthiest” scores. |
| high protein fast food orders | Result descriptions emphasized protein grams, calories and chain choices, including [BodyBuddy](https://bodybuddy.app/blog/healthy-fast-food-high-protein-orders). | Existing broad food lists do not replace restaurant order discovery. | Data-derived protein collections should keep complete order definitions and supported values, then offer a finder handoff. No competitor nutrition figures copied. |
| fast food meals under 600 calories | Search results included calorie-limit finders such as [MinMax](https://eatminmax.com/), observed through its result description. | The finder already applies an explicit maximum. | Preserve that utility; avoid publishing many nearly identical calorie-threshold pages. A curated collection requires analysis beyond a filter dump. |
| Chipotle bowl nutrition calories protein compare | Result descriptions included an ingredient builder at [MenuCalorie](https://menucalorie.com/chipotle-bowl-calories/) and a combination analysis at [Bowl Macros](https://www.bowl-macros.com/blog/chipotle-bowl-study). | Existing Chipotle guide already owns the chain intent. | Improve exact supported order comparisons in that route. Do not claim an exhaustive combination study from GetMacros’ selected orders. |

Additional authoritative source searches inspected NIST mass/volume definitions, USDA Food Buying Guide edible portions, FDA rounding resources and FDA menu-labeling guidance. These supported the publication claims; they were not interpreted as demand measurements.

## Query-to-page map for practical resources

Each title and description is implemented in `tools/release_explainers.json`. The generator should preserve the body text and useful tool links rather than append repeated keyword paragraphs.

| Route | Reader’s question | Distinct utility | Next action |
| --- | --- | --- | --- |
| grams-vs-milliliters-nutrition-labels.html | Can I compare 100 g with 100 mL? | Unit decision table and same-product conversion. | Compare matched label portions. |
| raw-vs-cooked-food-weight.html | Which preparation state should I weigh? | Two valid recording paths and measured batch yield. | Divide a recipe using a matching basis. |
| drained-weight-nutrition-label.html | Which can weight describes what I eat? | Supported drained scaling versus an unknowable undrained conversion. | Check the label or manufacturer. |
| calories-in-multi-serving-packages.html | What does the whole bag contain? | Inner-packet versus outer-box count. | Scale a nutrient to the eaten portion. |
| as-packaged-vs-prepared-nutrition.html | Is milk or oil included already? | Original double-counting and alternate preparation example. | Sum actual ingredients. |
| nutrition-label-rounding.html | Why are the numbers slightly different? | Rounding example and a check for larger input errors. | Preserve published values and uncertainty. |
| edible-portion-vs-purchased-weight.html | Do bones or peel belong in this weight? | Edible-yield and cost comparison. | Match edible nutrition basis. |
| unequal-recipe-portions.html | How do I count a larger container? | Weight shares summing back to the whole batch. | Use a finished-weight note. |
| calculate-macros-mixed-bowl.html | How do separate labels make a meal total? | Four-component bowl including sauce and different measurement units. | Check individual portions in the label tool. |
| protein-powder-scoop-weight.html | How much protein is in my partial scoop? | Powder mass versus protein mass. | Add shake liquid separately. |
| protein-cost-food-waste.html | Is the bulk pack still cheaper if I waste some? | Break-even use rate. | Compare package prices and realistic use. |
| use-calorie-target-meal-finder.html | How does a daily estimate help me pick lunch? | Meal limit versus daily total and non-sensitive manual handoff. | Enter optional limits in the finder. |
| compare-complete-restaurant-orders.html | Are these meal totals comparable? | An order-ranking reversal and inclusion worksheet. | Compare exact orders and source versions. |
| missing-restaurant-nutrition.html | Is “not verified” the same as zero? | Unknown sauce example and strict-filter implications. | Find a supported record or report a correction. |
| breakfast-drinks-and-add-ons.html | Does the sandwich number describe breakfast? | Full breakfast drink/side comparison. | Check the chain’s tracked breakfast orders. |

## Rejected or consolidated ideas

- Separate dry-versus-cooked-rice page: folded into raw/cooked weight; a second page would split the same problem.
- Another broad protein-cost calculator explanation: existing tool already serves it; food waste supplies a genuinely different decision.
- New general “what are macros,” “healthy fast food” or daily protein-target pages: existing established URLs serve them.
- Exact nutrient reductions from rinsing, draining, deleting sauces or changing milk without verified component data: unsupported, not published.
- Generic recipe estimates from a meal name: exact quantities are missing. The mixed-bowl page requires known ingredient labels.
- Separate pages for each calorie/filter combination: arbitrary states are product interactions, not a publication plan.

## Verification limits

Live search research was performed, but no current site ranking, keyword volume or AdSense eligibility was measured. One cooking-yield URL failed before the correct USDA file was found. Two third-party page fetches failed; their descriptions were not treated as full-page inspections. Source inspection is not the same as an independent dietitian review. Publication dates describe new authored pages, not newly reverified restaurant datasets.
