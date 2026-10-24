# Five article utility improvements — October 24, 2026

This release improves existing URLs. It adds no public pages, restaurant records
or branded-food records and does not claim a ranking or traffic gain.

The five pages were indexed and technically accessible. No crawl prohibition was
found. Their lack of impressions does not identify an algorithmic cause: they are
recent pages, two were only confirmed indexed on October 24, and the completed
performance report ended October 22. The 24-hour report also showed no activity.
Account reports and screenshots remain in the private evidence directory.

Implemented changes:

- Specific calories/protein/nutrition titles, H1s, descriptions and matching
  Article metadata for all five URLs. Original publication dates remain October
  19. The actual tool release is dated October 24.
- FAGE U.S. yogurt and Barilla Australian dry-pasta portion calculators, generated
  from the existing authored source tables. Both retain server-rendered tables
  when JavaScript is unavailable.
- Greggs UK and Tim Hortons Canada breakfast builders that add explicitly selected
  source components once. They read the current local order registry; they do not
  substitute another country's recipes or claim to be official combo totals.
- A manual UPC/EAN lookup form on the barcode guide, using the existing food
  library. A browser check found a real imported USDA item through its GTIN.
- Six contextual links from relevant breakfast, protein-food and serving-size
  guides, refreshed editorial cards and site-search previews.
- Small, route-specific assets. Calculation choices stay in memory; the tool
  code does not store them, place them in URLs, or send them to analytics.

Research and limits:

- Google Search Central: [helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content),
  [descriptive titles](https://developers.google.com/search/docs/appearance/title-link),
  and [spam policies](https://developers.google.com/search/docs/essentials/spam-policies).
- Public search observations included Greggs breakfast-baguette calories/protein,
  Tim Hortons Canada breakfast, FAGE fat-level comparisons, Australian Barilla
  Protein+ and barcode nutrition mismatches. These were observations of result
  types, not keyword-volume, ranking-position or traffic estimates.
- Barilla's [Australian Protein+](https://www.barilla.com/en-au/products/pasta/protein-plus/spaghetti-protein-plus)
  and [classic spaghetti](https://www.barilla.com/en-au/products/pasta/classic-blue-box/spaghetti)
  panels were re-read October 24 and agree with the retained table.
- FAGE's official pages returned retrieval errors during this check. Its retained
  October 19 source review is preserved and is not relabeled as checked today.
  Greggs and Tim Hortons likewise retain their original source-check dates.
- Source portions and rounding remain explicit. Unreported nutrients stay unknown.
  None of these changes proves why Google assigned a particular ranking.

Validation evidence is in `checks-final.json`, `implementation.json`,
`publication.json` and `production.json` when those stages are complete. Initial
failures and their fixes remain in `checks.log`: U.S. spelling in the global
editorial teaser, the new scoped CSS permission in the publication assertion,
and a Windows sandbox temporary-fixture permission error (retried successfully
with normal temporary-directory access).
