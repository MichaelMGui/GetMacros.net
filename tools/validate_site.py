#!/usr/bin/env python3
"""Validate GetMacros.net's static pages with only the Python standard library."""
from __future__ import annotations

import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from build_restaurant_pages import CHAIN_CONFIG, item_type, parse_meals
from site_scope import KEEP_ROOT_HTML

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://getmacros.net/"
PUBLISHER = "ca-pub-2316153877942502"
IGNORE_SCHEMES = ("http:", "https:", "mailto:", "tel:", "data:", "javascript:")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.in_h1 = False
        self.h1_parts: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[str] = []
        self.resources: list[str] = []
        self.images_without_alt = 0
        self.canonicals: list[str] = []
        self.jsonld: list[str] = []
        self._json_depth = 0
        self._json_parts: list[str] = []
        self.result_cards: list[str] = []
        self.main_ids: list[str] = []
        self.skip_links = 0

    @staticmethod
    def attrs(values) -> dict[str, str]:
        return {str(k).lower(): (v or "") for k, v in values}

    def handle_starttag(self, tag: str, attrs) -> None:
        a = self.attrs(attrs)
        tag = tag.lower()
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
            self.in_h1 = True
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if a["href"] == "#main-content":
                self.skip_links += 1
        elif tag == "main":
            self.main_ids.append(a.get("id", ""))
        elif tag == "img" and "alt" not in a:
            self.images_without_alt += 1
        if tag in {"img", "script"} and a.get("src"):
            self.resources.append(a["src"])
        if tag == "link":
            if a.get("href"):
                self.resources.append(a["href"])
            if "canonical" in a.get("rel", "").lower().split():
                self.canonicals.append(a.get("href", ""))
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._json_depth = 1
            self._json_parts = []
        if tag == "article" and "result-card" in a.get("class", "").split():
            self.result_cards.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "h1":
            self.in_h1 = False
        elif tag.lower() == "script" and self._json_depth:
            self.jsonld.append("".join(self._json_parts).strip())
            self._json_depth = 0
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)
        if self._json_depth:
            self._json_parts.append(data)


def attr_from_tag(tag: str, name: str) -> str:
    match = re.search(r"\b" + re.escape(name) + r"\s*=\s*([\"'])(.*?)\1", tag, re.I | re.S)
    return match.group(2) if match else ""


def local_target(current: str, href: str) -> str | None:
    clean = unquote(href.strip()).split("#", 1)[0].split("?", 1)[0]
    if not clean or clean.lower().startswith(IGNORE_SCHEMES) or clean.startswith("//"):
        return None
    if clean.startswith("/"):
        target = clean.lstrip("/")
    else:
        target = posixpath.join(posixpath.dirname(current), clean)
    target = posixpath.normpath(target)
    if target in (".", ""):
        target = "index.html"
    if clean.endswith("/"):
        target = posixpath.join(target, "index.html")
    return target


