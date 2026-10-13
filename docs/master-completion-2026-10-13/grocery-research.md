# Grocery data research — October 13, 2026

Research uses current primary documentation and actual source responses. No Search Console or keyword-volume claim is made here.

## Sources checked

- USDA [current downloads](https://fdc.nal.usda.gov/download-datasets/) still list April 2026 Branded as the current bulk release. Existing GetMacros source-separated CC0 manufacturer-label records remain intact. No Canadian identity is inferred from U.S. labels.
- Health Canada [CNF documentation](https://produits-sante.canada.ca/api/documentation/cnf-documentation-en.html) could not be opened through web research today. The repository already contains the 2026 official bulk dataset, dated nutrient provenance and Open Government Licence—Canada attribution; these reference profiles are not branded-grocery records.
- Open Food Facts [API documentation](https://openfoodfacts.github.io/openfoodfacts-server/api/) is current and readable. v3 is recommended for product operations, but structured search remains v2. It documents 15 product reads/minute/IP and 10 searches/minute/IP; more than a few hundred products should use bulk CSV/JSONL. Production search is therefore local, never remote search on every keystroke.
- OFF [product nutrition schema](https://openfoodfacts.github.io/documentation/docs/Product-Opener/schemas/schemas/product_nutrition/) explicitly defines normalized as-sold nutrient values: per 100 g or 100 mL, weight nutrients in grams, energy-kJ in kJ and energy-kcal in kcal. Prepared fields have their own suffix and are not substituted for as-sold values. [Export field definitions](https://github.com/openfoodfacts/openfoodfacts-server/blob/main/html/data-fields.txt) identify serving_quantity as grams or mL; the quantity alone does not reveal which.
- OFF [license guide](https://openfoodfacts.github.io/openfoodfacts-server/api/tutorials/license-be-on-the-legal-side/) identifies ODbL database rights, DbCL contents and separate CC BY-SA imagery. [ODbL terms](https://opendatacommons.org/licenses/odbl/1-0/) permit commercial use and distinguish derivative from collective databases; attribution, share-alike and freely accessible machine-readable data or transformations must be preserved. The OFF terms-of-use endpoint produced a bot notice and its wiki attribution summary an access-denied page through the web tool. Its own [published English terms source](https://github.com/openfoodfacts/openfoodfacts-web/blob/main/lang/en/texts/terms-of-use.html) was subsequently read: it confirms commercial reuse subject to the licenses, attribution to product pages for individual products, non-guaranteed data quality, third-party rights limits and that the French version prevails. No access controls were circumvented.

## Actual availability

A single descriptive-User-Agent read of the official Canadian v2 search returned HTTP 200 with 100 source product records. Its count field reported 128,301 products tagged for Canada; that is an observed provider count, not the number GetMacros imported, independently verified or currently stocked. The selected field response is retained in private research evidence.

The official daily bulk CSV gzip returned HTTP 200, 1,275,171,186 bytes, last modified October 13, 2026. Bulk downloading avoids repeatedly polling product/search endpoints. The full archive is private evidence and not bundled into page JavaScript.

## Import decision and quality boundaries

Use a separate /data/branded-foods/off/ derivative partition. Preserve exact source product/brand/barcode/package/market identity and individual source updates. The independently licensed USDA, CNF and curated retailer values are neither merged into this partition nor used to fill missing OFF nutrients. Unknown stays null; a genuinely reported zero remains zero.

Only valid source GTINs, named brands/products, explicit source-attributed supported markets and explicit matching g or mL servings pass. All products with OFF data-quality error tags, impossible core densities, inconsistent sugars/fat or missing usable nutrition are excluded. Supplements and infant products are excluded from this food logging catalogue. There is no independent package verification, allergy certification or retailer inventory claim.

Canada is searched across source brands; other supported markets use a curated brand queue. The queue includes requested store brands, national brands and regional grocery brands; inclusion is not proof of coverage. Actual counts will come from the finished partition manifest.

Volume products use the named source serving and source mL arithmetic. They have no invented gram portion or density. Vitamin A RAE, folate DFE and vitamin K phylloquinone are not inferred from differently named OFF fields. Gram-to-mg/µg and kJ-to-kcal conversions retain their exact field/factor provenance.

Every public derivative record retains ODbL, DbCL, linked attribution and redistribution metadata. Free normalized record/index shards, a source-subset NDJSON gzip and the normalizer are exposed alongside the manifest and RIGHTS.txt. No product images, package art, ratings, marketing copy, private user logs or U.S. fallback labels are imported. Community market tags can describe a shared product across countries; visitors must check the local package, not assume every national formulation is equal.

## Commercial options, researched but not integrated

[Edamam food API documentation](https://developer.edamam.com/food-database-api-docs) supports branded/barcode lookup and logging. Its [plan and caching terms](https://developer.edamam.com/food-database-api) restrict automated collection and general data copying; allowed caching is plan-specific and user-account-scoped, with attribution and active-subscription obligations. It is not a permitted bulk library source for this static release without a negotiated agreement. No account, key or purchase was made.

[FatSecret Platform](https://platform.fatsecret.com/platform-api) offers country-dependent licensed nutrition capabilities under its commercial agreements; claims about coverage and service levels are provider descriptions, not GetMacros measurements. It is a future licensed service candidate, not data silently imported into this project. No account, key, contract or purchase was made.

## Maintenance

The importer reads one TSV source record at a time rather than extracting the whole archive. A failed or empty source aborts before publication. Explicit retrieval-date input separates refreshing a source from checking a current physical package. Saved diary snapshots continue to retain the source version actually logged. Public coverage must always be generated from manifests, not from the brand research queue.

## Implemented result

The complete official 1,275,171,186-byte export was downloaded, with a same-ETag HTTP 206 resume after the initial bounded download timed out. SHA-256: f72687ee8bc6522054fe69dbfda6b91902c16af1ec2e043cde27bc6c29ad8176. The TSV stream contained 4,532,767 source product rows.

After a source-consistency audit quarantined 21 zero-energy profiles with positive protein/fat density pending package-label or rounding review, the reviewed ingestion boundaries produced 96,451 market-label profiles from 94,620 source products: Canada 46,950; United States 17,106; United Kingdom 24,206; Ireland 3,975; Australia 1,856; Mexico 1,743; New Zealand 423; Japan 192. These numbers count market profiles separately from source product identities. A source product can have multiple explicitly reported markets. They are community imports, not 96,451 independently verified current packages.

95,180 imported profiles contain all four core macros; 1,271 have partial core data, kept explicitly unknown. 10,526 use source mL servings with no inferred grams. No OFF photos or private diary entries were imported. Rejections, per-market and per-source-brand counts are in grocery-import.json, the public manifest and source-specific brand files. Source-level brand coverage includes President’s Choice, No Name, Great Value, Kirkland, Compliments, Selection, Irresistibles, Our Finest and Western Family. The source also contains 15 Canadian Nature’s Emporium brand-text matches and nine U.S. Erewhon matches. These are source brand/market tags, not verified retailer operations, current availability or a complete catalog. Absent qualifying rows remain gaps rather than fake records.

The public partition uses 3-hex record shards: maximum 224,508 bytes. The largest token file is 177,289 bytes; index pages max 37,139 bytes. Country posting lists are applied before candidate limits, preventing an early U.S. candidate slice from hiding actual Canadian records. A full catalogue is not loaded into the initial page or a single JavaScript bundle. Total static partition is roughly 598 MB, including separate compressed full/source-subset exports; this is a deployment-size consideration, not a claim that every visitor downloads it.

## Checks performed

17 Python boundary tests passed, including missing/true-zero values, GTIN checksums, exact gram/mL serving arithmetic, incompatible nutrient definitions, international identity, Unicode search, failed/empty import preservation and two-rerun subset idempotency with a preserved quarantine ledger.

Every 96,451 published profile was recomputed from the retained source subset. All index profiles, 518,823 token postings, barcode postings, country postings, per-country brand counts and freely redistributable normalized export were checked. Integrity results are in grocery-integrity.json.

Production-adapter tests use the actual local source records, not external provider mocks or fake product values. Seven requested Canadian brands return local source results; eight markets return source-attributed labels; actual barcode lookup, source-serving scaling, nulls, linked license preservation in diary snapshots, and provider/partition failures were checked. Precise cold queries fetched 0.997–1.558 MB over 12–31 static requests in this uncompressed Node loader. These are measured local bytes/request counts, not mobile field timing or browser visual inspection. Results are in grocery-search.json; root integration performs rendered browser verification.

The quarantine contains 15 Canadian and six U.S. source products. Some tiny condiment portions may reflect label rounding; other examples clearly combine zero energy with substantial fat/protein. No estimated replacement calories were published. IDs and native source values are retained in grocery-zero-energy-audit.json and the public quarantined.json, outside search/logging indexes. Reprocessing a retained source snapshot preserves its original retrieval date and bulk checksum; it does not claim that the provider was freshly retrieved. Eligible-subset reruns retain the separate quarantine evidence and count each excluded product once.
