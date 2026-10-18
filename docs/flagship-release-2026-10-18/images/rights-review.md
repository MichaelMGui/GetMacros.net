# Meal image rights and coverage

Research and asset review: 18 October 2026. Exact counts are generated from the current `js/order-registry.json` in `meal-image-manifest.json`, not estimated from page counts.

Final stable-registry regeneration covers **10,327 records across 12 existing markets**. All 10,327 have an individually identified, honestly labeled category-illustration assignment and a specific exact-photograph acquisition gap. Fifteen original SVG illustrations are available. **Exact meal photographs: 0. Authorized photographic background removals/compositions: 0.** These gaps remain unfinished; the illustration assignments are not counted as photo acquisition.

The regenerated manifest passed identity, asset-existence and nine category regression checks. All fifteen assets rendered in both themes without image-load failures or horizontal overflow. Final light/dark contact sheets were captured in `original-cutouts-light.png` and `original-cutouts-dark.png`; results are in `image-checks.json`.

## Implemented

Fifteen original transparent SVG category illustrations were created in `tools/flagship_release/image_assets.cjs`: burger, bowl, sandwich, wrap, pizza, salad, chicken, breakfast, fries, coffee, drink, dessert, sauce, sushi and side. They have consistent colors, proportions and optional light depth; no external image, brand logo, trademark packaging or restaurant photograph was traced. All are 400 × 300 with a transparent background and deliberate viewbox space.

`images/meal-cutouts/provenance.json` records source, dimensions, transformations, ownership context and file hashes. The category adapter `js/meal-images.js` explicitly returns `kind: illustration` and `exactPhotograph: false`. Display **Illustration** when the surrounding layout could otherwise imply a photograph of an exact restaurant item. Empty alt text is suitable when the meal name is already adjacent and this is decorative; do not write image alt text that invents observed ingredients.

Every existing restaurant record has a row in `meal-image-manifest.json` and the CSV. Each row preserves market, exact item name, source serving, category assignment, asset and the specific permission/photography gap. A fallback assignment does not count as a matched photograph or portion.

Browser renders of all assets in light and dark are saved beside this report. The images were inspected for cropping, clipping, legibility and transparent edges. These are native vector cutouts, not background-removed photographs; **authorized photographic cutouts added: 0**.

## Why no restaurant photographs were copied

No written image license or owned photography matching the exact menu-record portions was present in the repository. Public access to a menu photograph is not reuse permission.

- [McDonald’s U.S. terms](https://www.mcdonalds.com/us/en-us/terms-and-conditions.html) were inspected for ownership and permitted-use provisions. They do not establish a license for this commercial third-party catalogue to copy, edit and republish menu photos. Country-specific image reuse must be checked separately.
- [Chick-fil-A legal resources](https://www.chick-fil-a.com/legal) and its linked terms were inspected as the entry point for permission research. No GetMacros image permission was found. Neither a nutrition source nor a menu URL is treated as an image license.
- The existing `images/editorial-salad.webp` has recorded Anna Pelzer / Unsplash provenance in `images/README.md`. Its [original page](https://unsplash.com/photos/bowl-of-vegetable-salads-IGfIGP5ONV0) and [Unsplash license](https://unsplash.com/license) were rechecked. It remains editorial food inspiration, not a verified restaurant dish, and has **zero exact-meal matches** in this manifest.
- Historical `images/restaurant-logos/*.png` have no recorded reuse license and are not promoted as cleared assets. The app builder excludes that directory.

## Acquisition queue and acceptance gate

Prioritize current featured orders, U.S./Canadian breakfast, complete orders and UK chain coverage. For each photo: acquire owned/commissioned capture or written permission identifying the market, portion and allowed crop, background removal, composition and commercial web/app uses. Store the actual grant, attribution and expiry if applicable. Verify that packaging/ingredients/side sizes match the source serving. Only then change a row to an exact photograph.

For licensed background removal, inspect pale food, white rice, cheese, packaging, steam and fine edges against both themes. No white-background asset was edited without a grant. Composition of authorized components must be labeled when it is not an actual photographed tray.

Do not interpret the illustration set, a public URL, nutrition-data permission or an existing local raster file as restaurant photo clearance. All exact-photo gaps remain explicit until actual permission and serving match are established.
