#!/usr/bin/env python3
"""Rewrite titles and H1s to match how people actually search.

Two problems this fixes.

First, four titles were cut mid-sentence by an earlier trimming pass that tried
to reserve room for a " | GetMacros.net" suffix -- "A balanced breakfast
formula that works with sweet or". A truncated title is worse than a long one:
Google will shorten a long title itself, but it cannot repair a sentence that
stops mid-clause.

Second, and the larger problem, many titles were written as editorial headlines
rather than as the phrase a person types. "Dehydration and Performance: What
Matters" is a good headline for a magazine and a bad one for search, because
nobody types that. "Does Dehydration Affect Performance" is what gets typed.
Leading with the query wording matters more than being clever, because the
match between query and title is most of what earns the click.

Rules applied here:
  - lead with the words of the query, not the conclusion
  - keep question titles as questions; that is how these are searched
  - prefer concrete nouns people say ("cooking oil") over category language
    ("cooking fats")
  - no site-name suffix on articles: Google already shows the site name, and
    the suffix only eats visible characters
  - a title over ~60 characters is fine when the extra words are query words;
    it is not fine when they are decoration

Runs after the generators but before recover_site_focus.py, which re-syncs
og:title and twitter:title from the final <title>. Running it later leaves the
social tags quoting the old headline.
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

# slug -> (title, h1 or None to leave the H1 alone)
TITLES = {
    # --- cut mid-sentence by the old trimmer ---
    "balanced-breakfast-formula": (
        "What to Eat for Breakfast: A Balanced Formula",
        "What to eat for breakfast: a formula that works with sweet or savory food"),
    "batch-cooking-on-a-budget": (
        "Batch Cooking on a Budget Without Eating the Same Meal",
        None),
    "how-to-compare-grocery-unit-prices": (
        "How to Compare Grocery Unit Prices and Actually Save",
        None),
    "restaurant-nutrition-information": (
        "How Accurate Is Restaurant Nutrition Information?",
        "How accurate is restaurant nutrition information?"),

    # --- headline rewritten to the query ---
    "hydration-and-performance": (
        "Does Dehydration Affect Athletic Performance?",
        "Does dehydration affect performance?"),
    "thermic-effect-of-food-explained": (
        "Does Digesting Food Burn Calories? TEF Explained",
        "Does digesting food burn calories?"),
    "nutrition-label-rounding-explained": (
        "Why Nutrition Label Macros Don't Add Up",
        "Why nutrition label macros don't add up"),
    "carbohydrate-quality-guide": (
        "Are Carbs Bad for You? Carb Quality Explained",
        "Are carbs bad for you? A better question than good or bad"),
    "post-workout-meal-guide": (
        "What to Eat After a Workout (and How Soon)",
        "What to eat after a workout"),
    "pre-workout-meal-timing": (
        "What to Eat Before a Workout and When",
        "What to eat before a workout"),
    "protein-per-meal-guide": (
        "How Much Protein Per Meal Do You Need?",
        "How much protein per meal do you need?"),
    "macros-without-tracking": (
        "How to Hit Your Macros Without Counting Every Gram",
        None),
    "emergency-pantry-meals": (
        "Easy Pantry Meals for No-Time, No-Money Days",
        None),
    "choosing-food-database-entry": (
        "How to Pick the Right Food in a Calorie Tracker",
        "How to pick the right food in a calorie tracker"),
    "units-and-conversions-cheat-sheet": (
        "Nutrition Conversions: Grams, Ounces, Cups and Calories",
        None),
    "how-to-measure-sweat-rate": (
        "How to Calculate Your Sweat Rate",
        "How to calculate your sweat rate"),
    "restaurant-meals-every-diet-guide": (
        "Restaurant Meals for Keto, Vegan and Other Diets",
        "Restaurant meals for keto, vegan and other diets"),
    "serving-size-vs-portion-size": (
        "Serving Size vs. Portion Size: Why Your Macros Are Off",
        None),
    "weighing-cooking-oils-and-sauces": (
        "How to Measure Cooking Oil and Sauces for Macros",
        None),
    "reduce-food-waste-meal-planning": (
        "How to Reduce Food Waste With a Use-First Meal Plan",
        None),
    "shelf-stable-balanced-pantry": (
        "Healthy Pantry Staples: A Shelf-Stable Grocery List",
        None),
    "grocery-list-for-balanced-meals": (
        "Healthy Grocery List for Balanced Meals",
        None),
    "protein-on-a-budget": (
        "Cheap High-Protein Foods on a Budget",
        None),
    "high-protein-snacks-real-food": (
        "High-Protein Snacks From Real Food, Not Bars",
        None),
    "restaurant-food-allergy-communication": (
        "How to Order Safely With a Food Allergy",
        "How to order safely with a food allergy"),
    "how-to-calculate-recipe-nutrition": (
        "How to Calculate Calories and Macros in a Recipe",
        None),
    "budget-friendly-fruit-vegetables": (
        "Cheap Fruits and Vegetables: Fresh, Frozen or Canned?",
        None),
    "cooking-fats-guide": (
        "Best Cooking Oils: Which Fat to Use and When",
        "Best cooking oils: which fat to use and when"),
    "carbohydrates-for-strength-training": (
        "How Many Carbs Do You Need for Strength Training?",
        "How many carbs do you need for strength training?"),
    "low-fat-diet-risks": (
        "Are Low-Fat Diets Bad for You? The Risks",
        None),
    "meal-prep-for-macros": (
        "Meal Prep for Macros: A Simple Weekly System",
        None),
    "protein-quality-scores-pdcaas-diaas": (
        "Protein Quality Explained: PDCAAS vs. DIAAS",
        None),
    "macros-for-endurance-vs-strength-athletes": (
        "Macros for Endurance vs. Strength Athletes",
        None),
    "balanced-vegetarian-meal-formula": (
        "How to Build a Balanced Vegetarian Meal",
        None),
    "soluble-vs-insoluble-fiber": (
        "Soluble vs. Insoluble Fiber: Which Foods Have Which",
        None),
    "bulking-without-gaining-fat": (
        "How to Bulk Without Gaining Fat",
        None),

    # --- H1 case, so the site does not mix Title Case and sentence case ---
    "protein": ("What Does Protein Do? Functions and Deficiency | GetMacros",
                "What does protein do in your body?"),
    "fats": ("What Does Fat Do? Hormones, Vitamins and Intake | GetMacros",
             "What does fat do in your body?"),
    "carbs": ("What Do Carbs Do? Energy, Glycogen and Fiber | GetMacros",
              "What do carbs do in your body?"),
    "when-do-you-need-electrolytes": (None, "When do you actually need electrolytes?"),
    "protein-value-calculator": (None, "Protein cost per gram calculator"),
    "recipe-macro-scaler": (None, "Recipe calories and macros calculator"),
}


def main():
    os.chdir(ROOT)
    changed = 0
    for slug, (title, h1) in sorted(TITLES.items()):
        f = slug + ".html"
        if not os.path.exists(f):
            continue
        c = open(f, encoding="utf-8").read()
        out = c
        if title:
            out = re.sub(r"<title>.*?</title>",
                         lambda _: "<title>" + html.escape(title, quote=False) + "</title>",
                         out, count=1, flags=re.S)
        if h1:
            out = re.sub(r"(<h1[^>]*>).*?(</h1>)",
                         lambda m: m.group(1) + html.escape(h1, quote=False) + m.group(2),
                         out, count=1, flags=re.S)
        if out != c:
            open(f, "w", encoding="utf-8").write(out)
            changed += 1
    print(f"retitled {changed} page(s)")

    over = []
    for f in sorted(glob.glob("*.html")):
        m = re.search(r"<title>(.*?)</title>", open(f, encoding="utf-8").read(), re.S)
        if not m:
            continue
        t = html.unescape(m.group(1)).strip()
        # A title ending in a preposition or conjunction is a cut sentence.
        if re.search(r"\b(or|and|the|a|an|with|without|than|for|of|to|in)$", t, re.I):
            over.append((f, t))
    if over:
        print("WARNING: title still reads as cut mid-sentence:")
        for f, t in over:
            print(f"   {f}: {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
