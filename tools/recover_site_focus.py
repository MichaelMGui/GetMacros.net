#!/usr/bin/env python3
"""Apply the durable GetMacros content-pruning and technical SEO recovery."""
from __future__ import annotations

import csv
import datetime
import html
import io
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from focus_components import PUBLISHER, SITE, THEME_BOOT, footer, head, nav
from site_scope import KEEP_ROOT_HTML, decision_for, section_for

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "tools" / "recovery-baseline.json"
SEO_BASELINE = ROOT / "tools" / "seo-baseline.json"
REPORT = ROOT / "adsense-recovery-report.md"
TRUST = {"about.html", "contact.html", "privacy.html", "terms.html", "editorial-policy.html",
         "corrections.html", "accessibility.html", "sources.html"}


def clean_text(value: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value))).strip()


def match_text(text: str, pattern: str) -> str:
    match = re.search(pattern, text, re.I | re.S)
    return clean_text(match.group(1)) if match else ""


def metadata(path: Path) -> dict[str, str | bool]:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    robots = match_text(text, r'<meta\s+name=["\']robots["\'][^>]*content=["\'](.*?)["\']')
    desc = match_text(text, r'<meta\s+name=["\']description["\'][^>]*content=["\'](.*?)["\']')
    if not desc:
        desc = match_text(text, r'<meta\s+content=["\'](.*?)["\'][^>]*name=["\']description["\']')
    return {
        "path": rel,
        "title": match_text(text, r"<title[^>]*>(.*?)</title>"),
        "h1": match_text(text, r"<h1[^>]*>(.*?)</h1>"),
        "meta": desc,
        "indexable": "noindex" not in robots.casefold(),
    }


def snapshot() -> list[dict]:
    if BASELINE.exists():
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    pages = [metadata(p) for p in sorted(ROOT.rglob("*.html"))]
    BASELINE.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def assert_scope() -> None:
    missing = sorted(path for path in KEEP_ROOT_HTML if not (ROOT / path).exists())
    if missing:
        raise SystemExit("Focused allowlist contains missing pages: " + ", ".join(missing))
    if len(KEEP_ROOT_HTML) < 50:
        raise SystemExit("Focused allowlist is unexpectedly small; refusing to prune")


def remove_out_of_scope() -> list[str]:
    targets: list[Path] = []
    for path in ROOT.glob("*.html"):
        if path.name not in KEEP_ROOT_HTML:
            targets.append(path.resolve())
    for language in ("es", "fr"):
        lang_dir = (ROOT / language).resolve()
        if lang_dir.exists():
            targets.extend(p.resolve() for p in lang_dir.rglob("*.html"))
    root = ROOT.resolve()
    for target in targets:
        if root not in target.parents or target.suffix.lower() != ".html":
            raise SystemExit(f"Unsafe prune target: {target}")
    removed: list[str] = []
    for target in sorted(set(targets)):
        removed.append(target.relative_to(root).as_posix())
        target.unlink()
    for language in ("es", "fr"):
        lang_dir = ROOT / language
        if lang_dir.exists() and not any(lang_dir.iterdir()):
            lang_dir.rmdir()
    return removed


def normalize_path(href: str) -> str | None:
    parsed = urlparse(html.unescape(href.strip()))
    if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    value = parsed.path.lstrip("/")
    return value or "index.html"


STALE_REDIRECTS = {
    "tdee-vs-bmr.html": "calculators.html",
    "protein-for-muscle-growth.html": "macros-for-muscle-gain.html",
    "protein-on-a-budget.html": "protein-value-calculator.html",
    "how-to-measure-sweat-rate.html": "sweat-rate-calculator.html",
    "restaurant-nutrition-information.html": "sources.html",
    "nutrition-label-rounding-explained.html": "how-to-read-a-nutrition-label.html",
    "weighing-cooking-oils-and-sauces.html": "how-to-calculate-recipe-nutrition.html",
    "choosing-food-database-entry.html": "how-to-calculate-recipe-nutrition.html",
    "plant-based-protein-sources.html": "high-protein-foods-list.html",
    "how-much-fat-per-day.html": "fats.html",
}


