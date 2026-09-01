#!/usr/bin/env python3
"""Build substantial chain guides from the verified central meal dataset."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from focus_components import ASSET_VERSION, SITE, breadcrumbs, footer, head, nav

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "js" / "meal-data.js"

CHAIN_CONFIG = {
    "Chipotle": {
        "title": "Healthy Chipotle Orders: Calories & Protein | GetMacros",
        "h1": "Healthy Chipotle orders by calories and protein",
        "intro": "Chipotle is unusually flexible: protein, rice, beans, vegetables and toppings can be adjusted independently. Compare the complete builds we track, then use the official calculator for your exact custom bowl.",
        "source": "https://www.chipotle.com/nutrition-calculator",
        "source_label": "Chipotle nutrition calculator",
        "data_note": "Every tracked Chipotle build names each included ingredient. For the two current High Protein Menu items, Chipotle publishes the complete build, calories, protein and fiber; carbs and sodium are summed from the official ingredient table. The other four builds use the same ingredient-by-ingredient method.",
        "additional_sources": [
            ("https://newsroom.chipotle.com/2025-12-18-CHIPOTLE-UNVEILS-ITS-FIRST-EVER-HIGH-PROTEIN-MENU-FEATURING-A-NEW-SNACK-READY-HIGH-PROTEIN-CUP",
             "Chipotle High Protein Menu announcement"),
            ("https://www.chipotle.com/content/dam/chipotle/menu/nutrition/US-Nutrition-Facts-Paper-Menu-3-2025.pdf",
             "Chipotle U.S. ingredient nutrition table"),
        ],
        "advice": [
            "Choose the protein first; doubling it changes both calories and cost, so check the live builder.",
            "Rice and beans are not interchangeable: beans add fiber and protein, while rice mainly raises carbohydrate and energy.",
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
            "Plant-based bowls can be high in fiber but lower in protein. Add tofu or another listed protein if that is your priority.",
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
        "title": "Healthy Subway Orders: Calories & Protein | GetMacros",
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
            "Beans can add fiber and protein to vegetarian orders; removing meat without replacing it can leave a smaller meal.",
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
    if value is None:
        return "&mdash;"
    shown = f"{value:,.0f}" if float(value).is_integer() and abs(value) >= 1000 else f"{value:g}"
    return f"{shown}{unit}"


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
<th scope="col">Protein</th><th scope="col">Carbs</th><th scope="col">Fiber</th>
<th scope="col">Sodium</th><th scope="col">Protein / 100 cal</th></tr></thead><tbody>''' + "".join(rows) + "</tbody></table></div>"


def pick_cards(meals: list[dict], label: str) -> str:
    out = []
    for i, m in enumerate(meals, 1):
        out.append(f'''<article class="pick-card"><span class="rank">{html.escape(label)} #{i}</span>
<h3>{html.escape(m["name"])}</h3><p>{html.escape(m["why"])}</p><div class="pick-metrics">
<span>{n(m.get("cal"))} calories</span><span>{n(m.get("p"), " g")} protein</span>
<span>{n(m.get("f"), " g")} fiber</span><span>{n(m.get("na"), " mg")} sodium</span></div></article>''')
    return "".join(out)


def chain_finder(chain: str) -> str:
    """A focused matcher for the restaurant guide the visitor is already on."""
    safe_chain = html.escape(chain)
    return f'''<section class="chain-finder-section" id="chain-meal-finder" data-chain-finder data-chain="{html.escape(chain, quote=True)}"><div class="container chain-finder-layout">
<header class="chain-finder-intro"><p class="eyebrow">Quick match &middot; {safe_chain} only</p><h2>Find a meal from {safe_chain}</h2><p>Choose what matters today. We&rsquo;ll compare the complete {safe_chain} orders in this guide and explain the three closest matches.</p><ul><li>Uses this restaurant only</li><li>Shows calories, protein, fiber and sodium together</li><li>No account or email</li></ul></header>
<form class="chain-finder-form" data-chain-form><fieldset><legend>What should this meal help with?</legend><div class="chain-choice-grid chain-goals">
<label><input type="radio" name="chain-goal" value="balanced" checked><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-target"></use></svg><b>Balanced</b><small>Strong all-around fit</small></span></label>
<label><input type="radio" name="chain-goal" value="protein"><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-protein"></use></svg><b>High protein</b><small>Prioritize protein</small></span></label>
<label><input type="radio" name="chain-goal" value="light"><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-leaf"></use></svg><b>Cutting</b><small>Lighter, still substantial</small></span></label>
<label><input type="radio" name="chain-goal" value="energy"><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-flame"></use></svg><b>Bulking</b><small>Higher energy and protein</small></span></label>
<label><input type="radio" name="chain-goal" value="fibre"><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-leaf"></use></svg><b>Higher fiber</b><small>Favor published fiber</small></span></label>
<label><input type="radio" name="chain-goal" value="lowsodium"><span><svg aria-hidden="true"><use href="icon-sprite.svg#icon-water"></use></svg><b>Lower sodium</b><small>Compare substantial meals</small></span></label>
</div></fieldset><div class="chain-compact-fields"><fieldset><legend>Appetite</legend><div class="chain-choice-row"><label><input type="radio" name="chain-size" value="" checked><span>Any</span></label><label><input type="radio" name="chain-size" value="small"><span>Small</span></label><label><input type="radio" name="chain-size" value="medium"><span>Regular</span></label><label><input type="radio" name="chain-size" value="large"><span>Large</span></label></div></fieldset><fieldset><legend>Dietary filter</legend><div class="chain-choice-row"><label><input type="radio" name="chain-diet" value="" checked><span>None</span></label><label><input type="radio" name="chain-diet" value="vegetarian"><span>Vegetarian</span></label><label><input type="radio" name="chain-diet" value="plant"><span>Plant-based</span></label></div></fieldset></div>
<button class="btn btn-primary chain-find-button" type="submit">Find my {safe_chain} meal <span aria-hidden="true">&rarr;</span></button></form>
</div><div class="container chain-finder-results" data-chain-results hidden aria-live="polite"></div><div class="container chain-all-link"><p>Not set on {safe_chain}? <a href="restaurant-meal-finder.html">Find your best meal across all restaurants <span aria-hidden="true">&rarr;</span></a></p></div></section>'''


def build_page(chain: str, meals: list[dict]) -> tuple[str, str, str, str]:
    cfg = CHAIN_CONFIG[chain]
    path = meals[0]["url"]
    title, h1 = cfg["title"], cfg["h1"]
    ranked_protein = sorted([m for m in meals if m.get("p") is not None], key=lambda m: m["p"], reverse=True)[:3]
    substantial = [m for m in meals if item_type(m) not in {"Side", "Side / snack"}
                   and ((m.get("p") or 0) >= 15 or (m.get("cal") or 0) >= 250)]
    lighter = sorted([m for m in substantial if m.get("cal") is not None], key=lambda m: m["cal"])[:3]
    # One templated sentence with the chain name swapped in gave fifteen pages
    # near-identical meta descriptions -- a duplicate-content signal, and a row
    # of interchangeable snippets in the results. Naming this chain's own
    # numbers makes every description distinct and tells a searcher, before
    # they click, whether this page holds the order they are after.
    meta = f"Compare all {len(meals)} tracked {chain} items by calories, protein, fiber and sodium."
    if ranked_protein:
        top = ranked_protein[0]
        clause = f" {top['name']} leads on protein at {top['p']:g} g"
        if lighter:
            clause += f"; the lightest substantial order is {lighter[0]['cal']:g} calories"
        clause += "."
        if len(meta) + len(clause) <= 158:
            meta += clause
        elif len(meta) + len(f" {top['name']} leads on protein at {top['p']:g} g.") <= 158:
            meta += f" {top['name']} leads on protein at {top['p']:g} g."
        elif lighter:
            # Long item names can push the named clause past the length Google
            # renders. Fall back to the numbers alone rather than to a sentence
            # every chain would share.
            meta += (f" Top protein {top['p']:g} g; lightest substantial order "
                     f"{lighter[0]['cal']:g} calories.")
        else:
            meta += f" Top protein {top['p']:g} g."
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
    additional_sources = "".join(
        f'<li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>'
        for url, label in cfg.get("additional_sources", [])
    )
    additional_sources = (
        f'<p>Build-specific source details:</p><ul>{additional_sources}</ul>'
        if additional_sources else ""
    )
    data_note = cfg.get(
        "data_note",
        "These are standard U.S. menu builds from the central GetMacros dataset. Dashes mean the value was not available in a form we could verify—not zero.",
    )
    veg = ""
    if vegetarian:
        veg = f'''<article class="chain-pick-group"><header><span class="chain-pick-icon"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-leaf"></use></svg></span><div><p>Dietary pattern</p><h3>Vegetarian standard builds</h3></div></header><p>Confirm ingredients and cross-contact with the restaurant.</p><div class="pick-grid">{pick_cards(vegetarian[:4], "Vegetarian")}</div></article>'''
    body = f'''{head(path, title, meta, schema=schema)}
<body class="site-v3 article-page restaurant-guide recovery-page">{nav("fastfood")}
<main id="main-content">{breadcrumbs([("Home", "index.html"), ("Healthy Fast Food", "healthy-fast-food.html"), (chain, None)])}
<section class="focus-page-hero"><div class="container"><p class="eyebrow">{html.escape(chain)} nutrition guide</p>
<h1>{html.escape(h1)}</h1><p>{html.escape(cfg["intro"])}</p><div class="stat-row">
<span>{len(meals)} tracked options</span><span>Official source checked August 2026</span><span>No missing value treated as zero</span></div>
<div class="focus-actions"><a class="btn btn-primary" href="#chain-meal-finder">Find a {html.escape(chain)} meal</a>
<a class="btn btn-outline" href="#menu-comparison">Compare the menu</a></div></div></section>
{chain_finder(chain)}
<section class="chain-picks-section data-section"><div class="container"><div class="section-head"><p class="eyebrow">Best starting points</p><h2>{html.escape(chain)} orders by goal</h2><p>These short lists answer different questions. Every card keeps calories, protein, fiber and sodium together.</p></div><div class="chain-pick-groups">
<article class="chain-pick-group"><header><span class="chain-pick-icon"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-protein"></use></svg></span><div><p>High protein</p><h3>Most protein</h3></div></header><p>Ranked by published protein, with the rest of the meal still visible.</p><div class="pick-grid">{pick_cards(ranked_protein, "Protein")}</div></article>
<article class="chain-pick-group"><header><span class="chain-pick-icon"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-leaf"></use></svg></span><div><p>Cutting</p><h3>Lighter, substantial orders</h3></div></header><p>Tiny sides are excluded so these still function as an entrée or meal.</p><div class="pick-grid">{pick_cards(lighter, "Lighter")}</div></article>
<article class="chain-pick-group"><header><span class="chain-pick-icon"><svg aria-hidden="true"><use href="icon-sprite.svg#icon-flame"></use></svg></span><div><p>Bulking</p><h3>Higher-energy orders</h3></div></header><p>Larger options for bigger appetites, with protein kept in view.</p><div class="pick-grid">{pick_cards(energy, "Higher energy")}</div></article>
{veg}
</div></div></section>
<section id="menu-comparison" class="chain-menu-section"><div class="container"><details class="restaurant-menu-details"><summary><span><small>Complete nutrition table</small><strong>Compare every {html.escape(chain)} option we track</strong></span><b>Open table <span aria-hidden="true">+</span></b></summary><div class="restaurant-menu-content"><p>{html.escape(data_note)}</p>
{table(meals)}<p class="metric-note"><strong>Protein per 100 calories</strong> = protein grams ÷ calories × 100. It is a transparent efficiency metric, not a health score.</p></div></details></div></section>
<section><div class="container advice-grid"><article class="advice-card"><h2>How to order at {html.escape(chain)}</h2><ul>{advice}</ul></article>
<article class="advice-card"><h2>Match the order to your goal</h2><ul>
<li><strong>Cutting:</strong> start with the lighter substantial list, then choose a portion that keeps you satisfied.</li>
<li><strong>Bulking:</strong> use the higher-energy list and favour options with meaningful protein.</li>
<li><strong>High protein:</strong> compare grams of protein and protein per 100 calories; neither replaces total meal context.</li>
<li><strong>Higher fiber:</strong> favor beans, vegetables, whole grains or other items where fiber is actually published.</li>
</ul></article></div></section>
<section><div class="container"><div class="source-box"><h2>Official source and data freshness</h2>
<p><strong>Nutrition data checked: August 2026.</strong> Values reflect tracked standard U.S. menu builds and can change with recipes, portions, locations and customization.</p>
<p><a href="{html.escape(cfg["source"], quote=True)}">Open the official {html.escape(cfg["source_label"])}</a>. Confirm current nutrition and allergen information with {html.escape(chain)} when accuracy is important.</p>
{additional_sources}
<p>GetMacros is independent and is not sponsored or endorsed by {html.escape(chain)}.</p></div></div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Read next</p>
<h2>Make the rest of the day fit around it</h2>
<p>A single {html.escape(chain)} order is one decision. These guides cover the ones on either side of it.</p></div>
<div class="guide-grid">
<a class="guide-card" href="how-to-eat-out-without-wrecking-your-goal.html"><h3>How to eat out without wrecking your goal</h3><p>What to decide before you arrive, and which swaps actually change the numbers.</p></a>
<a class="guide-card" href="how-many-calories-should-i-eat-a-day.html"><h3>How many calories should I eat a day?</h3><p>Work out the daily target this meal has to fit inside.</p></a>
<a class="guide-card" href="how-much-sodium-per-day.html"><h3>How much sodium per day?</h3><p>Restaurant meals carry most of it. See what a day&rsquo;s worth looks like.</p></a>
</div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><h2>Compare another restaurant</h2>
<p>Use the finder to rank all {len(parse_meals())} tracked options, or return to the chain directory.</p></div><div class="focus-actions">
<a class="btn btn-primary" href="restaurant-meal-finder.html">Use Healthy Order Match</a><a class="btn" href="healthy-fast-food.html">Browse all restaurants</a></div></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}
<script src="js/lang.js?v=20260823a"></script><script src="js/meal-data.js?v={ASSET_VERSION}" defer></script><script src="js/chain-meal-finder.js?v={ASSET_VERSION}" defer></script></body></html>'''
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
