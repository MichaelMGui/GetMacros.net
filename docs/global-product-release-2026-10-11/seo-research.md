# Research performed October 11, 2026

No authorized Search Console or analytics session/export was available. The earlier visitor increase is not verified here. No search volume, difficulty, ranking forecast or field-performance result is asserted.

Current primary guidance inspected:

- [Google helpful, reliable content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): implemented useful source-backed tools and preserved existing article URLs; no individual indexable page per database record or numerical filter.
- [Google multi-regional sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites): published crawlable country paths with their own canonical URLs and genuine local data; no forced IP redirects or untranslated French/Japanese interface claims.
- [USDA API/source rights](https://fdc.nal.usda.gov/api-guide/): bulk CC0 downloads used, source editions preserved, no API key placed in frontend code.

Qualitative search observations, not measured demand:

| Query researched | Locale | Observed page types | GetMacros implementation | Overlap/maintenance |
|---|---|---|---|---|
| cooked chicken protein 100g; raw cooked rice calories; olive oil tablespoon nutrition | Not explicitly pinned; English search | Food composition entries and portion explanations | A source-profile search, source-supported measures and actual weighed examples added to the existing raw/cooked guide | Existing guide retained; historical USDA entries clearly labeled; import version recorded |
| Subway UK New Zealand ingredients sandwich nutrition comparison | English; country words in query | Country calculators and menu tables | Country-specific official UK/ROI September 2026 and New Zealand October 2025 recipe snapshots, plus ingredient comparison | Not an equal-weight or current-availability claim; refresh when official documents change |
| carnivore diet study; DASH diet evidence | English | Primary survey, government research background and opinion material | One evidence-reading guide distinguishes designs and definitions | No parallel thin diet pages; no clinician review claimed |
| Nutrition Made Simple official channel; food/nutrition books and documentaries | English | Creator/channel and publisher material | Publisher-verified cooking book, official NOVA archive and NHLBI resource shelf | Creator recommendation withheld pending adequate source practice review; streaming status stated |

Observed competitor pages: [subwaymacros UK ingredient page](https://www.subwaymacros.com/uk/ingredients), [SubMacros UK](https://submacros.co.uk/), and [Subway Nutrition Calculator New Zealand](https://subwaynutritioncalculator.org/new-zealand/). These were qualitative search-result observations. No competitor nutrient values were imported. One NZ-labeled result describes a shared U.S. catalog; GetMacros uses actual New Zealand recipe data instead. This observation is not a traffic estimate or a quality verdict on every competitor feature.

Implemented titles/descriptions identify market, portions and scope. Country tables and initial results are rendered into HTML; source links remain crawlable. Private diary/offline pages use noindex and are excluded from sitemap/search resources. Search previews are deduplicated and exclude non-indexable destinations. The general food search does not create indexable URLs for 13,578 profiles. Existing U.S. routes, verification files and paused advertising remain preserved.

Provider documentation inspected: [images](https://developers.openai.com/api/docs/guides/images-vision), [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [transcription](https://developers.openai.com/api/docs/guides/speech-to-text), [data controls](https://developers.openai.com/api/docs/guides/your-data). A real adapter is implemented but provider recognition, cost and language evaluation remain unperformed without credentials.
