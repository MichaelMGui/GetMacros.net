#!/usr/bin/env python3
"""Generates the quiz-hub-adjacent game pages and play.html for GetMacros.net."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_articles import ROOT, nav_html, FOOTER, ARTICLES, CORE_PAGES  # noqa: E402
from generate_quizzes import QUIZZES  # noqa: E402

MEMORY_PAIRS = [
    {"emoji": "🍗", "name": "Chicken Breast", "macro": "protein"},
    {"emoji": "🐟", "name": "Salmon", "macro": "fat"},
    {"emoji": "🥑", "name": "Avocado", "macro": "fat"},
    {"emoji": "🍚", "name": "Brown Rice", "macro": "carbs"},
    {"emoji": "🥣", "name": "Greek Yogurt", "macro": "protein"},
    {"emoji": "🍌", "name": "Banana", "macro": "carbs"},
]

PLATE_FOODS = [
    {"id": "chicken", "emoji": "🍗", "name": "Chicken Breast (150g)", "protein": 46, "fat": 5, "carb": 0},
    {"id": "salmon", "emoji": "🐟", "name": "Salmon (150g)", "protein": 37, "fat": 20, "carb": 0},
    {"id": "egg", "emoji": "🥚", "name": "Egg (1 large)", "protein": 6, "fat": 5, "carb": 0.5},
    {"id": "yogurt", "emoji": "🥣", "name": "Greek Yogurt (1 cup)", "protein": 17, "fat": 0, "carb": 6},
    {"id": "avocado", "emoji": "🥑", "name": "Avocado (half)", "protein": 2, "fat": 15, "carb": 9},
    {"id": "oliveoil", "emoji": "🫒", "name": "Olive Oil (1 tbsp)", "protein": 0, "fat": 14, "carb": 0},
    {"id": "almonds", "emoji": "🥜", "name": "Almonds (30g)", "protein": 6, "fat": 14, "carb": 6},
    {"id": "rice", "emoji": "🍚", "name": "Brown Rice (1 cup)", "protein": 5, "fat": 2, "carb": 45},
    {"id": "oats", "emoji": "🌾", "name": "Oats (40g)", "protein": 5, "fat": 3, "carb": 27},
    {"id": "banana", "emoji": "🍌", "name": "Banana (1 medium)", "protein": 1, "fat": 0, "carb": 27},
    {"id": "broccoli", "emoji": "🥦", "name": "Broccoli (1 cup)", "protein": 3, "fat": 0, "carb": 6},
    {"id": "beans", "emoji": "🫘", "name": "Black Beans (1 cup)", "protein": 15, "fat": 1, "carb": 41},
    {"id": "pb", "emoji": "🥜", "name": "Peanut Butter (2 tbsp)", "protein": 7, "fat": 16, "carb": 6},
    {"id": "sweetpotato", "emoji": "🍠", "name": "Sweet Potato (1 medium)", "protein": 2, "fat": 0, "carb": 24},
]

PLATE_TARGETS = [
    {"name": "High-Protein Lunch", "desc": "~565 calories, built around lean protein.", "protein": 50, "fat": 20, "carb": 45},
    {"name": "Balanced Dinner", "desc": "~665 calories, an even split across all three.", "protein": 40, "fat": 25, "carb": 60},
    {"name": "Post-Workout Recovery", "desc": "~625 calories, carb-forward for glycogen refill.", "protein": 45, "fat": 15, "carb": 70},
]

GAMES_META = [
    {"slug": "macro-memory-game", "title": "Macro Memory Match", "eyebrow": "Game",
     "meta": "A memory match game — flip cards to pair foods and learn which macronutrient each one is dominant in.",
     "intro": "Flip two cards at a time. Find all 6 matching pairs and learn each food's dominant macro along the way."},
    {"slug": "build-a-plate-game", "title": "Build-a-Plate", "eyebrow": "Game",
     "meta": "Build a plate of real foods to hit a randomly assigned protein, fat, and carb target as closely as possible.",
     "intro": "You'll get a randomly assigned macro target. Click foods to add servings, watch your totals fill in live, then submit for a grade."},
]


def game_page(slug, title, eyebrow, meta, intro, body_script):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | GetMacros.net</title>
<meta name="description" content="{meta}">
<link rel="canonical" href="https://getmacros.net/{slug}.html">
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
</head>
<body>
{nav_html("play")}

<main>
  <section class="page-hero" style="background:var(--color-primary-dark); color:#fff;">
    <div class="container">
      <p class="eyebrow">{eyebrow}</p>
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

{FOOTER}

<script src="js/main.js"></script>
<script src="js/confetti.js"></script>
<script src="js/games.js"></script>
<script>
{body_script}
</script>
</body>
</html>
'''


def build_play_hub():
    quiz_cards = "\n".join(
        f'        <a href="{qz["slug"]}.html" class="card {("carbs" if qz["category"]=="general" else qz["category"] if qz["category"]!="fat" else "fat")}"><h3>{qz["h1"]}</h3><p>{qz["intro"]}</p></a>'
        for qz in QUIZZES
    )
    game_cards = "\n".join(
        f'        <a href="{g["slug"]}.html" class="card carbs"><h3>{g["title"]}</h3><p>{g["intro"]}</p></a>'
        for g in GAMES_META
    )
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quizzes &amp; Games | GetMacros.net</title>
<meta name="description" content="Test your macro knowledge with quizzes, or play a nutrition game — Macro Memory Match and Build-a-Plate.">
<link rel="canonical" href="https://getmacros.net/play.html">
<link rel="stylesheet" href="css/style.css">
<script src="js/img-fallback.js"></script>
</head>
<body>
{nav_html("play")}

<main>
  <section class="hero page-hero" style="background: linear-gradient(rgba(90,20,15,.72),rgba(10,60,35,.8))">
    <div class="container">
      <p class="eyebrow">Play</p>
      <h1>Quizzes &amp; games</h1>
      <p>Everything here is built from the facts on this site. Test yourself, or just play around.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <h2><span class="pill protein">Quizzes</span></h2>
      <div class="card-grid">
{quiz_cards}
      </div>
    </div>
  </section>

  <section style="background:var(--color-carbs-bg)">
    <div class="container">
      <h2><span class="pill carbs">Games</span></h2>
      <div class="card-grid">
{game_cards}
      </div>
    </div>
  </section>
</main>

{FOOTER}

<script src="js/main.js"></script>
<script src="js/reveal.js"></script>
</body>
</html>
'''
    path = os.path.join(ROOT, "play.html")
    with open(path, "w") as f:
        f.write(html)
    print("wrote", path)


def main():
    memory_script = "initMemoryGame('game-root', " + json.dumps(MEMORY_PAIRS) + ");"
    path = os.path.join(ROOT, "macro-memory-game.html")
    with open(path, "w") as f:
        f.write(game_page("macro-memory-game", GAMES_META[0]["title"], GAMES_META[0]["eyebrow"],
                           GAMES_META[0]["meta"], GAMES_META[0]["intro"], memory_script))
    print("wrote", path)

    plate_script = "initPlateGame('game-root', " + json.dumps(PLATE_FOODS) + ", " + json.dumps(PLATE_TARGETS) + ");"
    path = os.path.join(ROOT, "build-a-plate-game.html")
    with open(path, "w") as f:
        f.write(game_page("build-a-plate-game", GAMES_META[1]["title"], GAMES_META[1]["eyebrow"],
                           GAMES_META[1]["meta"], GAMES_META[1]["intro"], plate_script))
    print("wrote", path)

    build_play_hub()
    build_full_sitemap()


def build_full_sitemap():
    domain = "https://getmacros.net"
    entries = []
    for path, priority in CORE_PAGES:
        entries.append(f"  <url>\n    <loc>{domain}/{path}</loc>\n    <priority>{priority}</priority>\n  </url>")
    for a in ARTICLES:
        entries.append(f'  <url>\n    <loc>{domain}/{a["slug"]}.html</loc>\n    <priority>0.7</priority>\n  </url>')
    entries.append(f"  <url>\n    <loc>{domain}/play.html</loc>\n    <priority>0.8</priority>\n  </url>")
    for qz in QUIZZES:
        entries.append(f'  <url>\n    <loc>{domain}/{qz["slug"]}.html</loc>\n    <priority>0.6</priority>\n  </url>')
    for g in GAMES_META:
        entries.append(f'  <url>\n    <loc>{domain}/{g["slug"]}.html</loc>\n    <priority>0.6</priority>\n  </url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    path = os.path.join(ROOT, "sitemap.xml")
    with open(path, "w") as f:
        f.write(xml)
    print("wrote", path, f"({len(CORE_PAGES) + len(ARTICLES) + 1 + len(QUIZZES) + len(GAMES_META)} urls)")


if __name__ == "__main__":
    main()
