#!/usr/bin/env python3
"""Add real depth to pages that were too thin to earn their place.

AdSense rejected the site for low-value content. 49 pages sat under 300 words --
pages promising "25 high-protein foods" or "how much protein per day" and
answering in three paragraphs.

Expansion here means more information, not more words: thresholds with their
numbers attached, worked examples with real figures, and the caveat that makes
a number usable. Padding a thin page with restatement is what caused the
rejection in the first place.

EXPANSIONS maps slug -> list of (heading, html). Blocks are marked so a rebuild
replaces them instead of stacking copies, and are placed above the page's
"keep reading" links so the page still ends on navigation.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
OPEN, CLOSE = "<!--EXPANSION:START-->", "<!--EXPANSION:END-->"

from expansions_data import EXPANSIONS  # noqa: E402


def render(secs):
    body = "".join('<section class="expanded"><div class="container">'
                   f"<h2>{h}</h2>{b}</div></section>" for h, b in secs)
    return OPEN + body + CLOSE


def main():
    os.chdir(ROOT)
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    done = 0
    for slug, secs in sorted(EXPANSIONS.items()):
        f = slug + ".html"
        if not os.path.exists(f):
            print(f"  WARNING no page for {slug}")
            continue
        c = open(f, encoding="utf-8").read()
        block = render(secs)
        if OPEN in c:
            out = re.sub(re.escape(OPEN) + r".*?" + re.escape(CLOSE),
                         lambda _: block, c, flags=re.S)
        else:
            m = (re.search(r'<section[^>]*>\s*<div class="container">\s*<h3>Keep reading', c)
                 or re.search(r'<section class="related-explore"', c))
            if m:
                out = c[:m.start()] + block + c[m.start():]
            elif "</main>" in c:
                out = c.replace("</main>", block + "</main>", 1)
            else:
                continue
        if out != c:
            open(f, "w", encoding="utf-8").write(out)
            done += 1
    print(f"expanded {done} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
