"""Migrate UI selectors in existing checks to the replaced interface."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for filename in ['test-publication-accessibility.cjs','test-botanical-resilience.cjs']:
 p=root/'tools'/filename;s=p.read_text(encoding='utf-8')
 s=s.replace(".discovery-submit",'.home-finder button[type=submit]')
 s=s.replace("p.locator('[data-reset]').click()","p.locator('#finder-filters [type=reset]').click()")
 s=s.replace("p.locator('.quiz-option input:checked')","p.locator('#finder-filters input:checked')")
 s=s.replace("'design/publication-accessibility.json'","'docs/redesign/reset/accessibility.json'")
 s=s.replace("'docs/redesign/resilience-checks.json'","'docs/redesign/reset/resilience-checks.json'")
 p.write_text(s,encoding='utf-8')