def remove_stale_links(text: str) -> str:
    def replace_anchor(match: re.Match) -> str:
        href = match.group(3)
        target = normalize_path(href)
        if not target or not target.endswith(".html") or target in KEEP_ROOT_HTML:
            return match.group(0)

        full_anchor = match.group(0)
        if re.search(r'class=["\'][^"\']*\b(?:guide-card|explore-card|explore-all)\b', full_anchor, re.I):
            return ""

        replacement = STALE_REDIRECTS.get(target)
        if replacement:
            return (f'<a{match.group(1)}href={match.group(2)}{replacement}'
                    f'{match.group(2)}{match.group(4)}>{match.group(5)}</a>')

        # Ordinary inline links become plain text. This preserves the sentence
        # without pretending a deleted article still has a destination.
        return match.group(5)

    text = re.sub(r'<a\b([^>]*?)href=(["\'])(.*?)\2([^>]*)>(.*?)</a>',
                  replace_anchor, text, flags=re.I | re.S)

    def remove_empty_group(match: re.Match) -> str:
        section = match.group(0)
        return section if re.search(r'class=["\'][^"\']*\b(?:guide-card|explore-card)\b', section, re.I) else ""

    return re.sub(
        r'<section\b[^>]*class=["\'][^"\']*\b(?:guide-group|related-explore)\b[^"\']*["\'][^>]*>.*?</section>',
        remove_empty_group,
        text,
        flags=re.I | re.S,
    )


def common_shell(path: str, text: str) -> str:
    current = ""
    if path in {"healthy-fast-food.html", "restaurant-meal-guides.html"} or "healthy-meals-macros" in path or "healthy-breakfast-macros" in path or "healthy-food-meals-macros" in path or "healthy-subs-macros" in path:
        current = "fastfood"
    elif path == "restaurant-meal-finder.html":
        current = "finder"
    elif path == "calculators.html" or path in {"budget-meal-builder.html", "carbohydrate-label-portion-tool.html", "nutrition-label-comparison-tool.html", "protein-value-calculator.html", "recipe-macro-scaler.html", "sodium-label-comparison-tool.html", "sweat-rate-calculator.html", "weight-goal-timeline-calculator.html"}:
        current = "calculators"
    elif path == "articles.html" or section_for(path) not in {"Site", "Trust", "Tools", "Healthy fast food"}:
        current = "guides"
    elif path == "about.html":
        current = "about"

    text = re.sub(r'<link\b[^>]*hreflang=[^>]*>\s*', "", text, flags=re.I)
    text = re.sub(
        r'<script\b[^>]*src=["\'][^"\']*js/(?:polish|site-motion|studio-v6|atelier-v5|theme-toggle|unified-v7)\.js[^"\']*["\'][^>]*></script>\s*',
        "",
        text,
        flags=re.I,
    )
    if "google-adsense-account" not in text:
        text = re.sub(r"</head>", f'<meta name="google-adsense-account" content="{PUBLISHER}"></head>', text, count=1, flags=re.I)
    if "readability-v2.css" not in text:
        text = re.sub(r"</head>", '<link rel="stylesheet" href="css/readability-v2.css?v=20260823d"></head>', text, count=1, flags=re.I)
    text = re.sub(r'<meta name="theme-color" content="#[0-9a-fA-F]{6}">', '<meta name="theme-color" content="#f4f7f2">', text, flags=re.I)
    if '<meta name="theme-color"' not in text:
        text = re.sub(r"</head>", '<meta name="theme-color" content="#f4f7f2"></head>', text, count=1, flags=re.I)
    # Rebuild the final cascade as a unit. Editorial v8 follows the unified
    # layer and its contrast repair because it owns the final page openings.
    text = re.sub(r'<link\b[^>]*href=["\'][^"\']*css/(?:theme|theme-fix|unified-v7|editorial-v8|clean-v9)\.css[^"\']*["\'][^>]*>\s*', "", text, flags=re.I)
    text = re.sub(r'<script>[^<]*gm-theme[^<]*</script>\s*', "", text, flags=re.I)
    text = re.sub(r"</head>", THEME_BOOT
                  + '<link rel="stylesheet" href="css/unified-v7.css?v=20260828g">'
                  + '<link rel="stylesheet" href="css/theme-fix.css?v=bb1ce922e4">'
                  + '<link rel="stylesheet" href="css/editorial-v8.css?v=20260830a">'
                  + '<link rel="stylesheet" href="css/clean-v9.css?v=ca9487b834"></head>',
                  text, count=1, flags=re.I)
    page_title = match_text(text, r"<title[^>]*>(.*?)</title>")
    page_desc = match_text(text, r'<meta\s+name=["\']description["\'][^>]*content=["\'](.*?)["\']')
    social = (
        (r'<meta\s+property=["\']og:title["\'][^>]*>', f'<meta property="og:title" content="{html.escape(page_title, quote=True)}">'),
        (r'<meta\s+property=["\']og:description["\'][^>]*>', f'<meta property="og:description" content="{html.escape(page_desc, quote=True)}">'),
        (r'<meta\s+name=["\']twitter:title["\'][^>]*>', f'<meta name="twitter:title" content="{html.escape(page_title, quote=True)}">'),
        (r'<meta\s+name=["\']twitter:description["\'][^>]*>', f'<meta name="twitter:description" content="{html.escape(page_desc, quote=True)}">'),
    )
    for pattern, replacement in social:
        text = re.sub(pattern, replacement, text, count=1, flags=re.I)
    shell = nav(current)
    # Some legacy pages place a page-specific <style> block between the skip
    # link and header. Replace the two elements independently so that CSS stays.
    text = re.sub(r'<a\b[^>]*class=["\'][^"\']*skip-link[^"\']*["\'][^>]*>.*?</a>', "", text, count=1, flags=re.I | re.S)
    if re.search(r'<header\b', text, re.I):
        text = re.sub(r'<header\b.*?</header>', shell, text, count=1, flags=re.I | re.S)
    else:
        text = re.sub(r'(<body\b[^>]*>)', r'\1' + shell, text, count=1, flags=re.I)
    if re.search(r'<footer\b', text, re.I):
        text = re.sub(r'<footer\b.*?</footer>', footer(), text, count=1, flags=re.I | re.S)
    else:
        text = re.sub(r'</body>', footer() + '</body>', text, count=1, flags=re.I)
    return remove_stale_links(text)


