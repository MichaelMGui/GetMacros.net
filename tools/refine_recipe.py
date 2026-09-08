"""Persist the recipe tool's distinction between batch scaling and portioning."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'recipe-macro-scaler.html'
text=path.read_text(encoding='utf-8')
text=text.replace('Enter nutrition per original serving, then choose how many servings the recipe originally made and how many you want now.', 'Enter nutrition per original serving. Choose whether to divide the same batch differently or make more of the recipe.')
if 'id="recipe-mode"' not in text:
    text=text.replace('<div class="tool-inputs">','<div class="tool-inputs"><div class="field"><label for="recipe-mode">What would you like to change?</label><select id="recipe-mode"><option value="portion">Divide the same batch into new portions</option><option value="scale">Make more or less of the recipe</option></select></div>',1)
text=re.sub(r'<script>const ids=\["orig".*?</script>', '<script src="js/recipe-scaler.js" defer></script>',text,flags=re.S)
text=text.replace('Every ingredient is multiplied by the same factor and the finished recipe is divided evenly.', 'For new portions, ingredients stay unchanged. For a larger or smaller batch, every ingredient is multiplied by the same factor and the nutrition per serving stays unchanged. Portions are divided evenly in both modes.')
path.write_text(text,encoding='utf-8')
