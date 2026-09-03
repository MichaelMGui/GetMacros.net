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
    "css/unified-v7.css",
    # theme-fix.css must follow unified-v7. It repairs colours unified-v7.css
    # sets with !important, so loading it any earlier makes those rules no-op --
    # which is exactly what happened when the recovery pass re-appended
    # unified-v7 on its own and left theme-fix in front of it. Editorial v8 is
    # deliberately last because it owns the final page-opening compositions.
    "css/theme-fix.css",
    "css/editorial-v8.css",
    # clean-v9 is last: it redefines every token system to the chosen "Clean"
    # direction, so it has to resolve after the sheets that read those tokens.
    "css/clean-v9.css",
    "js/unified-v7.js",
)
FORBIDDEN_INTERACTION_ASSETS = (
    "js/polish.js",
    "js/site-motion.js",
    "js/studio-v6.js",
    "js/atelier-v5.js",
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
    if "prefers-reduced-motion: reduce" not in (ROOT / "css" / "unified-v7.css").read_text(encoding="utf-8"):
        errors.append("css/unified-v7.css: reduced-motion fallback is missing")
    unified_css = (ROOT / "css" / "unified-v7.css").read_text(encoding="utf-8")
    for marker in (
        'html[data-theme="light"]', 'html[data-theme="dark"] .full-nav',
        '@media (max-width: 900px)', 'position: absolute !important',
        'body.site-v3 main { overflow: visible !important; }', '.quiz-nav .btn:only-child',
    ):
        if marker not in unified_css:
            errors.append(f"css/unified-v7.css: required responsive/theme contract is missing: {marker}")
    quiz_js = (ROOT / "js" / "meal-quiz.js").read_text(encoding="utf-8")
    if "quiz-back" not in quiz_js or "quiz-continue" not in quiz_js or "'<span></span>'" in quiz_js:
        errors.append("js/meal-quiz.js: intentional Back/Continue control contract is missing")
    pages = sorted(ROOT / name for name in KEEP_ROOT_HTML if (ROOT / name).exists())
    # Not design/: those are design-canvas working files, not site pages, and
    # the shared-asset contract does not apply to them.
    pages += sorted(p for p in ROOT.glob("*/*.html") if p.parent.name != "design")
    seen: set[Path] = set()
    pages = [p for p in pages if not (p in seen or seen.add(p))]

    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        parser = ContractParser()
        parser.feed(text)

        if "site-v3" not in parser.body_classes:
            errors.append(f"{rel}: body is missing the shared site-v3 design scope")
        if text.count("data-theme-toggle") != 1:
            errors.append(f"{rel}: expected exactly one shared light/dark theme toggle")
        if text.count('class="nav-utility"') != 1:
            errors.append(f"{rel}: expected exactly one shared navigation utility group")
        if 'localStorage.getItem("gm-theme")||"light"' not in text:
            errors.append(f"{rel}: light-first theme boot is missing")
        if '<meta name="theme-color" content="#e5ebe5">' not in text:
            errors.append(f"{rel}: light-first browser theme color is missing")
        if rel in CALCULATOR_PAGES:
            for asset in CALCULATOR_ASSETS:
                if Path(asset).name not in text:
                    errors.append(f"{rel}: missing calculator-suite asset {asset}")
                elif text.count(Path(asset).name) != 1:
                    errors.append(f"{rel}: calculator-suite asset must load exactly once: {asset}")
        for asset in REQUIRED_ASSETS:
            if Path(asset).name not in text:
                errors.append(f"{rel}: missing shared asset {asset}")
        for asset in FORBIDDEN_INTERACTION_ASSETS:
            if Path(asset).name in text:
                errors.append(f"{rel}: conflicting legacy interaction asset remains: {asset}")
        cascade_assets = REQUIRED_ASSETS[:9]
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
    # gm6-rail belonged to the restaurant explorer, which was a third route to
    # pages the nav and the finder results already reach, sitting directly under
    # two sections that send you to them.
    for required in ("home-launcher", "home-launch-card", "home-guide-grid"):
        if required not in home:
            errors.append(f"index.html: premium homepage component is missing: {required}")
    if "gm6-goal-story" in home:
        errors.append("index.html: removed scrolling goal-story clutter returned")
    if "gm6-restaurants" in home:
        errors.append("index.html: removed restaurant-explorer rail returned")
    if home.count('class="home-launch-card') != 3:
        errors.append("index.html: homepage must expose exactly three primary tool choices")
    for retired in ("order-console-macros", "gm6-finder-shell", "gm6-tool-bento"):
        if retired in home:
            errors.append(f"index.html: retired homepage demo returned: {retired}")
    finder = (ROOT / "restaurant-meal-finder.html").read_text(encoding="utf-8")
    if 'class="meal-database-disclosure"' not in finder:
        errors.append("restaurant-meal-finder.html: optional meal database disclosure is missing")
    search = (ROOT / "search.html").read_text(encoding="utf-8")
    if 'id="search-results-toggle"' not in search or "limit=12" not in search:
        errors.append("search.html: compact initial-result control is missing")

    if errors:
        print(f"FAILED: {len(errors)} visual-contract issue(s)")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"PASS: {len(pages)} pages share one visual, responsive and accessible interaction contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
