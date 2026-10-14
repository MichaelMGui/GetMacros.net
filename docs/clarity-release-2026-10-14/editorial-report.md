# Implemented editorial release — October 14, 2026

## Candidate implementation

Eleven distinct new articles and ten substantial additions at established URLs are implemented by `tools/clarity_release/editorial.py`. The generator is late and idempotent; it does not modify the restaurant registry, nutrition records, shared presentation, search, sitemap or article index. Root owns final index integration, shared presentation, deployment and live verification. These are release-candidate articles until those gates are completed; this report does not call them live.

The new batch covers named Canadian coffee/burger/poutine/chicken-side/pizza decisions, UK Greggs item/pack arithmetic, Australian GYG builds, Mexican Subway chicken recipes, a Canada–Mexico sandwich comparison, actual Canadian Kirkland nut portions and an original eight-market coverage analysis. Each has a direct first answer, explicit country/serving/source boundaries, useful calculations or differences and real next-action links. There is no hypothetical page-per-keyword expansion.

The ten established pages gain concrete recipe/label examples, a genuine complete-order example, source-version behavior, measured-volume distinctions, native energy rounding and calculator arithmetic. Existing publication dates and source editions remain intact. Each new worked section has its own addition date instead of overwriting the old review date.

`editorial-manifest.json` and `editorial-pages.csv` list every new purpose and route; `editorial-backlog.json` distinguishes implemented articles from improved pages, merged candidates and blocked topics. No removed route or redirect is required. No outline, topic list, table row or metadata-only change counts as a published new article.

## Copy and composition changes

- One exact comparison action appears immediately after the new article's first answer; it is not duplicated at the bottom.
- Article headings have no redundant subtitle repeating the answer. Breadcrumbs use a concise cluster and Learn link rather than echoing the full long title.
- Table serving definitions occupy a separate block below the food name, with full readable country names.
- Source tables are keyboard-focusable horizontal scroll regions; the existing scroll cue is present. Calories/protein relevant to the question are also visible in the answer text.
- Retailer source links identify the specific product, avoiding two indistinguishable “Kirkland source” links.
- Where a real example is added, an old blanket disclosure that every figure was invented is corrected to distinguish labelled hypothetical examples from separately sourced facts.
- The saved-meal guide clarifies that a new matching source does not automatically replace historical diary snapshots.
- The redundant logging-guide subtitle is removed. Necessary source, hypothetical-example, privacy and accessibility disclosures are retained.

## Audit and factual work

The baseline source-only audit extracted 350 public routes and 183 article-family candidates. It found 119 exact repeated-paragraph groups and no near-identical substantive introductions at the documented 0.72 threshold. Most high-frequency groups are necessary shared example/source or game-accessibility disclosures, so they were not blindly deleted. Relevant existing sections were read before the eleven distinct purposes and ten additions were selected. This is not a claim that all 350 pages were manually visually reviewed.

The article facts manifest contains 41 exact source-record inputs. No new restaurant or grocery values were invented or imported. Current official Harvey’s and Canadian Costco pages were inspected. Current Tim Hortons and New York Fries PDFs were downloaded; selected Tim Hortons rows were extracted and New York Fries bytes match the previous visually reviewed source. Current Canadian Subway PDF retrieval timed out, so its retained June edition remains labelled and no new source date or October recipe was inferred from search snippets.

The audit found a real Mexico Subway component presented as a full sandwich. Root corrected the source normalizer; the editorial comparison uses the true 205 g, 270 kcal, 15 g protein complete-sub identity and explicitly tests it.

No clinical, dietitian, kitchen, taste-test or physical-package review is claimed. No country comparison is treated as an isolated ingredient test, allergy guarantee, national-diet ranking or automatic healthy winner.

## SEO research actually performed

Five requested current Google documentation pages were opened and focused guidance read. Two official Search Central office-hours transcripts were read for relevant questions; archive dates are recorded. One SEO Made Easy video description was reviewed, but the video/transcript was not available through that initial watch-page request, so no watch claim is made. Root may append a separate actual transcript review if obtained later.

