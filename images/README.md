# Image manifest — GetMacros.net

This environment's network sandbox blocks every external image host (confirmed
by testing 20+ domains, all returning 403 at the egress proxy), so real stock
photos can't be downloaded from inside a Claude Code session here.

Instead, every food-gallery and diagram figure across the homepage, Protein,
Fat, and Carbs pages uses a **hand-drawn SVG illustration** from the icon
sprite (`icon-sprite.svg` — symbols `icon-chicken`, `icon-egg`, `icon-fish`,
`icon-legume`, `icon-yogurt`, `icon-avocado`, `icon-oil-bottle`, `icon-nut`,
`icon-grain`, `icon-rice-bowl`, `icon-veggie`, `icon-muscle`, `icon-glycogen`,
plus the general icon set). Each renders inside a `.illustration` tile tinted
to its macro category (`tint-protein` / `tint-fat` / `tint-carbs`) — see
`css/style.css`. The homepage's "balanced plate" graphic is a custom inline
multi-color SVG (a pie chart split into protein/fat/carb thirds), not part of
the sprite.

This is a deliberate design choice, not a placeholder: it needs zero external
assets, is crisp at any size, loads instantly, and matches the site's flat
editorial art direction. There is no photo-pending fallback state anymore for
these figures.

## If you want to swap in real photography later

1. Pick a real, licensed photo for the spot you want to replace (stock photo
   service, your own photography, or a properly-attributed Commons file —
   verify the license on the file page before using it).
2. Replace the `<div class="illustration ...">...</div>` block in the
   relevant page with an `<img>` tag pointing at a file in this `/images/`
   folder, keeping the existing `<figcaption>` and adding attribution if the
   license requires it.
3. Commit and push.

The hero background (`--hero-img`) was removed for the same reason — the
gradient background already carries the homepage hero, so no image request
is needed there. Add one back the same way if you'd like a real photo behind
the hero text.
