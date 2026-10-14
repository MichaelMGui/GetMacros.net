"""Prevent declared character gestures from pointing at nonexistent SVG layers."""
from pathlib import Path
import re,unittest,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]

class CharacterGestureIntegrity(unittest.TestCase):
    def test_declared_gestures_have_native_targets(self):
        symbols={n.attrib['id']:n for n in ET.parse(ROOT/'images/food-characters.svg').getroot() if 'id' in n.attrib}
        source=(ROOT/'js/food-characters.js').read_text(encoding='utf-8')
        definitions=re.findall(r"(\w+):\{name:'[^']+',motion:'([^']+)'",source)
        self.assertEqual(len(definitions),18)
        targets={'blink':'food-eyes','wave':'food-arm-wave','leaf':'food-leaf','nod':'food-nod'}
        for name,motion in definitions:
            with self.subTest(character=name):
                symbol=symbols['food-'+name]
                layers={value for element in symbol.iter() for value in element.attrib.get('class','').split()}
                self.assertIn(targets[motion],layers)

    def test_steak_wave_is_not_hidden_behind_the_body(self):
        root=ET.parse(ROOT/'images/food-characters.svg').getroot()
        steak=next(n for n in root if n.attrib.get('id')=='food-steak')
        children=list(steak)
        body=next(i for i,n in enumerate(children) if 'food-body' in n.attrib.get('class','').split())
        arms=next(i for i,n in enumerate(children) if 'food-arms' in n.attrib.get('class','').split())
        self.assertGreater(arms,body)
        self.assertTrue(any('food-arm-wave' in n.attrib.get('class','').split() for n in children[arms].iter()))

if __name__=='__main__':unittest.main()
