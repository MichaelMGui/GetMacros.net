# Editorial research and intent decisions

Research date: 18 October 2026. Locale: English-language search queries explicitly containing UK or Canada; search engine location was not independently controlled. No authorized Search Console export or keyword-tool volume data was available in this workstream. Findings below are qualitative search-result observations, not evidence of demand size, ranking, traffic or CTR.

## Queries actually inspected

| Query | Search observations | GetMacros implementation |
|---|---|---|
| LEON breakfast calories protein egg pot muffin UK official nutrition | Results include official LEON item pages with per-portion nutrient labels, an ingredient list and a separate brand article explaining its nutrition symbols. A reader needs to combine several product pages to compare breakfast formats. | A finished guide compares two muffins, the salmon/avocado egg pot and the larger halloumi sando; it keeps recipe and portion differences explicit. |
| Nando's UK chicken butterfly spicy rice chips nutrition calories | Results include the official dynamic menu, older third-party/PDF figures and independent menu-price pages. The official menu has standard side portions, sharing sizes and separate Northern Ireland recipes. | A worked order comparison fixes 1/4 Chicken and changes one regular side; it shows sums, not a copied menu dump, and explicitly excludes the Northern Ireland rice recipe from the standard calculation. |
| Wendy's UK breakfast muffin wrap calories nutrition | Results include official wrap pages, multiple historical official nutrition-chart editions, a general third-party menu calorie list and a copied chart on a document-sharing platform. None of those third-party nutrient figures was used. | A finished UK-only breakfast comparison identifies the March 2026 chart, filling, sauce and branch-availability limits. It does not infer a combo from a sandwich entry. |
| Chick-fil-A Canada waffle fries small medium calories chicken sandwich nutrition | Results expose the current official Canadian serving table and side menu alongside U.S. or older third-party charts. Small, medium and large fries have separate gram weights and unequal increments. | A finished Canadian same-main/same-drink comparison uses 96 g, 125 g and 179 g fries, shows all three order totals and links the exact small/medium side records. |

Follow-up searches actually inspected: `Nando's quarter chicken spicy rice regular calories UK` and `Chick-fil-A Canada Buddy Fruits Multifruit waffle fries grilled sandwich calories`. The latter revealed a material source conflict: the official [Multifruit product page](https://www.chick-fil-a.ca/menu/sides/buddy-fruits-multifruit) describes a 90 g pouch while the official nutrition table says 100 g, both reporting 60 kcal. This was reported to the market researcher, who is flagging the record and withholding its calculated complete order. The proposed fruit-versus-fries article was withdrawn before integration; no actual published route was removed. No 90/100 scaling, substituted U.S. Fruit Cup or invented portion resolution was used.

## Primary sources inspected

- [LEON Sausage & Egg Muffin](https://leon.co/menu/sausage-egg-muffin/), [Bacon & Egg Muffin](https://leon.co/menu/bacon-egg-muffin/), [Smoked Salmon & Avocado Egg Pot](https://leon.co/menu/smoked-salmon-avocado-egg-pot/), [Halloumi, Egg & Avo Sando](https://leon.co/menu/halloumi-egg-avo-sando/) and [menu](https://leon.co/menu/): individual per-portion labels and staged official menu capture. The research browser could not open the egg-pot page initially; an ordinary public HTTPS GET then returned 200 and its visible nutrition labels were inspected directly (211 kcal, 13 g protein, 145 g portion). No access control or credentials were bypassed.
- [Nando’s official menu](https://www.nandos.co.uk/food/menu/) and the staged official page-data nutrition: quarter chicken, regular side mapping, large-sharing notices, butter included with regular corn and the separate Northern Ireland rice entry. The article does not apply default British values silently to Northern Ireland.
- [Wendy’s UK March 25, 2026 chart](https://www.wendys.com/sites/default/files/2026-04/United-Kingdom-National-Nutrition-Information---3.25.2026-%28002%29.pdf) and [official breakfast wraps](https://www.wendys.com/en-gb/breakfast-wraps): exact portions/units, current matching wrap calorie labels, and the explicit warning that breakfast is not at all locations.
- [Chick-fil-A Canada nutrition](https://www.chick-fil-a.ca/nutrition-allergens), [sides](https://www.chick-fil-a.ca/menu/sides) and [grilled sandwich](https://www.chick-fil-a.ca/menu/entrees/grilled-chicken-sandwich): country, exact serving grams, native nutrient values and correctly named fruit product. No U.S. data was substituted.

The release’s UK and market researchers supplied source captures/hashes in `tools/flagship_release`. The article module checks the named staged records and recomputes composition totals with Decimal arithmetic. Eight direct official source URLs returned HTTP 200 during this editorial check; exact results and response hashes are in `source-link-checks.json`. A retrieval date is never relabeled as a source edition or clinical review.

## Existing intent overlap review

The repository’s root and localized public HTML routes were searched for the restaurants, breakfast formats and precise order intent. Existing U.S. Wendy’s/Chick-fil-A guides and generic breakfast comparisons were inspected as potential overlaps. Existing `greggs-sausage-roll-vs-vegan-roll-nutrition.html`, `fast-food-breakfast-protein-comparison.html`, `breakfast-food-vs-combo-menu.html` and `compare-complete-restaurant-orders.html` serve different restaurants, reference explanations or a general interactive tool. No equivalent LEON or Nando’s exact comparison was found.

Four new articles were selected. **Existing-page substantive improvements: 0 in this isolated workstream.** Restaurant hubs should link to their matching new article after integration; publication is owned by the main release integrator. No article count or anticipated traffic is treated as a quality result.

## Metadata and linking decisions implemented in the article export

Titles identify restaurant, market and exact comparison. Descriptions state the real portions or fields; they do not claim “healthiest”, a verified rating or guaranteed search performance. The direct numerical answer precedes each table. Each body links the relevant comparison, finder, order builder or diary with explicit market state. Source dates and component assumptions are visible. No FAQ/Recipe/review schema was authored, and no indexed filter variation is created.

Publication dates remain null until the main release publishes the page. This workstream does not submit a sitemap, claim Google indexing or change canonicals. Root owns final rendered-page QA and SEO integration.
