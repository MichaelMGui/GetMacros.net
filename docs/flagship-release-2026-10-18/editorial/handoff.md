# Four finished editorial resources

Source: `tools/flagship_release/editorial.py` exports `ARTICLES`, a list of four dictionaries containing `route`, `title`, `description`, `market`, `body`, source URLs/IDs, prepared/check dates and intent-overlap notes. Importing does not edit public pages. Calling `export()` writes only this documentation directory.

Run:

```sh
python -X utf8 tools/flagship_release/editorial.py
```

Use the existing article template and shared styles to render each body. Set publication information only when publication actually happens. Add Article/Breadcrumb markup only using the real visible template content; no invented author or medical reviewer. Root must connect these resources to the appropriate restaurant hubs, Learn index, search and sitemap, then test generated comparator links after staged menu records are integrated.

| Route | Purpose |
|---|---|
| `leon-uk-breakfast-muffin-egg-pot-nutrition.html` | Breakfast-format comparison with per-portion values and original published salt. |
| `nandos-uk-quarter-chicken-rice-chips-corn.html` | Same-main/alternative-side order arithmetic, regular versus sharing portions and Northern Ireland distinction. |
| `wendys-uk-breakfast-muffin-wrap-calories-protein.html` | Exact UK muffin/wrap recipes, sauce, salt and branch breakfast availability. |
| `chick-fil-a-canada-grilled-sandwich-fries-sizes.html` | Three complete listed Canadian orders with small, medium or large fries; same main/drink and explicit portion arithmetic. |

All four are authored resources of about 600 words including tables and source sections. Counts are descriptive, not a publication/quality metric. `articles.json` contains the body exports and source evidence. `editorial-checks.json` records source/arithmetic checks. No public HTML, sitemap, registry or stylesheet was modified in this workstream. Native and image artifacts from the earlier assignment remain separate.

Public route rendering, both-theme browser checks, production links and indexing are **not yet verified by this module**. Comparator URLs use staged stable IDs; re-export after any ID normalization before final integration. Source uncertainty and unavailable data remain explicit.

The initially considered Multifruit-versus-fries article was **rejected before integration**: official Canadian product prose says a 90 g pouch while the nutrition table reports 100 g. The market workstream will retain the discrepancy and withhold its composed order. No 90/100 scaling or false resolution was used. The finished Canadian article uses only the unambiguous fry sizes and source-defined tea/sandwich instead.
