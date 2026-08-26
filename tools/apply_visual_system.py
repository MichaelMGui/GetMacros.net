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


def upsert(text: str) -> str:
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
    return text


def main() -> None:
    changed = 0
    for name in sorted(KEEP_ROOT_HTML):
        path = ROOT / name
        if not path.exists():
            continue
        before = path.read_text(encoding="utf-8")
        after = upsert(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
    print(f"Applied premium visual system to {changed} retained pages.")


if __name__ == "__main__":
    main()
