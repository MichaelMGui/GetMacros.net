"""Render food comparisons from reviewed, consistently scaled reference values."""
from pathlib import Path
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
foods = json.loads((ROOT / 'tools/protein-food-review.json').read_text(encoding='utf-8'))
path = ROOT / 'high-protein-foods-list.html'
s = path.read_text(encoding='utf-8')

def rounded(value):
    return str(math.floor(value + .5))

def protein(food):
    return rounded(food['protein100'] * food['grams'] / 100)

icons = {}
for group in ['animal', 'plant']:
    card = re.search(r'<article class="protein-food-card" data-food-group="'+group+r'".*?</article>', s, re.S)[0]
    icons[group] = re.search(r'<svg\b.*?</svg>', card, re.S)[0]
cards = []
for food in foods:
    name = html.escape(food['name'], quote=True)
    cards.append('<article class="protein-food-card" data-food-group="'+food['group']+'" data-food-name="'+name+'">'+icons[food['group']]+'<h3>'+name+'</h3><p class="food-protein-number"><strong>'+protein(food)+' g</strong> protein</p><p class="food-portion">'+html.escape(food['portion'])+'</p></article>')
s = re.sub(r'(<div class="protein-food-grid">).*?(</div><p class="food-empty")', lambda m: m[1]+''.join(cards)+m[2], s, count=1, flags=re.S)

tables = []
for group in ['animal', 'plant']:
    rows = []
    for food in (f for f in foods if f['group'] == group):
        name = '<a href="'+html.escape(food['source'], quote=True)+'">'+html.escape(food['name'])+'</a>'
        if food['reference']:
            name += '<small class="food-source-detail">'+html.escape(food['reference'])+'</small>'
        values = [f"{food['protein100']:.1f} g", rounded(food['calories100']), rounded(food['protein100']/food['calories100']*100)+' g', food['portion'], protein(food)+' g']
        labels = ['Protein / 100 g','Calories / 100 g','Protein / 100 calories','Example portion','Protein / portion']
        rows.append('<tr><th scope="row">'+name+'</th>'+''.join('<td data-label="'+label+'">'+html.escape(v)+'</td>' for label,v in zip(labels,values))+'</tr>')
    tables.append('<table class="data-table"><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in ['Food & source','Protein per 100 g','Calories per 100 g','Protein per 100 calories','Example portion','Protein per portion'])+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table>')
iterator = iter(tables)
s = re.sub(r'<table class="data-table">.*?</table>', lambda m: next(iterator), s, flags=re.S)
s = re.sub(r'<p class="food-reference-note">.*?</p>', '<p class="food-reference-note">Numbers are rounded reference values, not a promise about every brand. The comparison table links each food to its USDA entry or product label. Weigh the portion you eat and use your package label when available.</p>', s, flags=re.S)
path.write_text(s, encoding='utf-8')
print(f'Rendered {len(foods)} sourced food comparisons with consistent portion calculations.')
