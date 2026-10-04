# Verified U.S. restaurant expansion

## Actual scope

380 additional orders across 10 new chains: Arby’s 53, SONIC 47, QDOBA 14,
El Pollo Loco 27, Del Taco 60, Noodles & Company 22, Culver’s 23, Taco John’s 122,
In-N-Out 9, Raising Cane’s 3. There are 378 published-order rows and 2 calculated
individual-portion orders. Ten new rows lack an exact fiber value and deliberately
keep it null. After integration with the existing 83 records, the dataset has 463
orders across 25 chains, with 15 records lacking at least one exact supported
nutrient if the original 5 incomplete records are unchanged.

These are useful recorded orders, not a promise that all are in stock or that a
single taco is a full lunch. Larger ordinary serving-size duplicates, stand-alone
add-ons, drinks and desserts were excluded from this expansion.

## Apply explicitly; safe to repeat

Run `python tools/build_restaurant_expansion.py` to regenerate private artifacts.
Run `python tools/build_restaurant_expansion.py --apply` when the release build is
ready to append its known records, merge the authoritative review source and
install its 10 guide pages. This command preserves unrelated meal/review rows.
Run `python tools/restaurant_release/test_expansion.py` for integration tests.

The adapter uses the existing meal schema: `f` is **fiber**, not fat. Fat lives
in provenance. Meal-time values are `main`/`breakfast`. Dietary labels stay empty
because the official nutrition rows do not establish a dietary or allergen-safety
classification. Appetite/size classification is omitted: a recorded portion’s
weight does not establish small/medium/large appetite suitability.

## Required root integration

1. Invoke `--apply` **before** `apply_audited_data.py` / finder generation so all
   counts and derived tags use the complete list. The pure function
   `append_meals(source_text)` is available for a pipeline that already owns the
   source writes; `merge_review(existing_rows)` is its review counterpart.
2. In `rebuild_publication.py`, after the existing legacy/specific provenance
   patches and **immediately before** `pack(metadata)`, add:

   ```python
   from build_restaurant_expansion import metadata_overrides
   metadata.update(metadata_overrides())
   ```

   Existing generic provenance initialization loses fat, portions, edition dates
   and nutrient bounds. This final merge restores the new records’ complete
   provenance. It must not run only after a finder snapshot has been rendered.
3. Add all payload `chains[].chain`/`route` mappings to root restaurant identity
   and guide-index generators. The exact routes are in `expansion-payload.json`.
   The generator copies the current shared header/footer/template presentation,
   replaces the entire guide body, and writes unique metadata. A root-wide header
   or theme update should run over these pages too, or regenerate them from the
   updated template.
4. Build all count-bearing snapshots, finder options, search indexes, restaurant
   navigation and sources after data integration. No hardcoded 83/15 credibility
   number should remain. Do not restore the previous snapshot during a later build.
5. Add all 10 guide URLs to sitemap/coverage and run the release render/overflow
   checks. Generated guide tables have an explicit scroll region and collapse the
   full-menu table initially. **No guide browser QA is claimed by this generator.**

## What the evidence means

`expansion-payload.json` contains source URL, actual row text, page, serving,
printed edition where established, nutrient methods and retrieval date per order.
`sources/retrieval-log.json` records HTTP outcome, resolved URL, bytes and SHA-256.
The downloaded official PDF snapshots and row text are retained privately under
tools and are not hotlinked public artwork. These PDF rights do not grant rights
to reuse restaurant photographs or logos.

In-N-Out’s linked January 2026 PDF was inspected through the web tool; the direct
local download returned a challenge. No local PDF snapshot is claimed. The local
challenge HTML must never be treated as source nutrition evidence.

Culver’s uses the official July 2025 PDF edition. Its current live page links a
Nutritionix guide; do not claim the older PDF is a newly verified 2026 recipe.
SONIC’s linked filename says September 2026 but its printed cover says Summer 2026.
QDOBA’s printed title establishes 2026, not a full September 1 date. Noodles and
Taco John’s exact printed edition dates were not established; null is intentional.

The PDF header/row-layout screenshots, other inspected row screenshots and text
are source-validation evidence. They are not screenshots of GetMacros’s final
rendered guide pages and do not establish accessibility or browser performance.

## Exclusions

- QDOBA’s Quesabirria Burrito/Quesadilla show 95/127 g fat, inconsistent with their
  calories. These rows were visually checked and excluded, not silently corrected.
- Taco John’s Beef Fiesta Rice Bowl shows 100 g fiber with 76 g carbohydrate. Excluded.
- Raising Cane’s published combo totals differ from sums of individual portions.
  The 2 calculated builds explicitly name those individual portions; neither is
  labeled as the official combo. Less-than 1 g fiber propagates to unknown total.
- Jimmy John’s official page returned a script shell; Potbelly and Shake Shack
  direct official data retrieval was blocked. No unofficial substitute was used.

The source audit is retrieval/transcription, not a kitchen test, local availability
survey, price survey or allergen assessment. Restaurant nutrient values are rounded;
they should not be replaced with macro-derived calorie estimates.

## Research snapshots and reproducible builds

The committed factual payload retains official URLs, source editions, source rows/pages, inspection notes and source hashes. Full restaurant PDFs, extracted layouts and screenshots are private research artifacts, not redistributed assets. Ordinary builds validate the curated records and verify every locally available PDF hash; the report explicitly lists unavailable snapshots. Reinspection requires obtaining the official snapshots, then calling `validate(require_source_snapshots=True)`. A successful build without those files does not mean the PDFs were re-inspected. In-N-Out was inspected through the official web/PDF reference and retains that limitation.
