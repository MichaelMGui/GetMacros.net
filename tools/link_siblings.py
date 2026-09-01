#!/usr/bin/env python3
"""Cross-link the calculators to each other.

Every tool page reached the rest of the site only through the header and the
calculators hub, so eight of the site's nine tools sat on two inbound internal
links each -- the weakest pages in the link graph despite being the ones people
arrive on from a search for a specific calculation. A reader who has just
worked out a portion of sodium has an obvious next question, and until now the
page ended without offering it.

This runs after the focus pass so it sees the final set of live pages, and it
is idempotent: the band is keyed by a marker class and replaced, not appended,
on every build.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from site_scope import TOOL_PAGES

ROOT = Path(__file__).resolve().parents[1]
MARKER = "gm-sibling-tools"

# Ordered so the band reads as a considered shortlist rather than a dump: the
# two most generally useful first, then the label tools, then the specialists.
TOOLS: list[tuple[str, str, str]] = [
    ("calculators.html", "Free macro calculator",
     "Estimate daily calories, protein, carbohydrate and fat from your own numbers."),
    ("recipe-macro-scaler.html", "Recipe calories and macros",
     "Scale a recipe up or down and get the numbers per serving."),
    ("nutrition-label-comparison-tool.html", "Compare two labels",
     "Put two foods on equal footing by serving and per 100 calories."),
    ("sodium-label-comparison-tool.html", "Sodium per portion",
     "Convert label sodium to the portion you actually eat."),
    ("carbohydrate-label-portion-tool.html", "Carbs per portion",
     "Multiply total carbohydrate by the servings you plan to eat."),
    ("protein-value-calculator.html", "Protein cost per gram",
     "Compare what a gram of protein costs in two foods."),
    ("weight-goal-timeline-calculator.html", "Weight goal timeline",
     "Estimate how long a goal takes at a safe rate."),
    ("budget-meal-builder.html", "Budget meal builder",
     "Build a practical meal around the ingredients you have."),
    ("sweat-rate-calculator.html", "Sweat rate",
     "Estimate fluid loss from a single training session."),
]

BAND = re.compile(
    r'<section class="[^"]*\b' + MARKER + r'\b[^"]*">.*?</section>\s*',
    re.S,
)


# Hand-picked "keep reading" links for the pages the generated related-boxes
# never reached: the three nutrient pillars and a handful of guides that ended
# without pointing anywhere. Each list is chosen for that page, not templated,
# so no two pages carry the same set. Anything already linked from the page
# body is left out rather than repeated.
KEEP_READING: dict[str, list[tuple[str, str]]] = {
    "protein.html": [
        ("how-much-protein-per-day.html", "How much protein per day"),
        ("high-protein-foods-list.html", "High-protein foods ranked"),
        ("what-are-macros.html", "What are macros?"),
        ("calculators.html", "Free macro calculator"),
    ],
    "carbs.html": [
        ("how-much-fiber-per-day.html", "How much fiber per day"),
        ("what-are-macros.html", "What are macros?"),
        ("how-many-calories-should-i-eat-a-day.html", "How many calories per day"),
        ("how-to-read-a-nutrition-label.html", "Read a nutrition label"),
    ],
    "fats.html": [
        ("what-are-macros.html", "What are macros?"),
        ("how-many-calories-should-i-eat-a-day.html", "How many calories per day"),
        ("how-to-read-a-nutrition-label.html", "Read a nutrition label"),
        ("calculators.html", "Free macro calculator"),
    ],
    "how-much-fiber-per-day.html": [
        ("carbs.html", "What carbohydrates actually do"),
        ("high-protein-foods-list.html", "High-protein foods ranked"),
        ("healthy-fast-food.html", "Fiber in fast-food meals"),
    ],
    "are-diet-drinks-bad-for-you.html": [
        ("how-many-calories-should-i-eat-a-day.html", "How many calories per day"),
        ("how-much-sodium-per-day.html", "How much sodium per day"),
        ("restaurant-meal-finder.html", "Find a meal that fits"),
    ],
    "body-recomposition-explained.html": [
        ("what-are-macros.html", "What are macros?"),
        ("how-to-eat-out-without-wrecking-your-goal.html", "Eating out without wrecking it"),
        ("restaurant-meal-finder.html", "Find a meal that fits"),
    ],
    "calories-vs-macros-what-matters-more.html": [
        ("what-are-macros.html", "What are macros?"),
        ("how-many-calories-should-i-eat-a-day.html", "How many calories per day"),
        ("how-to-calculate-macros-by-hand.html", "Calculate macros by hand"),
    ],
    "does-creatine-cause-hair-loss.html": [
        ("protein.html", "What protein actually does"),
        ("how-much-protein-per-day.html", "How much protein per day"),
        ("what-are-macros.html", "What are macros?"),
    ],
    "how-much-protein-can-your-body-absorb.html": [
        ("how-much-protein-per-day.html", "How much protein per day"),
        ("high-protein-foods-list.html", "High-protein foods ranked"),
        ("how-to-eat-out-without-wrecking-your-goal.html", "Eating out without wrecking it"),
    ],
    "how-to-calculate-recipe-nutrition.html": [
        ("recipe-macro-scaler.html", "Recipe calories and macros"),
        ("serving-size-vs-portion-size.html", "Serving size vs. portion size"),
        ("what-are-macros.html", "What are macros?"),
    ],
    "serving-size-vs-portion-size.html": [
        ("how-to-read-a-nutrition-label.html", "Read a nutrition label"),
        ("how-much-sodium-per-day.html", "How much sodium per day"),
        ("nutrition-label-comparison-tool.html", "Compare two labels"),
    ],
    "best-fast-food-restaurants-for-your-goals.html": [
        ("how-to-eat-out-without-wrecking-your-goal.html", "Eating out without wrecking it"),
        ("how-much-sodium-per-day.html", "How much sodium per day"),
        ("restaurant-meal-finder.html", "Find a meal that fits"),
    ],
}

READING_MARKER = "gm-keep-reading"
READING_BAND = re.compile(
    r'<section class="[^"]*\b' + READING_MARKER + r'\b[^"]*">.*?</section>\s*',
    re.S,
)


def keep_reading(name: str) -> str:
    links = [
        f'<a href="{href}">{html.escape(label)}</a>'
        for href, label in KEEP_READING[name]
        if (ROOT / href).exists()
    ]
    if not links:
        return ""
    return (
        f'<section class="tight {READING_MARKER}"><div class="container">'
        '<p class="section-intro"><strong>Keep reading:</strong> '
        + " &middot; ".join(links)
        + "</p></div></section>\n"
    )


def band_for(current: str) -> str:
    # Rotate the list so each page shows the five tools that follow it, rather
    # than the same five every time. Taking the head of a fixed order left the
    # last three tools linked from nothing but the hub, which is the problem
    # this band exists to solve.
    order = [t[0] for t in TOOLS]
    start = order.index(current) + 1 if current in order else 0
    rotated = TOOLS[start:] + TOOLS[:start]
    cards = []
    for href, label, blurb in rotated:
        if href == current or not (ROOT / href).exists():
            continue
        cards.append(
            f'<a class="tool-card" href="{href}"><h3>{html.escape(label)}</h3>'
            f"<p>{html.escape(blurb)}</p></a>"
        )
        if len(cards) == 6:
            break
    return (
        f'<section class="{MARKER}"><div class="container">'
        '<div class="section-head"><p class="eyebrow">More calculators</p>'
        "<h2>Other numbers worth checking</h2>"
        "<p>Every tool on GetMacros is free, runs in your browser, and shows the "
        "arithmetic it used.</p></div>"
        f'<div class="tool-grid">{"".join(cards)}</div>'
        '<p class="metric-note"><a class="text-link" href="calculators.html">'
        "See every calculator &rarr;</a></p>"
        "</div></section>\n"
    )


def main() -> int:
    changed = 0
    # The calculator hub already contains the complete, categorized library.
    # Adding this band there repeated the same links a second time.
    for name in sorted(TOOL_PAGES):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = BAND.sub("", text)
        # Ahead of the auto-anchor ad slot when there is one, so the band stays
        # part of the content rather than sitting below an advertisement.
        anchor = '<div class="ad-auto-anchor"'
        insert_at = text.find(anchor)
        if insert_at == -1:
            insert_at = text.find("</main>")
        if insert_at == -1:
            continue
        path.write_text(text[:insert_at] + band_for(name) + text[insert_at:],
                        encoding="utf-8")
        changed += 1

    reading = 0
    for name in sorted(KEEP_READING):
        path = ROOT / name
        if not path.exists():
            continue
        text = READING_BAND.sub("", path.read_text(encoding="utf-8"))
        # Generated articles already end in a related-links line of their own.
        # A second one under the same heading reads as a duplicate, so leave
        # those pages alone and only fill in the ones that end nowhere.
        if "<strong>Keep reading:</strong>" in text:
            continue
        anchor = '<div class="ad-auto-anchor"'
        insert_at = text.find(anchor)
        if insert_at == -1:
            insert_at = text.find("</main>")
        if insert_at == -1:
            continue
        path.write_text(text[:insert_at] + keep_reading(name) + text[insert_at:],
                        encoding="utf-8")
        reading += 1

    print(f"sibling tool links refreshed on {changed} page(s); "
          f"keep-reading links on {reading} page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
