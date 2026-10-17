# Open Food Facts expansion evidence — 2026-10-17

This work reprocesses the retained official export retrieved on **2026-10-13**. Research documentation was checked on 2026-10-17. Neither that research date nor a successful normalization means a current physical package was checked.

## Primary documentation

- [OFF API introduction](https://openfoodfacts.github.io/openfoodfacts-server/api/) recommends v3 for new product operations; structured search remains in v2. It specifies 15 product reads/minute/IP, 10 searches/minute/IP, a descriptive app User-Agent, and bulk CSV/JSONL for more than a few hundred products. The expansion uses a retained bulk snapshot and local indexes, without per-product API crawling or search-as-you-type API traffic.
- [Official CSV field definitions](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/html/data-fields.txt) specify UTF-8 tab-separated fields. `_100g` means per 100 g **or** 100 mL; `serving_quantity` also means grams **or** mL. A numeric quantity alone does not establish its dimension.
- [Legacy product-nutrition schema](https://openfoodfacts.github.io/documentation/docs/Product-Opener/schemas/schemas/product_nutrition/) defines normalized as-sold `_100g` values, grams for weight nutrients, kcal/kJ energy fields, and separately named prepared values. The importer does not substitute prepared nutrition or infer incompatible vitamin definitions.
- [Current v3.5 nutrition schema](https://openfoodfacts.github.io/documentation/docs/Product-Opener/schemas/schemas/product_nutrition_v3.5/) exposes explicit `per:100g`/`per:100ml`, preparation state and source nutrient sets. It distinguishes available carbohydrate from US/Canadian total carbohydrate. The retained TSV includes only `carbohydrates_100g`, so that value is preserved with a definition warning; fiber is never added or subtracted to manufacture another carbohydrate definition.
- [OFF license guide](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorials/license-be-on-the-legal-side/) identifies ODbL database rights, DbCL individual contents and separate CC BY-SA imagery. No product images are copied.
- [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) requires the applicable attribution and share-alike conditions. Public derivative use must offer the database or applicable alteration data by a freely accessible machine-readable route. This source-specific derivative therefore retains downloadable normalized data, its selected source records and a standalone transformation algorithm, with notices. Independently licensed USDA/CNF/retailer data are not folded into it.
- [DbCL 1.0](https://opendatacommons.org/licenses/dbcl/1-0/) covers individual contents and requires compliance with ODbL. Brand names identify products; they imply no partnership or endorsement.

The public [OFF data page](https://world.openfoodfacts.org/data) returned a bot notice to the research tool. Its restrictions were respected. The official export URL and acquisition evidence already retained in this repository were used; no access controls were bypassed.

## Retained archive and source completeness

The archive contains 4,532,767 product rows and 211 columns. Recorded retrieval: 2026-10-13T17:53:38.628Z. Provider Last-Modified: Tue, 13 Oct 2026 12:17:29 GMT. It is the official `en.openfoodfacts.org.products.csv.gz` export, served by the provider's S3 endpoint. The acquisition record captures a same-ETag HTTP 206 resume, not a new independent dataset.

Measured compressed size: **1,275,171,186 bytes**. Measured decompressed TSV size: **13,042,211,705 bytes**. SHA-256 verified during this work: `f72687ee8bc6522054fe69dbfda6b91902c16af1ec2e043cde27bc6c29ad8176`. The 13 GB TSV was streamed; no extracted copy was created. Details are in `off-source-footprint.json` and the retained acquisition JSON.

The old importer accepted all qualifying Canadian source brands but limited the other seven supported markets to a hand-picked brand list. The expansion removes that brand-selection gate while retaining the identity, unit, nutrition-quality and category gates. This accounts for **148,908 additional market profiles**, before any canonical deduplication reported by final staging. Canada already had the broader brand policy, so it receives no additional profiles from removing that gate.

| Market | All source country-tagged rows | Accepted with explicit source unit | Existing profiles | Additional before canonical dedupe |
| --- | ---: | ---: | ---: | ---: |
| Canada | 120,444 | 46,950 | 46,950 | 0 |
| United States | 910,130 | 72,769 | 17,106 | 55,663 |
| United Kingdom | 186,785 | 67,041 | 24,206 | 42,835 |
| Ireland | 78,632 | 35,223 | 3,975 | 31,248 |
| Australia | 73,300 | 9,159 | 1,856 | 7,303 |
| Mexico | 16,851 | 8,057 | 1,743 | 6,314 |
| New Zealand | 14,786 | 2,352 | 423 | 1,929 |
| Japan | 39,404 | 3,808 | 192 | 3,616 |

Counts are source-attributed market profiles, not unique global products, independently verified labels, retailer catalogs or current inventory. The same source product can explicitly report multiple markets. Market, source code, validated barcode representation, formulation, flavor/name, ingredients, package, serving and source version remain distinct. Supported markets are unchanged.

## Serving and nutrition boundaries

Of 245,359 accepted profiles, 225,046 have source gram servings and 20,313 have source milliliter servings. Gram profiles retain a 100 g basis plus their exact source gram portion. Volume profiles retain the named source mL serving and no gram portion or inferred density. Missing values remain null and explicit zero remains zero.

This TSV does **not** contain `nutrition_data_per`, `nutrition.aggregated_set.per` or another explicit nutrition-table basis field. Across supported-market candidates, 243,673 source rows fail the explicit matching serving-unit gate after preceding quality checks. They cannot honestly be made 100 g records merely because an `_100g` field or gram package size exists. Current OFF JSONL/API schema can support missing-serving records when it supplies an explicit as-sold 100 g/100 mL nutrient-set basis; that is a future source adapter, requiring matching source evidence and runtime volume support. No unit is inferred here from category, brand origin, serving text with mixed dimensions or package quantity.

Other source-row rejections include 468,253 missing product/brand identities, 373,321 missing usable core nutrition, 55,664 invalid/missing supported barcodes, 47,470 provider quality-error tags and 30 zero-energy records with substantial protein/fat awaiting package/rounding review. Counts are evaluated in gate order, so they do not describe mutually independent source defect prevalence. Supplement and infant-food exclusions remain. No replacement calories are invented.

## Staging and verification

`tools/global_coverage_2026_10_17/off_expand.py` stages only into this evidence directory. It preserves existing baseline IDs/formulation hashes, keeps retrieval/version evidence explicit, and writes deterministic gzip shards with `jsonEncoding:gzip`, three-hex record prefixes, 64-record index pages, barcode/token/market postings, country brand counts and a source-separated manifest. Normalization conversion context is stored once per record, with per-field original values/factors retained.

The freely downloadable `normalization.py` has only standard-library dependencies and can transform `source-records.ndjson.gz` into NDJSON on its own. `RIGHTS.txt`, ODbL/DbCL metadata and source attribution accompany the derivative. No images, marketing text, ratings or private diary contents enter the partition.

The completed staging contains **241,432 source products / 245,359 market profiles** and is **251,201,564 bytes**. Its normalized NDJSON gzip is 87,979,644 bytes; the selected source gzip is 39,068,616 bytes. The 87,071-byte uncompressed manifest exposes `brandCount:68202` and the country brand-file prefix, avoiding a duplicated global brand dictionary in the initial fetch. The largest compressed record shard is 36,457 bytes. The existing 96,451 IDs and formulation hashes are preserved. Gzip shard/index relationships and 6,624,693 source nutrient comparisons passed the streaming audit. No production deployment is performed by this staging tool.

`off_test_expand.py` covers source-brand eligibility, baseline identity preservation, null/zero, g/mL arithmetic, ambiguous units, GTIN checks, package/flavor/formulation/market distinctions, nutrient unit conversions, quality quarantine, carbohydrate no-adjustment, source-version honesty, deterministic gzip and standalone export operation. `off_verify_partition.py` uses a temporary compact SQLite identity/posting index to compare every record with retained source arithmetic and every index, barcode, token and market relationship. It does not retain all label objects in memory. Final measured bytes and completed verification results are recorded separately in `off-stage-report.json` and `off-integrity.json`.

The production `grocery_integrity_off.py` entry point delegates this expanded source version to that streaming audit. It opens the committed public source subset, not the original 1.275 GB archive. A small `off-baseline-invariants.json` pins the count, country counts and SHA-256 of all 96,451 original ID/formulation pairs, plus the 21 original quarantine source codes. Those invariants are reconstructed and checked from the retained subset in CI. The production audit passed 245,359 profiles, 6,624,693 source nutrient comparisons, 1,291,950 token postings, every record/index/export relationship, all 30 current quarantine records and source rights notices in 149.8 seconds. The integrated grocery test entry point passed 33 boundary/dispatch/baseline tests. Of the expanded profiles, 237,759 have all four core macro fields and 7,600 retain partial core data explicitly as unknown.
