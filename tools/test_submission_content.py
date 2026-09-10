"""Regression checks for the editorial and restaurant-data review."""
import html
import json
import re
from pathlib import Path

from build_meal_finder import goal_tags, substantial
from build_restaurant_pages import item_type, parse_meals
from submission_content import PAGES

ROOT = Path(__file__).resolve().parents[1]
meals = parse_meals()
records = json.loads((ROOT / 'tools/restaurant-review.json').read_text(encoding='utf-8'))
indexed = {(m['chain'], m['name']): m for m in meals}
reviewed = {(r['chain'], r['name']): r for r in records}
assert len(records) == len(reviewed), 'Duplicate review records'
assert indexed.keys() == reviewed.keys(), 'Every tracked order needs a source review'
for key, meal in indexed.items():
    record = reviewed[key]
    assert record['source'].startswith('https://'), key
    assert {k: meal[k] for k in ['cal', 'p', 'c', 'f', 'na']} == record['values'], key
    assert meal['t'] == goal_tags(meal), ('Stale filter tags', key)
    for nutrient, tag in [('p', 'protein'), ('f', 'fibre'), ('na', 'lowsodium')]:
        if meal[nutrient] is None:
            assert tag not in meal['t'], ('Unknown nutrient qualified for filter', key, tag)

assert 'vegetarian' not in indexed[('Popeyes', 'Red Beans & Rice, regular')]['diet']
assert 'plant' not in indexed[('CAVA', 'Falafel Crunch bowl')]['diet']
combo = indexed[('KFC', 'Grilled Breast with green beans and corn')]
assert item_type(combo) == 'Entrée / meal' and substantial(combo)
assert item_type(indexed[('Panera', 'Hearty Fireside Chili, bowl')]) == 'Entrée / meal'
assert item_type(indexed[('KFC', 'Green Beans, individual')]) == 'Side'

def total(names):
    return {k: sum(indexed[name][k] for name in names) for k in ['cal', 'p', 'c', 'f', 'na']}

panda = indexed[('Panda Express', 'Grilled Teriyaki Chicken with Super Greens')]
assert {k: panda[k] for k in ['cal', 'p', 'c', 'f', 'na']} == total([
    ('Panda Express', 'Grilled Teriyaki Chicken'), ('Panda Express', 'Super Greens side')])
popeyes = indexed[('Popeyes', '3 Blackened Tenders with regular red beans and rice')]
assert {k: popeyes[k] for k in ['cal', 'p', 'c', 'f', 'na']} == total([
    ('Popeyes', '3 Blackened Tenders'), ('Popeyes', 'Red Beans & Rice, regular')])

for name, page in PAGES.items():
    content = (ROOT / name).read_text(encoding='utf-8')
    heading = html.unescape(re.sub('<[^>]+>', '', re.search(r'<h1\b[^>]*>(.*?)</h1>', content, re.S)[1]))
    assert heading == page['title'], name
    assert 'By GetMacros' in content and 'GetMacros.net editorial team' not in content, name
    assert 'Updated September 9, 2026' in content, name
    assert html.escape(page['intro'], quote=True) in content, name
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', content, re.S):
        schema = json.loads(block)
        if schema.get('@type') in ['Article', 'BlogPosting']:
            assert schema['headline'] == page['title'], name
            assert schema['author']['name'] == 'GetMacros', name

protein = (ROOT / 'how-much-protein-per-day.html').read_text(encoding='utf-8')
assert 'nearly all healthy adults' in protein and '1.4–2.0' in protein
blog = (ROOT / 'best-fast-food-restaurants-for-your-goals.html').read_text(encoding='utf-8')
assert 'Hearty Fireside Chili' in blog and 'Turkey Chili' not in blog
assert 'article-hero' in blog, 'Keep the illustrated article header'
assert '520 calories and 25 g protein' in blog
foods = json.loads((ROOT / 'tools/protein-food-review.json').read_text(encoding='utf-8'))
food_page = (ROOT / 'high-protein-foods-list.html').read_text(encoding='utf-8')
assert len(foods) == len({f['name'] for f in foods}) == 25
for food in foods:
    card = re.search(r'<article class="protein-food-card"[^>]*data-food-name="'+re.escape(html.escape(food['name'], quote=True))+r'".*?</article>', food_page, re.S)
    assert card and f"<strong>{int(food['protein100']*food['grams']/100+.5)} g</strong>" in card[0], food['name']
    assert html.escape(food['source'], quote=True) in food_page, food['name']
assert next(f for f in foods if f['name']=='Firm tofu')['protein100'] == 17.27
assert next(f for f in foods if f['name']=='Pumpkin seeds, shelled')['protein100'] == 30.23
print(f'Submission review: {len(meals)} sourced orders and {len(PAGES)} reviewed pages passed.')

# The quiz must paint with the document and initialize only once after rebuilds.
quiz=(ROOT/'restaurant-meal-finder.html').read_text(encoding='utf-8')
for name in ('data','quiz'):
    scripts=re.findall(r'<script src="js/meal-'+name+r'\.js[^\"]*"[^>]*>',quiz)
    assert len(scripts)==1 and 'defer' in scripts[0], name
    assert quiz.index(scripts[0]) < quiz.index('</head>'), name
assert quiz.index('<script src="js/meal-data.js') < quiz.index('<script src="js/meal-quiz.js')
assert quiz.count('data-first-question') >= 1 and 'What’s your goal?' in quiz
assert quiz.count('<script data-quiz-bootstrap>')==1
print('Quiz delivery: visible first question and one ordered copy of each script.')
