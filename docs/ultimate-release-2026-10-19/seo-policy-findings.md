# Technical SEO, trust and measurement findings

Baseline inspected 19 October 2026. This report distinguishes source inspection, passive production HTTP and unavailable account evidence. It does not claim rendered quality, Google indexing, measured search demand or Journey approval.

## Concrete changes for the integrated release

1. **Correct stale current totals.** `about.html` describes 463 orders from 25 U.S. chains. `sources.html` calls the same October 4 snapshot the complete current dataset. Remove the current-total claim or generate a correctly scoped total; preserve the historic expansion facts with a clear snapshot date. The current registry contains 10,327 market-specific records, not 10,327 audited full-menu items.
2. **Make the analytics notice match evidence.** `privacy.html` states Cloudflare adds an analytics script. No beacon was found in six current public HTML responses. A Cloudflare security appendix was present. Verify real browser requests, then describe confirmed processing and distinguish edge/security logs from Web Analytics. Do not claim GA4 is installed: none is present in 439 local public pages or six passive production responses.
3. **Clarify the current asset inventory.** `images/README.md` starts with multiple historic sections each labeled current, conflicting font lists and obsolete image-free presentation claims. Add one authoritative current pointer while retaining history. Prior `images/meal-cutouts/provenance.json` and the image rights review identify original illustrations; historic third-party logo files are not rights-cleared merely because they remain on disk.
4. **Review new article purpose and authorship honestly.** The existing `editorial-policy.html` discloses software/AI assistance and no claimed medical review. Preserve this honesty. Each new page needs a specific reader task, meaningful original comparison/worked example, actual source assumptions, truthful dates and helpful tool links. Do not label automated arithmetic checks as dietitian or human expert review.
5. **Keep the successful SEO foundation.** The baseline parser found 436 indexable/sitemap routes with unique titles/descriptions, one H1 per page, valid JSON-LD, alt attributes and reciprocal hreflang. Do not rewrite all metadata merely to make a diff. Re-run the checks after new pages and layouts are integrated; source parsing does not establish crawl/index status.
6. **Keep personal states out of discovery.** `food-diary.html` and `offline.html` are noindex; the 404 is noindex without a canonical. Preserve the diary exclusion. Keep canonical links on browse/tool pages stable and do not add query combinations or branded-source shards to the sitemap. Current restaurant links and country alternatives are crawlable static anchors.

## Research applied to decisions

- [Google's starter guidance](https://developers.google.com/search/docs/fundamentals/seo-starter-guide): keep useful crawlable links and clear page-specific titles/descriptions; there is no useful word-count target.
- [Helpful content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): individual pages should offer original effort and a satisfying answer. Source attribution alone does not replace that effort. Preserve truthful creation and review information.
- [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies): do not create country/restaurant/nutrient combinations primarily to multiply search pages. New article count is a work target, not a quality metric.
- [Title links](https://developers.google.com/search/docs/appearance/title-link): concise, descriptive, distinct page titles; avoid repeated boilerplate, extra keyword variants and misleading prominence.
- [Images](https://developers.google.com/search/docs/appearance/google-images): meaningful content images belong in ordinary image elements with useful context, dimensions and responsive delivery. Label illustrations honestly; never write alt text implying an exact photographed portion.
- [Localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions): reciprocal alternatives must be real equivalents, including self-reference; market-specific articles are not automatically language alternatives.
- [JavaScript SEO](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics): preserve the substantial static HTML and anchors. Do not replace public guides with an empty application shell.
- [Faceted crawling](https://developers.google.com/crawling/docs/faceted-navigation): prevent arbitrary combinations becoming an endless crawl space. Existing canonical URLs and finite links are retained; a canonical is not a guarantee that a parameter URL cannot be crawled.

## Search observations and measurement limits

The companion [intent map](keyword-intent-map.csv) records literal public queries, observed result URLs, market, existing overlap and the proposed value of the page/tool. No position, search volume, difficulty, CTR or traffic estimate is reported. Public web search observations are **not** a Search Console report or proof that Google users typed a particular query at a measured rate. One existing Harvey's Canada guide appeared in a public search result; this does not establish site-wide indexing coverage or clicks.

For an authorized performance review, export Search Console query/page/country/device data for comparable date ranges and GA4 sessions/engagement/landing pages with timezone and filters. Prioritize clear intent gaps and pages with observed impressions, then measure outcomes after publication. No such private exports were available for this audit.
