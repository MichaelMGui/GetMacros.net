"""The intentionally narrow, indexable product scope for GetMacros.net.

This is an allowlist, not a list of exclusions. New generated pages do not become
indexable merely because a file exists; they must strengthen healthy fast food,
macro tools, or the practical guides that explain those products.
"""
from __future__ import annotations

from collections import OrderedDict


CORE_PAGES = {
    "index.html",
    "healthy-fast-food.html",
    "restaurant-meal-finder.html",
    "restaurant-meal-guides.html",
    "calculators.html",
    "articles.html",
    "blog.html",
    "search.html",
    "about.html",
    "contact.html",
    "privacy.html",
    "terms.html",
    "editorial-policy.html",
    "corrections.html",
    "accessibility.html",
    "sources.html",
    "404.html",
}

RESTAURANT_PAGES = {
    "cava-healthy-meals-macros.html",
    "chick-fil-a-healthy-meals-macros.html",
    "chipotle-healthy-meals-macros.html",
    "dunkin-healthy-breakfast-macros.html",
    "jersey-mikes-healthy-subs-macros.html",
    "kfc-healthy-meals-macros.html",
    "mcdonalds-healthy-meals-macros.html",
    "panda-express-healthy-meals-macros.html",
    "panera-healthy-meals-macros.html",
    "popeyes-healthy-meals-macros.html",
    "starbucks-healthy-food-meals-macros.html",
    "subway-healthy-meals-macros.html",
    "sweetgreen-healthy-meals-macros.html",
    "taco-bell-healthy-meals-macros.html",
    "wendys-healthy-meals-macros.html",
}

TOOL_PAGES = {
    "budget-meal-builder.html",
    "carbohydrate-label-portion-tool.html",
    "nutrition-label-comparison-tool.html",
    "protein-value-calculator.html",
    "recipe-macro-scaler.html",
    "sodium-label-comparison-tool.html",
    "sweat-rate-calculator.html",
    "weight-goal-timeline-calculator.html",
}

GUIDE_GROUPS = OrderedDict({
    "Journal": [
        "best-fast-food-restaurants-for-your-goals.html",
        "how-much-protein-can-your-body-absorb.html",
        "are-diet-drinks-bad-for-you.html",
        "does-creatine-cause-hair-loss.html",
        "calories-vs-macros-what-matters-more.html",
    ],
    "Macros and goals": [
        "protein.html", "carbs.html", "fats.html",
        "how-much-protein-per-day.html", "how-to-calculate-macros-by-hand.html",
        "macros-for-weight-loss.html", "macros-for-muscle-gain.html",
        "cutting-bulking-maintenance-explained.html", "body-recomposition-explained.html",
        "how-many-calories-should-i-eat-a-day.html", "what-are-macros.html",
        "how-to-calculate-maintenance-calories.html", "what-is-a-calorie-deficit.html",
        "can-you-build-muscle-in-a-calorie-deficit.html",
        "when-to-recalculate-calories-and-macros.html",
    ],
    "Eating out": [
        "how-to-eat-out-without-wrecking-your-goal.html",
    ],
    "Nutrients to watch": [
        "how-much-sodium-per-day.html", "how-much-fiber-per-day.html",
    ],
    "Protein and food": [
        "high-protein-foods-list.html",
        "how-to-build-a-balanced-meal-with-macros.html",
    ],
    "Training and everyday eating": [
        "what-to-eat-before-a-workout.html",
        "what-to-eat-after-a-workout.html",
        "why-did-i-gain-weight-overnight.html",
        "how-to-hit-protein-goal-on-budget.html",
        "calories-on-rest-days.html",
    ],
    "Labels and recipes": [
        "serving-size-vs-portion-size.html", "how-to-read-a-nutrition-label.html",
        "how-to-calculate-recipe-nutrition.html",
    ],
})

GUIDE_PAGES = {path for paths in GUIDE_GROUPS.values() for path in paths}
KEEP_ROOT_HTML = CORE_PAGES | RESTAURANT_PAGES | TOOL_PAGES | GUIDE_PAGES


def section_for(path: str) -> str:
    if path in RESTAURANT_PAGES or path in {
        "healthy-fast-food.html", "restaurant-meal-finder.html", "restaurant-meal-guides.html"
    }:
        return "Healthy fast food"
    if path in TOOL_PAGES or path == "calculators.html":
        return "Tools"
    for section, paths in GUIDE_GROUPS.items():
        if path in paths:
            return section
    if path in {"about.html", "contact.html", "privacy.html", "terms.html",
                "editorial-policy.html", "corrections.html", "accessibility.html",
                "sources.html"}:
        return "Trust"
    return "Site"


def decision_for(path: str) -> tuple[str, str]:
    if path in CORE_PAGES | RESTAURANT_PAGES | TOOL_PAGES:
        return "CORE", "Directly supports healthy fast-food discovery, macro tools, or site trust."
    if path in GUIDE_PAGES:
        return "SUPPORT", "Focused practical guidance that explains or supports a core GetMacros task."
    if path.startswith("es/") or path.startswith("fr/"):
        return "REMOVE", "Partial translation footprint without equivalent translated tools and guides."
    return "REMOVE", "Outside the focused healthy-fast-food and macro-tools product, duplicative, or insufficiently distinctive."
