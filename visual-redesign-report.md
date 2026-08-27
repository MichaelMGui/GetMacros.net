# GetMacros premium visual redesign

## Outcome

GetMacros now behaves like one focused nutrition product across all 118 retained HTML pages. The redesign keeps the existing URLs, copy, metadata, semantic structure, verified AdSense loader, and restaurant data while making the interface feel calmer, more intentional, and easier to scan.

## Design system

- A floating translucent navigation panel settles from 68 px to 60 px after scrolling. It uses one restrained blur layer, a consistent active state, and a horizontally scrollable mobile navigation row.
- The shared palette uses forest, paper, mint, lime, and neutral ink. Text contrast remains governed by `contrast-fix.css`, which loads after the core premium layer.
- Forms use a consistent 52 px target, clear labels and focus rings, a custom modern select arrow, and accessible native controls.
- Cards share one radius, border, shadow, hover lift, and pointer spotlight language. Mobile removes unnecessary motion and keeps the cards single-column.
- Long-form guides keep a calm reading measure, more generous leading, stronger introductory paragraphs, and consistent details/callout treatments.

## Homepage composition

- The goal and tool sections now use intentional bento layouts at desktop and collapse into a clear single column on small screens.
- The hero example includes a real macro ring showing the percentage of displayed calories supplied by displayed protein. It is explicitly a visualization of published meal math, not a mystery health score.
- Restaurant guides are presented as a horizontal, snap-aligned product rail rather than a long directory dump.
- One contained sticky methodology story explains source transparency without adding movement to every section.

## Motion system

- Hero auroras now morph between organic liquid shapes while drifting slowly; animation changes transform, opacity, filter, and border shape only, so it does not cause layout shift.
- Scroll reveals include a fail-safe that restores any unrevealed content.
- Cards use restrained hover lift and pointer sheen; buttons use small press feedback; numeric results and result cards enter in sequence.
- Reading progress, quiz progress, macro bars, chip selections, and the hero macro-ring glint use the same spring/ease language.
- `prefers-reduced-motion: reduce` disables the liquid motion, reveals, glint, ripples, counting animation, smooth scrolling, and hover movement.

## Page-wide quality controls

- `tools/audit_visual_contract.py` checks every retained page for the shared design assets in the correct cascade, responsive viewport metadata, design scope, landmarks, duplicate IDs, accessible form labels, non-empty selects, and obsolete markup.
- `tools/validate_site.py` continues to check SEO metadata, canonical URLs, Open Graph/Twitter metadata, JSON-LD, sitemap coverage, internal links, local assets, verified AdSense tags, restaurant data, and calculator entry points.
- Both audits run from `tools/build_site.sh`, so future regeneration cannot silently drop the visual system.

## QA completed

- Static contract: 118 pages.
- SEO/site validator: 118 HTML files, 117 indexable pages, 117 sitemap URLs, and 116 searchable resources.
- Responsive browser matrix: eight representative page types at 375, 390, 430, 768, and 1440 px (40 rendered combinations), with no horizontal overflow, H1 clipping, missing main landmark, or undersized base type.
- Visual browser review: homepage hero and bento grid, meal-finder hero/forms/quiz cards, calculator hub, and a long-form article.
- Console review: no errors or warnings on the representative matrix.
- Calculation test: unit conversions, BMR, TDEE, goal adjustments, and macro energy balance pass.

## Performance and advertising safeguards

- No WebGL, animation framework, external UI library, heavy parallax, pointer trail, or autoplay media was added.
- Liquid effects use CSS and tiny progressive-enhancement scripts. Core content renders without JavaScript.
- No URLs, titles, H1s, article bodies, restaurant facts, source links, schema, canonical tags, sitemap entries, or advertising identifiers were removed by this visual pass.
- Existing AdSense auto-ad anchors and the verified publisher loader remain present; ad placement is not simulated with fake containers.
