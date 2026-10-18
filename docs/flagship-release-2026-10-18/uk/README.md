# UK official-menu expansion handoff

Reviewed source snapshots on 18 October 2026. This is a **staged data handoff**, not a claim of deployment, whole-live-menu completeness, current stock, image rights, or App Store readiness.

## Delivered

- **4,736 named portions** across **17 additional UK-market chains**, representing **3,662 named source identities/recipes**. Sizes, milk recipes, regional allocations and ingredient portions are counted separately where the source distinguishes them. These are not 4,736 independent complete meals.
- 1,205 mains, 336 sides, 752 components, 333 desserts and 2,110 drinks. Component rows are excluded from whole-meal finder support.
- **Zero GetMacros-calculated composed orders** and **zero exact food photographs or cutouts** in this workstream. No rights to restaurant images were inferred.
- All **35 explicitly named UK candidates plus Chick-fil-A** have a disposition. Seventeen chains have new reviewed records, three existing chains are preserved, and sixteen have precise source-access, source-content or adapter gaps.
- **244 implemented source-category groups** are inventoried. This is reviewed selection coverage, not 244 claims of completed whole restaurant menus.
- **524 withheld rows/table groups**, including eleven audit withdrawals, are recorded. A withheld table group may represent several unresolved portions; it is not an exact count of missing products.
- The pre-release GB selection of **456 records** (Greggs 271, KFC 119, Subway 66) was preserved. Its older source verification dates were not refreshed merely because this release changed presentation.

| New UK chain | Named portions |
|---|---:|
| Nando’s | 270 |
| LEON | 148 |
| Wagamama | 193 |
| Wendy’s | 180 |
| Five Guys | 91 |
| Pepe’s | 131 |
| Starbucks | 1,280 |
| Chick-fil-A | 74 |
| Zizzi | 428 |
| ASK Italian | 367 |
| PizzaExpress | 398 |
| Tortilla | 284 |
| Tim Hortons | 289 |
| Wasabi | 74 |
| Caffè Nero | 422 |
| Chipotle | 24 |
| Chopstix | 83 |

Starbucks counts include exact published size/milk builds; Chipotle contains **ingredient components only**, not complete burritos. Tortilla bases/fillings retain their particular order-format allocations. A source-published Mini Stix food combination is distinct from a GetMacros-created complete order.

## Integration contract

`tools/flagship_release/uk_records.json` is the frozen, standard-library-readable artifact. It contains `records`, `updates: []` and `withdrawnIds`. The eleven withdrawn IDs must be removed from an already integrated registry before upserting this corrected batch.

`tools/flagship_release/uk_integration.py` provides:

- `load_batch()` — read the frozen artifact.
- `integrate(existing)` — preserve unrelated records, remove explicit withdrawals, and upsert stable GB identities. Idempotent, without file writes or network calls.
- `definitions()` — seventeen source-specific restaurant definitions for the existing guide generator.
- `presence_upserts(existing=())` — GB presence relationships separating operations, source coverage, component-only coverage and finder support.

Shared registries, frontends and public guide pages are owned by the release integrator. This workstream did not commit, push, deploy or mutate those files.

## Evidence and limitations

- `country-restaurant-matrix.csv` / `.json`: every named candidate, operating evidence, local menu/nutrition URLs, implementation, category coverage, image status and exact remaining gap.
- `chain-counts.json`: named source identities, portions and category counts per chain.
- `menu-category-completeness.csv`: actual implemented source groups and limited coverage claims.
- `source-register.json`: **57 used official captures**, source editions, SHA-256 hashes, capture methods, retrieval timestamps and limitations. Retrieval is explicitly separate from verification.
- `sources/retrieval.json`: also retains failed or non-PDF responses, so an HTML error response is not silently called a downloaded nutrition guide.
- `withheld.json`: unavailable macros, ambiguous serving associations, variable bundles, duplicate conflicts and conflicting source numbers.
- `quality-dispositions.json`: independent-audit corrections. No nutrition decimal was guessed to repair a contradiction. Zero gram masses for three fixed LEON drinks are unknown, with their original source zero retained. Small source parent/subset differences up to 0.5 g retain explicit source-quality warnings.

