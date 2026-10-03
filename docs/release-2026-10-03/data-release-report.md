# Restaurant-data and resource implementation

Implemented October 3, 2026, without deployment.

## Delivered

- Audited patch for41 existing order records at8 chains, plus27 official ingredient portions. The parent integrator applied central records; this agent did not rewrite central data directly.
-18 individually edited resources in `tools/release_collections.json`: numerical collections, cross-chain comparisons, ingredient references and an original dataset-coverage report. No restaurant×keyword publishing matrix. Two weak near-duplicate ideas were consolidated instead of padding the page count.
-183 reproducible table-fact rows across the resources, with explicit selection criteria, exact serving definitions and a claim/source manifest.
-Seven tested ingredient sums and two tested sodium differences in `data-derived-calculations.json`. No missing fat inferred from calorie arithmetic.
-All15 existing restaurant guide menu and comparison tables synchronized to83 central records by `tools/sync_restaurant_release.py`. New tables expose known fat, retain unknown values, and provide collapsible source/portion information. Header, footer, design template and unrelated article writing were preserved.
-Panda's old numeric metadata and chicken/greens arithmetic were corrected. The comparison distinguishes the full10ozgreens base from the3.5ozentree entry. CAVA's equal-sodium and Popeyes' close-sodium comparison statements were checked and remain numerically valid.
-Mixed Chipotle provenance links both the ingredient table and the High Protein Menu announcement. Source edition dates are separate from retrieval dates. Uninspected chains' source dates were not globally advanced.

## Checks performed

-`release_collections.py --require-applied`:18 unique resources, matching audited facts, known internal body links, balanced tables and section headings, no central nutrient-value differences including separate fat provenance.
-`sync_restaurant_release.py`:83 table rows and every generated numeric cell checked against central meals/provenance;15 two-order comparisons resolved by exact names.
-Repeated synchronization produced identical hashes for all15guides before subsequent deliberate presentation hooks were added.
-Existing local browser fixture rendered Panda, Chipotle and Chick-fil-A at320/1440px in both themes:12renders, successful source disclosure, no page overflow or runtime exception. These are repository-backed browser checks, not network checks against restaurant ordering systems.
-Two screenshots were personally inspected: narrow light Panda and desktop dark Chipotle. The oversized first-column issue found there was sent to the parent; compact/main table class hooks were then added for the parent's CSS fix. Earlier screenshots should not be represented as the final post-fix design.
-A duplicated comparison paragraph caused by a contiguous-HTML offset was detected by the editorial agent, repaired across15guides and fixed in the synchronizer.

## Exact evidence limits

-CAVA: accessible official April-2025-named document, no established printed date or current live-menu linkage.
-Starbucks: indexed official nutrition text inspected for3foods; direct retrieval did not render its live nutrition tables.
-Chipotle: ingredient PDF printed October2024, despite2025in its filename; High Protein Menu announcement is December18,2025. Retrieval on October3,2026 does not change either publication date. Half-rice remains an explicit calculation assumption.
-Chick-fil-A12nuggets:4nutrients rechecked; fiber/sodium not newly inspected. They remain unavailable in this release's comparison pool. Two large Chick-fil-A combinations were not newly recalculated because exact side portions were not reverified.
-Other7chains and42central records were not reverified by this source batch. Existing records and truthful previous check dates were retained.
-Ingredient/diet preference labels are existing editorial classifications, not new allergen or vegan certifications.
-Sources and search findings are documented in `source-notes-research.md`. Research is qualitative; no search volumes, rankings, approval odds or revenue forecasts were invented.
-No source PDF, complete restaurant dataset download or branded photo is republished by this work. Attribution is not represented as a universal database/image license or a legal reuse determination.
-The integrated18newpublic pages still require the parent's final browser/copy/route verification. No AdSense acceptance guarantee or accessibility certification is made.
