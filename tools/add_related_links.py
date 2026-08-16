#!/usr/bin/env python3
"""Give every page a 'Continue exploring' block of sibling links.

Most pages were reachable only from their hub listing, so useful content stayed
invisible unless you went looking. Siblings are taken from the page's own
breadcrumb cluster and rotated, so inbound links spread evenly across the
cluster instead of piling onto the same few pages.
"""
import glob
import html as H
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PER_PAGE = 6
MARK = "related-explore"


def hub_of(c):
    """Second link in the breadcrumb trail is the parent hub.

    Breadcrumb markup varies across the site (entity vs literal separators,
    inline vs pretty-printed), so match on the links themselves.
    """
    m = re.search(r'<nav class="breadcrumb".*?</nav>', c, re.S)
    if not m:
        return None, None
    links = re.findall(r'<a href="([^"]+\.html)"[^>]*>(.*?)</a>', m.group(0), re.S)
    links = [(h, re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", t))).strip()) for h, t in links]
    links = [(h, t) for h, t in links if h != "index.html"]
    if not links:
        return None, None
    return links[0]


def title_of(c, fallback):
    m = re.search(r"<h1[^>]*>(.*?)</h1>", c, re.S) or re.search(r"<title>(.*?)</title>", c, re.S)
    if not m:
        return fallback
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1)))
    return H.unescape(t).replace(" | GetMacros.net", "").strip()


def blurb_of(c):
    m = re.search(r'<meta name="description" content="([^"]*)"', c)
    if not m:
        return ""
    d = H.unescape(m.group(1)).strip()
    return (d[:104].rsplit(" ", 1)[0] + "…") if len(d) > 108 else d


def main():
    os.chdir(ROOT)
    files = sorted(glob.glob("*.html"))
    cache = {f: open(f, encoding="utf-8").read() for f in files}

    clusters = defaultdict(list)
    hub_name = {}
    for f in files:
        if f in ("404.html", "index.html"):
            continue
        hub, name = hub_of(cache[f])
        if not hub:
            continue
        clusters[hub].append(f)
        hub_name[hub] = name

    titles = {f: title_of(cache[f], f) for f in files}
    blurbs = {f: blurb_of(cache[f]) for f in files}

    added = 0
    for hub, members in clusters.items():
        members = sorted(members)
        n = len(members)
        if n < 2:
            continue
        for i, f in enumerate(members):
            c = cache[f]
            if MARK in c:
                continue
            # rotate the window so every sibling gets linked a similar number of times
            picks = [members[(i + 1 + k) % n] for k in range(min(PER_PAGE, n - 1))]
            cards = "".join(
                f'<a class="explore-card" href="{p}">'
                f'<strong>{H.escape(titles[p])}</strong>'
                + (f'<span>{H.escape(blurbs[p])}</span>' if blurbs[p] else "")
                + '</a>'
                for p in picks
            )
            hub_link = (f'<a class="explore-all" href="{hub}">'
                        f'See everything in {H.escape(hub_name.get(hub, "this topic"))} &rarr;</a>')
            block = (f'<section class="{MARK}" aria-labelledby="explore-more-heading">'
                     '<div class="container">'
                     '<h2 id="explore-more-heading">Continue exploring</h2>'
                     f'<div class="explore-grid">{cards}</div>{hub_link}'
                     '</div></section>')

            if "</main>" in c:
                out = c.replace("</main>", block + "</main>", 1)
            else:
                continue
            open(f, "w", encoding="utf-8").write(out)
            cache[f] = out
            added += 1

    print(f"'Continue exploring' added to {added} pages across {len(clusters)} clusters")


if __name__ == "__main__":
    sys.exit(main())
