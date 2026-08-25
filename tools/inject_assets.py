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
SHEETS = ["css/liquid.css", "css/contrast-fix.css"]


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
        if not add:
            continue
        open(f, "w", encoding="utf-8").write(c.replace("</head>", add + "</head>", 1))
        touched += 1
    print(f"asset links ensured on {touched} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
