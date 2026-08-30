#!/usr/bin/env python3
"""Ensure every page ends with one unified visual and interaction layer.

The generators emit their own <head>, so a stylesheet added by hand is dropped
on the next build. Page-specific layout CSS stays in place, while the unified
system is re-linked last so old behavior layers cannot compete with it.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# The full shared cascade, in the order audit_visual_contract.py requires.
# Only unified-v7.css was managed here, so any page the generators rewrote lost
# liquid, contrast-fix and polish -- 48 pages were failing the contract, and
# more importantly they were missing the contrast repairs, which is a
# readability bug rather than a cosmetic one.
SHEETS = [
    "css/liquid.css",
    "css/contrast-fix.css",
    "css/polish.css",
    "css/unified-v7.css",
    # After unified-v7 on purpose: it sets the failing colours with
    # !important, so a repair earlier in the cascade cannot win.
    "css/theme-fix.css",
    # The final editorial composition layer. It replaces the repeated green
    # billboard on product and secondary-page openings after all legacy fixes.
    "css/editorial-v8.css",
]
SCRIPTS = ["js/unified-v7.js"]
ASSET_VERSION = "20260828g"

# Legacy scroll-reveal. It sets opacity:0 on `main > section` and relies
# entirely on an IntersectionObserver callback to put it back, with no
# fallback: anything the observer misses stays invisible permanently. A
# full-site sweep found sections stuck at opacity 0 on 60 pages at desktop
# width. js/polish.js replaces it and reveals everything unconditionally after
# 1.2s, so the old script is stripped rather than left to compete.
DROP_SCRIPTS = [
    "js/reveal.js",
    "js/polish.js",
    "js/site-motion.js",
    "js/studio-v6.js",
    "js/atelier-v5.js",
    "js/theme-toggle.js",
]
DROP_SHEETS = ["css/theme.css"]

# The header is the same markup on every page, but its layout lives in
# atelier-v5.css, which 11 generated article pages never linked. Without it
# `.nav-mobile-search{display:none}` and the desktop nav-item display rules
# were missing, so the phone search field rendered inline in the desktop bar,
# overlapping "About". Linked where absent, immediately before liquid.css so
# the rest of the cascade keeps the order the contract checks; pages that
# already have it are left exactly where they are, since moving it past
# studio-v6 would change how they look.
SHARED_HEADER_SHEET = "css/atelier-v5.css"


def ensure_header_sheet(text, prefix, version):
    if "atelier-v5.css" in text:
        return text
    link = f'<link rel="stylesheet" href="{prefix}{SHARED_HEADER_SHEET}?v={version}">'
    marker = re.search(r'<link rel="stylesheet" href="[^"]*liquid\.css[^"]*">', text)
    if marker:
        return text[:marker.start()] + link + text[marker.start():]
    return text.replace("</head>", link + "</head>", 1)



def main():
    os.chdir(ROOT)
    pages = sorted(glob.glob("*.html")) + sorted(glob.glob("*/*.html"))
    touched = 0
    for f in pages:
        c = open(f, encoding="utf-8").read()
        if "</head>" not in c:
            continue
        v = ASSET_VERSION
        # Normalize the final cascade instead of appending duplicates.
        for sheet in SHEETS:
            c = re.sub(
                rf'<link rel=["\']stylesheet["\'] href=["\'][^"\']*(?<![A-Za-z0-9_-]){re.escape(os.path.basename(sheet))}(?:\?[^"\']*)?["\']>',
                "",
                c,
                flags=re.I,
            )
        for sheet in DROP_SHEETS:
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
        # Re-linked as one block at the end of <head> so the relative order
        # inside SHEETS is exactly the cascade the contract checks for.
        add = "".join(f'<link rel="stylesheet" href="{prefix}{sheet}?v={v}">' for sheet in SHEETS)
        out = c.replace("</head>", add + "</head>", 1)
        out = ensure_header_sheet(out, prefix, v)

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

        # The default is light; unified-v7.js updates this when dark is chosen.
        out = re.sub(r'<meta name="theme-color" content="#[0-9a-fA-F]{6}">',
                     '<meta name="theme-color" content="#f4f7f2">', out)

        out = re.sub(
            r'<script>try\{var t=localStorage\.getItem\(["\']gm-theme["\']\);if\(t\)document\.documentElement\.setAttribute\(["\']data-theme["\'],t\);\}catch\(e\)\{\}</script>\s*',
            "",
            out,
            flags=re.I,
        )

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
