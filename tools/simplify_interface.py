"""Final presentation pass: one clear heading, concise choices and consistent CTAs.

Run after generators and organization passes, which use some kicker text as
section markers. Preserve article copy, citations, form labels and referenced IDs.
"""
from pathlib import Path
import re
from normalize_calculator_layouts import Document

ROOT = Path(__file__).resolve().parents[1]
KICKERS = {'eyebrow', 'home-kicker', 'match-kicker', 'home-section-label'}
ACTION_CLASSES = {'text-link', 'about-text-link', 'home-text-link', 'home-extension-link'}
ARROW = r'(?:→|&rarr;|&#8594;)'


def simplify(text, name):
    if name == 'index.html':
        for old, new in {
            '<p>Choose more than one goal in the finder. Your answers shape the shortlist.</p>': '',
            'Compare protein alongside calories, fiber and sodium.': 'Find meals with more protein.',
            'Find lighter meals or larger orders for a bigger appetite.': 'Choose a lighter meal or a bigger portion.',
            'Estimate daily calories and macros before choosing your order.': 'Work out your daily calorie and macro targets.',
            'Find a protein-rich meal →': 'Find a meal',
            'Match your goal →': 'Find a meal',
            'Calculate your targets →': 'Calculate my macros',
            'Useful answers for your next meal.': 'Food questions, answered.',
            'Find a healthy fast-food meal': 'Find a fast-food meal',
            'Calculate calories and macros': 'Calculate my macros',
            'Compare nutrition labels': 'Compare two foods',
            'Get a practical daily estimate for your goal.': 'Estimate your daily targets.',
        }.items():
            text = text.replace(old, new)
        # A card has a heading, a short explanation and a single real link.
        text = re.sub(
            r'<a href="([^"]+)" class="home-decision">(.*?)<span>([^<]+)</span></a>',
            r'<article class="home-decision">\2<a class="btn action-link" href="\1">\3</a></article>',
            text, flags=re.S)
        text = re.sub(r'<a[^>]+class="home-launch-card[^>]*>.*?</a>',
                      lambda m: re.sub(r'<small>.*?</small>', '', m.group(0), flags=re.S), text, flags=re.S)
    if name == 'calculators.html':
        text = re.sub(r'<span class="(?:tool-group-icon|single-card-number)"[^>]*>\d+</span>', '', text)
        for copy in (
            'Use only the calculator you need. Each one shows a daily estimate and links to the published reference ranges behind it.',
            'Choose the calculator that matches the number you need.',
            'Compare food labels, recipe portions and protein costs.',
            'Estimate a timeline, measure observed sweat loss or compare restaurant meals.',
            'Based on body weight', 'Based on daily calories',
        ):
            text = text.replace('<p>' + copy + '</p>', '')
        text = text.replace('Nine tools for real nutrition decisions', 'Food &amp; nutrition tools')
    if name == 'healthy-fast-food.html':
        text = text.replace('Compare complete tracked orders—not just low-calorie sides—across 15 chains. Use the static rankings below or combine several preferences in Fast-food meal finder.',
                            'Explore meals from 15 restaurants, or find a match for your goals.')
    if name == 'search.html':
        text = text.replace('<p>Find a meal, calculate your macros or get a nutrition answer.</p>', '')
    if name == 'restaurant-meal-finder.html':
        text = re.sub(r'<a class="match-calc-link" href="calculators.html">.*?</a>',
                      '<a class="btn action-link match-calc-link" href="calculators.html">Calculate my daily macros</a>', text, flags=re.S)
    text = re.sub(r'<span>Keep going</span>', '', text)

    doc = Document(text)
    main = next((n for n in doc.nodes if n['tag'] == 'main'), None)
    if not main:
        return text
    kickers = [n for n in doc.nodes if n['tag'] == 'p' and 'end' in n
               and main['inner'] <= n['start'] < main['end']
               and set(n['attrs'].get('class', '').split()) & KICKERS
               and not n['attrs'].get('id')]
    for node in reversed(kickers):
        text = text[:node['start']] + text[node['end']:]
    doc = Document(text)
    main = next(n for n in doc.nodes if n['tag'] == 'main')
    edits = []
    for node in doc.nodes:
        if not (main['inner'] <= node['start'] < main['end']) or 'end' not in node:
            continue
        classes = set(node['attrs'].get('class', '').split())
        if node['tag'] != 'a':
            continue
        raw = text[node['start']:node['end']]
        content = text[node['inner']:node.get('close', node['end'])]
        has_arrow = bool(re.search(ARROW, content))
        # Inline reading links stay in the sentence. Standalone actions receive
        # a button surface; link cards keep their existing full-card hit area.
        is_card = bool(re.search(r'<(?:h[1-6]|img|b|strong)\b', content)) or any('card' in c for c in classes)
        ancestors = []
        parent = node['parent']
        while parent and parent is not main:
            ancestors.extend(parent['attrs'].get('class', '').split())
            parent = parent['parent']
        is_action = bool(classes & ACTION_CLASSES) or (has_arrow and not is_card and not classes)
        if 'tool-links' in ancestors:
            is_action = True
        if has_arrow:
            raw = re.sub(r'<(?:span|i)\b[^>]*>\s*' + ARROW + r'\s*</(?:span|i)>', '', raw)
            raw = re.sub(ARROW, '', raw)
        if is_action and 'action-link' not in classes:
            if 'class' in node['attrs']:
                raw = re.sub(r'class="([^"]*)"', r'class="\1 btn action-link"', raw, count=1)
            else:
                raw = raw.replace('<a ', '<a class="btn action-link" ', 1)
        if raw != text[node['start']:node['end']]:
            edits.append((node['start'], node['end'], raw))
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return re.sub(r'(?m)[ \t]+$', '', text)


if __name__ == '__main__':
    changed = 0
    for path in ROOT.glob('*.html'):
        original = path.read_text(encoding='utf-8')
        result = simplify(original, path.name)
        if result != original:
            path.write_text(result, encoding='utf-8')
            changed += 1
    print(f'Simplified headings and actions on {changed} pages.')
