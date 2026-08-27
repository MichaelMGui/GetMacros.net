#!/usr/bin/env python3
"""Audit the reusable visual and interaction contract on every retained page."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

from site_scope import KEEP_ROOT_HTML

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ASSETS = (
    "css/site-v3.css",
    "css/premium-v4.css",
    "css/liquid.css",
    "css/contrast-fix.css",
    "css/polish.css",
    "js/polish.js",
    "js/site-motion.js",
)
CALCULATOR_PAGES = {
    "calculators.html",
    "recipe-macro-scaler.html",
    "nutrition-label-comparison-tool.html",
    "protein-value-calculator.html",
    "budget-meal-builder.html",
    "sodium-label-comparison-tool.html",
    "carbohydrate-label-portion-tool.html",
    "weight-goal-timeline-calculator.html",
    "sweat-rate-calculator.html",
}
CALCULATOR_ASSETS = ("css/calculator-suite.css", "js/calculator-suite.js")


class ContractParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body_classes: set[str] = set()
        self.landmarks = {"header": 0, "nav": 0, "main": 0, "footer": 0}
        self.ids: list[str] = []
        self.label_fors: set[str] = set()
        self.controls: list[tuple[str, dict[str, str]]] = []
        self.select_depth = 0
        self.select_options: list[int] = []
        self.label_depth = 0

    @staticmethod
    def attrs(values) -> dict[str, str]:
        return {str(k).lower(): (v or "") for k, v in values}

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        a = self.attrs(attrs)
        if tag == "body":
            self.body_classes = set(a.get("class", "").split())
        if tag in self.landmarks:
            self.landmarks[tag] += 1
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "label" and a.get("for"):
            self.label_fors.add(a["for"])
        if tag == "label":
            self.label_depth += 1
        if tag in {"input", "select", "textarea"}:
            a["_wrapped_label"] = "yes" if self.label_depth else ""
            self.controls.append((tag, a))
        if tag == "select":
            self.select_depth += 1
            self.select_options.append(0)
        elif tag == "option" and self.select_depth:
            self.select_options[-1] += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "label":
            self.label_depth = max(0, self.label_depth - 1)
        if tag.lower() == "select":
            self.select_depth = max(0, self.select_depth - 1)


def main() -> int:
    errors: list[str] = []
    for asset in ("css/premium-v4.css", "css/liquid.css", "css/polish.css"):
        if "prefers-reduced-motion: reduce" not in (ROOT / asset).read_text(encoding="utf-8"):
            errors.append(f"{asset}: reduced-motion fallback is missing")
    if "prefers-reduced-motion: reduce" not in (ROOT / "css" / "calculator-suite.css").read_text(encoding="utf-8"):
        errors.append("css/calculator-suite.css: reduced-motion fallback is missing")
    if 'prefers-reduced-motion: reduce' not in (ROOT / "js" / "polish.js").read_text(encoding="utf-8"):
        errors.append("js/polish.js: reduced-motion guard is missing")
    pages = sorted(ROOT / name for name in KEEP_ROOT_HTML if (ROOT / name).exists())
    pages += sorted(ROOT.glob("*/*.html"))
    seen: set[Path] = set()
    pages = [p for p in pages if not (p in seen or seen.add(p))]

    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        parser = ContractParser()
        parser.feed(text)

        if "site-v3" not in parser.body_classes:
            errors.append(f"{rel}: body is missing the shared site-v3 design scope")
        if rel in CALCULATOR_PAGES:
            for asset in CALCULATOR_ASSETS:
                if Path(asset).name not in text:
                    errors.append(f"{rel}: missing calculator-suite asset {asset}")
                elif text.count(Path(asset).name) != 1:
                    errors.append(f"{rel}: calculator-suite asset must load exactly once: {asset}")
        for asset in REQUIRED_ASSETS:
            if Path(asset).name not in text:
                errors.append(f"{rel}: missing shared asset {asset}")
        cascade_assets = REQUIRED_ASSETS[:2] + REQUIRED_ASSETS[2:5]
        positions = []
        for asset in cascade_assets:
            match = re.search(r"(?<![A-Za-z0-9_-])" + re.escape(Path(asset).name), text)
            positions.append(match.start() if match else -1)
        if any(pos < 0 for pos in positions) or positions != sorted(positions):
            errors.append(f"{rel}: shared stylesheets are not in the required cascade order")
        for landmark in ("header", "nav"):
            if parser.landmarks[landmark] < 1:
                errors.append(f"{rel}: missing {landmark} landmark")
        for landmark in ("main", "footer"):
            if parser.landmarks[landmark] != 1:
                errors.append(f"{rel}: expected one {landmark} landmark, found {parser.landmarks[landmark]}")
        duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        if duplicate_ids:
            errors.append(f"{rel}: duplicate ids: {', '.join(duplicate_ids)}")
        for tag, attrs in parser.controls:
            if tag == "input" and attrs.get("type", "text").lower() in {"hidden", "submit", "button"}:
                continue
            control_id = attrs.get("id", "")
            named = bool(control_id and control_id in parser.label_fors)
            accessible = bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or named or attrs.get("_wrapped_label"))
            if not accessible:
                errors.append(f"{rel}: {tag} control lacks a programmatic label")
        if any(count == 0 for count in parser.select_options):
            errors.append(f"{rel}: empty select control")
        if re.search(r'<(?:font|marquee|center)\b', text, re.I):
            errors.append(f"{rel}: obsolete presentational markup remains")
        if '<meta name="viewport"' not in text:
            errors.append(f"{rel}: responsive viewport meta is missing")
        if not re.search(r'<link\b[^>]*rel=["\'][^"\']*\bicon\b', text, re.I):
            errors.append(f"{rel}: favicon declaration is missing")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for required in ("gm6-tool-bento", "gm6-finder-shell", "gm6-rail", "gm6-macro-score", "gm6-goal-story"):
        if required not in home:
            errors.append(f"index.html: premium homepage component is missing: {required}")

    if errors:
        print(f"FAILED: {len(errors)} visual-contract issue(s)")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"PASS: {len(pages)} pages share one visual, responsive and accessible interaction contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
