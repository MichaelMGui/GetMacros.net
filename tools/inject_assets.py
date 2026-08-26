#!/usr/bin/env python3
"""Ensure every page links the late-loading stylesheets.

The generators emit their own <head>, so a stylesheet added by hand is dropped
on the next build. Anything that has to load after the page's own CSS -- the
contrast repairs, the liquid motion -- is re-linked here instead.

Order matters: contrast-fix.css must come last so it can win on specificity
rather than by piling on !important.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
SHEETS = ["css/liquid.css", "css/contrast-fix.css", "css/polish.css"]
SCRIPTS = ["js/polish.js"]

# Legacy scroll-reveal. It sets opacity:0 on `main > section` and relies
# entirely on an IntersectionObserver callback to put it back, with no
# fallback: anything the observer misses stays invisible permanently. A
# full-site sweep found sections stuck at opacity 0 on 60 pages at desktop
# width. js/polish.js replaces it and reveals everything unconditionally after
# 1.2s, so the old script is stripped rather than left to compete.
DROP_SCRIPTS = ["js/reveal.js"]


def main():
    os.chdir(ROOT)
    pages = sorted(glob.glob("*.html")) + sorted(glob.glob("*/*.html"))
    touched = 0
    for f in pages:
        c = open(f, encoding="utf-8").read()
        if "</head>" not in c:
            continue
        m = re.search(r"\?v=([0-9a-z]+)", c)
        v = m.group(1) if m else "1"
        prefix = "../" if "/" in f else ""
        add = ""
        for sheet in SHEETS:
            if os.path.basename(sheet) in c:
                continue
            add += f'<link rel="stylesheet" href="{prefix}{sheet}?v={v}">'
        out = c.replace("</head>", add + "</head>", 1) if add else c

        # Behaviour scripts load deferred at the end of body: they only enhance
        # what is already rendered, so blocking parse for them would trade a
        # slower first paint for nothing.
        tail = ""
        for script in SCRIPTS:
            if os.path.basename(script) in out:
                continue
            tail += f'<script src="{prefix}{script}?v={v}" defer></script>'
        if tail and "</body>" in out:
            out = out.replace("</body>", tail + "</body>", 1)

        for dead in DROP_SCRIPTS:
            out = re.sub(r'<script[^>]*src="[^"]*' + re.escape(os.path.basename(dead)) +
                         r'[^"]*"[^>]*>\s*</script>', "", out)

        if out == c:
            continue
        open(f, "w", encoding="utf-8").write(out)
        touched += 1
    print(f"asset links ensured on {touched} page(s)")
    print(f"liquid-surface applied to {liquid_heroes()} hero(es)")
    return 0


def liquid_heroes():
    """Mark every page hero as a liquid surface.

    The drifting background is a ::before/::after pair, so it needs no markup
    beyond the class. Heroes that already carry the explicit blob markup are
    left alone rather than getting two sets of moving colour.
    """
    n = 0
    for f in sorted(glob.glob("*.html")) + sorted(glob.glob("*/*.html")):
        c = open(f, encoding="utf-8").read()
        if "liquid-blobs" in c:
            continue
        out = re.sub(
            r'<section class="((?:[^"]*\b)?(?:hero|page-hero|focus-hero|calc-hub-hero|'
            r'fast-hero-new|library-hero|learning-hero|guide-hub-hero|tool-hero|finder-hero)[^"]*)"',
            lambda m: (m.group(0) if "liquid-surface" in m.group(1)
                       else f'<section class="{m.group(1)} liquid-surface"'),
            c)
        if out != c:
            open(f, "w", encoding="utf-8").write(out)
            n += 1
    return n


if __name__ == "__main__":
    sys.exit(main())
