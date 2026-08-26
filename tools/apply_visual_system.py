#!/usr/bin/env python3
"""Attach the shared visual system to every retained HTML page."""
from __future__ import annotations

import re
from pathlib import Path

from site_scope import KEEP_ROOT_HTML

ROOT = Path(__file__).resolve().parents[1]
VERSION = "20260826a"
CSS = f'<link rel="stylesheet" href="css/premium-v4.css?v={VERSION}">'
JS = f'<script src="js/site-motion.js?v={VERSION}"></script>'
MATH = f'<script src="js/macro-math.js?v={VERSION}"></script>'


def upsert(text: str, name: str) -> str:
    text = re.sub(
        r'<link rel="stylesheet" href="css/premium-v4\.css\?v=[^"]+">',
        CSS,
        text,
        flags=re.I,
    )
    if CSS not in text:
        text = text.replace("</head>", f"{CSS}\n</head>", 1)

    text = re.sub(
        r'<script src="js/site-motion\.js\?v=[^"]+"></script>',
        JS,
        text,
        flags=re.I,
    )
    if JS not in text:
        text = text.replace("</body>", f"{JS}</body>", 1)
    if name == "index.html" and "js/macro-math.js" not in text:
        text = text.replace('<script src="js/home-calculator.js', MATH + '<script src="js/home-calculator.js', 1)
    if name == "calculators.html" and "js/macro-math.js" not in text:
        text = text.replace('<script src="js/calculators.js', MATH + '<script src="js/calculators.js', 1)
    if name == "restaurant-meal-finder.html" and "js/macro-math.js" not in text:
        text = text.replace('<script src="js/macro-meals.js', MATH + '<script src="js/macro-meals.js', 1)
    if name == "index.html":
        text = re.sub(r'js/home-calculator\.js\?v=[^"\']+', f'js/home-calculator.js?v={VERSION}', text, count=1)
    if name == "calculators.html":
        text = re.sub(r'js/calculators\.js\?v=[^"\']+', f'js/calculators.js?v={VERSION}', text, count=1)
    if name == "restaurant-meal-finder.html":
        text = re.sub(r'js/macro-meals\.js\?v=[^"\']+', f'js/macro-meals.js?v={VERSION}', text, count=1)
    return text


def main() -> None:
    changed = 0
    for name in sorted(KEEP_ROOT_HTML):
        path = ROOT / name
        if not path.exists():
            continue
        before = path.read_text(encoding="utf-8")
        after = upsert(before, name)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
    print(f"Applied premium visual system to {changed} retained pages.")


if __name__ == "__main__":
    main()
