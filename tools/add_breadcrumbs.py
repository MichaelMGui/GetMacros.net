#!/usr/bin/env python3
"""Add a visible breadcrumb trail and BreadcrumbList schema to pages missing them.

The parent hub is inferred from the links in the page's own content (header and
footer chrome excluded, since every page links to the same nav targets).
"""
import glob
import html as H
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
BASE = "https://getmacros.net/"

GENERIC = ["restaurant-meal-guides.html", "healthy-fast-food.html",
           "topics.html", "articles.html", "quiz.html", "calculators.html"]


def content_of(c):
    b = c[c.index("<body"):]
    b = re.sub(r"<header\b.*?</header>", " ", b, flags=re.S)
    b = re.sub(r"<footer\b.*?</footer>", " ", b, flags=re.S)
    return b


def title_of(path):
    c = open(path, encoding="utf-8").read()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", c, re.S)
    if not m:
        m = re.search(r"<title>(.*?)</title>", c, re.S)
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))) if m else path
    return H.unescape(t).replace(" | GetMacros.net", "").strip()


def main():
    os.chdir(ROOT)
    hubs = set(f for f in glob.glob("*.html") if f.endswith("-guides.html"))
    targets = [f for f in sorted(glob.glob("*.html"))
               if "BreadcrumbList" not in open(f, encoding="utf-8").read()
               and f not in ("404.html", "index.html")]

    names = {}
    done = 0
    for f in targets:
        c = open(f, encoding="utf-8").read()
        body = content_of(c)
        topical = [h for h in sorted(hubs) if f'href="{h}"' in body and h != f]
        hub = topical[0] if topical else None
        if not hub:
            for g in GENERIC:
                if f'href="{g}"' in body and g != f:
                    hub = g
                    break
        if not hub:
            hub = "topics.html" if f.endswith("-guides.html") else "articles.html"
        if hub == f:
            # A hub is its own fallback; fall back again rather than repeating it.
            hub = "topics.html" if f != "topics.html" else "articles.html"

        for p in (hub, f):
            if p not in names:
                names[p] = title_of(p)
        page_name, hub_name = names[f], names[hub]

        crumb = (
            '<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container">'
            f'<a href="index.html">Home</a> <span aria-hidden="true">&rsaquo;</span> '
            f'<a href="{hub}">{H.escape(hub_name)}</a> <span aria-hidden="true">&rsaquo;</span> '
            f'<span aria-current="page">{H.escape(page_name)}</span>'
            '</div></nav>'
        )
        data = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE},
                {"@type": "ListItem", "position": 2, "name": hub_name, "item": BASE + hub},
                {"@type": "ListItem", "position": 3, "name": page_name, "item": BASE + f},
            ],
        }
        ld = ('<script type="application/ld+json">'
              + json.dumps(data).replace("</", "<\\/") + "</script>")

        out = c.replace("</head>", ld + "</head>", 1)
        # Put the trail directly after the opening <main>, above the content.
        m = re.search(r"<main\b[^>]*>", out)
        if not m:
            continue
        out = out[:m.end()] + crumb + out[m.end():]
        if out != c:
            open(f, "w", encoding="utf-8").write(out)
            done += 1

    print(f"breadcrumbs added to {done} pages")


if __name__ == "__main__":
    sys.exit(main())
