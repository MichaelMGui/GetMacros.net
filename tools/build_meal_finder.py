#!/usr/bin/env python3
"""Render the full meal list into restaurant-meal-finder.html as static HTML.

The quiz above it is JavaScript, so without this the page has almost no text a
crawler can read and the 74 meals are invisible to search. Generating the list
from js/meal-data.js keeps the two from drifting: the quiz and the printed
table are the same 74 rows.

Writes between two markers so it can run on every build.
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

TAG_LABEL = {
    "protein": "high protein", "light": "lighter", "energy": "higher calorie",
    "fibre": "high fibre", "lowsodium": "lower sodium", "balanced": "balanced",
    "vegetarian": "vegetarian", "plant": "plant-based",
    "gluten": "gluten-aware", "breakfast": "breakfast",
}


def parse_meals():
    """Read the object literals out of meal-data.js.

    The file is hand-maintained JS rather than JSON, so each record is
    converted to JSON before parsing instead of being eval'd.
    """
    src = open(DATA, encoding="utf-8").read()
    meals = []
    for raw in re.findall(r"\{chain:.*?\}(?=,\n|\n\];|\n\])", src, re.S):
        obj = raw
        obj = re.sub(r"(\{|,)\s*([a-zA-Z_]\w*)\s*:", r'\1"\2":', obj)
        obj = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: json.dumps(m.group(1).replace("\\'", "'")), obj)
        meals.append(json.loads(obj))
    return meals


def num(v, unit=""):
    return "&mdash;" if v is None else f"{v:,}{unit}"


def render(meals):
    by_chain = {}
    for m in meals:
        by_chain.setdefault(m["chain"], []).append(m)

    out = [
        START,
        '<section class="meal-index"><div class="container">',
        f"<h2>Every meal we track, by restaurant</h2>",
        f"<p>All {len(meals)} items the finder draws on, across "
        f"{len(by_chain)} chains. Figures are standard published builds; a dash "
        "means the chain does not publish that value.</p>",
    ]
    for chain in sorted(by_chain):
        rows = sorted(by_chain[chain], key=lambda m: m["name"])
        guide = rows[0]["url"]
        out.append(f'<h3>{html.escape(chain)}</h3>')
        out.append('<div class="table-scroll"><table class="meal-table">')
        out.append("<thead><tr><th>Meal</th><th>Calories</th><th>Protein</th>"
                   "<th>Fibre</th><th>Sodium</th><th>Best for</th></tr></thead><tbody>")
        for m in rows:
            tags = ", ".join(TAG_LABEL.get(t, t) for t in m["t"]) or "&mdash;"
            out.append(
                f'<tr><th scope="row">{html.escape(m["name"])}</th>'
                f'<td>{num(m["cal"])}</td><td>{num(m["p"], " g")}</td>'
                f'<td>{num(m["f"], " g")}</td><td>{num(m["na"], " mg")}</td>'
                f"<td>{tags}</td></tr>"
            )
        out.append("</tbody></table></div>")
        out.append(f'<p class="meal-index-link">'
                   f'<a href="{html.escape(guide)}">Full {html.escape(chain)} guide &rarr;</a></p>')
    out.append("</div></section>")
    out.append(END)
    return "\n".join(out)


def main():
    meals = parse_meals()
    if len(meals) < 2:
        print(f"ERROR: parsed only {len(meals)} meals from meal-data.js", file=sys.stderr)
        return 1

    c = open(PAGE, encoding="utf-8").read()
    block = render(meals)
    if START in c and END in c:
        c = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, c, flags=re.S)
    else:
        c = c.replace("</main>", block + "</main>", 1)
    open(PAGE, "w", encoding="utf-8").write(c)
    print(f"meal index: {len(meals)} meals across "
          f"{len(set(m['chain'] for m in meals))} chains")
    return 0


if __name__ == "__main__":
    sys.exit(main())
