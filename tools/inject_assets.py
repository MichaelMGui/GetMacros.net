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
# theme.css loads last: it settles disagreements between the older
# stylesheets rather than adding another voice to them.
SHEETS = ["css/liquid.css", "css/contrast-fix.css", "css/polish.css", "css/theme.css"]
SCRIPTS = ["js/polish.js", "js/theme-toggle.js"]
ASSET_VERSION = "20260826b"

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
        v = ASSET_VERSION
        # Normalize the late cascade instead of merely appending missing files.
        # contrast-fix intentionally comes before effects-only polish.css, while
        # premium-v4 is inserted immediately before this group by the visual
        # system pass.
        for sheet in SHEETS:
            c = re.sub(
                rf'<link rel=["\']stylesheet["\'] href=["\'][^"\']*(?<![A-Za-z0-9_-]){re.escape(os.path.basename(sheet))}(?:\?[^"\']*)?["\']>',
                "",
                c,
                flags=re.I,
            )
        prefix = "../" if "/" in f else ""
        if not re.search(r'<link\b[^>]*rel=["\'][^"\']*\bicon\b', c, re.I):
            c = c.replace(
                "</head>",
                f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"></head>',
                1,
            )
        add = "".join(f'<link rel="stylesheet" href="{prefix}{sheet}?v={v}">' for sheet in SHEETS)
        out = c.replace("</head>", add + "</head>", 1)

        # Behaviour scripts load deferred at the end of body: they only enhance
        # what is already rendered, so blocking parse for them would trade a
        # slower first paint for nothing.
        tail = ""
        for script in SCRIPTS:
            out = re.sub(
                rf'<script[^>]*src=["\'][^"\']*(?<![A-Za-z0-9_-]){re.escape(os.path.basename(script))}(?:\?[^"\']*)?["\'][^>]*>\s*</script>',
                "",
                out,
                flags=re.I,
            )
            tail += f'<script src="{prefix}{script}?v={v}" defer></script>'
        if tail and "</body>" in out:
            out = out.replace("</body>", tail + "</body>", 1)

        for dead in DROP_SCRIPTS:
            out = re.sub(r'<script[^>]*src="[^"]*' + re.escape(os.path.basename(dead)) +
                         r'[^"]*"[^>]*>\s*</script>', "", out)

        # One theme-color sitewide. build_focus_pages wrote #123f2d while
        # validate_site demanded #073426 on calculators.html, so the build was
        # failing on a disagreement between two of its own steps.
        out = re.sub(r'<meta name="theme-color" content="#[0-9a-fA-F]{6}">',
                     '<meta name="theme-color" content="#123f2d">', out)

        # Apply a stored theme before first paint. Waiting for the deferred
        # script means a dark-mode visitor gets a white flash first.
        boot = ('<script>try{var t=localStorage.getItem("gm-theme");'
                'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>')
        if "gm-theme" not in out and "<head>" in out:
            out = out.replace("<head>", "<head>" + boot, 1)

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
