# Search discovery repair — October 23, 2026

This release improves existing, source-backed destinations. It creates no new
public URLs, nutrition records or articles. Private Search Console exports,
query telemetry, account screenshots and URL Inspection results remain outside
the public repository.

Implemented:

- All existing market homepages link directly to up to four supported local
  restaurant nutrition tables, in addition to the working finder shortcuts.
- Canadian, UK, U.S., Australian and Mexican homepages feature relevant existing
  reading using the same shared layout.
- Restaurant nutrition tables link to their exact market's worked comparisons.
  The 29 prior editorial-release articles receive explicit contextual links from
  relevant restaurant, grocery-coverage or food-logging guides.
- Restaurant directories use descriptive country-specific headings and metadata.
- The existing label comparison tool answers the observed compare-nutrition-facts
  intent through a matching heading/title while preserving its working form and
  example arithmetic.
- Only changed pages receive the actual October 23 sitemap modification date.
  Canonicals, historical article publication dates and established URLs remain.

No indexing or ranking gain is established by these code changes. A passing
Google live test means the page is fetchable and eligible for indexing, not that
Google has indexed it. Discovered-but-not-indexed URLs are not automatically a
robots, firewall or server failure. Alternative canonicals and intentionally
retired pages must not be reclassified as errors merely to reduce report counts.

Guidance checked:

- https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- https://developers.google.com/search/docs/appearance/title-link
- https://developers.google.com/search/docs/crawling-indexing/links-crawlable
- https://support.google.com/webmasters/answer/7440203
- https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl

Run `python tools/search_recovery/test_discovery.py` after the normal build.
`tools/search_recovery/build.py` includes this pass so repeat builds preserve it.