def normalize_survivors() -> None:
    for name in sorted(KEEP_ROOT_HTML):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        text = common_shell(name, text)
        path.write_text(text, encoding="utf-8")


def is_indexable(item: dict) -> bool:
    return bool(item["indexable"] and item["path"] != "404.html")


def build_search(final: list[dict]) -> None:
    """Build the search page.

    The old version emitted one flat list of every page as a full-bleed card,
    each with the same section word above a headline set at hero scale. Fifty-six
    of those in a row read as a wall of unlabelled text rather than a library --
    nothing told you what any group was, so the bottom of the page looked like
    leftovers. This version leads with a small set of starting points, then
    groups the rest under a heading per section with a count, and sets each hit
    as a row rather than a poster.
    """
    items = [item for item in final if is_indexable(item) and item["path"] != "search.html"]

    # The five things most people arrive wanting. Shown before the library so
    # the page answers "what is here" before it answers "what matches".
    starts = [
        ("restaurant-meal-finder.html", "Match", "Healthy Order Match",
         "Answer five questions and get ranked meals from 15 chains."),
        ("calculators.html", "Targets", "Free macro calculator",
         "Daily calories, protein, carbs and fat, with the assumptions shown."),
        ("healthy-fast-food.html", "Compare", "Healthy fast food",
         "83 complete orders ranked for cutting, bulking and high protein."),
        ("restaurant-meal-guides.html", "Browse", "Restaurant guides",
         "Every chain we track, with official nutrition sources."),
        ("articles.html", "Learn", "Nutrition guides",
         "What the numbers mean, and how to use them at the next meal."),
    ]
    start_tiles = "".join(
        f'<a class="search-start-tile" href="{path}">'
        f'<span class="search-start-num">{index:02d} &middot; {html.escape(kicker)}</span>'
        f'<span class="search-start-name">{html.escape(name)}</span>'
        f'<span class="search-start-copy">{html.escape(copy)}</span></a>'
        for index, (path, kicker, name, copy) in enumerate(starts, start=1))

    # Group order puts the product first and the housekeeping pages last, so
    # scrolling to the bottom lands on something that is meant to be there.
    order = ["Healthy fast food", "Tools", "Macros and goals", "Labels and recipes",
             "Protein and food", "Journal", "Trust", "Site"]
    blurbs = {
        "Healthy fast food": "Chain-by-chain menus, rankings and the meal finder.",
        "Tools": "Calculators that answer one question each.",
        "Macros and goals": "How to set and adjust the numbers for a goal.",
        "Labels and recipes": "Reading a label and doing the math on real food.",
        "Protein and food": "Food-level guides behind the protein numbers.",
        "Journal": "Longer answers to questions worth the space.",
        "Trust": "How the site is written, sourced and corrected.",
        "Site": "Everything else.",
    }
    grouped: dict[str, list[dict]] = {}
    for item in items:
        grouped.setdefault(section_for(str(item["path"])), []).append(item)
    for group in grouped.values():
        group.sort(key=lambda item: str(item["h1"] or item["title"]))

    total = 0
    blocks = []
    for section in order + [s for s in sorted(grouped) if s not in order]:
        group = grouped.get(section)
        if not group:
            continue
        hits = []
        for item in group:
            haystack = f'{item["title"]} {item["h1"]} {item["meta"]} {section}'.casefold()
            hits.append(
                f'<a class="search-hit" href="{item["path"]}" '
                f'data-search="{html.escape(haystack, quote=True)}">'
                f'<span class="search-hit-name">{html.escape(str(item["h1"] or item["title"]))}</span>'
                f'<span class="search-hit-copy">{html.escape(str(item["meta"]))}</span></a>')
        total += len(group)
        blocks.append(
            f'<section class="search-group" data-group>'
            f'<div class="search-group-head"><h2>{html.escape(section)}</h2>'
            f'<span class="search-group-count" data-count>{len(group)}</span></div>'
            f'<p class="search-group-note">{html.escape(blurbs.get(section, ""))}</p>'
            f'<div class="search-hits">{"".join(hits)}</div>'
            f'<p class="search-group-more" data-more hidden></p></section>')

    title = "Search Healthy Fast Food, Macro Tools & Guides | GetMacros"
    desc = ("Search every GetMacros page at once: healthy fast-food menu guides, "
            "restaurant comparisons, macro calculators and nutrition explainers.")
    # `perGroup` rather than one global cap: capping the first twelve rows
    # overall showed twelve restaurants and hid every other section, so the
    # page opened looking like one list again. Four from each section shows
    # what the library is made of before you expand it. `limit` is the point
    # below which expanding would be pointless.
    script = """(function(){
var q=document.getElementById('site-search'),
    hits=[].slice.call(document.querySelectorAll('.search-hit')),
    groups=[].slice.call(document.querySelectorAll('[data-group]')),
    status=document.getElementById('search-status'),
    toggle=document.getElementById('search-results-toggle'),
    startBlock=document.getElementById('search-start'),
    limit=12,perGroup=4,expanded=false;
function words(value){return value.toLowerCase().match(/[a-z0-9]+/g)||[];}
function run(){
  var terms=words(q.value),matched=0,shown=0;
  groups.forEach(function(group){
    var rows=[].slice.call(group.querySelectorAll('.search-hit')),live=0,kept=0;
    rows.forEach(function(hit){
      var hay=words(hit.dataset.search).join(' '),
          match=!terms.length||terms.every(function(t){return hay.indexOf(t)>-1;});
      if(match)live++;
      var visible=match&&(terms.length||expanded||kept<perGroup);
      if(visible)kept++;
      hit.hidden=!visible;
    });
    matched+=live;shown+=kept;
    var count=group.querySelector('[data-count]');
    if(count)count.textContent=live;
    var more=group.querySelector('[data-more]');
    if(more){var rest=live-kept;more.hidden=rest<1;more.textContent='+'+rest+' more in this section';}
    group.hidden=!live;
  });
  if(startBlock)startBlock.hidden=!!terms.length;
  if(terms.length)status.textContent=matched?matched+' match'+(matched===1?'':'es')+' for \u201c'+q.value.trim()+'\u201d':'Nothing matches \u201c'+q.value.trim()+'\u201d yet. Try a chain, a macro or a tool.';
  else status.textContent=expanded?'Showing all '+matched+' pages':'Showing '+shown+' of '+matched+' pages';
  toggle.hidden=!!terms.length||hits.length<=limit;
  toggle.setAttribute('aria-expanded',String(expanded));
  toggle.textContent=expanded?'Show fewer':'Show all '+hits.length+' pages';
}
q.addEventListener('input',function(){expanded=false;run();});
toggle.addEventListener('click',function(){
  expanded=!expanded;run();
  if(!expanded)document.querySelector('.search-library').scrollIntoView({behavior:'smooth',block:'start'});
});
var initial=new URLSearchParams(location.search).get('q');
if(initial)q.value=initial;
run();
})();"""
    body = f'''{head("search.html", title, desc)}<body class="site-v3 recovery-page search-page">{nav()}
<main id="main-content"><section class="search-hero"><div class="container"><p class="eyebrow">Search GetMacros</p><h1>Find a restaurant, tool or nutrition guide</h1><p>Every page on GetMacros in one place: healthy fast food, macro tools, and the guides that help you use them.</p>
<label class="search-box" for="site-search"><span>What are you looking for?</span><input id="site-search" type="search" placeholder="Try &ldquo;Chipotle,&rdquo; &ldquo;high protein&rdquo; or &ldquo;recipe macros&rdquo;" autocomplete="off"></label><p id="search-status" aria-live="polite">Showing 12 of {total} pages</p></div></section>
<section class="search-start" id="search-start"><div class="container"><div class="search-start-head"><p class="eyebrow">Start here</p><h2>The five people ask for most</h2></div><div class="search-start-grid">{start_tiles}</div></div></section>
<section class="search-library"><div class="container"><div class="search-library-head"><p class="eyebrow">The whole library</p><h2>Everything, grouped by what it does</h2></div>{"".join(blocks)}<div class="search-results-actions"><button class="search-results-toggle" id="search-results-toggle" type="button" aria-controls="search-results" aria-expanded="false">Show all {total} pages</button></div></div></section></main>{footer()}
<script>{script}</script></body></html>'''
    (ROOT / "search.html").write_text(body, encoding="utf-8")


