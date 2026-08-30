#!/usr/bin/env python3
"""Two navigation details the generators never filled in.

`aria-current="page"`. Twelve pages appear in the header nav and link to
themselves from it. Without the attribute, a screen reader reads that link the
same as every other -- there is no way to tell where you are in the site from
the navigation, which is precisely what the navigation is for. The breadcrumb
trail already marks its final crumb this way; the header did not.

BreadcrumbList schema. Fourteen pages render a visible breadcrumb trail with
no matching structured data, so the trail Google shows in a result is guessed
from the URL rather than read from the page. Deriving the schema from the
visible trail rather than from a separate table means the two cannot disagree,
which is the condition Google actually places on breadcrumb markup.

Idempotent: both passes skip a page that already has what they add.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://getmacros.net"

# Only the nav-link container. The brand mark, the Search button and the
# mobile search shortcut all link to a page too, and marking those "current"
# would tell a screen reader the logo is the page you are on.
NAV_LINKS = re.compile(r'<div class="full-nav-links"[^>]*>.*?</nav>', re.S | re.I)
NOT_A_LOCATION = ("modern-brand", "nav-action", "nav-mobile-search", "lang-switch")
CRUMB = re.compile(r'<nav class="breadcrumb"[^>]*>(.*?)</nav>', re.S | re.I)
ANCHOR = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S | re.I)
CURRENT = re.compile(r'<span aria-current="page"[^>]*>(.*?)</span>', re.S | re.I)


def strip_tags(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value))).strip()


def mark_current(text: str, name: str) -> tuple[str, bool]:
    nav = NAV_LINKS.search(text)
    if not nav:
        return text, False
    block = nav.group(0)
    if "aria-current" in block:
        return text, False

    def tag(match: re.Match) -> str:
        opening = match.group(0)
        href = re.search(r'href="([^"]+)"', opening)
        if not href or href.group(1) != name or "aria-current" in opening:
            return opening
        if any(cls in opening for cls in NOT_A_LOCATION):
            return opening
        return opening.replace("<a ", '<a aria-current="page" ', 1)

    updated = re.sub(r"<a\b[^>]*>", tag, block)
    if updated == block:
        return text, False
    return text.replace(block, updated, 1), True


def add_breadcrumb_schema(text: str, name: str) -> tuple[str, bool]:
    if "BreadcrumbList" in text:
        return text, False
    crumb = CRUMB.search(text)
    if not crumb:
        return text, False
    trail = crumb.group(1)
    items = []
    for href, label in ANCHOR.findall(trail):
        label = strip_tags(label)
        if not label:
            continue
        loc = f"{SITE}/" if href == "index.html" else f"{SITE}/{href}"
        items.append({"@type": "ListItem", "position": len(items) + 1,
                      "name": label, "item": loc})
    last = CURRENT.search(trail)
    if last:
        label = strip_tags(last.group(1))
        if label:
            loc = f"{SITE}/" if name == "index.html" else f"{SITE}/{name}"
            items.append({"@type": "ListItem", "position": len(items) + 1,
                          "name": label, "item": loc})
    if len(items) < 2:
        return text, False
    schema = {"@context": "https://schema.org", "@type": "BreadcrumbList",
              "itemListElement": items}
    tag = ('<script type="application/ld+json">'
           + json.dumps(schema, separators=(",", ":"))
           + "</script>")
    return text.replace("</head>", tag + "</head>", 1), True


ROBOTS = ('<meta name="robots" content="index, follow, max-snippet:-1, '
          'max-image-preview:large, max-video-preview:-1">')


def add_robots(text: str) -> tuple[str, bool]:
    """Opt every indexable page into full snippets and large image previews.

    With no robots meta at all, Google applies its conservative defaults: a
    truncated snippet and, in most regions, a thumbnail-sized image or none.
    The directive below is the documented way to ask for the full text snippet
    and the large image preview that rich results and Discover use. It is the
    single highest-leverage meta tag the site was missing, and it was missing
    from 67 of 68 pages.

    404.html already carries `noindex, follow` and must keep it -- an error
    page in the index is worse than no page at all.
    """
    if 'name="robots"' in text:
        return text, False
    return text.replace("</head>", ROBOTS + "</head>", 1), True


AUTHOR = '<meta name="author" content="The GetMacros.net editorial team">'


def add_author(text: str) -> tuple[str, bool]:
    if 'name="author"' in text:
        return text, False
    return text.replace("</head>", AUTHOR + "</head>", 1), True


def main() -> int:
    marked = crumbed = robotsed = authored = 0
    for path in sorted(ROOT.glob("*.html")):
        text = original = path.read_text(encoding="utf-8")
        text, did_mark = mark_current(text, path.name)
        text, did_crumb = add_breadcrumb_schema(text, path.name)
        text, did_robots = add_robots(text)
        text, did_author = add_author(text)
        marked += did_mark
        crumbed += did_crumb
        robotsed += did_robots
        authored += did_author
        if text != original:
            path.write_text(text, encoding="utf-8")
    print(f"navigation finished: current page marked on {marked}, "
          f"breadcrumb schema added on {crumbed}, robots directive on {robotsed}, "
          f"author on {authored}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
