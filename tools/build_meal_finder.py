#!/usr/bin/env python3
"""Derive goal tags for the meal data, and build the finder page's reference section.

Two jobs, both driven off js/meal-data.js so nothing can disagree with itself:

1. Goal tags (high protein, lighter, ...) are computed from each meal's own
   numbers and written back into the `t` array. They used to be hand-assigned
   and had drifted badly: 41 meals carried a "high protein" tag while only 36
   reached the 25 g the label claimed, and 16 were tagged higher-calorie when
   only 10 reached 600 kcal. A threshold that a page states out loud has to be
   the threshold the page actually applies.

2. The reference section under the quiz. Chain-by-chain tables were the wrong
   shape for this page: every chain guide already publishes its own menu, so
   repeating it here duplicated content and read as an appendix. What no single
   guide can offer is the view across all of them, which is also what people
   search for. So the section is a set of ranked cross-chain lists.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PAGE = os.path.join(ROOT, "restaurant-meal-finder.html")
DATA = os.path.join(ROOT, "js", "meal-data.js")
START = "<!--MEALS:START-->"
END = "<!--MEALS:END-->"

# Every threshold the site states in words. Change them here and the tags, the
# quiz labels generated from them, and the lists below all move together.
PROTEIN_G = 25
ENERGY_KCAL = 600
LIGHT_KCAL = 400
FIBRE_G = 5
SODIUM_MG = 600


def substantial(m):
    """Require enough energy and protein to function as a meaningful entrée."""
    name = m.get("name", "").lower()
    looks_like_side = any(word in name for word in ("side", "apple slices", "coleslaw", "green beans"))
    snack_size = m.get("size") == "small" and (m.get("p") or 0) < 10
    return (
        not looks_like_side
        and not snack_size
        and (m.get("cal") or 0) >= 250
        and (m.get("p") or 0) >= 15
    )


def goal_tags(m):
    """The goal tags a meal earns from its own published numbers."""
    t = []
    if m["p"] is not None and m["p"] >= PROTEIN_G:
        t.append("protein")
    if m["cal"] is not None and m["cal"] >= ENERGY_KCAL:
        t.append("energy")
    if substantial(m) and m["cal"] <= LIGHT_KCAL:
        t.append("light")
    if m["f"] is not None and m["f"] >= FIBRE_G:
        t.append("fibre")
    if substantial(m) and m["na"] is not None and m["na"] <= SODIUM_MG:
        t.append("lowsodium")
    # Balanced means nothing is at an extreme: a real meal's worth of calories
    # carrying a real meal's worth of protein.
    if (m["cal"] is not None and LIGHT_KCAL < m["cal"] < ENERGY_KCAL
            and m["p"] is not None and m["p"] >= 20):
        t.append("balanced")
    return t


def parse_meals(src):
    meals = []
    for raw in re.findall(r"\{chain:.*?\}(?=,\n|\n\];|\n\])", src, re.S):
        o = re.sub(r"(\{|,)\s*([a-zA-Z_]\w*)\s*:", r'\1"\2":', raw)
        o = re.sub(r"'((?:[^'\\]|\\.)*)'",
                   lambda m: json.dumps(m.group(1).replace("\\'", "'")), o)
        meals.append(json.loads(o))
    return meals


def write_tags(src, meals):
    """Write each meal's derived `t` array back into meal-data.js."""
    out, i = src, 0
    chunks = re.split(r"(\{chain:.*?\}(?=,\n|\n\];|\n\]))", src, flags=re.S)
    for k, chunk in enumerate(chunks):
        if not chunk.startswith("{chain:"):
            continue
        tags = ",".join("'%s'" % t for t in goal_tags(meals[i]))
        # Substitute inside the existing slot rather than removing and
        # reinserting it, which left a stray comma behind. The lookbehind keeps
        # this off the "t:[" inside "diet:[".
        body, n = re.subn(r"(?<![a-zA-Z])t:\[[^\]]*\]", "t:[%s]" % tags, chunk, count=1)
        assert n == 1, f"no t:[] slot in record {i}"
        chunks[k] = body
        i += 1
    assert i == len(meals), f"rewrote {i} of {len(meals)}"
    return "".join(chunks)


