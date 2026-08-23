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
    "Macros and goals": [
        "protein.html", "carbs.html", "fats.html",
        "how-much-protein-per-day.html", "how-many-carbs-per-day.html",
        "how-much-fat-per-day.html", "how-to-calculate-macros-by-hand.html",
        "how-to-track-your-macros.html", "macros-without-tracking.html",
        "macros-for-weight-loss.html", "macros-for-muscle-gain.html",
        "macros-for-vegetarians.html", "macros-for-endurance-vs-strength-athletes.html",
        "cutting-bulking-maintenance-explained.html", "body-recomposition-explained.html",
        "bulking-without-gaining-fat.html", "water-weight-vs-fat-loss.html",
        "tdee-vs-bmr.html", "thermic-effect-of-food-explained.html",
        "meal-frequency-and-metabolism.html", "intermittent-fasting-and-macros.html",
    ],
    "Protein and food choices": [
        "high-protein-foods-list.html", "high-protein-breakfast-ideas.html",
        "high-protein-snacks-real-food.html", "protein-on-a-budget.html",
        "plant-based-protein-sources.html", "complete-vs-incomplete-protein.html",
        "protein-quality-scores-pdcaas-diaas.html", "protein-per-meal-guide.html",
        "protein-timing.html", "protein-before-bed.html",
        "protein-for-muscle-growth.html", "protein-powder-101.html",
        "whey-vs-casein-protein.html", "are-protein-bars-actually-healthy.html",
        "simple-vs-complex-carbs.html", "net-carbs-vs-total-carbs.html",
        "carbohydrate-quality-guide.html", "best-time-to-eat-carbs.html",
        "healthy-high-fat-foods.html", "saturated-vs-unsaturated-fat.html",
        "cooking-fats-guide.html", "low-fat-diet-risks.html",
        "fiber-benefits.html", "high-fiber-foods-list.html",
        "soluble-vs-insoluble-fiber.html",
    ],
    "Meals, labels and portions": [
        "how-to-build-a-balanced-meal.html", "balanced-breakfast-formula.html",
        "balanced-vegetarian-meal-formula.html", "serving-size-vs-portion-size.html",
        "portion-sizes-without-a-scale.html", "how-to-read-a-nutrition-label.html",
        "food-labels-serving-size-traps.html", "nutrition-label-rounding-explained.html",
        "how-to-calculate-recipe-nutrition.html", "weighing-cooking-oils-and-sauces.html",
        "choosing-food-database-entry.html", "units-and-conversions-cheat-sheet.html",
        "meal-prep-for-macros.html", "grocery-list-for-balanced-meals.html",
        "batch-cooking-on-a-budget.html", "shelf-stable-balanced-pantry.html",
        "budget-friendly-fruit-vegetables.html", "emergency-pantry-meals.html",
        "how-to-compare-grocery-unit-prices.html", "reduce-food-waste-meal-planning.html",
    ],
    "Training and hydration": [
        "pre-workout-meal-timing.html", "post-workout-meal-guide.html",
        "carbohydrates-for-strength-training.html", "carb-loading-for-athletes.html",
        "hydration-and-performance.html", "how-to-measure-sweat-rate.html",
        "when-do-you-need-electrolytes.html", "sports-drinks-vs-water.html",
        "creatine-explained.html", "caffeine-and-athletic-performance.html",
    ],
    "Eating out": [
        "restaurant-meals-every-diet-guide.html",
        "restaurant-nutrition-information.html",
        "restaurant-food-allergy-communication.html",
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