def build_sitemap(final: list[dict]) -> None:
    paths = sorted(str(item["path"]) for item in final if is_indexable(item))
    urls = []
    for path in paths:
        loc = f"{SITE}/" if path == "index.html" else f"{SITE}/{path}"
        # lastmod from the file's own mtime rather than a build-wide constant:
        # stamping every page with today's date on every build tells a crawler
        # the whole site changed when one guide did, which is the fastest way
        # to have the signal ignored.
        stamp = datetime.date.fromtimestamp((ROOT / path).stat().st_mtime).isoformat()
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{stamp}</lastmod></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")


def build_feed(final: list[dict]) -> None:
    guides = [item for item in final if is_indexable(item) and section_for(str(item["path"])) not in {"Site", "Trust", "Tools"}][:20]
    items = "".join(f'<item><title>{html.escape(str(i["title"]))}</title><link>{SITE}/{i["path"]}</link><guid>{SITE}/{i["path"]}</guid><description>{html.escape(str(i["meta"]))}</description></item>' for i in guides)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>GetMacros Nutrition Guides</title><link>{SITE}/</link><description>Healthy fast-food comparisons, macro tools and practical nutrition guides.</description>{items}</channel></rss>'''
    (ROOT / "feed.xml").write_text(xml, encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    handle = io.StringIO(newline="")
    # Keep reports byte-stable across Windows and Linux builds.
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    content = handle.getvalue()
    if path.exists() and path.read_text(encoding="utf-8-sig") == content:
        return
    try:
        path.write_bytes(("\ufeff" + content).encode("utf-8"))
    except PermissionError:
        # Spreadsheet apps on Windows may hold an audit CSV open. That report
        # must not prevent the site, sitemap and validation work from finishing.
        print(f"WARNING: skipped locked report file: {path.name}")


def primary_intent(path: str, title: str) -> str:
    if path == "index.html": return "healthy fast food and macro calculator"
    if path == "healthy-fast-food.html": return "healthy fast food options"
    if path == "restaurant-meal-finder.html": return "healthy order match fast-food quiz"
    if path == "restaurant-meal-guides.html": return "healthy fast-food restaurant guides"
    if path == "calculators.html": return "macro calculator and nutrition tools"
    if path == "articles.html": return "nutrition guides for macros and meals"
    if "healthy" in path and "macros" in path: return clean_text(title).removesuffix(" | GetMacros").casefold()
    return clean_text(title).removesuffix(" | GetMacros").casefold()


def build_reports(baseline: list[dict], final: list[dict], removed: list[str]) -> None:
    old = {str(item["path"]): item for item in baseline}
    if SEO_BASELINE.exists():
        for item in json.loads(SEO_BASELINE.read_text(encoding="utf-8")):
            old.setdefault(str(item["path"]), {}).update(item)
    new = {str(item["path"]): item for item in final}
    removed_set = set(removed) | (set(old) - set(new))
    removed_rows = []
    for path in sorted(removed_set):
        decision, reason = decision_for(path)
        removed_rows.append({"old URL/path": "/" + path, "action": "404 (file removed)", "reason": reason,
                             "redirect target if any": ""})
    write_csv(ROOT / "removed-urls.csv", ["old URL/path", "action", "reason", "redirect target if any"], removed_rows)

    seo_rows = []
    for path in sorted(new):
        before, after = old.get(path, {}), new[path]
        if any(str(before.get(key, "")) != str(after.get(key, "")) for key in ("title", "h1", "meta")):
            seo_rows.append({"URL": "/" if path == "index.html" else "/" + path,
                "old title": before.get("title", ""), "new title": after["title"],
                "old H1": before.get("h1", ""), "new H1": after["h1"],
                "old meta description": before.get("meta", ""), "new meta description": after["meta"],
                "primary intent": primary_intent(path, str(after["title"]))})
    write_csv(ROOT / "seo-changes.csv", ["URL", "old title", "new title", "old H1", "new H1", "old meta description", "new meta description", "primary intent"], seo_rows)

    audit_rows = []
    for path in sorted(set(old) | set(new)):
        decision, reason = decision_for(path)
        audit_rows.append({"path": path, "section": section_for(path), "decision": decision, "reason": reason,
                           "final indexability": "indexable" if path in new and is_indexable(new[path]) else "not indexable / removed",
                           "replacement/redirect if relevant": ""})
    write_csv(ROOT / "content-audit.csv", ["path", "section", "decision", "reason", "final indexability", "replacement/redirect if relevant"], audit_rows)

    kept = sum(1 for item in final if is_indexable(item))
    report = f'''# GetMacros AdSense and SEO recovery report