def num(v, unit=""):
    return "&mdash;" if v is None else f"{v:,}{unit}"


def ranked(meals, key, reverse=True, limit=12, where=None):
    pool = [m for m in meals if m[key] is not None and (where is None or where(m))]
    pool.sort(key=lambda m: m[key], reverse=reverse)
    return pool[:limit]


def table(rows, highlight):
    """One ranked list. `highlight` is the column the ranking is by."""
    cols = [("cal", "Calories", ""), ("p", "Protein", " g"),
            ("f", "Fiber", " g"), ("na", "Sodium", " mg")]
    out = ['<div class="table-scroll"><table class="meal-table"><thead><tr>'
           '<th scope="col">Meal</th><th scope="col">Restaurant</th>']
    for k, label, _ in cols:
        cls = ' class="is-key"' if k == highlight else ""
        out.append(f'<th scope="col"{cls}>{label}</th>')
    out.append("</tr></thead><tbody>")
    for m in rows:
        out.append(f'<tr><th scope="row"><a href="{html.escape(m["url"])}">'
                   f'{html.escape(m["name"])}</a></th>'
                   f'<td>{html.escape(m["chain"])}</td>')
        for k, _, unit in cols:
            cls = ' class="is-key"' if k == highlight else ""
            out.append(f"<td{cls}>{num(m[k], unit)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def render(meals):
    n = len(meals)
    chains = sorted({m["chain"] for m in meals})

    sections = [
        ("highest-protein-fast-food", "Highest-protein fast food meals",
         f"Ranked across all {len(chains)} chains. Everything here clears "
         f"{PROTEIN_G} g, and the leaders roughly double it.",
         ranked(meals, "p"), "p"),
        ("high-calorie-fast-food", "High-calorie fast food meals for bulking",
         "Complete orders at 1,000 calories or more, ranked largest first. "
         "Combined orders name every item included; drinks and unlisted sauces are excluded.",
         ranked(meals, "cal", where=lambda m: m["cal"] >= 1000), "cal"),
        ("fast-food-under-400-calories", f"Fast food under {LIGHT_KCAL} calories",
         "Substantial entrées and meal components only: at least 250 calories and 15 g protein. "
         "Tiny sides and snack portions are excluded.",
         ranked(meals, "cal", reverse=False, where=lambda m: substantial(m) and m["cal"] <= LIGHT_KCAL), "cal"),
        ("highest-fibre-fast-food", "Fast food with the most fiber",
         "Fiber is the number most fast-food menus are thin on, and the one that "
         "most changes whether a meal holds you until the next one.",
         ranked(meals, "f"), "f"),
        ("lowest-sodium-fast-food", "Lower-sodium meals and entrées",
         "Only substantial items with at least 250 calories, 15 g protein and a published sodium figure qualify. "
         "A missing number is not a low one, so nothing unpublished is ranked here.",
         ranked(meals, "na", reverse=False, where=substantial), "na"),
        ("vegetarian-fast-food", "Every vegetarian option we track",
         "No meat or fish in the standard build. Ordered by protein, because that "
         "is the number these meals most often give up.",
         ranked(meals, "p", where=lambda m: "vegetarian" in m["diet"], limit=99), "p"),
        ("plant-based-fast-food", "Every plant-based option we track",
         "No animal products in the standard build. Check preparation locally: "
         "shared fryers and dairy-based sauces are the usual surprises.",
         ranked(meals, "p", where=lambda m: "plant" in m["diet"], limit=99), "p"),
        ("healthy-fast-food-breakfast", "Breakfast items worth ordering",
         "Served on the breakfast menu. Ordered by protein, since that is what "
         "decides whether a breakfast lasts past mid-morning.",
         ranked(meals, "p", where=lambda m: m["meal"] == "breakfast", limit=99), "p"),
    ]

    out = [START,
           '<div class="container"><details class="meal-database-disclosure">',
           f'<summary><strong>Browse all {n} tracked meals</strong><span>Optional: open the complete cross-chain nutrition database and rankings.</span></summary>',
           '<section class="meal-index"><div class="container">',
           "<h2>All tracked meals, ranked by nutrition</h2>",
           f"<p class=\"meal-index-intro\">The quiz answers one question at a time. "
           f"These are the standing lists behind it: all {n} tracked menu options from "
           f"{len(chains)} chains, sorted the ways people actually ask for them. "
           f"Every figure is the chain's published standard build.</p>",
           '<nav class="meal-jump" aria-label="Jump to a list"><ul>']
    for slug, title, _, _, _ in sections:
        out.append(f'<li><a href="#{slug}">{html.escape(title)}</a></li>')
    out.append("</ul></nav>")

    for slug, title, blurb, rows, key in sections:
        if not rows:
            continue
        out.append(f'<section class="meal-list" id="{slug}">')
        out.append(f"<h3>{html.escape(title)}</h3>")
        out.append(f'<p class="meal-list-note">{blurb} <b>{len(rows)}</b> '
                   f'{"item" if len(rows) == 1 else "items"}.</p>')
        out.append(table(rows, key))
        out.append("</section>")

    out.append('<p class="meal-index-foot">Looking for one restaurant rather than a '
               'ranking? Each chain has its own guide: ')
    out.append(", ".join(
        f'<a href="{html.escape(next(m["url"] for m in meals if m["chain"] == c))}">'
        f'{html.escape(c)}</a>' for c in chains))
    out.append(".</p>")
    out.append("</div></section></details></div>")
    out.append(END)
    return "\n".join(out)


def main():
    src = open(DATA, encoding="utf-8").read()
    meals = parse_meals(src)
    if len(meals) < 2:
        print(f"ERROR: parsed only {len(meals)} meals", file=sys.stderr)
        return 1

    for m in meals:
        m["t"] = goal_tags(m)

    # Render before writing anything. A failure here used to leave meal-data.js
    # half-rewritten, with the old tags already stripped and the new ones never
    # added.
    c = open(PAGE, encoding="utf-8").read()
    complete_count = sum(1 for m in meals if all(m.get(k) is not None for k in ("cal", "p", "f", "na")))
    c = re.sub(r"css/meal-finder-v2\.css\?v=[^\"']+", "css/meal-finder-v2.css?v=20260823c", c)
    c = c.replace('"name": "What sounds right for you today?"', '"name": "Healthy Order Match"')
    c = c.replace('>Healthy fast food</a>', '>Healthy Fast Food</a>')
    c = c.replace('aria-current="page">Meal finder</span>', 'aria-current="page">Healthy Order Match</span>')
    c = re.sub(r"Five clear questions rank \d+ (?:real menu items|tracked menu options) from \d+ restaurants\.",
               f"Five clear questions rank {len(meals)} tracked menu options from {len({m['chain'] for m in meals})} restaurants.", c)
    c = re.sub(r"<span>\d+ complete nutrition profiles</span>",
               f"<span>{complete_count} complete nutrition profiles</span>", c)
    c = re.sub(r'<div class="visual-card one"><b>\d+ choices</b>',
               f'<div class="visual-card one"><b>{len(meals)} choices</b>', c)
    block = render(meals)

    tagged = write_tags(src, meals)
    # Publish the thresholds so the quiz can label its own options from them.
    # The numbers a question promises and the numbers the tags apply are then
    # the same numbers, by construction.
    line = ("window.GM_THRESHOLDS = {protein:%d,energy:%d,light:%d,fibre:%d,sodium:%d};\n"
            % (PROTEIN_G, ENERGY_KCAL, LIGHT_KCAL, FIBRE_G, SODIUM_MG))
    if "window.GM_THRESHOLDS" in tagged:
        tagged = re.sub(r"window\.GM_THRESHOLDS = \{[^}]*\};\n", line, tagged)
    else:
        tagged = tagged.replace("window.GM_MEALS = [", line + "\nwindow.GM_MEALS = [", 1)
    if tagged != src:
        open(DATA, "w", encoding="utf-8").write(tagged)
    if START in c and END in c:
        c = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, c, flags=re.S)
    else:
        c = c.replace("</main>", block + "</main>", 1)
    open(PAGE, "w", encoding="utf-8").write(c)

    counts = {}
    for m in meals:
        for t in m["t"]:
            counts[t] = counts.get(t, 0) + 1
    print(f"meal data: {len(meals)} meals, derived tags {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
