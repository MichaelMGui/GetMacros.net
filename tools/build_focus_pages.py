#!/usr/bin/env python3
"""Build the focused homepage and primary product hubs."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from build_restaurant_pages import CHAIN_CONFIG, efficiency, item_type, parse_meals
from focus_components import SITE, breadcrumbs, footer, head, nav
from site_scope import GUIDE_GROUPS, RESTAURANT_PAGES, TOOL_PAGES

ROOT = Path(__file__).resolve().parents[1]


def page_meta(path: str) -> tuple[str, str, str]:
    text = (ROOT / path).read_text(encoding="utf-8")
    title = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
        (re.search(r"<title>(.*?)</title>", text, re.I | re.S) or ["", path])[1]))).strip()
    h1 = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ",
        (re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S) or ["", title])[1]))).strip()
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.I | re.S)
    desc = html.unescape(desc_match.group(1)).strip() if desc_match else ""
    return title, h1, desc


def meal_count_by_chain(meals: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meal in meals:
        counts[meal["chain"]] = counts.get(meal["chain"], 0) + 1
    return counts


def chain_cards(meals: list[dict]) -> str:
    counts = meal_count_by_chain(meals)
    links = []
    for chain in sorted(counts):
        path = next(m["url"] for m in meals if m["chain"] == chain)
        links.append(f'<a class="chain-card" href="{path}"><span>{html.escape(chain)}</span><b>{counts[chain]} options &rarr;</b></a>')
    return "".join(links)


def rank_list(meals: list[dict], metric: str, *, reverse=True, limit=4,
              where=lambda m: True, unit="") -> str:
    pool = [m for m in meals if m.get(metric) is not None and where(m)]
    pool.sort(key=lambda m: m[metric], reverse=reverse)
    rows = []
    for m in pool[:limit]:
        rows.append(f'<li><strong>{html.escape(m["name"])}<br><small>{html.escape(m["chain"])}</small></strong>'
                    f'<span>{m[metric]:g}{unit}</span></li>')
    return "".join(rows)


def substantial_meal(meal: dict) -> bool:
    """A meaningful entrée for rankings, not merely a technically listed item."""
    return (
        item_type(meal) not in {"Side", "Side / snack"}
        and (meal.get("cal") or 0) >= 250
        and (meal.get("p") or 0) >= 15
    )


def build_home(meals: list[dict]) -> None:
    count, chains = len(meals), len({m["chain"] for m in meals})
    example = max((m for m in meals if m.get("p") is not None and item_type(m) != "Side"),
                  key=lambda m: m["p"])
    title = "Healthy Fast Food Finder & Macro Calculator | GetMacros"
    meta = (f"Find healthy fast-food options across {chains} chains by calories, protein, fiber and sodium, "
            "then calculate daily macro targets with transparent tools.")
    schema = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "GetMacros.net",
         "url": f"{SITE}/", "description": meta,
         "potentialAction": {"@type": "SearchAction", "target": f"{SITE}/search.html?q={{search_term_string}}",
                             "query-input": "required name=search_term_string"}},
        {"@context": "https://schema.org", "@type": "Organization", "name": "GetMacros.net",
         "url": f"{SITE}/", "email": "getmacros.net@outlook.com",
         "publishingPrinciples": f"{SITE}/editorial-policy.html"},
    ]
    goals = [
        ("↗", "High protein", "Prioritize protein while keeping calories and sodium visible."),
        ("↓", "Lower calorie", "Find substantial entrées—not tiny sides presented as meals."),
        ("◎", "Cutting", "Balance a lower energy target with useful protein and satisfaction."),
        ("＋", "Bulking", "Compare higher-energy meals that still provide meaningful protein."),
        ("◇", "Higher fiber", "Find bowls, beans, grains and vegetables where fiber is published."),
        ("○", "Lower sodium", "Compare only published sodium values; missing never means zero."),
        ("♧", "Vegetarian", "Filter standard builds without meat or fish."),
    ]
    goal_html = "".join(
        f'<a class="goal-card" href="restaurant-meal-finder.html"><span aria-hidden="true">{icon}</span><h3>{label}</h3><p>{desc}</p></a>'
        for icon, label, desc in goals
    )
    tools = [
        ("calculators.html", "Free Macro Calculator", "Estimate calories, protein, carbohydrates and fat—then find meals that fit."),
        ("recipe-macro-scaler.html", "Recipe Calories and Macros Calculator", "Scale portions and recalculate macros per serving."),
        ("nutrition-label-comparison-tool.html", "Compare nutrition labels", "Put two foods on equal footing by serving and calories."),
        ("protein-value-calculator.html", "Protein Cost per Gram Calculator", "Compare the price of one gram of protein in two foods."),
        ("budget-meal-builder.html", "Budget meal builder", "Build a practical meal around food and cost constraints."),
        ("sodium-label-comparison-tool.html", "Sodium per Portion Calculator", "Compare sodium using the portion you actually eat."),
        ("carbohydrate-label-portion-tool.html", "Carbs per Portion Calculator", "Convert label carbohydrates to your real portion."),
        ("weight-goal-timeline-calculator.html", "Weight Goal Timeline Calculator", "Estimate a realistic range from a daily calorie change."),
        ("sweat-rate-calculator.html", "Sweat Rate Calculator", "Estimate observed fluid loss from a training session."),
    ]
    tool_html = "".join(f'<a class="tool-card" href="{p}"><span aria-hidden="true">{i+1:02d}</span><h3>{h}</h3><p>{d}</p></a>' for i, (p,h,d) in enumerate(tools))
    guides = [
        ("how-much-protein-per-day.html", "How much protein do I need?", "Understand the range before using a calculator."),
        ("high-protein-foods-list.html", "High-protein foods", "Compare practical animal and plant options."),
        ("cutting-bulking-maintenance-explained.html", "Cutting, bulking and maintenance", "Choose the phase that matches your goal."),
        ("how-to-read-a-nutrition-label.html", "Read a nutrition label", "Find the numbers that change a real food decision."),
        ("how-to-calculate-recipe-nutrition.html", "Calculate recipe nutrition", "Turn ingredient totals into useful per-serving numbers."),
        ("serving-size-vs-portion-size.html", "Serving size vs. portion size", "Scale label numbers to the amount you actually eat."),
    ]
    guide_html = "".join(f'<a class="guide-card" href="{p}"><h3>{h}</h3><p>{d}</p></a>' for p,h,d in guides)
    body = f'''{head("index.html", title, meta, schema=schema, extra='<link rel="stylesheet" href="css/modern.css?v=20260823a">')}
<body class="site-v3 modern-site recovery-page">{nav()}
<main id="main-content"><section class="focus-hero"><div class="container hero-grid"><div>
<p class="eyebrow">Fast-food nutrition for real goals</p><h1>Healthy fast food that fits your macros</h1>
<p>Compare complete restaurant orders by calories, protein, fiber and sodium. Find a meal for cutting, bulking or everyday eating—then use focused tools to understand the numbers.</p>
<div class="focus-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Find a fast-food meal</a><a class="btn btn-outline" href="calculators.html">Free Macro Calculator</a></div>
<div class="proof-strip"><span><strong>{count}</strong> tracked menu options</span><span><strong>{chains}</strong> restaurant chains</span><span><strong>Official</strong> chain nutrition sources</span></div></div>
<aside class="sample-card"><div class="sample-card-top"><span class="sample-label">A real tracked example</span><span class="sample-source">Official menu data</span></div><h2>{html.escape(example["name"])}</h2><p>{html.escape(example["chain"])} &middot; {html.escape(example["why"])}</p>
<div class="sample-visual"><div class="macro-ring" style="--protein-share:{round(example['p'] * 4 / example['cal'] * 100)}" aria-label="{round(example['p'] * 4 / example['cal'] * 100)} percent of calories come from protein"><strong>{round(example['p'] * 4 / example['cal'] * 100)}%</strong><span>from protein</span></div><div class="sample-macros"><span><b>{example["cal"]:g}</b>calories</span><span><b>{example["p"]:g} g</b>protein</span><span><b>{"—" if example.get("f") is None else f'{example["f"]:g} g'}</b>fiber</span></div></div></aside>
</div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Start with your goal</p><h2>Find an order for the job it needs to do</h2><p>No food is universally best. Combine goals in the finder and see the complete nutrition before choosing.</p></div><div class="goal-grid bento-grid">{goal_html}</div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><p class="eyebrow">Across every chain</p><h2>What the menu data shows</h2><p>Static comparisons give the page value before any interaction. These rankings are calculated from the same central records used by the finder.</p></div>
<div class="ranking-grid"><article class="ranking-card"><h3>Highest protein</h3><ol class="ranking-list">{rank_list(meals,"p",unit=" g")}</ol></article>
<article class="ranking-card"><h3>Lower-calorie substantial options</h3><ol class="ranking-list">{rank_list(meals,"cal",reverse=False,unit=" cal",where=substantial_meal)}</ol></article>
<article class="ranking-card"><h3>Highest fiber</h3><ol class="ranking-list">{rank_list(meals,"f",unit=" g")}</ol></article>
<article class="ranking-card"><h3>Lower-sodium meals and entrées</h3><ol class="ranking-list">{rank_list(meals,"na",reverse=False,unit=" mg",where=substantial_meal)}</ol></article></div>
<div class="focus-actions"><a class="btn btn-primary" href="healthy-fast-food.html">Explore healthy fast food</a><a class="btn" href="restaurant-meal-finder.html">Rank meals for my goals</a></div></div></section>
<section class="restaurant-rail-section"><div class="container"><div class="section-head rail-heading"><div><p class="eyebrow">15 restaurant guides</p><h2>Choose a chain</h2></div><p>Each guide exposes every worthwhile option we track, a full comparison table, derived protein efficiency, and chain-specific ordering advice.</p></div><div class="chain-grid chain-rail" aria-label="Restaurant nutrition guides">{chain_cards(meals)}</div></div></section>
<section class="compact-calc"><div class="container home-calculator"><div class="calculator-copy"><p class="eyebrow">Your daily targets</p><h2>Free macro calculator for meals you actually eat</h2><p>Estimate calories, protein, fat and carbohydrates using the Mifflin–St Jeor equation—then take those targets to Healthy Order Match and compare real restaurant orders.</p><ul><li>Feet/inches and metric controls on the full calculator</li><li>BMR and estimated TDEE context</li><li>One clear path from a daily target to a real meal</li></ul><a class="text-link light-link" href="calculators.html">Open the free macro calculator &rarr;</a></div>
<form id="home-macro-form" class="home-calc-form"><div class="compact-fields"><div><label for="hc-age">Age</label><input id="hc-age" name="age" type="number" min="18" max="100" value="30" required></div><div><label for="hc-sex">Equation sex</label><select id="hc-sex" name="sex"><option value="female">Female</option><option value="male">Male</option></select></div><div><label for="hc-weight">Weight (lb)</label><input id="hc-weight" name="weight" type="number" min="66" max="660" value="170" required></div><div><label for="hc-height">Height (in)</label><input id="hc-height" name="height" type="number" min="48" max="90" value="69" required></div><div class="span-two"><label for="hc-activity">Activity</label><select id="hc-activity" name="activity"><option value="1.2">Mostly sitting</option><option value="1.375">Light activity</option><option value="1.55" selected>Moderate activity</option><option value="1.725">High activity</option><option value="1.9">Very high activity</option></select></div><div class="span-two"><label for="hc-goal">Goal</label><select id="hc-goal" name="goal"><option value="lose">Gradual fat loss</option><option value="maintain" selected>Maintain weight</option><option value="gain">Build muscle</option></select></div></div><button class="button light calc-submit" type="submit">Get my free macro estimate</button><p id="hc-error" class="calc-error" hidden></p><div id="hc-results" class="home-calc-results" hidden aria-live="polite"><div class="result-head"><span>Estimated daily target</span><strong id="hc-calories">—</strong><small>calories</small></div><div class="result-macros"><span><b id="hc-protein">—</b>protein</span><span><b id="hc-carbs">—</b>carbs</span><span><b id="hc-fat">—</b>fat</span></div><p id="hc-context"></p><a class="text-link result-meal-link" href="restaurant-meal-finder.html">Now find a restaurant meal for these targets &rarr;</a></div><p class="calc-fineprint">For educational use by generally healthy adults. Estimates may not fit pregnancy, growth, illness or eating-disorder recovery.</p></form></div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Focused tools</p><h2>Useful nutrition math, without the clutter</h2><p>The main tool library now contains only calculators and comparison tools that support real food and macro decisions.</p></div><div class="tool-grid bento-tools">{tool_html}</div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><p class="eyebrow">Focused education</p><h2>Understand the numbers you use</h2><p>Curated guides support the tools and food decisions. Medical-condition libraries, academic physiology pages and generic trend content are no longer part of the indexed product.</p></div><div class="guide-grid">{guide_html}</div></div></section>
<section class="story-section"><div class="container method-band story-band"><div class="story-copy"><p class="eyebrow">How GetMacros works</p><h2>Transparent data, not a mystery score</h2><p>Restaurant values come from official chain sources and remain tied to standard menu builds. Missing nutrients stay missing instead of becoming zero.</p></div><div class="story-points"><span class="story-index">01 / 03</span><h3>What you can verify</h3><ul><li>Source link and checked date on every chain guide</li><li>Visible ranking thresholds and derived-metric formulas</li><li>Editorial policy, corrections route and limitations</li></ul><a class="btn btn-outline" href="editorial-policy.html">Read the editorial policy</a></div></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}
<script src="js/macro-math.js?v=20260826a"></script><script src="js/home-calculator.js?v=20260826a"></script></body></html>'''
    body = body.replace(
        '<option value="female">Female</option><option value="male">Male</option>',
        '<option value="male">Male</option><option value="female">Female</option>',
        1,
    )
    body = body.replace(
        '<option value="lose">Gradual fat loss</option><option value="maintain" selected>Maintain weight</option><option value="gain">Build muscle</option>',
        '<option value="lose">Lose weight</option><option value="recomp">Lose fat + build muscle</option><option value="maintain" selected>Maintain weight</option><option value="gain">Gain weight + build muscle</option>',
        1,
    )
    (ROOT / "index.html").write_text(body, encoding="utf-8")


def build_fast_food(meals: list[dict]) -> None:
    count, chains = len(meals), len({m["chain"] for m in meals})
    title = "Healthy Fast Food: Best High-Protein Orders | GetMacros"
    meta = (f"Compare {count} fast-food options across {chains} chains by calories, protein, fiber and sodium. "
            "Find meals for cutting, bulking, high protein and vegetarian goals.")
    visible = sorted([m for m in meals if m.get("p") is not None], key=lambda m:m["p"], reverse=True)[:10]
    schema = [
        {"@context":"https://schema.org","@type":"CollectionPage","name":"Healthy fast food options",
         "url":f"{SITE}/healthy-fast-food.html","description":meta,"dateModified":"2026-08-28"},
        {"@context":"https://schema.org","@type":"ItemList","name":"High-protein fast-food options",
         "numberOfItems":len(visible),"itemListElement":[{"@type":"ListItem","position":i,"name":m["name"],"url":f'{SITE}/{m["url"]}'} for i,m in enumerate(visible,1)]},
    ]
    goal_links = "".join(f'<a class="goal-card" href="restaurant-meal-finder.html"><h3>{label}</h3><p>{desc}</p></a>' for label,desc in [
        ("High protein","Prioritizes 25 g or more while showing calories and sodium."),
        ("Cutting","Highlights substantial lower-calorie options with useful protein."),
        ("Bulking","Surfaces higher-energy meals that still provide meaningful protein."),
        ("Higher fiber","Finds meals publishing at least 5 g fiber."),
        ("Lower sodium","Uses published sodium only; missing data never qualifies."),
        ("Vegetarian / plant based","Filters standard builds and keeps cross-contact caveats visible."),
    ])
    body = f'''{head("healthy-fast-food.html",title,meta,schema=schema)}<body class="site-v3 recovery-page">{nav("fastfood")}
<main id="main-content">{breadcrumbs([("Home","index.html"),("Healthy Fast Food",None)])}
<section class="focus-page-hero"><div class="container"><p class="eyebrow">The GetMacros restaurant database</p><h1>Healthy fast food for cutting, bulking and high protein</h1>
<p>Compare complete tracked orders—not just low-calorie sides—across {chains} chains. Use the static rankings below or combine several preferences in Healthy Order Match.</p>
<div class="stat-row"><span>{count} tracked menu options</span><span>{chains} restaurant chains</span><span>Official sources checked August 2026</span></div>
<div class="focus-actions"><a class="btn btn-primary" href="restaurant-meal-finder.html">Find my best meal</a><a class="btn btn-outline" href="#rankings">See the comparisons</a></div></div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Combine goals</p><h2>What matters for this order?</h2><p>High protein and bulking can coexist. So can vegetarian and lower calorie. The finder ranks compatible records without pretending one meal is best for everyone.</p></div><div class="goal-grid">{goal_links}</div></div></section>
<section id="rankings" class="data-section"><div class="container"><div class="section-head"><p class="eyebrow">Cross-chain comparisons</p><h2>Healthy fast-food options by the metric you care about</h2><p>Every number below comes from the central dataset. Small sides are excluded from the substantial lower-calorie list.</p></div><div class="ranking-grid">
<article class="ranking-card"><h3>Highest-protein fast food</h3><ol class="ranking-list">{rank_list(meals,"p",limit=8,unit=" g")}</ol></article>
<article class="ranking-card"><h3>Lower-calorie meals and entrées</h3><ol class="ranking-list">{rank_list(meals,"cal",reverse=False,limit=8,unit=" cal",where=substantial_meal)}</ol></article>
<article class="ranking-card"><h3>Higher-energy meals for bulking</h3><ol class="ranking-list">{rank_list(meals,"cal",limit=8,unit=" cal",where=lambda m:item_type(m) not in {"Side","Side / snack"} and (m.get("p") or 0)>=20)}</ol></article>
<article class="ranking-card"><h3>Highest-fiber options</h3><ol class="ranking-list">{rank_list(meals,"f",limit=8,unit=" g")}</ol></article>
<article class="ranking-card"><h3>Lower-sodium meals and entrées</h3><p class="ranking-note">Only substantial tracked items with published sodium qualify. Missing sodium is never treated as zero.</p><ol class="ranking-list">{rank_list(meals,"na",reverse=False,limit=8,unit=" mg",where=substantial_meal)}</ol></article>
<article class="ranking-card"><h3>Higher-protein vegetarian options</h3><ol class="ranking-list">{rank_list(meals,"p",limit=8,unit=" g",where=lambda m:"vegetarian" in m.get("diet",[]))}</ol></article>
<article class="ranking-card"><h3>Plant-based menu options</h3><ol class="ranking-list">{rank_list(meals,"p",limit=8,unit=" g",where=lambda m:"plant" in m.get("diet",[]))}</ol></article>
<article class="ranking-card"><h3>High-protein fast-food breakfasts</h3><ol class="ranking-list">{rank_list(meals,"p",limit=8,unit=" g",where=lambda m:m.get("meal")=="breakfast")}</ol></article></div></div></section>
<section><div class="container"><div class="section-head"><p class="eyebrow">Restaurant directory</p><h2>Healthy options by restaurant</h2><p>Every chain page now exposes all tracked options, protein-per-calorie, goal-based picks, unique ordering advice, an official source and a real checked date.</p></div><div class="chain-grid">{chain_cards(meals)}</div></div></section>
<section class="data-section"><div class="container method-band"><div><p class="eyebrow">Methodology</p><h2>What “healthy” means here</h2><p>It means useful information for a specific goal—not a universal label. Rankings keep calories, protein, fiber and sodium visible together.</p></div><div><h3>Important limits</h3><ul><li>Standard U.S. menu builds, not every customization</li><li>Entrées, sides and snacks are classified separately</li><li>Missing values remain blank, never zero</li><li>Diet tags do not imply allergy safety</li><li>Menus and recipes change; confirm the official source</li></ul><a class="btn btn-outline" href="sources.html">Read the data method</a></div></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}</body></html>'''
    (ROOT/"healthy-fast-food.html").write_text(body,encoding="utf-8")


def build_restaurant_directory(meals: list[dict]) -> None:
    title="Healthy Fast-Food Restaurants & Menu Guides | GetMacros"
    meta=f"Browse nutrition guides for {len({m['chain'] for m in meals})} fast-food and fast-casual chains, with calories, protein, fiber, sodium and official source links."
    body=f'''{head("restaurant-meal-guides.html",title,meta)}<body class="site-v3 recovery-page">{nav("fastfood")}<main id="main-content">
{breadcrumbs([("Home","index.html"),("Healthy Fast Food","healthy-fast-food.html"),("Restaurant Guides",None)])}
<section class="focus-page-hero"><div class="container"><p class="eyebrow">Chain-by-chain nutrition</p><h1>Healthy fast-food restaurant guides</h1><p>Choose a chain to compare every menu option in the GetMacros dataset and see goal-based picks, protein efficiency, official sources and checked dates.</p></div></section>
<section><div class="container"><div class="chain-grid">{chain_cards(meals)}</div></div></section>
<section class="data-section"><div class="container"><div class="section-head"><h2>Prefer one ranked list?</h2><p>Healthy Order Match compares all chains at once and can combine cutting, bulking, high-protein and dietary preferences.</p></div><a class="btn btn-primary" href="restaurant-meal-finder.html">Use Healthy Order Match</a></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}</body></html>'''
    (ROOT/"restaurant-meal-guides.html").write_text(body,encoding="utf-8")


def build_articles() -> None:
    cards=[]
    visible_count=0
    for group, paths in GUIDE_GROUPS.items():
        group_cards=[]
        for path in paths:
            if not (ROOT/path).exists():
                continue
            _,h1,desc=page_meta(path)
            group_cards.append(f'<a class="guide-card" href="{path}"><h3>{html.escape(h1)}</h3><p>{html.escape(desc)}</p></a>')
            visible_count+=1
        if group_cards:
            cards.append(f'<section class="guide-group"><div class="container"><div class="section-head"><h2>{html.escape(group)}</h2></div><div class="guide-grid">{"".join(group_cards)}</div></div></section>')
    title="Nutrition Guides for Macros, Meals & Eating Out | GetMacros"
    meta="Browse focused GetMacros guides about protein, carbs, fat, macro goals, meal building, food labels, eating out and practical sports nutrition."
    schema={"@context":"https://schema.org","@type":"CollectionPage","name":"GetMacros Nutrition Guides","url":f"{SITE}/articles.html","description":meta,"numberOfItems":visible_count}
    body=f'''{head("articles.html",title,meta,schema=schema)}<body class="site-v3 recovery-page">{nav("guides")}<main id="main-content">
{breadcrumbs([("Home","index.html"),("Nutrition Guides",None)])}<section class="guide-hub-hero"><div class="container"><p class="eyebrow">Focused, practical education</p><h1>Nutrition guides for the numbers you use</h1><p>Learn how protein, carbs, fat, portions and food labels connect to macro goals and real restaurant decisions. The library is curated around the GetMacros product—not every possible health topic.</p></div><figure class="editorial-figure"><img src="images/editorial-recipe-portions.webp" width="1536" height="1024" alt="Grilled chicken and vegetables divided into practical meal-prep portions" loading="lazy"><figcaption>Good nutrition guidance should lead to food decisions you can actually repeat.</figcaption></figure></section>{''.join(cards)}
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}</body></html>'''
    (ROOT/"articles.html").write_text(body,encoding="utf-8")


def build_about(meals: list[dict]) -> None:
    title="About GetMacros: Data, Tools & Editorial Standards"
    meta="Learn who GetMacros is for, how restaurant nutrition data and macro tools are built, how sources are checked, and how to report corrections."
    schema=[
        {"@context":"https://schema.org","@type":"AboutPage","name":"About GetMacros",
         "url":f"{SITE}/about.html","description":meta},
        {"@context":"https://schema.org","@type":"Organization","name":"GetMacros.net",
         "url":f"{SITE}/","email":"getmacros.net@outlook.com",
         "publishingPrinciples":f"{SITE}/editorial-policy.html"},
    ]
    body=f'''{head("about.html",title,meta,schema=schema)}<body class="site-v3 recovery-page">{nav("about")}<main id="main-content">
{breadcrumbs([("Home","index.html"),("About",None)])}<section class="focus-page-hero"><div class="container"><p class="eyebrow">About GetMacros</p><h1>Practical nutrition tools for real food decisions</h1><p>GetMacros helps people compare fast-food meals by calories, protein and other published nutrients, calculate macro targets, and understand the numbers without moralizing food.</p></div></section>
<section><div class="container content-list"><h2>What GetMacros publishes</h2><p>The focused product contains {len(meals)} tracked menu options across {len({m['chain'] for m in meals})} chains, Healthy Order Match, macro and food calculators, and a curated library of supporting guides.</p><p>GetMacros is independent. Restaurant names and menu information belong to their respective owners; no chain sponsors or endorses these guides.</p>
<h2>How restaurant data is handled</h2><ul><li>Values are tied to official restaurant nutrition sources.</li><li>Each chain guide shows its source and the real month the data was checked.</li><li>Missing values remain missing instead of being converted to zero.</li><li>Derived metrics show their formula and are not presented as health scores.</li><li>Menus change, so users are directed to confirm current official information.</li></ul>
<h2>Editorial responsibility</h2><p>Content is published by the GetMacros.net editorial team. The site does not invent doctor or dietitian bylines, and it does not claim that educational tools are individualized medical advice. The <a href="editorial-policy.html">editorial policy</a> explains sourcing, scope and updates.</p>
<h2>Corrections and contact</h2><p>If a menu value, calculation, source or explanation looks wrong, use the <a href="corrections.html">corrections process</a> or email <a href="mailto:getmacros.net@outlook.com">getmacros.net@outlook.com</a>. Include the page URL and the official source when possible.</p></div></section>
<div class="ad-auto-anchor" aria-hidden="true"></div></main>{footer()}</body></html>'''
    (ROOT/"about.html").write_text(body,encoding="utf-8")


def patch_existing_hubs() -> None:
    calc=ROOT/"calculators.html"
    if calc.exists():
        s=calc.read_text(encoding="utf-8")
        s=re.sub(r"<title>.*?</title>","<title>Free Macro Calculator &amp; Nutrition Tools | GetMacros</title>",s,count=1,flags=re.S)
        meta="Use the free macro calculator to estimate daily calories, protein, carbs and fat, then find restaurant meals that fit your goal."
        s=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{meta}">',s,count=1)
        s=re.sub(r'<meta property="og:title" content="[^"]*">','<meta property="og:title" content="Free Macro Calculator &amp; Nutrition Tools | GetMacros">',s,count=1)
        s=re.sub(r'<meta property="og:description" content="[^"]*">',f'<meta property="og:description" content="{meta}">',s,count=1)
        s=re.sub(r'<meta name="twitter:title" content="[^"]*">','<meta name="twitter:title" content="Free Macro Calculator &amp; Nutrition Tools | GetMacros">',s,count=1)
        s=re.sub(r'<meta name="twitter:description" content="[^"]*">',f'<meta name="twitter:description" content="{meta}">',s,count=1)
        s=re.sub(r'"name": "Macro Calculator"','"name": "Free Macro Calculator"',s,count=1)
        s=re.sub(r'<section class="calc-hub-hero">.*?</section>','''<section class="calc-hub-hero"><div class="container calc-hero-grid"><div><p class="eyebrow">Free, transparent and built for real meals</p><h1>Free macro calculator for meals you actually eat</h1><p>Estimate daily calories, protein, carbs and fat, understand the assumptions, then use Healthy Order Match to compare restaurant orders for cutting, maintenance or bulking.</p><div class="calc-hero-actions"><a class="btn btn-primary" href="#macro-calculator">Start free calculation</a><a class="btn btn-ghost" href="restaurant-meal-finder.html">Find a meal for my goal</a></div></div><figure class="calc-photo-card"><img src="images/editorial-protein-foods.webp" width="1536" height="1024" alt="Salmon, tofu, eggs, yogurt, chickpeas and grains arranged beside a food scale" fetchpriority="high"><figcaption>Start with an estimate. Finish with a meal decision you can actually use.</figcaption></figure></div></section>''',s,count=1,flags=re.S)
        s=s.replace("This page now keeps only tools that calculate, compare or transform nutrition numbers. General worksheets and appointment organizers have been removed from this hub.","This focused library keeps only tools that calculate, compare or transform nutrition numbers for macros, food labels, recipes, budgets, hydration and restaurant choices.")
        s=re.sub(r'<meta name="theme-color" content="[^"]+">',
                 '<meta name="theme-color" content="#123f2d">', s, count=1)
        s=s.replace('<meta property="og:locale" content="en_US">\n', '')
        s=re.sub(r'<meta property="og:image:alt" content="[^"]*">',
                 '<meta property="og:image:alt" content="GetMacros.net practical nutrition tools">', s, count=1)
        s=re.sub(
            r'<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container">.*?</div></nav>',
            breadcrumbs([("Home", "index.html"), ("Macro Calculator", None)]),
            s, count=1, flags=re.S,
        )
        calculator_breadcrumb = {
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Macro Calculator", "item": f"{SITE}/calculators.html"},
            ],
        }
        s=re.sub(
            r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "BreadcrumbList".*?</script>',
            f'<script type="application/ld+json">{json.dumps(calculator_breadcrumb)}</script>',
            s, count=1, flags=re.S,
        )
        if "calculators-polish.css" not in s:
            s=re.sub(r'(<link\s+rel="stylesheet"\s+href="css/calculator-height-v2\.css[^>]*>)',
                     r'\1<link rel="stylesheet" href="css/calculators-polish.css?v=20260823b">', s, count=1)
        if "js/macro-math.js" not in s:
            s=s.replace('<script src="js/calculators.js', '<script src="js/macro-math.js?v=20260826a"></script>\n<script src="js/calculators.js', 1)
        focused_library='''<section class="tool-library" id="tool-library"><div class="container"><div class="tool-library-head"><p class="eyebrow">Focused calculator library</p><h2>Nine tools for real nutrition decisions</h2><p>Choose the calculator that matches the number you need.</p></div><div class="tool-groups">
<article class="tool-group" id="food-tools"><div class="tool-group-head"><span class="tool-group-icon" aria-hidden="true">01</span><div><h3>Food, recipe and label math</h3><p>Scale a recipe or compare the foods you are actually choosing.</p></div></div><div class="tool-links"><a href="recipe-macro-scaler.html">Recipe Calories and Macros Calculator <span>→</span></a><a href="nutrition-label-comparison-tool.html">Compare Nutrition Labels Side by Side <span>→</span></a><a href="protein-value-calculator.html">Protein Cost per Gram Calculator <span>→</span></a><a href="budget-meal-builder.html">Budget Meal Builder <span>→</span></a><a href="sodium-label-comparison-tool.html">Sodium per Portion Calculator <span>→</span></a><a href="carbohydrate-label-portion-tool.html">Carbs per Portion Calculator <span>→</span></a></div></article>
<article class="tool-group" id="goal-tools"><div class="tool-group-head"><span class="tool-group-icon" aria-hidden="true">02</span><div><h3>Goals, training and eating out</h3><p>Estimate a timeline, measure observed sweat loss or compare restaurant meals.</p></div></div><div class="tool-links"><a href="weight-goal-timeline-calculator.html">Weight Goal Timeline Calculator <span>→</span></a><a href="sweat-rate-calculator.html">Sweat Rate Calculator <span>→</span></a><a href="restaurant-meal-finder.html">Healthy Order Match <span>→</span></a></div></article>
</div></div></section><div class="ad-auto-anchor" aria-hidden="true"></div>'''
        s=re.sub(r'<section class="tool-library".*?</section><div class="ad-auto-anchor"[^>]*></div>(?:<section class="related-explore".*?</section>)?', focused_library, s, count=1, flags=re.S)
        calc.write_text(s,encoding="utf-8")
    finder=ROOT/"restaurant-meal-finder.html"
    if finder.exists():
        s=finder.read_text(encoding="utf-8")
        s=re.sub(r"<title>.*?</title>","<title>Healthy Fast-Food Quiz: Healthy Order Match | GetMacros</title>",s,count=1,flags=re.S)
        s=re.sub(r"<h1[^>]*>.*?</h1>","<h1>Healthy Order Match</h1>",s,count=1,flags=re.S)
        finder.write_text(s,encoding="utf-8")


def main() -> int:
    meals=parse_meals()
    if len(meals)!=83 or len({m["chain"] for m in meals})!=15:
        raise SystemExit("Unexpected restaurant dataset size; refusing to publish hard-coded claims")
    build_home(meals)
    build_fast_food(meals)
    build_restaurant_directory(meals)
    build_articles()
    build_about(meals)
    patch_existing_hubs()
    print("built focused homepage, hubs and trust page")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
