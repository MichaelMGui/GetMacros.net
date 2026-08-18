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
        self.metas: list[dict[str, str]] = []
        self.links: list[str] = []
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
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonicals.append(a.get("href", ""))
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._json_depth = 1
            self._json_parts = []
        elif tag == "article" and "result-card" in a.get("class", "").split():
            self.result_cards.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "script" and self._json_depth:
            self.jsonld.append("".join(self._json_parts).strip())
            self._json_depth = 0
            self._json_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
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

        if not noindex:
            if parser.h1_count != 1:
                errors.append(f"{path}: expected exactly one H1, found {parser.h1_count}")
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
            og_urls = [m.get("content", "") for m in parser.metas if m.get("property", "").lower() == "og:url"]
            twitter_cards = [m for m in parser.metas if m.get("name", "").lower() == "twitter:card"]
            if len(og_titles) != 1:
                errors.append(f"{path}: expected one Open Graph title")
            if og_urls != [canonical_for(path)]:
                errors.append(f"{path}: Open Graph URL must match canonical")
            if len(twitter_cards) != 1:
                errors.append(f"{path}: expected one Twitter card declaration")

        for raw in parser.jsonld:
            try:
                json.loads(raw)
            except Exception as exc:
                errors.append(f"{path}: invalid JSON-LD: {exc}")

        if parser.images_without_alt:
            errors.append(f"{path}: {parser.images_without_alt} image(s) missing alt attributes")
        if "ca-pub-XXXXXXXXXXXXXXXX" in text or 'data-ad-slot="0000000000"' in text:
            errors.append(f"{path}: advertising placeholder remains")
        if "highperformanceformat.com" in text or "ads-config.js" in text:
            errors.append(f"{path}: obsolete third-party ad code remains")
        if re.search(r"pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js", text) and PUBLISHER not in text:
            errors.append(f"{path}: Google ad loader lacks the verified publisher ID")

    for title, paths in titles.items():
        if len(paths) > 1:
            errors.append("duplicate title: " + ", ".join(paths))
    for canonical, paths in canonicals.items():
        if len(paths) > 1:
            errors.append(f"duplicate canonical {canonical}: " + ", ".join(paths))

    all_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file()}
    for path, (_, parser) in pages.items():
        for href in parser.links:
            target = local_target(path, href)
            if target is not None and target not in all_files:
                errors.append(f"{path}: broken internal link {href!r} -> {target!r}")

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
