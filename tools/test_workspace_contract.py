"""Source regression checks for paired calculators and readable theme tokens.

These are structural checks, not a replacement for browser/device testing.
"""
import re
from normalize_calculator_layouts import Document, ROOT

PAIRED = {
    'nutrition-label-comparison-tool.html': ('compareForm', 'results'),
    'sodium-label-comparison-tool.html': ('tool', 'out'),
    'carbohydrate-label-portion-tool.html': ('tool', 'out'),
    'sweat-rate-calculator.html': ('form', 'result'),
}
for name, (form_id, output_id) in PAIRED.items():
    doc = Document((ROOT / name).read_text(encoding='utf-8'))
    form, output = doc.find(id=form_id), doc.find(id=output_id)
    assert 'tool-workspace' in form['parent']['attrs']['class'], name
    assert output['parent']['attrs']['class'] == 'tool-output', name
    assert output['parent']['parent'] is form['parent'], name
    assert output['end'] <= output['parent']['end'], name

for name in ['recipe-macro-scaler.html', 'protein-value-calculator.html', 'weight-goal-timeline-calculator.html']:
    doc = Document((ROOT / name).read_text(encoding='utf-8'))
    inputs, output = doc.find(cls='tool-inputs'), doc.find(cls='tool-output')
    assert inputs['parent'] is output['parent'], name
    assert 'tool-workspace' in inputs['parent']['attrs']['class'], name

for path in ROOT.glob('*.html'):
    doc = Document(path.read_text(encoding='utf-8'))
    meta = [n['attrs'] for n in doc.nodes if n['tag'] == 'meta']
    assert len([m for m in meta if m.get('name') == 'color-scheme']) == 1, path.name
    assert next(m for m in meta if m.get('name') == 'theme-color')['content'] == '#e5ebe5', path.name

food = Document((ROOT / 'high-protein-foods-list.html').read_text(encoding='utf-8'))
assert len([n for n in food.nodes if 'data-label' in n['attrs']]) == 125


def luminance(code):
    rgb = [int(code[i:i+2], 16)/255 for i in (1, 3, 5)]
    values = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c, w in zip(values, [.2126, .7152, .0722]))


def contrast(fg, bg):
    light, dark = sorted([luminance(fg), luminance(bg)], reverse=True)
    return (light+.05)/(dark+.05)


for name, fg, bg in [
    ('Light body', '#465b4f', '#e5ebe5'),
    ('Light panel', '#465b4f', '#f0f3ed'),
    ('Light result', '#465b4f', '#dbe4dc'),
    ('Dark body', '#bdc9c1', '#0d1712'),
    ('Dark panel', '#bdc9c1', '#15231b'),
    ('Navigation', '#eef8ee', '#174b36'),
    ('Menu', '#193828', '#e7ece5'),
    ('Light icon', '#205f42', '#e1efe6'),
]:
    ratio = contrast(fg, bg)
    assert ratio >= 4.5, (name, ratio)
    print(f'{name}: {ratio:.1f}:1')

css = (ROOT / 'css/clean-v9.css').read_text(encoding='utf-8')
tokens = re.sub(r'/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '', css, flags=re.S)
assert tokens.count('{') == tokens.count('}'), 'unbalanced CSS blocks'
print('PASS: seven paired workspaces, metadata, 25 mobile food rows and eight contrast pairs.')
