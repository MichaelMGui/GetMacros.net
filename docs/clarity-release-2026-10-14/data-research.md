# Reviewed restaurant expansion — October 14, 2026

This subtask adds one useful Canadian chain through pinned, individually reviewed
facts. It does not import a third-party restaurant database, rewrite inherited
nutrition, duplicate the grocery catalogue, or change the shared application.
The root release integrates the record payload, guide and market counts.

## What is implemented

`tools/clarity_release/restaurant_facts.json` contains 37 individually curated
named Canadian Triple O’s servings. `restaurant_ingest.py` creates 40 stable
records: those 37 official servings and three explicitly calculated orders.
Three of the official records are named dip/gravy portions and are excluded from
finder results. Thus 37 records support the finder. Every new record preserves
country, native grams, source edition, retrieval, review, hash, numerical units
and per-field provenance. No unreported ingredients, prices, dietary labels,
allergen guarantees or absolute micronutrient values are invented.

The source hierarchy is: current official local nutrition evidence first;
component sums from that evidence second; legitimately licensed food datasets
remain distinct reference/product sources. Search snippets and community tables
help locate questions, but are not nutrition evidence for these records.

## Source and operating presence

The live [official menu](https://www.tripleos.com/menus/) currently links this
[nutrition guide](https://diqidopw2893b.cloudfront.net/2025/07/02144402/Nutrition-June-2025.pdf).
The PDF downloaded successfully, both pages were rendered with Poppler and
actually read, and both print the June 2025 edition. The source does not provide
an exact day: `sourceDate` is `2025-06`, with month precision. October 14, 2026 is
the retrieval and review date, not a fabricated new nutrition edition.

SHA-256: `68487fd23a5851c2ec5110d0192475bf91cb4168e270519910747f820cbc066e`.

The expanded [official locator](https://www.tripleos.com/locations/) rendered
Alberta, British Columbia and Ontario locations. The local operator is White
Spot Limited. The Canadian main-site menu links this guide; the site separately
links its Asia operations. No equivalence to overseas menus is asserted. Venue
and airport menus can differ. The new presence entry makes operating presence,
available nutrition evidence and implemented finder coverage separate fields.

The current [Legal & Privacy page](https://www.tripleos.com/legal-privacy/) was
read in the actual browser. It addresses personal-information practices and does
not state an explicit commercial harvesting/database restriction. This is not a
legal opinion, a whole-catalogue reuse license or an endorsement. Only selected
item identities, serving definitions and factual quantities are distributed.
The source PDF, its artwork, arrangement, text, logo and browser dumps remain
private research evidence and must not be hosted or committed with the release.

## Useful differences preserved

- Standard and source-listed Without Sauce builds retain separate identities,
  native gram weights and reported values. No guessed sauce subtraction is used.
- Chicken Bacon Cheddar is 791 kcal and 44 g protein in its standard row; its
  published Without Sauce row is 567 kcal and 44 g protein. The source-labelled
  builds must not be reversed by a table parser.
- The current guide specifies five hashbrown pieces at 70 g. Older indexed
  guides label that weight as one piece. The edition and exact new count remain
  visible rather than silently mixing portions from different years.
- Named fries portions retain their own source grams and values. They are not
  scaled from the ounce label. Drinks retain their printed size name alongside
  native grams; there is no guessed fluid-ounce density.
- Dippin’ Chicken, fish and chips, and dips remain separate where the source
  presents separate rows. The fish-and-chips serving already contains fries.
- Source percentages for vitamins/minerals are not translated into assumed
  absolute quantities or daily values.

Three calculated orders give concrete complete-order utility:

| Explicit source portions | Calories | Protein |
| --- | ---: | ---: |
| Bacon Sunny Start Without Sauce + five-piece hashbrown | 611 kcal | 24.7 g |
| Chicken Bacon Cheddar Without Sauce + regular fries | 806 kcal | 47.5 g |
| Five-piece Dippin’ Chicken + regular fries + 45 g Honey Mustard | 914 kcal | 38.5 g |

These are GetMacros sums, not separately tested or published restaurant combos.
Each component and quantity is retained. Drinks and unlisted extras are excluded.
An unknown component nutrient leaves that order nutrient unknown.

## Contradictions withheld

The guide contains questionable rows. We did not repair them with guessed
values. Cajun Fries, the two Impossible Burger builds, four regular-size shakes
and the regular Frappuccino are withheld. Their printed calorie values differ
materially from their listed macros. The importer gates large contradictions;
this check does not treat the simple 4/4/9 formula as a precise replacement for
official energy calculations or rounding. Withheld identities/reasons stay in
the fact fixture and release payload for a later source clarification.

## Other Canadian candidates actually checked

| Chain | Observed official source | Disposition |
| --- | --- | --- |
| Dairy Queen | [Canadian food/treats table](https://www.dairyqueen.com/en-ca/nutrition/food-treats/) is readable through web research, with a printed February 26, 2026 date. | Native browser nutrition and legal pages were blocked. Several displayed rows contain clear numerical inconsistencies; no import or hidden correction. |
| Taco Bell | The rendered [Canadian support page](https://www.tacobell.ca/en/Customer-Care) links a country-specific Nutritionix resource. | [Canadian terms](https://www.tacobell.ca/en/Terms-&-Conditions) restrict reuse/republication without consent. No database extraction or permissions request performed. |
| Mucho Burrito | The actual [Canadian calculator](https://muchoburrito.com/nutrition/) renders choices and named builds. | [Legal page](https://muchoburrito.com/legal/) restricts copying without prior written consent. No menu ingestion; no claim that UI availability is reuse authorization. |
| Osmow’s | Current [terms](https://osmows.com/terms-of-service) expressly address commercial use and entry into a database. | Withheld pending appropriate authorization. Historical third-party/Quebec PDFs are not a replacement permission source. |
| Quesada | The current [Canadian nutrition PDF](https://quesada.ca/wp-content/uploads/2026/08/Nutritional-Information_Quesada_regular-portions_AUG2026_EN.pdf) is readable through web research. Its current ordering configuration links Pita Pit terms. | Retrieval alone does not resolve that terms relationship. Keep the prior pending status; do not fabricate new servings or treat current access as unrestricted reuse. |
| Freshslice | [Nutrition page](https://freshslice.com/nutritional-info/) primarily renders an allergen/ingredient table and a June 2026 update statement. | That table alone does not establish exact calorie/macro servings. No inferred nutrition records. |
| Edo Japan | The official nutrition endpoint was attempted but returned an empty rendered document. | The older Scribd copy is not current official evidence. No import. |

These are source/rights observations, not legal determinations and not assertions
that the chains do not supply nutrition. They remain useful research queues.
No outreach, account creation, purchase or permissions request was sent.

## Search intent actually researched

On October 14 the following queries were searched: “Triple O's Canada chicken
bacon cheddar without sauce nutrition,” “Triple O's breakfast sunny start bacon
calories hashbrown,” and “Triple O's iced coffee 12 oz 20 oz calories Canada.” The
search tool did not provide a fixed search locale or keyword demand metrics.

Results include old official PDFs, calorie trackers and a current competitor
table. That competitor's Chicken Bacon Cheddar table reverses the standard and
without-sauce values; our source inspection retains the original row alignment.
This is a practical opportunity for the new guide: answer which build and portion
the person ordered, link the actual source edition, compare, and log it. It does
not establish search volume, ranking potential or projected traffic.

The guide descriptor in `restaurant_additions.json` uses the distinct route
`/ca/en/restaurants/triple-os/`, a direct action and useful breakfast, exact-order,
side and coffee sections. Root integration and browser verification are required
before calling that route published.

## Grocery coverage review

The existing Open Food Facts manifest has 96,451 community-label market profiles
across eight markets. Its distinct products, aliases, market postings, bounded
shards, null handling and licensing pipeline already exist. USDA, Canadian
Nutrient File and retailer observations remain separate sources. This subtask
adds **zero** grocery profiles: it does not repeat the prior import or count
metadata/plans as new food. None of these imported product counts prove current
store inventory or independently checked national packaging. Keep the existing
source-quality disclosures and dated label provenance.

## Verification and integration

Seventeen independent Python test cases pass for country isolation, pinned
source hash where the private PDF is available, exact sauce variants, native
units, named fries portions, source zeros, unknown propagation, invalid input,
calculated totals, dip eligibility, stable identities, source metadata and
reproducible output. Command:
`python -X utf8 tools/clarity_release/test_restaurant_additions.py`.

The importer itself only writes `restaurant_additions.json`. Root integration
must merge by stable ID, add its one presence relationship, recompute country
chains/counts, render the guide and finder, refresh shared search and sitemap,
and verify compare/log journeys. Expected totals after only this expansion:
1,749 registry records, 423 Canadian records, 318 Canadian finder entries,
75 presence relationships and 11 macro-supported Canadian chains. These are
integration expectations, not a claim that root has already published them.
