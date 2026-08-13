#!/usr/bin/env python3
"""Generates the game pages and quiz.html hub for GetMacros.net."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_articles import ROOT, nav_html, FOOTER, ARTICLES, CORE_PAGES, ICON_SPRITE, ADSENSE_LOADER, AD_SLOT, seo_meta, article_jsonld, breadcrumb_jsonld, SITEMAP_LASTMOD, AUTHOR_NAME, ASSET_VERSION  # noqa: E402
from generate_quizzes import QUIZZES  # noqa: E402

MEMORY_PAIRS = [
    {"icon": "icon-protein", "name": "Chicken Breast", "macro": "protein"},
    {"icon": "icon-fat", "name": "Salmon", "macro": "fat"},
    {"icon": "icon-fat", "name": "Avocado", "macro": "fat"},
    {"icon": "icon-carbs", "name": "Brown Rice", "macro": "carbs"},
    {"icon": "icon-protein", "name": "Greek Yogurt", "macro": "protein"},
    {"icon": "icon-carbs", "name": "Banana", "macro": "carbs"},
]

PLATE_FOODS = [
    {"id": "chicken", "icon": "icon-protein", "name": "Chicken Breast (150g)", "protein": 46, "fat": 5, "carb": 0},
    {"id": "salmon", "icon": "icon-fat", "name": "Salmon (150g)", "protein": 37, "fat": 20, "carb": 0},
    {"id": "egg", "icon": "icon-protein", "name": "Egg (1 large)", "protein": 6, "fat": 5, "carb": 0.5},
    {"id": "yogurt", "icon": "icon-protein", "name": "Greek Yogurt (1 cup)", "protein": 17, "fat": 0, "carb": 6},
    {"id": "avocado", "icon": "icon-fat", "name": "Avocado (half)", "protein": 2, "fat": 15, "carb": 9},
    {"id": "oliveoil", "icon": "icon-fat", "name": "Olive Oil (1 tbsp)", "protein": 0, "fat": 14, "carb": 0},
    {"id": "almonds", "icon": "icon-fat", "name": "Almonds (30g)", "protein": 6, "fat": 14, "carb": 6},
    {"id": "rice", "icon": "icon-carbs", "name": "Brown Rice (1 cup)", "protein": 5, "fat": 2, "carb": 45},
    {"id": "oats", "icon": "icon-carbs", "name": "Oats (40g)", "protein": 5, "fat": 3, "carb": 27},
    {"id": "banana", "icon": "icon-carbs", "name": "Banana (1 medium)", "protein": 1, "fat": 0, "carb": 27},
    {"id": "broccoli", "icon": "icon-carbs", "name": "Broccoli (1 cup)", "protein": 3, "fat": 0, "carb": 6},
    {"id": "beans", "icon": "icon-protein", "name": "Black Beans (1 cup)", "protein": 15, "fat": 1, "carb": 41},
    {"id": "pb", "icon": "icon-fat", "name": "Peanut Butter (2 tbsp)", "protein": 7, "fat": 16, "carb": 6},
    {"id": "sweetpotato", "icon": "icon-carbs", "name": "Sweet Potato (1 medium)", "protein": 2, "fat": 0, "carb": 24},
]

PLATE_TARGETS = [
    {"name": "High-Protein Lunch", "desc": "~565 calories, built around lean protein.", "protein": 50, "fat": 20, "carb": 45},
    {"name": "Balanced Dinner", "desc": "~665 calories, an even split across all three.", "protein": 40, "fat": 25, "carb": 60},
    {"name": "Post-Workout Recovery", "desc": "~625 calories, carb-forward for glycogen refill.", "protein": 45, "fat": 15, "carb": 70},
]

SPRINT_FOODS = [
    {"name": "Chicken Breast", "icon": "icon-chicken", "macro": "protein"},
    {"name": "Turkey Breast", "icon": "icon-chicken", "macro": "protein"},
    {"name": "Egg Whites", "icon": "icon-egg", "macro": "protein"},
    {"name": "Greek Yogurt", "icon": "icon-yogurt", "macro": "protein"},
    {"name": "Cottage Cheese", "icon": "icon-yogurt", "macro": "protein"},
    {"name": "Tuna (canned in water)", "icon": "icon-fish", "macro": "protein"},
    {"name": "Whey Protein Powder", "icon": "icon-protein", "macro": "protein"},
    {"name": "Tofu", "icon": "icon-legume", "macro": "protein"},
    {"name": "Avocado", "icon": "icon-avocado", "macro": "fat"},
    {"name": "Olive Oil", "icon": "icon-oil-bottle", "macro": "fat"},
    {"name": "Almonds", "icon": "icon-nut", "macro": "fat"},
    {"name": "Walnuts", "icon": "icon-nut", "macro": "fat"},
    {"name": "Peanut Butter", "icon": "icon-nut", "macro": "fat"},
    {"name": "Butter", "icon": "icon-fat", "macro": "fat"},
    {"name": "Coconut Oil", "icon": "icon-fat", "macro": "fat"},
    {"name": "Brown Rice", "icon": "icon-rice-bowl", "macro": "carbs"},
    {"name": "Oats", "icon": "icon-grain", "macro": "carbs"},
    {"name": "White Bread", "icon": "icon-grain", "macro": "carbs"},
    {"name": "Banana", "icon": "icon-veggie", "macro": "carbs"},
    {"name": "Sweet Potato", "icon": "icon-veggie", "macro": "carbs"},
    {"name": "Quinoa", "icon": "icon-rice-bowl", "macro": "carbs"},
    {"name": "Broccoli", "icon": "icon-veggie", "macro": "carbs"},
]

DIET_FOODS = [
    {"name": "Broccoli", "icon": "icon-veggie", "diet": "vegan"},
    {"name": "Lentils", "icon": "icon-legume", "diet": "vegan"},
    {"name": "Tofu", "icon": "icon-legume", "diet": "vegan"},
    {"name": "Almonds", "icon": "icon-nut", "diet": "vegan"},
    {"name": "Brown Rice", "icon": "icon-rice-bowl", "diet": "vegan"},
    {"name": "Avocado", "icon": "icon-avocado", "diet": "vegan"},
    {"name": "Chickpeas", "icon": "icon-legume", "diet": "vegan"},
    {"name": "Oats", "icon": "icon-grain", "diet": "vegan"},
    {"name": "Apple", "icon": "icon-veggie", "diet": "vegan"},
    {"name": "Peanut Butter", "icon": "icon-nut", "diet": "vegan"},
    {"name": "Eggs", "icon": "icon-egg", "diet": "vegetarian"},
    {"name": "Greek Yogurt", "icon": "icon-yogurt", "diet": "vegetarian"},
    {"name": "Cheese", "icon": "icon-yogurt", "diet": "vegetarian"},
    {"name": "Honey", "icon": "icon-oil-bottle", "diet": "vegetarian"},
    {"name": "Milk", "icon": "icon-yogurt", "diet": "vegetarian"},
    {"name": "Butter", "icon": "icon-fat", "diet": "vegetarian"},
    {"name": "Chicken Breast", "icon": "icon-chicken", "diet": "neither"},
    {"name": "Salmon", "icon": "icon-fish", "diet": "neither"},
    {"name": "Bacon", "icon": "icon-chicken", "diet": "neither"},
    {"name": "Shrimp", "icon": "icon-fish", "diet": "neither"},
    {"name": "Beef", "icon": "icon-chicken", "diet": "neither"},
    {"name": "Turkey", "icon": "icon-chicken", "diet": "neither"},
]

GAMES_META = [
    {"slug": "macro-memory-game", "title": "Macro Memory Match", "icon": "icon-game", "cardcls": "carbs",
     "meta": "A memory match game — flip cards to pair foods and learn which macronutrient each one is dominant in.",
     "intro": "Flip two cards at a time. Find all 6 matching pairs and learn each food's dominant macro along the way."},
    {"slug": "build-a-plate-game", "title": "Build-a-Plate", "icon": "icon-target", "cardcls": "fat",
     "meta": "Build a plate of real foods to hit a randomly assigned protein, fat, and carb target as closely as possible.",
     "intro": "You'll get a randomly assigned macro target. Click foods to add servings, watch your totals fill in live, then submit for a grade."},
    {"slug": "macro-sprint-game", "title": "Macro Sprint", "icon": "icon-flame", "cardcls": "protein",
     "meta": "A fast-paced sorting game — see a food and click its dominant macronutrient before your lives run out.",
     "intro": "You'll see one food at a time. Click Protein, Fat, or Carbs as fast as you can — three wrong answers and it's game over. Beat your high score."},
    {"slug": "diet-sorter-game", "title": "Diet Sorter", "icon": "icon-leaf", "cardcls": "diets",
     "meta": "A fast-paced sorting game — see a food and click whether it's Vegan, Vegetarian, or Neither before your lives run out.",
     "intro": "You'll see one food at a time. Click Vegan, Vegetarian, or Neither as fast as you can — three wrong answers and it's game over. Beat your high score."},
]

def quiz_hub_jsonld():
    """CollectionPage + ItemList covering both quizzes and games on the hub page."""
    items = (
        [{"@type": "ListItem", "position": i + 1, "name": qz["title"], "url": f"https://getmacros.net/{qz['slug']}.html"}
         for i, qz in enumerate(QUIZZES)]
        + [{"@type": "ListItem", "position": len(QUIZZES) + i + 1, "name": g["title"], "url": f"https://getmacros.net/{g['slug']}.html"}
           for i, g in enumerate(GAMES_META)]
    )
    data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Quiz Yourself",
        "url": "https://getmacros.net/quiz.html",
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": "GetMacros.net", "url": "https://getmacros.net/"},
        "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items},
    }
    return '<script type="application/ld+json">' + json.dumps(data).replace("</", "<\\/") + "</script>"




def game_page(slug, title, icon, meta, intro, body_script, category="general"):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
{seo_meta(title, meta, f"https://getmacros.net/{slug}.html", category=category)}
{article_jsonld(title, meta, f"https://getmacros.net/{slug}.html", kind="Game", category=category)}
{breadcrumb_jsonld(title, f"https://getmacros.net/{slug}.html", hub_name="Quiz", hub_url="https://getmacros.net/quiz.html")}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{nav_html("quiz")}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#{icon}"/></svg> Game</p>
      <h1>{title}</h1>
      <p>{intro}</p>
    </div>
  </section>

  <section>
    <div class="container">
      <div id="game-root"></div>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/confetti.js?v={ASSET_VERSION}"></script>
<script src="js/games.js?v={ASSET_VERSION}"></script>
<script>
{body_script}
</script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''


def build_quiz_hub():
    quiz_cards = "\n".join(
        f'''        <a href="{qz["slug"]}.html" class="card {("carbs" if qz["category"]=="general" else qz["category"] if qz["category"]!="fat" else "fat")}">
          <span class="icon-badge {("carbs" if qz["category"]=="general" else qz["category"] if qz["category"]!="fat" else "fat")}"><svg class="icon" aria-hidden="true"><use href="#icon-quiz"/></svg></span>
          <h3>{qz["h1"]}</h3><p>{qz["intro"]}</p></a>'''
        for qz in QUIZZES
    )
    game_cards = "\n".join(
        f'''        <a href="{g["slug"]}.html" class="card {g["cardcls"]}">
          <span class="icon-badge {g["cardcls"]}"><svg class="icon" aria-hidden="true"><use href="#{g["icon"]}"/></svg></span>
          <h3>{g["title"]}</h3><p>{g["intro"]}</p></a>'''
        for g in GAMES_META
    )
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>if(self!==top){{try{{top.location=self.location;}}catch(e){{document.documentElement.style.display="none";}}}}</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://pagead2.googlesyndication.com https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.googletagservices.com; style-src 'self' 'unsafe-inline' https://*.googlesyndication.com; img-src 'self' data: https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com https://*.gstatic.com; font-src 'self'; connect-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-src 'self' https://*.googlesyndication.com https://*.doubleclick.net https://*.google.com; frame-ancestors 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1b6b4a">
<link rel="preconnect" href="https://pagead2.googlesyndication.com">
<link rel="preconnect" href="https://www.highperformanceformat.com">
<title>Quiz Yourself | GetMacros.net</title>
<meta name="description" content="Test what you know about protein, fat, carbs, and sports nutrition with interactive quizzes and hands-on nutrition games.">
<meta name="author" content="{AUTHOR_NAME}">
<link rel="canonical" href="https://getmacros.net/quiz.html">
{seo_meta("Quiz Yourself", "Test what you know about protein, fat, carbs, and sports nutrition with interactive quizzes and hands-on nutrition games.", "https://getmacros.net/quiz.html", og_type="website")}
{quiz_hub_jsonld()}
<link rel="stylesheet" href="css/style.css?v={ASSET_VERSION}">
<script src="js/img-fallback.js?v={ASSET_VERSION}"></script>
{ADSENSE_LOADER}
</head>
<body>
{ICON_SPRITE}
{nav_html("quiz")}

<main>
  <section class="hero page-hero" style="background: linear-gradient(160deg, rgba(224,71,59,.85), rgba(221,154,31,.75) 55%, rgba(23,138,90,.85))">
    <div class="container">
      <p class="eyebrow"><svg class="icon" aria-hidden="true"><use href="#icon-graduation"/></svg> Study tools</p>
      <h1>Quiz yourself</h1>
      <p>Built for students who need the material to actually stick. Every question and every game is sourced straight from the articles on this site — get it wrong, and we'll point you right to the explanation.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2><svg class="icon" aria-hidden="true" style="color:var(--color-protein)"><use href="#icon-quiz"/></svg> Quizzes</h2>
      <p class="section-intro">Short, focused, and immediately followed by an explanation — right or wrong.</p>
      <div class="card-grid">
{quiz_cards}
      </div>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2><svg class="icon" aria-hidden="true" style="color:var(--color-carbs)"><use href="#icon-game"/></svg> Games</h2>
      <p class="section-intro">Learn by doing, not just reading.</p>
      <div class="card-grid">
{game_cards}
      </div>
    </div>
  </section>
</main>

{AD_SLOT}
{FOOTER}

<script src="js/main.js?v={ASSET_VERSION}"></script>
<script src="js/reveal.js?v={ASSET_VERSION}"></script>
<script src="js/ads-config.js?v={ASSET_VERSION}"></script>
<script src="js/ads.js?v={ASSET_VERSION}"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "quiz.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def main():
    memory_script = "initMemoryGame('game-root', " + json.dumps(MEMORY_PAIRS) + ");"
    path = os.path.join(ROOT, "macro-memory-game.html")
    with open(path, "w") as f:
        f.write(game_page("macro-memory-game", GAMES_META[0]["title"], GAMES_META[0]["icon"],
                           GAMES_META[0]["meta"], GAMES_META[0]["intro"], memory_script))
    print("wrote", path)

    plate_script = "initPlateGame('game-root', " + json.dumps(PLATE_FOODS) + ", " + json.dumps(PLATE_TARGETS) + ");"
    path = os.path.join(ROOT, "build-a-plate-game.html")
    with open(path, "w") as f:
        f.write(game_page("build-a-plate-game", GAMES_META[1]["title"], GAMES_META[1]["icon"],
                           GAMES_META[1]["meta"], GAMES_META[1]["intro"], plate_script))
    print("wrote", path)

    sprint_script = "initSprintGame('game-root', " + json.dumps(SPRINT_FOODS) + ");"
    path = os.path.join(ROOT, "macro-sprint-game.html")
    with open(path, "w") as f:
        f.write(game_page("macro-sprint-game", GAMES_META[2]["title"], GAMES_META[2]["icon"],
                           GAMES_META[2]["meta"], GAMES_META[2]["intro"], sprint_script))
    print("wrote", path)

    diet_script = "initDietSortGame('game-root', " + json.dumps(DIET_FOODS) + ");"
    path = os.path.join(ROOT, "diet-sorter-game.html")
    with open(path, "w") as f:
        f.write(game_page("diet-sorter-game", GAMES_META[3]["title"], GAMES_META[3]["icon"],
                           GAMES_META[3]["meta"], GAMES_META[3]["intro"], diet_script))
    print("wrote", path)

    build_quiz_hub()
    build_full_sitemap()


def build_full_sitemap():
    domain = "https://getmacros.net"
    entries = []
    for path, priority in CORE_PAGES:
        entries.append(f"  <url>\n    <loc>{domain}/{path}</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>{priority}</priority>\n  </url>")
    for a in ARTICLES:
        entries.append(f'  <url>\n    <loc>{domain}/{a["slug"]}.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.7</priority>\n  </url>')
    entries.append(f"  <url>\n    <loc>{domain}/glossary.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.7</priority>\n  </url>")
    entries.append(f"  <url>\n    <loc>{domain}/quiz.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.8</priority>\n  </url>")
    for qz in QUIZZES:
        entries.append(f'  <url>\n    <loc>{domain}/{qz["slug"]}.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.6</priority>\n  </url>')
    for g in GAMES_META:
        entries.append(f'  <url>\n    <loc>{domain}/{g["slug"]}.html</loc>\n    <lastmod>{SITEMAP_LASTMOD}</lastmod>\n    <priority>0.6</priority>\n  </url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, "w") as f:
        f.write(xml)
    print("wrote", path, f"({len(CORE_PAGES) + len(ARTICLES) + 2 + len(QUIZZES) + len(GAMES_META)} urls)")


if __name__ == "__main__":
    main()
