Search landing-page recovery — October 21, 2026

Source: an authorized Search Console review of Performance, Page indexing,
individual URL Inspection, Sitemaps, manual actions, security, removals,
robots.txt and Crawl stats. Private telemetry and account information are not
included in the public repository. Google report totals and individual URL
Inspection can differ because the aggregate report is older.

Implementation
- Existing market finders: current catalog counts, accurate market-specific
  titles/descriptions, matching application schema and crawlable guide links.
- Existing regional protein collections: individual 250–900 kcal portions with
  at least 25 g protein, complete macros, up to two examples per chain; explicit
  editorial selection, no healthiest ranking. Catering/sharing packs excluded
  only from these curated lists. Full finder data is unchanged.
- U.S. healthy-fast-food guide: correct current counts, matching CollectionPage
  schema, a direct answer about portions and complete orders, relevant links.
- Shared homepages: deliberate links to the actual local comparison resource.
- Only changed landing pages receive a new sitemap modification date.
- Sources and nutrients preserved. No new restaurant or grocery records claimed.
- Four narrowly scoped legacy game URLs have reviewed replacement destinations.
  Their actual edge status is verified separately from repository publication.

Verification
See build-verified.log (local execution log), browser.json and before/after
screenshots. New selection/provenance/count tests: tools/search_recovery/test.py.
Current pages are not guaranteed to be indexed or rank because they build.
Production receipt and submission results are recorded after publication.

Guidance reviewed
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
https://developers.google.com/search/docs/crawling-indexing/301-redirects
https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
https://support.google.com/webmasters/answer/7440203
https://support.google.com/webmasters/answer/9012289

Limits
This work fixes verified content/discovery weaknesses; it does not prove the
cause of an algorithmic ranking change. Do not turn legitimate alternative
canonicals or retired unrelated articles into artificial indexing targets.
Do not mass-redirect unrelated health articles to the homepage. Search Console
requests are crawl requests, not confirmation of indexing or traffic gains.
