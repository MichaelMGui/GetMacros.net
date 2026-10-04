# Editorial release: evidence and limits

Research and writing date: October 4, 2026. This file documents the new articles, not a re-review date for old content or a claim of medical expert review.

## What was implemented

117 new, individually authored articles in `tools/editorial_release/articles.json`, generated into their existing-style public HTML shell by `tools/build_editorial_release.py`. Existing 73 articles and the previous 33 release resources are excluded from this count. The manifest records each new reader question, original utility, category, source count, word count and release-candidate state. About 32,000 authored body/table words are present; word count is a diagnostic, not the definition of quality.

46 articles use exact restaurant records, with 133 cited record occurrences checked against the versioned official-source payload. Five dataset articles perform explicit snapshot calculations. Other articles teach distinct label, portion, protein, fiber, cost, recipe and calculator decisions using clearly labeled invented examples. They do not invent prices, tested recipes, nutrition prescriptions or allergen certifications.

## Sources actually inspected

FDA label, serving-size, calorie, Daily Value, added-sugar, sodium, menu-labeling and food-allergy pages were opened with the web tool and their relevant body content read. USDA FoodData Central and Foundation Foods documentation were inspected for data types, food descriptions, edible portion, missing values and analytical variation. NIST mass, volume, Metric Kitchen, SI prefixes and conversion-factor guidance were opened for compatible measurement units and explicit conversion factors.

The per-source URL registry is `tools/editorial_release/sources.json`; article citations specify their supported purpose rather than implying the source tested our example arithmetic. The thermochemical energy conversion is specifically 4.184 kJ per kcal. Avoirdupois units are distinguished from fluid volume. Milli and micro are checked against the NIST prefix table.

Official U.S. restaurant PDFs were downloaded and inspected by the data verifier; the editorial work read the relevant extracted rows and headings for the values used, with source rows, pages, exact portions and limitations retained in article facts. Sources cover Arby’s, Del Taco, SONIC, Culver’s, Taco John’s, QDOBA, El Pollo Loco, Noodles & Company, In-N-Out and Raising Cane’s. The live In-N-Out PDF was also opened with the web tool and all nine burger rows inspected. Its local PDF snapshot is not claimed.

The restaurant-source directory is `tools/restaurant_release/sources/`, and the versioned factual payload is `tools/restaurant_release/expansion-payload.json`. A retrieval in October 2026 does not update the printed edition: notably Culver’s remains July 2025; Arby’s filename and edition disagree; SONIC’s filename and cover do not establish a precise edition date. Both discrepancy articles and public source notes preserve those limits.

## Specific checks and corrections

* Every new route, title, reader-intent string and body hash is distinct against the recorded baseline inventory.
* 292 arithmetic examples are recomputed using a restricted expression parser. No invented shopping prices are represented as current menu prices.
* 133 referenced restaurant rows match the payload’s six nutrient fields, exact serving, source page and source row.
* Snapshot counts are rechecked: 380 records, ten chains, 48 breakfast records, ten non-exact fiber rows, 378 directly published orders and two component-calculated orders. The nine In-N-Out records are three base burger names with three supported variations each.
* No exact authored paragraph of ten or more words repeats. No pair of whole bodies crosses the text-similarity gate. Shared navigation, measurement labels and legitimate source disclosures are excluded from this prose check.
* The intent review compares new questions against existing titles in `existing-intent-review.json`. Similar characters in titles are a review aid, not semantic evidence. The four highest automated title matches were read; they address different tasks: ranges versus missing fields, fiber reference scaling versus missing restaurant data, reversing an energy calculation versus recipe scaling, and receipt-based value versus daily calorie allocation. Two drafts were rejected during the broader intent review: privacy in calculator handoff duplicated an earlier resource, and usable-yield break-even was too close to an earlier food-waste article. They were replaced by compound feet/inches height input and price-interval robustness articles; they do not count toward 117.
* Official rows are not reverse-engineered into ingredients. Extra sides and drinks remain excluded unless explicitly named. El Pollo Loco dressing exclusions, Culver’s dinner footnotes, Taco John’s less-than fiber values, and calculated Cane’s tray boundaries remain visible.
* Unknown exact fiber is never converted to zero. Protein minimums and calorie/sodium maxima in worked comparisons are examples, not personal recommendations.

## Publication and visual limits

The generated articles are release candidates pending the parent task’s site-wide presentation, index/search/sitemap integration, browser review and release decision. This editorial subtask did not deploy, edit DNS or submit an AdSense review. No approval or traffic guarantee is claimed.

The article shell includes one main heading, page-specific metadata/canonical, honest organizational authorship, source notes, internal tool links, an expandable contents list and scrollable labeled tables. The editorial regression verifies generated copy retention and template structure. It does not constitute screen-reader certification, visual inspection of all 117 pages, laboratory food verification, medical expert review or field-performance measurement. Those distinctions remain explicit in the manifest.

Independent browser capture exercised 13 topic representatives in light/dark at 390/1440 px (52 route/theme/viewport combinations), using Edge via the repository’s asset-interception fixture. The final matrix passed all 52 combinations after the parent's generated-CSS build. It found no page overflow, JavaScript exceptions, missing images or repeated main/headings. Top and table contact sheets were visually inspected. Mobile eight-column nutrition tables were found to compress serving descriptions into unnecessarily tall rows. The first table-width correction made these wide tables readable scroll regions, but also forced compact two-column tables to scroll. The parent narrowed the rule to tables with four or more columns. Final checks now require compact two-column tables to fit their region and wide mobile tables to retain at least 700px of readable width. The final dataset table was visually inspected in both themes at 390px: chain names and counts fit together. Final restaurant comparison tables were inspected in both themes at 390px and on desktop; these retain horizontal scroll access to the remaining nutrient columns. The budget comparison's mobile table was also inspected. Do not mistake a passing overflow test alone for visual approval. Screenshots and raw browser results are under this directory; they describe repository assets, not live hosting or field performance.

## Reproduction

1. `python -X utf8 tools/editorial_release/author_batch_six.py` regenerates the five individually authored batches plus the two intent-review replacements and the source registry.
2. `python -X utf8 tools/build_editorial_release.py` emits the checked article routes and private integration manifest without changing public indexes.
3. `python -X utf8 tools/test-editorial-release.py` checks uniqueness, source registration, arithmetic, source-defined facts, snapshot calculations, internal references, retained body copy and generated main/canonical structure.

The parent release build must run the article generator before the shared presentation and indexing passes so the new routes inherit the final theme, navigation and saved-article controls.
