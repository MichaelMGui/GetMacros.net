# Restaurant integration review

Reviewed the late integration generator, pinned records, published registry,
Canadian data adapter, presence matrix, country directories and world index.
The output checks are read-only and must run after the final build/stamp finishes,
because earlier generators deliberately rebuild the base registry first.

## Corrections identified during review

- The initial finder and coverage predicates excluded components but included
  sauces lacking an explicit finderSupported field. The generator now excludes
  both categories. Four inherited Canadian sauces no longer appear as meals.
- The initial calorie-only counter used any missing macro. It now requires all
  three macro fields to be unknown and keeps partially reported macro records
  separate from calorie-only records.
- The first guide wording could imply identical extra amounts for all order
  sizes. It now spells out one snack extra, two regular extras and three large
  extras, applying the rule only to that ingredient.
- The world directory is derived from actual country registry rows rather than
  the older three-chain Canadian definition. It includes every tracked chain,
  including Pizza Nova's honest calorie-only selection and New York Fries.

## Source-unit and logging boundary

The restaurant food adapter now reads additionalNutrients only when its source
unit agrees with the food arithmetic unit. A value in grams does not silently
become milligrams. The boundary retains explicit zero, rejects unknown/negative
values, and does not infer a conversion from an unmatched unit.

test_restaurant_adapter.cjs passed 35 assertions over the real Canadian fries
profile and explicit unit-boundary cases: mg, micrograms, zero, missing values,
unsupported unit mismatch, source-supported grams/servings, immutable source
snapshots, source edition/retrieval dates and country-separated search. The
artificial boundary cases are tests only, not imported restaurant records.

## Output verification

test_integration.py has ten checks covering:

1. Each of the 27 reviewed additions appears exactly once with unchanged facts.
2. Canadian source and finder outputs contain only Canadian records; sauces,
   components and unsupported Pizza Nova macros do not enter the meal finder.
3. Every presence counter agrees with actual country and chain rows.
4. The 17 new operational entries do not acquire fabricated nutrition.
5. New York Fries has 27 complete records, 19 finder entries and two calculated
   orders with its current official source.
6. Every world-directory country names all of its tracked chains and accurate
   record/finder counts.
7. Local directory links preserve country-specific operations and unavailable
   nutrition disclosures.
8. The new guide contains all named portions, source dates, arithmetic and the
   correct extra rules; canonical, sitemap and search entries exist.
9. The Canadian chain definition comes from actual usable finder records.
10. The 35 food-adapter boundary cases pass.

An initial run happened while base generators were replacing registry, finder,
directory and sitemap outputs; it failed against that mixed intermediate state.
That attempt is not a finished-build result. After the completed build and late
integration corrections, all ten output checks passed on October 13, 2026. The
35 adapter checks were included and passed again. The final integrated registry
contains 1,709 restaurant records, including 383 Canadian records and 281
Canadian finder entries; the presence matrix contains 74 country–chain
relationships. These counts include earlier releases and are not all new records.

No visual/browser or production deployment is claimed by these source/output
checks. Root release QA owns the finished rendered screens and live checks.
