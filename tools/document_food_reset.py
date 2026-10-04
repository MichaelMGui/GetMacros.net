"""Record actual release evidence; distinguish visual review from automated rendering."""
from pathlib import Path
import csv,gzip,html,json,re,statistics
from redesign_inventory import family
R=Path(__file__).resolve().parents[1];O=R/'docs/food-reset-2026-10-03';O.mkdir(exist_ok=True)
reviewed=set(['index.html','restaurant-meal-finder.html','calculators.html','nutrition-label-comparison-tool.html','recipe-macro-scaler.html','protein-value-calculator.html','budget-meal-builder.html','chipotle-healthy-meals-macros.html','articles.html','blog.html','how-to-read-a-nutrition-label.html','sources.html','search.html','contact.html','privacy.html','404.html','healthy-fast-food.html','restaurant-meal-guides.html','sodium-label-comparison-tool.html','carbohydrate-label-portion-tool.html','sweat-rate-calculator.html','weight-goal-timeline-calculator.html','editorial-policy.html','corrections.html','accessibility.html','terms.html'])
plain=lambda s: re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>',' ',s))).strip()
rows=[];queries=[]
for route in ['/',*('/'+p.name for p in sorted(R.glob('*.html')))]:
 name=route[1:] or 'index.html';text=(R/name).read_text(encoding='utf-8');kind=family(name,text)
 title=plain(re.search(r'<title>(.*?)</title>',text,re.S)[1]);heading=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',text,re.S)[1])
 manual=name in reviewed
 rows.append(dict(route=route,template=kind,visual_status='Representative screenshot visually reviewed; see after/' if manual else 'Shared family migrated; this individual page render-checked, not manually inspected',copy_status='Task labels shortened; factual/legal copy and disclosures retained; duplication report reviewed',SEO_status='Unique metadata, canonical, sitemap and internal-link checks passed',responsive_status='Automated Chromium/WebKit: 320,390,768,1024,1280,1440; both themes',interaction_status='Relevant core journeys tested; individual reading links checked automatically',verification_performed='Route matrix + link/metadata checks; '+('manual screenshot review' if manual else 'no individual manual visual claim'),remaining_issues='No known route-specific blocker; see report for physical-device/accessibility/field-data limits'))
 action={'home':'Find my meal','finder':'Refine, view, save or compare an order','restaurant':'Open tracked orders and restaurant sources','calculator-hub':'Calculate daily macros','calculator':'Calculate or compare portions','journal':'Read a relevant article','article':'Follow sources and related tools','reference-index':'Choose a guide or restaurant','meal-ideas':'Choose and adjust a meal idea','search':'Search or open a matching result','trust':'Read source/method/corrections information','legal':'Read terms and privacy limits','contact':'Prepare an email draft','error':'Find a meal or search'}.get(kind,'Follow relevant source or tool')
 queries.append(dict(route=route,title=title,primary_user_intent=heading,intent_basis='Repository heading and task; qualitative, not measured search volume',unique_value=action,next_action=action))
for name,data in [('coverage.csv',rows),('query-to-page.csv',queries)]:
 with (O/name).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
assets=['css/publication.css','js/meal-view.js','js/meal-finder.js','js/meal-guide.js','js/food-experience.js','js/food-characters.js','images/food-characters.svg','fonts/gabarito-latin.woff2']
(O/'asset-sizes.json').write_text(json.dumps([dict(asset=f,bytes=(R/f).stat().st_size,gzipBytes=len(gzip.compress((R/f).read_bytes()))) for f in assets],indent=2),encoding='utf-8')
perf=[]
for page in ['index.html','calculators.html','restaurant-meal-finder.html']:
 values=[]
 for stage in ['before','after']:
  data=json.loads((O/f'performance-{stage}-final.json').read_text())['results'];sample=[r for r in data if r['page']==page]
  values.append(dict(stage=stage,lcpMs=statistics.median(r['lcp'] for r in sample),cls=statistics.median(r['cls'] for r in sample),longTaskExcessMs=statistics.median(r['longTasks'] for r in sample)))
 perf.append(dict(page=page,samples=values))