## Outcome

GetMacros now has one explicit product purpose: help people find fast-food meals that fit calories, protein and practical goals, then provide the tools and focused education needed to understand those numbers. The indexable footprint was reduced from {sum(1 for i in baseline if i['indexable'])} pages to {kept}; {len(removed_set)} HTML URLs were removed rather than redirected to unrelated destinations.

## What was wrong

- The homepage promoted article quantity instead of the site's distinctive restaurant data and tools.
- Hundreds of broad medical, academic-biochemistry, trend-diet, quiz, game and worksheet pages diluted topical focus.
- The calculators hub mixed useful macro tools with condition-specific planners.
- Restaurant guides exposed only a small portion of the central data and repeated near-identical editorial copy.
- Primary navigation and partial translations made the product look broader and less complete than it was.

## Structural changes made

- Established an explicit allowlist around healthy fast food, core tools, trust pages and a curated supporting guide library.
- Removed {len(removed_set)} out-of-scope HTML URLs from navigation, search, sitemap and the published file tree. No mass homepage redirects were created; URLs without a true equivalent correctly resolve as missing pages.
- Removed partial Spanish and French footprints and stale hreflang references.
- Simplified the site-wide navigation to Healthy Fast Food, Healthy Order Match, Macro Calculator, Nutrition Guides and About, with Search as a utility action.
- Rebuilt client-side search and XML sitemap exclusively from surviving indexable content.
- Changed the routine build so removed quizzes, games, glossary entries and broad articles cannot be regenerated.

