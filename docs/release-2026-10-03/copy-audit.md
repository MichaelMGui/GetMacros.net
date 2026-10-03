# Existing-page copy and comparison audit

Audit date: October 3, 2026. This work complements the new resource content gates; it does not replace rendered-page QA.

## Scope and repeatable check

`tools/release_copy_audit.py` examines all **73 existing tracked root HTML routes**, including articles, utilities, legal pages, tools and restaurant guides. It extracts authored headings and paragraphs inside `main`, then reports exact sentences of at least eight words and near-identical paragraphs of at least 25 words. Near matching requires a character similarity of at least 0.94 after a vocabulary prefilter. It also reports unlinked repeated headings of at least four words.

Navigation, footer, linked destination labels, metadata, source lists, named disclosure classes, table records and an explicit list of necessary shared statements are excluded. Tables remain subject to the separate data checks. Exclusions preserve actual ingredient definitions, units, calculation methods, safety caveats and provenance instead of rewriting factual language merely to make it different. Legal copy was included in the initial source inventory and left unchanged.

Run:

```text
python tools/release_copy_audit.py
```

The machine-readable result is `docs/release-2026-10-03/copy-audit.json`. This is a text scan, not a medical review or a claim that every sentence was visually inspected. Articles receiving editorial changes were read in source-text context; the parent release owns screenshots and browser journeys.

## Findings resolved

The first scan found a common “What to take away” heading in four long-form articles. This was not duplicate factual content, but it offered little guidance when skimming. Each article now ends with a specific heading, with the table-of-contents label updated as well:

| Existing route | Targeted change |
| --- | --- |
| `are-diet-drinks-bad-for-you.html` | “Choose drinks by what they replace”; replaced the dramatic “not poison” opening with “Diet drinks are optional.” |
| `calories-vs-macros-what-matters-more.html` | “Start with calories, then check protein and fat”; clearer explanation of energy intake and food composition; simpler finder handoff wording. |
| `does-creatine-cause-hair-loss.html` | “What the evidence means for your decision”; preserved trial descriptions and their limitations. |
| `how-much-protein-can-your-body-absorb.html` | “Plan the daily total, then your meals”; a more specific section heading for absorption versus muscle growth; replaced unexplained “hypertrophy” with “muscle growth.” |

Their factual claims, citations, publication dates and substantive review dates were preserved. These are focused editorial changes, not a claim that the cited nutrition research was reverified today.

During integration, the repeatable scan caught an actual duplicated visible comparison paragraph in every restaurant guide’s `ordering-comparison` section. The restaurant/data owner repaired the source-generation boundary and removed the second copy from all 15 guides. This audit did not edit those guides directly. A subsequent scan confirms those repeated comparison paragraphs no longer appear.

## Existing numerical comparisons synchronized

`healthy-fast-food.html`: all eight ranking groups were recomputed from the current `js/meal-data.js` snapshot using the existing eligibility and sorting rules. Its high-protein `ItemList` matches the visible selection. The selected rows remain U.S. tracked orders, not an exhaustive health ranking. Missing values are not filled with zero.

`best-fast-food-restaurants-for-your-goals.html`: the six-order table was matched by exact chain and order name. The corrected Panda Express Bigger Plate row now shows **1,450 calories, 129 g protein, 3 g fiber and 2,640 mg sodium**, in place of 1,445 / 112 / 1 / 2,410. The portion explanation remains a full fried-rice side plus three chicken entrées. An FDA label-reference link supports the sodium comparison. The missing-nutrient paragraph now explains the current dash/filter behavior rather than describing old removed menu examples.

Only these genuine comparison/data updates received an October 3 modification date. Original publication dates were preserved. This does not assert that every restaurant record was freshly verified; the separate nutrient provenance report identifies the source-inspected subset.

To preserve these six reviewed files after a shared generated-page rebuild, run:

```text
python tools/release_copy_audit.py --apply-reviewed
```

This opt-in step reapplies only the six named pages, then reruns the report. Running the audit without this flag never rewrites HTML. The reviewed step does not edit shared builders, restaurant guides, formulas, data files or new publication JSON.

## Final remaining repetition

The latest run checked **1,989 authored blocks** and reported **five exact sentence groups, three heading groups and one near-paragraph pair**. Every remaining item was inspected in the report:

- Chipotle’s actual ingredient list and the explanation that carbs/sodium are ingredient sums appear in its guide and the homepage meal preview. The same calculation disclosure applies to two separate supported Chipotle builds.
- Subway’s two-six-inch footlong definition appears in its guide and the homepage preview.
- McDonald’s “Extra sides, sauces and drinks are not included” legitimately applies to two separate complete-order definitions.
- The three repeated headings are actual meal names shared by the homepage and finder previews.
- The near-identical paragraph is the exact Chipotle ingredient-serving definition, with the homepage adding “U.S. menu.” Keeping it consistent is desirable.

No remaining reported pair is an interchangeable article introduction or substantive copied article paragraph. This statement is limited to the detector’s thresholds and the current report; it is not proof that all possible repetition has been eliminated.

## Checks performed and limits

- All six comparison table rows compared field-by-field against the current parsed meal data.
- All eight healthy-fast-food ranking groups reproduced with the existing ranking function.
- High-protein list names, positions and guide destinations checked against visible `ItemList` markup.
- Six reviewed files reapplied twice to establish idempotence.
- Existing copy report rerun after the restaurant duplicate fix.

The parent release performs final build, browser, responsive, link and runtime checks. This subtask did not certify accessibility or live deployment.