def canonical_for(path: str) -> str:
    if path == "index.html":
        return BASE
    if path.endswith("/index.html"):
        return BASE + path[:-10]
    return BASE + path


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    html_paths = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.html"))
    pages: dict[str, tuple[str, PageParser]] = {}
    titles: dict[str, list[str]] = {}
    descriptions_seen: dict[str, list[str]] = {}
    h1s_seen: dict[str, list[str]] = {}
    canonicals: dict[str, list[str]] = {}
    indexable: set[str] = set()

    for path in html_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        parser = PageParser()
        try:
            parser.feed(text)
        except Exception as exc:
            errors.append(f"{path}: HTML parser error: {exc}")
        pages[path] = (text, parser)

        robots = " ".join(m.get("content", "") for m in parser.metas if m.get("name", "").lower() == "robots").lower()
        noindex = "noindex" in robots
        if not noindex:
            indexable.add(path)

        title = " ".join("".join(parser.title_parts).split())
        if not title:
            errors.append(f"{path}: missing or empty <title>")
        else:
            titles.setdefault(title.casefold(), []).append(path)

        descriptions = [m.get("content", "").strip() for m in parser.metas if m.get("name", "").lower() == "description"]
        if not noindex and not any(descriptions):
            errors.append(f"{path}: missing non-empty meta description")
        elif not noindex:
            descriptions_seen.setdefault(descriptions[0].casefold(), []).append(path)

        if not noindex:
            if parser.h1_count != 1:
                errors.append(f"{path}: expected exactly one H1, found {parser.h1_count}")
            else:
                h1 = " ".join("".join(parser.h1_parts).split())
                if not h1:
                    errors.append(f"{path}: empty H1")
                else:
                    h1s_seen.setdefault(h1.casefold(), []).append(path)
            if len(parser.canonicals) != 1:
                errors.append(f"{path}: expected one canonical, found {len(parser.canonicals)}")
            elif parser.canonicals[0] != canonical_for(path):
                errors.append(f"{path}: canonical {parser.canonicals[0]!r} != {canonical_for(path)!r}")
            else:
                canonicals.setdefault(parser.canonicals[0], []).append(path)
            if parser.main_ids != ["main-content"]:
                errors.append(f"{path}: expected one <main id=\'main-content\'> landmark")
            if parser.skip_links != 1:
                errors.append(f"{path}: expected one skip link to #main-content")
            og_titles = [m for m in parser.metas if m.get("property", "").lower() == "og:title"]
            og_descriptions = [m.get("content", "") for m in parser.metas if m.get("property", "").lower() == "og:description"]
            og_urls = [m.get("content", "") for m in parser.metas if m.get("property", "").lower() == "og:url"]
            twitter_cards = [m for m in parser.metas if m.get("name", "").lower() == "twitter:card"]
            twitter_titles = [m.get("content", "") for m in parser.metas if m.get("name", "").lower() == "twitter:title"]
            twitter_descriptions = [m.get("content", "") for m in parser.metas if m.get("name", "").lower() == "twitter:description"]
            if len(og_titles) != 1:
                errors.append(f"{path}: expected one Open Graph title")
            elif og_titles[0].get("content", "") != title:
                errors.append(f"{path}: Open Graph title must match page title")
            if og_descriptions != [descriptions[0]]:
                errors.append(f"{path}: Open Graph description must match meta description")
            if og_urls != [canonical_for(path)]:
                errors.append(f"{path}: Open Graph URL must match canonical")
            if len(twitter_cards) != 1:
                errors.append(f"{path}: expected one Twitter card declaration")
            if twitter_titles != [title]:
                errors.append(f"{path}: Twitter title must match page title")
            if twitter_descriptions != [descriptions[0]]:
                errors.append(f"{path}: Twitter description must match meta description")
            adsense_accounts = [m.get("content", "") for m in parser.metas if m.get("name", "").lower() == "google-adsense-account"]
            if adsense_accounts != [PUBLISHER]:
                errors.append(f"{path}: expected one verified AdSense account meta tag")
            if f"adsbygoogle.js?client={PUBLISHER}" not in text:
                errors.append(f"{path}: verified AdSense loader missing")
            required_nav = (
                ("healthy-fast-food.html", "Healthy Fast Food"),
                ("restaurant-meal-finder.html", "Meal Finder"),
                ("calculators.html", "Macro Calculator"),
                ("articles.html", "Nutrition Guides"),
                ("about.html", "About"),
            )
            for nav_href, nav_label in required_nav:
                pattern = rf'<a\b[^>]*href=["\']{re.escape(nav_href)}["\'][^>]*>(.*?)</a>'
                anchor = re.search(pattern, text, re.I | re.S)
                label_text = re.sub(r'<[^>]+>', ' ', anchor.group(1)) if anchor else ''
                label_text = ' '.join(label_text.split())
                if not anchor or nav_label.casefold() not in label_text.casefold():
                    errors.append(f"{path}: focused primary navigation link missing: {nav_label}")

        for raw in parser.jsonld:
            try:
                json.loads(raw)
            except Exception as exc:
                errors.append(f"{path}: invalid JSON-LD: {exc}")

        if parser.images_without_alt:
            errors.append(f"{path}: {parser.images_without_alt} image(s) missing alt attributes")
        if "ca-pub-XXXXXXXXXXXXXXXX" in text or 'data-ad-slot="0000000000"' in text:
            errors.append(f"{path}: advertising placeholder remains")
        if "css/premium-v4.css?v=20260826b" not in text:
            errors.append(f"{path}: shared premium visual system is missing")
        if "js/site-motion.js?v=20260826b" not in text:
            errors.append(f"{path}: shared motion layer is missing")
        elif text.count("js/site-motion.js?") != 1:
            errors.append(f"{path}: shared motion layer must load exactly once")
        if text.count("js/polish.js?") != 1:
            errors.append(f"{path}: progressive polish layer must load exactly once")
        if "highperformanceformat.com" in text or "ads-config.js" in text:
            errors.append(f"{path}: obsolete third-party ad code remains")
        if re.search(r"pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js", text) and PUBLISHER not in text:
            errors.append(f"{path}: Google ad loader lacks the verified publisher ID")
        for section in re.findall(r'<section class="related-explore"[^>]*>.*?</section>', text, re.I | re.S):
            grid = re.search(r'<div class="explore-grid">(.*?)</div>', section, re.I | re.S)
            if not grid or not re.search(r'<a class="explore-card"', grid.group(1), re.I):
                errors.append(f"{path}: empty related-content block")
            elif re.search(r'<div class="explore-grid">\s*<(?:strong|span)\b', section, re.I):
                errors.append(f"{path}: orphaned related-content text")

    for title, paths in titles.items():
        if len(paths) > 1:
            errors.append("duplicate title: " + ", ".join(paths))
    for canonical, paths in canonicals.items():
        if len(paths) > 1:
            errors.append(f"duplicate canonical {canonical}: " + ", ".join(paths))
    for description, paths in descriptions_seen.items():
        if len(paths) > 1:
            errors.append("duplicate meta description: " + ", ".join(paths))
    for h1, paths in h1s_seen.items():
        if len(paths) > 1:
            warnings.append("duplicate H1 wording: " + ", ".join(paths))

    root_html = {Path(p).name for p in html_paths if "/" not in p}
    if root_html != KEEP_ROOT_HTML:
        for path in sorted(KEEP_ROOT_HTML - root_html):
            errors.append(f"focused allowlist: missing {path}")
        for path in sorted(root_html - KEEP_ROOT_HTML):
            errors.append(f"focused allowlist: unexpected HTML page {path}")

    all_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
    for path, (_, parser) in pages.items():
        for href in parser.links:
            target = local_target(path, href)
            if target is not None and target not in all_files:
                errors.append(f"{path}: broken internal link {href!r} -> {target!r}")
        for source in parser.resources:
            target = local_target(path, source)
            if target is not None and target not in all_files:
                errors.append(f"{path}: missing local asset {source!r} -> {target!r}")

    sitemap_path = ROOT / "sitemap.xml"
    try:
        sitemap_root = ET.parse(sitemap_path).getroot()
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = [e.text.strip() for e in sitemap_root.findall("s:url/s:loc", ns) if e.text]
    except Exception as exc:
        errors.append(f"sitemap.xml: cannot parse: {exc}")
        locations = []
    if len(locations) != len(set(locations)):
        for loc, count in Counter(locations).items():
            if count > 1:
                errors.append(f"sitemap.xml: duplicate URL {loc}")

    expected_urls = {canonical_for(p) for p in indexable}
    actual_urls = set(locations)
    for url in sorted(expected_urls - actual_urls):
        errors.append(f"sitemap.xml: missing {url}")
    for url in sorted(actual_urls - expected_urls):
        errors.append(f"sitemap.xml: URL has no indexable HTML page: {url}")

    if "404.html" in indexable:
        errors.append("404.html: must include noindex")
    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: https://getmacros.net/sitemap.xml" not in robots_text:
        errors.append("robots.txt: canonical sitemap declaration missing")
    ads_text = (ROOT / "ads.txt").read_text(encoding="utf-8")
    if f"google.com, pub-{PUBLISHER.removeprefix('ca-pub-')}, DIRECT" not in ads_text:
        errors.append("ads.txt: verified Google publisher record missing")

    key_text = "\n".join(pages[p][0] for p in ("index.html", "articles.html", "calculators.html", "healthy-fast-food.html", "restaurant-meal-finder.html"))
    stale_patterns = {
        r"340\s+(?:focused\s+)?guides": "stale 340-guides claim",
        r"Quizzes\s*&(?:amp;)?\s*Games": "quizzes/games remain in primary product pages",
        r'href=["\'](?:es/|fr/)': "partial-language link remains",
    }
    for pattern, label in stale_patterns.items():
        if re.search(pattern, key_text, re.I):
            errors.append(label)

    for path, (text, _) in pages.items():
        visible_text = re.sub(r"<(?:script|style)\b.*?</(?:script|style)>", " ", text, flags=re.I | re.S)
        visible_text = re.sub(r"<[^>]+>", " ", visible_text)
        if re.search(r"\bfibre\b", visible_text, re.I):
            errors.append(f"{path}: visible copy must use the U.S. spelling 'fiber'")

    meals = parse_meals()
    chains = {m["chain"] for m in meals}
    if len(meals) != 83 or len(chains) != 15:
        errors.append(f"restaurant data: expected 83 options across 15 chains, found {len(meals)} across {len(chains)}")
    meal_keys = Counter((m["chain"].casefold(), m["name"].casefold()) for m in meals)
    for key, count in meal_keys.items():
        if count > 1:
            errors.append(f"restaurant data: duplicate record {key[0]} / {key[1]}")
    for meal in meals:
        for field in ("cal", "p", "c", "f", "na"):
            value = meal.get(field)
            if value is not None and (not isinstance(value, (int, float)) or value < 0):
                errors.append(f"restaurant data: invalid {field} for {meal['chain']} / {meal['name']}")
        tags = set(meal.get("t", []))
        substantial = item_type(meal) not in {"Side", "Side / snack"} and (meal.get("cal") or 0) >= 250 and (meal.get("p") or 0) >= 15
        if "light" in tags and not (substantial and meal.get("cal", 0) <= 400):
            errors.append(f"restaurant data: light tag is not a substantial meal: {meal['chain']} / {meal['name']}")
        if "lowsodium" in tags and not (substantial and meal.get("na") is not None and meal["na"] <= 600):
            errors.append(f"restaurant data: low-sodium tag is not a substantial meal: {meal['chain']} / {meal['name']}")

    chipotle_meals = [meal for meal in meals if meal["chain"] == "Chipotle"]
    for meal in chipotle_meals:
        if meal.get("na") is None:
            errors.append(f"restaurant data: Chipotle sodium is missing for {meal['name']}")

    count_claims = {
        "index.html": r"<strong>83</strong>\s*tracked menu options",
        "about.html": r"83 tracked menu options",
        "healthy-fast-food.html": r"83 tracked menu options",
        "restaurant-meal-finder.html": r"83 tracked menu options",
    }
    for path, claim in count_claims.items():
        if not re.search(claim, pages.get(path, ("", PageParser()))[0]):
            errors.append(f"{path}: current restaurant-option count claim missing")
    finder_text = pages.get("restaurant-meal-finder.html", ("", PageParser()))[0]
    quiz_text = (ROOT / "js" / "meal-quiz.js").read_text(encoding="utf-8")
    if "quiz-skip" in quiz_text or "data-clear" in quiz_text:
        errors.append("meal quiz: small skip-link interaction returned")
    if "quiz-option-any" not in quiz_text or "data-any" not in quiz_text:
        errors.append("meal quiz: full-size any/no-preference options missing")
    if "!state[s.key].length ? ' checked'" in quiz_text or "any.checked = !state[key].length" in quiz_text:
        errors.append("meal quiz: no-preference option must not be selected automatically")
    if "var noPreference =" not in quiz_text:
        errors.append("meal quiz: explicit no-preference state is missing")
    if "results.slice(0, 5)" not in quiz_text or "root._rest.splice(0, 3)" not in quiz_text:
        errors.append("meal quiz: expected five initial results and three-at-a-time reveal")
    finder_css = (ROOT / "css" / "meal-finder-v2.css").read_text(encoding="utf-8")
    if re.search(r"\.quiz-option-any:has\(input:checked\)[^{]*\{[^}]*background:var\(--ink\)", finder_css, re.S):
        errors.append("meal quiz: no-preference selected state must not use the old black card")
    static_meal_count = sum(1 for meal in meals if meal["name"] in finder_text)
    if static_meal_count < 35:
        errors.append(f"restaurant-meal-finder.html: only {static_meal_count} tracked options appear in static HTML")
    for chain in chains:
        if chain not in finder_text:
            errors.append(f"restaurant-meal-finder.html: restaurant coverage missing from static HTML: {chain}")
    for chain, config in CHAIN_CONFIG.items():
        chain_meals = [m for m in meals if m["chain"] == chain]
        if not chain_meals:
            errors.append(f"restaurant data: no records for {chain}")
            continue
        page_path = chain_meals[0]["url"]
        page_text = pages.get(page_path, ("", PageParser()))[0]
        if config["source"] not in page_text:
            errors.append(f"{page_path}: official {chain} source missing")
        for meal in chain_meals:
            if meal["name"] not in page_text:
                errors.append(f"{page_path}: tracked item missing from visible HTML: {meal['name']}")

    calc_text = pages.get("calculators.html", ("", PageParser()))[0]
    home_text = pages.get("index.html", ("", PageParser()))[0]
    if ("js/macro-math.js?v=20260826c" not in calc_text
            or "js/macro-math.js?v=20260826c" not in home_text
            or "js/macro-math.js?v=20260826c" not in finder_text):
        errors.append("macro calculator: shared calculation engine is missing from a calculator entry point")
    for goal_value, goal_label in (
        ("lose", "Lose weight"),
        ("recomp", "Lose fat + build muscle"),
        ("maintain", "Maintain weight"),
        ("gain", "Gain weight + build muscle"),
    ):
        option = f'<option value="{goal_value}"'
        if option not in calc_text or goal_label not in calc_text:
            errors.append(f"calculators.html: goal option missing: {goal_label}")
        if option not in home_text or goal_label not in home_text:
            errors.append(f"index.html: goal option missing: {goal_label}")
        if option not in (ROOT / "js" / "macro-meals.js").read_text(encoding="utf-8") or goal_label not in (ROOT / "js" / "macro-meals.js").read_text(encoding="utf-8"):
            errors.append(f"meal finder macro calculator: goal option missing: {goal_label}")
    if calc_text.count('href="budget-meal-builder.html"') != 1:
        errors.append("calculators.html: Budget meal builder must appear exactly once")
    if "related-explore" in calc_text:
        errors.append("calculators.html: stale related-content dump remains")
    if "calculators-polish.css" not in calc_text or "sex-choice-icon" not in calc_text:
        errors.append("calculators.html: calculator readability controls missing")
    if '<meta name="theme-color" content="#073426">' not in calc_text:
        errors.append("calculators.html: site theme color is inconsistent")
    if 'property="og:locale"' in calc_text or 'content="GetMacros.net logo"' in calc_text:
        errors.append("calculators.html: stale social metadata remains")
    if '"name": "Articles"' in calc_text or "Home › Articles ›" in calc_text:
        errors.append("calculators.html: stale Articles breadcrumb remains")
    if '"name": "Macro Calculator"' not in calc_text or not re.search(r'Home</a>\s*<span[^>]*>&rsaquo;</span>\s*<span[^>]*>Macro Calculator</span>', calc_text):
        errors.append("calculators.html: calculator breadcrumb hierarchy is missing")

    try:
        ET.parse(ROOT / "feed.xml")
    except Exception as exc:
        errors.append(f"feed.xml: cannot parse: {exc}")
    try:
        json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"site.webmanifest: cannot parse JSON: {exc}")

    search_text, search_parser = pages.get("search.html", ("", PageParser()))
    result_links = set()
    for match in re.finditer(r"<article\b[^>]*class=[\"'][^\"']*\bresult-card\b[^\"']*[\"'][^>]*>(.*?)</article>", search_text, re.I | re.S):
        anchor = re.search(r"<a\b[^>]*href=[\"']([^\"']+)[\"']", match.group(1), re.I)
        if anchor:
            target = local_target("search.html", anchor.group(1))
            if target:
                result_links.add(target)
    expected_search = indexable - {"search.html"}
    for path in sorted(expected_search - result_links):
        errors.append(f"search.html: missing indexable page {path}")
    for path in sorted(result_links - expected_search):
        errors.append(f"search.html: result is not an indexable page {path}")

    if errors:
        print(f"FAILED: {len(errors)} issue(s)")
        for issue in errors:
            print(f" - {issue}")
        return 1
    print(
        f"PASS: {len(html_paths)} HTML files; {len(indexable)} indexable pages; "
        f"{len(locations)} sitemap URLs; {len(result_links)} searchable resources."
    )
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
