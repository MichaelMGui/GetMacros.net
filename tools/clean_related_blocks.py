#!/usr/bin/env python3
"""Remove orphaned text and normalize the related-content block on each page."""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECTION_RE = re.compile(
    r'<section class="related-explore"[^>]*>.*?</section>', re.I | re.S
)
CARD_RE = re.compile(
    r'<a class="explore-card"[^>]*>.*?</a>', re.I | re.S
)
ALL_RE = re.compile(
    r'<a class="explore-all"[^>]*>.*?</a>', re.I | re.S
)


def clean_section(match: re.Match[str]) -> str:
    section = match.group(0)
    cards = CARD_RE.findall(section)
    if not cards:
        return ""
    all_link = ALL_RE.search(section)
    return (
        '<section class="related-explore" aria-labelledby="explore-more-heading">'
        '<div class="container"><h2 id="explore-more-heading">Continue exploring</h2>'
        f'<div class="explore-grid">{"".join(cards)}</div>'
        f'{all_link.group(0) if all_link else ""}</div></section>'
    )


def main() -> None:
    changed = 0
    removed = 0
    for path in sorted(ROOT.glob("*.html")):
        source = path.read_text(encoding="utf-8")
        before = len(SECTION_RE.findall(source))
        if not before:
            continue
        result = SECTION_RE.sub(clean_section, source)
        after = len(SECTION_RE.findall(result))
        if result != source:
            path.write_text(result, encoding="utf-8")
            changed += 1
            removed += before - after
    print(f"Normalized {changed} pages; removed {removed} empty related blocks.")


if __name__ == "__main__":
    main()