(O/'performance-summary.json').write_text(json.dumps(perf,indent=2),encoding='utf-8')
table='\n'.join(f"| {r['page']} | {r['samples'][0]['lcpMs']/1000:.3f}s | {r['samples'][1]['lcpMs']/1000:.3f}s | {r['samples'][1]['cls']:.6f} |" for r in perf)
(O/'report.md').write_text(f'''# GetMacros food-character visual reset

Implemented October 3–4, 2026. Baseline: f5837976c812949efaca3ca20af6990de30edf1b. This release replaces the active presentation while preserving the existing static HTML product, data and URLs.

## What changed

- New Gabarito/Inter typography, warm open canvas, quiet rules and independently styled green-neutral night theme. No alternate Fresh/Harvest palettes. Original ingredient silhouettes replace the animal companions. Gabarito is self-hosted under its bundled SIL Open Font License.
- New homepage: one task, egg/strawberry/broccoli ensemble, four actual orders, one compact quiz invitation, open restaurant directory, concise tools and an editorial feature. Counts come from the dataset; “On the menu” makes no popularity claim.
- **One quiz implementation.** Hero and lower invitation open the same dialog. The homepage no longer embeds a second full finder below the hero. The finder offers the same quiz as an optional route into its controls. Four steps, no preselected answers, explicit resume, back/fresh/close, honest limits and shareable result state.
- Shared nutrition-specific meal rows: exact order and portion, calories/protein, quiet Save/Compare and native View meal disclosure containing full nutrients, serving assumptions and provenance. Unknown is “Not verified”; genuine zero remains zero. Filtering/ranking formulas unchanged.
- Quiet desktop sidebar and mobile filter sheet; restaurant, calories and protein first. Other priorities, nutrient limits and ingredient preferences are available on request. Active filters, clear/reset, sorting, result count, comparisons and sharing retained.
- Simple five-item navigation, responsive open menus, expanding native quick search, theme/motion settings, complete footer/trust navigation. SVG icons use consistent strokes; chain pictograms are original food-category marks, not official restaurant logos.
- Macro inputs grouped into About you → Activity → Goal, with an All inputs alternative and unchanged formulas. Other tools share deliberate fields/results and progressive explanations. Learn categories and restaurant tables/comparisons expand on request; article/legal sources remain readable and available.
- Liquid button highlights, gliding navigation, finite selected/saved feedback, finite character greetings/reactions and restrained result movement. No scroll-text reveal, blur, count-up nutrition, scroll interception or perpetual bouncing. Character idle reactions run only while the homepage scene is visible; Calm motion and system reduced-motion suppress them.
- Fixed two real interaction faults found during QA: numeric filter blur rebuilding the clicked meal before its disclosure could open; calculator input blur clearing a newly submitted result. Neither fix changes arithmetic or ranking.
- Removed active animal companion script/SVG/style, old display font imports and obsolete CSS rules. The builder assembles four intentional style sources into one stylesheet; the existing 70 KB guard remains unchanged. Old historical reports/tools are preserved but excluded from publishing.

## Coverage and evidence

`coverage.csv`: **107 public URLs, including / and /index.html; 106 HTML files**. All have the shared system. The inventory distinguishes manual screenshots from automated per-page rendering. Development fixtures/reports are excluded through the existing Pages configuration. No URLs were renamed.

Local Edge/Chromium and WebKit: **2,568 route/viewport checks** (107 × six widths × two themes × two engines), plus **56 resilience checks**. The matrix checks rendering, overflow, headings, IDs, labels, assets and runtime errors. Resilience checks include enlarged text, missing images, open menus/Escape, no-JavaScript navigation, system theme/first-frame/persistence. Reading-page link checks are programmatic, not a claim of individually clicking every source on the internet.

Eight core journey runs: quiz choices/back/resume/cancel, URL results, no matches/reset, saves, three-meal comparison, share, print, mobile menu, guided macro inputs, validation, units, theme and motion preference. Eight additional runs exercise quick search, native nutrition disclosure, numeric filters, every calculator family, simple-meal filters, article/restaurant anchor disclosure, no-result search and email-copy/draft links. Four animation-enabled runs verify liquid hover, navigation glide, finite character reactions, quiz selection, Calm persistence and reduced motion. `routes/`, `journeys/`, `details/` and `motion-checks.json` contain the actual results.

**26 representative routes captured** in `after/` at 390/1440 in both themes, plus quiz/open-menu states. All 26 have had a representative screenshot visually reviewed; key home/finder/calculator/quiz layouts were reviewed repeatedly in both themes. This is not manual inspection of all 107 URLs. Earlier baseline captures are in `before/`. Screenshots are real browser output, not mockups.

44 semantic text/action/control/focus color pairs pass the script's 4.5:1 text / 3:1 control thresholds in both themes. This does not certify every pixel, screen reader, device or WCAG criterion. Keyboard and native-dialog behaviors are also exercised in browser journeys.

## Build and functional validation

- Full supported build (`sh tools/build_site.sh`; local Windows equivalent `python tools/run_food_build.py`): 106 HTML, 105 indexable sitemap URLs, 104 search resources, **5,062 internal links/anchors**. Shared stylesheet remains under 70 KB. Verification retained; no automatic ad loader.
- `node tools/test_macro_math.js`: conversions, BMR, TDEE, goals and macro energy balance pass.
- `node tools/test-companion-engine.cjs`: 21/21 strict limits, missing values, genuine zero, ranking, URL state and immutable audited data checks pass.
- `node tools/test-meal-view.cjs`: missing/zero, units, portions, sources, factual reasons and HTML escaping pass; included in CI.
- `python tools/test-release-content.py`: 33 unique resources, 183 source facts, 142 nutrition rows, 41 audited records, seven ingredient sums, lossless provenance/partial dates pass.
- Repeating the full build produced identical hashes for all 106 pages. Final static/source gates pass after the last spacing changes.
- Browser commands: `node tools/test-food-routes.cjs --fast`, `node tools/test-food-journeys.cjs`, `node tools/test-food-details.cjs`, `node tools/test-food-motion.cjs`, `node tools/capture-food-reset.cjs`.

## Performance: lab only

Local Edge, 390×844, cold cache, 100 ms network latency, 1.6 Mbps download and 4× CPU slowdown; three runs/page, before then after without concurrent browser work. Median largest-content paint:

| Page | Before | After | After layout shift |
|---|---:|---:|---:|
{table}

The calculator and finder paint slightly later; the new font/art add bytes. Homepage paint is similar. After measurements show no long-task time over the test's 50 ms threshold, with zero/negligible layout shift. No claim of field Core Web Vitals, universal speed or an AdSense “HTML speed” score. Raw samples and asset raw/gzip sizes are supplied.

## Copy, content and search

Shortened task headings, button labels, hero copy and introductions; removed redundant labels/ordinal badges and duplicate finder output on the homepage. Reduced initial information density through native disclosure without deleting useful source content. The repetition report covers 73 established authored pages; 33 source-defined resources have a separate content gate. Its 10 sentence groups, seven heading groups and two near-paragraph pairs were reviewed: remaining repetitions are actual meal names/serving definitions reproduced consistently in catalogue/reference/finder views, not marketing introductions. Necessary disclosures are retained.

Existing restaurant dataset/provenance files and calculator formulas are unchanged. Scope remains **83 recorded orders at 15 U.S. chains**, with five incomplete core records excluded by the default complete-record filter. No new photos, synthetic exact meals, dietary promises, prices, authors or verification dates were invented. Generic simple-meal plate art is identified as meal ideas, not restaurant photography. The new layered cast is original code-native SVG; source builder retained.

Current live research is recorded in `seo-research.md`: primary Google helpful-content/faceted-navigation/JavaScript guidance plus one qualitative high-protein query and a primary restaurant announcement. No current Search Console account access, traffic export or keyword-volume measurements. `query-to-page.csv` maps existing page intent and next action; its intent is inferred from the repository, not measured demand. Preserve canonical/indexability/filter strategy, crawlable real links, static meal content and citations; do not create keyword-variant pages or fake review schema.

## Release and limits

Production release uses the user's existing authorization to push live. `tools/verify-food-live.cjs` checks all 107 live bodies, 15 key assets, real custom 404, and four mobile/desktop theme journeys after deployment. Its result is recorded separately; deployment is not inferred from a successful local build.

No known route-specific functional blockers remain in local QA. Exact remaining review limits: physical iOS/Android and assistive-technology testing, field performance, external source availability and independent medical/editorial review. New photography licensing is not a blocker because no photography was introduced. Ad serving remains paused pending the existing account/consent requirements; publisher verification and ads.txt are retained. AdSense acceptance and future traffic are not guaranteed by design changes.
''',encoding='utf-8')
print(f'Documented {len(rows)} public routes, {len(reviewed)} manually reviewed representatives, actual lab samples and release limitations.')