## Homepage and healthy fast food

- Rebuilt the homepage around real repository data: 83 tracked options across 15 chains, a real meal example, goal pathways, cross-chain rankings, chain access, a compact macro calculator and transparent methodology.
- Removed the “340 guides” claim and broad condition/topic directories.
- Rebuilt the Healthy Fast Food hub with explicit search intent, complete-meal safeguards, cross-chain protein/calorie/fibre/sodium comparisons, goal definitions, restaurant directory and limitations.
- Kept substantial static meal-finder rankings and explanatory content available before JavaScript interaction.

## Restaurant pages upgraded

- Rebuilt all 15 chain guides from `js/meal-data.js`, exposing all 83 tracked menu records rather than teaser rows.
- Added chain-specific titles, H1s, introductions and ordering guidance.
- Added full nutrient tables, high-protein, substantial lower-calorie, higher-energy and supported vegetarian picks.
- Added transparent protein grams per 100 calories with its formula and a warning that it is not a health score.
- Preserved official restaurant sources, an August 2026 checked date, missing-value semantics and menu-change disclaimers.

## Tools, guides and trust

- Focused the calculators hub on macro, label, recipe, budget, hydration and restaurant-decision tools.
- Rebuilt the article hub as a curated guide library tied to macros, food decisions, meal building, training and eating out.
- Updated About with truthful editorial ownership, data methodology, independence, limitations and corrections information.
- Standardized footer access to About, Editorial Policy, Sources, Corrections, Privacy, Terms, Accessibility and Contact.
- Preserved the verified AdSense publisher ID and `ads.txt` record; obsolete third-party ad code is rejected by validation.

