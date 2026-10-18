# Independent menu-data audit — 18 October 2026

The final staged batch passes the implemented integrity checks with **0 blocking errors and 37 explicitly retained review warnings**. This does not establish that every menu, recipe or restaurant is complete, or that all official source figures are chemically accurate.

## Inputs and actual coverage

| Input | Additions | Refreshes | Country–chain groups |
|---|---:|---:|---:|
| `tools/flagship_release/uk_records.json` | 4,736 | 0 | 17 |
| `tools/flagship_release/markets_release_records.json` | 1,971 | 135 | 12 |
| Total | **6,707** | **135** | **29** |

The 1,971 other-market additions contain **1,967 source portions and four calculated complete orders**. These are portions/configurations, not 6,707 different restaurant chains, whole meals or new public pages. The refreshes preserve proven existing U.S. record identities.

The audit checked 86 registered source capture files against their SHA-256 hashes. It also independently read and transcribed **58 original-source portions: two for every country–chain group**. This used official PDF text, original HTML and raw official JSON. It was not a screenshot review or laboratory test. The checks did not merely compare the ingestion export with itself.

Exact source URLs, original capture paths and hashes, row/page locators, hand-transcribed expected values, country and portion notes are in [source-spot-checks.json](source-spot-checks.json). PDF layout text independently extracted with pypdf is retained in `source-text/`; ingestion used different table extraction. Official JSON/HTML samples were read directly from the registered captures.

## What the audit tests

- Finite, nonnegative numeric values; boolean values rejected; explicit published zero retained; unknown remains null.
- Normalized kcal/g/mg units, market identity, country-specific restaurant identities and country-safe component references.
- Presence of exact serving definitions, nutrient provenance, HTTPS source URLs, source locations, retrieval dates and registered capture hashes.
- Core-macro completeness reflects known calories, protein, carbohydrate and fat; finder support requires known calories and protein.
- Sugar versus carbohydrate and saturated versus total fat; serving mass and macro-mass bounds; unusually large energy/sodium portions.
- Native per-100g conversions, salt-g to sodium-mg, sodium-g to mg, and explicitly calculated kJ to kcal using Decimal arithmetic.
- Calculated-order sums and propagation of unknown component nutrients.
- Duplicate IDs and duplicate named servings; no duplicate-named-serving warnings remain in the final batch.
- Replay of all 58 independently transcribed original-source samples, including capture-hash stability and two-per-group coverage.

Conversion tolerances are explicit: 0.051 g/kcal for rounded per-100g arithmetic, 1.01 mg for salt/sodium arithmetic, 0.011 kcal for kJ conversions and source-sample replay, and 0.051 for summed order nutrients. A source child nutrient exceeding its parent by more than 0.5 g is blocking; smaller source-reported discrepancies remain warnings rather than being invented away.

## Source mistakes and ambiguous records caught before integration

Findings were sent directly to the data owners and checked again after their fixes. They withdrew 11 UK records and five other-market records, including major source contradictions, unsupported zero-weight allocations and ambiguous French child-product pairs. Their source-specific disposition files retain the reasons. Examples include Nando’s Gatwick baked beans reporting saturated fat above total fat; LEON oat-milk mocha sugar above carbohydrate; Five Guys M&M shake contradictions; a Tim Hortons drink saturated-fat contradiction; and a New Zealand Domino’s mousse sugar/carbohydrate contradiction.

Three LEON source-reported zero masses became unknown mass, with the original zero retained as source evidence. Variable pick-and-mix bundles were withheld rather than published as zero-calorie meals. PizzaExpress same-name extras now distinguish the airport-breakfast allocation from a pizza topping. India Domino’s Pizza Mania variants retain their category identity. French child-menu products retain their distinct source context.

The Canadian Buddy Fruits pouch has conflicting official masses: 100 g in the nutrition table and 90 g in the product description. The record keeps unknown normalized mass and the explicit conflict; it must not be scaled by either mass or used in the withheld fruit complete order. The exact fry-based orders remain supported.

The shared registry contained none of the 16 withdrawn IDs when checked after the corrected handoff. Integration must continue honoring both batches’ `withdrawnIds`.

## Important source distinctions checked

- Chick-fil-A UK serving nutrients are computed from the source per-100g values and printed gram portions; Singapore, Canada and U.S. recipes remain separate.
- Wasabi uses its published serving calories while scaling its other per-100g nutrients by the printed mass. Rounded per-100g calories do not overwrite published serving calories.
- Wagamama’s native sodium in grams is converted directly to mg; its separately rounded salt is not used to overwrite sodium.
- Hungry Jack’s per-serving kJ is converted to kcal; the adjacent per-100g column is not substituted.
- Domino’s Australia/New Zealand sampled pizza records are one of eight slices, while the sampled Indian configuration records are whole source variants.
- Zizzi Ireland’s sampled portions differ from Zizzi UK and retain their local source figures.
- Chipotle Canada’s taco-tortilla fibre is reported as less than 1 g; the normalized value remains unknown, not zero.
- Tim Hortons’ source title mentioning UK and Ireland is not used as evidence to publish the UK records in Ireland.
- Nando’s Northern Ireland and airport variants, PizzaExpress England/Wales/Scotland scope, and component-versus-complete-order distinctions remain explicit.

## Warnings that remain

| Review warning | Count | Disposition |
|---|---:|---|
| Sugar slightly above carbohydrate | 3 | Source values retained; difference no more than 0.5 g. |
| Saturated fat slightly above fat | 24 | Source values retained; difference no more than 0.5 g. |
| More than 5,000 kcal | 6 | Explicit large bundle, sharing or whole-cake portions; not individual meal recommendations. |
| More than 20,000 mg sodium | 1 | U.S. large Mac & Cheese catering tray; source scope preserved. |
| Large 4/4/9 energy difference | 3 | Canadian beer/margarita source records; alcohol energy omitted by the crude macro screen. They are excluded from the meal finder. |

These are not a reason to rewrite official numbers to appear cleaner. The warnings, exact IDs and values remain in [audit.json](audit.json); downstream presentation should preserve source notes and appropriate scope.

## Reproduce

Run from the repository root:

```powershell
& 'C:/Users/slowf/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 tools/flagship_release/data_audit.py
```

Final result: exit **0**, 6,842 rows checked, 58 sampled source portions, 86 capture files, 0 blocking errors, 37 warnings. [self-tests.json](self-tests.json) records rejection fixtures for invalid/nonfinite values, wrong units, conversion mistakes, missing provenance, changed hashes, invalid mass, future source dates, wrong sums, cross-market components and unknown totals. A valid fixture and explicit zero are accepted.

Final input hashes:

```text
uk_records.json
f3a1e8cf32e18e6cfab72583bea8defc60d75caebe0bb66713c5a3dbe630cf01

markets_release_records.json
3da718ebf687a720ee01de26b8f56d3c6fa506884d31a0e247d9b8a66ea08cc1
```

## Limits

This audit edited no shared nutrition records or website templates. Browser rendering, image rights, comprehensive full-menu completeness, final production integration, ingredient equivalence and every-row manual source verification remain separate checks. Original source mistakes can still exist outside the sampled rows. Retrieval and arithmetic checks do not confer a medical endorsement, allergy guarantee, full-menu claim or real-time availability claim. No deployment or indexing was performed by this audit.
