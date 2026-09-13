"""Reuse the homepage bowl and existing tool icons as two flat visual diagrams."""
from pathlib import Path
import copy
import xml.etree.ElementTree as ET
from refine_colour_system import ART

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)

def node(name, attrs=None):
    return ET.Element(f'{{{NS}}}{name}', attrs or {})

def compose(kind, destination):
    canvas = node('svg', {'viewBox': '0 0 600 400', 'fill': 'none'})
    bowl = node('g', {'transform': 'translate(-15 14) scale(.82)'})
    original = ET.parse(ROOT / 'images/home-meal-bowl.svg').getroot()
    # The original plate, food, leaves and shadow remain unchanged.
    # Omit the napkin and fork to leave room for the relevant tool symbol.
    for index, child in enumerate(original):
        if index in (1, 2) or child.attrib.get('transform') == 'rotate(12 481 211)':
            continue
        bowl.append(copy.deepcopy(child))
    canvas.append(bowl)
    icon = node('g', {'transform': 'translate(344 137) scale(1.85)' if kind == 'tools'
                     else 'translate(342 81) scale(1.8)'})
    existing = ET.fromstring(f'<svg xmlns="{NS}">{ART[kind]}</svg>')
    colours = {'art-paper':'#FFFDF3', 'art-leaf':'#438355', 'art-blue':'#ADC4A2',
               'art-orange':'#F2D48A', 'art-berry':'#DB7152', 'art-shadow':'#244C37'}
    for part in existing.iter():
        role = part.attrib.pop('class', '')
        if role in colours:
            part.set('fill', colours[role])
            if role == 'art-shadow': part.set('opacity', '.1')
        if role in ('art-line', 'art-edge', 'art-cut'):
            part.set('stroke', '#FFFDF3' if role == 'art-cut' else '#456B57')
            part.set('stroke-width', part.get('stroke-width', '3'))
            part.set('stroke-linecap', 'round')
            part.set('stroke-linejoin', 'round')
    icon.extend(list(existing))
    canvas.append(icon)
    ET.ElementTree(canvas).write(ROOT / 'images' / destination, encoding='unicode')

if __name__ == '__main__':
    compose('tools', 'home-flat-tools.svg')
    compose('search', 'home-flat-finder.svg')
