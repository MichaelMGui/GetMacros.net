#!/usr/bin/env python3
"""Build substantial chain guides from the verified central meal dataset."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from focus_components import SITE, breadcrumbs, footer, head, nav

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "js" / "meal-data.js"

CHAIN_CONFIG = {
    "Chipotle": {
        "title": "Healthy Chipotle Orders: Calories, Protein & Macros | GetMacros",
        "h1": "Healthy Chipotle orders by calories and protein",
        "intro": "Chipotle is unusually flexible: protein, rice, beans, vegetables and toppings can be adjusted independently. Compare the complete builds we track, then use the official calculator for your exact custom bowl.",
        "source": "https://www.chipotle.com/nutrition-calculator",
        "source_label": "Chipotle nutrition calculator",
        "advice": [
            "Choose the protein first; doubling it changes both calories and cost, so check the live builder.",
            "Rice and beans are not interchangeable: beans add fibre and protein, while rice mainly raises carbohydrate and energy.",
            "Cheese, sour cream, guacamole and vinaigrette can make a bowl substantially larger. That may suit bulking, but it should be intentional.",
        ],
    },
    "Sweetgreen": {
        "title": "Healthy Sweetgreen Bowls: Calories & Protein | GetMacros",
        "h1": "Healthy Sweetgreen bowls by calories and protein",
        "intro": "Sweetgreen bowls range from lighter vegetable-led salads to substantial grain bowls. Protein, warm grains, avocado, cheese, nuts and dressing explain most of the difference.",
        "source": "https://www.sweetgreen.com/menu",
        "source_label": "Sweetgreen menu",
        "advice": [
            "A salad name does not determine its calorie total; grains, nuts, cheese, avocado and dressing matter more.",
            "For a meal rather than a side salad, check that the bowl contains a meaningful protein source and enough food for your appetite.",
            "Plant-based bowls can be high in fibre but lower in protein. Add tofu or another listed protein if that is your priority.",
        ],
    },
    "CAVA": {
        "title": "Healthy CAVA Orders: Bowls, Calories & Protein | GetMacros",
        "h1": "Healthy CAVA bowls and orders",
        "intro": "CAVA bowls combine bases, proteins, dips, toppings and dressings, so a menu name is only a starting point. Compare the tracked standard builds and confirm custom changes with CAVA.",
        "source": "https://support.cava.com/en_us/where-can-i-find-cava-s-nutritional-and-allergen-information-BJ_6nAj3T",
        "source_label": "CAVA nutrition and allergen information",
        "advice": [
            "Start with greens, grains or a mix based on appetite and training needs, not because one base is universally better.",
            "Dips and dressings are easy to stack. Choose the ones you value instead of automatically adding every option.",
            "Some CAVA nutrients are not available in a form we can verify for every build; missing values remain blank rather than being treated as zero.",
        ],
    },
    "Chick-fil-A": {
        "title": "Healthy Chick-fil-A Options: High-Protein Meals | GetMacros",
        "h1": "Healthy Chick-fil-A options and macros",
        "intro": "Chick-fil-A has several protein-forward grilled entrées, but sauces, dressings and sides determine the final meal. Compare the entrée first, then count the complete order.",
        "source": "https://www.chick-fil-a.com/nutrition-allergens",
        "source_label": "Chick-fil-A nutrition and allergens",
        "advice": [
            "Grilled nuggets are exceptionally protein-efficient, but the smaller count may need a side to become a complete meal.",
            "Salad dressing and dipping sauces are separate items. Add the packet you actually use, not an assumed amount.",
            "Breakfast sandwiches and lunch entrées solve different appetite needs; compare them within the meal you are buying.",
        ],
    },
    "Subway": {
        "title": "Healthy Subway Orders: Calories, Protein & Macros | GetMacros",
        "h1": "Healthy Subway orders by calories and protein",
        "intro": "At Subway, size and customization matter as much as the sandwich name. Bread length, extra protein, cheese and sauce can turn one menu item into very different meals.",
        "source": "https://www.subway.com/en-us/menunutrition1/nutrition",
        "source_label": "Subway U.S. nutrition",
        "advice": [
            "Compare six-inch and footlong portions directly; a footlong is not just a label change—it is roughly twice the food.",
            "Extra vegetables add volume, while cheese and sauces change energy and sodium more substantially.",
            "A salad can be protein-forward when it includes a real protein portion; dressing remains part of the meal.",
        ],
    },
    "Panera": {
        "title": "Healthy Panera Orders: Calories & Protein | GetMacros",
        "h1": "Healthy Panera orders by calories and protein",
        "intro": "Panera's half portions and You Pick Two format make portion size the main decision. Compare the food you plan to combine, including bread, dressing and sides.",
        "source": "https://www.panerabread.com/en-us/menu/nutrition.html",
        "source_label": "Panera nutrition information",
        "advice": [
            "Half portions are useful when pairing two foods, but two halves plus bread can still be a substantial order.",
            "Soups, sandwiches and salads often differ more in sodium than people expect; compare the full combination.",
            "Keep or skip the included side based on appetite rather than treating bread or fruit as automatically good or bad.",
        ],
    },
    "Starbucks": {
        "title": "Healthy Starbucks Food: Calories & Protein | GetMacros",
        "h1": "Healthy Starbucks food and breakfast options",
        "intro": "Starbucks food is only half the order when a drink is involved. Compare breakfast sandwiches and protein boxes here, then add the beverage you actually choose.",
        "source": "https://www.starbucks.com/menu/food/lunch/protein-boxes",
        "source_label": "Starbucks food menu",
        "advice": [
            "Count food and drinks separately; milk, syrup and size can make the beverage the larger part of the order.",
            "Protein boxes are mixed meals with several components, not a single protein food. Their calories reflect the whole box.",
            "For breakfast, compare protein and total energy together so a low number does not leave you hungry an hour later.",
        ],
    },
    "McDonald’s": {
        "title": "Healthy McDonald's Options: Calories & Protein | GetMacros",
        "h1": "Healthy McDonald's options and macros",
        "intro": "McDonald's has useful smaller entrées and breakfast options, but a complete order depends on sides, sauces and drinks. Compare the item first, then build the meal around your appetite.",
        "source": "https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html",
        "source_label": "McDonald's U.S. nutrition calculator",
        "advice": [
            "A hamburger can anchor a smaller meal; it is not automatically a complete meal for every adult.",
            "Breakfast sandwiches can offer more protein than many snack-style orders, with sodium as an important trade-off.",
            "Fries, sauces and caloric drinks belong in the comparison when they are part of what you eat.",
        ],
    },
    "Wendy’s": {
        "title": "Healthy Wendy's Options: Calories & Protein | GetMacros",
        "h1": "Healthy Wendy's options and macros",
        "intro": "Wendy's offers burgers, chicken, salads and baked potatoes with very different nutrition profiles. A salad is not automatically lighter once dressing and toppings are included.",
        "source": "https://www.wendys.com/en-us/nutrition-and-health",
        "source_label": "Wendy's nutrition and health",
        "advice": [
            "Baked potatoes work as a carbohydrate side or base; toppings determine whether they stay simple or become a larger entrée.",
            "For salads, include the dressing and crunchy toppings you actually use.",
            "Compare single and larger burgers by both protein and total energy rather than assuming the biggest item is required for a high-protein meal.",
        ],
    },
    "Taco Bell": {
        "title": "Healthy Taco Bell Options: Calories & Protein | GetMacros",
        "h1": "Healthy Taco Bell options and macros",
        "intro": "Taco Bell is highly customizable and has more vegetarian flexibility than many chains. Compare bowls and standard items, then account for add-ons, sauces and removed ingredients.",
        "source": "https://www.tacobell.com/nutrition/info",
        "source_label": "Taco Bell nutrition information",
        "advice": [
            "Beans can add fibre and protein to vegetarian orders; removing meat without replacing it can leave a smaller meal.",
            "Bowls make ingredients easier to adjust, but cheese, sour cream and sauces still count.",
            "Ordering several small items can exceed one substantial entrée, so compare the full order rather than each item alone.",
        ],
    },
    "Panda Express": {
        "title": "Healthy Panda Express Orders: Calories & Protein | GetMacros",
        "h1": "Healthy Panda Express orders and macros",
        "intro": "Panda Express orders are combinations of entrées and sides. The side can change calories, carbohydrate, vegetables and sodium as much as the entrée choice.",
        "source": "https://www.pandaexpress.com/nutritioninformation",
        "source_label": "Panda Express nutrition information",
        "advice": [
            "Compare entrée and side as one plate; an entrée number alone does not describe the meal.",
            "Mixed vegetables can add volume, while rice or noodles provide more carbohydrate and energy for larger needs.",
            "Sauced entrées often carry more sodium and sugar; use the official source for the exact current recipe.",
        ],
    },
    "KFC": {
        "title": "Healthy KFC Options: Calories & Protein | GetMacros",
        "h1": "Healthy KFC options and macros",
        "intro": "At KFC, chicken portion, preparation and sides shape the meal. Protein can be high, while sodium and the number of pieces are the most useful trade-offs to watch.",
        "source": "https://www.nutritionix.com/kfc/menu/premium",
        "source_label": "KFC menu nutrition",
        "advice": [
            "Count the number and type of chicken pieces you actually order; breast, thigh and tenders are not interchangeable.",
            "Sides can add vegetables, starch or extra energy. Choose them for the job the meal needs to do.",
            "Plant-based meal options are limited in the tracked U.S. menu and shared preparation may matter for dietary restrictions.",
        ],
    },
    "Popeyes": {
        "title": "Healthy Popeyes Options: Calories & Protein | GetMacros",
        "h1": "Healthy Popeyes options and macros",
        "intro": "Popeyes meals combine fried chicken or tenders with sauces, biscuits and sides. Compare the full portion and keep sodium visible alongside protein.",
        "source": "https://www.popeyes.com/nutritional-information",
        "source_label": "Popeyes nutritional information",
        "advice": [
            "Tender count is the clearest portion control; sauce and biscuit are separate parts of the order.",
            "Higher protein does not erase sodium or total energy, so use all three numbers for the decision.",
            "Plant-based main options are limited in the tracked menu; do not infer suitability from a side without checking ingredients.",
        ],
    },
    "Jersey Mike’s": {
        "title": "Healthy Jersey Mike's Subs: Calories & Protein | GetMacros",
        "h1": "Healthy Jersey Mike's subs and macros",
        "intro": "Jersey Mike's portions vary sharply by size, bread and preparation. Compare regular subs and Sub in a Tub options, then use the live builder for oil, cheese and custom amounts.",
        "source": "https://subs.jerseymikes.com/nutrition",
        "source_label": "Jersey Mike's nutrition builder",
        "advice": [
            "Sub size is the first variable to check; larger sizes scale bread, filling and sodium together.",
            "Oil, cheese and mayonnaise can be worthwhile, but they should be included in the number you compare.",
            "Sub in a Tub removes bread but does not guarantee a low-calorie or allergy-safe order.",
        ],
    },
    "Dunkin’": {
        "title": "Healthy Dunkin' Breakfast: Calories & Protein | GetMacros",
        "h1": "Healthy Dunkin' breakfast options and macros",
        "intro": "Dunkin' breakfast decisions include both food and drinks. Compare wraps and sandwiches here, then add the coffee size, milk and sweetener you actually order.",
        "source": "https://www.dunkindonuts.com/en/menu/nutrition",
        "source_label": "Dunkin' nutrition",
        "advice": [
            "A drink can contribute little or a lot depending on milk, flavouring and size; count it separately from breakfast food.",
            "Wake-Up Wraps are smaller portions, while sandwiches are more substantial. Choose based on appetite, not the healthier-sounding name.",
            "Sodium varies across egg, cheese and meat combinations, so compare the complete sandwich.",
        ],
    },
}


def parse_meals() -> list[dict]:
    src = DATA.read_text(encoding="utf-8")
    meals = []
    for raw in re.findall(r"\{chain:.*?\}(?=,\n|\n\];|\n\])", src, re.S):
        obj = re.sub(r"(\{|,)\s*([a-zA-Z_]\w*)\s*:", r'\1"\2":', raw)
        obj = re.sub(r"'((?:[^'\\]|\\.)*)'",
                     lambda m: json.dumps(m.group(1).replace("\\'", "'")), obj)
        meals.append(json.loads(obj))
    return meals


def item_type(meal: dict) -> str:
    name = meal["name"].lower()
    if meal.get("meal") == "breakfast":
        return "Breakfast"
    if any(word in name for word in ("side", "apple slices", "coleslaw", "green beans")):
        return "Side"
    if meal.get("size") == "small" and (meal.get("p") or 0) < 10:
        return "Side / snack"
    return "Entrée / meal"


def n(value, unit="") -> str:
    return "&mdash;" if value is None else f"{value:g}{unit}"


def efficiency(meal: dict) -> float | None:
    if meal.get("cal") and meal.get("p") is not None:
        return meal["p"] / meal["cal"] * 100
    return None


def table(meals: list[dict]) -> str:
    rows = []
    for m in meals:
        eff = efficiency(m)
        rows.append(f'''<tr><th scope="row">{html.escape(m["name"])}</th>
<td>{html.escape(item_type(m))}</td><td>{n(m.get("cal"))}</td><td>{n(m.get("p"), " g")}</td>
<td>{n(m.get("c"), " g")}</td><td>{n(m.get("f"), " g")}</td><td>{n(m.get("na"), " mg")}</td>
<td>{"&mdash;" if eff is None else f"{eff:.1f} g"}</td></tr>''')
    return '''<div class="table-wrap"><table class="comparison-table"><thead><tr>
<th scope="col">Tracked standard item</th><th scope="col">Type</th><th scope="col">Calories</th>
<th scope="col">Protein</th><th scope="col">Carbs</th><th scope="col">Fibre</th>
<th scope="col">Sodium</th><th scope="col">Protein / 100 cal</th></tr></thead><tbody>''' + "".join(rows) + "</tbody></table></div>"


def pick_cards(meals: list[dict], label: str) -> str:
    out = []
    for i, m in enumerate(meals, 1):
        out.append(f'''<article class="pick-card"><span class="rank">{html.escape(label)} #{i}</span>
<h3>{html.escape(m["name"])}</h3><p>{html.escape(m["why"])}</p><div class="pick-metrics">
<span>{n(m.get("cal"))} calories</span><span>{n(m.get("p"), " g")} protein</span>
<span>{n(m.get("f"), " g")} fibre</span><span>{n(m.get("na"), " mg")} sodium</span></div></article>''')
    return "".join(out)


def build_page(chain: str, meals: list[dict]) -> tuple[str, str, str, str]:
    cfg = CHAIN_CONFIG[chain]
    path = meals[0]["url"]
    title, h1 = cfg["title"], cfg["h1"]
    meta = (f"Compare {chain} options by calories, protein, carbs, fibre and sodium. "
            "See high-protein, lower-calorie and goal-based picks from verified menu data.")
    ranked_protein = sorted([m for m in meals if m.get("p") is not None], key=lambda m: m["p"], reverse=True)[:3]
    substantial = [m for m in meals if item_type(m) not in {"Side", "Side / snack"}
                   and ((m.get("p") or 0) >= 15 or (m.get("cal") or 0) >= 250)]
    lighter = sorted([m for m in substantial if m.get("cal") is not None], key=lambda m: m["cal"])[:3]
    energy = sorted([m for m in substantial if m.get("cal") is not None], key=lambda m: m["cal"], reverse=True)[:3]
    vegetarian = sorted([m for m in meals if "vegetarian" in m.get("diet", [])], key=lambda m: m.get("p") or -1, reverse=True)
    items = [{"@type": "ListItem", "position": i, "name": m["name"]} for i, m in enumerate(meals, 1)]
    schema = [
        {"@context": "https://schema.org", "@type": "WebPage", "name": h1,
         "url": f"{SITE}/{path}", "description": meta, "dateModified": "2026-08-23",
         "publisher": {"@type": "Organization", "name": "GetMacros.net", "url": f"{SITE}/"}},
        {"@context": "https://schema.org", "@type": "ItemList", "name": f"Tracked {chain} menu options",
         "numberOfItems": len(items), "itemListElement": items},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Healthy Fast Food", "item": f"{SITE}/healthy-fast-food.html"},
            {"@type": "ListItem", "position": 3, "name": chain, "item": f"{SITE}/{path}"},
        ]},
    ]
    advice = "".join(f"<li>{html.escape(text)}</li>" for text in cfg["advice"])
    veg = ""
    if vegetarian:
        veg = f'''<section><div class="container"><div class="section-head"><p class="eyebrow">Dietary pattern</p>
<h2>Vegetarian options in the tracked data</h2><p>These labels describe the standard build only. Confirm ingredients and cross-contact with the restaurant.</p></div>
<div class="pick-grid">{pick_cards(vegetarian[:4], "Vegetarian")}</div></div></section>'''
    body = f'''{head(path, title, meta, schema=schema)}
<body class="site-v3 article-page restaurant-guide recovery-page">{nav("fastfood")}
<main id="main-content">{breadcrumbs([("Home", "index.html"), ("Healthy Fast Food", "healthy-fast-food.html"), (chain, None)])}
<section class="focus-page-hero"><div class="container"><p class="eyebrow">{html.escape(chain)} nutrition guide</p>
<h1>{html.escape(h1)}</h1><p>{html.escape(cfg["intro"])}</p><div class="stat-row">
<span>{len(meals)} tracked options</span><span>Official source checked August 2026</span><span>No missing value treated as zero</span></div>
<div class="focus-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Find my best match</a>
<a class="btn btn-outline" href="#menu-comparison">Compare the menu</a></div></div></section>
<section id="menu-comparison"><div class="container"><div class="section-head"><p class="eyebrow">Complete tracked menu</p>
<h2>Compare every {html.escape(chain)} option we track</h2><p>These are standard U.S. menu builds from the central GetMacros dataset. Dashes mean the value was not available in a form we could verify—not zero.</p></div>
{table(meals)}<p class="metric-note"><strong>Protein per 100 calories</strong> = protein grams ÷ calories × 100. It is a transparent efficiency metric, not a health score.</p></div></section>
<section class="data-section"><div class="container"><div class="section-head"><p class="eyebrow">High protein</p><h2>Highest-protein {html.escape(chain)} picks</h2>
<p>Ranked only by published protein. Calories, fibre and sodium stay visible so one number does not make the whole decision.</p></div><div class="pick-grid">{pick_cards(ranked_protein, "Protein")}</div></div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Lower calorie, still substantial</p>
<h2>Lighter entrées and meals</h2><p>Tiny sides and low-calorie add-ons are excluded from this list. These are the lightest tracked options that still function as an entrée or meaningful meal component.</p></div>
<div class="pick-grid">{pick_cards(lighter, "Lighter")}</div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><p class="eyebrow">Higher energy</p>
<h2>Options for larger appetites and bulking</h2><p>Higher-calorie is not a warning label. These options can fit higher energy needs while keeping protein visible.</p></div>
<div class="pick-grid">{pick_cards(energy, "Higher energy")}</div></div></section>
{veg}
<section><div class="container advice-grid"><article class="advice-card"><h2>How to order at {html.escape(chain)}</h2><ul>{advice}</ul></article>
<article class="advice-card"><h2>Match the order to your goal</h2><ul>
<li><strong>Cutting:</strong> start with the lighter substantial list, then choose a portion that keeps you satisfied.</li>
<li><strong>Bulking:</strong> use the higher-energy list and favour options with meaningful protein.</li>
<li><strong>High protein:</strong> compare grams of protein and protein per 100 calories; neither replaces total meal context.</li>
<li><strong>Higher fibre:</strong> favour beans, vegetables, whole grains or other items where fibre is actually published.</li>
</ul></article></div></section>
<section><div class="container"><div class="source-box"><h2>Official source and data freshness</h2>
<p><strong>Nutrition data checked: August 2026.</strong> Values reflect tracked standard U.S. menu builds and can change with recipes, portions, locations and customization.</p>
<p><a href="{html.escape(cfg["source"], quote=True)}">Open the official {html.escape(cfg["source_label"])}</a>. Confirm current nutrition and allergen information with {html.escape(chain)} when accuracy is important.</p>
<p>GetMacros is independent and is not sponsored or endorsed by {html.escape(chain)}.</p></div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><h2>Compare another restaurant</h2>
<p>Use the finder to rank all {len(parse_meals())} tracked options, or return to the chain directory.</p></div><div class="focus-actions">
<a class="btn btn-primary" href="restaurant-meal-finder.html">Use the meal finder</a><a class="btn" href="healthy-fast-food.html">Browse all restaurants</a></div></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}
<script src="js/lang.js?v=20260823a"></script></body></html>'''
    return path, body, title, h1


def main() -> int:
    meals = parse_meals()
    by_chain: dict[str, list[dict]] = {}
    for meal in meals:
        by_chain.setdefault(meal["chain"], []).append(meal)
    missing = set(by_chain) - set(CHAIN_CONFIG)
    if missing:
        raise SystemExit(f"Missing chain configuration: {sorted(missing)}")
    for chain, chain_meals in by_chain.items():
        path, body, _, _ = build_page(chain, chain_meals)
        (ROOT / path).write_text(body, encoding="utf-8")
        print(f"wrote {path}: {len(chain_meals)} items")
    print(f"restaurant guides: {len(meals)} options across {len(by_chain)} chains")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