## SEO and technical changes

- Aligned the homepage, Healthy Fast Food hub, Healthy Order Match, directory and 15 restaurant pages with natural search intent.
- Regenerated canonical sitemap and search coverage from the final indexable set.
- Removed broken internal links and incomplete-language alternates.
- Added or preserved unique title, description, canonical, Open Graph, Twitter and valid JSON-LD requirements through automated validation.
- Continuous integration now performs a deterministic rebuild before validating links, metadata, structured data, accessibility basics and advertising configuration.

## Remaining legitimate risks

- AdSense approval cannot be guaranteed; Google makes the decision and may consider account history, traffic, policy signals and crawl timing outside this repository.
- Restaurant menus change. The site links to official sources and must continue periodic human rechecks.
- The available in-app browser runtime did not initialize during this work, so automated source/mobile CSS checks replace a final interactive browser pass. A production-device spot check remains prudent after deployment.
- No Search Console verification token was present in this repository. Nothing was removed; if verification is DNS-based or injected by hosting it remains external.

## Manual actions requiring external access

- Deploy the rebuilt files, submit the focused sitemap in Search Console and request recrawling for the homepage, Healthy Fast Food hub and restaurant guides.
- Confirm the AdSense consent message/CMP in the AdSense account for EEA, UK and Switzerland; this setting is account-side, not safely implementable from static source alone.
- Reapply for AdSense only after Google has crawled the new focused site and production smoke tests pass.
'''
    if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
        REPORT.write_text(report, encoding="utf-8")


def main() -> int:
    baseline = snapshot()
    assert_scope()
    removed = remove_out_of_scope()
    normalize_survivors()
    first_final = [metadata(ROOT / path) for path in sorted(KEEP_ROOT_HTML)]
    build_search(first_final)
    normalize_survivors()
    final = [metadata(ROOT / path) for path in sorted(KEEP_ROOT_HTML)]
    build_sitemap(final)
    build_feed(final)
    build_reports(baseline, final, removed)
    inventory = ROOT / "url-inventory-baseline.txt"
    if inventory.exists():
        try:
            inventory.unlink()
        except PermissionError:
            # A desktop preview may temporarily hold this non-published audit aid.
            pass
    for language in ("es", "fr"):
        directory = ROOT / language
        if directory.exists() and not any(directory.iterdir()):
            shutil.rmtree(directory)
    print(f"focused site: {sum(1 for i in final if is_indexable(i))} indexable pages; {len(removed)} files pruned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
