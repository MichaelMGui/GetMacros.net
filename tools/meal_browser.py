"""Render one browsable card per restaurant order, with a no-JavaScript fallback."""
from html import escape

FILTERS = [
    ('', 'All meals', ''),
    ('protein', 'High protein', 'highest-protein-fast-food'),
    ('light', '400 calories or less', 'fast-food-under-400-calories'),
    ('energy', '600+ calories', 'high-calorie-fast-food'),
    ('vegetarian', 'Vegetarian', 'vegetarian-fast-food'),
    ('plant', 'Plant-based', 'plant-based-fast-food'),
    ('breakfast', 'Breakfast', 'healthy-fast-food-breakfast'),
    ('fibre', 'High fiber', 'highest-fibre-fast-food'),
    ('lowsodium', 'Lower sodium', 'lowest-sodium-fast-food'),
]


def render(meals):
    out = ['<!--MEALS:START-->', '<div class="container meal-browser-shell">',
           '<details class="meal-database-disclosure" id="browse-meals">',
           f'<summary><strong>Browse {len(meals)} meals</strong></summary>',
           '<div class="meal-browser" data-meal-browser>',
           '<div class="meal-browser-controls" hidden>',
           '<label for="browse-query">Search meals or restaurants<input type="search" id="browse-query" placeholder="e.g. chicken" autocomplete="off"></label>',
           '<label for="browse-filter">Show<select id="browse-filter">']
    out.extend(f'<option value="{value}">{label}</option>' for value, label, _ in FILTERS)
    out.extend(['</select></label></div>',
                '<p class="browse-status" role="status" aria-live="polite" aria-atomic="true" hidden></p>',
                '<div class="browse-meal-grid">'])
    chain_order = ['Chipotle', 'Chick-fil-A', 'Subway', 'Panera', 'Panda Express']
    def order_key(meal):
        complete = all(meal[k] is not None for k in ('cal', 'p', 'f', 'na'))
        rank = chain_order.index(meal['chain']) if meal['chain'] in chain_order else len(chain_order)
        return (not complete, rank, meal['chain'], meal['name'])
    for meal in sorted(meals, key=order_key):
        # Editorial prefixes are not part of the restaurant's order name.
        name = meal['name'].replace('High-protein bulking order: ', '')
        tags = meal['t'] + meal['diet'] + ([meal['meal']] if meal['meal'] == 'breakfast' else [])
        slug = meal['url'].split('-healthy')[0]
        out.append(f'<article class="browse-meal" data-tags="{escape(" ".join(tags))}" '
                   f'data-search="{escape(meal["chain"] + " " + name, quote=True)}" '
                   f'data-protein="{meal["p"] if meal["p"] is not None else -1}" '
                   f'data-calories="{meal["cal"] if meal["cal"] is not None else -1}" '
                   f'data-fiber="{meal["f"] if meal["f"] is not None else -1}" '
                   f'data-sodium="{meal["na"] if meal["na"] is not None else 99999}">')
        out.append(f'<div class="browse-meal-brand"><img src="images/restaurant-logos/{escape(slug)}.png" '
                   f'width="36" height="36" alt="" loading="lazy"><span>{escape(meal["chain"])}</span></div>')
        out.append(f'<h3>{escape(name)}</h3><dl class="browse-meal-stats">')
        for key, label, unit in [('cal', 'Calories', ''), ('p', 'Protein', ' g'), ('f', 'Fiber', ' g'), ('na', 'Sodium', ' mg')]:
            value = 'Not listed' if meal[key] is None else f'{meal[key]:,}{unit}'
            out.append(f'<div><dt>{label}</dt><dd>{value}</dd></div>')
        out.append(f'</dl><a class="btn action-link" href="{escape(meal["url"])}">View menu</a></article>')
    out.extend(['</div>', '<p class="browse-empty" hidden>No meals found. Try another search or filter.</p>',
                '<button class="btn browse-more" type="button" hidden>Show more meals</button>',
                '<details class="browse-nutrition-note"><summary>Nutrition &amp; filters</summary>',
                '<p>Numbers are for the listed order; portions and substitutions can change them. Check allergens with the restaurant.</p>',
                '<p>High protein: 25 g or more. High fiber: 5 g or more. Lower sodium: up to 600 mg. Lower-calorie and lower-sodium filters include meals with at least 250 calories and 15 g protein.</p>',
                '<a href="sources.html">Nutrition sources</a></details>',
                '</div></details></div>', '<script src="js/meal-browser.js" defer></script>', '<!--MEALS:END-->'])
    return '\n'.join(out)