Qualitative query and search-result observations feed the concrete page map. Exact current Search Console/analytics data, keyword volumes and competitor traffic are unavailable. No traffic forecast or ranking promise is made. Full sources and applied decisions are in `editorial-research.md`.

## Verification checkpoint

`python tools/clarity_release/test_editorial.py`: **13 tests pass**. They check fixed official facts, whole-order sums, unknown nutrient propagation, actual branded portions, source-reported pack rounding, native energy, calculator arithmetic, genuine cross-market source identities, source dates, comparison deep links, content purpose, coverage denominators, static metadata and generator idempotence.

Initial browser verification rendered all 21 changed pages at 320, 390, 768, 1280 and 1440 CSS pixels in both themes: **210 actual render states passed**. Twenty screenshots were captured. Australia desktop, Kirkland dark mobile and Tim Hortons light mobile were manually opened. The serving-label run-together issue found there was corrected using block `.table-portion` markup and full country names.

During the final browser rerun, the updated shared navigation caused a 320 px header overflow (335 px document width), reported to root for its shared-header fix. Native article-to-comparison checks also exposed a fresh-load restaurant lookup cache bug in `food-library.js`, reported to root. These are real integration findings; the initial passing renders are not presented as final passing release checks. Final rerun results and screenshot review will be appended after those shared fixes.

Browser tools:

```text
node tools/clarity_release/editorial-browser.cjs
node tools/clarity_release/editorial-link-journeys.cjs
```

Screenshots: `docs/clarity-release-2026-10-14/editorial-screenshots/`.

## Exact integration and remaining limits

Run the owned generator after global/master completion/diary generators and before the final shared interface, search and asset stamp. Add only the eleven new manifest routes to the approved public allowlist, article index, search and sitemap. Preserve established URLs; use Article/BreadcrumbList only as represented by the visible page. Do not invent hreflang equivalence between unrelated comparisons.

The private `editorial-source-evidence/` directory contains source PDFs and extraction evidence; it is not a public asset collection and must not be published. No source imagery is reproduced.

Open source gaps: current Canadian Subway edition confirmation; unsupported coffee customizations; full Pizza Nova macros; current retailer inventory; reviewed French text; clinical claims outside this release's scope. These are explicitly deferred, not counted as implemented content.

Deployment: pending root's authorized workflow and live verification at this checkpoint.

## Final integrated candidate checks

After root fixed and stamped the shared 320 px navigation and fresh-load restaurant cache, the read-only final browser run passed **210 render states** across all 21 changed article routes, five widths and both themes. All responses were 200, one H1 per page, no document overflow, contained source-table regions and no runtime errors. Evidence: `editorial-screenshots/checks.json`.

The separate native integration run passed **six article → comparison journeys** in fresh browser contexts, covering medium Tim Hortons Latte/Protein Latte, actual Canada/Mexico Turkey Breast identities and exact Canadian Kirkland labels at 100 g, each in both themes. Links retained two public source identities, the intended basis and no private notes. Evidence: `editorial-link-journeys.json` and six actual comparison screenshots.

Five final screenshots were manually opened: Tim Hortons light mobile, Kirkland dark mobile, GYG light desktop, Canada–Mexico comparison light mobile and Kirkland comparison dark mobile. The remaining route states were automated browser renders; no broader manual-inspection claim is made. Final article Save-guide controls, shared navigation, table serving blocks and single early comparison CTA are visibly present.

Two minor comparison copy findings were reported to root: duplicated quantity 1 before an already one-serving source label, and raw source-status enums in ordinary copy. These are presentation findings, not changed nutrient calculations. Root owns their final wording and any resulting shared-component verification.

The idempotence gate now runs in a tiny isolated fixture with ROOT/OUT restored in finally. It never overwrites root’s integrated HTML, source snapshots, final statuses, Save controls or asset stamps. All **13 owned tests pass** with this isolation.

Deployment and production URL verification remain root’s responsibility; no local candidate screenshot is represented as a production result.
