#!/usr/bin/env python3
"""Derive goal tags for the meal data, and build the finder page's reference section.

Two jobs, both driven off js/meal-data.js so nothing can disagree with itself:

1. Goal tags (high protein, lighter, ...) are computed from each meal's own
   numbers and written back into the `t` array. They used to be hand-assigned
   and had drifted badly: 41 meals carried a "high protein" tag while only 36
   reached the 25 g the label claimed, and 16 were tagged higher-calorie when
   only 10 reached 600 kcal. A threshold that a page states out loud has to be
   the threshold the page actually applies.

2. A single browseable list under the quiz. Render each order once, with search,
   goal filters and progressive disclosure instead of repeated ranking tables.
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

HERO = r'''<section class="match-intro" data-spotlight>
  <div class="container match-intro-grid">
    <div class="match-intro-copy">
      <p class="match-kicker"><span>Healthy fast-food finder</span></p>
      <h1>Find a meal that fits your goals.</h1>
      <p>Choose what matters today. We compare real menu items from 15 restaurants and explain the strongest matches.</p>
    </div>
    <div class="match-live-quiz" role="region" aria-label="Healthy Order Match questionnaire">
      <div id="meal-quiz"></div>
    </div>
  </div>
</section>
<script src="js/meal-data.js?v=7faded9221"></script><script src="js/meal-quiz.js?v=9baee3767c"></script>'''

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
    from meal_browser import render as render_browser
    return render_browser(meals)


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
    c, hero_count = re.subn(
        r'<section class="(?:order-match-hero|match-intro)[^>]*>.*?</section>'
        r'(?:\s*<section class="quiz-stage[^>]*>.*?</section>)?'
        r'(?:\s*<script src="js/meal-data\.js[^>]*></script>'
        r'<script src="js/meal-quiz\.js[^>]*></script>)?'
        r'(?=\s*(?:<section class="mm-stage|<div class="ad-auto-anchor|<!--MEALS:START-->))',
        HERO,
        c,
        count=1,
        flags=re.S,
    )
    if hero_count != 1:
        raise RuntimeError("could not replace the meal finder hero")
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
