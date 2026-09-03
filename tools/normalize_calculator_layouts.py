"""One-time, idempotent structural migration; preserve original HTML byte ranges."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text, self.nodes, self.stack = text, [], []
        self.lines = [0]
        for i, char in enumerate(text):
            if char == '\n':
                self.lines.append(i + 1)
        self.feed(text)

    def source_position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_position()
        node = dict(tag=tag, attrs=dict(attrs), start=start,
                    inner=start + len(self.get_starttag_text()),
                    parent=self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)
        else:
            node['end'] = node['inner']

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node['end'] = node['inner']

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                node = self.stack[i]
                node['close'] = self.source_position()
                node['end'] = self.text.index('>', self.source_position()) + 1
                del self.stack[i:]
                break

    def find(self, *, id=None, cls=None):
        return next(n for n in self.nodes if
                    (id is None or n['attrs'].get('id') == id) and
                    (cls is None or cls in n['attrs'].get('class', '').split()))


def wrap_pair(name, form_id, output_id):
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    if 'class="tool-workspace"' in text:
        return
    doc = Document(text)
    form, out = doc.find(id=form_id), doc.find(id=output_id)
    assert form['parent'] is out['parent'], name
    assert form['end'] <= out['start'], name
    placeholder = ('<p class="workspace-placeholder">Your results will appear here after you calculate.</p>'
                   if 'hidden' in out['attrs'] else '')
    replacement = ('<div class="tool-workspace">' + text[form['start']:form['end']] +
                   '<aside class="tool-output" aria-label="Calculation results">' + placeholder +
                   text[form['end']:out['end']] + '</aside></div>')
    path.write_text(text[:form['start']] + replacement + text[out['end']:], encoding='utf-8')
    print('paired', name)


def split_toolbox(name, output_id=None):
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    if 'toolbox tool-workspace' in text:
        return
    doc = Document(text)
    box = doc.find(cls='toolbox')
    out = doc.find(id=output_id) if output_id else doc.find(cls='results')
    assert out['parent'] is box, name
    replacement = ('<div class="toolbox tool-workspace"><div class="tool-inputs">' +
                   text[box['inner']:out['start']] + '</div><aside class="tool-output" aria-label="Calculation results">' +
                   ('<p class="workspace-placeholder">Your timeline will appear here after you calculate.</p>' if 'hidden' in out['attrs'] else '') +
                   text[out['start']:box['close']] + '</aside></div>')
    path.write_text(text[:box['start']] + replacement + text[box['end']:], encoding='utf-8')
    print('split', name)


def metadata_and_food_labels():
    calculator_pages = {
        'calculators.html': 'calculator', 'recipe-macro-scaler.html': 'recipe',
        'nutrition-label-comparison-tool.html': 'compare', 'protein-value-calculator.html': 'value',
        'budget-meal-builder.html': 'basket', 'sodium-label-comparison-tool.html': 'sodium',
        'carbohydrate-label-portion-tool.html': 'carbs', 'weight-goal-timeline-calculator.html': 'target',
        'sweat-rate-calculator.html': 'water',
    }
    icons = dict(re.findall(r"^\s+(\w+): '(<[^\n]+>)'", (ROOT/'js/calculator-suite.js').read_text(encoding='utf-8'), re.M))
    for path in ROOT.glob('*.html'):
        text = path.read_text(encoding='utf-8')
        original = text
        if path.name in calculator_pages:
            icon = calculator_pages[path.name]
            body = re.search(r'<body class="([^"]*)"', text)
            if body and 'calculator-suite' not in body.group(1).split():
                text = text[:body.start(1)] + body.group(1) + ' calculator-suite calculator-suite--' + icon + text[body.end(1):]
            if icon != 'calculator' and 'class="suite-hero-mark"' not in text:
                mark = '<div class="suite-hero-mark" aria-hidden="true"><svg viewBox="0 0 24 24">' + icons[icon] + '</svg></div>'
                text = re.sub(r'(<h1\b)', lambda m: mark + m.group(1), text, count=1)
        if 'name="color-scheme"' not in text:
            text = re.sub(r'(<meta name="viewport"[^>]+>)', r'\1\n<meta name="color-scheme" content="light dark">\n<meta name="application-name" content="GetMacros">', text, count=1)
        text = text.replace('name="theme-color" content="#f4f7f2"', 'name="theme-color" content="#e5ebe5"')
        if path.name == 'high-protein-foods-list.html':
            text = text.replace('High-Protein Foods Ranked by Protein Per Calorie', '25 High-Protein Foods: Compare Servings &amp; Calories | GetMacros')
            text = text.replace('25 high-protein foods ranked by protein per 100 g, protein per 100 calories and protein in a realistic serving, so you can compare them the way you eat them.', 'Compare 25 high-protein foods by protein per serving and per 100 calories, including meat, fish, dairy and plant-based choices.')
            labels = ['Protein / 100 g', 'Calories / 100 g', 'Protein / 100 cal', 'Serving size', 'Protein / serving']
            def label_row(match):
                row = match.group(0)
                if 'data-label=' in row:
                    return row
                count = iter(labels)
                return re.sub(r'<td>', lambda _: '<td data-label="' + next(count) + '">', row)
            text = re.sub(r'<tr><th scope="row">.*?</tr>', label_row, text)
        if path.name == 'nutrition-label-comparison-tool.html':
            # Remove unsupported universal nutrition cut-offs, not useful data.
            text = re.sub(r'<section class="expanded"><div class="container"><h2>What to compare, in order of importance</h2>.*?</section>', '', text, flags=re.S)
        if path.name == 'protein-value-calculator.html':
            text = text.replace('href="protein-value-calculator.html">Read the complete protein-on-a-budget guide', 'href="how-to-hit-protein-goal-on-budget.html">Read the protein-on-a-budget guide')
        if text != original:
            path.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    for name in ['recipe-macro-scaler.html', 'protein-value-calculator.html']:
        split_toolbox(name)
    for name, form_id, output_id in [
        ('nutrition-label-comparison-tool.html', 'compareForm', 'results'),
        ('sodium-label-comparison-tool.html', 'tool', 'out'),
        ('carbohydrate-label-portion-tool.html', 'tool', 'out'),
        ('sweat-rate-calculator.html', 'form', 'result'),
    ]:
        wrap_pair(name, form_id, output_id)
    split_toolbox('weight-goal-timeline-calculator.html', 'wg-results')
    metadata_and_food_labels()
