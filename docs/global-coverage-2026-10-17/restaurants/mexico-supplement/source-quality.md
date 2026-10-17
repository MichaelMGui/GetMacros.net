# Mexico restaurant supplement: withheld

Reviewed 2026-10-17. **Zero new records, updates, presence upserts or guide briefs.**
The existing 100 Subway Mexico records remain unchanged. KFC Mexico was not
reprocessed or republished. No foreign menu substitutions were made.

## McDonald’s Mexico: numerical nutrition unavailable

The current official [hamburger category](https://www.mcdonalds.com.mx/menu/hamburguesas)
links the [Mexican Big Mac page](https://www.mcdonalds.com.mx/menu/hamburguesas/big-mac).
The readable product page exposes nutrition/allergen accordion headings, but no
numeric nutrition values. The [Cajita Feliz page](https://www.mcdonalds.com.mx/menu/cajita-feliz)
likewise exposes a nutrition prompt without a usable numeric table.

Six direct official-page download attempts returned **HTTP 403**: the normal Big
Mac URL, apex-domain Big Mac URL, a query-string variant, home page, menu index,
and Cajita Feliz page. Exact URLs/errors are in `retrieval.json`. No raw HTML was
captured, so no source hash is claimed for these failed downloads. The browser
inventory contained no enabled apps or browsers, preventing public accordion
inspection. `mcd-mx-web-observations.json` distinguishes readable web observations
from raw source captures. No nutrition was inferred from product descriptions.

## Burger King Mexico: usable access, unusable meal evidence

The accessible official [Big King page](https://www.burgerking.com.mx/menu/a-la-parrilla/big-king-s.html)
publishes **224 g and 570 kcal**, with no protein, carbohydrate or fat values.
Its captured HTML SHA-256 is
`463efe9443ffde8c2d86334f518b6a6531a2a08e670706d8258348082ff78a04`.

The current [menu application](https://www.burgerking.com.mx/es/menu) loads
`/static/js/main.bdd06e47.js`. That official public application defines nutrition
units and anonymous Sanity reads. The Mexican project/dataset identity is also
present in the official page’s image URLs. No token, account, API key, cookies
or authorization header was used. Exact query URLs and hashes are retained in
`retrieval.json`; the public endpoint is
`https://czqk28jt.apicdn.sanity.io/v2023-08-01/data/query/prod_bk_mx`.

The captured aggregate query reports **418 nutrition objects**, **79 with
carbohydrate**, **78 with fat**, **78 with protein**, and **78 complete macro
objects**. These are CMS object counts, **not current Mexican menu counts**.
Of the 78 complete objects, 59 lack a Spanish name and six explicitly contain
`PLU CONFIG TEST`. The remaining 13 have Spanish names but still lack verified
membership in the currently presented local menu. Dataset menu objects include
`Antarctica Menu` and a multilingual legacy `BK Menu`; public CMS inclusion is
insufficient proof of a published Mexican formulation. No blanket import was made.

Concrete conflicts in the captured objects:

| Source object | Published portion/data | Exclusion |
| --- | --- | --- |
| `148c51b3-ab00-4a59-adfd-9e244fcaa8a8`, Papas Grandes | `productSize: 176 Gramos`; `nutrition.weight: 159` g; 379.22 kcal, 4.89 g protein, 47.56 g carbohydrate, 16.93 g fat | Two conflicting source weights; neither selected or used to rescale the other. |
| `a43fcfc0-a996-461e-b103-aa2d5adbd270`, Papas Grandes | Same conflicting 176 g / 159 g and macros | Duplicate source ambiguity retained, not silently merged. |
| `76beba77-ed47-4020-900e-187ef9079683`, Manzanita Sol Grande | 850 ml; 350 kcal; protein/carbohydrate/fat all exactly 0 in source | Energy/macro contradiction; no guessed carbohydrate correction or ml-to-g conversion. |
| `f3760c9b-bdf8-4502-9519-2ec9d68b7e26`, Manzanita Sol Regular | 453 ml; 150 kcal; protein/carbohydrate/fat all exactly 0 in source | Same contradiction; no corrected record created. |
| `8fad2475-aedd-4554-9443-e1e26f4904e6`, Epura | 0 kcal and zero core macros; numeric weight 500; `productSize: null` | No established live local menu/packaged serving; water does not establish a usable meal batch. No 500 ml portion invented. |

All 78 raw complete objects, source object IDs, source-update timestamps, numerical
values and exclusion reasons are preserved in `withheld.json`. Source update
timestamps are **not** treated as nutrition edition dates or package checks.

The [regional nutrition page](https://www.burgerkinglatino.com/es/content/nutrition-information-documents-area)
links `https://bk-emea-prd.s3.amazonaws.com/sites/burgerking.es/files/documents/Mantel-Nutricional-16-08-2016.pdf`
and `https://bk-emea-prd.s3.amazonaws.com/sites/burgerking.es/files/documents/nutritionals.pdf`.
Those point to a Spanish-country storage path; Mexican applicability was not
established. They were not substituted for Mexican nutrition. The local
[real-food page](https://www.burgerking.com.mx/saborreal-s.html) contains a nutrition
accessibility statement, but no complete numerical nutrition table.

## Retained evidence and checks

`bk-mx-public-counts.json` SHA-256:
`a1b3cd3aba79b9a62cde0016b40762ab46dbc19e10631c3ccb10a2a6f8a9b007`.
It retains every one of the 78 complete objects. `bk-mx-public-menus.json` retains
all four observed menu objects. `bk-mx-public-nutrition.json` retains the first
250 nutrition objects from the initial bounded inspection, not an exhaustive
product archive. Captures are public factual menu data, not an image collection.

The inspected official JavaScript bundle SHA-256 was
`9fe325d9c92a3ad91d4d9d352bce8b5047f67b5e21ebcdcdc4b87c27602e2007`.
Only its needed project/dataset/unit excerpts remain in
`bk-mx-app-source-evidence.json`; the unrelated full app configuration/telemetry
bundle is not retained. `retrieval.json` explicitly records this distinction.

Run with the bundled Python runtime:

```text
python -X utf8 tools/global_coverage_2026_10_17/mexico-supplement-report.py
python -X utf8 tools/global_coverage_2026_10_17/mexico-supplement-test.py
```

All seven tests pass: empty accepted batch; retained capture hashes; both fries
portion conflicts; unchanged contradictory soda values; template/test evidence;
McDonald’s access limits; and the unchanged 100-record Subway Mexico nutrition,
identity and source fingerprint. No shared runtime, build, production data or
existing batch file was edited.
