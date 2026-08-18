#!/usr/bin/env python3
"""Normalize the middle (hub) label in every breadcrumb trail.

Breadcrumb hub names were derived from each hub's <h1>, which is a headline, not
a label. That produced trails like "Home > Choose a restaurant.See the useful
details. > ..." — long, sentence-shaped, and occasionally word-glued where a
<br> was stripped without a separator. Google renders the breadcrumb in the
search result, so the middle rung is user-facing text and needs to read like a
section name.

This runs after add_breadcrumbs.py and rewrites both the visible trail and the
BreadcrumbList schema so the two never disagree. It is idempotent.
"""
import glob
import html as H
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# Hubs whose <h1> is a headline rather than a section name.
LABELS = {
    "articles.html": "Articles",
    "topics.html": "Topics",
    "quiz.html": "Quizzes &amp; games",
    "calculators.html": "Calculators",
    "glossary.html": "Glossary",
    "healthy-fast-food.html": "Healthy fast food",
    "restaurant-meal-guides.html": "Restaurant guides",
    "search.html": "Search",
    "sources.html": "Sources",
}

# Acronyms that must keep their capitalization when a label is sentence-cased.
ACRONYMS = {"PCOS", "IBS", "RDA", "DRI", "AMDR", "BMR", "TDEE", "GERD"}


def sentence_case(label):
    """Lowercase Title Cased hub names, preserving acronyms and the first word."""
    words = label.split(" ")
    out = []
    for i, w in enumerate(words):
        bare = w.strip("(),:")
        if bare.upper() in ACRONYMS or bare.isupper():
            out.append(w)
        elif i == 0:
            out.append(w[:1].upper() + w[1:])
        elif w[:1].isupper():
            # Lowercase each part of a hyphenated compound too: "Bone-Health".
            out.append("-".join(
                q if q.upper() in ACRONYMS else q[:1].lower() + q[1:]
                for q in w.split("-")))
        else:
            out.append(w)
    return " ".join(out)


def label_for(href, fallback):
    if href in LABELS:
        return LABELS[href]
    # A generated "-guides.html" hub already has a name-shaped <h1>; just fix
    # its capitalization so the trails read consistently across the site.
    return sentence_case(fallback)


def main():
    os.chdir(ROOT)
    changed = 0
    for f in sorted(glob.glob("*.html")):
        c = open(f, encoding="utf-8").read()
        if "BreadcrumbList" not in c:
            continue

        # Visible trail: Home > <a href="HUB">NAME</a> > current
        m = re.search(
            r'(<nav class="breadcrumb".*?<a href="index\.html">Home</a>'
            r'\s*<span aria-hidden="true">(?:&rsaquo;|›)</span>\s*'
            r'<a href=")([^"]+)(">)(.*?)(</a>)',
            c, re.S)
        if not m:
            continue
        href, old = m.group(2), m.group(4)
        new = label_for(href, re.sub(r"\s+", " ", old).strip())

        out = c if new == old else c[:m.start(4)] + new + c[m.end(4):]
        # Schema position 2 must match the visible rung exactly. Sync it even
        # when the visible label needed no change: a page whose <main> was
        # rewritten by hand can carry a correct trail over stale schema.
        plain_new = H.unescape(new)
        out = re.sub(r'("position": 2, "name": ")(?:[^"\\]|\\.)*(")',
                     lambda mm: mm.group(1) + plain_new + mm.group(2), out)
        if out == c:
            continue
        open(f, "w", encoding="utf-8").write(out)
        changed += 1

    print(f"breadcrumb hub labels normalized on {changed} pages")


if __name__ == "__main__":
    sys.exit(main())