Important source bases:

- Nando’s native nutrient milligrams become grams; source side-size ordering was checked against its linked production UI. Northern Ireland and Gatwick recipes remain distinct.
- Wagamama source sodium is grams and becomes milligrams; independently rounded salt does not overwrite direct sodium. Unrelated request geolocation was redacted from the captured page; only public menu data is extracted.
- Chick-fil-A UK publishes per-100-gram values and serving masses. Each serving nutrient is calculated openly from those inputs. There is no imported U.S. breakfast menu. Salad/protein rows are not treated as complete combos.
- Wasabi serving calories remain published values; other macros scale from per-100-gram values and explicit portion mass. Multi-size tables needing a different adapter remain withheld.
- Five Guys shake bases/mix-ins are components. Heathrow-only breakfast/build options retain their restriction.
- PizzaExpress source scope is England, Wales and Scotland, with airport breakfast restricted to Edinburgh and Gatwick. Separate Northern Ireland/local editions are not substituted. Pizza portions are whole source pizzas, not slices.
- Zizzi’s UK guide is separate from its ROI/Belfast guide. Tim Hortons’ “UK & Ireland” source title alone is not Republic of Ireland operating evidence. The separate-market worker received these limitations.
- Salt-derived sodium uses `salt (g) × 1000 ÷ 2.5`, with conversion provenance. Fibre, sodium and other missing fields remain unknown where the source does not provide them.

The local official Chipotle calculator returned an actual PDF, saved as `sources/chipotle.html` because that was the requested URL type. Its `%PDF` signature and source hash are checked. Treat this file as binary; its extension is not its format.

The sixteen unimplemented candidates are McDonald’s, Burger King, Popeyes, Domino’s, Pizza Hut, Papa Johns, Shake Shack, Taco Bell, Wingstop, Jollibee, Pret A Manger, Costa Coffee, itsu, German Doner Kebab, Slim Chickens and Wenzel’s. Their individual blockers are in the matrix. Several have accessible sources but an unfinished reviewed adapter; those are implementation gaps, not claims that nutrition does not exist.

## Reproduction and checks

The site build needs only the frozen JSON and standard-library integration module. Research-time extraction uses `pdfplumber`; HTML category adapters additionally use `lxml`. Do not load these dependencies into the public application.

```text
python tools/flagship_release/uk_extract.py --check --only html
python tools/flagship_release/uk_extract.py --check --only coordinates
python tools/flagship_release/uk_extract.py --check --only pdf
python tools/flagship_release/uk_verify.py
```

`uk_extract.py` reconstructs saved intermediate tables from official captures. `--check` compares without overwriting frozen artifacts. Omitting `--check` intentionally writes new extracts and requires review if a layout changes.

For a deliberate future re-stage after source review:

```text
python tools/flagship_release/uk_stage.py
python tools/flagship_release/uk_research.py
python tools/flagship_release/uk_verify.py
```

`uk_stage.py` writes only owned staging artifacts and calls `uk_quality.py` before handoff. It no longer filters against the mutable integrated registry; stable IDs and explicit withdrawals belong to integration. `uk_fetch.cjs` performs bounded public captures and writes hashes; its configuration files are the source queue, not verified records.

**Actual results:** `uk_verify.py` passed **18 tests** on 4,736 records, including source-byte hashes, native units, country separation, salt/sodium arithmetic, all Chick-fil-A and Wasabi serving calculations, source-row anchors, subregion restrictions, withdrawals, idempotence and report reconciliation. `verification.json` records the result. HTML reconstruction, Starbucks food-coordinate reconstruction and **all eleven PDF intermediate-table reconstructions** matched the saved extracts. `extraction-verification.json` records those commands and results.

Wendy’s first page and the Five Guys full table were rendered and visually inspected during source review; their PNG evidence is in `sources`. These checks do not imply that every PDF page or every public website route was visually inspected. Integrated public-route, browser, screenshot, SEO and deployment verification belongs to the parent release.
